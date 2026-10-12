/* ═══════════════════════════════════════════════════════════════════════════
   Aara — ProjectsHub's 3D AI guide (hero section)
   A jointed humanoid android built procedurally with three.js:
     · pearl ceramic shell panels over graphite mechanics, glossy face visor
     · LED eyes that wake on hover, blink, follow the cursor, and a "voice" bar
       that animates while she explains a lesson
     · articulated shoulders / elbows / wrists / fingers / hips / knees, so
       gestures read like a real robot rather than a toy
     · image-based reflections (generated studio environment), soft shadows
   Renders only while visible; honours prefers-reduced-motion.
   Public API:  window.phAara.mount(canvas, { onInteract(part) }) -> { speak(), gesture(part) }
   ═══════════════════════════════════════════════════════════════════════════ */
(function () {
  'use strict';

  var THREE_URL = 'https://cdn.jsdelivr.net/npm/three@0.170.0/build/three.module.js';

  function mount(canvas, opts) {
    opts = opts || {};
    var api = { speak: function () {}, gesture: function () {}, ready: false };
    if (!canvas || canvas.dataset.robotReady === 'true' || canvas.dataset.robotReady === 'loading') return api;
    canvas.dataset.robotReady = 'loading';

    import(THREE_URL).then(function (THREE) {
      build(THREE, canvas, opts, api);
    }).catch(function (err) {
      canvas.dataset.robotReady = 'error';
      console.error('Unable to load the 3D robot engine.', err);
      if (opts.onError) opts.onError('The 3D preview couldn\'t load. Please refresh the page.');
    });
    return api;
  }

  function build(THREE, canvas, opts, api) {
    var renderer;
    try {
      renderer = new THREE.WebGLRenderer({ canvas: canvas, alpha: true, antialias: true, powerPreference: 'high-performance' });
    } catch (err) {
      canvas.dataset.robotReady = 'error';
      console.error('Unable to initialize the 3D robot WebGL renderer.', err);
      if (opts.onError) opts.onError('This browser couldn\'t start the 3D preview.');
      return;
    }
    var reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
    renderer.setClearColor(0x000000, 0);
    renderer.outputColorSpace = THREE.SRGBColorSpace;
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1.05;
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;

    var scene = new THREE.Scene();
    var camera = new THREE.PerspectiveCamera(30, 1, 0.1, 60);
    var LOOK_AT = new THREE.Vector3(0, 1.74, 0);

    // ── Studio environment for realistic reflections (no external files) ─────
    (function makeEnvironment() {
      var env = new THREE.Scene();
      var room = new THREE.Mesh(
        new THREE.BoxGeometry(10, 8, 10),
        new THREE.MeshBasicMaterial({ color: 0x8f9bb3, side: THREE.BackSide })
      );
      env.add(room);
      function panel(w, h, color, intensity, pos, rot) {
        var m = new THREE.Mesh(new THREE.PlaneGeometry(w, h), new THREE.MeshBasicMaterial({ color: color }));
        m.material.color.multiplyScalar(intensity);
        m.position.set(pos[0], pos[1], pos[2]);
        if (rot) m.rotation.set(rot[0], rot[1], rot[2]);
        env.add(m);
      }
      panel(6, 2.2, 0xffffff, 3.2, [0, 3.9, 0], [Math.PI / 2, 0, 0]);        // big softbox overhead
      panel(2.4, 4, 0xffffff, 2.4, [-4.9, 1.2, 1.5], [0, Math.PI / 2, 0]);  // key strip left
      panel(1.4, 4, 0xc7d2fe, 1.6, [4.9, 1.0, -1], [0, -Math.PI / 2, 0]);   // indigo kicker right
      panel(3, 1.2, 0xa5f3fc, 1.2, [0, 0.6, -4.9], [0, 0, 0]);              // cyan back glow
      panel(5, 2, 0xf1f5f9, 1.4, [0, 1.4, 4.9], [0, Math.PI, 0]);           // front fill
      var pmrem = new THREE.PMREMGenerator(renderer);
      scene.environment = pmrem.fromScene(env, 0.035).texture;
      pmrem.dispose();
    })();

    // ── Lights ───────────────────────────────────────────────────────────────
    scene.add(new THREE.HemisphereLight(0xf8fbff, 0x5b6478, 0.55));
    var key = new THREE.DirectionalLight(0xffffff, 2.2);
    key.position.set(-1.6, 7.5, 3.6);
    key.castShadow = true;
    key.shadow.mapSize.set(1024, 1024);
    key.shadow.camera.left = -1.6; key.shadow.camera.right = 1.6;
    key.shadow.camera.top = 3.8; key.shadow.camera.bottom = -0.4;
    key.shadow.camera.near = 1; key.shadow.camera.far = 14;
    key.shadow.bias = -0.0004;
    key.shadow.normalBias = 0.02;
    key.shadow.radius = 5;
    scene.add(key);
    var rim = new THREE.DirectionalLight(0x67e8f9, 1.6);
    rim.position.set(3.2, 3.2, -3.5);
    scene.add(rim);
    var kicker = new THREE.DirectionalLight(0xa5b4fc, 0.9);
    kicker.position.set(-3.5, 1.5, -2.5);
    scene.add(kicker);

    // ── Materials ────────────────────────────────────────────────────────────
    var shell = new THREE.MeshPhysicalMaterial({
      color: 0xf4f6fa, roughness: 0.32, metalness: 0.0, clearcoat: 1, clearcoatRoughness: 0.14,
      sheen: 0.2, sheenColor: new THREE.Color(0xdbeafe), envMapIntensity: 1.1,
    });
    var shellShade = shell.clone();
    shellShade.color.set(0xe3e8f0);
    var graphite = new THREE.MeshPhysicalMaterial({
      color: 0x1d2333, roughness: 0.38, metalness: 0.75, clearcoat: 0.4, clearcoatRoughness: 0.3, envMapIntensity: 1.2,
    });
    var joint = new THREE.MeshPhysicalMaterial({
      color: 0x30384d, roughness: 0.24, metalness: 0.95, envMapIntensity: 1.4,
    });
    var rubber = new THREE.MeshStandardMaterial({ color: 0x141824, roughness: 0.85, metalness: 0.05 });
    var visorMat = new THREE.MeshPhysicalMaterial({
      color: 0x05070d, roughness: 0.06, metalness: 0.35, clearcoat: 1, clearcoatRoughness: 0.03,
      reflectivity: 0.9, envMapIntensity: 1.8,
    });
    var ledCyan = new THREE.MeshBasicMaterial({ color: 0x7deeff, toneMapped: false, transparent: true });
    var ledIndigo = new THREE.MeshBasicMaterial({ color: 0x8b8ff8, toneMapped: false, transparent: true });
    var accent = new THREE.MeshStandardMaterial({
      color: 0x22d3ee, emissive: 0x22d3ee, emissiveIntensity: 1.4, roughness: 0.3, toneMapped: false,
    });
    var accentIndigo = new THREE.MeshStandardMaterial({
      color: 0x6366f1, emissive: 0x6366f1, emissiveIntensity: 1.2, roughness: 0.3, toneMapped: false,
    });

    // ── Geometry helpers ─────────────────────────────────────────────────────
    function shadowed(mesh) { mesh.castShadow = true; mesh.receiveShadow = true; return mesh; }

    function plate(topW, bottomW, h, depth, bevel, material, segs) {
      // A trapezoid armour plate with generous rounded edges (front view = XY).
      var r = Math.min(bevel, h / 3);
      var s = new THREE.Shape();
      var tw = topW / 2, bw = bottomW / 2, hh = h / 2;
      s.moveTo(-bw + r, -hh);
      s.lineTo(bw - r, -hh);
      s.quadraticCurveTo(bw, -hh, bw + (tw - bw) * (r / h), -hh + r);
      s.lineTo(tw - (tw - bw) * (r / h), hh - r);
      s.quadraticCurveTo(tw, hh, tw - r, hh);
      s.lineTo(-tw + r, hh);
      s.quadraticCurveTo(-tw, hh, -tw + (tw - bw) * (r / h), hh - r);
      s.lineTo(-bw - (tw - bw) * (r / h) + 0 * r, -hh + r);
      s.quadraticCurveTo(-bw, -hh, -bw + r, -hh);
      var g = new THREE.ExtrudeGeometry(s, {
        depth: Math.max(0.001, depth - bevel * 2), bevelEnabled: true, bevelThickness: bevel, bevelSize: bevel * 0.9,
        bevelSegments: segs || 6, curveSegments: 10,
      });
      g.translate(0, 0, -(depth - bevel * 2) / 2);
      g.computeVertexNormals();
      return shadowed(new THREE.Mesh(g, material));
    }
    function capsule(radius, length, material, radial) {
      return shadowed(new THREE.Mesh(new THREE.CapsuleGeometry(radius, length, 6, radial || 20), material));
    }
    function taperedLimb(rTop, rBottom, length, material) {
      // Smooth tapered limb: lathe profile with rounded ends.
      var pts = [];
      var steps = 14;
      for (var i = 0; i <= steps; i++) {
        var t = i / steps;
        var y = -length / 2 + t * length;
        var r = rBottom + (rTop - rBottom) * t;
        var bulge = Math.sin(Math.PI * Math.min(1, t * 1.15)) * 0.012;
        pts.push(new THREE.Vector2(r + bulge, y));
      }
      // rounded caps
      var caps = [];
      for (var j = 0; j <= 6; j++) {
        var a = (j / 6) * (Math.PI / 2);
        caps.push(new THREE.Vector2(Math.cos(a) * rBottom, -length / 2 - Math.sin(a) * rBottom * 0.55));
      }
      caps.reverse();
      var top = [];
      for (var k = 0; k <= 6; k++) {
        var b = (k / 6) * (Math.PI / 2);
        top.push(new THREE.Vector2(Math.cos(b) * rTop, length / 2 + Math.sin(b) * rTop * 0.55));
      }
      var profile = caps.concat(pts.slice(1, -1)).concat(top);
      return shadowed(new THREE.Mesh(new THREE.LatheGeometry(profile, 28), material));
    }
    function sphere(r, material, seg) { return shadowed(new THREE.Mesh(new THREE.SphereGeometry(r, seg || 24, Math.round((seg || 24) * 0.7)), material)); }
    function cyl(rt, rb, h, material, seg) { return shadowed(new THREE.Mesh(new THREE.CylinderGeometry(rt, rb, h, seg || 24), material)); }
    function torus(r, tube, material) { return new THREE.Mesh(new THREE.TorusGeometry(r, tube, 10, 48), material); }
    function at(obj, x, y, z) { obj.position.set(x, y, z); return obj; }
    function radialTexture(stops) {
      var c = document.createElement('canvas'); c.width = c.height = 128;
      var g = c.getContext('2d');
      var grad = g.createRadialGradient(64, 64, 0, 64, 64, 64);
      stops.forEach(function (s) { grad.addColorStop(s[0], s[1]); });
      g.fillStyle = grad; g.fillRect(0, 0, 128, 128);
      var t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace;
      return t;
    }

    // ── Rig ──────────────────────────────────────────────────────────────────
    var robot = new THREE.Group();
    scene.add(robot);

    // Pelvis
    var hips = new THREE.Group();
    hips.position.y = 1.68;
    robot.add(hips);
    var pelvis = plate(0.52, 0.38, 0.24, 0.34, 0.07, shell);
    pelvis.position.y = 0.02;
    hips.add(pelvis);
    hips.add(at(plate(0.13, 0.08, 0.08, 0.04, 0.015, graphite), 0, -0.04, 0.165));   // groin cover
    var belt = plate(0.5, 0.48, 0.07, 0.33, 0.03, graphite);
    belt.position.y = 0.16;
    hips.add(belt);
    hips.add(at(new THREE.Mesh(new THREE.BoxGeometry(0.2, 0.012, 0.004), accent), 0, 0.16, 0.168));

    // Spine / waist (exposed mechanics)
    var waist = new THREE.Group();
    waist.position.y = 0.2;
    waist.userData.robotPart = 'chest';
    hips.add(waist);
    waist.add(at(cyl(0.12, 0.14, 0.2, joint), 0, 0.08, 0));
    for (var ri = 0; ri < 3; ri++) {
      var rib = torus(0.135 - ri * 0.004, 0.016, graphite);
      rib.rotation.x = Math.PI / 2;
      rib.position.y = 0.03 + ri * 0.055;
      waist.add(rib);
    }
    var abA = plate(0.3, 0.26, 0.09, 0.07, 0.025, shellShade);
    waist.add(at(abA, 0, 0.05, 0.12));
    var abB = plate(0.33, 0.3, 0.09, 0.07, 0.025, shellShade);
    waist.add(at(abB, 0, 0.15, 0.125));

    // Chest
    var chest = new THREE.Group();
    chest.position.y = 0.2;
    chest.userData.robotPart = 'chest';
    waist.add(chest);
    // Sculpted V-shaped torso: an oval lathe (wide chest, narrow waist)
    var torsoProfile = [
      [0.0, 0.0], [0.2, 0.0], [0.235, 0.05], [0.29, 0.16], [0.37, 0.3], [0.425, 0.42],
      [0.44, 0.51], [0.425, 0.58], [0.37, 0.645], [0.26, 0.685], [0.12, 0.7], [0.0, 0.705],
    ].map(function (p) { return new THREE.Vector2(p[0], p[1]); });
    var TORSO_DEPTH = 0.6;
    var chestShell = shadowed(new THREE.Mesh(new THREE.LatheGeometry(torsoProfile, 56), shell));
    chestShell.scale.set(1, 1, TORSO_DEPTH);
    chest.add(chestShell);
    // Front pectoral armour panel, following the torso curve
    var pecProfile = [[0.36, 0.33], [0.41, 0.4], [0.438, 0.47], [0.445, 0.52], [0.43, 0.58], [0.38, 0.635], [0.3, 0.665]]
      .map(function (p) { return new THREE.Vector2(p[0] + 0.012, p[1]); });
    var pecs = shadowed(new THREE.Mesh(new THREE.LatheGeometry(pecProfile, 40, -0.95, 1.9), shellShade));
    pecs.material = shellShade.clone();
    pecs.material.side = THREE.DoubleSide;
    pecs.scale.set(1, 1, TORSO_DEPTH);
    chest.add(pecs);
    // Core "heart" light
    var core = new THREE.Group();
    core.position.set(0, 0.235, 0.198);
    chest.add(core);
    core.add(cyl(0.075, 0.075, 0.03, graphite, 32)).rotation.x = Math.PI / 2;
    var coreRing = torus(0.062, 0.009, accent);
    coreRing.position.z = 0.018;
    core.add(coreRing);
    var coreDot = new THREE.Mesh(new THREE.CircleGeometry(0.038, 32), ledCyan.clone());
    coreDot.position.z = 0.02;
    core.add(coreDot);
    var coreGlow = new THREE.Sprite(new THREE.SpriteMaterial({
      map: radialTexture([[0, 'rgba(103,232,249,0.85)'], [0.35, 'rgba(34,211,238,0.25)'], [1, 'rgba(34,211,238,0)']]),
      transparent: true, depthWrite: false, blending: THREE.AdditiveBlending,
    }));
    coreGlow.scale.set(0.34, 0.34, 1);
    coreGlow.position.z = 0.03;
    core.add(coreGlow);
    // Back battery module
    var pack = plate(0.46, 0.4, 0.42, 0.12, 0.04, graphite);
    pack.position.set(0, 0.34, -0.25);
    chest.add(pack);
    for (var vi = 0; vi < 3; vi++) {
      chest.add(at(new THREE.Mesh(new THREE.BoxGeometry(0.26, 0.012, 0.006), accentIndigo), 0, 0.27 + vi * 0.07, -0.312));
    }
    // Collar
    chest.add(at(cyl(0.16, 0.2, 0.06, graphite), 0, 0.66, 0));

    // Neck + head
    var neck = new THREE.Group();
    neck.position.y = 0.68;
    chest.add(neck);
    neck.add(at(cyl(0.062, 0.075, 0.18, joint), 0, 0.08, 0));
    for (var ni = 0; ni < 2; ni++) {
      var nr = torus(0.07, 0.012, graphite);
      nr.rotation.x = Math.PI / 2; nr.position.y = 0.05 + ni * 0.06;
      neck.add(nr);
    }
    var head = new THREE.Group();
    head.position.y = 0.2;
    head.scale.setScalar(1.12);
    head.userData.robotPart = 'head';
    neck.add(head);
    var skull = sphere(0.27, shell, 48);
    skull.scale.set(0.9, 1.04, 0.98);
    skull.position.y = 0.2;
    head.add(skull);
    var jaw = sphere(0.2, shellShade, 36);
    jaw.scale.set(1.0, 0.62, 1.06);
    jaw.position.set(0, 0.06, 0.01);
    head.add(jaw);
    // Face visor (partial sphere shell on the front of the head)
    var visorGeo = new THREE.SphereGeometry(0.272, 48, 32, Math.PI / 2 - 1.05, 2.1, 1.02, 0.98);
    var visor = new THREE.Mesh(visorGeo, visorMat);
    visor.scale.set(0.905, 1.045, 0.99);
    visor.position.y = 0.2;
    visor.scale.multiplyScalar(1.012);
    head.add(visor);
    // Ear pods
    [-1, 1].forEach(function (s) {
      var pod = cyl(0.07, 0.078, 0.07, graphite, 32);
      pod.rotation.z = Math.PI / 2;
      pod.position.set(s * 0.245, 0.19, -0.01);
      head.add(pod);
      var ring = torus(0.052, 0.009, accentIndigo);
      ring.rotation.y = Math.PI / 2;
      ring.position.set(s * 0.282, 0.19, -0.01);
      head.add(ring);
    });
    // Crown sensor strip
    var crown = new THREE.Mesh(new THREE.TorusGeometry(0.2, 0.008, 8, 48, Math.PI * 0.7), accent);
    crown.rotation.set(0, Math.PI / 2, Math.PI / 2 + Math.PI * 0.35);
    crown.position.set(0, 0.24, -0.02);
    crown.scale.set(1, 1.12, 1);
    head.add(crown);

    // LED eyes on the visor
    var face = new THREE.Group();
    face.position.y = 0.2;
    head.add(face);
    var eyes = [];
    var eyeGlowTex = radialTexture([[0, 'rgba(165,243,252,0.9)'], [0.4, 'rgba(34,211,238,0.28)'], [1, 'rgba(34,211,238,0)']]);
    [-1, 1].forEach(function (s) {
      var pivot = new THREE.Group();
      pivot.rotation.y = s * 0.36;
      pivot.rotation.x = -0.08;
      face.add(pivot);
      var eye = new THREE.Group();
      eye.position.z = 0.279;
      pivot.add(eye);
      var led = new THREE.Mesh(new THREE.CapsuleGeometry(0.022, 0.04, 4, 12), ledCyan);
      led.rotation.z = Math.PI / 2;
      eye.add(led);
      var glow = new THREE.Sprite(new THREE.SpriteMaterial({ map: eyeGlowTex, transparent: true, depthWrite: false, blending: THREE.AdditiveBlending }));
      glow.scale.set(0.13, 0.085, 1);
      glow.position.z = 0.01;
      eye.add(glow);
      eyes.push({ pivot: pivot, eye: eye, led: led, glow: glow, side: s, baseYaw: s * 0.36 });
    });
    // Voice bar (animates while Aara explains)
    var voice = [];
    var voicePivot = new THREE.Group();
    voicePivot.rotation.x = 0.3;
    face.add(voicePivot);
    for (var vb = 0; vb < 7; vb++) {
      var bar = new THREE.Mesh(new THREE.BoxGeometry(0.011, 0.04, 0.004), ledIndigo.clone());
      var ang = (vb - 3) * 0.075;
      var holder = new THREE.Group();
      holder.rotation.y = ang;
      voicePivot.add(holder);
      bar.position.z = 0.277;
      holder.add(bar);
      voice.push(bar);
    }

    // Arms
    function makeArm(side) {
      var shoulder = new THREE.Group();
      shoulder.position.set(side * 0.47, 0.57, -0.01);
      shoulder.userData.robotPart = side > 0 ? 'left-arm' : 'right-arm';
      chest.add(shoulder);
      shoulder.add(sphere(0.105, joint, 28));
      var cap = new THREE.Mesh(new THREE.SphereGeometry(0.165, 32, 20, 0, Math.PI * 2, 0, Math.PI * 0.55), shell);
      shadowed(cap);
      cap.scale.set(1.0, 0.95, 1.08);
      cap.position.set(side * 0.03, 0.02, 0);
      cap.rotation.z = -side * 0.35;
      shoulder.add(cap);
      var capStripe = torus(0.12, 0.007, accentIndigo);
      capStripe.rotation.x = Math.PI / 2;
      capStripe.rotation.y = -side * 0.35;
      capStripe.position.set(side * 0.06, -0.025, 0);
      shoulder.add(capStripe);

      var upper = new THREE.Group();
      shoulder.add(upper);
      upper.add(at(taperedLimb(0.092, 0.08, 0.3, shell), 0, -0.25, 0));
      upper.add(at(cyl(0.07, 0.07, 0.07, graphite), 0, -0.45, 0));

      var elbow = new THREE.Group();
      elbow.position.y = -0.5;
      upper.add(elbow);
      var eJoint = sphere(0.074, joint, 24);
      elbow.add(eJoint);
      var axle = cyl(0.04, 0.04, 0.17, graphite, 16);
      axle.rotation.z = Math.PI / 2;
      elbow.add(axle);
      elbow.add(at(taperedLimb(0.08, 0.06, 0.28, shell), 0, -0.22, 0));
      var inner = taperedLimb(0.05, 0.04, 0.22, graphite);
      inner.position.set(0, -0.21, -0.045);
      elbow.add(inner);
      elbow.add(at(new THREE.Mesh(new THREE.BoxGeometry(0.008, 0.12, 0.004), accent), side * 0.0, -0.2, 0.079));

      var wrist = new THREE.Group();
      wrist.position.y = -0.43;
      elbow.add(wrist);
      wrist.add(sphere(0.05, joint, 20));
      var hand = new THREE.Group();
      hand.position.y = -0.05;
      wrist.add(hand);
      var palm = plate(0.12, 0.11, 0.13, 0.06, 0.022, graphite, 4);
      palm.position.y = -0.06;
      hand.add(palm);
      var back = plate(0.11, 0.1, 0.1, 0.02, 0.008, shell, 3);
      back.position.set(0, -0.055, -0.035);
      hand.add(back);
      var fingers = [];
      for (var f = 0; f < 4; f++) {
        var fx = -0.042 + f * 0.028;
        var knuckle = new THREE.Group();
        knuckle.position.set(fx, -0.13, 0.004);
        hand.add(knuckle);
        var len1 = f === 1 || f === 2 ? 0.05 : 0.042;
        knuckle.add(at(capsule(0.012, len1, rubber, 10), 0, -len1 / 2 - 0.006, 0));
        var mid = new THREE.Group();
        mid.position.y = -len1 - 0.016;
        knuckle.add(mid);
        mid.add(at(capsule(0.011, len1 * 0.8, shellShade, 10), 0, -len1 * 0.4 - 0.004, 0));
        fingers.push({ k: knuckle, m: mid });
      }
      var thumb = new THREE.Group();
      thumb.position.set(-side * 0.058, -0.07, 0.02);
      thumb.rotation.z = side * 0.7;
      hand.add(thumb);
      thumb.add(at(capsule(0.013, 0.045, rubber, 10), 0, -0.03, 0));

      return { shoulder: shoulder, upper: upper, elbow: elbow, wrist: wrist, hand: hand, fingers: fingers, thumb: thumb, side: side };
    }
    var armL = makeArm(1);   // Aara's left (viewer's right)
    var armR = makeArm(-1);  // Aara's right (viewer's left)

    // Legs
    function makeLeg(side) {
      var hip = new THREE.Group();
      hip.position.set(side * 0.15, -0.08, 0);
      hip.userData.robotPart = side > 0 ? 'left-leg' : 'right-leg';
      hips.add(hip);
      hip.add(sphere(0.1, joint, 24));
      hip.add(at(taperedLimb(0.12, 0.095, 0.44, shell), 0, -0.33, 0));
      var thighPanel = taperedLimb(0.07, 0.06, 0.3, graphite);
      thighPanel.position.set(side * 0.06, -0.33, -0.02);
      hip.add(thighPanel);
      var knee = new THREE.Group();
      knee.position.y = -0.66;
      hip.add(knee);
      knee.add(sphere(0.085, joint, 24));
      var kneeCap = new THREE.Mesh(new THREE.SphereGeometry(0.09, 24, 16, 0, Math.PI * 2, 0, Math.PI * 0.5), shellShade);
      shadowed(kneeCap);
      kneeCap.rotation.x = Math.PI / 2;
      kneeCap.position.z = 0.04;
      kneeCap.scale.set(1, 1, 0.6);
      knee.add(kneeCap);
      knee.add(at(taperedLimb(0.095, 0.07, 0.48, shell), 0, -0.34, 0));
      var calf = taperedLimb(0.06, 0.045, 0.3, graphite);
      calf.position.set(0, -0.3, -0.05);
      knee.add(calf);
      knee.add(at(new THREE.Mesh(new THREE.BoxGeometry(0.008, 0.18, 0.004), accent), 0, -0.3, 0.092));
      var ankle = new THREE.Group();
      ankle.position.y = -0.7;
      knee.add(ankle);
      ankle.add(sphere(0.055, joint, 20));
      var foot = plate(0.2, 0.22, 0.4, 0.1, 0.04, shell, 4);
      foot.rotation.x = -Math.PI / 2;
      foot.position.set(0, -0.08, 0.07);
      ankle.add(foot);
      var sole = plate(0.21, 0.23, 0.41, 0.035, 0.012, rubber, 3);
      sole.rotation.x = -Math.PI / 2;
      sole.position.set(0, -0.135, 0.07);
      ankle.add(sole);
      return { hip: hip, knee: knee, ankle: ankle, side: side };
    }
    var legL = makeLeg(1);
    var legR = makeLeg(-1);

    // Ground: shadow catcher + contact shadow + brand ring
    var ground = new THREE.Mesh(new THREE.CircleGeometry(1.25, 48), new THREE.ShadowMaterial({ opacity: 0.14 }));
    ground.rotation.x = -Math.PI / 2;
    ground.receiveShadow = true;
    scene.add(ground);
    var contact = new THREE.Mesh(new THREE.PlaneGeometry(1.5, 1.5), new THREE.MeshBasicMaterial({
      map: radialTexture([[0, 'rgba(15,23,42,0.42)'], [0.45, 'rgba(15,23,42,0.12)'], [1, 'rgba(15,23,42,0)']]),
      transparent: true, depthWrite: false,
    }));
    contact.rotation.x = -Math.PI / 2;
    contact.position.y = 0.002;
    contact.scale.set(1, 0.7, 1);
    scene.add(contact);
    var ring = new THREE.Mesh(new THREE.RingGeometry(0.98, 1.0, 96), new THREE.MeshBasicMaterial({
      color: 0x22d3ee, transparent: true, opacity: 0.45, side: THREE.DoubleSide, toneMapped: false,
    }));
    ring.rotation.x = -Math.PI / 2;
    ring.position.y = 0.004;
    scene.add(ring);
    var ringDash = new THREE.Mesh(new THREE.RingGeometry(1.08, 1.095, 96, 1, 0, Math.PI * 0.6), new THREE.MeshBasicMaterial({
      color: 0x6366f1, transparent: true, opacity: 0.5, side: THREE.DoubleSide, toneMapped: false,
    }));
    ringDash.rotation.x = -Math.PI / 2;
    ringDash.position.y = 0.005;
    scene.add(ringDash);
    var pad = new THREE.Mesh(new THREE.CircleGeometry(0.98, 64), new THREE.MeshBasicMaterial({
      map: radialTexture([[0, 'rgba(99,102,241,0.14)'], [0.7, 'rgba(34,211,238,0.06)'], [1, 'rgba(34,211,238,0)']]),
      transparent: true, depthWrite: false,
    }));
    pad.rotation.x = -Math.PI / 2;
    pad.position.y = 0.003;
    scene.add(pad);

    // ── Resting pose ─────────────────────────────────────────────────────────
    var REST = {
      armZ: 0.16, armX: 0.06, elbowX: -0.32, wristX: -0.1, fingerCurl: 0.32,
    };

    // ── Interaction state ────────────────────────────────────────────────────
    var pointer = { x: 0, y: 0 }, focus = { x: 0, y: 0 };
    var hovered = false, awake = 0;
    var gesture = null;
    var speakUntil = 0;
    var nextBlink = performance.now() + 2500, blinkStart = 0;
    var raycaster = new THREE.Raycaster();
    var ndc = new THREE.Vector2();

    function resize() {
      var rect = canvas.getBoundingClientRect();
      if (!rect.width || !rect.height) return;
      renderer.setSize(rect.width, rect.height, false);
      camera.aspect = rect.width / rect.height;
      // Fit the full figure (feet to head, arms out) with breathing room.
      var needH = 4.35, needW = 2.5;
      var vfov = THREE.MathUtils.degToRad(camera.fov);
      var distH = (needH / 2) / Math.tan(vfov / 2);
      var distW = (needW / 2) / (Math.tan(vfov / 2) * camera.aspect);
      var dist = Math.max(distH, distW);
      camera.position.set(0, LOOK_AT.y + 0.18, dist);
      camera.lookAt(LOOK_AT);
      camera.updateProjectionMatrix();
      if (reducedMotion) render(0);
    }

    function partAt(evt) {
      if (!evt || typeof evt.clientX !== 'number') return null;
      var rect = canvas.getBoundingClientRect();
      ndc.x = ((evt.clientX - rect.left) / rect.width) * 2 - 1;
      ndc.y = -((evt.clientY - rect.top) / rect.height) * 2 + 1;
      raycaster.setFromCamera(ndc, camera);
      var hits = raycaster.intersectObject(robot, true);
      for (var i = 0; i < hits.length; i++) {
        var o = hits[i].object;
        while (o && o !== robot) {
          if (o.userData.robotPart) return o.userData.robotPart;
          o = o.parent;
        }
      }
      return null;
    }

    function startGesture(part, duration) {
      if (reducedMotion) return;
      var durations = { 'left-arm': 2200, 'right-arm': 2200, head: 1700, chest: 1600, 'left-leg': 1600, 'right-leg': 1600 };
      gesture = { part: part, start: performance.now(), dur: duration || durations[part] || 2000 };
    }
    api.gesture = startGesture;
    api.speak = function (ms) { speakUntil = performance.now() + (ms || 1600); };

    canvas.addEventListener('pointermove', function (e) {
      var r = canvas.getBoundingClientRect();
      pointer.x = THREE.MathUtils.clamp(((e.clientX - r.left) / r.width - 0.5) * 2, -1, 1);
      pointer.y = THREE.MathUtils.clamp(((e.clientY - r.top) / r.height - 0.5) * 2, -1, 1);
      canvas.style.cursor = partAt(e) ? 'pointer' : 'default';
      if (reducedMotion) render(0);
    });
    canvas.addEventListener('pointerenter', function () { hovered = true; if (reducedMotion) render(0); });
    canvas.addEventListener('pointerleave', function () { hovered = false; pointer.x = pointer.y = 0; if (reducedMotion) render(0); });
    canvas.addEventListener('focus', function () { hovered = true; if (reducedMotion) render(0); });
    canvas.addEventListener('blur', function () { hovered = false; if (reducedMotion) render(0); });
    function interact(evt) {
      var part = partAt(evt);
      var fallback = !part;
      part = part || 'left-arm';
      hovered = true;
      if (opts.onInteract) opts.onInteract(part, fallback);
      startGesture(part);
      api.speak(1800);
    }
    canvas.addEventListener('click', interact);
    canvas.addEventListener('keydown', function (e) {
      if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); interact(null); }
    });

    // ── Animation ────────────────────────────────────────────────────────────
    function ease(t) { return t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2; }
    function envelope(p) {
      // smooth in (0→0.25), hold, smooth out (0.75→1)
      if (p < 0.25) return ease(p / 0.25);
      if (p > 0.75) return ease((1 - p) / 0.25);
      return 1;
    }
    function lerp(a, b, t) { return a + (b - a) * t; }

    function poseArm(arm, t, g, gp, ge) {
      var s = arm.side;
      var breathe = Math.sin(t * 1.3 + (s > 0 ? 0 : 1.2)) * 0.02;
      var z = REST.armZ + breathe, x = REST.armX, ex = REST.elbowX, ez = 0, wx = REST.wristX, wz = 0, curl = REST.fingerCurl;
      var mine = g === (s > 0 ? 'left-arm' : 'right-arm');
      if (mine && ge > 0) {
        // Raise the arm to the side, bend the elbow up and wave from the elbow.
        z = lerp(z, 1.28, ge);
        x = lerp(x, -0.32, ge);
        ex = lerp(ex, -0.18, ge);
        ez = lerp(0, 1.55, ge) + Math.sin(gp * Math.PI * 7) * 0.38 * ge;
        wz = Math.sin(gp * Math.PI * 7 + 0.6) * 0.22 * ge;
        curl = lerp(curl, 0.05, ge);
      } else if (g && (g.indexOf('leg') > -1) && ge > 0) {
        z += 0.25 * ge; // balance
      } else if (g === 'chest' && ge > 0) {
        x = lerp(x, -0.25, ge); ex = lerp(ex, -0.9, ge); curl = lerp(curl, 0.6, ge);
      }
      arm.shoulder.rotation.z = s * z;
      arm.shoulder.rotation.x = x;
      arm.elbow.rotation.x = ex;
      arm.elbow.rotation.z = s * ez;
      arm.wrist.rotation.x = wx;
      arm.wrist.rotation.z = s * wz;
      arm.fingers.forEach(function (f, i) {
        var c = curl + i * 0.04;
        f.k.rotation.x = -c;
        f.m.rotation.x = -c * 1.3;
      });
    }

    function poseLeg(leg, t, g, ge, other) {
      var mine = g === (leg.side > 0 ? 'left-leg' : 'right-leg');
      var hipX = 0, kneeX = 0, ankleX = 0, hipZ = leg.side * 0.025;
      if (mine && ge > 0) {
        hipX = -0.95 * ge; kneeX = 1.35 * ge; ankleX = -0.35 * ge;
      } else if (other && ge > 0) {
        kneeX = 0.12 * ge; hipX = -0.06 * ge; ankleX = -0.06 * ge;
      }
      leg.hip.rotation.x = hipX;
      leg.hip.rotation.z = hipZ;
      leg.knee.rotation.x = kneeX;
      leg.ankle.rotation.x = ankleX;
    }

    function render(t) {
      var now = performance.now();
      var g = null, gp = 0, ge = 0;
      if (gesture) {
        gp = Math.min(1, (now - gesture.start) / gesture.dur);
        ge = envelope(gp);
        g = gesture.part;
        if (gp >= 1) gesture = null;
      }

      // Attention: eyes wake on hover/interaction
      var wantAwake = hovered || !!gesture || now < speakUntil ? 1 : 0;
      awake += (wantAwake - awake) * (reducedMotion ? 1 : 0.08);

      // Look-at tracking (smoothed)
      var k = reducedMotion ? 1 : 0.07;
      focus.x += (pointer.x - focus.x) * k;
      focus.y += (pointer.y - focus.y) * k;

      // Body: weight shift + subtle turn toward the cursor
      var sway = reducedMotion ? 0 : Math.sin(t * 0.9) * 0.012;
      robot.rotation.y = focus.x * 0.22;
      hips.position.x = sway * 1.4;
      hips.rotation.z = -sway * 0.6;
      waist.rotation.z = sway * 0.9;
      waist.rotation.y = focus.x * 0.08;
      chest.scale.set(1, 1 + (reducedMotion ? 0 : Math.sin(t * 1.3) * 0.006), 1);

      var leaning = g && g.indexOf('leg') > -1 ? ge : 0;
      var bowing = g === 'chest' ? ge : 0;
      waist.rotation.x = bowing * 0.22 - leaning * 0.05;
      hips.rotation.x = -leaning * 0.04;
      hips.position.y = 1.68 - (g && g.indexOf('leg') > -1 ? 0.03 * ge : 0);
      hips.position.x += (g === 'left-leg' ? -0.05 : g === 'right-leg' ? 0.05 : 0) * ge;

      // Head: follow cursor; tilt + nod for the head gesture
      var hg = g === 'head' ? ge : 0;
      head.rotation.y = focus.x * 0.45 + Math.sin(gp * Math.PI * 4) * 0.12 * hg;
      head.rotation.x = focus.y * 0.22 - bowing * 0.15 + Math.sin(gp * Math.PI * 6) * 0.14 * hg;
      head.rotation.z = -focus.x * 0.05 + 0.24 * hg;

      poseArm(armL, t, g, gp, ge);
      poseArm(armR, t, g, gp, ge);
      poseLeg(legL, t, g, ge, g === 'right-leg');
      poseLeg(legR, t, g, ge, g === 'left-leg');

      // Eyes: standby (dim slits) → awake (bright, round), blink, track cursor
      var blink = 1;
      if (!reducedMotion && awake > 0.5) {
        if (now > nextBlink) { blinkStart = now; nextBlink = now + 2600 + Math.random() * 2600; }
        var bt = (now - blinkStart) / 150;
        if (bt >= 0 && bt < 1) blink = Math.abs(1 - bt * 2) * 0.9 + 0.1;
      }
      var happy = (g && ge > 0.3) ? 1 : 0;
      eyes.forEach(function (e) {
        var open = lerp(0.22, 1, awake) * blink;
        e.eye.scale.set(lerp(1, 1.08, happy), Math.max(0.08, open), 1);
        e.led.material.opacity = lerp(0.5, 1, awake);
        e.glow.material.opacity = lerp(0.2, 0.75, awake);
        e.glow.scale.set(0.13, 0.085, 1);
        e.pivot.rotation.y = e.baseYaw + focus.x * 0.09;
        e.pivot.rotation.x = -0.08 + focus.y * 0.07 - happy * 0.04;
      });

      // Voice bar while speaking
      var speaking = now < speakUntil && !reducedMotion;
      voice.forEach(function (b, i) {
        var h = speaking
          ? 0.25 + Math.abs(Math.sin(now * 0.018 + i * 1.7) * Math.sin(now * 0.007 + i)) * 1.1
          : lerp(0.12, 0.2, awake);
        b.scale.y += (h - b.scale.y) * 0.35;
        b.material.opacity = lerp(0.35, 0.95, awake);
      });

      // Core heartbeat (stronger on chest gesture)
      var beat = reducedMotion ? 0.6 : 0.55 + Math.pow(Math.max(0, Math.sin(t * 2.4)), 6) * 0.45;
      var corePulse = beat + (g === 'chest' ? ge * 0.8 : 0) + (speaking ? 0.2 : 0);
      coreGlow.material.opacity = Math.min(1, 0.45 + corePulse * 0.55);
      coreGlow.scale.setScalar(0.28 + corePulse * 0.14);
      accent.emissiveIntensity = 1.1 + corePulse * 0.6;

      ring.material.opacity = lerp(0.32, 0.65, awake);
      ringDash.rotation.z = reducedMotion ? 0 : t * 0.35;

      renderer.render(scene, camera);
    }

    // Render loop only while visible
    var clock = new THREE.Clock();
    var visible = true, running = false, rafId = 0;
    function loop() {
      if (!running) return;
      render(clock.getElapsedTime());
      rafId = requestAnimationFrame(loop);
    }
    function setRunning(on) {
      if (reducedMotion) { render(0); return; }
      if (on && !running) { running = true; clock.start(); loop(); }
      else if (!on && running) { running = false; cancelAnimationFrame(rafId); }
    }
    if ('IntersectionObserver' in window) {
      new IntersectionObserver(function (entries) {
        visible = entries[0].isIntersecting;
        setRunning(visible && !document.hidden);
      }, { threshold: 0.05 }).observe(canvas);
    }
    document.addEventListener('visibilitychange', function () { setRunning(visible && !document.hidden); });
    if (window.ResizeObserver) new ResizeObserver(resize).observe(canvas);
    else window.addEventListener('resize', resize);

    resize();
    canvas.dataset.robotReady = 'true';
    api.ready = true;
    setRunning(true);
    if (reducedMotion) render(0);
    // A friendly hello once she appears on screen
    setTimeout(function () { if (!reducedMotion) { startGesture('left-arm'); api.speak(1200); } }, 900);
  }

  window.phAara = { mount: mount };
  if (window.phAaraQueue) {
    var q = window.phAaraQueue;
    window.phAaraQueue = null;
    var ctl = mount(q.canvas, q.opts);
    if (q.onMounted) q.onMounted(ctl);
  }
})();
