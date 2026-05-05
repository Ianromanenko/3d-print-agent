import { state } from '../state.js';
import { i18n } from '../i18n.js';

/**
 * Base class for all wizard steps.
 * SECURITY NOTE: innerHTML is used only for trusted template strings (our code,
 * not user input). Any user-supplied text is always inserted via textContent.
 */
export class StepBase {
  constructor({ id, title, optional = false } = {}) {
    this.id = id;
    this.title = title;
    this.optional = optional;
    this._router = null;
  }

  mount(container, router) {
    this._router = router;
    state.setStepStatus(this.id, 'in-progress');
    // Safe: render() returns trusted template HTML only
    container.innerHTML = this.render(); // eslint-disable-line no-unsanitized/property
    this.afterMount(container);
  }

  render() {
    return `<div class="step">
      <h2 class="step-title"></h2>
      <p>Step ${this.id} — override render() in your step class.</p>
      ${this.renderNav()}
    </div>`;
  }

  afterMount(container) {
    // Set title via textContent to avoid any XSS risk from step title strings
    const h2 = container.querySelector('.step-title');
    if (h2) h2.textContent = this.title;
  }

  renderNav({ nextLabel, backLabel, showBack = true, showNext = true } = {}) {
    const back = showBack
      ? `<button class="btn btn-secondary" id="btn-back">${backLabel || i18n.t('back')}</button>`
      : '';
    const next = showNext
      ? `<button class="btn btn-primary" id="btn-next">${nextLabel || i18n.t('next')}</button>`
      : '';
    const skip = this.optional
      ? `<button class="btn btn-ghost" id="btn-skip">${i18n.t('skip')}</button>`
      : '';
    return `<div class="step-nav">${back}${skip}${next}</div>`;
  }

  bindNav(container) {
    container.querySelector('#btn-next')?.addEventListener('click', () => this.complete());
    container.querySelector('#btn-back')?.addEventListener('click', () => this._router.back());
    container.querySelector('#btn-skip')?.addEventListener('click', () => this._router.skip(this.id));
  }

  complete() {
    state.setStepStatus(this.id, 'completed');
    this._router.next();
  }
}
