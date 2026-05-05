import { StepBase } from './step-base.js';

const RELEASE_VERSION = 'v2.3.2';
const RELEASE_BASE = `https://github.com/OrcaSlicer/OrcaSlicer/releases/tag/${RELEASE_VERSION}`;

const DOWNLOADS = {
  arm64: {
    label: 'Apple Silicon (M1/M2/M3/M4)',
    file: `OrcaSlicer_Mac_arm64_${RELEASE_VERSION}.dmg`,
    url: `https://github.com/OrcaSlicer/OrcaSlicer/releases/download/${RELEASE_VERSION}/OrcaSlicer_Mac_arm64_${RELEASE_VERSION}.dmg`,
  },
  x86: {
    label: 'Intel Mac',
    file: `OrcaSlicer_Mac_x86_64_${RELEASE_VERSION}.dmg`,
    url: `https://github.com/OrcaSlicer/OrcaSlicer/releases/download/${RELEASE_VERSION}/OrcaSlicer_Mac_x86_64_${RELEASE_VERSION}.dmg`,
  },
};

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
          <h3>OrcaSlicer ${RELEASE_VERSION} — macOS</h3>
          <p>Pick your Mac type and download the <code>.dmg</code> directly. Not sure?
          Apple logo → <strong>About This Mac</strong> — if it says "Apple M…" choose Apple Silicon, otherwise Intel.</p>
        </div>
      </div>

      <div style="display:flex; gap:12px; flex-wrap:wrap;">
        <a href="${DOWNLOADS.arm64.url}" class="btn btn-primary" download>
          ⬇️ Apple Silicon (M1–M4)
        </a>
        <a href="${DOWNLOADS.x86.url}" class="btn btn-secondary" download>
          ⬇️ Intel Mac
        </a>
        <a href="${RELEASE_BASE}" target="_blank" rel="noopener" class="btn btn-ghost">
          📋 All releases
        </a>
      </div>

      <ol style="padding-left:20px; display:flex; flex-direction:column; gap:8px; font-size:15px; margin-top:8px;">
        <li>Click the correct download button above — a <code>.dmg</code> file will download</li>
        <li>Open the <code>.dmg</code> from your Downloads folder</li>
        <li>Drag <strong>OrcaSlicer</strong> to the <strong>Applications</strong> folder shortcut in the window</li>
        <li>Launch OrcaSlicer from Applications</li>
        <li>macOS may warn "unverified developer" — <strong>right-click the app → Open</strong> to bypass this</li>
        <li>Sign in with your Bambu account when the login screen appears</li>
      </ol>

      <div class="alert alert-info">
        💡 You can skip this step for now — OrcaSlicer is only needed when you're ready to actually send a print job (Phase 2).
      </div>
      ${this.renderNav({ nextLabel: 'Installed →' })}
    </div>`;
  }

  afterMount(container) {
    super.afterMount(container);
    this.bindNav(container);
  }
}
