import LocalUploadAdapter from '../../server/adapters/model-sources/local-upload.js';

describe('LocalUploadAdapter', () => {
  const adapter = new LocalUploadAdapter();

  test('search() always returns empty array', async () => {
    const results = await adapter.search('anything');
    expect(results).toEqual([]);
  });

  test('getDetail() returns metadata from filename', async () => {
    const detail = await adapter.getDetail('my-cool-model.stl');
    expect(detail.id).toBe('my-cool-model.stl');
    expect(detail.title).toBe('my cool model');
    expect(detail.fileType).toBe('stl');
    expect(detail.fileUrl).toContain('my-cool-model.stl');
  });

  test('getDetail() detects 3MF files', async () => {
    const detail = await adapter.getDetail('organizer.3mf');
    expect(detail.fileType).toBe('3mf');
  });

  test('download() throws for local files', async () => {
    await expect(adapter.download('/some/path')).rejects.toThrow('LocalUpload');
  });
});
