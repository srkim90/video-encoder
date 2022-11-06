#
# 17/02/2019
# Juan M. Casillas <juanm.casillas@gmail.com>
# https://github.com/juanmcasillas/gopro2gpx.git
#
# Released under GNU GENERAL PUBLIC LICENSE v3. (Use at your own risk)
#

import subprocess
import re
import json
import platform
from collections import namedtuple

Version = namedtuple('Version', ['major', 'medium', 'minor'])

def default_fftools():
    if platform.system() == 'Windows':
        ffmpeg, ffprobe = "ffmpeg.exe", "ffprobe.exe"
    else:
        ffmpeg, ffprobe = "ffmpeg", "ffprobe"

    return ffmpeg, ffprobe


class FFMpegTools:

    def __init__(self, ffprobe=None, ffmpeg=None):
        default_ffmpeg, default_ffprobe = default_fftools()

        self.ffmpeg = ffmpeg if ffmpeg else default_ffmpeg
        self.ffprobe = ffprobe if ffprobe else default_ffprobe

        self.version = self.getVersion()

        self.use_json_format = False
        if self.version.major >= 4:
            self.use_json_format = True

    def getVersion(self):
        output = self.runCmdRaw(self.ffmpeg, ['-version'])
        version_info = output.decode('utf-8')
        version_info_reg = re.compile('ffmpeg version (\d+)\.(\d+)\.(\d+)', flags=re.I)
        m = version_info_reg.search(version_info)
        if m and len(m.groups()) == 3:
            major = int(m.group(1))
            medium = int(m.group(2))
            minor = int(m.group(3))
        return Version(major, medium, minor)

    def runCmd(self, cmd, args):
        result = subprocess.run([ cmd ] + args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output = result.stderr.decode('utf-8')
        return output

    def runCmdRaw(self, cmd, args):
        result = subprocess.run([ cmd ] + args, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        output = result.stdout
        return output

    def getMetadataTrack(self, fname):
        if self.use_json_format:
            return self._getMetadataTrackFromJSON(fname)
        else:
            return self._getMetadataTrackFromText(fname)

    def _getMetadataTrackFromJSON(self, fname):
        """
            % ffprobe -print_format json -show_streams video.mp4
            % ffprobe -v quiet -print_format json -show_format -show_streams video.mp4"

            {
                "streams": [
                    {
                        "index": 0,
                        "codec_name": "h264",
                        "codec_long_name": "H.264 / AVC / MPEG-4 AVC / MPEG-4 part 10",
                        ...
                    },
                    {
                        "index": 1,
                        "codec_name": "aac",
                        "codec_long_name": "AAC (Advanced Audio Coding)",
                        ...
                    },
                    {
                        "index": 2,
                        "codec_type": "data",
                        "codec_tag_string": "tmcd",
                        ...
                    },
                    {
                        "index": 3,
                        "codec_name": "bin_data",
                        "codec_long_name": "binary data",
                        "codec_type": "data",
                        "codec_tag_string": "gpmd",
                        "codec_tag": "0x646d7067",
                        "r_frame_rate": "0/0",
                        "avg_frame_rate": "0/0",
                        "time_base": "1/1000",
                        "start_pts": 0,
                        "start_time": "0.000000",
                        "duration_ts": 29663,
                        "duration": "29.663000",
                        "bit_rate": "48730",
                        "nb_frames": "31",
                        "disposition": {
                            "default": 1,
                            "dub": 0,
                            "original": 0,
                            "comment": 0,
                            "lyrics": 0,
                            "karaoke": 0,
                            "forced": 0,
                            "hearing_impaired": 0,
                            "visual_impaired": 0,
                            "clean_effects": 0,
                            "attached_pic": 0,
                            "timed_thumbnails": 0
                        },
                        "tags": {
                            "creation_time": "2021-03-26T09:44:06.000000Z",
                            "language": "eng",
                            "handler_name": "\tGoPro MET"
                        }
                    }
                ],
                "format": {
                    ...
                }
            }
        """
        args = ['-print_format', 'json', '-show_streams', fname]

        md = json.loads(self.runCmdRaw(self.ffprobe, args))
        stream = next((stream for stream in md['streams'] if stream['codec_tag_string'] == 'gpmd'), None)

        if not stream:
            return None, None
        info_string = 'Stream {}[{}], {} ({})'.format(stream['index'], stream['id'], stream['codec_name'], stream['codec_tag_string'])
        return int(stream["index"]), info_string

    def _getMetadataTrackFromText(self, fname):
        """
        % ffprobe GH010039.MP4 2>&1

        The channel marked as gpmd (Stream #0:3(eng): Data: none (gpmd / 0x646D7067), 29 kb/s (default))
        In this case, the stream #0:3 is the required one (get the 3)

        Input #0, mov,mp4,m4a,3gp,3g2,mj2, from 'GH010039.MP4':
            Stream #0:1(eng): Audio: aac (LC) (mp4a / 0x6134706D), 48000 Hz, stereo, fltp, 189 kb/s (default)
            Stream #0:2(eng): Data: none (tmcd / 0x64636D74), 0 kb/s (default)
            Stream #0:3(eng): Data: none (gpmd / 0x646D7067), 29 kb/s (default)
            Stream #0:4(eng): Data: none (fdsc / 0x63736466), 12 kb/s (default)
        """
        output = self.runCmd(self.ffprobe, [fname])
        # Stream #0:3(eng): Data: bin_data (gpmd / 0x646D7067), 29 kb/s (default)
        # Stream #0:2(eng): Data: none (gpmd / 0x646D7067), 29 kb/s (default)
        # Stream #0:3[0x4](eng): Data: bin_data (gpmd
        reg = re.compile('Stream #\d:(\d)(?:\[0x\d+\])?\(.+\): Data: \w+ \(gpmd', flags=re.I|re.M)

        m = reg.search(output)

        if not m:
            return None, None
        return int(m.group(1)), m.group(0)

    def getMetadata(self, track, fname):

        output_file = "-"
        args = [ '-y', '-i', fname, '-codec', 'copy', '-map', '0:%d' % track, '-f', 'rawvideo', output_file ]
        output = self.runCmdRaw(self.ffmpeg, args)
        return(output)
