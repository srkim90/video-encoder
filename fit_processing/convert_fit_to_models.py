from typing import Union, List

import fitparse

from models.gpx_models import GpxModels
from models.gpx_node_models import from_fit_fields, GpxNodeModels


class FitConverter:

    @staticmethod
    def converter(fit_files: Union[str, List[str]]) -> GpxModels:
        model = GpxModels(start_time=None, end_time=None, nodes=[])
        if type(fit_files) != list:
            fit_files = [fit_files]
        for fit_file_name in fit_files:
            fitfile = fitparse.FitFile(
                fit_file_name,
                data_processor=fitparse.StandardUnitsDataProcessor()
            )
            FitConverter.__convert_to_models(fitfile, model)
        model.start_time = model.nodes[0].timestamp
        model.end_time = model.nodes[-1].timestamp
        return model

    @staticmethod
    def __convert_to_models(fitfile, model: GpxModels):
        messages = fitfile.messages
        for m in messages:
            node: GpxNodeModels = from_fit_fields(m.fields)
            if node.timestamp is not None and node.position_lat is not None and node.position_long is not None:
                model.nodes.append(node)
