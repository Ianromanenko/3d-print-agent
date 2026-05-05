import { StepBase } from './step-base.js';

export class Step16Wifi extends StepBase {
  constructor() { super({ id: '1.6', title: 'Connect to WiFi' }); }

  render() {
    return `<div class="step">
      <h2 class="step-title"></h2>
      <div class="image-step">
        <div class="image-step-visual">
          <img src="/assets/illustrations/wifi-screen.svg" alt="Bambu Lab A1 WiFi settings screen" />
        </div>
        <div class="image-step-caption">
          <h3>Connect the printer to your WiFi</h3>
          <p>On the printer touchscreen tap <strong>Settings (gear icon) → Network → WiFi</strong>.
          Select your home WiFi network and enter your password.</p>
        </div>
      </div>
      <ol style="padding-left:20px; display:flex; flex-direction:column; gap:8px; font-size:15px;">
        <li>On the printer screen, tap the <strong>gear icon ⚙️</strong> (bottom right)</li>
        <li>Tap <strong>Network</strong></li>
        <li>Tap <strong>WiFi</strong></li>
        <li>Select your WiFi network name</li>
        <li>Enter your WiFi password using the on-screen keyboard</li>
        <li>Tap <strong>Connect</strong> — the WiFi icon should appear at the top of the screen</li>
      </ol>
      <div class="alert alert-warn">
        ⚠️ Use the same WiFi network your Mac is on. The printer does <strong>not</strong> support 5 GHz-only networks — use 2.4 GHz or a mixed-band network.
      </div>
      ${this.renderNav()}
    </div>`;
  }

  afterMount(container) {
    super.afterMount(container);
    this.bindNav(container);
  }
}
