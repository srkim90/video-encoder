import datetime
import os
import platform
from typing import Union

from fitparse import FitFile

from fit_processing.convert_fit_to_csv import write_fitfile_to_csv
from fit_processing.convert_fit_to_models import FitConverter
from models.gpx_models import GpxModels
from models.video_models import VideoModels

# https://tw0226.tistory.com/97\
# https://github.com/mcandocia/fit_processing
'''
경로가 꼬여서 생긴 에러로

나의 경우엔 shapely가 설치된 경로인 C:\Anaconda3\Lib\site-packages\shapely\DLLs 폴더였는데,

폴더에 들어가면 geos.dll, geos_c.dll 파일이 있는 것을 볼 수 있었고,

두 파일을 C:\Anaconda3\Library\bin 로 옮겼더니 해결되었다.
'''

class GarminGpxService:
    def __init__(self, model: VideoModels) -> None:
        super().__init__()
        self.model = model
        self.dir_split = '\\' if platform.system() == 'Windows' else '/'
        self.fit_base_dir = "\\\\192.168.20.100\\media\\hdd14Ta\\riding\\가민" if platform.system() == 'Windows' else \
            "/srkim/mnt/hdd14Ta/riding/가민"

    def __find_fit_file(self) -> Union[str, None]:
        auto_check_day: str = ""
        check_time = datetime.datetime.strptime("2020-06-10T12:00:00", "%Y-%m-%dT%H:%M:%S")
        for file_name in os.listdir(self.model.dir_name):
            if ".fit" not in file_name:
                continue
            # case.1 동일 디렉토리에 fit 파일 존재 할 경우, 해당 파일 신뢰
            return os.path.join(self.model.dir_name, file_name)
        if self.model.creation_time < check_time:
            # 고프로 구입한 날짜보다 동영상의 시간이 이전일 경우 동영상 자체의 시간 신뢰하지 않음 (베터리 오래 빼두고 있으면 시간 초기화됨)
            if 'hdd14Ta' in self.model.dir_name:
                for item in self.model.dir_name.split(self.dir_split):
                    if len(item) < 10:
                        continue
                    if "20" == item[0:2] and "-" in item:
                        auto_check_day = item[0:10]
        else:
            auto_check_day = self.model.creation_time.strftime("%Y-%m-%d")

        selected_fit = None
        fit_list = []
        selected_sz = 0
        for item in os.listdir(self.fit_base_dir):
            if auto_check_day in item:
                fit_list.append(os.path.join(self.fit_base_dir, item))
        if len(fit_list) == 0:
            return None
        for fit in fit_list:
            st_size = os.stat(fit).st_size
            if selected_sz < st_size:
                selected_fit = os.path.join(self.fit_base_dir, fit)
                selected_sz = st_size
        return selected_fit

    def __fit_to_gpx(self, fit_path) -> GpxModels:
        gpx_model: GpxModels = FitConverter.converter(self.model, fit_path)
        self.__save_gpx_cache_file(fit_path, gpx_model)
        return gpx_model

    def __make_cache_file_name(self, fit_path: str) -> str:
        return fit_path.replace(".fit", "_gpx_cache.json")

    def __save_gpx_cache_file(self, fit_path: str, gpx_model: GpxModels) -> None:
        gpx_cache_path = self.__make_cache_file_name(fit_path)
        json_data = GpxModels.to_json(gpx_model, indent=4, ensure_ascii=False).encode("utf-8")
        with open(gpx_cache_path, "wb") as fd:
            fd.write(json_data)
        return

    def __check_gpx_cache_file(self, fit_path: str) -> Union[GpxModels, None]:
        gpx_cache_path = self.__make_cache_file_name(fit_path)
        if os.path.exists(gpx_cache_path) is True:
            with open(gpx_cache_path, "rb") as fd:
                return GpxModels.from_json(fd.read())
        return None

    def get_garmin_gpx_data(self) -> Union[GpxModels, None]:
        fit_path = self.__find_fit_file()
        if fit_path is None:
            return None
        gpx_model = self.__check_gpx_cache_file(fit_path)
        if gpx_model is not None:
            return gpx_model
        gpx_model = self.__fit_to_gpx(fit_path)
        return gpx_model