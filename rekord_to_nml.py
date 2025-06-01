import base64
import hashlib
import random
import uuid
import xml.etree.ElementTree as ET
import sys
from os.path import exists

from consts import KEY_TO_CODE
from utils import (
    get_attribute,
    format_date,
    get_tonalikey,
    get_track_color,
    get_cue_type,
    set_conversion,
    get_location,
    set_cue_color,
    today,
)


class Rekordbox2Traktor:
    def __init__(self):
        self.root = None
        self.track = None
        self.cues = []
        self.track_index = 0
        self.cue_index = 0
        self.track_info = {}
        self.tracks = []

    def generate_audio_id(self):
        # AUDIO_ID contains Base64-encoded audio fingerprint data (spectral analysis, transients, beat info) that Traktor uses for validation.
        # Since we can't generate authentic fingerprints without Native Instruments' algorithms, we use a static placeholder.
        # Imported tracks might require re-analysis in Traktor.
        return "AWAWZmRENDMzMzf//////////////////////f/////////////////////s/////////////////////5b///7//////////+//////af/////////////////////+///////////f/////////1n/////////9Y///////////f/////////+r/7///////9XYzMzM0MyMzJUMzNDNDMzRDn//////////////////////f/////////////////////e/////////////////////3r+/+////////7u7u/v////vf//7////////v/+//////+FZneYYQAAAA=="

    def set_track_info(self, track):
        self.track_info = {
            'id': get_attribute(track, "TrackId") or uuid.uuid4().hex[:8],
            'title': get_attribute(track, "Name"),
            'artist': get_attribute(track, "Artist"),
            'album': get_attribute(track, "Album"),
            'key': get_tonalikey(get_attribute(track, "Tonality")),
            'bpm': float(get_attribute(track, "AverageBpm") or "120.0"),
            'color': get_track_color(get_attribute(track, "Colour")),
            'genre': get_attribute(track, "Genre"),
            'playtime': get_attribute(track, "TotalTime"),
            'playcount': get_attribute(track, "PlayCount"),
            'bitrate': float(get_attribute(track, "BitRate") or "320") * 1000,
            'import_date': format_date(get_attribute(track, "DateAdded")),
            'modif_date': format_date(get_attribute(track, "DateModified")),
            'last_played': format_date(get_attribute(track, "LastPlayed")),
            'ranking': get_attribute(track, "Rating"),
            'filesize': get_attribute(track, "Size"),
            'location': get_attribute(track, "Location"),
            'comments': get_attribute(track, "Comments")
        }

        return self.track_info

    @staticmethod
    def sec_2_ms(time_sec):
        return float(time_sec) * 1000 if time_sec else 0

    def add_location(self):
        location_data = get_location(self.track_info['location'])
        location = ET.SubElement(self.track, "LOCATION",
                                 DIR=location_data["DIR"],
                                 FILE=location_data["FILE"],
                                 VOLUME=location_data["VOLUME"],
                                 VOLUMEID=location_data["VOLUME"])
        return location

    def add_album(self):
        if self.track_info['album']:
            album = ET.SubElement(self.track, "ALBUM", TITLE=self.track_info['album'])
            return album
        return None

    def add_modification_info(self):
        modif = ET.SubElement(self.track, "MODIFICATION_INFO", AUTHOR_TYPE="user")
        return modif

    def add_info(self):
        info_attrs = {
            "BITRATE": str(int(self.track_info['bitrate'])),
            "GENRE": self.track_info['genre'],
            "KEY": KEY_TO_CODE[self.track_info['key']],
            "PLAYCOUNT": self.track_info['playcount'],
            "PLAYTIME": self.track_info['playtime'],
            "PLAYTIME_FLOAT": f"{float(self.track_info['playtime']):.6f}",
            "RANKING": self.track_info['ranking'],
            "IMPORT_DATE": self.track_info['import_date'],
            "LAST_PLAYED": self.track_info['last_played'],
            "FLAGS": "12",
            # "FILESIZE": str(int(float(self.track_info['filesize']) / 1024)) if self.track_info['filesize'] else "0",
            "COLOR": self.track_info['color']
        }

        if self.track_info['comments']:
            info_attrs["COMMENT"] = self.track_info['comments']

        info = ET.SubElement(self.track, "INFO", **info_attrs)
        return info

    def add_tempo(self):
        tempo = ET.SubElement(self.track, "TEMPO",
                              BPM=f"{self.track_info['bpm']:.6f}",
                              BPM_QUALITY="100.000000")
        return tempo

    def add_loudness(self):
        loudness = ET.SubElement(self.track, "LOUDNESS",
                                 PEAK_DB="-1.0",
                                 PERCEIVED_DB="-1.0",
                                 ANALYZED_DB="-1.0")
        return loudness

    def add_musical_key(self):
        musical_key = ET.SubElement(self.track, "MUSICAL_KEY", VALUE=self.track_info['key'])
        return musical_key

    def add_beatmarker(self, start_ms, bpm, is_autogrid=False):
        name = "AutoGrid" if is_autogrid else "Beat Marker"

        cue = ET.SubElement(self.track, "CUE_V2",
                            NAME=name,
                            DISPL_ORDER="0",
                            TYPE="4",
                            START=f"{start_ms:.6f}",
                            LEN="0.000000",
                            REPEATS="-1",
                            HOTCUE="-1")

        grid = ET.SubElement(cue, "GRID", BPM=f"{bpm:.6f}")

        return cue

    def add_autogrid(self, start_ms):
        cue = ET.SubElement(self.track, "CUE_V2",
                            NAME="AutoGrid",
                            DISPL_ORDER="0",
                            TYPE="0",
                            START=f"{start_ms:.6f}",
                            LEN="0.000000",
                            REPEATS="-1",
                            HOTCUE="0",
                            COLOR="#FFFFFF")

        return cue

    def add_cue(self, position_mark):
        cue_type = get_attribute(position_mark, "Type")
        start_sec = get_attribute(position_mark, "Start")
        end_sec = get_attribute(position_mark, "End")
        num = get_attribute(position_mark, "Num")
        name = get_attribute(position_mark, "Name") or "n.n."

        start_ms = self.sec_2_ms(start_sec)
        loop_length = 0
        if end_sec:
            loop_length = self.sec_2_ms(end_sec) - start_ms

        hotcue = num if num and num != "-1" else str(self.cue_index)

        cue_attrs = {
            "NAME": name,
            "DISPL_ORDER": "0",
            "TYPE": get_cue_type(cue_type),
            "START": f"{start_ms:.6f}",
            "LEN": f"{loop_length:.6f}",
            "REPEATS": "-1",
            "HOTCUE": hotcue
        }

        cue = ET.SubElement(self.track, "CUE_V2", **cue_attrs)
        r = get_attribute(position_mark, "Red")
        g = get_attribute(position_mark, "Green")
        b = get_attribute(position_mark, "Blue")

        if r and g and b:
            set_cue_color(cue, r=r, g=g, b=b)

        self.cue_index += 1
        return cue

    def process_tempo(self, track):
        tempo_elements = track.findall("TEMPO")

        if not tempo_elements:
            self.add_beatmarker(0, self.track_info['bpm'], is_autogrid=True)
            self.add_autogrid(0)

        elif len(tempo_elements) == 1:
            tempo = tempo_elements[0]
            start_sec = float(get_attribute(tempo, "Inizio") or "0")
            bpm = float(get_attribute(tempo, "Bpm") or str(self.track_info['bpm']))
            start_ms = self.sec_2_ms(start_sec)

            self.add_beatmarker(start_ms, bpm, is_autogrid=True)
            self.add_autogrid(start_ms)

        else:
            for i, tempo in enumerate(tempo_elements):
                start_sec = float(get_attribute(tempo, "Inizio") or "0")
                bpm = float(get_attribute(tempo, "Bpm") or str(self.track_info['bpm']))
                start_ms = self.sec_2_ms(start_sec)

                is_autogrid = (i == 0)
                self.add_beatmarker(start_ms, bpm, is_autogrid=is_autogrid)

                if is_autogrid:
                    self.add_autogrid(start_ms)

    def process_cues(self, track):
        position_marks = track.findall("POSITION_MARK")

        for position_mark in position_marks:
            name = get_attribute(position_mark, "Name")
            if name == "AutoGrid":
                continue

            self.add_cue(position_mark)

    def reset_track(self):
        self.track = None
        self.cues = []
        self.cue_index = 1
        self.track_info = {}

    def add_entry(self, collection):
        info = self.track_info

        entry = ET.SubElement(
            collection,
            "ENTRY",
            MODIFIED_DATE= info['modif_date'] or today(),
            MODIFIED_TIME="0", # TODO change
            AUDIO_ID=self.generate_audio_id(),
            TITLE=info['title'],
            ARTIST=info['artist']
        )
        return entry

    def add_playlist(self, name="collection"):
        playlists = ET.SubElement(self.root, "PLAYLISTS")
        root_node = ET.SubElement(playlists, "NODE", TYPE="FOLDER", NAME="$ROOT")
        subnodes = ET.SubElement(root_node, "SUBNODES", COUNT="1")

        playlist_node = ET.SubElement(subnodes, "NODE", TYPE="PLAYLIST", NAME=name)
        playlist = ET.SubElement(
            playlist_node, "PLAYLIST",
            ENTRIES=str(len(self.tracks)),
            TYPE="LIST",
            UUID=uuid.uuid4().hex
        )

        for track_loc in self.tracks:
            entry = ET.SubElement(playlist, "ENTRY")
            primary_key = ET.SubElement(entry, "PRIMARYKEY", TYPE="TRACK", KEY=track_loc)

    def process_track(self, track, collection):
        self.reset_track()

        self.set_track_info(track)
        self.track = self.add_entry(collection)

        self.add_location()
        self.add_album()
        self.add_modification_info()
        self.add_info()
        self.add_tempo()
        self.add_loudness()
        self.add_musical_key()

        self.process_tempo(track)
        self.process_cues(track)

        return True

    def add_head(self):
        head = ET.SubElement(self.root, "HEAD", COMPANY="www.native-instruments.com", PROGRAM="Traktor Pro 4")
        return head

    def add_collection(self, entries):
        collection = ET.SubElement(self.root, "COLLECTION", ENTRIES=str(len(entries)))
        return collection

    def add_sets(self, entries=[]):
        sets = ET.SubElement(self.root, "SETS", ENTRIES=str(len(entries)))
        return sets

    def add_indexing(self):
        indexing = ET.SubElement(self.root, "INDEXING")
        return indexing

    def convert_xml_to_nml(self, xml_file, nml_file):
        tree = ET.parse(xml_file)
        root = tree.getroot()

        self.root = ET.Element("NML", VERSION="20")

        entries = root.findall(".//TRACK")

        self.add_head()
        collection = self.add_collection(entries)

        self.tracks = []

        for track in entries:
            if self.process_track(track, collection):
                loc = get_location(get_attribute(track, "Location"))
                self.tracks.append(f"{loc['VOLUME']}{loc['DIR']}{loc['FILE']}")
                self.track_index += 1

        self.add_sets()
        self.add_playlist()
        self.add_indexing()

        tree = ET.ElementTree(self.root)
        tree.write(nml_file, encoding="utf-8", xml_declaration=True, short_empty_elements=False)


if __name__ == "__main__":
    set_conversion("rekordbox", "traktor")
    if len(sys.argv) < 2:
        print("Usage: python rekord_to_nml.py playlist.rekordbox.xml")
    else:
        xml_file = sys.argv[1]

        if not exists(xml_file):
            print("Usage: python rekord_to_nml.py playlist.rekordbox.xml")
            sys.exit(1)

        filepath = xml_file.replace(".xml", "").replace(".rekordbox", "")
        nml_file = f"{filepath}.nml"
        open(nml_file, "w").close()

        converter = Rekordbox2Traktor()
        converter.convert_xml_to_nml(xml_file, nml_file)

        print(f"☕️ {xml_file} was converted to {nml_file}!")