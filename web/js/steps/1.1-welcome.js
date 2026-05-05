import { StepBase } from './step-base.js';

export class Step11Welcome extends StepBase {
  constructor() { super({ id: '1.1', title: 'Welcome to 3D Print Agent' }); }

  render() {
    return `<div class="step">
      <div style="text-align:center; padding: 24px 0;">
        <div style="font-size:80px; margin-bottom:16px;">🖨️</div>
        <h1 class="step-title" style="font-size:32px;">Your first 3D print starts here</h1>
        <p class="step-subtitle" style="margin-top:12px; font-size:17px;">
          This wizard will guide you through everything — from turning on your Bambu Lab A1
          to holding your finished print in your hands.<br><br>
          <strong>No experience needed.</strong> We'll go step by step.
        </p>
      </div>
      <div class="alert alert-info" style="margin-top:8px;">
        📦 Before we start, make sure your Bambu Lab A1 box is nearby and you have
        a bottle of <strong>isopropyl alcohol (90%+)</strong> for cleaning the build plate.
      </div>
      ${this.renderNav({ showBack: false, nextLabel: "Let's go →" })}
    </div>`;
  }

  afterMount(container) {
    super.afterMount(container);
    this.bindNav(container);
  }
}
