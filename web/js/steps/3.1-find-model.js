import { StepBase } from './step-base.js';
import { state } from '../state.js';
import { api } from '../api-client.js';

export class Step31FindModel extends StepBase {
  constructor() { super({ id: '3.1', title: 'Choose what to print' }); }

  render() {
    return `<div class="step">
      <h2 class="step-title"></h2>
      <p class="step-body">Describe what you want, paste a MakerWorld link, or upload your own STL/3MF file.</p>

      <div class="search-bar">
        <input id="search-input" type="text" placeholder="e.g. Apple Watch band organizer, vase, phone stand…" />
        <button class="btn btn-primary" id="btn-search">🔍 Search</button>
      </div>

      <div style="text-align:center; color:var(--c-muted); font-size:14px; margin: 4px 0;">— or —</div>

      <div class="upload-zone" id="upload-zone">
        <div class="upload-icon">📁</div>
        <p><strong>Drop an STL or 3MF file here</strong></p>
        <p style="font-size:13px; margin-top:4px;">or click to browse</p>
        <input type="file" id="file-input" accept=".stl,.3mf" style="display:none;" />
      </div>

      <div id="search-results" style="margin-top:8px;"></div>
      <div id="search-status" style="text-align:center; color:var(--c-muted); font-size:14px;"></div>
    </div>`;
  }

  afterMount(container) {
    super.afterMount(container);
    const input   = container.querySelector('#search-input');
    const btnSearch = container.querySelector('#btn-search');
    const zone    = container.querySelector('#upload-zone');
    const fileInput = container.querySelector('#file-input');

    btnSearch.addEventListener('click', () => this._search(container));
    input.addEventListener('keydown', e => { if (e.key === 'Enter') this._search(container); });

    zone.addEventListener('click', () => fileInput.click());
    zone.addEventListener('dragover', e => { e.preventDefault(); zone.classList.add('drag-over'); });
    zone.addEventListener('dragleave', () => zone.classList.remove('drag-over'));
    zone.addEventListener('drop', e => {
      e.preventDefault(); zone.classList.remove('drag-over');
      const file = e.dataTransfer.files[0];
      if (file) this._handleFile(file);
    });
    fileInput.addEventListener('change', () => {
      const file = fileInput.files[0];
      if (file) this._handleFile(file);
    });
  }

  async _search(container) {
    const input = container.querySelector('#search-input');
    const status = container.querySelector('#search-status');
    const results = container.querySelector('#search-results');
    const q = input.value.trim();
    if (!q) return;

    status.textContent = 'Searching MakerWorld…';
    results.textContent = '';

    try {
      const data = await api.search(q);
      status.textContent = '';
      if (!data.results.length) {
        status.textContent = 'No results found. Try different keywords.';
        return;
      }
      this._renderResults(results, data.results);
    } catch (e) {
      status.textContent = `Search failed: ${e.message}`;
    }
  }

  _renderResults(container, results) {
    container.textContent = '';
    const grid = document.createElement('div');
    grid.className = 'model-grid';

    results.forEach(model => {
      const card = document.createElement('div');
      card.className = 'model-card';

      if (model.thumbnail) {
        const img = document.createElement('img');
        img.className = 'model-card-thumb';
        img.src = model.thumbnail;
        img.alt = model.title;
        img.loading = 'lazy';
        img.onerror = () => { img.replaceWith(this._placeholder()); };
        card.appendChild(img);
      } else {
        card.appendChild(this._placeholder());
      }

      const info = document.createElement('div');
      info.className = 'model-card-info';
      const title = document.createElement('div');
      title.className = 'model-card-title';
      title.textContent = model.title;
      const meta = document.createElement('div');
      meta.className = 'model-card-meta';
      meta.textContent = `by ${model.author} · ❤️ ${model.likes}`;
      info.appendChild(title);
      info.appendChild(meta);
      card.appendChild(info);

      card.addEventListener('click', () => this._selectModel(model));
      grid.appendChild(card);
    });

    container.appendChild(grid);
  }

  _placeholder() {
    const div = document.createElement('div');
    div.className = 'model-card-thumb-placeholder';
    div.textContent = '🖨️';
    return div;
  }

  async _handleFile(file) {
    const ext = file.name.split('.').pop().toLowerCase();
    if (!['stl', '3mf'].includes(ext)) {
      alert('Please upload an STL or 3MF file.');
      return;
    }
    const url = URL.createObjectURL(file);
    state.set('selectedModel', {
      id: file.name,
      title: file.name,
      fileUrl: url,
      fileType: ext,
      isLocal: true,
    });
    this.complete();
  }

  _selectModel(model) {
    state.set('selectedModel', model);
    this.complete();
  }
}
