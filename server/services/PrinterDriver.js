/**
 * PrinterDriver interface — adapters: bambu-cloud, octoprint, lan-mode, etc.
 */
export class PrinterDriver {
  /** @returns {Promise<{connected: boolean, state: string}>} */
  async getStatus() {
    throw new Error('PrinterDriver.getStatus() not implemented');
  }

  /** @returns {Promise<{jobId: string}>} */
  async print(gcodeFile, options = {}) {
    throw new Error('PrinterDriver.print() not implemented');
  }

  /** @returns {Promise<void>} */
  async pause(jobId) {
    throw new Error('PrinterDriver.pause() not implemented');
  }

  /** @returns {Promise<void>} */
  async cancel(jobId) {
    throw new Error('PrinterDriver.cancel() not implemented');
  }
}
