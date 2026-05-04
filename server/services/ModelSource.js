/**
 * ModelSource interface — all model-source adapters must implement these methods.
 * Swap implementations by changing config.services.modelSource.
 */
export class ModelSource {
  /** @returns {Promise<{id,title,thumbnail,author,likes,printTime,filament,url}[]>} */
  async search(query, { page = 1, pageSize = 12 } = {}) {
    throw new Error('ModelSource.search() not implemented');
  }

  /** @returns {Promise<{id,title,description,thumbnail,fileUrl,fileType,dimensions}>} */
  async getDetail(id) {
    throw new Error('ModelSource.getDetail() not implemented');
  }

  /** @returns {Promise<Buffer>} */
  async download(fileUrl) {
    throw new Error('ModelSource.download() not implemented');
  }
}
