import * as THREE from '/vendor/three/three.module.js';
import { OrbitControls } from '/vendor/three/examples/jsm/controls/OrbitControls.js';
import { STLLoader } from '/vendor/three/examples/jsm/loaders/STLLoader.js';

export class Viewer3D {
  constructor(container) {
    this.container = container;
    this._init();
  }

  _init() {
    const w = this.container.clientWidth;
    const h = this.container.clientHeight || w * 0.75;

    // Scene
    this.scene = new THREE.Scene();
    this.scene.background = new THREE.Color(0x1a1a1f);
    this.scene.add(new THREE.AmbientLight(0xffffff, 0.6));
    const dirLight = new THREE.DirectionalLight(0xffffff, 0.8);
    dirLight.position.set(5, 10, 7);
    this.scene.add(dirLight);
    const fillLight = new THREE.DirectionalLight(0x8888ff, 0.3);
    fillLight.position.set(-5, -2, -7);
    this.scene.add(fillLight);

    // Grid
    const grid = new THREE.GridHelper(200, 20, 0x333344, 0x222233);
    this.scene.add(grid);

    // Camera
    this.camera = new THREE.PerspectiveCamera(45, w / h, 0.1, 2000);
    this.camera.position.set(100, 80, 100);

    // Renderer
    this.renderer = new THREE.WebGLRenderer({ antialias: true });
    this.renderer.setPixelRatio(window.devicePixelRatio);
    this.renderer.setSize(w, h);
    this.renderer.shadowMap.enabled = true;
    this.container.appendChild(this.renderer.domElement);

    // Controls
    this.controls = new OrbitControls(this.camera, this.renderer.domElement);
    this.controls.enableDamping = true;
    this.controls.dampingFactor = 0.05;

    // Resize observer
    new ResizeObserver(() => this._onResize()).observe(this.container);

    this._animate();
  }

  async loadSTL(url) {
    const loader = new STLLoader();
    return new Promise((resolve, reject) => {
      loader.load(url, (geometry) => {
        geometry.computeBoundingBox();
        geometry.center();

        const material = new THREE.MeshPhongMaterial({
          color: 0x4f9eff,
          specular: 0x888888,
          shininess: 60,
        });
        const mesh = new THREE.Mesh(geometry, material);
        mesh.castShadow = true;
        mesh.receiveShadow = true;

        this._clearModel();
        this.mesh = mesh;
        this.scene.add(mesh);
        this._fitCamera(mesh);
        resolve(this._getDimensions(geometry));
      }, undefined, reject);
    });
  }

  _getDimensions(geometry) {
    const box = new THREE.Box3().setFromObject(
      new THREE.Mesh(geometry)
    );
    const size = new THREE.Vector3();
    box.getSize(size);
    return {
      x: size.x.toFixed(1),
      y: size.y.toFixed(1),
      z: size.z.toFixed(1),
    };
  }

  _fitCamera(mesh) {
    const box = new THREE.Box3().setFromObject(mesh);
    const center = new THREE.Vector3();
    box.getCenter(center);
    const size = new THREE.Vector3();
    box.getSize(size);
    const maxDim = Math.max(size.x, size.y, size.z);
    const fov = this.camera.fov * (Math.PI / 180);
    const dist = Math.abs(maxDim / Math.sin(fov / 2)) * 0.8;
    this.camera.position.set(center.x + dist, center.y + dist * 0.6, center.z + dist);
    this.controls.target.copy(center);
    this.controls.update();
  }

  _clearModel() {
    if (this.mesh) {
      this.scene.remove(this.mesh);
      this.mesh.geometry.dispose();
      this.mesh.material.dispose();
      this.mesh = null;
    }
  }

  toggleWireframe() {
    if (this.mesh) {
      this.mesh.material.wireframe = !this.mesh.material.wireframe;
    }
  }

  resetView() {
    if (this.mesh) this._fitCamera(this.mesh);
  }

  _onResize() {
    const w = this.container.clientWidth;
    const h = this.container.clientHeight || w * 0.75;
    this.camera.aspect = w / h;
    this.camera.updateProjectionMatrix();
    this.renderer.setSize(w, h);
  }

  _animate() {
    requestAnimationFrame(() => this._animate());
    this.controls.update();
    this.renderer.render(this.scene, this.camera);
  }

  dispose() {
    this._clearModel();
    this.renderer.dispose();
  }
}
