import { StepBase } from './step-base.js';

export class Step13PlacePrinter extends StepBase {
  constructor() { super({ id: '1.3', title: 'Place the printer' }); }

  render() {
    return `<div class="step">
      <h2 class="step-title"></h2>
      <div class="image-step">
        <div class="image-step-visual">
          <img src="/assets/illustrations/place-printer.svg" alt="Place printer on flat surface with clearance" />
        </div>
        <div class="image-step-caption">
          <h3>Find a good spot</h3>
          <p>Place your printer on a <strong>stable, flat surface</strong> — a desk or table works well.
          Leave at least <strong>10 cm (4 inches)</strong> of clearance on all sides so air can flow freely
          and the print head won't bump anything.</p>
        </div>
      </div>
      <div class="alert alert-warn">
        ⚠️ Avoid placing the printer near an open window or air vent — drafts can cause failed prints.
      </div>
      ${this.renderNav()}
    </div>`;
  }

  afterMount(container) {
    super.afterMount(container);
    this.bindNav(container);
  }
}
