from dataclasses import dataclass, field
from datetime import datetime
from dataclasses_json import dataclass_json, config
from marshmallow import fields


@dataclass_json
@dataclass
class StreamModels:
    index: int
    codec_type: str
    creation_time: datetime = field(
        metadata=config(
            encoder=datetime.isoformat,
            decoder=datetime.fromisoformat,
            mm_field=fields.DateTime(format='iso')
        ))
    fps: float
    handler_name: str
    vendor_id: str
    timecode: str
    width: int
    height: int
