/**
 * Slicer interface — adapters: orcaslicer (Phase 2), bambu-studio, prusaslicer, etc.
 */
export class Slicer {
  /** @returns {Promise<{gcodeFile, printTimeSeconds, filamentGrams, layerCount}>} */
  async slice(modelPath, { profile = 'default', scalePercent = 100, copies = 1 } = {}) {
    throw new Error('Slicer.slice() not implemented');
  }

  /** @returns {Promise<boolean>} */
  async isAvailable() {
    throw new Error('Slicer.isAvailable() not implemented');
  }
}
