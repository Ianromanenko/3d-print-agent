import { Router } from 'express';
import { registry } from '../../services/registry.js';

export const router = Router();

router.get('/', async (req, res, next) => {
  try {
    const printer = await registry.printer();
    const status = await printer.getStatus();
    res.json(status);
  } catch (e) { next(e); }
});
