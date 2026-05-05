import { StepBase } from './step-base.js';
import { state } from '../state.js';
import { Viewer3D } from '../components/viewer-3d.js';

export class Step41Preview extends StepBase {
  constructor() { super({ id: '4.1', title: 'Preview your model' }); }

  render() {
    const model = state.get('selectedModel') || {};
    const name = model.title || 'Unknown model';
    return `<div class="step">
      <h2 class="step-title"></h2>
      <p class="step-subtitle" id="model-name-display"></p>

      <div class="viewer-wrap" id="viewer-container" style="min-height:360px;">
        <div class="loading-spinner" id="viewer-loading">Loading 3D model…</div>
      </div>

      <div class="viewer-dims" id="viewer-dims-overlay" style="display:none;"></div>

      <div style="display:flex; gap:10px; flex-wrap:wrap; margin-top:12px;">
        <button class="btn btn-secondary btn-sm" id="btn-wireframe">◻ Wireframe</button>
        <button class="btn btn-secondary btn-sm" id="btn-reset-view">⟳ Reset view</button>
      </div>

      <div style="background:var(--c-surface); border:1px solid var(--c-border);
        border-radius:var(--radius); padding:20px; margin-top:8px;">
        <h3 style="font-size:16px; margin-bottom:12px;">Print settings</h3>
        <div style="display:grid; grid-template-columns:1fr 1fr; gap:12px;">
          <div>
            <label style="font-size:13px; color:var(--c-muted);">Scale</label>
            <div style="display:flex; align-items:center; gap:8px; margin-top:4px;">
              <input id="input-scale" type="number" value="100" min="10" max="500"
                style="width:80px; padding:8px; background:var(--c-surface2);
                border:1px solid var(--c-border); border-radius:var(--radius-sm);
                color:var(--c-text); font-size:15px;" />
              <span style="color:var(--c-muted);">%</span>
            </div>
          </div>
          <div>
            <label style="font-size:13px; color:var(--c-muted);">Copies</label>
            <input id="input-copies" type="number" value="1" min="1" max="10"
              style="width:80px; padding:8px; margin-top:4px; background:var(--c-surface2);
              border:1px solid var(--c-border); border-radius:var(--radius-sm);
              color:var(--c-text); font-size:15px;" />
          </div>
        </div>
        <div style="margin-top:12px; font-size:13px; color:var(--c-muted);">
          Estimated: <span id="est-time">~1h 0m</span> · <span id="est-filament">~12g</span>
        </div>
      </div>

      ${this.renderNav({ nextLabel: '🖨️ Send to printer →' })}
    </div>`;
  }

  afterMount(container) {
    super.afterMount(container);

    const model = state.get('selectedModel') || {};
    const nameEl = container.querySelector('#model-name-display');
    if (nameEl) nameEl.textContent = model.title || '';

    // Init viewer
    const viewerContainer = container.querySelector('#viewer-container');
    const loading = container.querySelector('#viewer-loading');
    const dimsOverlay = container.querySelector('#viewer-dims-overlay');

    if (model.fileUrl && model.fileType === 'stl') {
      const viewer = new Viewer3D(viewerContainer);
      loading.style.display = 'none';

      viewer.loadSTL(model.fileUrl).then(dims => {
        if (dimsOverlay) {
          dimsOverlay.style.display = 'block';
          dimsOverlay.textContent = `X: ${dims.x}mm  Y: ${dims.y}mm  Z: ${dims.z}mm`;
        }
      }).catch(err => {
        loading.textContent = `Could not load 3D model: ${err.message}`;
        loading.style.display = 'block';
      });

      container.querySelector('#btn-wireframe').addEventListener('click', () => viewer.toggleWireframe());
      container.querySelector('#btn-reset-view').addEventListener('click', () => viewer.resetView());
    } else {
      loading.textContent = '3D preview available for STL files. 3MF support coming soon.';
    }

    // Save settings
    container.querySelector('#input-scale').addEventListener('change', e => state.set('printScale', e.target.value));
    container.querySelector('#input-copies').addEventListener('change', e => state.set('printCopies', e.target.value));

    this.bindNav(container);
  }
}
