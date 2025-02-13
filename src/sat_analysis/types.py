import dataclasses
from typing import Type, TypeVar
from datetime import datetime, timezone

import pyorbital.orbital
'''
Dataclasses to enforce the schema on the API response
'''
@dataclasses.dataclass
class Info():
    satid: int
    satname: str
    transactionscount: int

    def __post_init__(self):
        #store the creation time 
        self.creation_time : datetime = datetime.now(timezone.utc)

@dataclasses.dataclass
class TleData():
    info: Info
    tle: str

    def __post_init__(self):
        lines_list = self.tle.split('\n')
        #remove whitespace for both lines after splitting
        lines_list = [line.strip() for line in lines_list]
        self.line1 = lines_list[0]
        self.line2 = lines_list[1]

    def get_position(self, time = datetime.now(timezone.utc)):
        orbiter = pyorbital.orbital.Orbital(
            "None",
            line1 = self.line1,
            line2 = self.line2
        )
        calculated_pos = orbiter.get_lonlatalt(time)
        #I have this as a dictionary to be easily able to map
        # it to 3-D numpy array
        position_dict = {
            'longitude': calculated_pos[0],
            'latitude': calculated_pos[1],
            'altitude': calculated_pos[2]
        }
        return position_dict
    
    def get_positions_over_time(self, time_values : list[datetime]):
        positions = {}
        for time in time_values:
            positions[time] = self.get_position(time)
        return positions

T = TypeVar('T')
def from_dict(data_class: Type[T], data: dict) -> T:
    """
    Convert a dictionary to a dataclass instance
    """
    if dataclasses.is_dataclass(data_class):
        #first identify the field names and types of the data class
        fieldtypes = {f.name: f.type for f in dataclasses.fields(data_class)}
        data_class_kwargs = {}
        for field_name, field_type in fieldtypes.items():
            field_value = data[field_name]
            #create any sub dataclasses
            data_class_kwargs[field_name] = from_dict(field_type, field_value)
        instantiated_cls =  data_class(**data_class_kwargs)
        return instantiated_cls
    else: # if it's a primitive type
        return data
