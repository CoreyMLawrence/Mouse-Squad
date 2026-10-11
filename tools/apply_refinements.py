import sys, re

with open('index.html', 'r') as f:
    html = f.read()

# 1. Add native splash scene drawing functions (replacing renderSplash with drawSplashScene and pixel characters)
splash_scene_code = """
// ================= Faithful Native Recreation of Splash Screens =================
const SPLASH_DIGITS = {
  '0': [
    '.#####.',
    '##...##',
    '##...##',
    '###..##',
    '#######',
    '##.####',
    '##...##',
    '##...##',
    '.#####.'
  ],
  '1': [
    '...##..',
    '#####..',
    '#####..',
    '...##..',
    '...##..',
    '...##..',
    '...##..',
    '...##..',
    '#######'
  ],
  '2': [
    '..####.',
    '.##..##',
    '.....##',
    '.....##',
    '....##.',
    '...##..',
    '..##...',
    '.##....',
    '.######'
  ]
};

const SPLASH_LETTERS = {
  'L': [
    '##..',
    '##..',
    '##..',
    '##..',
    '####'
  ],
  'E': [
    '####',
    '##..',
    '####',
    '##..',
    '####'
  ],
  'V': [
    '##.##',
    '##.##',
    '##.##',
    '.###.',
    '..#..'
  ]
};

function drawSplashPixelChar(grid, x, y, size, col, outline = 4){
  const rows = grid.length, cols = grid[0].length;
  ctx.fillStyle = '#000000';
  for(let r = 0; r < rows; r++){
    for(let c = 0; c < cols; c++){
      if(grid[r][c] === '#'){
        ctx.fillRect(R(x + c * size - outline), R(y + r * size - outline), R(size + outline * 2), R(size + outline * 2 + 2));
      }
    }
  }
  ctx.fillStyle = col;
  for(let r = 0; r < rows; r++){
    for(let c = 0; c < cols; c++){
      if(grid[r][c] === '#'){
        ctx.fillRect(R(x + c * size), R(y + r * size), R(size), R(size));
      }
    }
  }
}

function drawSplashScene(lvl){
  // 1. Sky
  rect(0, 0, WNAT, HNAT, '#72EFFF');

  // 2. Stylized Clouds (measured from splash art)
  const c = '#FFFFFF';
  disc(140, 75, 28, 18, c); disc(164, 65, 22, 19, c); disc(188, 75, 26, 17, c); rect(134, 75, 60, 16, c);
  disc(585, 65, 24, 15, c); disc(605, 56, 18, 16, c); disc(625, 65, 22, 14, c); rect(580, 65, 50, 14, c);
  disc(650, 75, 20, 13, c); disc(666, 68, 16, 14, c); disc(682, 75, 18, 12, c); rect(646, 75, 40, 12, c);

  // 3. Road & Curb
  rect(0, 336, WNAT, HNAT - 336, '#4F7074');
  rect(0, 336, WNAT, 4, '#3E575A');
  for(const rx of [60, 260, 440, 620]){
    rrect(rx, 366, 44, 7, 3); ctx.fillStyle = '#70959A'; ctx.fill();
    rrect(rx + 90, 402, 44, 7, 3); ctx.fillStyle = '#70959A'; ctx.fill();
  }

  // 4. Scalloped Hedge
  rect(0, 314, WNAT, 22, '#02BD39');
  for(let bx = -10; bx < WNAT + 20; bx += 24){
    disc(bx + 12, 314, 12, 12, '#02BD39');
  }

  // 5. School Building (right side)
  rect(550, 215, 200, 121, '#F2E0C8');
  rect(545, 324, 210, 12, '#E2CEB4');
  ctx.fillStyle = '#DB6565'; ctx.beginPath();
  ctx.moveTo(535, 215); ctx.lineTo(650, 138); ctx.lineTo(765, 215);
  ctx.closePath(); ctx.fill();
  rect(540, 212, 220, 6, '#C44E4E');
  rect(626, 95, 48, 46, '#F2E0C8');
  ctx.fillStyle = '#DB6565'; ctx.beginPath();
  ctx.moveTo(620, 95); ctx.lineTo(650, 62); ctx.lineTo(680, 95);
  ctx.closePath(); ctx.fill();
  disc(650, 118, 15, 15, '#FFFFFF');
  ctx.strokeStyle = '#2E2E31'; ctx.lineWidth = 2.5; ctx.beginPath(); ctx.arc(650, 118, 15, 0, Math.PI * 2); ctx.stroke();
  disc(650, 118, 2.5, 2.5, '#2E2E31');
  rect(650, 117, 9, 2, '#2E2E31');
  rect(649, 109, 2, 9, '#2E2E31');
  for(const wx of [572, 638, 704]){
    rrect(wx, 236, 22, 30, 11); ctx.fillStyle = '#FFFFFF'; ctx.fill();
  }
  rrect(625, 280, 50, 56, 8); ctx.fillStyle = '#FFFFFF'; ctx.fill();
  rrect(630, 285, 40, 51, 4); ctx.fillStyle = '#DB6565'; ctx.fill();
  rect(649, 285, 2, 51, '#FFFFFF');

  // 6. Tree & Bushes
  disc(492, 324, 16, 16, '#02BD39');
  disc(518, 324, 18, 18, '#02BD39');
  disc(544, 324, 16, 16, '#02BD39');
  rect(500, 276, 10, 60, '#8D5733');
  disc(505, 255, 30, 30, '#02BD39');

  // 7. School Bus (left side)
  rrect(20, 250, 175, 86, 16); ctx.fillStyle = '#FFE73F'; ctx.fill();
  rrect(180, 286, 32, 50, 8); ctx.fillStyle = '#FFE73F'; ctx.fill();
  rect(24, 252, 165, 8, '#F8FF3E');
  rrect(156, 264, 28, 36, 4); ctx.fillStyle = '#B3EEF8'; ctx.fill();
  rrect(38, 264, 28, 36, 4); ctx.fillStyle = '#B3EEF8'; ctx.fill();
  rrect(75, 264, 28, 36, 4); ctx.fillStyle = '#B3EEF8'; ctx.fill();
  rrect(112, 264, 28, 36, 4); ctx.fillStyle = '#B3EEF8'; ctx.fill();
  rect(20, 308, 175, 4, '#2E2E31');
  rect(20, 321, 175, 4, '#2E2E31');
  disc(62, 336, 19, 19, '#2E2E31'); disc(62, 336, 9, 9, '#9EAAAF'); disc(62, 336, 4, 4, '#2E2E31');
  disc(168, 336, 19, 19, '#2E2E31'); disc(168, 336, 9, 9, '#9EAAAF'); disc(168, 336, 4, 4, '#2E2E31');
  rrect(202, 324, 14, 12, 3); ctx.fillStyle = '#2E2E31'; ctx.fill();
  disc(206, 302, 5, 5, '#FFFFFF');
  rect(186, 272, 8, 16, '#2E2E31'); rect(180, 280, 8, 3, '#2E2E31');

  // 8. Bus Stop Sign
  rect(222, 276, 4, 60, '#507074');
  rrect(210, 252, 28, 26, 6); ctx.fillStyle = '#00C8ED'; ctx.fill();
  rrect(213, 255, 22, 20, 3); ctx.fillStyle = '#FFFFFF'; ctx.fill();
  rrect(216, 258, 16, 11, 2); ctx.fillStyle = '#00C8ED'; ctx.fill();
  disc(219, 271, 1.5, 1.5, '#00C8ED'); disc(229, 271, 1.5, 1.5, '#00C8ED');

  // 9. Central Chunky 3D Pixel Art Text: "LEVEL"
  const letters = ['L', 'E', 'V', 'E', 'L'];
  const letW = [4, 4, 5, 4, 4];
  const letSize = 7;
  const letSpacing = 7;
  let totalLetW = 0;
  for(let i = 0; i < letters.length; i++) totalLetW += letW[i] * letSize + (i < letters.length - 1 ? letSpacing : 0);
  let curLx = WNAT / 2 - totalLetW / 2;
  const letY = 110;
  for(let i = 0; i < letters.length; i++){
    drawSplashPixelChar(SPLASH_LETTERS[letters[i]], curLx, letY, letSize, COL.hud, 4);
    curLx += letW[i] * letSize + letSpacing;
  }

  // 10. Massive Chunky 3D Pixel Art Numbers: "01" or "02"
  const numStr = lvl === 1 ? '01' : '02';
  const numSize = 10;
  const numSpacing = 18;
  const digitW = 7 * numSize;
  const totalNumW = digitW * 2 + numSpacing;
  const numX = WNAT / 2 - totalNumW / 2;
  const numY = 175;
  drawSplashPixelChar(SPLASH_DIGITS[numStr[0]], numX, numY, numSize, COL.hud, 5);
  drawSplashPixelChar(SPLASH_DIGITS[numStr[1]], numX + digitW + numSpacing, numY, numSize, COL.hud, 5);

  // 11. Green HUD Frame
  hudFrame();

  // 12. Skip prompt
  if(splashT > 25 && Math.floor(frame / 20) % 2 === 0){
    text('PRESS A TO START', WNAT / 2, HNAT - 24, 2, COL.hud, 'c', '#000');
  }
}

function renderSplash(){
  drawSplashScene(splashLevel);
}
"""

old_render_splash = """function renderSplash(){
  rect(0,0,WNAT,HNAT,'#000');
  const img=splashLevel===1?splashImg1:splashImg2;
  if(img && img.complete && img.naturalWidth>0){
    ctx.drawImage(img,0,0,WNAT,HNAT);
  }
  hudFrame();
  if(splashT>30 && Math.floor(frame/20)%2===0){
    text('PRESS A TO START',WNAT/2,HNAT-24,2,COL.hud,'c','#000');
  }
}"""

assert old_render_splash in html, "Could not find old_render_splash"
html = html.replace(old_render_splash, splash_scene_code)

# 2. Add drawing functions for Street Obstacles and Pigeon right before renderSplash
street_draw_code = """
// ================= Street Obstacles & Enemies (Level 2) =================
function drawHydrant(x, y){
  const cx = x + 16;
  rrect(x + 5, y + 8, 22, 38, 4); ctx.fillStyle = '#FC3939'; ctx.fill();
  rect(x + 3, y + 36, 26, 10, '#D32F2F');
  disc(cx, y + 8, 9, 8, '#F9D23C');
  rect(cx - 3, y, 6, 6, '#D9A21C');
  rect(x, y + 18, 6, 10, '#F9D23C'); rect(x, y + 20, 2, 6, '#D9A21C');
  rect(x + 26, y + 18, 6, 10, '#F9D23C'); rect(x + 30, y + 20, 2, 6, '#D9A21C');
  disc(cx, y + 23, 5, 5, '#F9D23C');
}

function drawBench(x, y, w = 76, h = 38){
  ctx.fillStyle = '#3F575D';
  rect(x + 8, y + 16, 6, 22); rect(x + w - 14, y + 16, 6, 22);
  rect(x + 4, y + 34, 14, 4); rect(x + w - 18, y + 34, 14, 4);
  rrect(x, y + 14, w, 7, 2); ctx.fillStyle = '#C98A4B'; ctx.fill();
  rect(x + 2, y + 14, w - 4, 2, '#E4AD70');
  rrect(x + 2, y, w - 4, 6, 2); ctx.fillStyle = '#C98A4B'; ctx.fill();
  rrect(x + 2, y + 7, w - 4, 5, 2); ctx.fillStyle = '#C98A4B'; ctx.fill();
  ctx.fillStyle = '#3F575D';
  rect(x + 12, y, 4, 14); rect(x + w - 16, y, 4, 14);
}

function drawCardboardBox(x, y, w, h){
  rrect(x, y, w, h, 3); ctx.fillStyle = '#C98A4B'; ctx.fill();
  rect(x + 2, y + 2, w - 4, 3, '#E4AD70');
  rect(x + w - 3, y + 2, 2, h - 4, '#8D5733');
  rect(x + w/2 - 4, y, 8, h, '#F3AB27');
  rect(x + w/2 - 4, y, 8, 2, '#FCEDC3');
  rect(x + 6, y + h/2 - 5, 12, 10, '#FFFFFF');
  rect(x + 8, y + h/2 - 3, 8, 2, '#333');
  rect(x + 8, y + h/2 + 1, 6, 2, '#333');
}

function drawBarrier(x, y, w = 60, h = 48){
  ctx.strokeStyle = '#8D5733'; ctx.lineWidth = 5;
  ctx.beginPath();
  ctx.moveTo(x + 10, y + h); ctx.lineTo(x + 14, y + 10); ctx.lineTo(x + 18, y + h);
  ctx.moveTo(x + w - 18, y + h); ctx.lineTo(x + w - 14, y + 10); ctx.lineTo(x + w - 10, y + h);
  ctx.stroke();
  rrect(x, y + 8, w, 18, 2); ctx.fillStyle = '#FFFFFF'; ctx.fill();
  ctx.save();
  ctx.beginPath(); rrect(x, y + 8, w, 18, 2); ctx.clip();
  ctx.fillStyle = '#FC6903';
  for(let sx = -10; sx < w + 20; sx += 16){
    ctx.beginPath();
    ctx.moveTo(x + sx, y + 26); ctx.lineTo(x + sx + 8, y + 26);
    ctx.lineTo(x + sx + 18, y + 8); ctx.lineTo(x + sx + 10, y + 8);
    ctx.closePath(); ctx.fill();
  }
  ctx.restore();
}

function drawSkateboard(x, y, w = 52, h = 22){
  ctx.fillStyle = '#03F9FC';
  ctx.beginPath();
  ctx.moveTo(x + 2, y + 4); ctx.lineTo(x + 10, y + 9);
  ctx.lineTo(x + w - 10, y + 9); ctx.lineTo(x + w - 2, y + 4);
  ctx.lineTo(x + w, y + 7); ctx.lineTo(x + w - 9, y + 13);
  ctx.lineTo(x + 9, y + 13); ctx.lineTo(x, y + 7);
  ctx.closePath(); ctx.fill();
  rect(x + 10, y + 7, w - 20, 3, '#222222');
  ctx.fillStyle = '#CCCCCC';
  rect(x + 11, y + 12, 6, 4); rect(x + w - 17, y + 12, 6, 4);
  disc(x + 14, y + 17, 4.5, 4.5, '#F9D23C');
  disc(x + w - 14, y + 17, 4.5, 4.5, '#F9D23C');
}

function drawTrashBin(x, y, w = 46, h = 58){
  rrect(x + 3, y + 12, w - 6, h - 12, 3); ctx.fillStyle = '#2C4C38'; ctx.fill();
  for(let i = 0; i < 4; i++) rect(x + 8 + i * 9, y + 16, 3, h - 20, '#1E3527');
  ctx.fillStyle = '#1D3325';
  ctx.beginPath();
  ctx.moveTo(x, y + 12); ctx.quadraticCurveTo(x + w / 2, y, x + w, y + 12);
  ctx.closePath(); ctx.fill();
  rrect(x, y + 10, w, 5, 2); ctx.fillStyle = '#3B634B'; ctx.fill();
}

function drawPigeon(x, y, vx){
  const dir = vx < 0 ? -1 : 1;
  ctx.save();
  ctx.translate(R(x), R(y));
  ctx.scale(dir, 1);
  const flap = Math.sin(frame * 0.25) * 8;
  disc(0, 0, 14, 10, '#878787');
  disc(10, -4, 8, 7, '#757575');
  disc(6, -2, 4, 4, '#03B733');
  disc(13, -5, 1.5, 1.5, '#FC3939');
  ctx.fillStyle = '#F3AB27'; ctx.beginPath();
  ctx.moveTo(17, -5); ctx.lineTo(23, -3); ctx.lineTo(17, -2); ctx.closePath(); ctx.fill();
  ctx.fillStyle = '#555555'; ctx.beginPath();
  ctx.moveTo(-4, -2); ctx.lineTo(-14, -8 + flap); ctx.lineTo(2, -2 + flap * 0.5); ctx.closePath(); ctx.fill();
  rect(-18, -3, 8, 4, '#555555');
  ctx.restore();
}
"""

html = html.replace("// ================= Faithful Native Recreation of Splash Screens =================", street_draw_code + "\n// ================= Faithful Native Recreation of Splash Screens =================")

# 3. Update enemyBox and stepEnemies for pigeon
old_enemy_box = """function enemyBox(e){
  if(e.t==='plane') return {x:e.x-20, y:e.y-12, w:40, h:20};
  return e.t==='eraser'?{x:e.x-17,y:e.y-22,w:34,h:22}:{x:e.x-9,y:e.y-42,w:18,h:42};
}
function stepEnemies(){
  const D=curDiff();
  for(const e of enemies){
    if(!e.alive){ if(e.dead>0) e.dead--; continue; }
    const tgt=nearestPlayer(e.x); if(!tgt || Math.abs(e.x-tgt.b.x)>900) continue;   // asleep off-screen
    if(e.t==='plane'){
      e.x+=e.vx*D.enemy;
      e.y=e.baseY+Math.sin(frame*0.08+e.x*0.02)*8;
      if(e.x<e.minX||e.x>e.maxX) e.vx*=-1;
    } else if(e.t==='eraser'){"""

new_enemy_box = """function enemyBox(e){
  if(e.t==='plane'||e.t==='pigeon') return {x:e.x-20, y:e.y-12, w:40, h:20};
  return e.t==='eraser'?{x:e.x-17,y:e.y-22,w:34,h:22}:{x:e.x-9,y:e.y-42,w:18,h:42};
}
function stepEnemies(){
  const D=curDiff();
  for(const e of enemies){
    if(!e.alive){ if(e.dead>0) e.dead--; continue; }
    const tgt=nearestPlayer(e.x); if(!tgt || Math.abs(e.x-tgt.b.x)>900) continue;   // asleep off-screen
    if(e.t==='plane'||e.t==='pigeon'){
      e.x+=e.vx*D.enemy;
      e.y=e.baseY+Math.sin(frame*0.08+e.x*0.02)*8;
      if(e.x<e.minX||e.x>e.maxX) e.vx*=-1;
    } else if(e.t==='eraser'){"""

assert old_enemy_box in html, "Could not find old_enemy_box"
html = html.replace(old_enemy_box, new_enemy_box)

# 4. In drawEnemy, add pigeon
old_draw_enemy_plane = """  if(e.t==='plane'){
    drawPaperPlane(x,e.y,e.vx);
    return;
  }"""

new_draw_enemy_plane = """  if(e.t==='plane'){
    drawPaperPlane(x,e.y,e.vx);
    return;
  }
  if(e.t==='pigeon'){
    drawPigeon(x,e.y,e.vx);
    return;
  }"""

assert old_draw_enemy_plane in html, "Could not find old_draw_enemy_plane"
html = html.replace(old_draw_enemy_plane, new_draw_enemy_plane)

# 5. In buildLevel(2), introduce creative natural street obstacles and flying pigeons
old_build_level_2 = """    // Level 2 (Main Street — exact original level)
    LEVEL_LEN = LEVEL_LEN_2; ARENA_X = ARENA_X_2; CHECKPOINT_X = CHECKPOINT_X_2;
    leftWall = 0; rightWall = LEVEL_LEN_2;
    for(const [x, n] of CRATE_COLS) for(let k = 0; k < n; k++) crates.push({t: 'crate', x, y: FEET - CR * (k + 1), w: CR, h: CR});
    enemies = [
      {t:'eraser',x:1500,minX:1300,maxX:1850},{t:'pencil',x:2150},{t:'eraser',x:2900,minX:2700,maxX:3150},
      {t:'pencil',x:3050},{t:'eraser',x:4000,minX:3750,maxX:4300},{t:'eraser',x:4200,minX:3800,maxX:4500},
      {t:'pencil',x:4400},{t:'pencil',x:5300},{t:'eraser',x:5450,minX:5200,maxX:5560},{t:'pencil',x:5750},
    ].map(e=>({...e, y:FEET, vx:e.t==='eraser'?-0.8:0, vy:0, alive:true, hop:60+Math.random()*60, dead:0}));"""

new_build_level_2 = """    // Level 2 (Main Street — Creative & Natural Street Obstacles)
    LEVEL_LEN = LEVEL_LEN_2; ARENA_X = ARENA_X_2; CHECKPOINT_X = CHECKPOINT_X_2;
    leftWall = 0; rightWall = LEVEL_LEN_2;

    // 1. Skateboards on curb (w: 52, h: 22)
    for(const sx of [520, 2140, 3960, 4520, 5840]) crates.push({t: 'skateboard', x: sx, y: FEET - 22, w: 52, h: 22});

    // 2. Fire Hydrants (w: 32, h: 46)
    for(const hx of [820, 1960, 3220, 4720, 5600]) crates.push({t: 'hydrant', x: hx, y: FEET - 46, w: 32, h: 46});

    // 3. Wooden Park Benches (w: 76, h: 38)
    for(const bx of [1420, 2600, 3720, 5320]) crates.push({t: 'bench', x: bx, y: FEET - 38, w: 76, h: 38});

    // 4. Street Construction Barriers (w: 60, h: 48)
    for(const rx of [2860, 4240, 5740]) crates.push({t: 'barrier', x: rx, y: FEET - 48, w: 60, h: 48});

    // 5. City Metal Trash Bins (w: 46, h: 58)
    for(const tx of [1720, 3100, 4480]) crates.push({t: 'trashbin', x: tx, y: FEET - 58, w: 46, h: 58});

    // 6. Cardboard Delivery Boxes (stacks)
    const boxes = [
      {x: 1120, h: 48}, {x: 1176, h: 96},
      {x: 2320, h: 48}, {x: 2376, h: 96}, {x: 2432, h: 144},
      {x: 3476, h: 48}, {x: 3532, h: 96}, {x: 3588, h: 144},
      {x: 4776, h: 96}, {x: 5020, h: 48}, {x: 5076, h: 144},
      {x: 5900, h: 96}
    ];
    for(const b of boxes) crates.push({t: 'box', x: b.x, y: FEET - b.h, w: 48, h: b.h});

    // 7. Wooden Crates in Arena & key points
    crates.push({t: 'crate', x: ARENA_X_2 + 60, y: FEET - CR * 2, w: CR, h: CR * 2});
    crates.push({t: 'crate', x: ARENA_X_2 + WNAT - 60 - CR, y: FEET - CR * 2, w: CR, h: CR * 2});
    crates.push({t: 'crate', x: 3276, y: FEET - CR, w: CR, h: CR});

    // Enemies: Patrolling erasers, bouncing pencils, and street pigeons!
    enemies = [
      {t:'eraser',x:1500,minX:1300,maxX:1850},
      {t:'pencil',x:2150},
      {t:'pigeon',x:1750,baseY:FEET-72,vx:-1.6,minX:1400,maxX:2100},
      {t:'eraser',x:2900,minX:2700,maxX:3150},
      {t:'pencil',x:3050},
      {t:'pigeon',x:2850,baseY:FEET-80,vx:-1.8,minX:2500,maxX:3200},
      {t:'eraser',x:4000,minX:3750,maxX:4300},
      {t:'eraser',x:4200,minX:3800,maxX:4500},
      {t:'pigeon',x:4100,baseY:FEET-75,vx:-1.7,minX:3700,maxX:4400},
      {t:'pencil',x:4400},
      {t:'pencil',x:5300},
      {t:'pigeon',x:5200,baseY:FEET-70,vx:-1.9,minX:4800,maxX:5500},
      {t:'eraser',x:5450,minX:5200,maxX:5560},
      {t:'pencil',x:5750},
    ].map(e=>({...e, y:FEET, vx:e.vx||(e.t==='eraser'?-0.8:0), vy:0, alive:true, hop:60+Math.random()*60, dead:0}));"""

assert old_build_level_2 in html, "Could not find old_build_level_2"
html = html.replace(old_build_level_2, new_build_level_2)

# 6. In renderPlay(), update crate drawing to include all street obstacles
old_crate_render = """      if(c.t==='cubby') drawCubby(c.x-camX,c.y,c.w,c.h);
      else if(c.t==='trash') drawTrashCan(c.x-camX,c.y,c.w,c.h);
      else if(c.t==='book') drawBookStack(c.x-camX,c.y,c.w,c.h);
      else if(c.t==='locker') drawLocker(c.x-camX,c.y,c.w,c.h);
      else if(c.t==='cone') drawCone(c.x-camX,c.y,c.w,c.h);
      else drawCrate(R(c.x-camX),c.y);"""

new_crate_render = """      if(c.t==='cubby') drawCubby(c.x-camX,c.y,c.w,c.h);
      else if(c.t==='trash') drawTrashCan(c.x-camX,c.y,c.w,c.h);
      else if(c.t==='book') drawBookStack(c.x-camX,c.y,c.w,c.h);
      else if(c.t==='locker') drawLocker(c.x-camX,c.y,c.w,c.h);
      else if(c.t==='cone') drawCone(c.x-camX,c.y,c.w,c.h);
      else if(c.t==='hydrant') drawHydrant(c.x-camX,c.y);
      else if(c.t==='bench') drawBench(c.x-camX,c.y,c.w,c.h);
      else if(c.t==='box') drawCardboardBox(c.x-camX,c.y,c.w,c.h);
      else if(c.t==='barrier') drawBarrier(c.x-camX,c.y,c.w,c.h);
      else if(c.t==='skateboard') drawSkateboard(c.x-camX,c.y,c.w,c.h);
      else if(c.t==='trashbin') drawTrashBin(c.x-camX,c.y,c.w,c.h);
      else drawCrate(R(c.x-camX),c.y);"""

assert old_crate_render in html, "Could not find old_crate_render"
html = html.replace(old_crate_render, new_crate_render)

# 7. Update Level 1 exit sequence: mouse enters doorway threshold, hops into sunlight, and fades out through the door
old_exit_logic = """    if(!level1ExitActive && maxX>EXIT_DOOR_X-120){
      level1ExitActive=true; level1ExitTimer=0;
    }
    if(level1ExitActive){
      level1ExitTimer++;
      for(const p of live){
        if(p.b.x<EXIT_DOOR_X-30){ p.b.vx=2.0; p.b.face=1; }
        else { p.b.vx=0; }
      }
      if(level1ExitTimer===50){
        for(const p of live){ if(p.b.ground) p.b.vy=-8.5; }
        sfx('jump'); sfx('trophy');
        trophies[3]=true;
        addScore(2000,EXIT_DOOR_X,FEET-140);
        for(const p of live) addScore(500*p.lives);
        for(let i=0;i<40;i++) confetti.push({x:WNAT/2+(Math.random()-0.5)*300,y:-10,vx:(Math.random()-0.5)*3,vy:1+Math.random()*3,r:0,vr:0.1,c:COL.hud,s:'r',w:8});
      }
      if(level1ExitTimer>80){
        for(const p of live) p.b.vx=3.6;
      }
      if(level1ExitTimer>=150){
        level1ExitActive=false;
        triggerSplash(2);
        return;
      }
    }"""

new_exit_logic = """    if(!level1ExitActive && maxX>EXIT_DOOR_X-120){
      level1ExitActive=true; level1ExitTimer=0;
    }
    if(level1ExitActive){
      level1ExitTimer++;
      const doorCenterX = EXIT_DOOR_X + 65;

      if(level1ExitTimer < 50){
        // Gather in front of the door
        for(let k=0; k<live.length; k++){
          const p = live[k], targetX = EXIT_DOOR_X + 35 + k * 26;
          p.b.vx = Math.sign(targetX - p.b.x) * Math.min(2.0, Math.abs(targetX - p.b.x) * 0.15);
          if(Math.abs(p.b.x - targetX) < 2){ p.b.x = targetX; p.b.vx = 0; p.b.face = 1; }
        }
      } else if(level1ExitTimer === 50){
        // Doors swing open! Victory jump & fanfare!
        for(const p of live){ if(p.b.ground) p.b.vy = -8.5; p.b.vx = 0; }
        sfx('jump'); sfx('trophy');
        trophies[3] = true;
        addScore(2000, EXIT_DOOR_X, FEET - 140);
        for(const p of live) addScore(500 * p.lives);
        for(let i=0; i<40; i++) confetti.push({x: WNAT/2+(Math.random()-0.5)*300, y: -10, vx: (Math.random()-0.5)*3, vy: 1+Math.random()*3, r: 0, vr: 0.1, c: COL.hud, s: 'r', w: 8});
      } else if(level1ExitTimer > 80 && level1ExitTimer <= 130){
        // Step directly into the open doorway threshold!
        for(const p of live){
          p.b.vx = (doorCenterX - p.b.x) * 0.12;
          p.b.face = 1;
          p.exitFade = Math.max(0, 1 - (level1ExitTimer - 85) / 35);
          p.exitScale = Math.max(0.4, 1 - (level1ExitTimer - 85) * 0.015);
        }
      } else if(level1ExitTimer > 130){
        for(const p of live){
          p.b.vx = 0;
          p.exitFade = 0; // completely outside!
        }
      }

      if(level1ExitTimer >= 155){
        level1ExitActive = false;
        for(const p of live){ p.exitFade = undefined; p.exitScale = undefined; }
        triggerSplash(2);
        return;
      }
    }"""

assert old_exit_logic in html, "Could not find old_exit_logic"
html = html.replace(old_exit_logic, new_exit_logic)

# 8. In drawPlayers(), support exitFade and exitScale
old_draw_players = """function drawPlayers(){
  const multi=players.length>1;
  // draw back-to-front so nobody hides behind a later player's tail
  [...players].map((p,k)=>({p,k})).sort((a,b)=>a.p.b.y-b.p.b.y).forEach(({p,k})=>{
    if(p.out) return;
    const b=p.b; shadowAt(b.x,b.y,26);
    const blink=b.inv>0 && Math.floor(b.inv/4)%2===0;
    drawMouse(p.id,b.x,b.y,b.face,mouseFrame(b),blink?0.35:1,k*2);
    if(multi){
      const h=SPR[p.id+'_idle'].height, tx=b.x-camX, ty=b.y-h-14;
      text('P'+(k+1),tx,ty,2,PCOL[k],'c','#000');
      ctx.fillStyle=PCOL[k]; ctx.beginPath(); ctx.moveTo(R(tx-4),R(ty+12)); ctx.lineTo(R(tx+4),R(ty+12)); ctx.lineTo(R(tx),R(ty+16)); ctx.fill();
    }
  });
}"""

new_draw_players = """function drawPlayers(){
  const multi=players.length>1;
  // draw back-to-front so nobody hides behind a later player's tail
  [...players].map((p,k)=>({p,k})).sort((a,b)=>a.p.b.y-b.p.b.y).forEach(({p,k})=>{
    if(p.out) return;
    const fade = p.exitFade !== undefined ? p.exitFade : 1;
    if(fade <= 0) return; // Stepped through the door!
    const b=p.b;
    const sc = p.exitScale !== undefined ? p.exitScale : 1;
    ctx.save();
    if(sc !== 1){
      ctx.translate(R(b.x - camX), R(b.y));
      ctx.scale(sc, sc);
      ctx.translate(-R(b.x - camX), -R(b.y));
    }
    shadowAt(b.x, b.y, 26 * fade);
    const blink=b.inv>0 && Math.floor(b.inv/4)%2===0;
    const alpha=(blink?0.35:1) * fade;
    drawMouse(p.id,b.x,b.y,b.face,mouseFrame(b),alpha,k*2);
    if(multi && fade > 0.3){
      const h=SPR[p.id+'_idle'].height, tx=b.x-camX, ty=b.y-h-14;
      text('P'+(k+1),tx,ty,2,PCOL[k],'c','#000');
      ctx.fillStyle=PCOL[k]; ctx.beginPath(); ctx.moveTo(R(tx-4),R(ty+12)); ctx.lineTo(R(tx+4),R(ty+12)); ctx.lineTo(R(tx),R(ty+16)); ctx.fill();
    }
    ctx.restore();
  });
}"""

assert old_draw_players in html, "Could not find old_draw_players"
html = html.replace(old_draw_players, new_draw_players)

with open('index.html', 'w') as f:
    f.write(html)

print('Updated index.html with all refinements, length:', len(html))
