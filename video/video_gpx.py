import os
import subprocess
from typing import Union
import xmltodict
from haversine import haversine
import ffmpeg

from enums.video_types import VIDEO_CLASS_GOPRO, VIDEO_CLASS_SONY, VIDEO_CLASS_OSMO
from gopro2gpx import gopro2gpx
from models.gpx_models import GpxModels
from models.gpx_node_models import from_video_fields, GpxNodeModels
from models.video_models import VideoModels
# https://github.com/SK-Hardwired/xavc_rtmd2srt <sony>
# https://github.com/juanmcasillas/gopro2gpx <gopro>
from video.garmin_gpx_service import GarminGpxService


class Args(object):
    def __init__(self):
        self.binary = False
        self.skip = False
        self.verbose = 0
        self.files = []
        self.outputfile = None

class VideoGpxService:
    def __init__(self, model: VideoModels) -> None:
        super().__init__()
        self.model: VideoModels = model
        self.garmin_gpx: GarminGpxService = GarminGpxService(model)

    def __no_garmin_gpx_validate(self, video_gpx: GpxModels) -> GpxModels:
        for idx, node in enumerate(video_gpx.nodes):
            if idx == 0:
                continue
            old_node = video_gpx.nodes[idx-1]
            distance = haversine((old_node.position_lat, old_node.position_long), (node.position_lat, node.position_long), unit='m')
            node.distance = old_node.distance + distance
            node.speed = (distance * 3600) / 1000
            node.enhanced_speed = node.speed

        return video_gpx

    def __cam_init_gpx_prepare_validate(self, garmin_gpx: GpxModels, video_gpx: GpxModels, s_index: int) -> GpxModels:
        turn_on_idx = None
        for idx, node in enumerate(video_gpx.nodes):
            if idx == 0:
                continue
            old_node = video_gpx.nodes[idx-1]
            if old_node.position_lat != node.position_lat or old_node.position_long != node.position_long:
                turn_on_idx = idx
                break
        if turn_on_idx < 3:
            return video_gpx

        jdx = 0
        for idx in range(turn_on_idx-1, -1, -1):
            jdx += 1
            video_gpx.nodes[idx] = garmin_gpx.nodes[(s_index+turn_on_idx)-jdx-3]
        return video_gpx

    def __update_video_gpx_from_garmin_gpx(self, garmin_gpx: GpxModels, video_gpx: GpxModels) -> GpxModels:
        # 비디오에서 추출한 GPX를 가민 fit 파일에서 가저온 gpx내용으로 보충한다. (파워, 케이던스, 심박 등등)
        check_distance = 500
        if garmin_gpx is None:
            return self.__no_garmin_gpx_validate(video_gpx)
        # fit gpx 에서 영상 시작, 끝 점의 인덱스를 찾는다. (영상 위치 보고 판단!)
        video_start_pos = (video_gpx.nodes[0].position_lat, video_gpx.nodes[0].position_long)
        video_end_pos = (video_gpx.nodes[-1].position_lat, video_gpx.nodes[-1].position_long)
        detect_start_idx = None
        detect_end_idx = None
        start_min_distance = check_distance
        end_min_distance = check_distance
        for idx, node in enumerate(garmin_gpx.nodes):
            now_pos = (node.position_lat, node.position_long)
            with_s_distance = haversine(video_start_pos, now_pos, unit='m')
            with_e_distance = haversine(video_end_pos, now_pos, unit='m')
            if start_min_distance > with_s_distance and with_s_distance < check_distance:
                start_min_distance = with_s_distance
                detect_start_idx = idx
            if end_min_distance > with_e_distance and with_e_distance < check_distance:
                end_min_distance = with_e_distance
                detect_end_idx = idx
        # 영상 시작/끝 지점을 가민 gpx에서 탐지해서 해당 구간만을 자른다.
        if detect_start_idx is None or detect_end_idx is None:
            return self.__no_garmin_gpx_validate(video_gpx)
        garmin_gpx_nodes = garmin_gpx.nodes[detect_start_idx:detect_end_idx]

        # 루프를 돌면서 영상의 gpx와 같은 지점을 찾아 해당 지점에서의 메타데이터를 보충해넣는다.
        for jdx, video_node in enumerate(video_gpx.nodes):
            detect_idx = None
            min_distance = check_distance
            video_pos = (video_node.position_lat, video_node.position_long)
            for idx, garmin_at in enumerate(garmin_gpx_nodes):
                now_pos = (garmin_at.position_lat, garmin_at.position_long)
                with_distance = haversine(video_pos, now_pos, unit='m')
                if min_distance > with_distance and with_distance < check_distance:
                    detect_idx = idx
                    min_distance = with_distance
            if detect_idx is not None:
                video_gpx.nodes[jdx] = garmin_gpx_nodes[detect_idx]
        video_gpx = self.__cam_init_gpx_prepare_validate(garmin_gpx, video_gpx, detect_start_idx)
        video_gpx.start_time = garmin_gpx.start_time
        video_gpx.end_time = garmin_gpx.end_time
        return video_gpx

    def __xml_gpx_to_model(self, garmin_gpx: GpxModels, video_xml_gpx: str) -> GpxModels:
        video_dict_gpx = xmltodict.parse(video_xml_gpx)
        trkpt = video_dict_gpx['gpx']['trk']['trkseg']['trkpt']
        video_model_gpx = GpxModels(None, None, self.model, [])
        old_node = None
        for idx, item in enumerate(trkpt):
            node: GpxNodeModels = from_video_fields(item)
            if old_node is not None:
                if old_node.timestamp == node.timestamp:
                    continue
            old_node = node
            video_model_gpx.nodes.append(node)
        video_model_gpx.start_time = video_model_gpx.nodes[0].timestamp
        video_model_gpx.end_time = video_model_gpx.nodes[-1].timestamp
        return self.__update_video_gpx_from_garmin_gpx(garmin_gpx, video_model_gpx)

    def __covert_bin_to_gpx(self, bin_name) -> GpxModels:
        gpx_name = bin_name.replace(".bin", ".gpx")
        args = Args()
        args.files = [bin_name,]
        args.outputfile = gpx_name
        args.binary = True
        args.verbose = 2
        xml_gpx = gopro2gpx.main_core(args)
        garmin_gpx = self.garmin_gpx.get_garmin_gpx_data()
        return self.__xml_gpx_to_model(garmin_gpx, xml_gpx)#xmltodict.parse(xml_gpx)


    def __get_gpx_stream_file(self) -> Union[str, None]:
        model = self.model
        if model.gpx_stream_idx == -1:
            return None
        ext_name = model.file_name.split(".")[-1]
        bin_name = model.file_name.replace("." + ext_name, ".bin")
        cmd = 'ffmpeg -y -i %s -codec copy -map 0:d:%d -f rawvideo %s' % (model.file_name, model.gpx_stream_idx, bin_name)
        subprocess.run(cmd, shell=True)
        return bin_name

    def __save_video_gpx(self, video_gpx: GpxModels):
        gpx_video_path = VideoGpxService.make_video_gpx_file_name(self.model.dir_name, self.model.file_name)
        json_data = GpxModels.to_json(video_gpx, indent=4, ensure_ascii=False).encode("utf-8")
        with open(gpx_video_path, "wb") as fd:
            fd.write(json_data)
        return

    def __get_gopro_gpx_data(self) -> Union[GpxModels, None]:
        bin_name = self.__get_gpx_stream_file()
        gpx_dict = self.__covert_bin_to_gpx(bin_name)
        if os.path.exists(bin_name) is True:
            os.remove(bin_name)
        self.__save_video_gpx(gpx_dict)
        return gpx_dict

    def __get_osmo_gpx_data(self) -> Union[GpxModels, None]:
        return None

    def __get_sony_gpx_data(self) -> Union[GpxModels, None]:
        return None

    @staticmethod
    def make_video_gpx_file_name(dir_name: str, file_name: str) -> str:
        ext = file_name.split('.')[-1]
        file_name = file_name.replace("." + ext, "_gpx_video.json")
        return os.path.join(dir_name, file_name)

    def get_gpx_data(self) -> Union[GpxModels, None]:
        if self.model.video_type in VIDEO_CLASS_GOPRO:
            return self.__get_gopro_gpx_data()
        elif self.model.video_type in VIDEO_CLASS_SONY:
            return self.__get_sony_gpx_data()
        elif self.model.video_type in VIDEO_CLASS_OSMO:
            return self.__get_osmo_gpx_data()
        else:
            return None
