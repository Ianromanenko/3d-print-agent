import { StepBase } from './step-base.js';

export class Step14PowerOn extends StepBase {
  constructor() { super({ id: '1.4', title: 'Power on the printer' }); }

  render() {
    return `<div class="step">
      <h2 class="step-title"></h2>
      <div class="image-step">
        <div class="image-step-visual">
          <img src="/assets/illustrations/power-switch.svg" alt="Power switch location on back of Bambu Lab A1" />
        </div>
        <div class="image-step-caption">
          <h3>Flip the power switch</h3>
          <p>Plug the power cable into the back of the printer and into a wall outlet.
          Find the <strong>rocker switch on the back-left</strong> of the printer and flip it to <strong>ON (I)</strong>.</p>
        </div>
      </div>
      <div class="alert alert-info">
        💡 The screen will light up and the printer will make a startup sound. This takes about 30 seconds.
        Wait until you see the home screen before proceeding.
      </div>
      ${this.renderNav()}
    </div>`;
  }

  afterMount(container) {
    super.afterMount(container);
    this.bindNav(container);
  }
}
