import { StepBase } from './step-base.js';

export class Step19Login extends StepBase {
  constructor() { super({ id: '1.9', title: 'Sign into OrcaSlicer' }); }

  render() {
    return `<div class="step">
      <h2 class="step-title"></h2>
      <div class="image-step">
        <div class="image-step-visual">
          <img src="/assets/illustrations/orcaslicer-login.svg" alt="OrcaSlicer login screen" />
        </div>
        <div class="image-step-caption">
          <h3>Connect OrcaSlicer to your printer</h3>
          <p>Open OrcaSlicer on your Mac. On first launch it will ask you to add a printer —
          choose <strong>Bambu Lab → A1</strong>. Sign in with your Bambu account.
          OrcaSlicer will find your printer automatically over the cloud.</p>
        </div>
      </div>
      <ol style="padding-left:20px; display:flex; flex-direction:column; gap:8px; font-size:15px;">
        <li>Open OrcaSlicer</li>
        <li>Click <strong>Add Printer</strong> → <strong>Bambu Lab</strong> → <strong>A1</strong></li>
        <li>Click <strong>Login with Bambu Cloud</strong></li>
        <li>Enter your Bambu account email and password</li>
        <li>Your A1 should appear in the printer list on the left side — click it to select</li>
      </ol>
      ${this.renderNav()}
    </div>`;
  }

  afterMount(container) {
    super.afterMount(container);
    this.bindNav(container);
  }
}
