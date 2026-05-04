import { Router } from 'express';
import { registry } from '../../services/registry.js';
import { config } from '../../config.js';
import { FileStore } from '../../lib/file-store.js';
import { ValidationError, NotFoundError } from '../../lib/errors.js';
import path from 'path';

export const router = Router();
const store = new FileStore(config.data.modelsDir);

// Download a model from a source (MakerWorld) and cache locally
router.post('/', async (req, res, next) => {
  try {
    const { fileUrl, filename } = req.body;
    if (!fileUrl) throw new ValidationError('fileUrl is required');
    const name = filename ?? path.basename(new URL(fileUrl).pathname);
    if (await store.exists(name)) {
      return res.json({ filename: name, cached: true });
    }
    const source = await registry.modelSource();
    const buf = await source.download(fileUrl);
    await store.save(name, buf);
    res.json({ filename: name, cached: false });
  } catch (e) { next(e); }
});

// Serve a cached local model file
router.get('/local/:filename', async (req, res, next) => {
  try {
    const { filename } = req.params;
    if (!await store.exists(filename)) throw new NotFoundError(`Model not found: ${filename}`);
    const ext = path.extname(filename).toLowerCase();
    const ct = ext === '.3mf' ? 'application/zip' : 'application/octet-stream';
    res.setHeader('Content-Type', ct);
    store.stream(filename).pipe(res);
  } catch (e) { next(e); }
});
