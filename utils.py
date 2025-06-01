from xml.etree.ElementTree import Element
from datetime import datetime
from typing import Literal

from consts import DATE_FORMAT, COLOR_MAP, TONALITY_MAP, COLOR_NAME_TO_RGB, CUE_COLORS, RGB_TO_CUE_TYPE

softType = Literal["traktor", "rekordbox"]

# VARIABLES TO BE DEFINED BY SPECIFIC SCRIPTS
original: softType
target: softType

def set_conversion(o: softType, t: softType):
    global original, target
    original = o
    target = t


def get_attribute(element: Element, attribute):
    """Get an attribute from an element if it exists."""
    if element is not None and attribute in element.attrib:
        return element.get(attribute)
    return ""


def get_element(element: Element, sub_element):
    """Find a sub-element from an element."""
    try:
        return element.find(sub_element)
    except Exception:
        return None


def format_date(date):
    try:
        return datetime.strptime(date, DATE_FORMAT.get(original)).strftime(DATE_FORMAT.get(target))
    except Exception:
        return date


def _get_traktor_track_color(rgb_color):
    """Convert Rekordbox RGB color to Traktor color number."""
    return COLOR_MAP.get(rgb_color, "")


def _get_rekordbox_track_color(color_nb):
    """Convert Traktor color number to Rekordbox RGB color."""
    # Reverse lookup in the COLOR_MAP
    for rgb, num in COLOR_MAP.items():
        if num == color_nb:
            return rgb
    return ""


def get_track_color(color):
    if target == "traktor":
        return _get_traktor_track_color(color)
    elif target == "rekordbox":
        return _get_rekordbox_track_color(color)
    return ""


def _get_traktor_cue_type(rekordbox_type):
    """Convert Rekordbox cue type to Traktor cue type."""
    # Rekordbox: Cue = "0", Loop = "4"
    # Traktor: Cue = "0", Fade-In = "1", Fade-Out = "2", Load = "3", AutoGrid / Grid = "4", Loop = "5"
    return "5" if rekordbox_type == "4" else "0"


def _get_rekordbox_cue_type(traktor_type):
    """Convert Traktor cue type to Rekordbox cue type."""
    # Traktor: Cue = "0", Fade-In = "1", Fade-Out = "2", Load = "3", AutoGrid / Grid = "4", Loop = "5"
    # Rekordbox: Cue = "0", Loop = "4" (Fade-In "1", Fade-Out "2", Load "3" DON'T WORK)
    return "4" if traktor_type == "5" else "0"


def get_cue_type(ctype):
    if target == "traktor":
        return _get_traktor_cue_type(ctype)
    elif target == "rekordbox":
        return _get_rekordbox_cue_type(ctype)
    return "0"


def _get_traktor_key(tonality):
    """Convert Rekordbox tonality to Traktor musical key."""
    return TONALITY_MAP.get(tonality, "")


def _get_rekordbox_tonality(musical_key):
    """Convert Traktor musical key to Rekordbox tonality."""
    for ton, key in TONALITY_MAP.items():
        if key == musical_key:
            return ton
    return ""


def get_tonalikey(tonalikey):
    if target == "traktor":
        return _get_rekordbox_tonality(tonalikey)
    elif target == "rekordbox":
        return _get_traktor_key(tonalikey)
    return ""


def _get_traktor_location(location):
    """Parse Rekordbox location to get directory, file and volume."""
    if location and location.startswith("file://localhost"):
        # Remove prefix and replace URL encoding
        path = location.replace("file://localhost", "").replace("%20", " ")

        # Parse path into components
        parts = path.split("/")

        # Determine volume
        if path.startswith("/"):
            if len(parts) > 1:
                volume = parts[1]
            else:
                volume = "Macintosh HD"
        else:
            volume = "Macintosh HD"

        # Extract filename (last component)
        file_name = parts[-1] if parts else ""

        # Build directory path in Traktor format
        dir_parts = parts[1:-1] if path.startswith("/") else parts[:-1]
        dir_path = "/:".join([""] + dir_parts + [""])

        return {
            "DIR": dir_path,
            "FILE": file_name,
            "VOLUME": volume
        }
    return {
        "DIR": "/:",
        "FILE": "",
        "VOLUME": "Macintosh HD"
    }


def _get_rekordbox_location(location):
    """Get Rekordbox location path from directory, file and volume."""
    if location is not None:
        dir_path = location.get("DIR").replace("/:","/")
        file_name = location.get("FILE")
        volume = get_attribute(location, "VOLUME")
        disk = f"/{volume}" if not "Mac" in volume else ""
        return f"file://localhost{disk}{dir_path}{file_name}".replace(" ", "%20")
    return ""


def get_location(location):
    if target == "traktor":
        return _get_traktor_location(location)
    elif target == "rekordbox":
        return _get_rekordbox_location(location)
    return ""


def map_to_color(ctype):
    ctype = str(ctype).lower().replace(" ", "").replace("-", "")
    return CUE_COLORS.get(ctype, "blue")


def color_distance(color1, color2):
    r1, g1, b1 = color1
    r2, g2, b2 = color2
    # Calculate squared Euclidean distance
    return (r1 - r2) ** 2 + (g1 - g2) ** 2 + (b1 - b2) ** 2


def find_closest_color(target_rgb, color_map):
    """Find the closest color in the color map to the target RGB."""
    min_distance = float('inf')
    closest_color = None

    for color_key, value in color_map.items():
        # Assume all keys are in "r-g-b" format
        compare_rgb = tuple(map(int, color_key.split('-')))
        distance = color_distance(target_rgb, compare_rgb)

        if distance < min_distance:
            min_distance = distance
            closest_color = value

    return closest_color


def get_cue_color_values(r, g, b):
    rgb_key = f"{r}-{g}-{b}"
    if rgb_key in RGB_TO_CUE_TYPE:
        return RGB_TO_CUE_TYPE[rgb_key]

    closest_type = find_closest_color((int(r), int(g), int(b)), RGB_TO_CUE_TYPE)

    return closest_type or "0"

def _set_traktor_cue_color(cue, r, g, b):
    ctype = get_cue_color_values(r, g, b)
    cue.set("Type", ctype)
    return cue

def _set_rekordbox_cue_color(cue, ctype, cname):
    if ctype == "0" and cname != "n.n.":
        ctype = cname

    color = map_to_color(ctype)
    rgb = COLOR_NAME_TO_RGB.get(color, "")
    if rgb:
        cue.set("Red", rgb["R"])
        cue.set("Green", rgb["G"])
        cue.set("Blue", rgb["B"])
    return cue

def set_cue_color(cue, **kwargs):
    if target == "traktor":
        r, g, b = kwargs.get("r"), kwargs.get("g"), kwargs.get("b")
        return _set_traktor_cue_color(cue, r, g, b)
    elif target == "rekordbox":
        ctype, cname = kwargs.get("ctype"), kwargs.get("cname")
        return _set_rekordbox_cue_color(cue, ctype, cname)
    return cue
