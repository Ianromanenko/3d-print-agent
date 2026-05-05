import { Router } from './router.js';
import { state } from './state.js';
import { HelpPanel } from './components/help-panel.js';

// Stage 1 — Hardware setup
import { Step11Welcome }     from './steps/1.1-welcome.js';
import { Step12UnboxCheck }  from './steps/1.2-unbox-check.js';
import { Step13PlacePrinter} from './steps/1.3-place-printer.js';
import { Step14PowerOn }     from './steps/1.4-power-on.js';
import { Step15Calibration } from './steps/1.5-calibration.js';
import { Step16Wifi }        from './steps/1.6-wifi.js';
import { Step17BindAccount } from './steps/1.7-bind-account.js';
import { Step18OrcaSlicer }  from './steps/1.8-orcaslicer.js';
import { Step19Login }       from './steps/1.9-login.js';
import { Step110Verify }     from './steps/1.10-verify.js';

// Stage 2 — Per-print setup
import { Step21CleanPlate }  from './steps/2.1-clean-plate.js';
import { Step22LoadFilament} from './steps/2.2-load-filament.js';
import { Step23FilamentType} from './steps/2.3-filament-type.js';

// Stage 3 — Choose model
import { Step31FindModel }   from './steps/3.1-find-model.js';

// Stage 4 — Preview & confirm
import { Step41Preview }     from './steps/4.1-preview.js';

// Stage 5 — Print
import { Step51Print }       from './steps/5.1-print.js';

function init() {
  const container = document.getElementById('wizard-container');
  const helpPanelEl = document.getElementById('help-panel');
  const helpContentEl = document.getElementById('help-panel-content');
  const help = new HelpPanel(helpPanelEl, helpContentEl);

  document.getElementById('btn-help').addEventListener('click', () => help.toggle());
  document.getElementById('btn-close-help').addEventListener('click', () => help.hide());

  const settingsModal = document.getElementById('settings-modal');
  document.getElementById('btn-settings').addEventListener('click', () => settingsModal.showModal());
  document.getElementById('btn-close-settings').addEventListener('click', () => settingsModal.close());
  document.getElementById('btn-reset-setup').addEventListener('click', () => {
    state.set('setupComplete', false);
    settingsModal.close();
    router.goto('1.1');
  });
  document.getElementById('btn-reset-all').addEventListener('click', () => {
    if (confirm('Reset all progress?')) { state.reset(); location.reload(); }
  });

  const router = new Router(container, help);

  // Always register all steps — router skips Stage 1 if setupComplete
  const setupSteps = [
    new Step11Welcome(),
    new Step12UnboxCheck(),
    new Step13PlacePrinter(),
    new Step14PowerOn(),
    new Step15Calibration(),
    new Step16Wifi(),
    new Step17BindAccount(),
    new Step18OrcaSlicer(),
    new Step19Login(),
    new Step110Verify(),
  ];

  const printSteps = [
    new Step21CleanPlate(),
    new Step22LoadFilament(),
    new Step23FilamentType(),
    new Step31FindModel(),
    new Step41Preview(),
    new Step51Print(),
  ];

  // Skip Stage 1 if setup already done
  const steps = state.isSetupComplete()
    ? printSteps
    : [...setupSteps, ...printSteps];

  steps.forEach(s => router.register(s));
  router.start();
}

document.addEventListener('DOMContentLoaded', init);
