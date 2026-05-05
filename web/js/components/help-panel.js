// SECURITY: All content in ISSUES is hardcoded in this file (not user input).
// innerHTML is used only to render this trusted static data.
const ISSUES = [
  {
    id: 'not-detected',
    title: 'Printer not detected',
    steps: [
      'Make sure the printer is powered on (switch on the back).',
      'Check that the printer shows a WiFi icon — if not, go through WiFi setup again.',
      'Restart the printer and wait 60 seconds.',
      'Make sure your Mac and the printer are on the same WiFi network.',
      'Try logging out and back into the Bambu Handy app.',
    ],
  },
  {
    id: 'first-layer',
    title: 'First layer not sticking',
    steps: [
      'Clean the build plate with 90%+ isopropyl alcohol — wipe in one direction, rotate 90° and wipe again.',
      'Let the plate dry completely (30 seconds).',
      'Make sure the plate is clipped in correctly on all four corners.',
      'Run Auto Bed Leveling from the printer touchscreen (Settings → Calibration).',
      'Try slowing the first layer speed to 20 mm/s in OrcaSlicer.',
      'If using Silk PLA, increase bed temperature to 60°C.',
    ],
  },
  {
    id: 'stringing',
    title: 'Stringing or blobs between parts',
    steps: [
      'Silk PLA tends to string more than regular PLA — this is normal.',
      'In OrcaSlicer, increase retraction distance to 0.8–1.2 mm.',
      'Lower the nozzle temperature by 5°C (try 225°C).',
      'Enable "Wipe while retracting" in OrcaSlicer.',
    ],
  },
  {
    id: 'jam',
    title: 'Filament jam / no extrusion',
    steps: [
      'On the touchscreen, go to Filament → Unload Filament.',
      'Wait for nozzle to heat to 220°C, then pull filament out gently.',
      'Cut off any blob at the tip with scissors.',
      'Re-insert filament until the extruder grabs it.',
      'Go to Filament → Load Filament and wait until it comes out the nozzle.',
    ],
  },
  {
    id: 'stopped',
    title: 'Print stopped mid-way',
    steps: [
      'Check the printer screen for an error message.',
      'If "runout": load new filament and resume.',
      'If "LIDAR error": clean the LIDAR sensor with a dry cloth.',
      'Check WiFi — a disconnection can pause the print.',
      'Try resuming from the printer touchscreen (Print → Resume).',
    ],
  },
  {
    id: 'software',
    title: 'Software / connection errors',
    steps: [
      'Make sure the backend is running: open terminal → "npm start" in project folder.',
      'Make sure OrcaSlicer is installed: run "npm run check-orcaslicer".',
      'Check you are signed into your Bambu account in OrcaSlicer.',
      'Restart both the printer and OrcaSlicer.',
    ],
  },
];

function buildPanelDOM(contentEl) {
  contentEl.textContent = '';
  ISSUES.forEach(issue => {
    const details = document.createElement('details');
    details.className = 'help-issue';

    const summary = document.createElement('summary');
    summary.className = 'help-issue-title';
    summary.textContent = issue.title;
    details.appendChild(summary);

    const body = document.createElement('div');
    body.className = 'help-issue-body';
    const ol = document.createElement('ol');
    issue.steps.forEach(step => {
      const li = document.createElement('li');
      li.textContent = step;
      ol.appendChild(li);
    });
    body.appendChild(ol);
    details.appendChild(body);
    contentEl.appendChild(details);
  });
}

export class HelpPanel {
  constructor(panelEl, contentEl) {
    this.panelEl = panelEl;
    this.contentEl = contentEl;
    buildPanelDOM(contentEl);
  }

  toggle() { this.panelEl.classList.toggle('hidden'); }
  show()   { this.panelEl.classList.remove('hidden'); }
  hide()   { this.panelEl.classList.add('hidden'); }
}
