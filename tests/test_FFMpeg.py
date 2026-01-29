import os
import unittest

from libprick import FFMpeg, Pricker


class TestFFMpeg(unittest.TestCase):

    def test_ffmpeg(self):
        ffmpeg = FFMpeg()

        ffmpeg.open(os.path.join("fixtures", "example-mp4-file-small.mp4"))

        num_frames = 0
        while ffmpeg.read_frame():
            num_frames += 1

        ffmpeg.close()

        assert num_frames == 1905

    def test_prick(self):

        prick = Pricker()

        prick.open(os.path.join("fixtures", "example-mp4-file-small.mp4"))

        result = prick.hexdigest()

        assert result == "0c0c485897471aaf7efc771e537baba407baad41c3c50762f4857a54326cd3b5"
