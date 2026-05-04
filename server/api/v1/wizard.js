import { Router } from 'express';
import { promises as fs } from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

export const router = Router();
const __dirname = path.dirname(fileURLToPath(import.meta.url));
const STATE_FILE = path.join(__dirname, '../../../data/wizard-state.json');

async function readState() {
  try {
    const raw = await fs.readFile(STATE_FILE, 'utf8');
    return JSON.parse(raw);
  } catch { return {}; }
}

async function writeState(state) {
  await fs.mkdir(path.dirname(STATE_FILE), { recursive: true });
  await fs.writeFile(STATE_FILE, JSON.stringify(state, null, 2));
}

// GET /api/v1/wizard/state
router.get('/state', async (req, res, next) => {
  try {
    res.json(await readState());
  } catch (e) { next(e); }
});

// PUT /api/v1/wizard/state
router.put('/state', async (req, res, next) => {
  try {
    const current = await readState();
    const merged = { ...current, ...req.body };
    await writeState(merged);
    res.json(merged);
  } catch (e) { next(e); }
});

// DELETE /api/v1/wizard/state (reset)
router.delete('/state', async (req, res, next) => {
  try {
    await writeState({});
    res.json({ reset: true });
  } catch (e) { next(e); }
});
