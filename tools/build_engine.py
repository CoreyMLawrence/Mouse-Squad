import sys, re

def build():
    with open('../index.html', 'r') as f:
        html = f.read()
        
    with open('assets.js', 'r') as f:
        assets_js = f.read()
        
    # 1. Replace ASSETS
    html = re.sub(r'const ASSETS = \{.*?\n\};\n', assets_js, html, flags=re.DOTALL)
    
    # 2. Replace decode function
    new_decode = """function decode(s){
  const c = document.createElement('canvas');
  c.width = s.w; c.height = s.h;
  const g = c.getContext('2d');
  const img = g.createImageData(s.w, s.h);
  
  if (s.rle) {
    const raw = atob(s.rle);
    let i = 0, px = 0;
    while(i < raw.length) {
      const val = raw.charCodeAt(i++);
      const count = raw.charCodeAt(i++);
      for(let k=0; k<count; k++) {
        if(val !== 255) {
          const o = px * 4;
          const p = s.pal[val];
          img.data[o]=p[0]; img.data[o+1]=p[1]; img.data[o+2]=p[2]; img.data[o+3]=255;
        }
        px++;
      }
    }
  } else {
    for(let y=0;y<s.h;y++)for(let x=0;x<s.w;x++){
      const k = s.px[y][x];
      if(k<0) continue;
      const o = (y*s.w+x)*4, p = s.pal[k];
      img.data[o]=p[0]; img.data[o+1]=p[1]; img.data[o+2]=p[2]; img.data[o+3]=255;
    }
  }
  g.putImageData(img,0,0);
  return c;
}

const flip = (c) => {
  const fc = document.createElement('canvas');
  fc.width = c.width; fc.height = c.height;
  const fg = fc.getContext('2d');
  fg.translate(c.width, 0); fg.scale(-1, 1);
  fg.drawImage(c, 0, 0);
  return fc;
};

const SPR = {};
for(const k in ASSETS) {
  SPR[k] = decode(ASSETS[k]);
  SPR[k+'_flip'] = flip(SPR[k]);
}
"""
    html = re.sub(r'function decode\(s\)\{.*?const SPR = \{.*?\n\};\n', new_decode, html, flags=re.DOTALL)
    
    # 3. Replace map definitions and globals
    new_map = """// ---------- world ----------
const T = 12; // 12x12 native tiles
const MAP_WIDTH = 120;
const MAP_HEIGHT = 18;
const LEVEL = [];
for(let j=0; j<MAP_HEIGHT; j++) {
  const row = [];
  for(let i=0; i<MAP_WIDTH; i++) {
    if(j >= 15) row.push(1);
    else row.push(0);
  }
  LEVEL.push(row);
}

for(let i=10; i<15; i++) LEVEL[12][i] = 1;
for(let i=20; i<25; i++) LEVEL[10][i] = 1;
for(let i=35; i<42; i++) LEVEL[13][i] = 1;

let NI=MAP_WIDTH, NJ=MAP_HEIGHT;
let WNAT=384, HNAT=216; // Camera size
let GRID=LEVEL;

const solidCell = (i,j) => (i<0||j<0||i>=NI||j>=NJ) ? true : GRID[j][i]===1;

let camX = 0;

function setWorld(grid) {
  GRID = grid; NJ = grid.length; NI = grid[0].length;
  cv.width = WNAT; cv.height = HNAT;
  ctx.imageSmoothingEnabled = false;
  fit();
}
"""
    html = re.sub(r'// ---------- world ----------.*?// ---------- canvas ----------', new_map + '\n// ---------- canvas ----------', html, flags=re.DOTALL)
    
    # 4. Replace physics
    start_str = "class Walker"
    end_str = "// ---------- ring AI ----------"
    start_idx = html.find(start_str)
    end_idx = html.find(end_str)
    
    new_physics = """// ---------- AABB platformer physics ----------
class Body{
  constructor(x,y){
    this.x=x; this.y=y;               
    this.vx=0; this.vy=0;             
    this.w=16; this.h=32;
    this.face=1;                      
    this.air=false;
    this.animT=0;
    this.animState='idle';
    this.jheld=false;
    this.coyote=0;
    this.jumpBuf=0;
  }
  
  step(pad){
    const MAX_RUN=1.9, ACC=0.12, FRIC=0.80, SKID=0.30;
    const JUMP=4.2, GRAV_UP=0.13, GRAV_DN=0.30, TERM=4.5, AIR_CTRL=0.10;
    
    if(this.air){
      this.vy += (this.vy < 0 && this.jheld) ? GRAV_UP : GRAV_DN;
      if(this.vy > TERM) this.vy = TERM;
    } else {
      this.vy = 0;
      this.coyote = 6;
    }
    
    pad.prevJump = pad.prevJump || false;
    const justJump = pad.jump && !pad.prevJump;
    if(justJump) this.jumpBuf = 6;
    pad.prevJump = pad.jump;
    
    if(this.jumpBuf > 0 && this.coyote > 0){
      this.vy = -JUMP;
      this.air = true;
      this.coyote = 0;
      this.jumpBuf = 0;
    }
    if(this.jumpBuf > 0) this.jumpBuf--;
    if(this.coyote > 0) this.coyote--;
    
    this.jheld = pad.jump;
    
    let ix = pad.gx;
    if(ix !== 0){
      this.face = ix;
      let acc = this.air ? AIR_CTRL : (Math.sign(this.vx) !== ix ? SKID : ACC);
      this.vx += ix * acc;
      if(this.vx > MAX_RUN) this.vx = MAX_RUN;
      if(this.vx < -MAX_RUN) this.vx = -MAX_RUN;
      this.animState = 'walk';
    } else {
      if(!this.air) this.vx *= FRIC;
      if(Math.abs(this.vx) < 0.1) this.vx = 0;
      this.animState = 'idle';
    }
    if(this.air) this.animState = 'jump';
    
    // Y Collision
    this.y += this.vy;
    let head = Math.floor((this.y - this.h)/T);
    let feet = Math.floor(this.y/T);
    let l = Math.floor((this.x - this.w/2 + 1)/T);
    let r = Math.floor((this.x + this.w/2 - 1)/T);
    
    this.air = true;
    if(this.vy > 0) { // falling
      if(solidCell(l, feet) || solidCell(r, feet)){
        this.y = feet * T;
        this.vy = 0;
        this.air = false;
      }
    } else if(this.vy < 0) { // jumping up
      if(solidCell(l, head) || solidCell(r, head)){
        this.y = (head + 1) * T + this.h;
        this.vy = 0;
      }
    }
    
    // X Collision
    this.x += this.vx;
    head = Math.floor((this.y - this.h + 1)/T);
    feet = Math.floor((this.y - 1)/T);
    l = Math.floor((this.x - this.w/2)/T);
    r = Math.floor((this.x + this.w/2)/T);
    
    if(this.vx > 0){ // moving right
      if(solidCell(r, head) || solidCell(r, feet)){
        this.x = r * T - this.w/2;
        this.vx = 0;
      }
    } else if(this.vx < 0){ // moving left
      if(solidCell(l, head) || solidCell(l, feet)){
        this.x = (l + 1) * T + this.w/2;
        this.vx = 0;
      }
    }
    
    if(this.x < this.w/2) { this.x = this.w/2; this.vx = 0; }
    if(this.x > NI*T - this.w/2) { this.x = NI*T - this.w/2; this.vx = 0; }
    
    this.animT++;
  }
}
"""
    html = html[:start_idx] + new_physics + html[end_idx:]
    html = html.replace('new Walker', 'new Body')
    
    # Boss logic
    html = html.replace('function ringStep(){', 'function bossStep(){\n  ring.x = camX + WNAT - 40; // Boss chases from right\n  ring.y = Math.sin(Date.now()/200)*10 + HNAT/2;\n  return; // Skip old logic\n')
    html = html.replace('ringStep()', 'bossStep()')
    
    draw_boss = '''
    if (SPR.boss_body_angry) {
      ctx.drawImage(SPR.boss_body_angry, Math.round(rx - SPR.boss_body_angry.width/2) - camX, Math.round(ry - SPR.boss_body_angry.height/2));
      if (SPR.boss_propeller) {
         ctx.drawImage(SPR.boss_propeller, Math.round(rx - SPR.boss_propeller.width/2) - camX, Math.round(ry - SPR.boss_body_angry.height/2 - 20));
      }
    }
'''
    html = re.sub(r'ctx\.drawImage\(SPR\.ring,.*?\);', draw_boss, html)
    
    # 5. Fix rendering
    draw_fix = """function drawActor(body, colorStr){
  if(!body) return;
  let spr_name = colorStr + '_' + body.animState;
  if(body.animState === 'walk'){
     spr_name = colorStr + '_walk' + (Math.floor(body.animT / 8) % 2 + 1);
  }
  let s = SPR[spr_name];
  if(!s) s = SPR[colorStr + '_idle']; // fallback
  if(!s) return;
  
  if(body.face < 0){
    s = SPR[spr_name + '_flip'] || s;
  }
  
  ctx.save();
  ctx.translate(Math.round(body.x) - camX, Math.round(body.y));
  ctx.drawImage(s, -s.width/2, -s.height);
  ctx.restore();
}

function drawLevel() {
  ctx.fillStyle = '#476566'; // Sky color
  ctx.fillRect(0, 0, WNAT, HNAT);
  
  if(SPR.scenery_2x){
    let bgX = (camX * 0.5) % SPR.scenery_2x.width;
    ctx.drawImage(SPR.scenery_2x, -bgX, HNAT - 48 - SPR.scenery_2x.height);
    ctx.drawImage(SPR.scenery_2x, -bgX + SPR.scenery_2x.width, HNAT - 48 - SPR.scenery_2x.height);
  }
  
  ctx.fillStyle = '#38544a'; // Grass line
  ctx.fillRect(0, HNAT-48, WNAT, 48);
  
  ctx.fillStyle = '#02c136'; // Road/blocks
  const startCol = Math.floor(camX / T);
  const endCol = startCol + (WNAT / T) + 1;
  
  for(let j=0; j<NJ; j++){
    for(let i=startCol; i<endCol; i++){
      if(solidCell(i, j)){
        ctx.fillRect(i*T - camX, j*T, T, T);
      }
    }
  }
}
"""
    s2 = html.find('function drawWalker')
    e2 = html.find('// ---------- fixed-timestep loop')
    html = html[:s2] + draw_fix + '\n' + html[e2:]
    
    # Fix the draw call in the play state
    html = html.replace('drawWalker(player, P1S.a, P1S.b, null, P1S.vis);', "drawActor(player, p1Char);")
    html = html.replace('if(tbs) drawWalker(null,SPR.blueA,SPR.blueB,tbs,blueVis);', '')
    html = html.replace('drawWalker(null,SPR.redA,SPR.redB, {x:LAY.spawn.x*T,y:LAY.spawn.y*T,n:{x:0,y:-1},face:1,animT:0}, redVis);', '')
    html = html.replace('drawWalker(blueW, P2S.a, P2S.b, null, P2S.vis);', "drawActor(blueW, 'yellow');")
    html = html.replace('if(bs) drawWalker(null, P2S.a, P2S.b, bs, P2S.vis);', '')
    html = html.replace('else drawWalker(null, P2S.a, P2S.b, {x:LAY.blueIdle.x*T,y:LAY.blueIdle.y*T,n:{x:0,y:-1},face:1,animT:0}, P2S.vis);', '')
    
    # 6. Inject level drawing and camera logic into the frame tick
    tick_start = html.find("function tick(){")
    tick_logic = """function tick(){
  // Camera follow
  if(state==='play'){
    camX = player.x - WNAT/2;
    if(camX < 0) camX = 0;
    if(camX > NI*T - WNAT) camX = NI*T - WNAT;
  }
  drawLevel();
"""
    html = html.replace("function tick(){", tick_logic)
    
    html = re.sub(r'ctx\.fillStyle = BG;.*?ctx\.fillRect\(0,0,WNAT,HNAT\);', '', html, flags=re.DOTALL)
    html = re.sub(r'for\(let j=0;j<NJ;j\+\+\)for\(let i=0;i<NI;i\+\+\).*?ctx\.fillRect\(i\*T,j\*T,T,T\);\s*\}', '', html, flags=re.DOTALL)
    
    # Reset modifications
    html = html.replace('player.x=LAY.spawn.x*T; player.y=LAY.spawn.y*T; player.n={x:0,y:-1}; player.v=0; player.air=false;', 'player = new Body(100, 100);')
    html = re.sub(r'LAY\.[a-zA-Z]+\.x\*T', '120', html)
    html = re.sub(r'LAY\.[a-zA-Z]+\.y\*T', '100', html)
    html = html.replace('LAY.ringCell.i', '30').replace('LAY.ringCell.j', '10')
    html = html.replace('let charSel=0;', 'let charSel=1;')
    
    # Catch logic
    s3 = html.find('// catch check:')
    e3 = html.find('        if(music&&!music.muted) jingle();')
    new_catch = '''// Level end check
    if(player.x > (NI-4) * T){
        state='won';
        winFx={x:player.x, y:player.y, t:0, holder:player};
        if(music&&!music.muted) jingle();
'''
    html = html[:s3] + new_catch + html[e3:]
    html = html.replace('jingle();\n        break;\n      }\n    }', 'jingle();\n    }')
    
    # Win render state
    s4 = html.find("if(state==='won'){")
    e4 = html.find("// ---------- audio (Web Audio API) ----------")
    new_win = '''if(state==='won'){
    // Darken background
    ctx.fillStyle = 'rgba(0,0,0,0.5)';
    ctx.fillRect(0,0,WNAT,HNAT);
    
    // Draw Victory UI
    if(SPR.victory_overlay){
        ctx.drawImage(SPR.victory_overlay, 0, 0);
    }
}
'''
    html = html[:s4] + new_win + html[e4:]
    
    # Character select screen
    s5 = html.find('function drawTitle(){')
    e5 = html.find('function padEdges(){')
    new_title = '''function drawTitle(){
  // Character Select Screen
  ctx.fillStyle = '#000';
  ctx.fillRect(0,0,WNAT,HNAT);
  
  ctx.strokeStyle = '#222';
  ctx.lineWidth = 1;
  for(let x=0; x<WNAT; x+=24) { ctx.beginPath(); ctx.moveTo(x,0); ctx.lineTo(x,HNAT); ctx.stroke(); }
  for(let y=0; y<HNAT; y+=24) { ctx.beginPath(); ctx.moveTo(0,y); ctx.lineTo(WNAT,y); ctx.stroke(); }
  
  ctx.fillStyle = '#0f0';
  ctx.font = '20px monospace';
  ctx.textAlign = 'center';
  ctx.fillText('CHOOSE YOUR MOUSE', WNAT/2, 40);
  
  const mice = ['pink', 'cyan', 'yellow'];
  const colors = ['#ff00ff', '#00ffff', '#ffff00'];
  
  for(let i=0; i<3; i++) {
    const x = WNAT/4 * (i+1);
    const y = HNAT/2 + 20;
    
    ctx.fillStyle = colors[i];
    ctx.beginPath();
    ctx.ellipse(x, y + 20, 25, 8, 0, 0, Math.PI*2);
    ctx.fill();
    
    if(charSel === i){
       ctx.strokeStyle = '#fff';
       ctx.lineWidth = 3;
       ctx.stroke();
    }
    
    const spr = SPR[mice[i] + '_idle'];
    if(spr) {
       ctx.drawImage(spr, x - spr.width/2, y - spr.height/2 + (charSel===i ? Math.sin(Date.now()/100)*3 : 0));
    }
  }
  
  ctx.fillStyle = '#fff';
  ctx.font = '12px monospace';
  if(Math.floor(Date.now()/500)%2===0) {
    ctx.fillText('PRESS JUMP TO START', WNAT/2, HNAT - 30);
  }
}

function titleUpdate(){
  if(pad.gx === 1 && (!padPrev || !padPrev.gx)) charSel = (charSel + 1) % 3;
  if(pad.gx === -1 && (!padPrev || !padPrev.gx)) charSel = (charSel + 2) % 3;
  if(pad.jump && (!padPrev || !padPrev.jump)) {
     p1Char = ['pink', 'cyan', 'yellow'][charSel];
     beginPlay(1);
  }
}
'''
    html = html[:s5] + new_title + html[e5:]

    with open('index.html', 'w') as f:
        f.write(html)
        
    print("Rebuilt index.html safely.")

if __name__ == '__main__':
    build()
