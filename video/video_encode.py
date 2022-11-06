#!/srkim/anaconda3/bin/python
import json
import os
import platform
import subprocess
import sys
import threading
import time
import traceback

from typing import Union, List, Tuple

from models.video_models import VideoModels
from video.ffprobe_parser import FfProbeParse
from video.select_options import OptionSelector
from video.video_gpx import VideoGpxService


def str_stack_trace() -> str:
    type, value, tb = sys.exc_info()
    ex_traceback = ""
    for line in traceback.format_exception(type, value, tb):
        ex_traceback += "%s" % (line,)
    return ex_traceback


class VideoEncoder:
    def __init__(self, base_dir: str) -> None:
        super().__init__()
        self.WORK_THREAD_COUNT = 1
        self.check_ext = ["mp4", "avi", "mkv"]
        self.check_codec = ["h264", 'hevc']
        self.base_dir = base_dir
        self.lock = threading.Lock()
        self.queue: List[VideoModels] = []
        self.h_threads = []
        self.__init_threads()
        self.abs_path = self.__get_abs_path(base_dir)

    @staticmethod
    def __get_abs_path(base_dir: str):
        if base_dir[0] == '/' or base_dir[0] == '\\' or base_dir[1] == ':':
            return base_dir
        now_path = os.path.abspath('.')
        return os.path.join(now_path, base_dir)



    def __init_threads(self):
        for idx in range(self.WORK_THREAD_COUNT):
            h_thread = threading.Thread(target=self.__work_thread, args=(idx,))
            h_thread.daemon = True
            h_thread.start()
            self.h_threads.append(h_thread)

    def __os_ok(self, f_name: str, check_encode: str) -> bool:
        meta_at = FfProbeParse.get_metadata(f_name)
        if meta_at is None:
            return False
        try:
            codec: str = meta_at.origin_codec.lower()
        except KeyError:
            return False
        if codec == check_encode:
            return True
        return False

    def __work_thread(self, idx):
        while True:
            self.lock.acquire()
            if self.queue is None:
                self.lock.release()
                break
            if len(self.queue) == 0:
                self.lock.release()
                time.sleep(1.0)
                continue
            model: VideoModels = self.queue[0]
            self.queue = self.queue[1:]
            self.lock.release()
            self.__encode(model)

    def __encode_enqueue(self, model: VideoModels):
        while True:
            self.lock.acquire()
            if len(self.queue) > self.WORK_THREAD_COUNT:
                self.lock.release()
                time.sleep(1.0)
                continue
            self.queue.append(model)
            self.lock.release()
            break

    def __make_ffmpeg_cmd(self, model: VideoModels) -> (str, str):
        tmp_file_suffix = "tmp." + model.file_name.split(".")[-1]
        new_file_name = "%s.%s" % (model.file_name, tmp_file_suffix)
        org_file_name = model.file_name
        OptionSelector.select_map(model)
        input_codec = OptionSelector.select_input_codec(model)
        output_codec = "hevc_nvenc"
        bit_rate = OptionSelector.select_bit_rate(model)
        cmd: List[str] = []
        if platform.system() == "Linux":
            wrap = "'"
        else:
            wrap = '"'
        cmd.append("ffmpeg")
        cmd.append("-noautorotate")
        cmd.append("-hwaccel cuvid")
        cmd.append("-c:v %s" % (input_codec,))
        cmd.append("-i %s%s%s" % (wrap, org_file_name, wrap))
        cmd.append("-map_metadata 0")
        cmd.append("-movflags use_metadata_tags")
        cmd.append("-copy_unknown")

        for maps in OptionSelector.select_map(model):
            cmd.append(maps)

        cmd.append("-c:v %s" % (output_codec,))
        cmd.append("-vtag hvc1")
        cmd.append("-b:v %d" % (bit_rate,))
        cmd.append("%s%s%s" % (wrap, new_file_name, wrap))

        cmd_text = ""
        for item in cmd:
            cmd_text += "%s " % (item,)
        return cmd_text, new_file_name

    def __encode(self, model: VideoModels):
        try:
            self.__encode_in(model)
        except Exception as e:
            print("Error. __encode : %s\n%s" % (e, str_stack_trace()))
            return

    def __encode_in(self, model: VideoModels):
        cmd, new_file_name = self.__make_ffmpeg_cmd(model)
        print(cmd)
        gpx = VideoGpxService(model)
        gpx_data = gpx.get_gpx_data()
        if os.path.exists(new_file_name) is True:
            os.remove(new_file_name)
        subprocess.run(cmd, shell=True)
        if self.__os_ok(new_file_name, "hevc") is True:
            stat = os.stat(model.file_name)
            os.utime(new_file_name, (stat.st_atime, stat.st_mtime))
            os.remove(model.file_name)

            f_ext = model.file_name.split(".")[-1]
            f_name = model.file_name.replace(".%s" % f_ext, "")
            file_name = "%s_hevc.%s" % (f_name, f_ext)
            os.rename(new_file_name, file_name)

        return

    def __check_already_work(self, full_path: str):
        ext = full_path.split(".")[-1]
        gpx_path = full_path.replace("." + ext, '.gpx')
        json_path = full_path.replace("." + ext, '_gpx_video.json')
        if os.path.exists(gpx_path) is True or os.path.exists(json_path) is True:
            return True
        return False

    def scan(self):
        for (root, dirs, files) in os.walk(self.abs_path):
            if len(files) > 0:
                for file_name in files:
                    file_name: str
                    if "_hevc." in file_name.lower() or '.tmp.' in file_name:
                        continue
                    full_path = os.path.join(root, file_name)
                    if self.__check_already_work(full_path) is True:
                        continue
                    if os.stat(full_path).st_size < 1024 * 1024 * 10:
                        continue
                    model: VideoModels = FfProbeParse.get_metadata(full_path)
                    if model is not None:
                        self.__encode_enqueue(model)
        while len(self.queue) > 0:
            time.sleep(1.0)
        self.queue = None
        for h_thread in self.h_threads:
            h_thread.join()
        return


def main():
    if platform.system() == "Linux":
        dir = "../../"
    else:
        dir = "C:\\Users\\shshr\\Videos\\sample\\5"
    e = VideoEncoder(dir)
    e.scan()


if __name__ == "__main__":
    main()
