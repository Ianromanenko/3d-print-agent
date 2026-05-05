import { StepBase } from './step-base.js';
import { state } from '../state.js';

const ITEMS = [
  'Bambu Lab A1 printer (main unit)',
  'Power cable',
  'Build plate (textured PEI)',
  'Toolbox (cutters, screwdriver, spare parts)',
  'Spool holder',
  'PTFE tubes',
  'Quick-start guide',
  'Filament sample (if included)',
];

export class Step12UnboxCheck extends StepBase {
  constructor() {
    super({ id: '1.2', title: 'Unbox & check parts' });
    this._checked = new Set(state.get('step_1.2_checked') || []);
  }

  render() {
    const items = ITEMS.map((item, i) => {
      const checked = this._checked.has(i) ? 'checked' : '';
      return `<li class="checklist-item ${checked}" data-idx="${i}">
        <span class="check-icon">${checked ? '✓' : ''}</span>
        <span>${item}</span>
      </li>`;
    }).join('');
    return `<div class="step">
      <h2 class="step-title"></h2>
      <p class="step-body">Tick off each item as you find it in the box. Don't worry if the sample filament isn't included — it's optional.</p>
      <ul class="checklist">${items}</ul>
      <p class="step-subtitle" id="check-hint" style="margin-top:4px;"></p>
      ${this.renderNav({ nextLabel: 'All checked →' })}
    </div>`;
  }

  afterMount(container) {
    const h2 = container.querySelector('.step-title');
    if (h2) h2.textContent = this.title;

    this._updateHint(container);

    container.querySelectorAll('.checklist-item').forEach(li => {
      li.addEventListener('click', () => {
        const idx = Number(li.dataset.idx);
        if (this._checked.has(idx)) { this._checked.delete(idx); li.classList.remove('checked'); li.querySelector('.check-icon').textContent = ''; }
        else { this._checked.add(idx); li.classList.add('checked'); li.querySelector('.check-icon').textContent = '✓'; }
        state.set('step_1.2_checked', [...this._checked]);
        this._updateHint(container);
      });
    });
    this.bindNav(container);
  }

  _updateHint(container) {
    const hint = container.querySelector('#check-hint');
    if (!hint) return;
    const remaining = ITEMS.length - this._checked.size;
    hint.textContent = remaining === 0 ? '✅ All parts found!' : `${remaining} item${remaining > 1 ? 's' : ''} remaining`;
  }
}
