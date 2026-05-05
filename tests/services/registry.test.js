import { registry } from '../../server/services/registry.js';

describe('Service registry', () => {
  test('modelSource() returns an adapter with search()', async () => {
    const source = await registry.modelSource();
    expect(typeof source.search).toBe('function');
    expect(typeof source.getDetail).toBe('function');
    expect(typeof source.download).toBe('function');
  });

  test('slicer() returns an adapter with slice()', async () => {
    const slicer = await registry.slicer();
    expect(typeof slicer.slice).toBe('function');
    expect(typeof slicer.isAvailable).toBe('function');
  });

  test('printer() returns an adapter with getStatus()', async () => {
    const printer = await registry.printer();
    expect(typeof printer.getStatus).toBe('function');
    expect(typeof printer.print).toBe('function');
  });

  test('slicer.isAvailable() returns false in Phase 1', async () => {
    const slicer = await registry.slicer();
    const available = await slicer.isAvailable();
    expect(available).toBe(false);
  });

  test('printer.getStatus() returns not_configured in Phase 1', async () => {
    const printer = await registry.printer();
    const status = await printer.getStatus();
    expect(status.connected).toBe(false);
    expect(status.state).toBe('not_configured');
  });
});
