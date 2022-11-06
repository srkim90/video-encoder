from typing import List, Tuple, Union

from models.stream_models import StreamModels
from models.video_models import VideoModels
from video.select_bitrate import BitrateSelector


class OptionSelector:

    @staticmethod
    def select_data_map(model: StreamModels, idx_data: int) -> Union[None,str]:
        allow_list = ["GoPro MET",]
        for check in allow_list:
            if check in model.handler_name:
                return "-map 0:d:%d" % idx_data
        return None

    @staticmethod
    def select_map(model: VideoModels) -> List[str]:
        maps = []
        idx_data = 0
        for stream in model.streams:
            if stream.codec_type == 'video':
                maps.append("-map 0:v")
            elif stream.codec_type == 'audio':
                maps.append("-map 0:a")
            elif stream.codec_type == 'data':
                map_cmd = OptionSelector.select_data_map(stream, idx_data)
                if map_cmd is not None:
                    maps.append(map_cmd)
                idx_data += 1
        return maps

    @staticmethod
    def select_input_codec(model: VideoModels):
        origin_codec = model.origin_codec
        if origin_codec == "h264":
            return "h264_cuvid"
        elif origin_codec == "hevc" or origin_codec == "h265":
            return "hevc_cuvid"
        else:
            raise IOError("not supported input codec : %s" % origin_codec)

    @staticmethod
    def select_bit_rate(model: VideoModels) -> int:
        return BitrateSelector.select_bit_rate(model)
