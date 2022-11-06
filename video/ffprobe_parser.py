import datetime
import json
import platform
import subprocess
from typing import Union, List

from enums.video_types import VideoDeviceType
from models.stream_models import StreamModels
from models.video_models import VideoModels


class FfProbeParse:

    @staticmethod
    def __parse_stream(stream: dict) -> StreamModels:
        tags: dict = stream['tags']
        creation_time = None
        handler_name = None
        vendor_id = None
        timecode = None
        try:
            creation_time = datetime.datetime.strptime(tags['creation_time'].split(".")[0], "%Y-%m-%dT%H:%M:%S")
        except KeyError:
            pass
        try:
            handler_name = tags['handler_name']
        except KeyError:
            pass
        try:
            vendor_id = tags['vendor_id']
        except KeyError:
            pass
        try:
            timecode = tags['timecode']
        except KeyError:
            pass
        avg_frame_rate = stream['avg_frame_rate']
        if '/' in avg_frame_rate:
            a = float(avg_frame_rate.split("/")[0])
            b = float(avg_frame_rate.split("/")[1])
            avg_frame_rate = 0.0
            if b > 0:
                avg_frame_rate = float(float(a)/float(b))
        else:
            avg_frame_rate = float(avg_frame_rate)

        width: int = 0
        height: int = 0
        if 'width' in stream.keys() and 'height' in stream.keys():
            width = int(stream["width"])
            height = int(stream["height"])
        return StreamModels(
            fps=avg_frame_rate,
            index=stream['index'],
            codec_type=stream['codec_type'],
            creation_time=creation_time,
            handler_name=handler_name,
            vendor_id=vendor_id,
            timecode=timecode,
            width=width,
            height=height
        )

    @staticmethod
    def get_video_type(video_stream: StreamModels, streams: List[StreamModels]) -> VideoDeviceType:
        f_sony = False
        for stream in streams:
            if 'Timed Metadata Media Handler' in stream.handler_name:
                f_sony = True
                break
        if 'gopro' in video_stream.handler_name.lower():
            if video_stream.height < 1100:
                if video_stream.fps > 58:
                    return VideoDeviceType.GO_PRO_1080P_60FPS
                else:
                    return VideoDeviceType.GO_PRO_1080P_30FPS
            if video_stream.height < 1800:
                if video_stream.fps > 58:
                    return VideoDeviceType.GO_PRO_2_7K_30FPS
                else:
                    return VideoDeviceType.GO_PRO_2_7K_60FPS
            else:
                if video_stream.fps > 58:
                    return VideoDeviceType.GO_PRO_4K_30FPS
                else:
                    return VideoDeviceType.GO_PRO_4K_60FPS
        elif 'dji' in video_stream.handler_name.lower():
            if video_stream.height < 1100:
                if video_stream.fps > 58:
                    return VideoDeviceType.OSMO_1080P_60FPS
                else:
                    return VideoDeviceType.OSMO_1080P_30FPS
            if video_stream.height < 1800:
                if video_stream.fps > 58:
                    return VideoDeviceType.OSMO_2_7K_30FPS
                else:
                    return VideoDeviceType.OSMO_2_7K_60FPS
            else:
                if video_stream.fps > 58:
                    return VideoDeviceType.OSMO_4K_30FPS
                else:
                    return VideoDeviceType.OSMO_4K_60FPS
        elif f_sony is True:
            if video_stream.height < 1100:
                if video_stream.fps > 28:
                    return VideoDeviceType.SONY_1080P_30FPS
                else:
                    return VideoDeviceType.SONY_1080P_24FPS
            if video_stream.height < 1800:
                if video_stream.fps > 28:
                    return VideoDeviceType.SONY_2_7K_30FPS
                else:
                    return VideoDeviceType.SONY_2_7K_24FPS
            else:
                if video_stream.fps > 28:
                    return VideoDeviceType.SONY_4K_30FPS
                else:
                    return VideoDeviceType.SONY_4K_24FPS
        return VideoDeviceType.UNKNOWN

    @staticmethod
    def get_metadata(full_file_name: str) -> Union[VideoModels, None]:
        dir_split = '\\' if platform.system() == 'Windows' else '/'
        try:
            cmd = ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", "-show_streams", "%s" % (full_file_name,)]
            fd_popen = subprocess.Popen(cmd, stdout=subprocess.PIPE).stdout
            data = fd_popen.read().strip().decode("utf-8")
            fd_popen.close()
            streams: List[StreamModels] = []
            video_stream_obj = None
            if len(data) < 10:
                return None
            data_dict = json.loads(data)
            gpx_stream_idx = -1
            for idx, stream in enumerate(data_dict['streams']):
                stream_obj = FfProbeParse.__parse_stream(stream)
                streams.append(stream_obj)
                if stream_obj.codec_type == "video":
                    video_stream_obj = stream_obj
                if "GoPro MET" in stream_obj.handler_name:
                    gpx_stream_idx = idx - 2
            if video_stream_obj is None:
                return None
            video_stream = data_dict['streams'][0]
            format = data_dict['format']
            file_name = full_file_name.split(dir_split)[-1]
            dir_name = full_file_name.replace(file_name, "")
            if dir_name[-1] == dir_split:
                dir_name = dir_name[0:-1]
            try:
                creation_time = datetime.datetime.strptime(data_dict['format']['tags']['creation_time'].split(".")[0], "%Y-%m-%dT%H:%M:%S")
            except KeyError:
                creation_time = datetime.datetime.now()
            return VideoModels(
                video_type=FfProbeParse.get_video_type(video_stream_obj, streams),
                file_name=format['filename'],
                origin_codec=video_stream['codec_name'],
                origin_bit_rate=int(video_stream['bit_rate']),
                dimensions_x=int(video_stream['coded_width']),
                dimensions_y=int(video_stream['coded_height']),
                streams=streams,
                video_streams=video_stream_obj,
                gpx_stream_idx=gpx_stream_idx,
                creation_time=creation_time,
                duration=float(data_dict['format']['duration']),
                dir_name=dir_name
            )
        except IOError as e:
            return None
