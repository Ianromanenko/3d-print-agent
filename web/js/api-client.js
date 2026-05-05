const BASE = '/api/v1';

async function request(method, path, body) {
  const opts = {
    method,
    headers: { 'Content-Type': 'application/json' },
  };
  if (body) opts.body = JSON.stringify(body);
  const res = await fetch(`${BASE}${path}`, opts);
  const data = await res.json();
  if (!res.ok) throw new Error(data.error?.message || `HTTP ${res.status}`);
  return data;
}

export const api = {
  search:   (query, page = 1)   => request('POST', '/search', { query, page }),
  download: (fileUrl, filename)  => request('POST', '/download', { fileUrl, filename }),
  slice:    (modelFile, opts)    => request('POST', '/slice', { modelFile, ...opts }),
  print:    (gcodeFile)          => request('POST', '/print', { gcodeFile }),
  status:   ()                   => request('GET',  '/status'),
  wizardState: {
    get:    ()      => request('GET',    '/wizard/state'),
    put:    (data)  => request('PUT',    '/wizard/state', data),
    reset:  ()      => request('DELETE', '/wizard/state'),
  },
};
