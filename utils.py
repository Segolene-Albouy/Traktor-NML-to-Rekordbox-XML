import xml.etree.ElementTree as ET
from datetime import datetime

from consts import DATE_FORMAT, COLOR_MAP, TONALITY_MAP

# VARIABLES TO BE DEFINED BY SPECIFIC SCRIPTS
original = None
target = None

def set_conversion(o, t):
    global original, target
    original = o
    target = t


def get_attribute(element, attribute):
    """Get an attribute from an element if it exists."""
    if element is not None and attribute in element.attrib:
        return element.get(attribute)
    return ""


def get_element(element, sub_element):
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


def _convert_tonality_to_key(tonality):
    """Convert Rekordbox tonality to Traktor musical key."""
    return TONALITY_MAP.get(tonality, "")


def _convert_key_to_tonality(musical_key):
    """Convert Traktor musical key to Rekordbox tonality."""
    for ton, key in TONALITY_MAP.items():
        if key == musical_key:
            return key
    return ""


def get_tonalikey(tonalikey):
    if target == "traktor":
        return _convert_key_to_tonality(tonalikey)
    elif target == "rekordbox":
        return _convert_tonality_to_key(tonalikey)
    return ""


def _parse_location_path(location):
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


def _get_location_path(location):
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
        return _parse_location_path(location)
    elif target == "rekordbox":
        return _get_location_path(location)
    return ""


def get_cue_color_values(r, g, b):
    """Map RGB color values to a Traktor cue type."""
    # This is a simplification - in practice you might want a more sophisticated mapping
    rgb_colors = {
        # Format: "R-G-B": "type"
        "222-68-207": "0",  # Pink - Hotcue
        "180-50-255": "0",  # Orchidea - Hotcue
        "170-114-255": "0",  # Violet - Hotcue
        "100-115-255": "0",  # Mauve - Hotcue

        "48-90-255": "0",  # Blue - Hotcue
        "80-180-255": "0",  # Sky - Hotcue
        "0-224-255": "3",  # Cyan - Load
        "31-163-146": "3",  # Turquoise - Load

        "16-177-118": "4",  # Celadon - Grid
        "40-226-20": "5",  # Green - Loop
        "165-225-22": "4",  # Lime - Grid
        "180-190-4": "4",  # Kaki - Grid

        "195-175-4": "0",  # Yellow - Hotcue
        "224-100-27": "5",  # Orange - Loop
        "230-40-40": "1",  # Red - Fade in
        "255-18-123": "2"  # Magenta - Fade out
    }

    key = f"{r}-{g}-{b}"
    return rgb_colors.get(key, "0")  # Default to Hotcue
