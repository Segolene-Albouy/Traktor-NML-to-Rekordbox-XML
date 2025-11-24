class Rekordbox2Traktor {
    constructor() {
        this.root = null;
        this.track = null;
        this.cues = [];
        this.trackIndex = 0;
        this.cueIndex = 0;
        this.trackInfo = {};
        this.tracks = [];
    }

    generateAudioId() {
        return "AWAWZmRENDMzMzf//////////////////////f/////////////////////s/////////////////////5b///7//////////+//////af/////////////////////+///////////f/////////1n/////////9Y///////////f/////////+r/7///////9XYzMzM0MyMzJUMzNDNDMzRDn//////////////////////f/////////////////////e/////////////////////3r+/+////////7u7u/v////vf//7////////v/+//////+FZneYYQAAAA==";
    }

    setTrackInfo(track) {
        this.trackInfo = {
            id: getAttribute(track, "TrackID") || Math.random().toString(36).substr(2, 8),
            title: getAttribute(track, "Name"),
            artist: getAttribute(track, "Artist"),
            album: getAttribute(track, "Album"),
            key: getTonalikey(getAttribute(track, "Tonality")),
            bpm: parseFloat(getAttribute(track, "AverageBpm") || "120.0"),
            color: getTrackColor(getAttribute(track, "Colour")),
            genre: getAttribute(track, "Genre"),
            playtime: getAttribute(track, "TotalTime"),
            playcount: getAttribute(track, "PlayCount"),
            bitrate: parseFloat(getAttribute(track, "BitRate") || "320") * 1000,
            import_date: formatDate(getAttribute(track, "DateAdded")),
            modif_date: formatDate(getAttribute(track, "DateModified")),
            last_played: formatDate(getAttribute(track, "LastPlayed")),
            ranking: getAttribute(track, "Rating"),
            filesize: getAttribute(track, "Size"),
            location: getAttribute(track, "Location"),
            comments: getAttribute(track, "Comments")
        };

        return this.trackInfo;
    }

    static sec2ms(timeSec) {
        return timeSec ? parseFloat(timeSec) * 1000 : 0;
    }

    addLocation() {
        const locationData = getLocation(this.trackInfo.location);
        const location = document.createElementNS(null, "LOCATION");
        location.setAttribute("DIR", locationData.DIR);
        location.setAttribute("FILE", locationData.FILE);
        location.setAttribute("VOLUME", locationData.VOLUME);
        location.setAttribute("VOLUMEID", locationData.VOLUME);
        this.track.appendChild(location);
        return location;
    }

    addAlbum() {
        if (this.trackInfo.album) {
            const album = document.createElementNS(null, "ALBUM");
            album.setAttribute("TITLE", this.trackInfo.album);
            this.track.appendChild(album);
            return album;
        }
        return null;
    }

    addModificationInfo() {
        const modif = document.createElementNS(null, "MODIFICATION_INFO");
        modif.setAttribute("AUTHOR_TYPE", "user");
        this.track.appendChild(modif);
        return modif;
    }

    addInfo() {
        const info = document.createElementNS(null, "INFO");
        info.setAttribute("BITRATE", String(Math.floor(this.trackInfo.bitrate)));
        info.setAttribute("GENRE", this.trackInfo.genre);
        info.setAttribute("KEY", KEY_TO_CODE[this.trackInfo.key] || "10d");
        info.setAttribute("PLAYCOUNT", this.trackInfo.playcount);
        info.setAttribute("PLAYTIME", this.trackInfo.playtime);
        info.setAttribute("PLAYTIME_FLOAT", parseFloat(this.trackInfo.playtime).toFixed(6));
        info.setAttribute("RANKING", this.trackInfo.ranking);
        info.setAttribute("IMPORT_DATE", this.trackInfo.import_date);
        info.setAttribute("LAST_PLAYED", this.trackInfo.last_played);
        info.setAttribute("FLAGS", "12");
        info.setAttribute("COLOR", this.trackInfo.color);

        if (this.trackInfo.comments) {
            info.setAttribute("COMMENT", this.trackInfo.comments);
        }

        this.track.appendChild(info);
        return info;
    }

    addTempo() {
        const tempo = document.createElementNS(null, "TEMPO");
        tempo.setAttribute("BPM", this.trackInfo.bpm.toFixed(6));
        tempo.setAttribute("BPM_QUALITY", "100.000000");
        this.track.appendChild(tempo);
        return tempo;
    }

    addLoudness() {
        const loudness = document.createElementNS(null, "LOUDNESS");
        loudness.setAttribute("PEAK_DB", "-1.0");
        loudness.setAttribute("PERCEIVED_DB", "-1.0");
        loudness.setAttribute("ANALYZED_DB", "-1.0");
        this.track.appendChild(loudness);
        return loudness;
    }

    addMusicalKey() {
        const musicalKey = document.createElementNS(null, "MUSICAL_KEY");
        musicalKey.setAttribute("VALUE", this.trackInfo.key);
        this.track.appendChild(musicalKey);
        return musicalKey;
    }

    addBeatmarker(startMs, bpm, isAutogrid = false) {
        const name = isAutogrid ? "AutoGrid" : "Beat Marker";
        const cue = document.createElementNS(null, "CUE_V2");
        cue.setAttribute("NAME", name);
        cue.setAttribute("DISPL_ORDER", "0");
        cue.setAttribute("TYPE", "4");
        cue.setAttribute("START", startMs.toFixed(6));
        cue.setAttribute("LEN", "0.000000");
        cue.setAttribute("REPEATS", "-1");
        cue.setAttribute("HOTCUE", "-1");

        const grid = document.createElementNS(null, "GRID");
        grid.setAttribute("BPM", bpm.toFixed(6));
        cue.appendChild(grid);

        this.track.appendChild(cue);
        return cue;
    }

    addAutogrid(startMs) {
        const cue = document.createElementNS(null, "CUE_V2");
        cue.setAttribute("NAME", "AutoGrid");
        cue.setAttribute("DISPL_ORDER", "0");
        cue.setAttribute("TYPE", "0");
        cue.setAttribute("START", startMs.toFixed(6));
        cue.setAttribute("LEN", "0.000000");
        cue.setAttribute("REPEATS", "-1");
        cue.setAttribute("HOTCUE", "0");
        cue.setAttribute("COLOR", "#FFFFFF");

        this.track.appendChild(cue);
        return cue;
    }

    addCue(positionMark) {
        const cueType = getAttribute(positionMark, "Type");
        const startSec = getAttribute(positionMark, "Start");
        const endSec = getAttribute(positionMark, "End");
        const num = getAttribute(positionMark, "Num");
        const name = getAttribute(positionMark, "Name") || "n.n.";

        const startMs = Rekordbox2Traktor.sec2ms(startSec);
        let loopLength = 0;
        if (endSec) {
            loopLength = Rekordbox2Traktor.sec2ms(endSec) - startMs;
        }

        const hotcue = (num && num !== "-1") ? num : String(this.cueIndex);

        const cue = document.createElementNS(null, "CUE_V2");
        cue.setAttribute("NAME", name);
        cue.setAttribute("DISPL_ORDER", "0");
        cue.setAttribute("TYPE", getCueType(cueType));
        cue.setAttribute("START", startMs.toFixed(6));
        cue.setAttribute("LEN", loopLength.toFixed(6));
        cue.setAttribute("REPEATS", "-1");
        cue.setAttribute("HOTCUE", hotcue);

        const r = getAttribute(positionMark, "Red");
        const g = getAttribute(positionMark, "Green");
        const b = getAttribute(positionMark, "Blue");

        if (r && g && b) {
            const hexColor = `#${parseInt(r).toString(16).padStart(2, '0')}${parseInt(g).toString(16).padStart(2, '0')}${parseInt(b).toString(16).padStart(2, '0')}`.toUpperCase();
            cue.setAttribute("COLOR", hexColor);
        }

        this.track.appendChild(cue);
        this.cueIndex++;
        return cue;
    }

    processTempo(track) {
        const tempoElements = Array.from(track.querySelectorAll("TEMPO"));

        if (tempoElements.length === 0) {
            this.addBeatmarker(0, this.trackInfo.bpm, true);
            this.addAutogrid(0);
        } else if (tempoElements.length === 1) {
            const tempo = tempoElements[0];
            const startSec = parseFloat(getAttribute(tempo, "Inizio") || "0");
            const bpm = parseFloat(getAttribute(tempo, "Bpm") || String(this.trackInfo.bpm));
            const startMs = Rekordbox2Traktor.sec2ms(startSec);

            this.addBeatmarker(startMs, bpm, true);
            this.addAutogrid(startMs);
        } else {
            tempoElements.forEach((tempo, i) => {
                const startSec = parseFloat(getAttribute(tempo, "Inizio") || "0");
                const bpm = parseFloat(getAttribute(tempo, "Bpm") || String(this.trackInfo.bpm));
                const startMs = Rekordbox2Traktor.sec2ms(startSec);

                const isAutogrid = i === 0;
                this.addBeatmarker(startMs, bpm, isAutogrid);

                if (isAutogrid) {
                    this.addAutogrid(startMs);
                }
            });
        }
    }

    processCues(track) {
        const positionMarks = Array.from(track.querySelectorAll("POSITION_MARK"));

        for (const positionMark of positionMarks) {
            const name = getAttribute(positionMark, "Name");
            if (name === "AutoGrid") continue;

            this.addCue(positionMark);
        }
    }

    resetTrack() {
        this.track = null;
        this.cues = [];
        this.cueIndex = 1;
        this.trackInfo = {};
    }

    addEntry(collection) {
        const info = this.trackInfo;
        const entry = document.createElementNS(null, "ENTRY");
        entry.setAttribute("MODIFIED_DATE", info.modif_date || today());
        entry.setAttribute("MODIFIED_TIME", "0");
        entry.setAttribute("AUDIO_ID", this.generateAudioId());
        entry.setAttribute("TITLE", info.title);
        entry.setAttribute("ARTIST", info.artist);

        collection.appendChild(entry);
        return entry;
    }

    addPlaylist(name = "collection") {
        const playlists = document.createElementNS(null, "PLAYLISTS");
        this.root.appendChild(playlists);

        const rootNode = document.createElementNS(null, "NODE");
        rootNode.setAttribute("TYPE", "FOLDER");
        rootNode.setAttribute("NAME", "$ROOT");
        playlists.appendChild(rootNode);

        const subnodes = document.createElementNS(null, "SUBNODES");
        subnodes.setAttribute("COUNT", "1");
        rootNode.appendChild(subnodes);

        const playlistNode = document.createElementNS(null, "NODE");
        playlistNode.setAttribute("TYPE", "PLAYLIST");
        playlistNode.setAttribute("NAME", name);
        subnodes.appendChild(playlistNode);

        const playlist = document.createElementNS(null, "PLAYLIST");
        playlist.setAttribute("ENTRIES", String(this.tracks.length));
        playlist.setAttribute("TYPE", "LIST");
        playlist.setAttribute("UUID", this.generateUUID());
        playlistNode.appendChild(playlist);

        for (const trackLoc of this.tracks) {
            const entry = document.createElementNS(null, "ENTRY");
            playlist.appendChild(entry);

            const primaryKey = document.createElementNS(null, "PRIMARYKEY");
            primaryKey.setAttribute("TYPE", "TRACK");
            primaryKey.setAttribute("KEY", trackLoc);
            entry.appendChild(primaryKey);
        }
    }

    generateUUID() {
        return 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'.replace(/x/g, () =>
            Math.floor(Math.random() * 16).toString(16)
        );
    }

    processTrack(track, collection) {
        this.resetTrack();
        this.setTrackInfo(track);
        this.track = this.addEntry(collection);

        this.addLocation();
        this.addAlbum();
        this.addModificationInfo();
        this.addInfo();
        this.addTempo();
        this.addLoudness();
        this.addMusicalKey();

        this.processTempo(track);
        this.processCues(track);

        return true;
    }

    addHead() {
        const head = document.createElementNS(null, "HEAD");
        head.setAttribute("COMPANY", "www.native-instruments.com");
        head.setAttribute("PROGRAM", "Traktor Pro 4");
        this.root.appendChild(head);
        return head;
    }

    addCollection(entries) {
        const collection = document.createElementNS(null, "COLLECTION");
        collection.setAttribute("ENTRIES", String(entries.length));
        this.root.appendChild(collection);
        return collection;
    }

    addSets(entries = []) {
        const sets = document.createElementNS(null, "SETS");
        sets.setAttribute("ENTRIES", String(entries.length));
        this.root.appendChild(sets);
        return sets;
    }

    addIndexing() {
        const indexing = document.createElementNS(null, "INDEXING");
        this.root.appendChild(indexing);
        return indexing;
    }

    convertXmlToNml(xmlContent) {
        setConversion("rekordbox", "traktor");

        const parser = new DOMParser();
        const xmlDoc = parser.parseFromString(xmlContent, "text/xml");
        const root = xmlDoc.documentElement;

        const nmlDoc = document.implementation.createDocument(null, "NML");
        this.root = nmlDoc.documentElement;
        this.root.setAttribute("VERSION", "20");

        const entries = Array.from(root.querySelectorAll("TRACK"));

        this.addHead();
        const collection = this.addCollection(entries);

        this.tracks = [];

        for (const track of entries) {
            if (this.processTrack(track, collection)) {
                const loc = getLocation(getAttribute(track, "Location"));
                this.tracks.push(`${loc.VOLUME}${loc.DIR}${loc.FILE}`);
                this.trackIndex++;
            }
        }

        this.addSets();
        this.addPlaylist();
        this.addIndexing();

        const serializer = new XMLSerializer();
        return '<?xml version="1.0" encoding="utf-8"?>\n' + serializer.serializeToString(this.root);
    }
}

const KEY_TO_CODE = {
    "0": "10d", "1": "11d", "2": "12d", "3": "1d", "4": "2d", "5": "3d",
    "6": "4d", "7": "5d", "8": "6d", "9": "7d", "10": "8d", "11": "9d",
    "12": "10m", "13": "11m", "14": "12m", "15": "1m", "16": "2m", "17": "3m",
    "18": "4m", "19": "5m", "20": "6m", "21": "7m", "22": "8m", "23": "9m",
};

async function convertXMLToNML(xmlContent) {
    const converter = new Rekordbox2Traktor();
    return converter.convertXmlToNml(xmlContent);
}
