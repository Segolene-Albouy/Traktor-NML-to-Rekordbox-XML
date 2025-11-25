function analyzeTrack(track, fileType) {
    const isNML = fileType === 'nml';

    const info = {
        title: track.getAttribute(isNML ? 'TITLE' : 'Name') || 'Unknown',
        artist: track.getAttribute(isNML ? 'ARTIST' : 'Artist') || 'Unknown',
        duration: isNML
            ? parseFloat(track.querySelector('INFO')?.getAttribute('PLAYTIME') || 0)
            : parseFloat(track.getAttribute('TotalTime') || 0)
    };

    const cueElements = isNML
        ? track.querySelectorAll('CUE_V2')
        : track.querySelectorAll('POSITION_MARK');

    const cues = Array.from(cueElements)
        .filter(cue => {
            const name = cue.getAttribute(isNML ? 'NAME' : 'Name');
            return name !== 'AutoGrid';
        })
        .map(cue => {
            const startAttr = cue.getAttribute(isNML ? 'START' : 'Start');
            const start = parseFloat(startAttr) / (isNML ? 1000 : 1);

            let length = 0;
            if (isNML) {
                length = parseFloat(cue.getAttribute('LEN')) / 1000;
            } else {
                const endAttr = cue.getAttribute('End');
                if (endAttr) {
                    length = parseFloat(endAttr) - parseFloat(startAttr);
                }
            }

            let color;
            if (isNML) {
                const colorAttr = cue.getAttribute('COLOR');
                color = colorAttr || '#4a9eff';
            } else {
                const r = cue.getAttribute('Red');
                const g = cue.getAttribute('Green');
                const b = cue.getAttribute('Blue');
                color = (r && g && b) ? `rgb(${r},${g},${b})` : '#4a9eff';
            }

            return {start, length, color, isLoop: length > 0};
        });

    return {...info, cues, hasHotcues: cues.length > 0};
}
