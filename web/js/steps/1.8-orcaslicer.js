import { StepBase } from './step-base.js';

const RELEASE_VERSION = 'v2.3.2';
const DMG_URL = `https://github.com/OrcaSlicer/OrcaSlicer/releases/download/${RELEASE_VERSION}/OrcaSlicer_Mac_universal_V2.3.2.dmg`;
const RELEASES_PAGE = `https://github.com/OrcaSlicer/OrcaSlicer/releases/tag/${RELEASE_VERSION}`;
const BREW_CMD = 'brew install --cask orcaslicer';

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
          <p>Pick the easiest method for you. The universal <code>.dmg</code> works on
          <strong>both Apple Silicon and Intel Macs</strong>.</p>
        </div>
      </div>

      <!-- Option A: One-line Homebrew install -->
      <div style="background:var(--c-surface); border:1px solid var(--c-border);
        border-radius:var(--radius); padding:20px; display:flex; flex-direction:column; gap:12px;">
        <div style="display:flex; align-items:center; gap:8px;">
          <span class="badge badge-success">Easiest</span>
          <strong>Option A — Homebrew (1 command)</strong>
        </div>
        <p style="font-size:14px; color:var(--c-muted); margin:0;">
          Open Terminal, paste this, and press Enter:
        </p>
        <div style="display:flex; gap:8px; align-items:stretch;">
          <code id="brew-cmd" style="flex:1; padding:10px 14px; background:var(--c-surface2);
            border:1px solid var(--c-border); border-radius:var(--radius-sm);
            font-family:monospace; font-size:14px; user-select:all;">${BREW_CMD}</code>
          <button class="btn btn-secondary btn-sm" id="btn-copy-brew">📋 Copy</button>
        </div>
        <p style="font-size:13px; color:var(--c-muted); margin:0;">
          Don't have Homebrew? Install it first with one command from
          <a href="https://brew.sh" target="_blank" rel="noopener" style="color:var(--c-primary);">brew.sh</a>.
        </p>
      </div>

      <!-- Option B: Direct .dmg download -->
      <div style="background:var(--c-surface); border:1px solid var(--c-border);
        border-radius:var(--radius); padding:20px; display:flex; flex-direction:column; gap:12px;">
        <strong>Option B — Direct .dmg download</strong>
        <a href="${DMG_URL}" class="btn btn-primary" download>
          ⬇️ Download OrcaSlicer ${RELEASE_VERSION}.dmg (universal)
        </a>
        <p style="font-size:13px; color:var(--c-muted); margin:0;">
          Or browse <a href="${RELEASES_PAGE}" target="_blank" rel="noopener" style="color:var(--c-primary);">all releases on GitHub</a>.
        </p>
      </div>

      <!-- Manual install steps -->
      <details style="background:var(--c-surface); border:1px solid var(--c-border);
        border-radius:var(--radius); padding:16px 20px;">
        <summary style="cursor:pointer; font-weight:600;">📦 After downloading the .dmg…</summary>
        <ol style="padding-left:20px; display:flex; flex-direction:column; gap:8px; font-size:14px; margin-top:12px;">
          <li>Open the <code>.dmg</code> from your Downloads folder</li>
          <li>Drag <strong>OrcaSlicer</strong> into the <strong>Applications</strong> folder shortcut in the window</li>
          <li>Launch OrcaSlicer from Applications</li>
          <li>If macOS warns "unverified developer", <strong>right-click the app → Open</strong> → confirm</li>
          <li>Sign in with your Bambu account when the login screen appears</li>
        </ol>
      </details>

      <div class="alert alert-info">
        💡 You can skip this step for now — OrcaSlicer is only needed when you're ready to actually send a print job (Phase 2).
      </div>
      ${this.renderNav({ nextLabel: 'Installed →' })}
    </div>`;
  }

  afterMount(container) {
    super.afterMount(container);
    const btn = container.querySelector('#btn-copy-brew');
    if (btn) {
      btn.addEventListener('click', async () => {
        try {
          await navigator.clipboard.writeText(BREW_CMD);
          btn.textContent = '✅ Copied';
          setTimeout(() => { btn.textContent = '📋 Copy'; }, 1800);
        } catch {
          btn.textContent = '⚠️ Press ⌘C';
        }
      });
    }
    this.bindNav(container);
  }
}
