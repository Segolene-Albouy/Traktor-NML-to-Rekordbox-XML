class Track {
    id = null;
    index = 0;
    title = '';
    artist = '';
    album = '';
    genre = '';
    bpm
    key
    color
    playtime
    playcount
    bitrate
    import_date
    modif_date
    last_played
    ranking
    comments = "";
    location = "";

    constructor(xml_track) {

    }

    from_xml(){

    }

    from_nml(){

    }
}

class Cue {
    cueType = "";
    cueName = "";
    no = null;
    start = 0.0;
    length = 0.0;
    index = -1;
    color = "";
    isBeatGrid = false;
}

class Playlist {
    name = "";
    type = "";
    tracks = [];
}
