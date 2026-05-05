import { StepBase } from './step-base.js';

export class Step15Calibration extends StepBase {
  constructor() { super({ id: '1.5', title: 'Initial calibration' }); }

  render() {
    return `<div class="step">
      <h2 class="step-title"></h2>
      <div class="image-step">
        <div class="image-step-visual">
          <img src="/assets/illustrations/calibration-screen.svg" alt="Bambu Lab A1 calibration screen" />
        </div>
        <div class="image-step-caption">
          <h3>Follow the on-screen setup wizard</h3>
          <p>The printer will guide you through first-time calibration automatically.
          Tap <strong>OK / Start</strong> on each screen and let the printer run its calibration routine.
          This takes about 5–10 minutes.</p>
        </div>
      </div>
      <div class="alert alert-warn">
        ⚠️ Don't touch the printer or the build plate while calibration is running.
        If it asks you to install the build plate first, click it in on all four corners.
      </div>
      ${this.renderNav()}
    </div>`;
  }

  afterMount(container) {
    super.afterMount(container);
    this.bindNav(container);
  }
}
