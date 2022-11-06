from typing import List, Tuple

from enums.video_types import VideoDeviceType
from models.video_models import VideoModels


class BitrateSelector:

    @staticmethod
    def __auto_select(model: VideoModels) -> int:
        ratio_codec = 1.0
        bit_rate_pair: List[Tuple[int, float]] = [
            (1000, 2.5),
            (2500, 2.0),
            (4000, 1.75),
            (6000, 1.5),
            (8000, 1.25),
            (10000, 1.0),
        ]
        ratio_org_bit_rate = 1.0
        if model.origin_codec == "h264":
            ratio_codec = 0.4
        elif model.origin_codec == "hevc" or model.origin_codec == "h265":
            ratio_codec = 0.35
        for pair in bit_rate_pair:
            check_bit = pair[0]
            check_rate = pair[1]
            if model.origin_bit_rate < check_bit:
                ratio_org_bit_rate = check_rate
                break
        ratio = ratio_codec * ratio_org_bit_rate
        if ratio > 1.0:
            ratio = 1.0
        return int(model.origin_bit_rate * ratio)

    @staticmethod
    def select_bit_rate(model: VideoModels) -> int:
        # GoPro
        if model.video_type == VideoDeviceType.GO_PRO_1080P_30FPS:
            return int(model.origin_bit_rate / 3)
        elif model.video_type == VideoDeviceType.GO_PRO_2_7K_30FPS:
            return int(model.origin_bit_rate / 3)
        elif model.video_type == VideoDeviceType.GO_PRO_4K_30FPS:
            return int(model.origin_bit_rate / 2.25)
        elif model.video_type == VideoDeviceType.GO_PRO_1080P_60FPS:
            return int(model.origin_bit_rate / 3)
        elif model.video_type == VideoDeviceType.GO_PRO_2_7K_60FPS:
            return int(model.origin_bit_rate / 3)
        elif model.video_type == VideoDeviceType.GO_PRO_4K_60FPS:
            return int(model.origin_bit_rate / 2.25)

        # SONY
        elif model.video_type == VideoDeviceType.SONY_1080P_24FPS:
            return int(model.origin_bit_rate / 3)
        elif model.video_type == VideoDeviceType.SONY_2_7K_24FPS:
            return int(model.origin_bit_rate / 3)
        elif model.video_type == VideoDeviceType.SONY_4K_24FPS:
            return int(model.origin_bit_rate / 3)
        elif model.video_type == VideoDeviceType.SONY_1080P_30FPS:
            return int(model.origin_bit_rate / 3)
        elif model.video_type == VideoDeviceType.SONY_2_7K_30FPS:
            return int(model.origin_bit_rate / 3)
        elif model.video_type == VideoDeviceType.SONY_4K_30FPS:
            return int(model.origin_bit_rate / 3)

        # OSOMO
        elif model.video_type == VideoDeviceType.OSMO_1080P_30FPS:
            return int(model.origin_bit_rate / 3)
        elif model.video_type == VideoDeviceType.OSMO_2_7K_30FPS:
            return int(model.origin_bit_rate / 3)
        elif model.video_type == VideoDeviceType.OSMO_4K_30FPS:
            return int(model.origin_bit_rate / 3)
        elif model.video_type == VideoDeviceType.OSMO_4K_60FPS:
            return int(model.origin_bit_rate / 3)
        elif model.video_type == VideoDeviceType.OSMO_1080P_60FPS:
            return int(model.origin_bit_rate / 3)
        elif model.video_type == VideoDeviceType.OSMO_2_7K_60FPS:
            return int(model.origin_bit_rate / 3)

        return BitrateSelector.__auto_select(model)
