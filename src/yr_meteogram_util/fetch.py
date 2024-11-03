"""Module for downloading meteograms as svg from YR and to perform simple modifications on them."""

import re
import asyncio

import aiohttp

def make_meteogram_transparent(meteogram: str) -> str:
    """
    Manipulates the meteogram svg by making it transparent.
    Currently uses a quick and dirty method that might fail if the original contents is changed.

    Arguments:
    meteogram - the string containing the meteogram svg.

    Returns a string containing the meteogram with the background removed.
    """

    # Remove style="background-color:#<any color>
    meteogram = re.sub(r'(style="background-color:#)[0-9A-Fa-f]+"',
                     '',
                     meteogram)

    # Remove '<rect x="0" y="0" width="782" height="391" fill="#<any color>"'
    # with '<rect x="0" y="0" width="782" height="391" fill="#<background_color>'
    meteogram = re.sub(r'(<rect\s+x="0"\s+y="0"\s+width="782"\s+'
                     + r'height="391"\s+fill="#)[0-9A-Fa-f]+"\s+/>',
                     '',
                     meteogram)

    return meteogram

def unhide_dark_meteogram_details(meteogram: str) -> str:
    """
    Manipulates the meteogram svg by changing black color to whiteish.
    The black details in the dark version (with some browsers). Must be a bug in Yr.
    Safari renders them as "black on black". Chrome and Edge does not.
    The changes makes Safari render the colors the same as Chrome and Edge.
    Currently uses a quick and dirty method that might fail if the original contents is changed.

    Arguments:
    meteogram - the string containing the meteogram svg.

    Returns a string containing the meteogram svg with always visible colors.
    """
    # First change color of some symbols to off-white (same color as lables)
    symbol_color = "#a2a5b3"
    meteogram = re.sub(r'(cy="18"\s+r="1.25"\s+stroke=")currentColor' +
                     r'("\s+stroke-width="1.5"/><path stroke=")currentColor' +
                     r'("\s+stroke-width="1.5"\s+d="M12)',
                     lambda m: m.group(1) + symbol_color + m.group(2) + symbol_color + m.group(3),
                     meteogram)
    meteogram = re.sub(r'(viewBox="0\s+0\s+24\s+24"><path\s+fill=")currentColor' +
                     r'("\s+d="M2.04 12l-.747-.06.748.06zm19.92)',
                     lambda m: m.group(1) + symbol_color + m.group(2),
                     meteogram)
    meteogram = re.sub(r'(<path\s+stroke=")currentColor' +
                     r'("\s+stroke-width="1.5"\s+d="M18 12H2m7.268-7A2)',
                     lambda m: m.group(1) + symbol_color + m.group(2),
                     meteogram)

    # Then change the reminding to white
    meteogram = meteogram.replace("currentColor", "#FFFFFF")
    return meteogram

def crop_meteogram(meteogram: str) -> str:
    """
    Manipulates the meteogram svg by croping it to the essentials.
    Also moves source information to a better sopt.
    Currently uses a quick and dirty method that might fail if the original contents is changed.

    Arguments:
    meteogram - the string containing the meteogram svg.

    Returns a string containing the croped meteogram svg.
    """

    # Set a viewBox for the crop
    height = '300'
    meteogram = re.sub(r'(<svg\s+xmlns:xlink="http://www.w3.org/1999/xlink"\s+'
                     + r'width="782"\s+height=)"391"',
                     lambda m: f'{m.group(1)}"{height}" viewBox="0 85 782 {height}"',
                     meteogram)

    # Move "Served by" and logos to a better location
    base_y = float(363)
    meteogram = meteogram.replace('translate(612, 22.25)', f'translate(612, {str(base_y)})')
    meteogram = meteogram.replace('y="24.28"', f'y="{str(base_y + 1.79)}"')
    meteogram = meteogram.replace('y="20"', f'y="{str(base_y - 2.5)}"')

    return meteogram

async def fetch_svg_async(location_id: str, dark: bool = False, crop: bool = False,
                          make_transparent: bool = False, unhide_dark_objects = False) -> str:
    """
    Download a meteogram as a svg.

    Arguments:
    location - the Id of the location.
    dark - download the dark version.
    crop - crop the svg to minimum.
    make_transparent - remove the background color.
    unhide_dark_objects - in dark version; alter black objects to visible color.

    Returns a string containing the meteogram svg.
    """

    meteogram_url = f'https://www.yr.no/en/content/{location_id}/meteogram.svg'

    if dark:
        meteogram_url += '?mode=dark'

    async with aiohttp.ClientSession() as session:
        async with session.get(meteogram_url) as response:
            meteogram = await response.text()

    if crop:
        meteogram = crop_meteogram(meteogram)

    if make_transparent:
        meteogram = make_meteogram_transparent(meteogram)

    if dark and unhide_dark_objects:
        meteogram = unhide_dark_meteogram_details(meteogram)

    return meteogram

def fetch_svg(location_id: str, dark: bool = False, crop: bool = False,
              make_transparent: bool = False, unhide_dark_objects = False) -> str:
    """
    Download a meteogram as a svg.

    Arguments:
    location - the Id of the location.
    dark - download the dark version.
    crop - crop the svg to minimum.
    make_transparent - remove the background color.
    unhide_dark_objects - in dark version; alter black objects to visible color.

    Returns a string containing the meteogram svg.
    """
    meteogram = asyncio.run(fetch_svg_async(location_id, dark, crop,
                                            make_transparent, unhide_dark_objects))
    return meteogram
