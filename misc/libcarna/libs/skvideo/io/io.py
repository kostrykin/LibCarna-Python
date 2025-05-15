import numpy as np

from .avconv import LibAVWriter
from .ffmpeg import FFmpegWriter
from .. import _HAS_AVCONV
from .. import _HAS_FFMPEG
from ..utils import *


def vwrite(fname, videodata, inputdict=None, outputdict=None, backend='ffmpeg', verbosity=0):
    """Save a video to file entirely from memory.

    Parameters
    ----------
    fname : string
        Video file name.

    videodata : ndarray
        ndarray of dimension (T, M, N, C), (T, M, N), (M, N, C), or (M, N),
        where T is the number of frames, M is the height, N is width,
        and C is number of channels.

    inputdict : dict
        Input dictionary parameters, i.e. how to interpret the piped datastream
        coming from python to the subprocess.

    outputdict : dict
        Output dictionary parameters, i.e. how to encode the data to
        disk.

    backend : string
        Program to use for handling video data.
        Only 'ffmpeg' and 'libav' are supported at this time.

    verbosity : int
        Setting to 0 (default) disables all debugging output.
        Setting to 1 enables all debugging output.
        Useful to see if the backend is behaving properly.

    Returns
    -------
    none

    """
    if not inputdict:
        inputdict = {}

    if not outputdict:
        outputdict = {}

    videodata = vshape(videodata)

    # check that the appropriate videodata size was passed
    T, M, N, C = videodata.shape

    if backend == "ffmpeg":
        # check if FFMPEG exists in the path
        assert _HAS_FFMPEG, "Cannot find installation of real FFmpeg (which comes with ffprobe)."

        writer = FFmpegWriter(fname, inputdict=inputdict, outputdict=outputdict, verbosity=verbosity)
        for t in range(T):
            writer.writeFrame(videodata[t])
        writer.close()
    elif backend == "libav":
        # check if FFMPEG exists in the path
        assert _HAS_AVCONV, "Cannot find installation of libav."
        writer = LibAVWriter(fname, inputdict=inputdict, outputdict=outputdict, verbosity=verbosity)
        for t in range(T):
            writer.writeFrame(videodata[t])
        writer.close()
    else:
        raise NotImplemented
