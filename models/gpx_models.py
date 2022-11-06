from dataclasses import dataclass, field
from datetime import datetime
from typing import List

from dataclasses_json import dataclass_json, config
from fitparse.records import FieldData, Field
from marshmallow import fields

from models.gpx_node_models import GpxNodeModels


@dataclass_json
@dataclass
class GpxModels:
    # def __init__(self) -> None:
    #     super().__init__()
    #     self.nodes = []
    #     # self.start_time = None
    #     # self.end_time = None

    start_time: datetime = field(
        metadata=config(
            encoder=datetime.isoformat,
            decoder=datetime.fromisoformat,
            mm_field=fields.DateTime(format='iso')
        ))
    end_time: datetime = field(
        metadata=config(
            encoder=datetime.isoformat,
            decoder=datetime.fromisoformat,
            mm_field=fields.DateTime(format='iso')
        ))
    nodes: List[GpxNodeModels]
