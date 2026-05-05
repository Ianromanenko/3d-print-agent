import { state } from './state.js';
import { logger } from './logger.js';

/**
 * Wizard router — manages step sequence and navigation.
 * Steps are registered in order; the router tracks current position.
 */
export class Router {
  constructor(container, helpPanel) {
    this.container = container;
    this.helpPanel = helpPanel;
    this.steps = [];      // [{id, instance}]
    this.current = 0;     // index into this.steps
  }

  register(stepInstance) {
    this.steps.push(stepInstance);
    return this;
  }

  /** Jump to a step by ID */
  goto(id) {
    const idx = this.steps.findIndex(s => s.id === id);
    if (idx === -1) { logger.warn(`Router: unknown step ${id}`); return; }
    this.current = idx;
    this._mount();
  }

  next() {
    if (this.current < this.steps.length - 1) {
      this.current++;
      this._mount();
    }
  }

  back() {
    if (this.current > 0) {
      this.current--;
      this._mount();
    }
  }

  skip(id) {
    state.setStepStatus(id, 'skipped');
    this.next();
  }

  start() {
    const saved = state.currentStep();
    const idx = this.steps.findIndex(s => s.id === saved);
    this.current = idx >= 0 ? idx : 0;
    this._mount();
  }

  _mount() {
    const step = this.steps[this.current];
    if (!step) return;
    state.setCurrentStep(step.id);
    this._updateProgress();
    this.container.scrollTo(0, 0);
    step.mount(this.container, this);
  }

  _updateProgress() {
    const total = this.steps.length;
    const done  = this.current;
    const pct   = Math.round((done / total) * 100);
    const bar   = document.getElementById('progress-bar-fill');
    const label = document.getElementById('progress-label');
    if (bar)   bar.style.width = `${pct}%`;
    if (label) label.textContent = `Step ${done + 1} of ${total}`;
  }
}

// Tiny logger shim for the browser
const logger = { warn: (...a) => console.warn(...a) };
