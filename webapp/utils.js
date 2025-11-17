const COLOR_MAP = {
    "0xFF0000": "1",  // Red
    "0xFFA500": "2",  // Orange
    "0xFFFF00": "3",  // Yellow
    "0x00FF00": "4",  // Green
    "0x0000FF": "5",  // Blue
    "0xFF007F": "6",  // Rose
    "0x660099": "7",  // Violet
};

const TONALITY_MAP = {
    "C": "0", "Db": "1", "D": "2", "Eb": "3", "E": "4", "F": "5",
    "Gb": "6", "G": "7", "Ab": "8", "A": "9", "Bb": "10", "B": "11",
    "Cm": "12", "Dbm": "13", "Dm": "14", "Ebm": "15", "Em": "16", "Fm": "17",
    "Gbm": "18", "Gm": "19", "Abm": "20", "Am": "21", "Bbm": "22", "Bm": "23",
};

const COLOR_NAME_TO_RGB = {
    "pink": {"R": "222", "G": "68", "B": "207"},
    "orchidea": {"R": "180", "G": "50", "B": "255"},
    "violet": {"R": "170", "G": "114", "B": "255"},
    "mauve": {"R": "100", "G": "115", "B": "255"},
    "blue": {"R": "48", "G": "90", "B": "255"},
    "sky": {"R": "80", "G": "180", "B": "255"},
    "cyan": {"R": "0", "G": "224", "B": "255"},
    "turquoise": {"R": "31", "G": "163", "B": "146"},
    "celadon": {"R": "16", "G": "177", "B": "118"},
    "green": {"R": "40", "G": "226", "B": "20"},
    "lime": {"R": "165", "G": "225", "B": "22"},
    "kaki": {"R": "180", "G": "190", "B": "4"},
    "yellow": {"R": "195", "G": "175", "B": "4"},
    "orange": {"R": "224", "G": "100", "B": "27"},
    "red": {"R": "230", "G": "40", "B": "40"},
    "magenta": {"R": "255", "G": "18", "B": "123"},
};

const CUE_COLORS = {
    "0": "blue",
    "1": "red",
    "2": "green",
    "3": "cyan",
    "4": "lime",
    "5": "orange",
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
};

function getAttribute(element, attribute){
    if (!element){
        return ""
    }
    return element.getAttribute(attribute) || ""
}

function getElement(element, subElement){
    try {
        return element.querySelector(subElement);
    } catch (e) {
        return null
    }
}

function formatDate(date){
    const date = new Date();

}