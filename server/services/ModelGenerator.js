/**
 * ModelGenerator interface — future: text-to-3D (OpenAI, Meshy, Shap-E, etc.)
 */
export class ModelGenerator {
  /** @returns {Promise<{modelPath: string, previewUrl: string}>} */
  async generate(description, options = {}) {
    throw new Error('ModelGenerator.generate() not implemented');
  }
}
