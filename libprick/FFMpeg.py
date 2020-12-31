import copy
import os
import platform
import sys
import sysconfig
from ctypes import Structure, POINTER, CFUNCTYPE, c_int, c_void_p, c_char, c_uint, c_int64, c_uint8, c_char_p, \
    c_ulong, CDLL, byref
from typing import Optional

int64_t = c_int64
uint8_t = c_uint8
STRING = c_char_p
size_t = c_ulong


class AVFormatContext(Structure):
    pass


class AVPacket(Structure):
    pass


AVFormatContext._fields_ = [
        ('av_class', int64_t),
        ('iformat', int64_t),
        ('oformat', int64_t),
        ('priv_data', c_void_p),
        ('pb', int64_t),
        ('ctx_flags', c_int),
        ('nb_streams', c_uint),
        ('streams', int64_t),
        ('filename', c_char * 1024),
        ('url', STRING),
        ('start_time', c_int64),
        ('duration', c_int64),
        ('bit_rate', c_int64),
        ('packet_size', c_uint),
        ('max_delay', c_int),
        ('flags', c_int),
        ('probesize', c_uint),
        ('max_analyze_duration', c_int),
        ('key', int64_t),
        ('keylen', c_int),
        ('nb_programs', c_uint),
        ('programs', int64_t),
        ('video_codec_id', c_int),
        ('audio_codec_id', c_int),
        ('subtitle_codec_id', c_int),
        ('max_index_size', c_uint),
        ('max_picture_buffer', c_uint),
        ('nb_chapters', c_uint),
        ('chapters', int64_t),
        ('metadata', int64_t),
        ('start_time_realtime', c_int64),
        ('fps_probe_size', c_int),
        ('error_recognition', c_int),
        ('interrupt_callback', int64_t),
        ('debug', c_int),
        ('max_interleave_delta', int64_t),
        ('strict_std_compliance', c_int),
        ('event_flags', c_int),
        ('max_ts_probe', c_int),
        ('avoid_negative_ts', c_int),
        ('ts_id', c_int),
        ('audio_preload', c_int),
        ('max_chunk_duration', c_int),
        ('max_chunk_size', c_int),
        ('use_wallclock_as_timestamps', c_int),
        ('avio_flags', c_int),
        ('duration_estimation_method', c_int),
        ('skip_initial_bytes', int64_t),
        ('correct_ts_overflow', c_uint),
        ('seek2any', c_int),
        ('flush_packets', c_int),
        ('probe_score', c_int),
        ('format_probesize', c_int),
        ('codec_whitelist', STRING),
        ('format_whitelist', STRING),
        ('internal', int64_t),
        ('io_repositioned', c_int),
        ('video_codec', int64_t),
        ('audio_codec', int64_t),
        ('subtitle_codec', int64_t),
        ('data_codec', int64_t),
        ('metadata_header_padding', c_int),
        ('opaque', c_void_p),
        ('control_message_cb', CFUNCTYPE(c_int, int64_t, c_int, c_void_p, size_t)),
        ('output_ts_offset', int64_t),
        ('dump_separator', int64_t),
        ('data_codec_id', c_int),  # AVCodecID
        ('protocol_whitelist', STRING),
        ('open_cb', CFUNCTYPE(c_int, POINTER(AVFormatContext), int64_t, STRING, c_int, int64_t, int64_t)),
        ('io_close', CFUNCTYPE(c_void_p, POINTER(AVFormatContext), int64_t)),
        ('protocol_blacklist', STRING),
        ('max_streams', c_int),
        ('skip_estimate_duration_from_pts', c_int),
        ('max_probe_packets', c_int),
    ]

AVPacket._fields_ = [
    ('buf', int64_t),
    ('pts', int64_t),
    ('dts', int64_t),
    ('data', POINTER(uint8_t)),
    ('size', c_int),
    ('stream_index', c_int),
    ('flags', c_int),
    ('side_data', POINTER(c_int)),
    ('side_data_elems', c_int),
    ('duration', c_int64),
    ('pos', c_int64),
    ('convergence_duration', c_int64),
]


class FFMpegError(Exception):
    pass


class Frame:
    def __init__(self, stream_index: int, data: bytes):
        self.stream_index = stream_index
        self.data = data


class FFMpeg:

    AVSEEK_FLAG_BYTE = 2
    AV_LOG_QUIET = -8

    avformat = None
    avcodec = None
    avutil = None

    def __init__(self):
        lib_path = FFMpeg.__get_lib_path()

        os_family = platform.system()

        if os_family == 'Windows':
            FFMpeg.avcodec = CDLL("{0}avcodec-58".format(lib_path))
            FFMpeg.avformat = CDLL("{0}avformat-58".format(lib_path))
            FFMpeg.avutil = CDLL("{0}avutil-56".format(lib_path))
        elif os_family == 'Linux':
            cython = sysconfig.get_config_var('SOABI')
            FFMpeg.avcodec = CDLL("{0}codec/codec.{1}.so".format(lib_path, cython))
            FFMpeg.avformat = CDLL("{0}format.{1}.so".format(lib_path, cython))
            FFMpeg.avutil = CDLL("{0}utils.{1}.so".format(lib_path, cython))
        else:
            print("Platform '{0}' not supported".format(os_family), file=sys.stderr)
            exit(1)

        FFMpeg.avcodec.av_free_packet.argtypes = [POINTER(AVPacket)]
        FFMpeg.avformat.avformat_open_input.argtypes = [POINTER(POINTER(AVFormatContext)), c_char_p, c_char_p, c_char_p]
        FFMpeg.avformat.avformat_close_input.argtypes = [POINTER(POINTER(AVFormatContext))]

        FFMpeg.avformat.av_register_all()
        FFMpeg.avutil.av_log_set_level(FFMpeg.AV_LOG_QUIET)

        self.pFormatCtx = None

    def open(self, path):
        self.pFormatCtx = POINTER(AVFormatContext)()
        res = FFMpeg.avformat.avformat_open_input(self.pFormatCtx, path.encode('utf-8'), None, None)
        if res:
            raise FFMpegError("Could not open {0}".format(path))

        res = FFMpeg.avformat.avformat_find_stream_info(self.pFormatCtx, None)  # needed to populate duration

        if res < 0:
            raise FFMpegError("Could not find stream {0}".format(path))

        if self.pFormatCtx.contents.nb_streams <= 0:
            raise FFMpegError("Invalid number of streams: {0}".format(self.pFormatCtx.contents.nb_streams))

        self.seek_start()

    def seek_start(self) -> None:
        FFMpeg.avformat.av_seek_frame(self.pFormatCtx, 0, 0, FFMpeg.AVSEEK_FLAG_BYTE)

    def read_frame(self) -> Optional[Frame]:
        avp = AVPacket()
        res = FFMpeg.avformat.av_read_frame(self.pFormatCtx, byref(avp))

        if res < 0:
            return None

        stream_index = avp.stream_index
        data = copy.copy(avp.data.contents)
        FFMpeg.avcodec.av_free_packet(avp)

        return Frame(stream_index, data)

    def close(self) -> None:
        if self.pFormatCtx:
            FFMpeg.avformat.avformat_close_input(self.pFormatCtx)
        self.pFormatCtx = None

    def get_num_streams(self) -> Optional[int]:
        if not self.pFormatCtx:
            return None
        return self.pFormatCtx.contents.nb_streams

    @staticmethod
    def __get_lib_path() -> str:

        os_family = platform.system()
        path = ''

        if os_family == 'Windows':
            path = "{0}\\Lib\\site-packages\\av\\".format(sys.base_exec_prefix)
            if getattr(sys, 'frozen', False):
                path = '{0}\\'.format(sys.base_exec_prefix)

        elif os_family == 'Linux':
            path = "{0}/lib/python{1}/site-packages/av/".format(sys.base_exec_prefix,
                                                                '.'.join(platform.python_version_tuple()[0:2]))
            if getattr(sys, 'frozen', False):
                path = '{0}/av/'.format(sys.base_exec_prefix)

        else:
            print("Platform '{0}' not supported".format(os_family), file=sys.stderr)
            exit(1)

        if not os.path.exists(path):
            raise FFMpegError("Could not load FFMpeg libs. Is the 'av' package installed?\nlib path: {0}".format(path))

        return path
