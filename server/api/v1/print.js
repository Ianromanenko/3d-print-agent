import { Router } from 'express';
import { registry } from '../../services/registry.js';

export const router = Router();

router.post('/', async (req, res, next) => {
  try {
    const { gcodeFile } = req.body;
    const printer = await registry.printer();
    const job = await printer.print(gcodeFile);
    res.json(job);
  } catch (e) { next(e); }
});
