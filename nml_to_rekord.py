import xml.etree.ElementTree as ET
import sys
from os.path import exists

from utils import (
    get_attribute,
    format_date,
    get_element,
    get_tonalikey,
    get_track_color,
    get_cue_type,
    set_conversion,
    get_location,
    set_cue_color
)


class Traktor2Rekordbox:
    def __init__(self):
        """Initialize the converter with default values."""
        self.track = None
        self.cues = []
        self.track_index = 0
        self.cue_index = 0
        self.added_tempos = 0
        self.track_info = {}

    def set_track_info(self, entry):
        """Extract track metadata from NML entry."""
        info = get_element(entry, "INFO")

        self.track_info = {
            'title': get_attribute(entry, "TITLE"),
            'artist': get_attribute(entry, "ARTIST"),
            'album': get_attribute(get_element(entry, "ALBUM"), "TITLE"),
            'key': get_tonalikey(get_attribute(get_element(entry, "MUSICAL_KEY"), "VALUE")),
            'bpm': float(get_attribute(get_element(entry, "TEMPO"), "BPM")),
            'color': get_track_color(get_attribute(info, "COLOR")),
            'genre': get_attribute(info, "GENRE"),
            'playtime': get_attribute(info, "PLAYTIME"),
            'playcount': get_attribute(info, "PLAYCOUNT"),
            'bitrate': float(get_attribute(info, "BITRATE")) / 1000,
            'import_date': format_date(get_attribute(info, "IMPORT_DATE")),
            'modif_date': format_date(get_attribute(entry, "MODIFIED_DATE")),
            'last_played': format_date(get_attribute(info, "LAST_PLAYED")),
            'ranking': get_attribute(info, "RANKING")
        }

        return self.track_info

    @staticmethod
    def is_beatgrid(cue):
        """
        Check if a CUE_V2 element is a beatgrid marker (AutoGrid or Beat Marker with GRID element)
        """
        cue_name = get_attribute(cue, "NAME")
        grid_element = cue.find("GRID")
        return (cue_name in ["AutoGrid", "Beat Marker"]) and grid_element is not None

    @staticmethod
    def ms_2_sec(time_ms):
        """Convert time from milliseconds to seconds."""
        return float(time_ms) / 1000 if time_ms else 0

    def add_tempo(self, start, bpm, metro=None):
        bpm_value = round(float(bpm), 2)
        if metro:
            ET.SubElement(self.track, "TEMPO", Inizio=f"{start}", Bpm=f"{bpm_value}", Metro=metro, Battito="1")
        else:
            ET.SubElement(self.track, "TEMPO", Inizio=f"{start}", Bpm=f"{bpm_value}", Battito="1")
        self.added_tempos += 1

    def add_beatgrid(self, cue):
        start_seconds = self.ms_2_sec(get_attribute(cue, "START"))
        grid_element = cue.find("GRID")
        grid_bpm = get_attribute(grid_element, "BPM")

        if grid_bpm:
            self.add_tempo(start_seconds, grid_bpm, metro="4/4")

    def add_cue(self, cue):
        """
        Create a POSITION_MARK element from a regular cue/loop.

        Args:
            cue: CUE_V2 XML element containing cue/loop information
        """
        cue_type = get_attribute(cue, "TYPE")
        cue_name = get_attribute(cue, "NAME")
        start_seconds = self.ms_2_sec(get_attribute(cue, "START"))
        length = get_attribute(cue, "LEN")
        hotcue_no = get_attribute(cue, "HOTCUE")

        # Use hotcue number if available, otherwise use current index
        c_num = hotcue_no if hotcue_no and hotcue_no != "-1" else str(self.cue_index)

        position_mark = ET.SubElement(
            self.track,
            "POSITION_MARK",
            Type=get_cue_type(cue_type),
            Num=c_num,
            Start=f"{start_seconds}",
            Name=cue_name
        )

        set_cue_color(position_mark, ctype=cue_type, cname=cue_name)

        # Add end time for loops (when length > 0)
        if length and float(length) != 0:
            end_seconds = start_seconds + self.ms_2_sec(length)
            position_mark.set("End", f"{end_seconds}")

        # Num="-1" allows the cue to be indexed but not displayed in the pad / useful for grid

        # hidden_cue = ET.SubElement(self.track, "POSITION_MARK",  Type=get_cue_type(cue_type), Num="-1", Start=f"{start_seconds}", Name=cue_name)
        # set_cue_color(hidden_cue, ctype=cue_type, cname=cue_name)
        # if length and float(length) != 0:
        #     hidden_cue.set("End", f"{end_seconds}")

        self.cue_index += 1

    def process_cue(self, cue):
        """
        Process a single CUE_V2 element and add appropriate elements to the track.

        Args:
            cue: CUE_V2 XML element from NML
        """
        if self.is_beatgrid(cue):
            self.add_beatgrid(cue)
        else:
            self.add_cue(cue)

    def default_tempo(self):
        """
        Add a default TEMPO element if no beatgrid markers were processed
        for tracks that don't have flexible beatgrids.
        """
        if self.added_tempos == 0:
            # Look for AutoGrid cue to get the start position
            autogrid_start = None
            for cue in self.cues:
                if get_attribute(cue, "NAME") == "AutoGrid":
                    autogrid_start = self.ms_2_sec(get_attribute(cue, "START"))
                    break

            if autogrid_start is not None:
                self.add_tempo(autogrid_start, self.track_info['bpm'])

    def add_track(self, collection, location):
        """
        Create the main TRACK element with all metadata.

        Args:
            collection: Parent COLLECTION element
            location: Track file location

        Returns:
            ET.Element: Created TRACK element
        """
        kind = "3"
        creation_date = "0"
        size = "0"

        info = self.track_info
        return ET.SubElement(collection, "TRACK",
             TrackID=f"{self.track_index:09d}", Name=info['title'], Artist=info['artist'],
             Album=info['album'], Genre=info['genre'], Kind=kind, Size=size,
             TotalTime=info['playtime'], DiscNumber="0", TrackNumber=f"{self.track_index}",
             Year=creation_date, AverageBpm=f"{info['bpm']}", BitRate=f"{info['bitrate']}",
             DateModified=info['modif_date'], DateAdded=info['import_date'],
             SampleRate="0", PlayCount=info['playcount'], LastPlayed=info['last_played'],
             Rating=info['ranking'], Tonality=info['key'], Location=location,
             Colour=info['color'])

    def reset_track(self):
        """Reset internal state for processing a new track."""
        self.track = None
        self.cues = []
        self.cue_index = 0
        self.added_tempos = 0
        self.track_info = {}

    @staticmethod
    def is_playlist(entry):
        return get_element(entry, "PRIMARYKEY") is not None

    def process_cues(self, entry):
        self.cues = entry.findall("CUE_V2")
        for cue in self.cues:
            self.process_cue(cue)

    def process_entry(self, entry, collection):
        """
        Process a single NML entry and convert it to Rekordbox format.

        Args:
            entry: NML ENTRY element
            collection: Rekordbox COLLECTION element

        Returns:
            bool: True if track was processed, False if skipped
        """
        if self.is_playlist(entry):
            # TODO: Handle playlist entries
            return False

        self.reset_track()

        self.set_track_info(entry)
        location = get_location(get_element(entry, "LOCATION"))

        self.track = self.add_track(collection, location)

        # Process all cues and tempo markers
        self.process_cues(entry)

        # Add fallback tempo if no beat grid markers were found
        self.default_tempo()

        return True

    def convert_nml_to_xml(self, nml_file, xml_file):
        """
        nml_file: Path to input NML file
        xml_file: Path to output XML file
        """
        tree = ET.parse(nml_file)
        root = tree.getroot()
        entries = root.findall(".//ENTRY")

        rekordbox = ET.Element("DJ_PLAYLISTS", Version="1.0.0")
        track_count = sum(1 for entry in entries if not self.is_playlist(entry))
        collection = ET.SubElement(rekordbox, "COLLECTION", Entries=str(track_count))

        # Process each track
        for entry in entries:
            if self.process_entry(entry, collection):
                self.track_index += 1

        tree = ET.ElementTree(rekordbox)
        tree.write(xml_file, encoding="utf-8", xml_declaration=True)


if __name__ == "__main__":
    set_conversion("traktor", "rekordbox")
    if len(sys.argv) < 2:
        print("Usage: python nml_to_rekord.py playlist.nml")
    else:
        nml_file = sys.argv[1]

        if not exists(nml_file):
            print("Usage: python nml_to_rekord.py playlist.nml")

        rekordbox_file = f"{''.join(nml_file.split('.')[:-1])}.rekordbox.xml"
        open(rekordbox_file, "w").close()

        converter = Traktor2Rekordbox()
        converter.convert_nml_to_xml(nml_file, rekordbox_file)
