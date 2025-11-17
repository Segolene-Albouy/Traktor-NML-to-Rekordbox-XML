async function convertNMLToXML(nmlContent) {
    const parser = new DOMParser();
    const nmlDoc = parser.parseFromString(nmlContent, 'text/xml');

    // Create Rekordbox XML structure
    const rekordboxDoc = document.implementation.createDocument(null, 'DJ_PLAYLISTS', null);
    const root = rekordboxDoc.documentElement;
    root.setAttribute('Version', '1.0.0');

    const entries = nmlDoc.querySelectorAll('ENTRY');
    const trackEntries = Array.from(entries).filter(entry => !entry.querySelector('PRIMARYKEY'));

    const collection = rekordboxDoc.createElement('COLLECTION');
    collection.setAttribute('Entries', trackEntries.length.toString());
    root.appendChild(collection);

    trackEntries.forEach((entry, index) => {
        const track = convertNMLEntryToRekordboxTrack(rekordboxDoc, entry, index);
        collection.appendChild(track);
    });

    return new XMLSerializer().serializeToString(rekordboxDoc);
}

function convertNMLEntryToRekordboxTrack(doc, entry, index) {
    const track = doc.createElement('TRACK');

    // Basic attributes
    track.setAttribute('TrackID', index.toString().padStart(9, '0'));
    track.setAttribute('Name', entry.getAttribute('TITLE') || '');
    track.setAttribute('Artist', entry.getAttribute('ARTIST') || '');

    const info = entry.querySelector('INFO');
    if (info) {
        track.setAttribute('Genre', info.getAttribute('GENRE') || '');
        track.setAttribute('TotalTime', info.getAttribute('PLAYTIME') || '0');
        track.setAttribute('PlayCount', info.getAttribute('PLAYCOUNT') || '0');
        track.setAttribute('Rating', info.getAttribute('RANKING') || '0');
    }

    const tempo = entry.querySelector('TEMPO');
    if (tempo) {
        track.setAttribute('AverageBpm', tempo.getAttribute('BPM') || '120');
    }

    // Add other required attributes with defaults
    track.setAttribute('Album', '');
    track.setAttribute('Kind', '3');
    track.setAttribute('Size', '0');
    track.setAttribute('DiscNumber', '0');
    track.setAttribute('TrackNumber', index.toString());
    track.setAttribute('Year', '0');
    track.setAttribute('BitRate', '320');
    track.setAttribute('DateModified', new Date().toISOString().split('T')[0]);
    track.setAttribute('DateAdded', new Date().toISOString().split('T')[0]);
    track.setAttribute('SampleRate', '0');
    track.setAttribute('LastPlayed', '');
    track.setAttribute('Tonality', '');
    track.setAttribute('Location', '');
    track.setAttribute('Colour', '0x000000');

    return track;
}