class PlaylistConverter {
    constructor() {
        this.file = null;
        this.fileType = null;
        this.elements = {
            uploadZone: document.getElementById('uploadZone'),
            fileInput: document.getElementById('fileInput'),
            sections: {
                upload: document.getElementById('uploadSection'),
                action: document.getElementById('actionSection'),
                progress: document.getElementById('progressSection'),
                result: document.getElementById('resultSection')
            },
            fileName: document.getElementById('fileName'),
            fileDetails: document.getElementById('fileDetails'),
            targetFormat: document.getElementById('targetFormat'),
            progressFill: document.getElementById('progressFill'),
            progressText: document.getElementById('progressText')
        };
        this.init();
    }

    init() {
        const {uploadZone, fileInput} = this.elements;
        uploadZone.addEventListener('click', () => fileInput.click());
        uploadZone.addEventListener('dragover', e => this.handleDrag(e, true));
        uploadZone.addEventListener('dragleave', e => this.handleDrag(e, false));
        uploadZone.addEventListener('drop', e => this.handleDrop(e));
        fileInput.addEventListener('change', e => this.handleFileSelect(e));

        document.querySelectorAll('.action-btn').forEach(btn =>
            btn.addEventListener('click', () => this.handleAction(btn.dataset.action))
        );
    }

    handleDrag(e, isDragging) {
        e.preventDefault();
        this.elements.uploadZone.classList.toggle('dragover', isDragging);
    }

    handleDrop(e) {
        e.preventDefault();
        this.elements.uploadZone.classList.remove('dragover');
        const files = e.dataTransfer.files;
        if (files.length) this.processFile(files[0]);
    }

    handleFileSelect(e) {
        if (e.target.files.length) this.processFile(e.target.files[0]);
    }

    processFile(file) {
        const ext = file.name.split('.').pop().toLowerCase();
        if (!['nml', 'xml'].includes(ext)) {
            this.showError('Invalid file type. Please select .nml or .xml');
            return;
        }

        this.file = file;
        this.fileType = ext;
        this.elements.fileName.textContent = file.name;
        this.elements.fileDetails.textContent = `${(file.size / 1024).toFixed(1)} KB • ${ext.toUpperCase()}`;
        this.elements.targetFormat.textContent = ext === 'nml' ? 'XML' : 'NML';

        this.showSection('action');
    }

    async handleAction(action) {
        this.showSection('progress');

        try {
            if (action === 'convert') {
                await this.convert();
            } else if (action === 'analyze') {
                await this.analyze();
            }
        } catch (error) {
            this.showError(error.message);
        }
    }

    async convert() {
        this.updateProgress(20, 'Reading file...');
        const content = await this.readFile();

        this.updateProgress(60, 'Converting...');
        const converted = this.fileType === 'nml'
            ? await convertNMLToXML(content)
            : await convertXMLToNML(content);

        this.updateProgress(100, 'Complete');

        const filename = this.file.name.replace(
            `.${this.fileType}`,
            this.fileType === 'nml' ? '.xml' : '.nml'
        );

        setTimeout(() => this.showSuccess('Conversion complete', converted, filename), 300);
    }

    async analyze() {
        this.updateProgress(50, 'Analyzing tracks...');
        const content = await this.readFile();
        const parser = new DOMParser();
        const doc = parser.parseFromString(content, 'text/xml');

        const collection = doc.getElementsByTagName('COLLECTION')[0];
        const tracks = this.fileType === 'nml'
            ? Array.from(collection.getElementsByTagName('ENTRY'))
            : Array.from(collection.getElementsByTagName('TRACK'));

        const analysis = tracks.map(track => analyzeTrack(track, this.fileType));

        analysis.sort((a, b) => {
            if (a.hasHotcues === b.hasHotcues) return 0;
            return a.hasHotcues ? 1 : -1;
        });

        this.updateProgress(100, 'Analysis complete');
        setTimeout(() => this.showTrackAnalysis(analysis), 300);
    }

    showTrackAnalysis(tracks) {
        const section = this.elements.sections.result;

        const trackList = tracks.map(track => {
            const timeline = track.cues.map(cue => {
                const position = (cue.start / track.duration) * 100;
                const width = cue.isLoop ? (cue.length / track.duration) * 100 : 0;

                return cue.isLoop
                    ? `<div class="loop" style="left: ${position}%; width: ${width}%; background: ${cue.color};"></div>`
                    : `<div class="cue" style="left: ${position}%; background: ${cue.color};"></div>`;
            }).join('');

            const statusClass = track.hasHotcues ? '' : 'no-cues';

            return `
                <div class="track-item ${statusClass}">
                    <div class="track-info">
                        <div class="track-title">${track.title}</div>
                        <div class="track-artist">${track.artist}</div>
                    </div>
                    <div class="track-timeline">
                        ${timeline || '<span class="empty-timeline">No cues</span>'}
                    </div>
                </div>
            `;
        }).join('');

        section.innerHTML = `
            <div class="result-card">
                <h3>Track Analysis</h3>
                <div class="stats">
                    <div class="stat">
                        <span class="stat-value">${tracks.length}</span>
                        <span class="stat-label">Total Tracks</span>
                    </div>
                    <div class="stat">
                        <span class="stat-value">${tracks.filter(t => !t.hasHotcues).length}</span>
                        <span class="stat-label">Without Cues</span>
                    </div>
                </div>
                <div class="track-list">${trackList}</div>
                <button class="reset-btn" id="resetBtn">Back</button>
            </div>
        `;

        section.querySelector('#resetBtn').onclick = () => this.showSection('action');
        this.showSection('result');
    }

    readFile() {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = e => resolve(e.target.result);
            reader.onerror = reject;
            reader.readAsText(this.file);
        });
    }

    updateProgress(percent, text) {
        this.elements.progressFill.style.width = `${percent}%`;
        this.elements.progressText.textContent = text;
    }

    showSection(name) {
        Object.values(this.elements.sections).forEach(s => s.style.display = 'none');
        this.elements.sections[name].style.display = 'block';
    }

    showSuccess(message, content, filename) {
        const section = this.elements.sections.result;
        section.innerHTML = `
                    <div class="result-card success">
                        <span class="feature-icon">🎛️</span>
                        <h3>${message}</h3>
                        <button class="download-btn" id="downloadBtn">Download ${filename}</button>
                        <button class="reset-btn" id="resetBtn">Process Another</button>
                    </div>
                `;

        section.querySelector('#downloadBtn').onclick = () => this.download(filename, content);
        section.querySelector('#resetBtn').onclick = () => this.reset();
        this.showSection('result');
    }

    showAnalysis(data) {
        const section = this.elements.sections.result;
        section.innerHTML = `
                    <div class="result-card">
                        <h3>Cue Analysis</h3>
                        <div class="stats">
                            <div class="stat">
                                <span class="stat-value">${data.totalCues}</span>
                                <span class="stat-label">Total Cues</span>
                            </div>
                            <div class="stat">
                                <span class="stat-value">${data.hotcues}</span>
                                <span class="stat-label">Hot Cues</span>
                            </div>
                        </div>
                        <button class="reset-btn" id="resetBtn">Back</button>
                    </div>
                `;

        section.querySelector('#resetBtn').onclick = () => this.showSection('action');
        this.showSection('result');
    }

    showError(message) {
        const section = this.elements.sections.result;
        section.innerHTML = `
                    <div class="result-card error">
                        <span class="feature-icon">⛓️‍💥</span>
                        <h3>Error</h3>
                        <p>${message}</p>
                        <button class="reset-btn" id="resetBtn">Try Again</button>
                    </div>
                `;

        section.querySelector('#resetBtn').onclick = () => this.reset();
        this.showSection('result');
    }

    download(filename, content) {
        const blob = new Blob([content], {type: 'text/xml'});
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        a.click();
        URL.revokeObjectURL(url);
    }

    reset() {
        this.file = null;
        this.fileType = null;
        this.showSection('upload');
    }
}