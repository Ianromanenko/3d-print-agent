import { StepBase } from './step-base.js';

export class Step17BindAccount extends StepBase {
  constructor() { super({ id: '1.7', title: 'Link to your Bambu account' }); }

  render() {
    return `<div class="step">
      <h2 class="step-title"></h2>
      <div class="image-step">
        <div class="image-step-visual">
          <img src="/assets/illustrations/qr-bind.svg" alt="Scan QR code with Bambu Handy app" />
        </div>
        <div class="image-step-caption">
          <h3>Scan the QR code with Bambu Handy</h3>
          <p>On the printer screen, go to <strong>Settings → Account → Bind</strong>.
          A QR code will appear. Open the <strong>Bambu Handy</strong> app on your phone,
          tap the <strong>+</strong> button, and scan the QR code.</p>
        </div>
      </div>
      <ol style="padding-left:20px; display:flex; flex-direction:column; gap:8px; font-size:15px;">
        <li>If you don't have a Bambu account, create one at <a href="https://bambulab.com" target="_blank" rel="noopener" style="color: var(--c-primary)">bambulab.com</a></li>
        <li>Install <strong>Bambu Handy</strong> on your phone (App Store or Google Play)</li>
        <li>Sign in to Bambu Handy with your account</li>
        <li>On the printer: Settings ⚙️ → Account → Bind</li>
        <li>In Bambu Handy: tap <strong>+</strong> → Scan QR code</li>
        <li>Point your phone at the printer screen — you should see a success message</li>
      </ol>
      ${this.renderNav()}
    </div>`;
  }

  afterMount(container) {
    super.afterMount(container);
    this.bindNav(container);
  }
}
