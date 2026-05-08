# Hero Shaders — drop-in `<script type="module">` blocks

Each block targets `<canvas id="hero-depth-canvas">` inside a `<figure>` with `aspect-[3/4]`. The shell already provides this slot. Replace the contents of `<script id="hero-technique" type="module">…</script>` in `index.html` with the chosen block.

## Compatibility matrix

| Hero | human | product | brand-mark | abstract | scene |
|---|:-:|:-:|:-:|:-:|:-:|
| A · Depth Displacement | ✅ | ✅ | ❌ | ⚠️ | ✅ |
| B · Tilt & Sheen | ✅ | ✅ | ✅ | ✅ | ✅ |
| C · Particle Sample | ❌ | ⚠️ | ⚠️ | ✅ | ⚠️ |
| D · Glass Refraction | ⚠️ | ✅ | ❌ | ✅ | ✅ |
| E · Volumetric Slices | ✅ | ✅ | ❌ | ✅ | ✅ |
| F · Light Caustics | ⚠️ | ✅ | ❌ | ✅ | ✅ |

✅ = good fit · ⚠️ = use with caution · ❌ = avoid (will likely look bad).

**Hard rule:** C on a face is forbidden — eyes void out and dehumanise. C on a logo is fine. C on an abstract image is excellent.

---

## Required assets

All variants assume the project folder contains:
- `hero.jpg` (downscaled subject, ~900px wide)
- `hero_depth.jpg` (depth map from Depth Anything V2; only A, E need this)

The shell preloads both via `<link rel="preload" as="image">`.

---

## Variant A — Depth Displacement (Apple-style)

```html
<script id="hero-technique" type="module">
  import * as THREE from 'three';

  const canvas = document.getElementById('hero-depth-canvas');
  if (canvas) {
    const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true });
    renderer.setPixelRatio(Math.min(2, window.devicePixelRatio));
    const scene = new THREE.Scene();
    const cam = new THREE.PerspectiveCamera(28, 3/4, 0.1, 100);
    cam.position.set(0, 0, 5);

    const PLANE_W = 3, PLANE_H = 4;
    const geom = new THREE.PlaneGeometry(PLANE_W, PLANE_H, 220, 290);

    const loader = new THREE.TextureLoader();
    const texPhoto = loader.load('hero.jpg');
    const texDepth = loader.load('hero_depth.jpg');
    texPhoto.colorSpace = THREE.SRGBColorSpace;
    texPhoto.minFilter = texDepth.minFilter = THREE.LinearFilter;

    const mat = new THREE.ShaderMaterial({
      uniforms: {
        uPhoto: { value: texPhoto },
        uDepth: { value: texDepth },
        uMouse: { value: new THREE.Vector2(0,0) },
        uTime:  { value: 0 },
        uStrength: { value: 0.36 },
        uParallax: { value: 0.16 },
        uVignette: { value: 0.85 }
      },
      vertexShader: `
        uniform sampler2D uDepth;
        uniform float uStrength;
        varying vec2 vUv;
        void main() {
          vUv = uv;
          float d = texture2D(uDepth, uv).r;
          float dn = smoothstep(0.0, 1.0, d);
          vec3 displaced = position + vec3(0.0, 0.0, dn * uStrength);
          gl_Position = projectionMatrix * modelViewMatrix * vec4(displaced, 1.0);
        }
      `,
      fragmentShader: `
        uniform sampler2D uPhoto;
        uniform sampler2D uDepth;
        uniform vec2 uMouse;
        uniform float uParallax;
        uniform float uVignette;
        uniform float uTime;
        varying vec2 vUv;
        void main() {
          float d = texture2D(uDepth, vUv).r;
          vec2 offset = uMouse * uParallax * (d - 0.15);
          vec2 uv = clamp(vUv - offset, vec2(0.001), vec2(0.999));
          vec4 col = texture2D(uPhoto, uv);
          float dist = distance(vUv, vec2(0.5));
          float vig = 1.0 - smoothstep(0.35, 0.85, dist) * (1.0 - uVignette);
          col.rgb *= vig;
          float n = fract(sin(dot(vUv * (1500.0 + sin(uTime*0.3)*40.0), vec2(12.9898, 78.233))) * 43758.5453);
          col.rgb += (n - 0.5) * 0.025;
          gl_FragColor = col;
        }
      `
    });
    const mesh = new THREE.Mesh(geom, mat);
    scene.add(mesh);

    function resize() {
      const r = canvas.getBoundingClientRect();
      const w = Math.max(1, Math.round(r.width)), h = Math.max(1, Math.round(r.height));
      renderer.setSize(w, h, false);
      cam.aspect = w/h; cam.updateProjectionMatrix();
      const fovY = cam.fov * Math.PI / 180;
      const visibleH = 2 * Math.tan(fovY/2) * cam.position.z;
      const scale = Math.max(visibleH / PLANE_H, (visibleH * cam.aspect) / PLANE_W);
      mesh.scale.setScalar(scale * 1.02);
    }
    resize();
    new ResizeObserver(resize).observe(canvas);

    const figure = canvas.closest('figure');
    const mouse = { tx: 0, ty: 0, x: 0, y: 0 };
    function onMove(e) {
      const r = (figure || canvas).getBoundingClientRect();
      const cx = e.touches ? e.touches[0].clientX : e.clientX;
      const cy = e.touches ? e.touches[0].clientY : e.clientY;
      mouse.tx = ((cx - r.left) / r.width  - 0.5) * 2.0;
      mouse.ty = ((cy - r.top)  / r.height - 0.5) * 2.0;
    }
    window.addEventListener('mousemove', onMove);
    window.addEventListener('touchmove', onMove, { passive: true });
    figure?.addEventListener('mouseleave', () => { mouse.tx = 0; mouse.ty = 0; });

    let revealed = false;
    const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    const clock = new THREE.Clock();
    function loop() {
      const t = clock.elapsedTime;
      mat.uniforms.uTime.value = t;
      mouse.x += (mouse.tx - mouse.x) * 0.06;
      mouse.y += (mouse.ty - mouse.y) * 0.06;
      mat.uniforms.uMouse.value.set(mouse.x, -mouse.y);
      if (!reduce) {
        cam.position.x = mouse.x * 0.05;
        cam.position.y = -mouse.y * 0.04 + Math.sin(t*0.4)*0.005;
        cam.lookAt(0,0,0);
      }
      renderer.render(scene, cam);
      if (!revealed && texPhoto.image && texDepth.image) {
        revealed = true;
        canvas.classList.add('in');
      }
      requestAnimationFrame(loop);
    }
    loop();
  }
</script>
```

Tuning knobs are in `depth-portrait-tuning.md`. Default values are battle-tested on the Cleo project.

---

## Variant B — Tilt & Sheen

Plain plane, no depth displacement. Mesh yaws/pitches with cursor like a polaroid. Anisotropic specular sheen sweeps with cursor + autonomous drift.

```html
<script id="hero-technique" type="module">
  import * as THREE from 'three';
  const canvas = document.getElementById('hero-depth-canvas');
  if (canvas) {
    const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true });
    renderer.setPixelRatio(Math.min(2, window.devicePixelRatio));
    const scene = new THREE.Scene();
    const cam = new THREE.PerspectiveCamera(28, 3/4, 0.1, 100);
    cam.position.set(0, 0, 5);

    const PLANE_W = 3, PLANE_H = 4;
    const geom = new THREE.PlaneGeometry(PLANE_W, PLANE_H, 32, 42);
    const tex = new THREE.TextureLoader().load('hero.jpg');
    tex.colorSpace = THREE.SRGBColorSpace;
    tex.anisotropy = 8;

    const mat = new THREE.ShaderMaterial({
      uniforms: {
        uPhoto: { value: tex },
        uTime: { value: 0 },
        uTilt: { value: new THREE.Vector2(0,0) },
        uVignette: { value: 0.85 }
      },
      vertexShader: `varying vec2 vUv; void main(){ vUv = uv; gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0); }`,
      fragmentShader: `
        uniform sampler2D uPhoto; uniform float uTime; uniform vec2 uTilt; uniform float uVignette;
        varying vec2 vUv;
        void main() {
          vec4 col = texture2D(uPhoto, vUv);
          vec2 c = vUv - 0.5;
          float diag = c.x + c.y * 1.3;
          float band = uTilt.x * 0.55 - uTilt.y * 0.35 + sin(uTime * 0.35) * 0.08;
          float sheen = smoothstep(0.18, 0.0, abs(diag - band));
          vec3 sheenCol = vec3(1.0, 0.86, 0.62);
          col.rgb += sheen * 0.18 * sheenCol;
          float diag2 = c.x - c.y * 1.1;
          float sheen2 = smoothstep(0.04, 0.0, abs(diag2 + band * 0.55 - 0.25)) * 0.08;
          col.rgb += sheen2 * sheenCol;
          float dist = distance(vUv, vec2(0.5));
          col.rgb *= 1.0 - smoothstep(0.35, 0.85, dist) * (1.0 - uVignette);
          float n = fract(sin(dot(vUv * 1500.0, vec2(12.9898, 78.233))) * 43758.5453);
          col.rgb += (n - 0.5) * 0.022;
          gl_FragColor = col;
        }
      `
    });
    const mesh = new THREE.Mesh(geom, mat);
    scene.add(mesh);

    function resize() {
      const r = canvas.getBoundingClientRect();
      renderer.setSize(r.width, r.height, false);
      cam.aspect = r.width/r.height; cam.updateProjectionMatrix();
      const visibleH = 2 * Math.tan(cam.fov * Math.PI / 360) * cam.position.z;
      const scale = Math.max(visibleH / PLANE_H, (visibleH * cam.aspect) / PLANE_W);
      mesh.scale.setScalar(scale * 1.06);
    }
    resize();
    new ResizeObserver(resize).observe(canvas);

    const figure = canvas.closest('figure');
    const mouse = { tx:0, ty:0, x:0, y:0 };
    function onMove(e) {
      const r = (figure || canvas).getBoundingClientRect();
      const cx = e.touches ? e.touches[0].clientX : e.clientX;
      const cy = e.touches ? e.touches[0].clientY : e.clientY;
      mouse.tx = ((cx - r.left) / r.width - 0.5) * 2.0;
      mouse.ty = ((cy - r.top)  / r.height - 0.5) * 2.0;
    }
    window.addEventListener('mousemove', onMove);
    figure?.addEventListener('mouseleave', () => { mouse.tx = 0; mouse.ty = 0; });

    const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    const clock = new THREE.Clock();
    let revealed = false;
    function loop() {
      const t = clock.elapsedTime;
      mat.uniforms.uTime.value = t;
      mouse.x += (mouse.tx - mouse.x) * 0.07;
      mouse.y += (mouse.ty - mouse.y) * 0.07;
      mat.uniforms.uTilt.value.set(mouse.x, mouse.y);
      if (!reduce) {
        const MAX = 0.18;
        mesh.rotation.y =  mouse.x * MAX + Math.sin(t * 0.35) * 0.012;
        mesh.rotation.x = -mouse.y * MAX + Math.cos(t * 0.27) * 0.010;
      }
      renderer.render(scene, cam);
      if (!revealed && tex.image) { revealed = true; canvas.classList.add('in'); }
      requestAnimationFrame(loop);
    }
    loop();
  }
</script>
```

---

## Variant C — Particle Sample

⚠️ Do not use on human faces. Eyes void out and dehumanise the subject. Best for abstract subjects, art portfolios, or product silhouettes.

Decode photo to a 2D pixel field, seed N particles each carrying one pixel's RGB. Particles fly in from a noise cloud and assemble into the image. Mouse repels nearby particles within the figure.

The full implementation is ~150 lines — see the working version in the Cleo project (`site-c/index.html`). Key parameters:
- `PARTICLE_COUNT`: 60_000 default; up to 150_000 for higher fidelity at the cost of frame budget
- Importance sampling: `Math.random() > Math.pow(lum + 0.04, 0.7)` rejects dark pixels, keeps silhouette tight
- Repel radius: 0.55 (in plane units), strength 0.18 when cursor is inside the figure

Full block: copy from `site-c/index.html` of the Cleo project until this skill bundles a tested version.

---

## Variant D — Glass Refraction

Photo stays flat; an animated glass slab in front distorts the image via 2D simplex noise + chromatic aberration. Mouse tilts the glass.

```html
<script id="hero-technique" type="module">
  import * as THREE from 'three';
  const canvas = document.getElementById('hero-depth-canvas');
  if (canvas) {
    const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true });
    renderer.setPixelRatio(Math.min(2, window.devicePixelRatio));
    const scene = new THREE.Scene();
    const cam = new THREE.PerspectiveCamera(28, 3/4, 0.1, 100);
    cam.position.set(0, 0, 5);

    const PLANE_W = 3, PLANE_H = 4;
    const geom = new THREE.PlaneGeometry(PLANE_W, PLANE_H, 220, 290);
    const tex = new THREE.TextureLoader().load('hero.jpg');
    tex.colorSpace = THREE.SRGBColorSpace;
    tex.anisotropy = 8;

    const mat = new THREE.ShaderMaterial({
      uniforms: {
        uPhoto: { value: tex },
        uMouse: { value: new THREE.Vector2(0,0) },
        uTime: { value: 0 },
        uVignette: { value: 0.85 },
        uChromatic: { value: 0.005 },   // tuned down from 0.012 — original "fixed" value from Cleo project
        uDistort:   { value: 0.014 }    // tuned down from 0.040 — original "fixed" value
      },
      vertexShader: `varying vec2 vUv; void main(){ vUv = uv; gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0); }`,
      fragmentShader: `
        uniform sampler2D uPhoto;
        uniform vec2 uMouse;
        uniform float uTime, uVignette, uChromatic, uDistort;
        varying vec2 vUv;
        vec2 hash2(vec2 p){ p = vec2(dot(p,vec2(127.1,311.7)), dot(p,vec2(269.5,183.3))); return -1.0 + 2.0 * fract(sin(p) * 43758.5453123); }
        float snoise(vec2 p){
          const float K1 = 0.366025404, K2 = 0.211324865;
          vec2 i = floor(p + (p.x+p.y)*K1);
          vec2 a = p - i + (i.x+i.y)*K2;
          vec2 o = (a.x>a.y) ? vec2(1.0,0.0) : vec2(0.0,1.0);
          vec2 b = a - o + K2; vec2 c = a - 1.0 + 2.0*K2;
          vec3 h = max(0.5 - vec3(dot(a,a), dot(b,b), dot(c,c)), 0.0);
          vec3 n = h*h*h*h * vec3(dot(a, hash2(i)), dot(b, hash2(i+o)), dot(c, hash2(i+1.0)));
          return dot(n, vec3(70.0));
        }
        void main() {
          vec2 p = vUv * 1.6;  // tuned down from 3.5 — finer scale, less "compass needle" wobble
          float n1 = snoise(p + vec2(uTime*0.07, uTime*0.05));
          float n2 = snoise(p * 2.1 - vec2(uTime*0.04, uTime*0.06));
          float field = n1 * 0.6 + n2 * 0.4;
          float eps = 0.005;
          float fx = snoise((vUv + vec2(eps,0.0)) * 1.6 + vec2(uTime*0.07, uTime*0.05))
                   - snoise((vUv - vec2(eps,0.0)) * 1.6 + vec2(uTime*0.07, uTime*0.05));
          float fy = snoise((vUv + vec2(0.0,eps)) * 1.6 + vec2(uTime*0.07, uTime*0.05))
                   - snoise((vUv - vec2(0.0,eps)) * 1.6 + vec2(uTime*0.07, uTime*0.05));
          vec2 normal = vec2(fx, fy) * 60.0;
          vec2 disp = (normal * uDistort) + (uMouse * 0.6 * 0.05);
          vec2 uvR = clamp(vUv - disp * (1.0 + uChromatic), vec2(0.001), vec2(0.999));
          vec2 uvG = clamp(vUv - disp,                       vec2(0.001), vec2(0.999));
          vec2 uvB = clamp(vUv - disp * (1.0 - uChromatic), vec2(0.001), vec2(0.999));
          vec3 col = vec3(texture2D(uPhoto, uvR).r, texture2D(uPhoto, uvG).g, texture2D(uPhoto, uvB).b);
          float spec = smoothstep(0.4, 0.85, abs(field) + 0.08 * sin(uTime * 0.3));
          col += vec3(1.0, 0.92, 0.78) * spec * 0.06;
          float dist = distance(vUv, vec2(0.5));
          col *= 1.0 - smoothstep(0.35, 0.85, dist) * (1.0 - uVignette);
          float gr = fract(sin(dot(vUv * 1500.0, vec2(12.9898, 78.233))) * 43758.5453);
          col += (gr - 0.5) * 0.020;
          gl_FragColor = vec4(col, 1.0);
        }
      `
    });
    const mesh = new THREE.Mesh(geom, mat);
    scene.add(mesh);

    function resize() {
      const r = canvas.getBoundingClientRect();
      renderer.setSize(r.width, r.height, false);
      cam.aspect = r.width/r.height; cam.updateProjectionMatrix();
      const visibleH = 2 * Math.tan(cam.fov * Math.PI / 360) * cam.position.z;
      const scale = Math.max(visibleH / PLANE_H, (visibleH * cam.aspect) / PLANE_W);
      mesh.scale.setScalar(scale * 1.02);
    }
    resize();
    new ResizeObserver(resize).observe(canvas);

    const figure = canvas.closest('figure');
    const mouse = { tx:0, ty:0, x:0, y:0 };
    function onMove(e) {
      const r = (figure || canvas).getBoundingClientRect();
      const cx = e.touches ? e.touches[0].clientX : e.clientX;
      const cy = e.touches ? e.touches[0].clientY : e.clientY;
      mouse.tx = ((cx - r.left) / r.width - 0.5) * 2.0;
      mouse.ty = ((cy - r.top)  / r.height - 0.5) * 2.0;
    }
    window.addEventListener('mousemove', onMove);
    figure?.addEventListener('mouseleave', () => { mouse.tx = 0; mouse.ty = 0; });

    const clock = new THREE.Clock();
    let revealed = false;
    function loop() {
      mat.uniforms.uTime.value = clock.elapsedTime;
      mouse.x += (mouse.tx - mouse.x) * 0.06;
      mouse.y += (mouse.ty - mouse.y) * 0.06;
      mat.uniforms.uMouse.value.set(mouse.x, -mouse.y);
      renderer.render(scene, cam);
      if (!revealed && tex.image) { revealed = true; canvas.classList.add('in'); }
      requestAnimationFrame(loop);
    }
    loop();
  }
</script>
```

---

## Variant E — Volumetric Slices

NOT YET BUNDLED. Splits the photo into N=4–6 parallax slabs based on depth quantiles, renders each as a translucent plane at a different Z. Lighter than depth-displacement (geometry is just a few quads), good for mobile.

Approach: uniform `uSliceN` (default 5), generate N planes, each textured with `texPhoto` masked to its depth band via the `texDepth` map. Mouse parallaxes the camera; slabs read as foreground/middle/background.

When implementing: use `transparent: true`, `depthWrite: false`, `blending: THREE.NormalBlending`. Watch for transparency sorting — render front-to-back, force `mesh.renderOrder` per slab.

---

## Variant F — Light Caustics

NOT YET BUNDLED. Photo stays flat; an animated caustic light pattern (like sunlight through water or the rim of a glass) sweeps over it. Two layers of distorted Voronoi noise scrolled in opposite directions; multiplied into a warm tint, additive over the photo.

Use sparingly — caustics on a face turn it into a "bathroom photo." Pairs well with beauty/perfume/beverage products.
