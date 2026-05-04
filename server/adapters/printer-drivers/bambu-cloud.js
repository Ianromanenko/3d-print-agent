import { PrinterDriver } from '../../services/PrinterDriver.js';
import { logger } from '../../lib/logger.js';

/**
 * Bambu Cloud driver — Phase 2.
 * Will use MQTT over TLS to send jobs via Bambu's cloud.
 */
export default class BambuCloudDriver extends PrinterDriver {
  async getStatus() {
    logger.warn('BambuCloud driver not yet implemented (Phase 2)');
    return { connected: false, state: 'not_configured' };
  }

  async print(_gcodeFile, _options) {
    logger.warn('BambuCloud driver not yet implemented (Phase 2)');
    return { jobId: `mock-${Date.now()}` };
  }

  async pause(_jobId) {
    logger.warn('BambuCloud pause not yet implemented (Phase 2)');
  }

  async cancel(_jobId) {
    logger.warn('BambuCloud cancel not yet implemented (Phase 2)');
  }
}
