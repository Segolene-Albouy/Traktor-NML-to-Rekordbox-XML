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
        return f"file://localhost/{dir_path}{file_name}".replace(" ", "%20")
    return ""

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
    product = ET.SubElement(rekordbox, "PRODUCT", Name="Cross DJ Free", Version="3.4.0 (64bits)", Company="MixVibes") # DELETE
    collection = ET.SubElement(rekordbox, "COLLECTION", Entries=str(len(entries)))

    track_nb = 1

    # Process each track
    for entry in entries:
        if get_element(entry, "PRIMARYKEY"):
            continue

        track_id = f"{track_nb:04d}" # get_attribute(entry, "AUDIO_ID")
        track_nb += 1
        title = get_attribute(entry, "TITLE")
        artist = get_attribute(entry, "ARTIST")

        album = get_attribute(get_element(entry, "ALBUM"), "TITLE")
        key = convert_tonality(get_attribute(get_element(entry, "MUSICAL_KEY"), "VALUE"))
        bpm = get_attribute(get_element(entry, "TEMPO"), "BPM") # TODO round

        info = get_element(entry, "INFO")
        genre = get_attribute(info, "GENRE")
        playtime = get_attribute(info, "PLAYTIME")
        playcount = get_attribute(info, "PLAYCOUNT")
        bitrate = get_attribute(info, "BITRATE")
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
            Year=creation_date, AverageBpm=bpm, BitRate=bitrate,
            DateModified=modif_date, DateAdded=import_date, 
            SampleRate="0", PlayCount=playcount, LastPlayed=last_played,
            Rating=ranking, Tonality=key, Location=location)

        # TODO: see if inizio must be set
        tempo = ET.SubElement(track, "TEMPO", Inizio="0", Bpm=bpm, Battito="1")

        i = 1
        for cue in entry.findall("CUE_V2"):
            cue_type = get_attribute(cue, "TYPE")
            start = get_attribute(cue, "START")
            end = get_attribute(cue, "LEN")

            # num = get_attribute(cue, "HOTCUE")
            # before num = "-1" ou num

            position_mark = ET.SubElement(track, "POSITION_MARK", Type=cue_type, Start=start, End=end, Num=f"{i}")
            i += 1

    tree = ET.ElementTree(rekordbox)
    tree.write(xml_file, encoding="utf-8", xml_declaration=True)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python nml_to_rekord.py playlist.nml")
    else:
        nml_file = sys.argv[1]

        if not exists(nml_file):
            print("Usage: python nml_to_rekord.py playlist.nml")

        rekordbox_file = f"{nml_file.split('.')[:-1]}.rekordbox.xml"
        open(rekordbox_file, "w").close()

        convert_nml_to_xml(nml_file, rekordbox_file)
