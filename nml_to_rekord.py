import xml.etree.ElementTree as ET
from datetime import datetime
import sys
from os.path import exists

def get_attribute(element, attribute):
    if element is not None and attribute in element.attrib:
        return element.get(attribute)
    return ""

def get_element(element, sub_element):
    try:
        return element.find(sub_element)
    except Exception as e:
        return None

def format_date(date):
    try:
        return datetime.strptime(date, "%Y/%m/%d").strftime("%Y-%m-%d")
    except Exception:
        return ""

def get_location_path(location):
    if location is not None:
        dir_path = location.get("DIR").replace("/:","/")
        file_name = location.get("FILE")
        volume = get_attribute(location, "VOLUME")
        disk = f"/{volume}" if not "Mac" in volume else ""
        return f"file://localhost{disk}{dir_path}{file_name}".replace(" ", "%20")
    return ""

def get_track_color(color_nb):
    color_nb_to_rgb = {
        "1": "0xFF0000", # Red
        "2": "0xFFA500", # Orange
        "3": "0xFFFF00", # Yellow
        "4": "0x00FF00", # Green
        "5": "0x0000FF", # Blue
        "6": "0xFF007F", # Rose
        "7": "0x660099", # Violet
    }
    return color_nb_to_rgb.get(color_nb, "")

def get_cue_color(ctype):
    color = map_to_color(ctype)
    rekordbox_colors = {
        "pink": {"R":"222", "G":"68", "B":"207"},        # (1)
        "orchidea": {"R":"180", "G":"50", "B":"255"},    # (2)
        "violet": {"R":"170", "G":"114", "B":"255"},     # (3)
        "mauve": {"R":"100", "G":"115", "B":"255"},      # (4)
        
        "blue": {"R":"48", "G":"90", "B":"255"},         # (5)
        "sky": {"R":"80", "G":"180", "B":"255"},         # (6)
        "cyan": {"R":"0", "G":"224", "B":"255"},         # (7)
        "turquoise": {"R":"31", "G":"163", "B":"146"},   # (8)
        
        "celadon": {"R":"16", "G":"177", "B":"118"},     # (9)
        "green": {"R":"40", "G":"226", "B":"20"},        # (10)
        "lime": {"R":"165", "G":"225", "B":"22"},        # (11)
        "kaki": {"R":"180", "G":"190", "B":"4"},         # (12)
        
        "yellow": {"R":"195", "G":"175", "B":"4"},       # (13)
        "orange": {"R":"224", "G":"100", "B":"27"},      # (14)
        "red": {"R":"230", "G":"40", "B":"40"},          # (15)
        "magenta": {"R":"255", "G":"18", "B":"123"},     # (16)
    }
    return rekordbox_colors.get(color, "")

def map_to_color(ctype):
    ctype = str(ctype).lower().replace(" ", "").replace("-", "")
    color_map = {
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
    return color_map.get(ctype, "")

def set_cue_color(cue, ctype):
    rgb = get_cue_color(ctype)
    if rgb:
        cue.set("Red", rgb["R"])
        cue.set("Green", rgb["G"])
        cue.set("Blue", rgb["B"])
    return cue

def convert_cue_type(traktor_ctype):
    # Rekordbox: Cue = "0", Loop = "4" (Fade-In "1", Fade-Out "2", Load "3" DON'T WORK)
    # Traktor: Cue = "0", Fade-In = "1", Fade-Out = "2", Load = "3", AutoGrid / Grid = "4", Loop = "5"
    return "4" if traktor_ctype == "5" else "0"

def convert_tonality(musical_key):
    musical_key_to_tonality = {
        "0": "C",
        "1": "Db",
        "2": "D",
        "3": "Eb", 
        "4": "E",
        "5": "F",
        "6": "Gb",
        "7": "G",
        "8": "Ab",
        "9": "A",
        "10": "Bb",
        "11": "B",
        "12": "Cm",
        "13": "Dbm",
        "14": "Dm",
        "15": "Ebm",
        "16": "Em",
        "17": "Fm",
        "18": "Gbm",
        "19": "Gm",
        "20": "Abm",
        "21": "Am",
        "22": "Bbm",
        "23": "Bm",
    }
    return musical_key_to_tonality.get(musical_key, "")

def convert_nml_to_xml(nml_file, xml_file):
    tree = ET.parse(nml_file)
    root = tree.getroot()

    entries = root.findall(".//ENTRY")

    rekordbox = ET.Element("DJ_PLAYLISTS", Version="1.0.0")
    collection = ET.SubElement(rekordbox, "COLLECTION", Entries=str(len(entries)))

    track_nb = 1

    # Process each track
    for entry in entries:
        if get_element(entry, "PRIMARYKEY") is not None:
            continue

        track_id = f"{track_nb:04d}"
        track_nb += 1
        title = get_attribute(entry, "TITLE")
        artist = get_attribute(entry, "ARTIST")

        album = get_attribute(get_element(entry, "ALBUM"), "TITLE")
        key = convert_tonality(get_attribute(get_element(entry, "MUSICAL_KEY"), "VALUE"))
        bpm = float(get_attribute(get_element(entry, "TEMPO"), "BPM"))

        info = get_element(entry, "INFO")
        color = get_track_color(get_attribute(info, "COLOR"))
        genre = get_attribute(info, "GENRE")
        playtime = get_attribute(info, "PLAYTIME")
        playcount = get_attribute(info, "PLAYCOUNT")
        bitrate = float(get_attribute(info, "BITRATE")) / 1000
        import_date = format_date(get_attribute(info, "IMPORT_DATE"))
        modif_date = format_date(get_attribute(entry, "MODIFIED_DATE"))
        last_played = format_date(get_attribute(info, "LAST_PLAYED"))
        ranking = get_attribute(info, "RANKING")

        location = get_location_path(get_element(entry, "LOCATION"))

        kind = "3"
        creation_date = "0"
        size = "0"

        # LOUDNESS / COMMENT / SIZE
        
        track = ET.SubElement(collection, "TRACK", 
            TrackID=track_id, Name=title, Artist=artist, 
            Album=album, Genre=genre, Kind=kind, Size=size, 
            TotalTime=playtime, DiscNumber="0", TrackNumber=f"{track_nb}", 
            Year=creation_date, AverageBpm=f"{bpm}", BitRate=f"{bitrate}",
            DateModified=modif_date, DateAdded=import_date, 
            SampleRate="0", PlayCount=playcount, LastPlayed=last_played,
            Rating=ranking, Tonality=key, Location=location, Colour=color)

        i = 0
        inizio = None
        for cue in entry.findall("CUE_V2"):
            cue_type = get_attribute(cue, "TYPE") # type = 0 => autoGrid et hotcues / 4 = loop
            cue_name = get_attribute(cue, "NAME")
            start = float(get_attribute(cue, "START")) / 1000
            length = get_attribute(cue, "LEN")
            no = get_attribute(cue, "HOTCUE")

            if cue_name == "AutoGrid":
                inizio = start
            
            hot_cue = ET.SubElement(track, "POSITION_MARK", Type=convert_cue_type(cue_type), Num=f"{no or i}", Start=f"{start}", Name=cue_name)
            # {no if no != "-1" else i}
            set_cue_color(hot_cue, cue_type, cue_name)

            # Num="-1" allows the cue to be indexed but not displayed in the pad / useful for grid 
            # hot_cue_0 = ET.SubElement(track, "POSITION_MARK", Type=cue_type, Num="-1", Start=f"{start}", Name=cue_name)
            # set_cue_color(hot_cue_0, cue_name if cue_name != "n.n." else cue_type)

            if float(length) != 0:
                end = start + (float(length) / 1000)
                hot_cue.set("End", f"{end}")
                # hot_cue_0.set("End", f"{end}")
            i += 1

        if inizio is not None:
            ET.SubElement(track, "TEMPO", Inizio=f"{inizio}", Bpm=f"{round(bpm, 2)}", Battito="1")

    tree = ET.ElementTree(rekordbox)
    tree.write(xml_file, encoding="utf-8", xml_declaration=True)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python nml_to_rekord.py playlist.nml")
    else:
        nml_file = sys.argv[1]

        if not exists(nml_file):
            print("Usage: python nml_to_rekord.py playlist.nml")

        rekordbox_file = f"{''.join(nml_file.split('.')[:-1])}.rekordbox.xml"
        open(rekordbox_file, "w").close()

        convert_nml_to_xml(nml_file, rekordbox_file)
