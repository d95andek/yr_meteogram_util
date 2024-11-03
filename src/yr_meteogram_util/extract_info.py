"""Module for extracting information from meteogram svgs downloaded from YR."""

import re

def get_location_name(meteogram: str) -> str:
    """
    Extracts the location name from a meteogram.
    Currently uses a quick and dirty method that might fail if the original contents is changed.

    Arguments:
    meteogram - the string containing the meteogram svg.

    Returns a string containing the location name.
    """

    location = re.search(r'Weather\s+forecast\s+for\s+(.*)', meteogram).group(1)

    return location
