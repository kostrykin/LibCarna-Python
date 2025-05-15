import os
import warnings

import numpy as np

from ..utils import *


class VideoWriterAbstract(object):
    """Writes frames

    this class provides sane initializations for the default case.
    """
    NEED_RGB2GRAY_HACK = False
    DEFAULT_OUTPUT_PIX_FMT = "yuvj444p"

    def __init__(self, filename, inputdict=None, outputdict=None, verbosity=0):
        """Prepares parameters

        Does not instantiate the an FFmpeg subprocess, but simply
        prepares the required parameters.

        Parameters
        ----------
        filename : string
            Video file path for writing

        inputdict : dict
            Input dictionary parameters, i.e. how to interpret the data coming from python.

        outputdict : dict
            Output dictionary parameters, i.e. how to encode the data
            when writing to file.

        Returns
        -------
        none

        """
        self.DEVNULL = open(os.devnull, 'wb')

        filename = os.path.abspath(filename)
        _, self.extension = os.path.splitext(filename)

        # check that the extension makes sense
        encoders = self._getSupportedEncoders()
        if encoders != NotImplemented:
            assert str.encode(
                self.extension).lower() in encoders, "Unknown encoder extension: " + self.extension.lower()

        self._filename = filename
        basepath, _ = os.path.split(filename)

        # check to see if filename is a valid file location
        assert os.access(basepath, os.W_OK), "Cannot write to directory: " + basepath

        if not inputdict:
            inputdict = {}

        if not outputdict:
            outputdict = {}

        self.inputdict = inputdict
        self.outputdict = outputdict
        self.verbosity = verbosity

        if "-f" not in self.inputdict:
            self.inputdict["-f"] = "rawvideo"
        self.warmStarted = False

    def _warmStart(self, M, N, C, dtype):
        self.warmStarted = True

        if "-pix_fmt" not in self.inputdict:
            # check the number channels to guess
            if dtype.kind == 'u' and dtype.itemsize == 2:
                suffix = 'le' if dtype.byteorder else 'be'
                if C == 1:
                    if self.NEED_RGB2GRAY_HACK:
                        self.inputdict["-pix_fmt"] = "rgb48" + suffix
                        self.rgb2grayhack = True
                        C = 3
                    else:
                        self.inputdict["-pix_fmt"] = "gray16" + suffix
                elif C == 2:
                    self.inputdict["-pix_fmt"] = "ya16" + suffix
                elif C == 3:
                    self.inputdict["-pix_fmt"] = "rgb48" + suffix
                elif C == 4:
                    self.inputdict["-pix_fmt"] = "rgba64" + suffix
                else:
                    raise NotImplemented
            else:
                if C == 1:
                    if self.NEED_RGB2GRAY_HACK:
                        self.inputdict["-pix_fmt"] = "rgb24"
                        self.rgb2grayhack = True
                        C = 3
                    else:
                        self.inputdict["-pix_fmt"] = "gray"
                elif C == 2:
                    self.inputdict["-pix_fmt"] = "ya8"
                elif C == 3:
                    self.inputdict["-pix_fmt"] = "rgb24"
                elif C == 4:
                    self.inputdict["-pix_fmt"] = "rgba"
                else:
                    raise NotImplemented

        self.bpp = bpplut[self.inputdict["-pix_fmt"]][1]
        self.inputNumChannels = bpplut[self.inputdict["-pix_fmt"]][0]
        bitpercomponent = self.bpp // self.inputNumChannels
        if bitpercomponent == 8:
            self.dtype = np.dtype('u1')  # np.uint8
        elif bitpercomponent == 16:
            suffix = self.inputdict['-pix_fmt'][-2:]
            if suffix == 'le':
                self.dtype = np.dtype('<u2')
            elif suffix == 'be':
                self.dtype = np.dtype('>u2')
        else:
            raise ValueError(self.inputdict['-pix_fmt'] + 'is not a valid pix_fmt for numpy conversion')

        assert self.inputNumChannels == C, "Failed to pass the correct number of channels %d for the pixel format %s." % (
            self.inputNumChannels, self.inputdict["-pix_fmt"])

        if ("-s" in self.inputdict):
            widthheight = self.inputdict["-s"].split('x')
            self.inputwidth = int(widthheight[0])
            self.inputheight = int(widthheight[1])
        else:
            self.inputdict["-s"] = str(N) + "x" + str(M)
            self.inputwidth = N
            self.inputheight = M

        # prepare output parameters, if raw
        if self.extension == ".yuv":
            if "-pix_fmt" not in self.outputdict:
                self.outputdict["-pix_fmt"] = self.DEFAULT_OUTPUT_PIX_FMT
                if self.verbosity > 0:
                    warnings.warn("No output color space provided. Assuming {}.".format(self.DEFAULT_OUTPUT_PIX_FMT),
                                  UserWarning)

        self._createProcess(self.inputdict, self.outputdict, self.verbosity)

    def _createProcess(self, inputdict, outputdict, verbosity):
        pass

    def _prepareData(self, data):
        return data  # general case : do nothing

    def close(self):
        """Closes the video and terminates FFmpeg process

        """
        if self._proc is None:  # pragma: no cover
            return  # no process
        if self._proc.poll() is not None:
            return  # process already dead
        if self._proc.stdin:
            self._proc.stdin.close()
        self._proc.wait()
        self._proc = None
        self.DEVNULL.close()

    def writeFrame(self, im):
        """Sends ndarray frames to FFmpeg

        """
        vid = vshape(im)
        T, M, N, C = vid.shape
        if not self.warmStarted:
            self._warmStart(M, N, C, im.dtype)

        vid = vid.clip(0, (1 << (self.dtype.itemsize << 3)) - 1).astype(self.dtype)
        vid = self._prepareData(vid)
        T, M, N, C = vid.shape  # in case of hack ine prepareData to change the image shape (gray2RGB in libAV for exemple)

        # check if we need to do some bit-plane swapping
        # for the raw data format
        if self.inputdict["-pix_fmt"].startswith('yuv444p') or self.inputdict["-pix_fmt"].startswith('yuvj444p') or \
                self.inputdict["-pix_fmt"].startswith('yuva444p'):
            vid = vid.transpose((0, 3, 1, 2))

        # Check size of image
        if M != self.inputheight or N != self.inputwidth:
            raise ValueError('All images in a movie should have same size')
        if C != self.inputNumChannels:
            raise ValueError('All images in a movie should have same '
                             'number of channels')

        assert self._proc is not None  # Check status

        # Write
        try:
            self._proc.stdin.write(vid.tostring())
        except IOError as e:
            # Show the command and stderr from pipe
            msg = '{0:}\n\nFFMPEG COMMAND:\n{1:}\n\nFFMPEG STDERR ' \
                  'OUTPUT:\n'.format(e, self._cmd)
            raise IOError(msg)

    def _getSupportedEncoders(self):
        return NotImplemented

    def _dict2Args(self, dict):
        args = []
        for key in dict.keys():
            args.append(key)
            args.append(dict[key])
        return args

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
