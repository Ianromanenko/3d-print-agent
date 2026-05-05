import { StepBase } from './step-base.js';

export class Step18OrcaSlicer extends StepBase {
  constructor() { super({ id: '1.8', title: 'Install OrcaSlicer', optional: true }); }

  render() {
    return `<div class="step">
      <h2 class="step-title"></h2>
      <p class="step-body">OrcaSlicer is free, open-source software that prepares your 3D models for printing.
      We'll use it to slice models and send print jobs to your A1 in Phase 2 of this agent.</p>
      <div class="image-step">
        <div class="image-step-visual" style="padding: 32px;">
          <img src="/assets/illustrations/orcaslicer-logo.svg" alt="OrcaSlicer logo" style="max-height:120px;" />
        </div>
        <div class="image-step-caption">
          <h3>Download OrcaSlicer (macOS)</h3>
          <p>Click the button below to go to the OrcaSlicer releases page. Download the latest <code>.dmg</code> file for macOS (Apple Silicon or Intel, depending on your Mac).</p>
        </div>
      </div>
      <a href="https://github.com/SoftFever/OrcaSlicer/releases/latest" target="_blank" rel="noopener" class="btn btn-primary">
        ⬇️ Download OrcaSlicer
      </a>
      <ol style="padding-left:20px; display:flex; flex-direction:column; gap:8px; font-size:15px; margin-top:8px;">
        <li>Download the <code>.dmg</code> file</li>
        <li>Open the <code>.dmg</code> and drag <strong>OrcaSlicer</strong> to your Applications folder</li>
        <li>Launch OrcaSlicer — macOS may warn about an unverified developer; right-click the app and choose Open to bypass this</li>
        <li>Sign in with your Bambu account when prompted</li>
      </ol>
      <div class="alert alert-info">
        💡 You can skip this step for now — OrcaSlicer is only needed when you're ready to actually send a print job.
      </div>
      ${this.renderNav({ nextLabel: 'Installed →' })}
    </div>`;
  }

  afterMount(container) {
    super.afterMount(container);
    this.bindNav(container);
  }
}
