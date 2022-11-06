from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List

from dataclasses_json import dataclass_json, config
from fitparse.records import FieldData, Field
from marshmallow import fields


@dataclass_json
@dataclass
class GpxNodeModels:
    timestamp: datetime = field(
        metadata=config(
            encoder=datetime.isoformat,
            decoder=datetime.fromisoformat,
            mm_field=fields.DateTime(format='iso')
        ))
    position_lat: float # 37.4131190
    position_long: float # 127.1346390
    distance: float  # 140.21[m]
    accumulated_power: int  # 2274 [watts]
    enhanced_altitude: float  # 113.20000000000005 [m]
    altitude: float  # 113.20000000000005 [m]
    enhanced_speed: float  # 5.048[m/s]
    speed: float  # 5.048[m/s]
    power: int  # 128[watts]
    heart_rate: int  # 124[bpm]
    cadence: int  # 71[rpm]
    temperature: int  # 22[C]
    left_right_balance: int  # 190
    fractional_cadence: float  # 0.0[rpm]


def from_video_fields(field_data: dict) -> GpxNodeModels:
    timestamp = datetime.strptime(field_data["time"].split(".")[0], "%Y-%m-%dT%H:%M:%S") + timedelta(hours=9)
    position_lat = float(field_data["@lat"])
    position_long = float(field_data["@lon"])
    enhanced_altitude = float(field_data["ele"])
    altitude = enhanced_altitude
    accumulated_power = 0
    distance = 0.0
    enhanced_speed = 0.0
    speed = 0.0
    power = 0
    heart_rate = 0
    cadence = 0
    temperature = 0
    left_right_balance = 0
    fractional_cadence = 0.0
    return GpxNodeModels(timestamp,
                         position_lat,
                         position_long,
                         distance,
                         accumulated_power,
                         enhanced_altitude,
                         altitude,
                         enhanced_speed,
                         speed,
                         power,
                         heart_rate,
                         cadence,
                         temperature,
                         left_right_balance,
                         fractional_cadence)

def from_fit_fields(field_data_list: List[FieldData]) -> GpxNodeModels:
    timestamp = None
    position_lat = None
    position_long = None
    distance = 0.0
    accumulated_power = 0
    enhanced_altitude = 0.0
    altitude = 0.0
    enhanced_speed = 0.0
    speed = 0.0
    power = 0
    heart_rate = 65
    cadence = 0
    temperature = 0
    left_right_balance = 0
    fractional_cadence = 0.0

    for idx, field_data in enumerate(field_data_list):
        name = field_data.name
        value = field_data.value

        if name == "timestamp":
            timestamp = value + timedelta(hours=9) # datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
        elif name == "position_lat":
            position_lat = value#float(value / 446355899.0) #value * (37.4131190 / 446355899.0)
        elif name == "position_long":
            position_long = value#float(value / 1516775322.0) #value * (127.1346390 / 1516775322)
        elif name == "distance":
            if value is not None:
                distance = value
        elif name == "accumulated_power":
            if value is not None:
                accumulated_power = value
        elif name == "enhanced_altitude":
            if value is not None:
                enhanced_altitude = value
        elif name == "altitude":
            if value is not None:
                altitude = value
        elif name == "enhanced_speed":
            if value is not None:
                enhanced_speed = value
        elif name == "speed":
            if value is not None:
                speed = value
        elif name == "power":
            if value is not None:
                power = value
        elif name == "heart_rate":
            if value is not None:
                heart_rate = value
        elif name == "cadence":
            if value is not None:
                cadence = value
        elif name == "temperature":
            if value is not None:
                temperature = value
        elif name == "left_right_balance":
            if value is not None:
                left_right_balance = value
        elif name == "fractional_cadence":
            if value is not None:
                fractional_cadence = value
    return GpxNodeModels(timestamp,
                         position_lat,
                         position_long,
                         distance,
                         accumulated_power,
                         enhanced_altitude,
                         altitude,
                         enhanced_speed,
                         speed,
                         power,
                         heart_rate,
                         cadence,
                         temperature,
                         left_right_balance,
                         fractional_cadence)
