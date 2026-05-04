import express from 'express';
import cors from 'cors';
import { createServer } from 'http';
import { fileURLToPath } from 'url';
import path from 'path';
import { config } from './config.js';
import { v1 } from './api/v1/index.js';
import { errorMiddleware } from './lib/errors.js';
import { attachWebSocket } from './websocket/print-status.js';
import { logger } from './lib/logger.js';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const app = express();
const httpServer = createServer(app);

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Serve Three.js from node_modules
app.use('/vendor/three', express.static(
  path.join(__dirname, '../node_modules/three/build')
));
app.use('/vendor/three/examples', express.static(
  path.join(__dirname, '../node_modules/three/examples')
));

// Serve uploaded models for the 3D viewer
app.use('/models', express.static(
  path.join(__dirname, '../data/models')
));

// API
app.use('/api/v1', v1);

// SPA — serve web/ for everything else
app.use(express.static(path.join(__dirname, '../web')));
app.get('*', (_req, res) => {
  res.sendFile(path.join(__dirname, '../web/index.html'));
});

// Error handler
app.use(errorMiddleware);

// WebSocket
const wss = attachWebSocket(httpServer);

// Start
httpServer.listen(config.port, () => {
  logger.info(`3D Print Agent running → http://localhost:${config.port}`);
});

export { wss };
