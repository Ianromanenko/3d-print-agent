import { StepBase } from './step-base.js';
import { state } from '../state.js';
import { api } from '../api-client.js';

export class Step110Verify extends StepBase {
  constructor() { super({ id: '1.10', title: 'Verify connection' }); }

  render() {
    return `<div class="step">
      <h2 class="step-title"></h2>
      <p class="step-body">Let's check if everything is connected properly.</p>
      <div id="status-card" style="background:var(--c-surface); border:1px solid var(--c-border);
        border-radius:var(--radius); padding:32px; text-align:center;">
        <div style="font-size:48px; margin-bottom:12px;" id="status-icon">⏳</div>
        <p id="status-text" style="font-size:16px; color:var(--c-muted);">Checking connection…</p>
      </div>
      <div class="alert alert-info">
        💡 <strong>Phase 1 note:</strong> Real printer connection is coming in Phase 2.
        For now, this confirms the backend server is running correctly.
      </div>
      ${this.renderNav({ nextLabel: 'Continue →' })}
    </div>`;
  }

  afterMount(container) {
    super.afterMount(container);
    this.bindNav(container);
    this._check(container);
  }

  async _check(container) {
    try {
      const s = await api.status();
      const icon = container.querySelector('#status-icon');
      const text = container.querySelector('#status-text');
      if (s.connected) {
        icon.textContent = '✅';
        text.textContent = 'Printer connected and ready!';
      } else {
        icon.textContent = '⚙️';
        text.textContent = 'Backend running. Printer connection set up in Phase 2.';
      }
      state.setSetupComplete();
    } catch {
      const icon = container.querySelector('#status-icon');
      const text = container.querySelector('#status-text');
      icon.textContent = '⚠️';
      text.textContent = 'Could not reach backend. Make sure "npm start" is running.';
    }
  }
}
