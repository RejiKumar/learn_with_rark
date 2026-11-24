// Generic scene templates. make_video.py writes `const SPECS = [...]` above this file's contents.
// Objects and type only: no people or animals.
export default (kit) => {
  const { O, room, cam, drift, prog, ease, lerp, clay, rbox, torus, cyl, metal, glow, spill, sign } = kit;
  const ACCENT = '#7CF2C8';

  const wrap = (x, text, cx, y, maxW, lh) => {
    const words = String(text).split(' '); let line = ''; const out = [];
    for (const w of words) { const t = line ? line + ' ' + w : w; if (x.measureText(t).width > maxW && line) { out.push(line); line = w; } else line = t; }
    out.push(line); out.forEach((l, i) => x.fillText(l, cx, y + i * lh)); return out.length;
  };

  const phoneScreen = (s, t, w, h, x) => {
    x.fillStyle = '#0b0d12'; x.fillRect(0, 0, w, h); x.textAlign = 'center'; x.textBaseline = 'middle';
    x.fillStyle = '#e8ecf3'; x.font = `800 ${w * 0.085}px Inter`; wrap(x, s.title || '', w / 2, h * 0.16, w * 0.86, w * 0.1);
    if (s.mode === 'toggle') {
      const k = prog(t, (s.at ?? 1.6) - 0.1, (s.at ?? 1.6) + 0.25, ease.out);
      x.fillStyle = '#9fb0c8'; x.font = `600 ${w * 0.055}px Inter`; x.fillText(s.subtitle || '', w / 2, h * 0.34);
      const bw = w * 0.5, bh = h * 0.09, bx = (w - bw) / 2, by = h * 0.46;
      x.fillStyle = k > 0.5 ? '#2fd07a' : '#3a4150'; x.beginPath(); x.roundRect(bx, by, bw, bh, bh / 2); x.fill();
      x.fillStyle = '#fff'; x.beginPath(); x.arc(bx + bh / 2 + k * (bw - bh), by + bh / 2, bh * 0.42, 0, Math.PI * 2); x.fill();
      x.fillStyle = k > 0.5 ? '#2fd07a' : '#6b7587'; x.font = `800 ${w * 0.09}px Inter`; x.fillText(k > 0.5 ? 'ON' : 'OFF', w / 2, h * 0.68);
    } else if (s.mode === 'code') {
      const code = ['482 913', '175 608', '936 240'][Math.min(2, Math.floor(t / 1.7))];
      x.fillStyle = ACCENT; x.font = `800 ${w * 0.2}px Inter`; x.fillText(code, w / 2, h * 0.45);
      const k = (t % 1.7) / 1.7;
      x.strokeStyle = '#1d2a36'; x.lineWidth = w * 0.035; x.beginPath(); x.arc(w / 2, h * 0.68, w * 0.16, 0, Math.PI * 2); x.stroke();
      x.strokeStyle = ACCENT; x.beginPath(); x.arc(w / 2, h * 0.68, w * 0.16, -Math.PI / 2, -Math.PI / 2 + (1 - k) * Math.PI * 2); x.stroke();
    } else {
      const lines = s.lines || [];
      lines.forEach((l, i) => {
        const y = h * (0.32 + i * 0.13), shown = Math.floor(prog(t, 0.3 + i * 0.9, 1.1 + i * 0.9, ease.out) * l.length);
        x.fillStyle = '#1a1f2b'; x.fillRect(w * 0.08, y - h * 0.04, w * 0.84, h * 0.08);
        x.fillStyle = '#cdd6e6'; x.textAlign = 'left'; x.font = `600 ${w * 0.055}px Inter`; x.fillText(l.slice(0, shown), w * 0.12, y); x.textAlign = 'center';
      });
    }
    if (s.badge && t > (s.badgeAt ?? 2.4)) {
      const on = Math.floor(t * 4) % 2 === 0, c = s.badgeColor || '#ff3b30';
      x.fillStyle = on ? c : '#00000066'; x.fillRect(0, h * 0.56, w, h * 0.13);
      x.fillStyle = '#fff'; x.font = `800 ${w * 0.1}px Inter`; x.fillText(s.badge, w / 2, h * 0.625);
    }
  };

  const make = (s, i) => {
    if (s.type === 'door') return {
      build(g) { room(g, 'night', { keyPower: 60, fillPower: 0.35, wallZ: -2 }); const door = O.door(g, { gap: 0.09 });
        const sp = spill(g, 3.2, 1.3, '#ffe2b0', 0.9); sp.position.set(0, 0.05, 0.9); sp.rotation.x = -Math.PI / 2; return { door, sp }; },
      update({ door, sp }, t) { door.open(prog(t, 0, 1.2, ease.out) * 0.35); sp.set(0.8 + 0.2 * Math.sin(t * 9));
        const d = drift(t, 0.015); cam(d.x + lerp(0.8, 0, prog(t, 0, 1, ease.out)), 1.5 + d.y, lerp(11, 7.4, prog(t, 0, 1.4, ease.out)), 0, 1.55, 0, 30); },
    };
    if (s.type === 'padlock') return {
      build(g) { room(g, 'clay', { keyPower: 80, fillPower: 0.2 });
        rbox(g, 1.2, 1, 0.5, 0.08, metal('#c9b27a'), 0, 1.3, 0); const sh = torus(g, 0.42, 0.09, metal('#e1ddd2'), 0, 2.0, 0);
        const dot = cyl(g, 0.07, 0.07, 0.06, glow('#2fd07a', 0), 0, 1.35, 0.26); dot.rotation.x = Math.PI / 2; return { sh, dot }; },
      update({ sh, dot }, t) { sh.position.y = 2.0 + (1 - prog(t, 0, 0.5, ease.drop)) * 0.5 - 0.18 * prog(t, 0.2, 0.6, ease.drop);
        dot.material.emissiveIntensity = prog(t, 0.6, 1.0, ease.out) * 6; const d = drift(t, 0.015);
        cam(d.x, 1.6 + d.y, lerp(11, 8.6, prog(t, 0, 2.5, ease.out)), 0, 1.6, 0, 30); },
    };
    if (s.type === 'sign') return {
      build(g) { const r = room(g, s.look || 'ink', { keyPower: 60, fillPower: 0.5, wallZ: -2 });
        const sg = sign(g, s.text || '', { w: 3.2, h: 1.6, size: 0.3, color: s.color || '#fff', weight: 800 }); sg.position.set(0, 1.6, r.wall.position.z + 0.05); return { sg }; },
      update({ sg }, t) { const a = prog(t, 0, 0.5, ease.back); sg.scale.set(a, a, a); const d = drift(t, 0.015); cam(d.x, 1.6 + d.y, lerp(8, 5.2, prog(t, 0, 1.6, ease.out)), 0, 1.6, 0, 32); },
    };
    if (s.type === 'bulb') return {
      build(g) { const r = room(g, 'night', { keyPower: 150, fillPower: 1.1, wallZ: -2.4 }); const p = O.pendant(g, 3, { power: 14, core: 8, color: '#ffb066', shadow: true }); return { p, r }; },
      update({ p, r }, t) { const lit = prog(t, 0.2, 1.4, ease.out); p.bulb.set(0.1 + lit * 0.9); r.key.intensity = 30 + lit * 120;
        const d = drift(t, 0.02); cam(d.x, 2.1 + d.y, lerp(7, 3.9, prog(t, 0, 2.6, ease.inOut)), 0, 2, 0, 30); },
    };
    // default: a phone. Slides in fast so the first frames already move.
    return {
      build(g) { room(g, 'ink', { keyPower: 55, angle: 0.4, keyX: -0.6, keyZ: 3 }); const phone = O.phone(g, { power: 1.2 }); phone.position.set(0, 1.5, 0); return { phone }; },
      update({ phone }, t, k) { phone.screen.paint((x, w, h) => phoneScreen(s, t, w, h, x));
        phone.position.y = 1.5 + (1 - prog(t, 0, 0.55, ease.back)) * -3; phone.rotation.y = Math.sin(t * 0.7) * 0.1 + (1 - prog(t, 0, 0.7, ease.out)) * 1.2;
        const d = drift(t, 0.012); cam(d.x, 1.55 + d.y, lerp(7.2, 3.9, prog(t, 0, 2.2, ease.out)), 0, 1.5, 0, 32); void k; void i; },
    };
  };

  const out = {};
  SPECS.forEach((s, i) => { out['b' + (i + 1)] = make(s, i); });
  return out;
};
