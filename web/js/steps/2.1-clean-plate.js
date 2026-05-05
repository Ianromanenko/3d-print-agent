import { StepBase } from './step-base.js';

export class Step21CleanPlate extends StepBase {
  constructor() { super({ id: '2.1', title: 'Clean the build plate' }); }

  render() {
    return `<div class="step">
      <h2 class="step-title"></h2>
      <div class="image-step">
        <div class="image-step-visual">
          <img src="/assets/illustrations/clean-plate.svg" alt="Cleaning the build plate with isopropyl alcohol" />
        </div>
        <div class="image-step-caption">
          <h3>Wipe with isopropyl alcohol</h3>
          <p>This is the most important step for a successful first layer. Skin oils and dust
          prevent filament from sticking. Do this before <em>every</em> print.</p>
        </div>
      </div>
      <ol style="padding-left:20px; display:flex; flex-direction:column; gap:8px; font-size:15px;">
        <li>Remove the build plate from the printer — it's magnetic, just lift it off</li>
        <li>Put a few drops of <strong>90%+ isopropyl alcohol</strong> on a paper towel or lint-free cloth</li>
        <li>Wipe the plate in <strong>one direction</strong> (e.g., left to right) across the whole surface</li>
        <li>Rotate the plate 90° and wipe again in the same direction</li>
        <li>Let it dry for 30 seconds (it evaporates fast)</li>
        <li>Handle only by the edges from now on — don't touch the print surface with your fingers</li>
        <li>Clip the plate back onto the printer — you'll feel it snap into the magnetic corners</li>
      </ol>
      <div class="alert alert-warn">
        ⚠️ Never use regular rubbing alcohol (70%) — it leaves residue that makes prints fail.
        Use <strong>90%+</strong> isopropyl, available at any pharmacy.
      </div>
      ${this.renderNav()}
    </div>`;
  }

  afterMount(container) {
    super.afterMount(container);
    this.bindNav(container);
  }
}
