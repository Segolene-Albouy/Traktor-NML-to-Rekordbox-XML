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

RB_COLORS = {
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
    "buildup": "celadon",
    "drop": "pink",
    "outro": "violet",
    "cue1": "rose",
    "cue2": "magenta",
    "cue3": "mauve",
    "cue4": "sky",
    "AutoGrid": "kaki",
}
