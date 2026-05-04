import { Router } from 'express';
import { registry } from '../../services/registry.js';
import { ValidationError } from '../../lib/errors.js';

export const router = Router();

router.post('/', async (req, res, next) => {
  try {
    const { query, page = 1, pageSize = 12 } = req.body;
    if (!query || typeof query !== 'string' || !query.trim()) {
      throw new ValidationError('query is required');
    }
    const source = await registry.modelSource();
    const results = await source.search(query.trim(), { page, pageSize });
    res.json({ results, page, pageSize, query });
  } catch (e) { next(e); }
});
