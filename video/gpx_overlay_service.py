import os
from typing import Union

from models.gpx_models import GpxModels


class GpxOverlayService:
    def __init__(self, gpx_json_path: str) -> None:
        super().__init__()
        self.models: GpxModels = self.__load_gpx_models(gpx_json_path)

    @staticmethod
    def __load_gpx_models(gpx_json_path: str) -> Union[GpxModels, None]:
        if os.path.exists(gpx_json_path) is True:
            with open(gpx_json_path, "rb") as fd:
                return GpxModels.from_json(fd.read())
        raise FileNotFoundError("Not exist : %s" % gpx_json_path)

    def draw(self):
        for item in self.models.nodes:
            print(item)



def main():
    e = GpxOverlayService("C:\\Users\\shshr\\Videos\\sample\\4\\GoPro8_2.7K_60fps_227030_GH030227_gpx_video.json")
    e.draw()

if __name__ == "__main__":
    main()