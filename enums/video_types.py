from enum import Enum, auto


class VideoDeviceType(str, Enum):
    GO_PRO_1080P_30FPS = "GO_PRO_1080P_30FPS"
    GO_PRO_2_7K_30FPS = "GO_PRO_2_7K_30FPS"
    GO_PRO_4K_30FPS = "GO_PRO_4K_30FPS"
    GO_PRO_1080P_60FPS = "GO_PRO_1080P_60FPS"
    GO_PRO_2_7K_60FPS = "GO_PRO_2_7K_60FPS"
    GO_PRO_4K_60FPS = "GO_PRO_4K_60FPS"

    SONY_1080P_30FPS = "SONY_1080P_30FPS"
    SONY_2_7K_30FPS = "SONY_2_7K_30FPS"
    SONY_4K_30FPS = "SONY_4K_30FPS"
    SONY_1080P_24FPS = "SONY_1080P_24FPS"
    SONY_2_7K_24FPS = "SONY_2_7K_24FPS"
    SONY_4K_24FPS = "SONY_4K_24FPS"

    OSMO_1080P_30FPS = "OSMO_1080P_30FPS"
    OSMO_2_7K_30FPS = "OSMO_2_7K_30FPS"
    OSMO_4K_30FPS = "OSMO_4K_30FPS"
    OSMO_4K_60FPS = "OSMO_4K_60FPS"
    OSMO_1080P_60FPS = "OSMO_1080P_60FPS"
    OSMO_2_7K_60FPS = "OSMO_2_7K_60FPS"

    UNKNOWN = "UNKNOWN"


VIDEO_CLASS_GOPRO = [VideoDeviceType.GO_PRO_1080P_30FPS,
                     VideoDeviceType.GO_PRO_2_7K_30FPS,
                     VideoDeviceType.GO_PRO_4K_30FPS,
                     VideoDeviceType.GO_PRO_1080P_60FPS,
                     VideoDeviceType.GO_PRO_2_7K_60FPS,
                     VideoDeviceType.GO_PRO_4K_60FPS]

VIDEO_CLASS_SONY = [VideoDeviceType.SONY_1080P_30FPS,
                     VideoDeviceType.SONY_2_7K_30FPS,
                     VideoDeviceType.SONY_4K_30FPS,
                     VideoDeviceType.SONY_1080P_24FPS,
                     VideoDeviceType.SONY_2_7K_24FPS,
                     VideoDeviceType.SONY_4K_24FPS]

VIDEO_CLASS_OSMO = [VideoDeviceType.OSMO_1080P_30FPS,
                     VideoDeviceType.OSMO_2_7K_30FPS,
                     VideoDeviceType.OSMO_4K_30FPS,
                     VideoDeviceType.OSMO_1080P_60FPS,
                     VideoDeviceType.OSMO_2_7K_60FPS,
                     VideoDeviceType.OSMO_4K_60FPS]