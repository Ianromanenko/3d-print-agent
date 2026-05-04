import fetch from 'node-fetch';
import { ModelSource } from '../../services/ModelSource.js';
import { AdapterError } from '../../lib/errors.js';
import { config } from '../../config.js';

const BASE = config.makerworld.apiUrl;
const HEADERS = {
  'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
  'Accept': 'application/json',
  'Referer': 'https://makerworld.com/',
};

export default class MakerWorldAdapter extends ModelSource {
  async search(query, { page = 1, pageSize = 12 } = {}) {
    const url = `${BASE}/design-list/search?keyword=${encodeURIComponent(query)}&page=${page}&page_size=${pageSize}`;
    let res;
    try {
      res = await fetch(url, { headers: HEADERS });
    } catch (e) {
      throw new AdapterError(`MakerWorld fetch failed: ${e.message}`);
    }
    if (!res.ok) throw new AdapterError(`MakerWorld returned ${res.status}`);

    const data = await res.json();
    const items = data.hits ?? data.designs ?? data.items ?? [];

    return items.map(item => ({
      id: String(item.id ?? item.design_id),
      title: item.title ?? item.name ?? 'Untitled',
      thumbnail: item.cover ?? item.thumbnail ?? item.img_url ?? null,
      author: item.designer?.name ?? item.author ?? 'Unknown',
      likes: item.like_count ?? item.likes ?? 0,
      printTime: item.print_time ?? null,
      filament: item.filament ?? null,
      url: `https://makerworld.com/en/models/${item.id ?? item.design_id}`,
    }));
  }

  async getDetail(id) {
    const url = `${BASE}/design/${id}`;
    let res;
    try {
      res = await fetch(url, { headers: HEADERS });
    } catch (e) {
      throw new AdapterError(`MakerWorld detail fetch failed: ${e.message}`);
    }
    if (!res.ok) throw new AdapterError(`MakerWorld detail returned ${res.status}`);

    const item = await res.json();
    return {
      id: String(item.id),
      title: item.title ?? 'Untitled',
      description: item.description ?? '',
      thumbnail: item.cover ?? item.thumbnail ?? null,
      fileUrl: item.download_url ?? null,
      fileType: item.file_type ?? 'stl',
      dimensions: item.dimensions ?? null,
    };
  }

  async download(fileUrl) {
    const res = await fetch(fileUrl, { headers: HEADERS });
    if (!res.ok) throw new AdapterError(`MakerWorld download failed: ${res.status}`);
    return Buffer.from(await res.arrayBuffer());
  }
}
