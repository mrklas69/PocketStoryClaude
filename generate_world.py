"""Generate a Three.js world visualization as a standalone HTML file.

Usage:
    .venv/Scripts/python.exe generate_world.py
    Then open frontend/index.html in a browser.
"""

import json
import math
from collections import defaultdict
from pathlib import Path

from backend.core.entity import Entity, EntityType


# ── Build the demo world ────────────────────────────────────────────────────

world   = Entity("The World",             EntityType.ENVI,   capacity=None)
valley  = Entity("Green Valley",          EntityType.ENVI,   capacity=10,  parent_id=world.id)
harold  = Entity("Harold",               EntityType.CHAR,               parent_id=valley.id)
shield  = Entity("Harold's Heavy Shield", EntityType.UNIQUE,             parent_id=harold.id)
apples  = Entity("Apples",               EntityType.SUMS,    number=12,   parent_id=harold.id)
fishing = Entity("Fishing",              EntityType.RULES,             parent_id=harold.id)

all_entities = [world, valley, harold, shield, apples, fishing]


# ── Tree layout in 3D ───────────────────────────────────────────────────────

def compute_layout(entities: list[Entity]) -> dict:
    by_parent: dict = defaultdict(list)
    for e in entities:
        if e.parent_id is not None:
            by_parent[str(e.parent_id)].append(e)

    root = next(e for e in entities if e.parent_id is None)
    positions: dict = {}

    def place(entity, x, y, z, angle_start, angle_span, radius):
        positions[str(entity.id)] = (x, y, z)
        children = by_parent[str(entity.id)]
        n = len(children)
        if n == 0:
            return
        child_radius = max(1.5, radius * 0.6)
        child_y = y - 2.5
        for i, child in enumerate(children):
            angle = angle_start if n == 1 else (
                angle_start - angle_span / 2 + (i / (n - 1)) * angle_span
            )
            cx = x + radius * math.cos(angle)
            cz = z + radius * math.sin(angle)
            child_span = min(angle_span / max(n, 1) * 1.8, math.pi * 1.5)
            place(child, cx, child_y, cz, angle, child_span, child_radius)

    place(root, 0, 4, 0, math.pi / 2, math.pi * 2, 4)
    return positions


positions = compute_layout(all_entities)

TYPE_COLORS = {
    "ENVI":   "#4488ff",
    "CHAR":   "#44ff88",
    "UNIQUE": "#ffcc44",
    "SUMS":   "#ff44cc",
    "RULES": "#44ffff",
}

nodes = []
for e in all_entities:
    pos = positions.get(str(e.id), (0, 0, 0))
    label = e.name + (f" \u00d7{e.number}" if e.type == EntityType.SUMS else "")
    nodes.append({
        "id":    str(e.id),
        "name":  label,
        "type":  e.type.value,
        "color": TYPE_COLORS[e.type.value],
        "x":     round(pos[0], 3),
        "y":     round(pos[1], 3),
        "z":     round(pos[2], 3),
    })

edges = [
    {"from": str(e.parent_id), "to": str(e.id)}
    for e in all_entities if e.parent_id is not None
]

world_data = {"nodes": nodes, "edges": edges}


# ── HTML template ───────────────────────────────────────────────────────────

HTML = """\
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>PocketStory — World View</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body { background: #0a0a18; overflow: hidden; font-family: 'Courier New', monospace; }
    #app { width: 100vw; height: 100vh; }
    .label {
      color: #eee;
      font-size: 11px;
      padding: 2px 8px;
      background: rgba(0,0,0,0.6);
      border-radius: 4px;
      pointer-events: none;
      white-space: nowrap;
    }
    #legend {
      position: fixed; top: 16px; right: 16px;
      background: rgba(10,10,24,0.88);
      border: 1px solid rgba(255,255,255,0.08);
      padding: 14px 18px; border-radius: 8px;
      font-size: 12px; line-height: 2.1; color: #bbb;
    }
    #legend h3 { margin-bottom: 4px; font-size: 14px; color: #fff; letter-spacing: 1px; }
    .dot {
      display: inline-block; width: 10px; height: 10px;
      border-radius: 50%; margin-right: 8px; vertical-align: middle;
    }
    #hint {
      position: fixed; bottom: 16px; left: 50%; transform: translateX(-50%);
      color: rgba(255,255,255,0.25); font-size: 11px; pointer-events: none;
    }
  </style>
  <script type="importmap">
  { "imports": {
      "three": "https://cdn.jsdelivr.net/npm/three@0.170.0/build/three.module.js",
      "three/addons/": "https://cdn.jsdelivr.net/npm/three@0.170.0/examples/jsm/"
  } }
  </script>
</head>
<body>
  <div id="app"></div>
  <div id="legend">
    <h3>PocketStory</h3>
    <div><span class="dot" style="background:#4488ff"></span>ENVI &mdash; Kulisy</div>
    <div><span class="dot" style="background:#44ff88"></span>CHAR &mdash; Herci</div>
    <div><span class="dot" style="background:#ffcc44"></span>UNIQUE &mdash; Rekvizita</div>
    <div><span class="dot" style="background:#ff44cc"></span>SUMS &mdash; Zásoby</div>
    <div><span class="dot" style="background:#44ffff"></span>RULES &mdash; Scén&aacute;ř</div>
  </div>
  <div id="hint">drag to rotate &nbsp;&middot;&nbsp; scroll to zoom</div>

  <script type="module">
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { CSS2DRenderer, CSS2DObject } from 'three/addons/renderers/CSS2DRenderer.js';

const DATA = __WORLD_DATA__;

// Scene
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x0a0a18);
scene.fog = new THREE.FogExp2(0x0a0a18, 0.035);

// Camera
const camera = new THREE.PerspectiveCamera(55, innerWidth / innerHeight, 0.1, 200);
camera.position.set(4, 6, 14);

// WebGL renderer
const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setPixelRatio(devicePixelRatio);
renderer.setSize(innerWidth, innerHeight);
document.getElementById('app').appendChild(renderer.domElement);

// CSS2D renderer (labels)
const labelRenderer = new CSS2DRenderer();
labelRenderer.setSize(innerWidth, innerHeight);
labelRenderer.domElement.style.cssText = 'position:absolute;top:0;pointer-events:none';
document.getElementById('app').appendChild(labelRenderer.domElement);

// Lights
scene.add(new THREE.AmbientLight(0xffffff, 0.5));
const sun = new THREE.DirectionalLight(0xffffff, 1.4);
sun.position.set(8, 14, 8);
scene.add(sun);

// Controls
const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.dampingFactor = 0.06;
controls.target.set(1, 1, 0);

// Index nodes by id
const nodeMap = Object.fromEntries(DATA.nodes.map(n => [n.id, n]));

// Edges
const edgeMat = new THREE.LineBasicMaterial({ color: 0x334466, opacity: 0.75, transparent: true });
DATA.edges.forEach(({ from, to }) => {
  const a = nodeMap[from], b = nodeMap[to];
  if (!a || !b) return;
  const geo = new THREE.BufferGeometry().setFromPoints([
    new THREE.Vector3(a.x, a.y, a.z),
    new THREE.Vector3(b.x, b.y, b.z),
  ]);
  scene.add(new THREE.Line(geo, edgeMat));
});

// Nodes
const sphereGeo = new THREE.SphereGeometry(0.28, 24, 16);
DATA.nodes.forEach(node => {
  const color = new THREE.Color(node.color);
  const mat = new THREE.MeshStandardMaterial({
    color, emissive: color, emissiveIntensity: 0.18,
    roughness: 0.35, metalness: 0.4,
  });
  const mesh = new THREE.Mesh(sphereGeo, mat);
  mesh.position.set(node.x, node.y, node.z);
  scene.add(mesh);

  const div = document.createElement('div');
  div.className = 'label';
  div.textContent = node.name;
  const label = new CSS2DObject(div);
  label.position.set(0, 0.52, 0);
  mesh.add(label);
});

// Resize
window.addEventListener('resize', () => {
  camera.aspect = innerWidth / innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(innerWidth, innerHeight);
  labelRenderer.setSize(innerWidth, innerHeight);
});

// Animate
(function loop() {
  requestAnimationFrame(loop);
  controls.update();
  renderer.render(scene, camera);
  labelRenderer.render(scene, camera);
})();
  </script>
</body>
</html>
"""


# ── Write output ────────────────────────────────────────────────────────────

output = Path("frontend/index.html")
html = HTML.replace("__WORLD_DATA__", json.dumps(world_data))
output.write_text(html, encoding="utf-8")
print(f"Generated: {output.resolve()}")
print("Open in browser: frontend/index.html")
