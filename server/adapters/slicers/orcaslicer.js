import { Slicer } from '../../services/Slicer.js';
import { logger } from '../../lib/logger.js';

/**
 * OrcaSlicer adapter — Phase 2.
 * Wraps the OrcaSlicer CLI to slice models and send to printer.
 */
export default class OrcaSlicerAdapter extends Slicer {
  async slice(_modelPath, _opts) {
    logger.warn('OrcaSlicer adapter not yet implemented (Phase 2)');
    // Phase 1: return mock data so the UI flow works end-to-end
    return {
      gcodeFile: null,
      printTimeSeconds: 3600,
      filamentGrams: 12.4,
      layerCount: 240,
    };
  }

  async isAvailable() {
    return false; // Phase 2 will detect OrcaSlicer install
  }
}
