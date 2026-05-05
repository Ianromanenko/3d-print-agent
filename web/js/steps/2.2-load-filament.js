import { StepBase } from './step-base.js';

export class Step22LoadFilament extends StepBase {
  constructor() { super({ id: '2.2', title: 'Load filament' }); }

  render() {
    return `<div class="step">
      <h2 class="step-title"></h2>
      <div class="image-step">
        <div class="image-step-visual">
          <img src="/assets/illustrations/load-filament.svg" alt="Loading filament into Bambu Lab A1" />
        </div>
        <div class="image-step-caption">
          <h3>Insert your filament spool</h3>
          <p>The A1 uses an external spool holder. The filament feeds through a PTFE tube
          into the extruder on the print head.</p>
        </div>
      </div>
      <ol style="padding-left:20px; display:flex; flex-direction:column; gap:8px; font-size:15px;">
        <li>Place your filament spool on the spool holder behind the printer</li>
        <li>Cut the filament end at a sharp 45° angle with scissors or cutters — this helps it thread through</li>
        <li>Feed the filament through the PTFE tube from the spool holder to the print head</li>
        <li>On the printer touchscreen, tap <strong>Filament → Load Filament</strong></li>
        <li>Select <strong>PLA</strong> as the material type</li>
        <li>The printer will heat the nozzle to 220°C — wait for it</li>
        <li>When prompted, push the filament in until the extruder grabs it and pulls automatically</li>
        <li>Wait until you see filament coming out of the nozzle — it's ready!</li>
        <li>Tap <strong>Finish</strong> on the printer screen</li>
      </ol>
      <div class="alert alert-info">
        💡 If you're using <strong>Bambu PLA Silk White</strong>, you may need to set the nozzle
        temperature to <strong>230°C</strong> for best results. You can change this in OrcaSlicer later.
      </div>
      ${this.renderNav()}
    </div>`;
  }

  afterMount(container) {
    super.afterMount(container);
    this.bindNav(container);
  }
}
