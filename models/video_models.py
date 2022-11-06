from dataclasses import dataclass, field
from datetime import datetime
from typing import List

from dataclasses_json import dataclass_json, config

from enums.video_types import VideoDeviceType
from models.stream_models import StreamModels
from marshmallow import fields

@dataclass_json
@dataclass
class VideoModels:
    video_type: VideoDeviceType
    dir_name: str
    file_name: str
    duration: float
    creation_time: datetime = field(
        metadata=config(
            encoder=datetime.isoformat,
            decoder=datetime.fromisoformat,
            mm_field=fields.DateTime(format='iso')
        ))
    origin_codec: str
    origin_bit_rate: int
    dimensions_x: int
    dimensions_y: int
    gpx_stream_idx: int
    video_streams: StreamModels
    streams: List[StreamModels]
