import platform

from video.video_encode import VideoEncoder


def main():
    if platform.system() == "Linux":
        dir = "./"
    else:
        dir = "C:\\Users\\shshr\\Videos\\sample\\4"
    e = VideoEncoder(dir)
    e.scan()
    pass


if __name__ == "__main__":
    main()
