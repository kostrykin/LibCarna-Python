import base64
import io
import tempfile
from typing import (
    Any,
    Iterable,
)

import imageio_ffmpeg
import numpngw
import numpy as np

try:
    from IPython.core.display import HTML as IPythonHTML
except ImportError:
    IPythonHTML = None
    

def _render_html_apng(array: np.ndarray | Iterable[np.ndarray], fps: float = 25) -> str:

    # The image is a single frame, create an animation with a single frame
    if isinstance(array, np.ndarray) and array.ndim == 3:
        return _render_html_apng([array], fps=fps)
    
    # Assume that the image is a list of frames, create a temporal stack
    elif not isinstance(array, np.ndarray):
        return _render_html_apng(np.array(list(array)), fps=fps)
    
    # The image is a temporal stack, create an animated PNG
    elif isinstance(array, np.ndarray) and array.ndim == 4:
        buf = io.BytesIO()
        numpngw.write_apng(buf, array, delay=1000 / fps, use_palette=False)
        buf.seek(0)
        buf_base64_str = base64.b64encode(buf.read()).decode('ascii')
        return f'<img src="data:image/apng;base64, {buf_base64_str}"/>'
    
    # The image is not a valid type
    else:
        raise ValueError('Array must be 3D or 4D data.')
    

def _render_html_h264(array: np.ndarray | Iterable[np.ndarray], fps: float = 25) -> str:

    # The image is a single frame, create an animation with a single frame
    if isinstance(array, np.ndarray) and array.ndim == 3:
        return _render_html_h264([array], fps=fps)
    
    # Encode video
    with tempfile.NamedTemporaryFile(suffix='.mp4') as mp4_file:
        with imageio_ffmpeg.write_frames(
            mp4_file.name,
            size=array.shape[1:],
            fps=fps,
            codec='h264',
            pix_fmt_out='yuv420p',
        ) as writer:
            writer.send(None)
            for frame in array:
                writer.send(frame)
        buf = mp4_file.read()

    # Produce HTML
    buf_base64_str = base64.b64encode(buf).decode('ascii')
    return(
        '<video autoplay loop muted style="max-width: 100%;">'
        f'<source type="video/mp4" src="data:video/mp4;base64, {buf_base64_str}"/>'
        '</video>'
    )


html_plugins = dict(
    apng=_render_html_apng,
    h264=_render_html_h264,
)
    

def imshow(array: np.ndarray | Iterable[np.ndarray], *colorbars, fps: float = 25, format: str = 'auto') -> Any:
    """
    Display an image or a sequence of images in a Jupyter notebook.

    Arguments:
        array: The image or sequence of images to display. Can be a 3D NumPy array (RGB image) or 4D NumPy array
            (stack of RGB images), or an iterable of 3D arrays (sequence of RGB images).
        colorbars: Optional colorbars to display alongside the image.
        fps: The frames per second for the animation. Default is 25.
        format: The format to use for displaying the image. Can be `'apng'` or `'h264'`. Default is `'auto'`, which
            will use `'apng'` for single images, and `'h264'` for image stacks or sequences.
    """
    assert IPythonHTML is not None, 'Please install IPython to use this function.'

    if format == 'auto':
        if isinstance(array, np.ndarray) and (array.ndim == 3 or (array.ndim == 4 and array.shape[0] == 1)):
            format = 'apng'
        else:
            format = 'h264'

    # Resolve the format to the proper plugin
    _render_html = html_plugins.get(format, None)
    if _render_html is None:
        raise ValueError(f'Format "{format}" not supported.')
    
    # Delegate to the selected plugin
    nl = '\n'  # Python <3.12 does not allow backslashes in f-strings expressions
    return IPythonHTML(
        f"""
        <div style="display: inline-flex; padding: 0.5em;">
            <div style="display: inline-block; font-size: 0;">
                {_render_html(array, fps=fps)}
            </div>
            {nl.join(cb.tohtml() for cb in colorbars)}
        </div>
        """)