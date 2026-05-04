export class AppError extends Error {
  constructor(message, statusCode = 500, code = 'INTERNAL_ERROR') {
    super(message);
    this.statusCode = statusCode;
    this.code = code;
  }
}

export class NotFoundError extends AppError {
  constructor(msg = 'Not found') { super(msg, 404, 'NOT_FOUND'); }
}

export class ValidationError extends AppError {
  constructor(msg = 'Validation error') { super(msg, 400, 'VALIDATION_ERROR'); }
}

export class AdapterError extends AppError {
  constructor(msg = 'Adapter error') { super(msg, 502, 'ADAPTER_ERROR'); }
}

export function errorMiddleware(err, req, res, next) {
  const status = err.statusCode ?? 500;
  const code   = err.code ?? 'INTERNAL_ERROR';
  res.status(status).json({ error: { code, message: err.message } });
}
