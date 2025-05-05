import base64
import io
from typing import (
    Any,
    Iterable,
)

import numpngw
import numpy as np

try:
    from IPython.core.display import HTML as IPythonHTML
except ImportError:
    IPythonHTML = None
    

def imshow(array: np.ndarray | Iterable[np.ndarray], fps: float = 25) -> Any:
    assert IPythonHTML is not None, 'Please install IPython to use this function.'

    # The image is a single frame, create an animation with a single frame
    if isinstance(array, np.ndarray) and array.ndim == 3:
        return imshow([array], fps=fps)
    
    # Assume that the image is a list of frames, create a temporal stack
    elif not isinstance(array, np.ndarray):
        return imshow(np.array(list(array)), fps=fps)
    
    # The image is a temporal stack, create an animated PNG
    elif isinstance(array, np.ndarray) and array.ndim == 4:
        buf = io.BytesIO()
        numpngw.write_apng(buf, array, delay=1000 / fps, use_palette=False)
        buf.seek(0)
        buf_base64_str = base64.b64encode(buf.read()).decode('ascii')
        return IPythonHTML(f'<img src="data:image/apng;base64, {buf_base64_str}"/>')
    
    # The image is not a valid type
    else:
        raise ValueError('Array must be 3D or 4D data.')