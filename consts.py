DATE_FORMAT = {
    "traktor": "%Y/%m/%d",
    "rekordbox": "%Y-%m-%d"
}

# Color mapping between Rekordbox RGB and Traktor color number
COLOR_MAP = {
    "0xFF0000": "1",  # Red
    "0xFFA500": "2",  # Orange
    "0xFFFF00": "3",  # Yellow
    "0x00FF00": "4",  # Green
    "0x0000FF": "5",  # Blue
    "0xFF007F": "6",  # Rose
    "0x660099": "7",  # Violet
}

TONALITY_MAP = {
    "C": "0",
    "Db": "1",
    "D": "2",
    "Eb": "3",
    "E": "4",
    "F": "5",
    "Gb": "6",
    "G": "7",
    "Ab": "8",
    "A": "9",
    "Bb": "10",
    "B": "11",
    "Cm": "12",
    "Dbm": "13",
    "Dm": "14",
    "Ebm": "15",
    "Em": "16",
    "Fm": "17",
    "Gbm": "18",
    "Gm": "19",
    "Abm": "20",
    "Am": "21",
    "Bbm": "22",
    "Bm": "23",
}

KEY_TO_CODE = {
    "0": "10d",  # C major
    "1": "11d",  # Db major
    "2": "12d",  # D major
    "3": "1d",   # Eb major
    "4": "2d",   # E major
    "5": "3d",   # F major
    "6": "4d",   # Gb major
    "7": "5d",   # G major
    "8": "6d",   # Ab major
    "9": "7d",   # A major
    "10": "8d",  # Bb major
    "11": "9d",  # B major
    "12": "10m", # Cm minor (This one is correct, you would need to check others)
    "13": "11m", # Dbm minor
    "14": "12m", # Dm minor
    "15": "1m",  # Ebm minor
    "16": "2m",  # Em minor
    "17": "3m",  # Fm minor
    "18": "4m",  # Gbm minor
    "19": "5m",  # Gm minor
    "20": "6m",  # Abm minor
    "21": "7m",  # Am minor
    "22": "8m",  # Bbm minor
    "23": "9m",  # Bm minor
}

COLOR_NAME_TO_RGB = {
    "pink": {"R": "222", "G": "68", "B": "207"},  # (1)
    "orchidea": {"R": "180", "G": "50", "B": "255"},  # (2)
    "violet": {"R": "170", "G": "114", "B": "255"},  # (3)
    "mauve": {"R": "100", "G": "115", "B": "255"},  # (4)

    "blue": {"R": "48", "G": "90", "B": "255"},  # (5)
    "sky": {"R": "80", "G": "180", "B": "255"},  # (6)
    "cyan": {"R": "0", "G": "224", "B": "255"},  # (7)
    "turquoise": {"R": "31", "G": "163", "B": "146"},  # (8)

    "celadon": {"R": "16", "G": "177", "B": "118"},  # (9)
    "green": {"R": "40", "G": "226", "B": "20"},  # (10)
    "lime": {"R": "165", "G": "225", "B": "22"},  # (11)
    "kaki": {"R": "180", "G": "190", "B": "4"},  # (12)

    "yellow": {"R": "195", "G": "175", "B": "4"},  # (13)
    "orange": {"R": "224", "G": "100", "B": "27"},  # (14)
    "red": {"R": "230", "G": "40", "B": "40"},  # (15)
    "magenta": {"R": "255", "G": "18", "B": "123"},  # (16)
}

RGB_TO_CUE_TYPE = {
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

CUE_COLORS = {
    "0": "blue", # Hotcue
    "1": "red", # Fade in
    "2": "green", # Fade out
    "3": "cyan", # Load
    "4": "lime", # Grid
    "5": "orange", # Loop
    "start": "yellow",
    "intro": "yellow",
    "break": "turquoise",
    "bridge": "turquoise",
    "chorus": "rose",
    "verse": "mauve",
    "up": "celadon",
    "buildup": "celadon",
    "drop": "pink",
    "down": "sky",
    "outro": "violet",
    "cue1": "rose",
    "cue2": "magenta",
    "cue3": "mauve",
    "cue4": "sky",
    "AutoGrid": "kaki",
}
