import { Router } from 'express';
import { registry } from '../../services/registry.js';

export const router = Router();

router.post('/', async (req, res, next) => {
  try {
    const { modelFile, scalePercent = 100, copies = 1 } = req.body;
    const slicer = await registry.slicer();
    const result = await slicer.slice(modelFile, { scalePercent, copies });
    res.json(result);
  } catch (e) { next(e); }
});
