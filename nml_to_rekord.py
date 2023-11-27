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
        windows_prefix = "" if dir_path.startswith("/Users") else "/D:"
        return f"file://localhost{windows_prefix}{dir_path}{file_name}".replace(" ", "%20")
    return ""

def get_color(color_nb):
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
        color = get_color(get_attribute(info, "COLOR"))
        genre = get_attribute(info, "GENRE")
        playtime = get_attribute(info, "PLAYTIME")
        playcount = get_attribute(info, "PLAYCOUNT")
        bitrate = float(get_attribute(info, "BITRATE")) / 1000
        import_date = format_date(get_attribute(info, "IMPORT_DATE"))
        last_played = format_date(get_attribute(info, "LAST_PLAYED"))
        ranking = get_attribute(info, "RANKING")

        location = get_location_path(get_element(entry, "LOCATION"))

        modif_date = "1970-01-01"
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
            Rating=ranking, Tonality=key, Location=location, Color=color)

        i = 0
        inizio = None
        for cue in entry.findall("CUE_V2"):
            cue_type = get_attribute(cue, "TYPE") # type = 0 => autoGrid et hotcues / 4 = loop
            cue_name = get_attribute(cue, "NAME")
            start = float(get_attribute(cue, "START")) / 1000
            length = get_attribute(cue, "LEN")

            if cue_name == "AutoGrid":
                inizio = start
                cue_type = "0"
            
            hot_cue = ET.SubElement(track, "POSITION_MARK", Type=cue_type, Num=f"{i}", Start=f"{start}", Name=cue_name)
            # hot_cue_0 is for cues to be indexed
            hot_cue_0 = ET.SubElement(track, "POSITION_MARK", Type=cue_type, Num=f"-1", Start=f"{start}", Name=cue_name)

            if float(length) != 0:
                end = start + (float(length) / 1000)
                hot_cue.set("End", f"{end}")
                hot_cue_0.set("End", f"{end}")
                hot_cue.set("Type", "4")
                hot_cue_0.set("Type", "4")
                cue_type = "0"

            i += 1

        if inizio is not None:
            tempo = ET.SubElement(track, "TEMPO", Inizio=f"{inizio}", Bpm=f"{round(bpm, 2)}", Battito="1")

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
