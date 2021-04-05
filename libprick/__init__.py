import hashlib
import os
from typing import List

from libprick.FFMpeg import FFMpeg, FFMpegError


class PrickError(Exception):
    pass


class Pricker:

    MIN_CALLBACK_INTERVAL = 1000000

    def __init__(self, callback=None):
        self.callback = callback
        self.ffmpeg = FFMpeg()
        self.hashers = []
        self.bytes_hashed = 0
        self.bytes_last_callback = 0

    def open(self, path: str) -> None:
        self.reset()
        self.ffmpeg.close()

        try:
            self.ffmpeg.open(path)
            self.hashers = [hashlib.sha256() for _ in range(self.ffmpeg.get_num_streams())]
        except FFMpegError as e:
            raise PrickError("Could not open file") from e

        self.__hash()

    def reset(self) -> None:
        self.hashers = []

    def digest(self) -> bytes:
        digests = self.stream_digests()
        digest = digests[0]
        for curr in digests[1:]:
            digest = bytes([_a ^ _b for _a, _b in zip(digest, curr)])

        return digest

    def hexdigest(self) -> str:
        return self.digest().hex()

    def stream_digests(self) -> List[bytes]:
        return [x.digest() for x in self.hashers]

    def stream_hexdigests(self) -> List[str]:
        return [x.hexdigest() for x in self.hashers]

    def __del__(self):
        self.ffmpeg.close()

    def __hash(self):
        if not self.ffmpeg.pFormatCtx:
            raise PrickError('')

        frame = self.ffmpeg.read_frame()
        while frame:
            self.hashers[frame.stream_index].update(frame.data)

            if self.callback:
                self.bytes_hashed += len(frame.data)
                if self.bytes_hashed > self.bytes_last_callback + Pricker.MIN_CALLBACK_INTERVAL:
                    self.callback(self.bytes_hashed)
                    self.bytes_last_callback = self.bytes_hashed

            frame = self.ffmpeg.read_frame()


    @staticmethod
    def version() -> int:
        return 1
