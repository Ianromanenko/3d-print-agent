import { StepBase } from './step-base.js';
import { state } from '../state.js';

export class Step51Print extends StepBase {
  constructor() { super({ id: '5.1', title: 'Printing…' }); }

  render() {
    return `<div class="step">
      <h2 class="step-title"></h2>
      <div class="print-progress">
        <div class="big-pct" id="pct-display">0%</div>
        <div class="print-track"><div class="print-fill" id="print-fill" style="width:0%"></div></div>
        <div class="print-meta">
          <span>⏱ <span id="time-left">Calculating…</span></span>
          <span>🌡 Nozzle: <span id="nozzle-temp">—</span></span>
          <span>📦 Layer: <span id="layer-display">—</span></span>
        </div>
      </div>

      <div id="print-status-msg" class="alert alert-info" style="margin-top:8px;">
        ⚙️ Sending job to printer… (Phase 1: simulated)
      </div>

      <div id="print-done" style="display:none;">
        <div class="alert alert-success" style="margin-top:16px;">
          ✅ Print complete!
        </div>
        <div class="image-step" style="margin-top:16px;">
          <div class="image-step-visual">
            <img src="/assets/illustrations/remove-print.svg" alt="Removing the finished print" />
          </div>
          <div class="image-step-caption">
            <h3>Removing your print</h3>
            <p>Wait for the build plate to cool to room temperature (about 5 minutes).<br>
            Then gently flex the magnetic plate — the print will pop off by itself.<br>
            If it doesn't release, use the included spatula at a low angle.</p>
          </div>
        </div>
        <button class="btn btn-primary btn-full" id="btn-print-again" style="margin-top:16px;">
          🖨️ Print something else
        </button>
      </div>
    </div>`;
  }

  afterMount(container) {
    super.afterMount(container);
    this._simulate(container);
    container.querySelector('#btn-print-again')?.addEventListener('click', () => {
      state.set('selectedModel', null);
      this._router.goto('2.1');
    });
  }

  _simulate(container) {
    let pct = 0;
    const model = state.get('selectedModel');
    const totalMin = 60;

    const tick = () => {
      if (pct >= 100) {
        this._onDone(container);
        return;
      }
      pct = Math.min(100, pct + (Math.random() * 1.5 + 0.5));
      const remaining = Math.round((totalMin * (100 - pct)) / 100);

      const fill = container.querySelector('#print-fill');
      const pctEl = container.querySelector('#pct-display');
      const timeEl = container.querySelector('#time-left');
      const nozzleEl = container.querySelector('#nozzle-temp');
      const layerEl = container.querySelector('#layer-display');
      const msg = container.querySelector('#print-status-msg');

      if (fill)   fill.style.width = `${pct.toFixed(1)}%`;
      if (pctEl)  pctEl.textContent = `${Math.round(pct)}%`;
      if (timeEl) timeEl.textContent = pct > 5 ? `~${remaining}m left` : 'Calculating…';
      if (nozzleEl) nozzleEl.textContent = `${228 + Math.round(Math.random() * 4)}°C`;
      if (layerEl)  layerEl.textContent = `${Math.round(pct * 2.4)} / 240`;
      if (msg && pct > 5) msg.textContent = '🖨️ Printing… (Phase 1: simulated)';

      setTimeout(tick, 300);
    };
    setTimeout(tick, 1500);
  }

  _onDone(container) {
    const msg = container.querySelector('#print-status-msg');
    const done = container.querySelector('#print-done');
    if (msg)  msg.style.display = 'none';
    if (done) done.style.display = 'block';
  }
}
