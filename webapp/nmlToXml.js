class Traktor2Rekordbox {
    constructor() {
        this.track = null;
        this.cues = [];
        this.trackIndex = 0;
        this.cueIndex = 0;
        this.addedTempos = 0;
        this.trackInfo = {};
        this.trackIdMap = {};
    }

    setTrackInfo(entry) {
        const info = getElement(entry, "INFO");
        const location = getElement(entry, "LOCATION");

        this.trackInfo = {
            id: getAttribute(entry, "AUDIO_ID"),
            title: getAttribute(entry, "TITLE"),
            artist: getAttribute(entry, "ARTIST"),
            album: getAttribute(getElement(entry, "ALBUM"), "TITLE"),
            key: getTonalikey(getAttribute(getElement(entry, "MUSICAL_KEY"), "VALUE")),
            bpm: parseFloat(getAttribute(getElement(entry, "TEMPO"), "BPM") || "0.0"),
            color: getTrackColor(getAttribute(info, "COLOR")),
            genre: getAttribute(info, "GENRE"),
            playtime: getAttribute(info, "PLAYTIME"),
            playcount: getAttribute(info, "PLAYCOUNT"),
            bitrate: parseFloat(getAttribute(info, "BITRATE") || "0.0") / 1000,
            import_date: formatDate(getAttribute(info, "IMPORT_DATE")),
            modif_date: formatDate(getAttribute(entry, "MODIFIED_DATE")),
            last_played: formatDate(getAttribute(info, "LAST_PLAYED")),
            ranking: getAttribute(info, "RANKING"),
            file_path: this.getFilePath(location)
        };

        return this.trackInfo;
    }

    static isBeatgrid(cue) {
        const cueName = getAttribute(cue, "NAME");
        const gridElement = cue.querySelector("GRID");
        return (cueName === "AutoGrid" || cueName === "Beat Marker") && gridElement !== null;
    }

    getFilePath(location) {
        if (!location) return "";

        const volume = getAttribute(location, "VOLUME");
        const directory = getAttribute(location, "DIR");
        const file = getAttribute(location, "FILE");

        return `${volume}${directory}${file}`;
    }

    static ms2sec(timeMs) {
        return timeMs ? parseFloat(timeMs) / 1000 : 0;
    }

    addTempo(start, bpm, metro = null) {
        const bpmValue = Math.round(parseFloat(bpm) * 100) / 100;
        const tempo = document.createElementNS(null, "TEMPO");
        tempo.setAttribute("Inizio", String(start));
        tempo.setAttribute("Bpm", String(bpmValue));
        tempo.setAttribute("Battito", "1");
        if (metro) tempo.setAttribute("Metro", metro);
        this.track.appendChild(tempo);
        this.addedTempos++;
    }

    addBeatgrid(cue) {
        const startSeconds = Traktor2Rekordbox.ms2sec(getAttribute(cue, "START"));
        const gridElement = cue.querySelector("GRID");
        const gridBpm = getAttribute(gridElement, "BPM");

        if (gridBpm) {
            this.addTempo(startSeconds, gridBpm, "4/4");
        }
    }

    addCue(cue) {
        const cueType = getAttribute(cue, "TYPE");
        const cueName = getAttribute(cue, "NAME");
        const startSeconds = Traktor2Rekordbox.ms2sec(getAttribute(cue, "START"));
        const length = getAttribute(cue, "LEN");
        const hotcueNo = getAttribute(cue, "HOTCUE");

        const cNum = (hotcueNo && hotcueNo !== "-1") ? hotcueNo : String(this.cueIndex);

        const positionMark = document.createElementNS(null, "POSITION_MARK");
        positionMark.setAttribute("Type", getCueType(cueType));
        positionMark.setAttribute("Num", cNum);
        positionMark.setAttribute("Start", String(startSeconds));
        positionMark.setAttribute("Name", cueName);

        setCueColor(positionMark, cueType, cueName);

        if (length && parseFloat(length) !== 0) {
            const endSeconds = startSeconds + Traktor2Rekordbox.ms2sec(length);
            positionMark.setAttribute("End", String(endSeconds));
        }

        this.track.appendChild(positionMark);
        this.cueIndex++;
    }

    processCue(cue) {
        if (Traktor2Rekordbox.isBeatgrid(cue)) {
            this.addBeatgrid(cue);
        } else {
            this.addCue(cue);
        }
    }

    defaultTempo() {
        if (this.addedTempos === 0) {
            let autogridStart = null;
            for (const cue of this.cues) {
                if (getAttribute(cue, "NAME") === "AutoGrid") {
                    autogridStart = Traktor2Rekordbox.ms2sec(getAttribute(cue, "START"));
                    break;
                }
            }

            if (autogridStart !== null) {
                this.addTempo(autogridStart, this.trackInfo.bpm);
            }
        }
    }

    addTrack(collection, location) {
        const info = this.trackInfo;
        const trackId = String(this.trackIndex).padStart(9, '0');

        if (info.file_path) {
            this.trackIdMap[info.file_path] = trackId;
        }

        const track = document.createElementNS(null, "TRACK");
        track.setAttribute("TrackID", trackId);
        track.setAttribute("Name", info.title);
        track.setAttribute("Artist", info.artist);
        track.setAttribute("Album", info.album);
        track.setAttribute("Genre", info.genre);
        track.setAttribute("Kind", "3");
        track.setAttribute("Size", "0");
        track.setAttribute("TotalTime", info.playtime);
        track.setAttribute("DiscNumber", "0");
        track.setAttribute("TrackNumber", String(this.trackIndex));
        track.setAttribute("Year", "0");
        track.setAttribute("AverageBpm", String(info.bpm));
        track.setAttribute("BitRate", String(info.bitrate));
        track.setAttribute("DateModified", info.modif_date);
        track.setAttribute("DateAdded", info.import_date);
        track.setAttribute("SampleRate", "0");
        track.setAttribute("PlayCount", info.playcount);
        track.setAttribute("LastPlayed", info.last_played);
        track.setAttribute("Rating", info.ranking);
        track.setAttribute("Tonality", info.key);
        track.setAttribute("Location", location);
        track.setAttribute("Colour", info.color);

        collection.appendChild(track);
        return track;
    }

    resetTrack() {
        this.track = null;
        this.cues = [];
        this.cueIndex = 0;
        this.addedTempos = 0;
        this.trackInfo = {};
    }

    static isPlaylist(entry) {
        return getElement(entry, "PRIMARYKEY") !== null;
    }

    processCues(entry) {
        this.cues = Array.from(entry.querySelectorAll("CUE_V2"));
        for (const cue of this.cues) {
            this.processCue(cue);
        }
    }

    processEntry(entry, collection) {
        if (Traktor2Rekordbox.isPlaylist(entry)) {
            return false;
        }

        this.resetTrack();
        this.setTrackInfo(entry);
        const location = getLocation(getElement(entry, "LOCATION"));

        this.track = this.addTrack(collection, location);
        this.processCues(entry);
        this.defaultTempo();

        return true;
    }

    processPlaylists(root, playlistsNode) {
        const nmlPlaylists = root.querySelector("PLAYLISTS");
        if (!nmlPlaylists) return;

        const rootNode = nmlPlaylists.querySelector("NODE");
        if (!rootNode) return;

        const subnodes = rootNode.querySelector("SUBNODES");
        const nodes = subnodes ?
            Array.from(subnodes.querySelectorAll(":scope > NODE")) :
            Array.from(rootNode.querySelectorAll(":scope > NODE"));

        for (const node of nodes) {
            this.processPlaylistNode(node, playlistsNode);
        }
    }

    processPlaylistNode(nmlNode, parentNode) {
        const nodeType = getAttribute(nmlNode, "TYPE");
        const nodeName = getAttribute(nmlNode, "NAME");

        if (nodeType === "FOLDER") {
            const folderNode = document.createElementNS(null, "NODE");
            folderNode.setAttribute("Type", "0");
            folderNode.setAttribute("Name", nodeName);
            folderNode.setAttribute("Count", "0");
            parentNode.appendChild(folderNode);

            const subnodes = nmlNode.querySelector("SUBNODES");
            const children = subnodes ?
                Array.from(subnodes.querySelectorAll(":scope > NODE")) :
                Array.from(nmlNode.querySelectorAll(":scope > NODE"));

            for (const child of children) {
                this.processPlaylistNode(child, folderNode);
            }
        } else if (nodeType === "PLAYLIST") {
            const playlistElement = nmlNode.querySelector("PLAYLIST");
            if (!playlistElement) return;

            const entries = Array.from(playlistElement.querySelectorAll("ENTRY"));

            const playlistNode = document.createElementNS(null, "NODE");
            playlistNode.setAttribute("Type", "1");
            playlistNode.setAttribute("Name", nodeName);
            playlistNode.setAttribute("KeyType", "0");
            playlistNode.setAttribute("Entries", String(entries.length));
            parentNode.appendChild(playlistNode);

            for (const entry of entries) {
                const primarykey = getElement(entry, "PRIMARYKEY");
                if (!primarykey) continue;

                const filePath = getAttribute(primarykey, "KEY");
                if (filePath in this.trackIdMap) {
                    const trackId = this.trackIdMap[filePath];
                    const trackNode = document.createElementNS(null, "TRACK");
                    trackNode.setAttribute("Key", trackId);
                    playlistNode.appendChild(trackNode);
                }
            }
        }
    }

    convertNmlToXml(nmlContent) {
        setConversion("traktor", "rekordbox");

        const parser = new DOMParser();
        const nmlDoc = parser.parseFromString(nmlContent, "text/xml");
        const root = nmlDoc.documentElement;

        const entries = Array.from(root.querySelectorAll("ENTRY"));
        const trackCount = entries.filter(e => !Traktor2Rekordbox.isPlaylist(e)).length;

        const rekordboxDoc = document.implementation.createDocument(null, "DJ_PLAYLISTS");
        const rekordbox = rekordboxDoc.documentElement;
        rekordbox.setAttribute("Version", "1.0.0");

        const collection = rekordboxDoc.createElementNS(null, "COLLECTION");
        collection.setAttribute("Entries", String(trackCount));
        rekordbox.appendChild(collection);

        for (const entry of entries) {
            if (this.processEntry(entry, collection)) {
                this.trackIndex++;
            }
        }

        const playlists = rekordboxDoc.createElementNS(null, "PLAYLISTS");
        rekordbox.appendChild(playlists);

        const rootNode = rekordboxDoc.createElementNS(null, "NODE");
        rootNode.setAttribute("Type", "0");
        rootNode.setAttribute("Name", "ROOT");
        rootNode.setAttribute("Count", "0");
        playlists.appendChild(rootNode);

        this.processPlaylists(root, rootNode);

        const serializer = new XMLSerializer();
        return '<?xml version="1.0" encoding="utf-8"?>\n' + serializer.serializeToString(rekordbox);
    }
}

async function convertNMLToXML(nmlContent) {
    const converter = new Traktor2Rekordbox();
    return converter.convertNmlToXml(nmlContent);
}
