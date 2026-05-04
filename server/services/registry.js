import { config } from '../config.js';
import { logger } from '../lib/logger.js';

const adapters = {};

async function load(category, name) {
  const key = `${category}:${name}`;
  if (adapters[key]) return adapters[key];

  const paths = {
    'modelSource:makerworld':   '../adapters/model-sources/makerworld.js',
    'modelSource:local-upload': '../adapters/model-sources/local-upload.js',
    'slicer:orcaslicer':        '../adapters/slicers/orcaslicer.js',
    'printerDriver:bambu-cloud':'../adapters/printer-drivers/bambu-cloud.js',
  };

  const modulePath = paths[key];
  if (!modulePath) throw new Error(`No adapter registered for ${key}`);

  const mod = await import(modulePath);
  const instance = new mod.default();
  adapters[key] = instance;
  logger.info(`Loaded adapter: ${key}`);
  return instance;
}

export const registry = {
  modelSource: () => load('modelSource', config.services.modelSource),
  slicer:      () => load('slicer',      config.services.slicer),
  printer:     () => load('printerDriver', config.services.printerDriver),
};
