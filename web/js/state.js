const KEY = '3dpa_state';

function load() {
  try { return JSON.parse(localStorage.getItem(KEY) || '{}'); }
  catch { return {}; }
}

function save(s) {
  localStorage.setItem(KEY, JSON.stringify(s));
}

let _state = load();
const _listeners = new Set();

export const state = {
  get: (key) => key ? _state[key] : { ..._state },

  set: (key, value) => {
    _state = { ..._state, [key]: value };
    save(_state);
    _listeners.forEach(fn => fn(_state));
    // Sync to server (best-effort, non-blocking)
    fetch('/api/v1/wizard/state', {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ [key]: value }),
    }).catch(() => {});
  },

  reset: () => {
    _state = {};
    save(_state);
    fetch('/api/v1/wizard/state', { method: 'DELETE' }).catch(() => {});
    _listeners.forEach(fn => fn(_state));
  },

  subscribe: (fn) => {
    _listeners.add(fn);
    return () => _listeners.delete(fn);
  },

  // Convenience
  isSetupComplete: () => !!_state.setupComplete,
  setSetupComplete: () => state.set('setupComplete', true),
  currentStep: () => _state.currentStep || '1.1',
  setCurrentStep: (id) => state.set('currentStep', id),
  stepStatus: (id) => _state[`step_${id}`] || 'not-started',
  setStepStatus: (id, status) => state.set(`step_${id}`, status),
};
