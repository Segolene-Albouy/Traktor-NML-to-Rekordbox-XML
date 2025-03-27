import xml.etree.ElementTree as ET
import sys
from os.path import exists

from consts import RB_COLORS, CUE_COLORS
from utils import get_attribute, format_date, get_element, get_tonalikey, get_track_color, get_cue_type, set_conversion, \
    get_location


def get_cue_color(ctype):
    color = map_to_color(ctype)
    return RB_COLORS.get(color, "")

def map_to_color(ctype):
    ctype = str(ctype).lower().replace(" ", "").replace("-", "")
    return CUE_COLORS.get(ctype, "blue")

def set_cue_color(cue, ctype, cname):
    if ctype == "0" and cname != "n.n.":
        ctype = cname

    rgb = get_cue_color(ctype)
    if rgb:
        cue.set("Red", rgb["R"])
        cue.set("Green", rgb["G"])
        cue.set("Blue", rgb["B"])
    return cue

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
        key = get_tonalikey(get_attribute(get_element(entry, "MUSICAL_KEY"), "VALUE"))
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

        location = get_location(get_element(entry, "LOCATION"))

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
            
            hot_cue = ET.SubElement(track, "POSITION_MARK", Type=get_cue_type(cue_type), Num=f"{no or i}", Start=f"{start}", Name=cue_name)
            # {no if no != "-1" else i}
            set_cue_color(hot_cue, cue_type, cue_name)

            # Num="-1" allows the cue to be indexed but not displayed in the pad / useful for grid 
            # hot_cue_0 = ET.SubElement(track, "POSITION_MARK", Type=cue_type, Num="-1", Start=f"{start}", Name=cue_name)
            # set_cue_color(hot_cue_0, cue_type, cue_name)

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
    set_conversion("rekordbox", "traktor")
    if len(sys.argv) < 2:
        print("Usage: python nml_to_rekord.py playlist.nml")
    else:
        nml_file = sys.argv[1]

        if not exists(nml_file):
            print("Usage: python nml_to_rekord.py playlist.nml")

        rekordbox_file = f"{''.join(nml_file.split('.')[:-1])}.rekordbox.xml"
        open(rekordbox_file, "w").close()

        convert_nml_to_xml(nml_file, rekordbox_file)
