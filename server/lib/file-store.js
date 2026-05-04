import { promises as fs } from 'fs';
import path from 'path';
import { createReadStream } from 'fs';

export class FileStore {
  constructor(dir) {
    this.dir = dir;
  }

  async ensure() {
    await fs.mkdir(this.dir, { recursive: true });
  }

  filePath(name) {
    return path.join(this.dir, name);
  }

  async save(name, buffer) {
    await this.ensure();
    await fs.writeFile(this.filePath(name), buffer);
    return this.filePath(name);
  }

  async exists(name) {
    try {
      await fs.access(this.filePath(name));
      return true;
    } catch { return false; }
  }

  async list() {
    await this.ensure();
    return fs.readdir(this.dir);
  }

  stream(name) {
    return createReadStream(this.filePath(name));
  }

  async delete(name) {
    await fs.unlink(this.filePath(name));
  }
}
