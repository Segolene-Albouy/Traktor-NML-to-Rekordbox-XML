async function convertXMLToNML(xmlContent) {
    const parser = new DOMParser();
    const xmlDoc = parser.parseFromString(xmlContent, 'text/xml');

    // Create NML structure
    const nmlDoc = document.implementation.createDocument(null, 'NML', null);
    const root = nmlDoc.documentElement;
    root.setAttribute('VERSION', '20');

    // Add HEAD
    const head = nmlDoc.createElement('HEAD');
    head.setAttribute('COMPANY', 'www.native-instruments.com');
    head.setAttribute('PROGRAM', 'Traktor Pro 4');
    root.appendChild(head);

    const tracks = xmlDoc.querySelectorAll('TRACK');

    const collection = nmlDoc.createElement('COLLECTION');
    collection.setAttribute('ENTRIES', tracks.length.toString());
    root.appendChild(collection);

    tracks.forEach((track, index) => {
        const entry = convertRekordboxTrackToNMLEntry(nmlDoc, track, index);
        collection.appendChild(entry);
    });

    // Add empty SETS and PLAYLISTS
    const sets = nmlDoc.createElement('SETS');
    sets.setAttribute('ENTRIES', '0');
    root.appendChild(sets);

    const playlists = nmlDoc.createElement('PLAYLISTS');
    root.appendChild(playlists);

    const indexing = nmlDoc.createElement('INDEXING');
    root.appendChild(indexing);

    return new XMLSerializer().serializeToString(nmlDoc);
}

function convertRekordboxTrackToNMLEntry(doc, track, index) {
    const entry = doc.createElement('ENTRY');

    // Basic attributes
    entry.setAttribute('MODIFIED_DATE', new Date().toISOString().split('T')[0].replace(/-/g, '/'));
    entry.setAttribute('MODIFIED_TIME', '0');
    entry.setAttribute('AUDIO_ID', generateAudioId());
    entry.setAttribute('TITLE', track.getAttribute('Name') || '');
    entry.setAttribute('ARTIST', track.getAttribute('Artist') || '');

    // Add LOCATION
    const location = doc.createElement('LOCATION');
    location.setAttribute('DIR', '/:');
    location.setAttribute('FILE', '');
    location.setAttribute('VOLUME', 'Macintosh HD');
    location.setAttribute('VOLUMEID', 'Macintosh HD');
    entry.appendChild(location);

    // Add MODIFICATION_INFO
    const modifInfo = doc.createElement('MODIFICATION_INFO');
    modifInfo.setAttribute('AUTHOR_TYPE', 'user');
    entry.appendChild(modifInfo);

    // Add INFO
    const info = doc.createElement('INFO');
    info.setAttribute('BITRATE', '320000');
    info.setAttribute('GENRE', track.getAttribute('Genre') || '');
    info.setAttribute('PLAYCOUNT', track.getAttribute('PlayCount') || '0');
    info.setAttribute('PLAYTIME', track.getAttribute('TotalTime') || '0');
    info.setAttribute('RANKING', track.getAttribute('Rating') || '0');
    info.setAttribute('IMPORT_DATE', new Date().toISOString().split('T')[0].replace(/-/g, '/'));
    info.setAttribute('FLAGS', '12');
    info.setAttribute('COLOR', '0');
    entry.appendChild(info);

    // Add TEMPO
    const tempo = doc.createElement('TEMPO');
    tempo.setAttribute('BPM', track.getAttribute('AverageBpm') || '120');
    tempo.setAttribute('BPM_QUALITY', '100.000000');
    entry.appendChild(tempo);

    return entry;
}

function generateAudioId() {
    return 'AWAWZmRENDMzMzf//////////////////////f/////////////////////s/////////////////////5b///7//////////+//////af/////////////////////+///////////f/////////1n/////////9Y///////////f/////////+r/7///////9XYzMzM0MyMzJUMzNDNDMzRDn//////////////////////f/////////////////////e/////////////////////3r+/+////////7u7u/v////vf//7////////v/+//////+FZneYYQAAAA==';
}