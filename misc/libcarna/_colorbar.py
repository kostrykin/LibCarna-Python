import base64
import io

import numpy as np
from PIL import Image

import libcarna


def _sample_down(colorlist, max_resolution):
    """
    Downsample the color list to a maximum resolution.
    """
    max_resolution = max((max_resolution, 2))
    if len(colorlist) <= max_resolution:
        return colorlist

    step = len(colorlist) // max_resolution
    return colorlist[::step]


class colorbar:

    def __init__(
            self,
            colorlist: list[libcarna.base.Color],
            min_intensity: float,
            max_intensity: float,
            ticks: int = 5,
            tick_labels: bool = True,
            max_resolution: int = 1024,
        ):
        self.colorlist = _sample_down(colorlist, max_resolution)
        self.min_intensity = min_intensity
        self.max_intensity = max_intensity
        self.ticks = max((ticks, 2))
        self.tick_labels = tick_labels

    def toarray(self) -> np.array:
        array = np.full(shape=(len(self.colorlist), 1, 4), fill_value=0, dtype=np.uint8)
        for i, color in enumerate(self.colorlist[::-1]):
            array[i, :, 0] = int(color.r)
            array[i, :, 1] = int(color.g)
            array[i, :, 2] = int(color.b)
            array[i, :, 3] = int(color.a)
        return array

    def topng(self) -> bytes:
        array = self.toarray()
        buf = io.BytesIO()
        Image.fromarray(array, mode='RGBA').save(buf, format='PNG')
        buf.seek(0)
        return buf.read()

    def tohtml(self) -> str:
        # Render the image
        png = self.topng()
        png_base64_str = base64.b64encode(png).decode('ascii')

        # Create the ticks
        ticks_list = list()
        step_size = (self.max_intensity - self.min_intensity) / (self.ticks - 1)
        for tick_idx, intensity in enumerate(np.linspace(self.max_intensity, self.min_intensity, num=self.ticks)):
            height_str = '0' if tick_idx == self.ticks - 1 else f'{100 / (self.ticks - 1)}%'
            extra_style = 'transform: translateY(-1px);' if tick_idx == self.ticks - 1 else ''

            # Format the intensity string
            if self.tick_labels:
                if step_size < 10:
                    intensity_str = f'{intensity:g}'
                elif step_size < 1000:
                    intensity_str = f'{round(intensity):d}'
                elif step_size < 10_000:
                    intensity_str = f'{intensity / 1000:.1f}k'
                else:
                    intensity_str = f'{round(intensity / 1000):d}k'
                    if intensity_str == '0k':
                        intensity_str = '0'
            else:
                intensity_str = ''
            
            ticks_list.append(f'''
                <div style="line-height: 0; height: {height_str}; position: relative; padding-left: 0.5em;">
                    {intensity_str}
                    <span style="position: absolute; height: 1px; background-color: black;
                        top: 0; left: -1em; width: 1.2em; {extra_style}"></span>
                </div>''')

        ticks_html = '\n'.join(ticks_list)

        # Render the HTML
        return fr'''
            <div style="display: inline-flex; margin-left: 0.5em;">
                <div style="background-image: url('data:image/svg+xml,%3Csvg viewBox=\'0 0 40 40\' width=\'20\' \
                    height=\'20\' xmlns=\'http://www.w3.org/2000/svg\'%3E%3Cg fill=\'%23aaa\' fill-opacity=\'1\' \
                    fill-rule=\'evenodd\'%3E%3Cpath d=\'M0 40L40 0H20L0 20M40 40V20L20 40\'/%3E%3C/g%3E%3C/svg%3E');
                    background-color: #ffffff; width: 1em; display: inline;">

                    <div style="box-shadow: inset 0px 0px 0px 1px black; height: 100%; background-size: 100% 100%;
                        background-image: url('data:image/png;base64, {png_base64_str}');"></div>
                </div>
                <div style="display: inline-block;">
                    {ticks_html}
                </div>
            </div>'''
