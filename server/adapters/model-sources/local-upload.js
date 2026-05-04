import { ModelSource } from '../../services/ModelSource.js';

/**
 * LocalUpload adapter — handles files uploaded directly by the user.
 * No search capability; getDetail and download work on already-stored files.
 */
export default class LocalUploadAdapter extends ModelSource {
  async search(_query) {
    // Local uploads don't support search — the UI handles this
    return [];
  }

  async getDetail(filename) {
    return {
      id: filename,
      title: filename.replace(/\.(stl|3mf)$/i, '').replace(/[-_]/g, ' '),
      description: 'Locally uploaded model',
      thumbnail: null,
      fileUrl: `/api/v1/download/local/${encodeURIComponent(filename)}`,
      fileType: filename.toLowerCase().endsWith('.3mf') ? '3mf' : 'stl',
      dimensions: null,
    };
  }

  async download(_fileUrl) {
    throw new Error('LocalUpload: download not applicable — file already on disk');
  }
}
