import { WebSocketServer } from 'ws';
import { logger } from '../lib/logger.js';

export function attachWebSocket(server) {
  const wss = new WebSocketServer({ server, path: '/ws' });

  wss.on('connection', (ws) => {
    logger.info('WebSocket client connected');
    ws.send(JSON.stringify({ type: 'connected', message: 'WebSocket ready' }));

    ws.on('close', () => logger.info('WebSocket client disconnected'));
    ws.on('error', (e) => logger.error('WebSocket error', e.message));
  });

  // Broadcast helper — call this from print adapter when status changes
  wss.broadcast = (data) => {
    const msg = JSON.stringify(data);
    wss.clients.forEach(client => {
      if (client.readyState === 1) client.send(msg);
    });
  };

  return wss;
}
