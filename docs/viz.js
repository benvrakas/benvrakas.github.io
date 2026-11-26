// Theme visualizations for the project headers: print (slicer preview + live G-code), pcb (generated board),
// code (editor typing the project's metadata), lab (rotating caffeine molecule, drag to turn), cad (dimensioned drawing).
(() => {
  const nodes = document.querySelectorAll('.viz[data-viz]');
  if (!nodes.length) return;
  const NS = 'http://www.w3.org/2000/svg';
  const RM = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const mk = (tag, at, parent) => {
    const e = document.createElementNS(NS, tag);
    for (const k in at) e.setAttribute(k, at[k]);
    if (parent) parent.appendChild(e);
    return e;
  };
  const svg = (node, w = 360, h = 210) => mk('svg', { viewBox: `0 0 ${w} ${h}`, preserveAspectRatio: 'xMidYMid meet' }, node);
  const rand = (seed) => { let s = (seed * 2654435761) % 4294967296 || 1; return () => ((s = (s * 1664525 + 1013904223) % 4294967296) / 4294967296); };
  const f2 = (n) => n.toFixed(2);
  const txt = (parent, x, y, s, at = {}) => { const t = mk('text', { x, y, ...at }, parent); t.textContent = s; return t; };
  const live = [];

  // ---------------------------------------------------------------- print: slicer preview with streaming G-code
  function print(node) {
    const S = svg(node);
    let R = rand(+node.dataset.seed || 7);
    const list = mk('g', { class: 'gl' }, S);
    mk('rect', { x: 0, y: 0, width: 148, height: 210, class: 'glbg' }, list);
    const ROWS = 12, LY = (i) => 24 + i * 15.2;
    const hl = mk('rect', { x: 0, y: LY(ROWS - 1) - 11, width: 148, height: 15, class: 'hl' }, list);
    const rows = Array.from({ length: ROWS }, (_, i) => mk('text', { x: 9, y: LY(i) }, list));
    const cap = txt(S, 160, 18, '', { class: 'cap' });
    const cx = 262, cy = 124, k = 2.2, LH = 3.6, NL = 8;
    const P = (x, y, z) => [cx + (x - y) * 0.866 * k, cy + (x + y) * 0.5 * k - z * LH];
    const bedG = mk('g', {}, S), layersG = mk('g', {}, S);
    const noz = mk('g', { class: 'noz' }, S);
    mk('path', { d: 'M-6 -18 H6 L2.5 -5 L0 0 L-2.5 -5 Z' }, noz);
    let W, H, r, moves, mi, prog, layer, g, cur, e, lines, hold, z;

    const rrect = (w, h, rr, n = 4) => {
      const pts = [];
      for (const [x, y, a0] of [[w - rr, h - rr, 0], [-w + rr, h - rr, 90], [-w + rr, -h + rr, 180], [w - rr, -h + rr, 270]])
        for (let i = 0; i <= n; i++) { const a = (a0 + 90 * i / n) * Math.PI / 180; pts.push([x + rr * Math.cos(a), y + rr * Math.sin(a)]); }
      pts.push(pts[0]);
      return pts;
    };
    const infill = (w, h, sp, s) => {
      const out = []; let flip = false;
      for (let c = -(w + h) + sp / 2; c < w + h; c += sp) {
        let xa = (-h - c) / s, xb = (h - c) / s;
        if (xa > xb) [xa, xb] = [xb, xa];
        xa = Math.max(xa, -w); xb = Math.min(xb, w);
        if (xb - xa < 1) continue;
        let a = [xa, s * xa + c], b = [xb, s * xb + c];
        if (flip) [a, b] = [b, a];
        flip = !flip;
        out.push(a, b);
      }
      return out;
    };
    const plan = (L) => {
      const m = [{ c: `;LAYER:${L}` }, { c: `G1 Z${f2(0.2 * (L + 1))} F600` }];
      let last = null;
      const run = (pts, type, label) => {
        m.push({ c: `;TYPE:${label}` });
        if (last) m.push({ t: 'travel', a: last, b: pts[0] });
        for (let i = 1; i < pts.length; i++) m.push({ t: type, a: pts[i - 1], b: pts[i] });
        last = pts[pts.length - 1];
      };
      run(rrect(W, H, r), 'outer', 'WALL-OUTER');
      run(rrect(W - 1.6, H - 1.6, Math.max(0.6, r - 1.6)), 'inner', 'WALL-INNER');
      run(infill(W - 2.6, H - 2.6, L === 0 || L === NL - 1 ? 2.2 : 4.4, L % 2 ? 1 : -1), 'fill', L === 0 || L === NL - 1 ? 'SKIN' : 'FILL');
      return m;
    };
    const push = (s, cm) => {
      lines.push([s, cm]);
      if (lines.length > ROWS) lines.shift();
      rows.forEach((t, i) => {
        const l = lines[i - (ROWS - lines.length)];
        t.textContent = l ? l[0] : '';
        t.setAttribute('class', l && l[1] ? 'cm' : '');
      });
    };
    const reset = () => {
      W = 22 + R() * 9; H = 13 + R() * 8; r = 2 + R() * 7;
      layersG.textContent = ''; bedG.textContent = '';
      const bed = [[-W - 9, -H - 9], [W + 9, -H - 9], [W + 9, H + 9], [-W - 9, H + 9]].map(([x, y]) => P(x, y, -0.4).join(',')).join(' ');
      mk('polygon', { points: bed, class: 'bed' }, bedG);
      for (let i = -3; i <= 3; i++) {
        const a = P(-W - 9, i * (H + 9) / 3.5, -0.4), b = P(W + 9, i * (H + 9) / 3.5, -0.4);
        mk('line', { x1: a[0], y1: a[1], x2: b[0], y2: b[1], class: 'bedl' }, bedG);
      }
      layer = 0; e = 0; lines = []; hold = 0; mi = 0; prog = 0; cur = null; z = 0;
      moves = plan(0); g = mk('g', { class: 'lay' }, layersG);
      ['G28 ; home', 'M104 S215', 'M140 S60', 'G92 E0'].forEach((s) => push(s, s[0] === ';'));
    };
    const tick = (dt) => {
      if (hold > 0) { hold -= dt; if (hold <= 0) { R = rand(Math.floor(Math.random() * 1e6)); reset(); } return; }
      let budget = dt;
      while (budget > 0) {
        const mv = moves[mi];
        if (!mv) {
          g.setAttribute('class', 'lay old');
          g.querySelectorAll('.travel').forEach((t) => t.remove());
          layer++;
          if (layer >= NL) { hold = 2.4; cap.textContent = `layer ${NL}/${NL} · done`; return; }
          moves = plan(layer); mi = 0; z = layer; g = mk('g', { class: 'lay' }, layersG);
          continue;
        }
        if (mv.c) { push(mv.c, mv.c[0] === ';'); mi++; budget -= 0.05; continue; }
        const len = Math.hypot(mv.b[0] - mv.a[0], mv.b[1] - mv.a[1]);
        const speed = mv.t === 'travel' ? 520 : 230;
        if (!cur) {
          const a = P(mv.a[0], mv.a[1], z);
          cur = mk('line', { x1: a[0], y1: a[1], x2: a[0], y2: a[1], class: mv.t }, g);
          if (mv.t === 'travel') push(`G0 X${f2(mv.b[0] + 110)} Y${f2(mv.b[1] + 110)}`);
          else { e += len * 0.0333; push(`G1 X${f2(mv.b[0] + 110)} Y${f2(mv.b[1] + 110)} E${e.toFixed(4)}`); }
        }
        const need = (len * (1 - prog)) / speed;
        let t;
        if (budget >= need) { prog = 1; budget -= need; } else { prog += (budget * speed) / Math.max(len, 1e-6); budget = 0; }
        t = Math.min(1, prog);
        const p = P(mv.a[0] + (mv.b[0] - mv.a[0]) * t, mv.a[1] + (mv.b[1] - mv.a[1]) * t, z);
        cur.setAttribute('x2', p[0]); cur.setAttribute('y2', p[1]);
        noz.setAttribute('transform', `translate(${p[0]} ${p[1]})`);
        if (prog >= 1) { cur = null; prog = 0; mi++; }
      }
      cap.textContent = `layer ${layer + 1}/${NL} · Z ${f2(0.2 * (layer + 1))} mm`;
    };
    reset();
    return { node, tick, finish: () => tick(1e6) };
  }

  // ---------------------------------------------------------------- pcb: generated board with signal pulses
  function pcb(node) {
    const S = svg(node), R = rand(+node.dataset.seed || 5);
    mk('rect', { x: 5, y: 5, width: 350, height: 200, rx: 10, class: 'board' }, S);
    [[18, 18], [342, 18], [18, 192], [342, 192]].forEach(([x, y]) => mk('circle', { cx: x, cy: y, r: 5.5, class: 'hole' }, S));
    const cu = mk('g', { class: 'cu' }, S), sigs = mk('g', {}, S), parts = mk('g', {}, S), silk = mk('g', { class: 'silk' }, S);
    const ux = 192, uy = 106, half = 25, n = 8, pitch = 5.6, mid = (n - 1) / 2;
    const traces = [];
    const trace = (d) => { mk('path', { d, class: 'tr' }, cu); traces.push(d); };
    const via = (x, y) => mk('circle', { cx: x, cy: y, r: 3.4, class: 'via' }, cu);
    for (let k = 0; k < n; k++) {
      const o = (k - mid) * pitch;
      // left -> J1 header
      const py = uy + o, ty = uy + (k - mid) * 16, xb = 152, dy = Math.abs(ty - py);
      trace(`M${ux - half - 6} ${py} H${xb} L${xb - dy} ${ty} H44`);
      mk('rect', { x: ux - half - 7, y: py - 1.4, width: 7, height: 2.8, class: 'pad' }, parts);
      mk(k ? 'circle' : 'rect', k ? { cx: 40, cy: ty, r: 5, class: 'th' } : { x: 35, y: ty - 5, width: 10, height: 10, class: 'th' }, parts);
      // right -> resistor column -> vias
      const ry = uy + (k - mid) * 14, rb = 238, rdy = Math.abs(ry - py);
      trace(`M${ux + half + 6} ${py} H${rb} L${rb + rdy} ${ry} H281`);
      trace(`M297 ${ry} H${312 + (k % 2) * 14}`);
      via(315 + (k % 2) * 14, ry);
      mk('rect', { x: ux + half, y: py - 1.4, width: 7, height: 2.8, class: 'pad' }, parts);
      mk('rect', { x: 279, y: ry - 3.2, width: 6, height: 6.4, class: 'pad' }, parts);
      mk('rect', { x: 291, y: ry - 3.2, width: 6, height: 6.4, class: 'pad' }, parts);
      mk('rect', { x: 284.5, y: ry - 2.6, width: 7, height: 5.2, class: 'res' }, parts);
      // top and bottom -> staggered vias
      const px = ux + o, vt = 34 + (k % 2) * 11, vb = 176 - (k % 2) * 11;
      trace(`M${px} ${uy - half - 6} V${vt + 3}`); via(px, vt);
      trace(`M${px} ${uy + half + 6} V${vb - 3}`); via(px, vb);
      mk('rect', { x: px - 1.4, y: uy - half - 7, width: 2.8, height: 7, class: 'pad' }, parts);
      mk('rect', { x: px - 1.4, y: uy + half, width: 2.8, height: 7, class: 'pad' }, parts);
      if (k % 2 === 0) txt(silk, 302, ry + 2.5, `R${k + 1}`, { 'font-size': 6 });
    }
    mk('rect', { x: ux - half, y: uy - half, width: half * 2, height: half * 2, rx: 2, class: 'ic' }, parts);
    mk('circle', { cx: ux - half + 6, cy: uy - half + 6, r: 2, class: 'pin1' }, parts);
    txt(parts, ux, uy + 2, 'V-LABS', { class: 'icl' });
    txt(parts, ux, uy + 10, ((node.dataset.years || '').match(/\d{4}/g) || []).join('-'), { class: 'icl sm' });
    txt(silk, ux + half + 5, uy - half - 3, 'U1');
    txt(silk, 33, 36, 'J1');
    txt(silk, 60, 198, `${(node.dataset.title || '').split(':')[0].slice(0, 30).toUpperCase()} · REV ${'ABCD'[Math.floor(R() * 4)]}`, { class: 'bt' });
    // capacitors near the chip corners
    [[ux - half - 16, uy - half - 14], [ux + half + 10, uy + half + 9]].forEach(([x, y], i) => {
      mk('rect', { x, y, width: 4.5, height: 5, class: 'pad' }, parts);
      mk('rect', { x: x + 8, y, width: 4.5, height: 5, class: 'pad' }, parts);
      txt(silk, x, y - 3, `C${i + 1}`, { 'font-size': 6 });
    });
    if (!RM) traces.forEach((d) => {
      if (R() < 0.45) return;
      const s = mk('path', { d, class: 'sig', pathLength: 300 }, sigs);
      s.style.animationDelay = `${(-R() * 3).toFixed(2)}s`;
      s.style.animationDuration = `${(2 + R() * 2).toFixed(2)}s`;
    });
    return null;
  }

  // ---------------------------------------------------------------- code: editor typing the project's metadata
  function code(node) {
    const d = node.dataset, tags = (d.tags || '').split('|').filter(Boolean);
    const T = [];
    const p = (t, c = '') => T.push([t, c]);
    p(`// ${d.title}\n`, 'cm');
    p('export const ', 'kw'); p('project', 'fn'); p(' = {\n');
    p('  slug: '); p(`"${d.slug}"`, 'str'); p(',\n');
    p('  years: '); p(`"${d.years}"`, 'str'); p(',\n');
    p('  stack: [');
    tags.forEach((t, i) => { p(`"${t}"`, 'str'); if (i < tags.length - 1) p(', '); });
    p('],\n');
    p('};\n\n');
    p('ship', 'fn'); p('(project);');
    const total = T.reduce((a, t) => a + t[0].length, 0);
    const lineCount = T.reduce((a, t) => a + (t[0].match(/\n/g) || []).length, 1);
    node.innerHTML = `<div class="ed"><div class="tabs"><span class="on">${d.slug}.ts</span><span>README.md</span></div>`
      + `<div class="eb"><pre class="gut">${Array.from({ length: lineCount }, (_, i) => i + 1).join('\n')}</pre><pre class="src"></pre></div></div>`;
    const src = node.querySelector('.src');
    const esc = (s) => s.replace(/&/g, '&amp;').replace(/</g, '&lt;');
    let shown = 0;
    const render = (n) => {
      let left = n, out = '';
      for (const [t, c] of T) {
        if (left <= 0) break;
        const s = t.slice(0, left); left -= s.length;
        out += c ? `<span class="${c}">${esc(s)}</span>` : esc(s);
      }
      src.innerHTML = out + '<span class="caret"></span>';
    };
    const tick = (dt) => {
      if (shown >= total) return;
      shown = Math.min(total, shown + dt * 34);
      render(Math.floor(shown));
    };
    render(0);
    return { node, tick, finish: () => { shown = total; render(total); } };
  }

  // ---------------------------------------------------------------- lab: caffeine, ball-and-stick, drag to rotate
  function lab(node) {
    const S = svg(node);
    const uid = Math.random().toString(36).slice(2, 7);
    const defs = mk('defs', {}, S);
    const CPK = { C: ['#c9ced6', '#5b6270'], N: ['#a9c1ff', '#3456c8'], O: ['#ffb3b3', '#c62f2f'], H: ['#ffffff', '#9aa3b2'] };
    for (const el in CPK) {
      const g = mk('radialGradient', { id: `a${el}${uid}`, cx: '35%', cy: '30%', r: '70%' }, defs);
      mk('stop', { offset: '0', 'stop-color': CPK[el][0] }, g);
      mk('stop', { offset: '1', 'stop-color': CPK[el][1] }, g);
    }
    const A = [], B = [], deg = Math.PI / 180;
    const add = (el, x, y, z = 0) => (A.push({ el, x, y, z }), A.length - 1);
    const bond = (i, j, o = 1) => B.push([i, j, o]);
    const hex = (a) => [1.4 * Math.cos(a * deg), 1.4 * Math.sin(a * deg)];
    const pc = [2.176, 0], pent = (a) => [pc[0] + 1.191 * Math.cos(a * deg), 1.191 * Math.sin(a * deg)];
    const C5 = add('C', ...hex(30)), C6 = add('C', ...hex(90)), N1 = add('N', ...hex(150));
    const C2 = add('C', ...hex(210)), N3 = add('N', ...hex(270)), C4 = add('C', ...hex(330));
    const N7 = add('N', ...pent(72)), C8 = add('C', ...pent(0)), N9 = add('N', ...pent(-72));
    [[C5, C6], [C6, N1], [N1, C2], [C2, N3], [N3, C4], [C5, N7], [N7, C8], [N9, C4]].forEach(([a, b]) => bond(a, b));
    bond(C4, C5, 2); bond(C8, N9, 2);
    const out = (i, c, len, el) => {
      const a = A[i], dx = a.x - c[0], dy = a.y - c[1], L = Math.hypot(dx, dy);
      return add(el, a.x + dx / L * len, a.y + dy / L * len);
    };
    bond(C6, out(C6, [0, 0], 1.23, 'O'), 2);
    bond(C2, out(C2, [0, 0], 1.23, 'O'), 2);
    bond(C8, out(C8, pc, 1.08, 'H'));
    const methyl = (i, c) => {
      const m = out(i, c, 1.47, 'C'); bond(i, m);
      const ux = (A[m].x - A[i].x) / 1.47, uy = (A[m].y - A[i].y) / 1.47;
      for (let j = 0; j < 3; j++) {
        const ph = (j * 120 + 90) * deg;
        bond(m, add('H', A[m].x + 1.09 * (0.334 * ux - 0.943 * Math.cos(ph) * uy), A[m].y + 1.09 * (0.334 * uy + 0.943 * Math.cos(ph) * ux), 1.09 * 0.943 * Math.sin(ph)));
      }
    };
    methyl(N1, [0, 0]); methyl(N3, [0, 0]); methyl(N7, pc);
    const mx = A.reduce((s, a) => s + a.x, 0) / A.length, my = A.reduce((s, a) => s + a.y, 0) / A.length;
    A.forEach((a) => { a.x -= mx; a.y -= my; });
    const RAD = { C: 0.36, N: 0.34, O: 0.33, H: 0.22 };
    const G = mk('g', {}, S);
    const atomEls = A.map((a) => mk('circle', { fill: `url(#a${a.el}${uid})`, class: 'atom' }));
    const bondEls = B.map(([, , o]) => (o === 2 ? [mk('line', { class: 'bond' }), mk('line', { class: 'bond' })] : [mk('line', { class: 'bond' })]));
    txt(S, 12, 198, 'C₈H₁₀N₄O₂ · caffeine', { class: 'cap' });
    txt(S, 348, 18, 'drag to rotate', { class: 'cap', 'text-anchor': 'end' });
    let ry = 0.6, rx = 0.45, auto = 0, drag = null;
    const sc = 23, cx = 180, cy = 104, cam = 9;
    const draw = () => {
      const cyw = Math.cos(ry), syw = Math.sin(ry), cxw = Math.cos(rx), sxw = Math.sin(rx);
      const pr = A.map((a) => {
        const x1 = a.x * cyw + a.z * syw, z1 = -a.x * syw + a.z * cyw;
        const y2 = a.y * cxw - z1 * sxw, z2 = a.y * sxw + z1 * cxw;
        const f = cam / (cam + z2);
        return { X: cx + x1 * sc * f, Y: cy - y2 * sc * f, z: z2, f };
      });
      const items = [];
      A.forEach((a, i) => items.push({ z: pr[i].z, el: atomEls[i], set: () => {
        atomEls[i].setAttribute('cx', pr[i].X); atomEls[i].setAttribute('cy', pr[i].Y); atomEls[i].setAttribute('r', RAD[a.el] * sc * pr[i].f);
      } }));
      B.forEach(([i, j, o], b) => {
        const p = pr[i], q = pr[j], z = (p.z + q.z) / 2 + 0.01;
        const dx = q.X - p.X, dy = q.Y - p.Y, L = Math.hypot(dx, dy) || 1, nx = -dy / L * 2.3, ny = dx / L * 2.3;
        bondEls[b].forEach((ln, m) => {
          const off = o === 2 ? (m ? 1 : -1) : 0;
          items.push({ z, el: ln, set: () => {
            ln.setAttribute('x1', p.X + nx * off); ln.setAttribute('y1', p.Y + ny * off);
            ln.setAttribute('x2', q.X + nx * off); ln.setAttribute('y2', q.Y + ny * off);
          } });
        });
      });
      items.sort((a, b) => b.z - a.z).forEach((it) => { it.set(); G.appendChild(it.el); });
    };
    node.addEventListener('pointerdown', (e) => { drag = [e.clientX, e.clientY, ry, rx]; node.setPointerCapture(e.pointerId); });
    node.addEventListener('pointermove', (e) => {
      if (!drag) return;
      ry = drag[2] + (e.clientX - drag[0]) * 0.012; rx = Math.max(-1.4, Math.min(1.4, drag[3] + (e.clientY - drag[1]) * 0.012));
      auto = 0; draw();
    });
    const end = () => { drag = null; };
    node.addEventListener('pointerup', end); node.addEventListener('pointercancel', end);
    draw();
    return { node, tick: (dt) => { if (drag) return; auto = Math.min(1, auto + dt * 0.5); ry += dt * 0.45 * auto; draw(); }, finish: draw };
  }

  // ---------------------------------------------------------------- cad: orthographic drawing, iso view, title block
  function cad(node) {
    const S = svg(node), d = node.dataset;
    const dw = mk('g', { class: 'dwg' }, S);
    const L = (x1, y1, x2, y2, c = 'ol') => mk('line', { x1, y1, x2, y2, class: c, pathLength: 1 }, dw);
    const T = (x, y, s, at = {}) => txt(dw, x, y, s, { class: 'dt', ...at });
    mk('rect', { x: 4, y: 4, width: 352, height: 202, class: 'frame' }, dw);
    // front view: plate with two holes and a slot
    mk('rect', { x: 34, y: 34, width: 120, height: 70, rx: 6, class: 'ol', pathLength: 1 }, dw);
    [[58, 69], [130, 69]].forEach(([x, y]) => {
      mk('circle', { cx: x, cy: y, r: 9, class: 'ol', pathLength: 1 }, dw);
      L(x - 14, y, x + 14, y, 'cl'); L(x, y - 14, x, y + 14, 'cl');
    });
    mk('rect', { x: 82, y: 58, width: 24, height: 22, rx: 11, class: 'ol', pathLength: 1 }, dw);
    L(94, 50, 94, 88, 'cl');
    // side view with hidden lines
    mk('rect', { x: 178, y: 34, width: 14, height: 70, class: 'ol', pathLength: 1 }, dw);
    [60, 78].forEach((y) => L(178, y, 192, y, 'hid'));
    L(172, 69, 198, 69, 'cl');
    // dimensions
    const arrow = (x, y, a) => mk('path', { d: 'M0 0 L7 -2.2 L7 2.2 Z', transform: `translate(${x} ${y}) rotate(${a})`, class: 'ar' }, dw);
    L(34, 108, 34, 128, 'dim'); L(154, 108, 154, 128, 'dim'); L(34, 123, 154, 123, 'dim'); arrow(34, 123, 0); arrow(154, 123, 180);
    T(94, 119, '120.0', { 'text-anchor': 'middle' });
    L(30, 34, 12, 34, 'dim'); L(30, 104, 12, 104, 'dim'); L(17, 34, 17, 104, 'dim'); arrow(17, 34, 90); arrow(17, 104, -90);
    T(14, 72, '70.0', { 'text-anchor': 'middle', transform: 'rotate(-90 14 72)' });
    L(178, 108, 178, 128, 'dim'); L(192, 108, 192, 128, 'dim'); L(166, 123, 204, 123, 'dim'); arrow(178, 123, 180); arrow(192, 123, 0);
    T(185, 136, '14', { 'text-anchor': 'middle' });
    L(136.4, 62.6, 158, 22, 'dim'); L(158, 22, 206, 22, 'dim'); arrow(136.4, 62.6, -62);
    T(160, 19, '2× ⌀18 THRU');
    T(34, 148, 'FRONT'); T(178, 148, 'RIGHT'); T(318, 140, 'ISO', { 'text-anchor': 'middle' });
    // isometric view (faces x=120, y=14, z=70 are visible)
    const s = 0.5, ox = 284, oy = 94;
    const P = (x, y, z) => [ox + (x - y) * 0.866 * s, oy + (x + y) * 0.5 * s - z * s];
    const poly = (pts, c) => mk('polygon', { points: pts.map((p) => P(...p).join(',')).join(' '), class: c, pathLength: 1 }, dw);
    poly([[120, 0, 0], [120, 14, 0], [120, 14, 70], [120, 0, 70]], 'ol face');
    poly([[0, 14, 0], [120, 14, 0], [120, 14, 70], [0, 14, 70]], 'ol face');
    poly([[0, 0, 70], [120, 0, 70], [120, 14, 70], [0, 14, 70]], 'ol face');
    [24, 96].forEach((hx) => {
      const pts = [];
      for (let i = 0; i < 24; i++) { const a = i / 24 * 2 * Math.PI; pts.push([hx + 9 * Math.cos(a), 14, 35 + 9 * Math.sin(a)]); }
      poly(pts, 'ol');
    });
    // title block
    const tb = mk('g', { class: 'tb' }, dw);
    mk('rect', { x: 214, y: 150, width: 138, height: 52, class: 'frame' }, tb);
    [[214, 168, 352, 168], [214, 185, 352, 185], [290, 168, 290, 202]].forEach(([a, b, c, e]) => mk('line', { x1: a, y1: b, x2: c, y2: e, class: 'frame' }, tb));
    const lab = (x, y, s) => txt(tb, x, y, s, { class: 'tl' });
    const val = (x, y, s) => txt(tb, x, y, s, { class: 'tv' });
    const title = (d.title || '').split(':')[0].toUpperCase();
    lab(218, 156, 'TITLE'); val(218, 165, title.length > 26 ? title.slice(0, 25) + '…' : title);
    lab(218, 173, 'DWG NO'); val(218, 182, `BV-${String(d.seed || 1).padStart(3, '0')}`);
    lab(294, 173, 'SCALE'); val(294, 182, '1:2');
    lab(218, 190, 'DATE'); val(218, 199, ((d.years || '').match(/\d{4}/g) || []).join('-'));
    lab(294, 190, 'SHEET'); val(294, 199, '1 OF 1');
    if (RM) S.classList.add('done');
    return null;
  }

  const VIZ = { print, pcb, code, lab, cad };
  const io = 'IntersectionObserver' in window ? new IntersectionObserver((es) => es.forEach((e) => { e.target._vis = e.isIntersecting; })) : null;
  nodes.forEach((n) => {
    const v = VIZ[n.dataset.viz] && VIZ[n.dataset.viz](n);
    if (!v) return;
    n._vis = !io;
    if (io) io.observe(n);
    live.push(v);
  });
  if (RM) { live.forEach((v) => v.finish && v.finish()); return; }
  let last = 0;
  const loop = (t) => {
    const dt = last ? Math.min(0.05, (t - last) / 1000) : 0;
    last = t;
    live.forEach((v) => { if (v.node._vis) v.tick(dt); });
    requestAnimationFrame(loop);
  };
  if (live.length) requestAnimationFrame(loop);
})();
