import { StepBase } from './step-base.js';
import { state } from '../state.js';

const PRESETS = [
  { id: 'bambu-pla-silk-white', label: 'Bambu PLA Silk White', nozzle: 230, bed: 55 },
  { id: 'bambu-pla-basic',      label: 'Bambu PLA Basic',       nozzle: 220, bed: 35 },
  { id: 'bambu-petg',           label: 'Bambu PETG',            nozzle: 250, bed: 70 },
  { id: 'generic-pla',          label: 'Generic PLA',           nozzle: 215, bed: 60 },
];

export class Step23FilamentType extends StepBase {
  constructor() { super({ id: '2.3', title: 'Confirm filament type' }); }

  render() {
    const saved = state.get('filamentPreset') || 'bambu-pla-silk-white';
    const opts = PRESETS.map(p => `<option value="${p.id}" ${p.id === saved ? 'selected' : ''}>${p.label} — ${p.nozzle}°C / bed ${p.bed}°C</option>`).join('');
    return `<div class="step">
      <h2 class="step-title"></h2>
      <p class="step-body">Select the filament you just loaded. This sets the correct temperatures for your print.</p>
      <div style="display:flex; flex-direction:column; gap:12px;">
        <label style="font-weight:600; font-size:15px;">Filament type</label>
        <select id="filament-select" style="padding:12px 16px; background:var(--c-surface2);
          border:1px solid var(--c-border); border-radius:var(--radius-sm);
          color:var(--c-text); font-size:15px;">
          ${opts}
        </select>
        <div id="preset-info" class="alert alert-info"></div>
      </div>
      ${this.renderNav({ nextLabel: 'Confirm →' })}
    </div>`;
  }

  afterMount(container) {
    super.afterMount(container);
    const select = container.querySelector('#filament-select');
    const info = container.querySelector('#preset-info');
    const update = () => {
      const preset = PRESETS.find(p => p.id === select.value);
      if (preset && info) {
        info.textContent = `Nozzle: ${preset.nozzle}°C  ·  Bed: ${preset.bed}°C`;
      }
      state.set('filamentPreset', select.value);
    };
    select.addEventListener('change', update);
    update();
    this.bindNav(container);
  }
}
