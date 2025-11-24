const DATE_FORMAT = {
    traktor: "yyyy/MM/dd",
    rekordbox: "yyyy-MM-dd"
};

const COLOR_MAP = {
    "0xFF0000": "1",
    "0xFFA500": "2",
    "0xFFFF00": "3",
    "0x00FF00": "4",
    "0x0000FF": "5",
    "0xFF007F": "6",
    "0x660099": "7",
};

const TONALITY_MAP = {
    "C": "0", "Db": "1", "D": "2", "Eb": "3", "E": "4", "F": "5",
    "Gb": "6", "G": "7", "Ab": "8", "A": "9", "Bb": "10", "B": "11",
    "Cm": "12", "Dbm": "13", "Dm": "14", "Ebm": "15", "Em": "16", "Fm": "17",
    "Gbm": "18", "Gm": "19", "Abm": "20", "Am": "21", "Bbm": "22", "Bm": "23",
};

const COLOR_NAME_TO_RGB = {
    "pink": {R: "222", G: "68", B: "207"},
    "orchidea": {R: "180", G: "50", B: "255"},
    "violet": {R: "170", G: "114", B: "255"},
    "mauve": {R: "100", G: "115", B: "255"},
    "blue": {R: "48", G: "90", B: "255"},
    "sky": {R: "80", G: "180", B: "255"},
    "cyan": {R: "0", G: "224", B: "255"},
    "turquoise": {R: "31", G: "163", B: "146"},
    "celadon": {R: "16", G: "177", B: "118"},
    "green": {R: "40", G: "226", B: "20"},
    "lime": {R: "165", G: "225", B: "22"},
    "kaki": {R: "180", G: "190", B: "4"},
    "yellow": {R: "195", G: "175", B: "4"},
    "orange": {R: "224", G: "100", B: "27"},
    "red": {R: "230", G: "40", B: "40"},
    "magenta": {R: "255", G: "18", B: "123"},
};

const CUE_COLORS = {
    "0": "blue", "1": "red", "2": "green", "3": "cyan", "4": "lime", "5": "orange",
    "start": "yellow", "intro": "yellow", "break": "turquoise", "bridge": "turquoise",
    "chorus": "rose", "verse": "mauve", "up": "celadon", "buildup": "celadon",
    "drop": "pink", "down": "sky", "outro": "violet", "cue1": "rose",
    "cue2": "magenta", "cue3": "mauve", "cue4": "sky", "AutoGrid": "kaki",
};

let original = null;
let target = null;

function setConversion(o, t) {
    original = o;
    target = t;
}

function getAttribute(element, attribute) {
    return element?.getAttribute(attribute) || "";
}

function getElement(element, subElement) {
    try {
        return element?.querySelector(subElement);
    } catch {
        return null;
    }
}

function formatDate(dateStr) {
    if (!dateStr) return dateStr;
    try {
        const parts = dateStr.split(/[-\/]/);
        if (original === "traktor" && target === "rekordbox") {
            return `${parts[0]}-${parts[1]}-${parts[2]}`;
        }
        if (original === "rekordbox" && target === "traktor") {
            return `${parts[0]}/${parts[1]}/${parts[2]}`;
        }
    } catch {
        return dateStr;
    }
    return dateStr;
}

function today() {
    const d = new Date();
    const year = d.getFullYear();
    const month = String(d.getMonth() + 1).padStart(2, '0');
    const day = String(d.getDate()).padStart(2, '0');
    return target === "traktor" ? `${year}/${month}/${day}` : `${year}-${month}-${day}`;
}

function getTraktorTrackColor(rgbColor) {
    return COLOR_MAP[rgbColor] || "";
}

function getRekordboxTrackColor(colorNb) {
    for (const [rgb, num] of Object.entries(COLOR_MAP)) {
        if (num === colorNb) return rgb;
    }
    return "";
}

function getTrackColor(color) {
    if (target === "traktor") return getTraktorTrackColor(color);
    if (target === "rekordbox") return getRekordboxTrackColor(color);
    return "";
}

function getTraktorCueType(rekordboxType) {
    return rekordboxType === "4" ? "5" : "0";
}

function getRekordboxCueType(traktorType) {
    return traktorType === "5" ? "4" : "0";
}

function getCueType(ctype) {
    if (target === "traktor") return getTraktorCueType(ctype);
    if (target === "rekordbox") return getRekordboxCueType(ctype);
    return "0";
}

function getTraktorKey(tonality) {
    return TONALITY_MAP[tonality] || "0";
}

function getRekordboxTonality(musicalKey) {
    for (const [ton, key] of Object.entries(TONALITY_MAP)) {
        if (key === musicalKey) return ton;
    }
    return "";
}

function getTonalikey(tonalikey) {
    if (target === "rekordbox") return getRekordboxTonality(tonalikey);
    if (target === "traktor") return getTraktorKey(tonalikey);
    return "";
}

function getTraktorLocation(locationStr) {
    const volume = "Macintosh HD";

    if (!locationStr || !locationStr.startsWith("file://localhost")) {
        return {DIR: "/:", FILE: "", VOLUME: volume};
    }

    let path = locationStr.replace("file://localhost", "");
    path = decodeURIComponent(path);

    if (path.length > 3 && path[0] === "/" && path[2] === ":") {
        const driveLetter = path[1].toUpperCase();
        const pathWithoutDrive = path.substring(3);
        const parts = pathWithoutDrive.split("/").filter(p => p);

        const fileName = parts[parts.length - 1] || "";
        const dirParts = parts.slice(0, -1);
        const dirPath = "/:" + [driveLetter + ":", ...dirParts].join("/:") + "/:";

        return {DIR: dirPath, FILE: fileName, VOLUME: volume};
    } else {
        const parts = path.split("/").filter(p => p);
        if (!parts.length) return {DIR: "/:", FILE: "", VOLUME: volume};

        const fileName = parts[parts.length - 1] || "";
        const dirParts = parts.slice(0, -1);
        const dirPath = "/:" + dirParts.join("/:") + "/:";

        return {DIR: dirPath, FILE: fileName, VOLUME: volume};
    }
}

function getRekordboxLocation(location) {
    if (!location) return "";

    const dirPath = getAttribute(location, "DIR").replace(/\/:/g, "/");
    const fileName = getAttribute(location, "FILE");
    const volume = getAttribute(location, "VOLUME");
    const disk = volume.includes("Mac") ? "" : `/${volume}`;

    return `file://localhost${disk}${dirPath}${fileName}`.replace(/ /g, "%20");
}

function getLocation(location) {
    if (target === "traktor") return getTraktorLocation(location);
    if (target === "rekordbox") return getRekordboxLocation(location);
    return "";
}

function mapToColor(ctype) {
    const normalized = String(ctype).toLowerCase().replace(/[ -]/g, "");
    return CUE_COLORS[normalized] || "blue";
}

function setCueColor(cue, ctype, cname) {
    if (ctype === "0" && cname !== "n.n.") {
        ctype = cname;
    }

    const color = mapToColor(ctype);
    const rgb = COLOR_NAME_TO_RGB[color];

    if (rgb) {
        cue.setAttribute("Red", rgb.R);
        cue.setAttribute("Green", rgb.G);
        cue.setAttribute("Blue", rgb.B);
    }
}
