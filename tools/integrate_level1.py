import sys, re, subprocess

with open('index.html.bak-level1', 'r') as f:
    html = f.read()

# 1. Add splash_data.js script tag before the main <script> tag
if 'splash_data.js' not in html:
    html = html.replace('<script>\nconst ASSETS =', '<script src="splash_data.js"></script>\n<script>\nconst ASSETS =')

# 2. Add splash images initialization right after ASSETS decoding setup (e.g. after SPRL definition)
splash_init = """
// ---------- splash screens (LEVEL 01 & LEVEL 02) ----------
const splashImg1 = new Image();
splashImg1.src = typeof SPLASH_1_DATA !== 'undefined' ? SPLASH_1_DATA : 'art/splash_1_768.png';
const splashImg2 = new Image();
splashImg2.src = typeof SPLASH_2_DATA !== 'undefined' ? SPLASH_2_DATA : 'art/splash_2_768.png';
let splashLevel = 1, splashT = 0;
"""

if 'splashImg1' not in html:
    target = "SPR.boss_flash=tinted(SPR.boss_angry,'#ffffff',0.85); SPRL.boss_flash=flipped(SPR.boss_flash);\nfor(const k of ['party_p','party_c','party_y']) SPR[k+'_ko']=tinted(SPR[k],'#2a2a2a');"
    assert target in html, "Could not find SPR.boss_flash target"
    html = html.replace(target, target + "\n" + splash_init)

# 3. Add school palette colors to COL
school_colors = """  // school hallway palette (from concept art)
  hallWall:'#68D7D1', hallWallDk:'#56BEB8', hallFloor:'#E2E4BC', hallGrout:'#D3D5A8',
  hallTrim:'#F4EDE3', hallTrimBorder:'#B6EAE2', hallLamp:'#386872', hallLampDk:'#2B535B',
  schoolDoor:'#DB5C66', schoolDoorWin:'#BCE8F6', schoolDoorHandle:'#E8C06C',
  cubby:'#D96D69', cubbyDk:'#A3433E', cubbyHi:'#EE8581',
  trashBlue:'#285BE6', trashDk:'#1D49BF', trashHi:'#4D7DF2',
  bpBlue:'#2882EB', bpGreen:'#7BD42A', bpPurple:'#9C40D6',
  juiceBox:'#FFB000', juiceDk:'#DF9A03', juiceHi:'#FEB100',
  cautionYellow:'#FEE12B',"""

if 'hallWall' not in html:
    target = "  magenta:'#FC03A5', cyan:'#03F9FC', yellow:'#F9FC39',\n};"
    assert target in html, "Could not find COL target"
    html = html.replace(target, "  magenta:'#FC03A5', cyan:'#03F9FC', yellow:'#F9FC39',\n" + school_colors + "\n};")

# 4. Replace level definitions and buildLevel
old_level_section = """// ================= level: "Main Street" =================
const LEVEL_LEN=7200, ARENA_X=LEVEL_LEN-WNAT, CHECKPOINT_X=6150;
const CR=56;                                   // crate size
const MICE=['pink','cyan','yellow'];
const MOUSE_STATS={                            // small personality differences
  pink:  {jv:11.3, maxv:3.0, dbl:false, tail:'#878787'},   // jumps highest
  cyan:  {jv:10.5, maxv:3.6, dbl:false, tail:'#696969'},   // runs fastest
  yellow:{jv:10.4, maxv:3.1, dbl:true,  tail:'#45453F'},   // double jump
};
const PARTY_ICON={pink:'party_p',cyan:'party_c',yellow:'party_y'};
const META=ASSETS._meta;
// crate columns: [x, height-in-crates]
const CRATE_COLS=[[820,1],[1120,1],[1176,2],[1960,1],[2320,1],[2376,2],[2432,3],[3220,2],[3276,1],
  [3420,1],[3476,2],[3532,3],[3588,3],[4720,1],[4776,2],[5020,1],[5076,3],[5600,1],[5900,2],
  [ARENA_X+60,2],[ARENA_X+WNAT-60-CR,2]];
const TREES=[150,700,1500,2150,2900,3800,4450,5300,6000];
const SIGNS=[420,2650,4100,CHECKPOINT_X];
let crates=[], enemies=[], pickups=[], fx=[], shots=[];
function buildLevel(){
  crates=[];
  for(const [x,n] of CRATE_COLS) for(let k=0;k<n;k++) crates.push({x, y:FEET-CR*(k+1), w:CR, h:CR});
  enemies=[
    {t:'eraser',x:1500,minX:1300,maxX:1850},{t:'pencil',x:2150},{t:'eraser',x:2900,minX:2700,maxX:3150},
    {t:'pencil',x:3050},{t:'eraser',x:4000,minX:3750,maxX:4300},{t:'eraser',x:4200,minX:3800,maxX:4500},
    {t:'pencil',x:4400},{t:'pencil',x:5300},{t:'eraser',x:5450,minX:5200,maxX:5560},{t:'pencil',x:5750},
  ].map(e=>({...e, y:FEET, vx:e.t==='eraser'?-0.8:0, vy:0, alive:true, hop:60+Math.random()*60, dead:0}));
  pickups=[];
  const arc=(x0,n,dx,h)=>{ for(let k=0;k<n;k++) pickups.push({t:'cheese',x:x0+k*dx,y:FEET-60-Math.sin(k/(n-1)*Math.PI)*h}); };
  arc(380,5,40,60); arc(1000,3,40,40); arc(1660,4,40,50); arc(2560,6,40,90); arc(3700,5,40,70);
  arc(4300,4,40,50); arc(5150,6,40,90); arc(5650,4,40,60);
  pickups.push({t:'cheese',x:820+CR/2,y:FEET-CR-40});
  // three hidden-ish trophies on top of the tall stacks (the 4th is the boss)
  pickups.push({t:'trophy',id:0,x:1176+CR/2,y:FEET-CR*2-70});
  pickups.push({t:'trophy',id:1,x:3588+CR/2,y:FEET-CR*3-110});
  pickups.push({t:'trophy',id:2,x:5076+CR/2,y:FEET-CR*3-120});
  for(const p of pickups){ p.taken=false; p.ph=Math.random()*6; }
  fx=[]; shots=[];
}"""

new_level_section = """// ================= levels: Level 1 (School Hallway) & Level 2 (Main Street) =================
let currentLevel = 1;
const LEVEL_LEN_1 = 5600, ARENA_X_1 = LEVEL_LEN_1 - WNAT, CHECKPOINT_X_1 = 2800, EXIT_DOOR_X = 5150;
const LEVEL_LEN_2 = 7200, ARENA_X_2 = LEVEL_LEN_2 - WNAT, CHECKPOINT_X_2 = 6150;
let LEVEL_LEN = LEVEL_LEN_1, ARENA_X = ARENA_X_1, CHECKPOINT_X = CHECKPOINT_X_1;
let level1ExitActive = false, level1ExitTimer = 0;
const CR = 56;                                   // crate size
const MICE = ['pink', 'cyan', 'yellow'];
const MOUSE_STATS = {                            // small personality differences
  pink:  {jv:11.3, maxv:3.0, dbl:false, tail:'#878787'},   // jumps highest
  cyan:  {jv:10.5, maxv:3.6, dbl:false, tail:'#696969'},   // runs fastest
  yellow:{jv:10.4, maxv:3.1, dbl:true,  tail:'#45453F'},   // double jump
};
const PARTY_ICON = {pink:'party_p', cyan:'party_c', yellow:'party_y'};
const META = ASSETS._meta;

// Level 2 (Main Street) Scenery
const CRATE_COLS = [[820,1],[1120,1],[1176,2],[1960,1],[2320,1],[2376,2],[2432,3],[3220,2],[3276,1],
  [3420,1],[3476,2],[3532,3],[3588,3],[4720,1],[4776,2],[5020,1],[5076,3],[5600,1],[5900,2],
  [ARENA_X_2+60,2],[ARENA_X_2+WNAT-60-CR,2]];
const TREES = [150,700,1500,2150,2900,3800,4450,5300,6000];
const SIGNS = [420,2650,4100,CHECKPOINT_X_2];

// Level 1 (School Hallway) Scenery
const L1_DOORS = [
  {x: 400, label: 'RM 101'},
  {x: 950, label: 'ART'},
  {x: 1600, label: 'LIBRARY'},
  {x: 2250, label: 'SCIENCE'},
  {x: 2820, label: 'GYM'},
  {x: 3500, label: 'MUSIC'},
  {x: 4100, label: 'CAFE'},
  {x: 4650, label: 'OFFICE'},
  {x: EXIT_DOOR_X, isExit: true}
];

const L1_COATRACKS = [
  {x: 140, w: 160, backpacks: [{off: 30, c: 'blue'}, {off: 90, c: 'green'}]},
  {x: 680, w: 160, backpacks: [{off: 40, c: 'purple'}, {off: 100, c: 'blue'}]},
  {x: 1220, w: 160, backpacks: [{off: 30, c: 'green'}, {off: 90, c: 'purple'}]},
  {x: 1820, w: 160, backpacks: [{off: 40, c: 'blue'}, {off: 100, c: 'green'}]},
  {x: 2460, w: 180, backpacks: [{off: 30, c: 'purple'}, {off: 90, c: 'blue'}, {off: 140, c: 'green'}]},
  {x: 3100, w: 160, backpacks: [{off: 40, c: 'blue'}, {off: 100, c: 'purple'}]},
  {x: 3720, w: 160, backpacks: [{off: 30, c: 'green'}, {off: 90, c: 'blue'}]},
  {x: 4320, w: 160, backpacks: [{off: 40, c: 'purple'}, {off: 100, c: 'green'}]},
  {x: 4860, w: 160, backpacks: [{off: 30, c: 'blue'}, {off: 90, c: 'purple'}]}
];

const L1_BOARDS = [
  {x: 580, t: 'photos'},
  {x: 1100, t: 'poster'},
  {x: 1980, t: 'photos'},
  {x: 3300, t: 'poster'},
  {x: 4420, t: 'photos'}
];

let crates=[], enemies=[], pickups=[], fx=[], shots=[];
function buildLevel(lvl = currentLevel){
  currentLevel = lvl;
  crates = []; enemies = []; pickups = []; fx = []; shots = [];
  level1ExitActive = false; level1ExitTimer = 0;

  if(currentLevel === 1){
    LEVEL_LEN = LEVEL_LEN_1; ARENA_X = ARENA_X_1; CHECKPOINT_X = CHECKPOINT_X_1;
    leftWall = 0; rightWall = LEVEL_LEN_1;

    // School Hallway Platforms & Obstacles
    // 1. Pink cubby bookshelves (w: 176, h: 64)
    const cubbies = [
      {x: 280, w: 176, h: 64},
      {x: 780, w: 176, h: 64},
      {x: 1380, w: 176, h: 64},
      {x: 1468, w: 88, h: 128}, // tiered 2nd level cubby
      {x: 2080, w: 176, h: 64},
      {x: 2620, w: 176, h: 64},
      {x: 2708, w: 88, h: 128}, // high cubby platform for Trophy #1
      {x: 3180, w: 176, h: 64},
      {x: 3820, w: 176, h: 64},
      {x: 4220, w: 176, h: 64},
      {x: 4760, w: 176, h: 64}
    ];
    for(const c of cubbies){
      crates.push({t: 'cubby', x: c.x, y: FEET - c.h, w: c.w, h: c.h});
    }

    // 2. Royal blue recycling / trash cans (w: 48, h: 62)
    const trashCans = [540, 1140, 1720, 2380, 2440, 2980, 3580, 4480, 4980];
    for(const tx of trashCans){
      crates.push({t: 'trash', x: tx, y: FEET - 62, w: 48, h: 62});
    }

    // 3. Textbook stacks (w: 48, h: 36 or 54)
    const books = [
      {x: 660, h: 36}, {x: 1880, h: 54}, {x: 2780, h: 36}, {x: 3420, h: 36}, {x: 4040, h: 36}
    ];
    for(const b of books){
      crates.push({t: 'book', x: b.x, y: FEET - b.h, w: 48, h: b.h});
    }

    // 4. Tall school locker banks (w: 70, h: 140)
    crates.push({t: 'locker', x: 1780, y: FEET - 140, w: 70, h: 140});
    crates.push({t: 'locker', x: 3940, y: FEET - 140, w: 70, h: 140});

    // 5. Caution wet floor A-frame signs (w: 32, h: 44)
    const cones = [1320, 2540, 3680, 4580];
    for(const cx of cones){
      crates.push({t: 'cone', x: cx, y: FEET - 44, w: 32, h: 44});
    }

    // Level 1 Enemies: sliding erasers, bouncing pencils, gliding paper airplanes
    enemies = [
      // Eraser patrols on floor & cubby shelves
      {t: 'eraser', x: 700, minX: 580, maxX: 780},
      {t: 'eraser', x: 1470, minX: 1380, maxX: 1550, y: FEET - 64},
      {t: 'eraser', x: 2150, minX: 1950, maxX: 2350},
      {t: 'eraser', x: 2710, minX: 2620, maxX: 2790, y: FEET - 64},
      {t: 'eraser', x: 3280, minX: 3050, maxX: 3400},
      {t: 'eraser', x: 3880, minX: 3700, maxX: 4050},
      {t: 'eraser', x: 4320, minX: 4150, maxX: 4450},
      {t: 'eraser', x: 4820, minX: 4680, maxX: 4940},

      // Hopping pencils
      {t: 'pencil', x: 1080},
      {t: 'pencil', x: 1660},
      {t: 'pencil', x: 2320},
      {t: 'pencil', x: 3080},
      {t: 'pencil', x: 3620},
      {t: 'pencil', x: 4180},
      {t: 'pencil', x: 4720},

      // Gliding paper airplanes
      {t: 'plane', x: 1550, baseY: FEET - 75, vx: -1.7, minX: 1200, maxX: 1800},
      {t: 'plane', x: 2580, baseY: FEET - 85, vx: -1.8, minX: 2200, maxX: 2900},
      {t: 'plane', x: 3520, baseY: FEET - 80, vx: -1.7, minX: 3200, maxX: 3800},
      {t: 'plane', x: 4450, baseY: FEET - 70, vx: -1.9, minX: 4100, maxX: 4750}
    ].map(e => ({
      ...e,
      y: e.y || FEET,
      vy: 0,
      vx: e.vx || (e.t === 'eraser' ? -0.8 : 0),
      alive: true,
      hop: 60 + Math.random() * 60,
      dead: 0
    }));

    // Level 1 Pickups
    const arc = (x0, n, dx, h) => {
      for(let k = 0; k < n; k++) pickups.push({t: 'cheese', x: x0 + k * dx, y: FEET - 60 - Math.sin(k / (n - 1) * Math.PI) * h});
    };
    arc(350, 4, 35, 50);
    arc(950, 5, 35, 60);
    arc(1920, 5, 40, 70);
    arc(2700, 4, 35, 50);
    arc(3350, 6, 35, 80);
    arc(4350, 5, 35, 60);
    arc(4900, 6, 35, 70);

    // Red Apples (+150 pts)
    const apples = [360, 564, 1164, 1850, 2404, 3100, 3604, 4150, 4780, 5004];
    for(const ax of apples) pickups.push({t: 'apple', x: ax, y: FEET - 80});

    // Golden Juice / Milk Cartons (+1 Life heal, +200 pts)
    const juices = [868, 1424, 2820, 3864, 4680];
    for(const jx of juices) pickups.push({t: 'juice', x: jx, y: FEET - 85});

    // 3 Hidden Trophies in Level 1
    pickups.push({t: 'trophy', id: 0, x: 1815, y: FEET - 140 - 50}); // atop high locker bank
    pickups.push({t: 'trophy', id: 1, x: 2752, y: FEET - 128 - 50}); // atop 2nd tier cubby
    pickups.push({t: 'trophy', id: 2, x: 3975, y: FEET - 140 - 50}); // atop 2nd locker bank

    for(const p of pickups){ p.taken = false; p.ph = Math.random() * 6; }
  } else {
    // Level 2 (Main Street — exact original level)
    LEVEL_LEN = LEVEL_LEN_2; ARENA_X = ARENA_X_2; CHECKPOINT_X = CHECKPOINT_X_2;
    leftWall = 0; rightWall = LEVEL_LEN_2;
    for(const [x, n] of CRATE_COLS) for(let k = 0; k < n; k++) crates.push({t: 'crate', x, y: FEET - CR * (k + 1), w: CR, h: CR});
    enemies = [
      {t:'eraser',x:1500,minX:1300,maxX:1850},{t:'pencil',x:2150},{t:'eraser',x:2900,minX:2700,maxX:3150},
      {t:'pencil',x:3050},{t:'eraser',x:4000,minX:3750,maxX:4300},{t:'eraser',x:4200,minX:3800,maxX:4500},
      {t:'pencil',x:4400},{t:'pencil',x:5300},{t:'eraser',x:5450,minX:5200,maxX:5560},{t:'pencil',x:5750},
    ].map(e=>({...e, y:FEET, vx:e.t==='eraser'?-0.8:0, vy:0, alive:true, hop:60+Math.random()*60, dead:0}));
    const arc=(x0,n,dx,h)=>{ for(let k=0;k<n;k++) pickups.push({t:'cheese',x:x0+k*dx,y:FEET-60-Math.sin(k/(n-1)*Math.PI)*h}); };
    arc(380,5,40,60); arc(1000,3,40,40); arc(1660,4,40,50); arc(2560,6,40,90); arc(3700,5,40,70);
    arc(4300,4,40,50); arc(5150,6,40,90); arc(5650,4,40,60);
    pickups.push({t:'cheese',x:820+CR/2,y:FEET-CR-40});
    pickups.push({t:'trophy',id:0,x:1176+CR/2,y:FEET-CR*2-70});
    pickups.push({t:'trophy',id:1,x:3588+CR/2,y:FEET-CR*3-110});
    pickups.push({t:'trophy',id:2,x:5076+CR/2,y:FEET-CR*3-120});
    for(const p of pickups){ p.taken=false; p.ph=Math.random()*6; }
  }
  fx = []; shots = [];
}"""

assert old_level_section in html, "Could not find old_level_section"
html = html.replace(old_level_section, new_level_section)

# 5. Update enemyBox and stepEnemies for paper plane
old_enemies = """// ================= enemies (built from the boss's school-supply theme) =================
function enemyBox(e){ return e.t==='eraser'?{x:e.x-17,y:e.y-22,w:34,h:22}:{x:e.x-9,y:e.y-42,w:18,h:42}; }
function stepEnemies(){
  const D=curDiff();
  for(const e of enemies){
    if(!e.alive){ if(e.dead>0) e.dead--; continue; }
    const tgt=nearestPlayer(e.x); if(!tgt || Math.abs(e.x-tgt.b.x)>900) continue;   // asleep off-screen
    if(e.t==='eraser'){
      e.x+=e.vx*D.enemy; if(e.x<e.minX||e.x>e.maxX) e.vx*=-1;
    } else {
      e.vy+=0.45; e.y+=e.vy; if(e.y>=FEET){ e.y=FEET; e.vy=0; }
      if(e.y>=FEET && --e.hop<=0){ e.vy=-8.5; e.hop=70+Math.random()*50; e.dir=Math.sign(tgt.b.x-e.x)||1; }
      if(e.y<FEET) e.x+=(e.dir||-1)*1.4*D.enemy;
    }
  }
}"""

new_enemies = """// ================= enemies (built from the boss's school-supply theme) =================
function enemyBox(e){
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
    } else if(e.t==='eraser'){
      e.x+=e.vx*D.enemy; if(e.x<e.minX||e.x>e.maxX) e.vx*=-1;
    } else {
      e.vy+=0.45; e.y+=e.vy; if(e.y>=FEET){ e.y=FEET; e.vy=0; }
      if(e.y>=FEET && --e.hop<=0){ e.vy=-8.5; e.hop=70+Math.random()*50; e.dir=Math.sign(tgt.b.x-e.x)||1; }
      if(e.y<FEET) e.x+=(e.dir||-1)*1.4*D.enemy;
    }
  }
}"""

assert old_enemies in html, "Could not find old_enemies"
html = html.replace(old_enemies, new_enemies)

# 6. Update beginGame and startRun
old_gameflow = """function beginGame(pk){
  picks=pk; score=0; trophies=[false,false,false,false]; checkpoint=80;
  buildLevel(); startRun();
}
function startRun(){            // everyone back at the last checkpoint with 3 lives
  spawnPlayers(picks, checkpoint);
  resetBoss(); arenaLocked=false; leftWall=0; rightWall=LEVEL_LEN;
  camX=Math.max(0,Math.min(ARENA_X,checkpoint-300));
  state='play'; stateT=0; banner=150; setTrack('street');
}"""

new_gameflow = """function beginGame(pk){
  picks=pk; score=0; trophies=[false,false,false,false]; checkpoint=80;
  currentLevel=1;
  triggerSplash(1);
}
function triggerSplash(lvl){
  splashLevel=lvl; state='splash'; splashT=0; sfx('confirm');
}
function nextAfterSplash(){
  currentLevel=splashLevel; checkpoint=80; trophies=[false,false,false,false];
  buildLevel(currentLevel); startRun();
}
function startRun(){            // everyone back at the last checkpoint with 3 lives
  spawnPlayers(picks, checkpoint);
  if(currentLevel===2){ resetBoss(); arenaLocked=false; }
  else { arenaLocked=false; level1ExitActive=false; level1ExitTimer=0; }
  leftWall=0; rightWall=LEVEL_LEN;
  camX=Math.max(0,Math.min(ARENA_X,checkpoint-300));
  state='play'; stateT=0; banner=150; setTrack('street');
}"""

assert old_gameflow in html, "Could not find old_gameflow"
html = html.replace(old_gameflow, new_gameflow)

# 7. Update frameInput for state === 'splash'
old_frame_input = """function frameInput(){
  if(state==='title'){ titleUpdate(); return; }
  if(state==='play'){"""

new_frame_input = """function frameInput(){
  if(state==='splash'){
    if((anyEdge('a')||anyEdge('b')||anyEdge('start')) && splashT>15) nextAfterSplash();
    return;
  }
  if(state==='title'){ titleUpdate(); return; }
  if(state==='play'){"""

assert old_frame_input in html, "Could not find old_frame_input"
html = html.replace(old_frame_input, new_frame_input)

# 8. Update tick() for splash state, pickups (apple/juice), and level 1 exit vs level 2 boss
old_tick_start = """function tick(){
  frame++; stateT++;
  if(banner>0) banner--;
  if(shake>0) shake*=0.85, shake<0.5&&(shake=0);
  if(state==='win'||state==='victory'){ stepConfetti(); return; }
  if(state!=='play') return;"""

new_tick_start = """function tick(){
  frame++; stateT++;
  if(banner>0) banner--;
  if(shake>0) shake*=0.85, shake<0.5&&(shake=0);
  if(state==='splash'){ splashT++; if(splashT>160) nextAfterSplash(); return; }
  if(state==='win'||state==='victory'){ stepConfetti(); return; }
  if(state!=='play') return;"""

assert old_tick_start in html, "Could not find old_tick_start"
html = html.replace(old_tick_start, new_tick_start)

# In tick(), update pickups handling
old_pickups_handling = """    for(const pk of pickups){
      if(pk.taken) continue;
      if(Math.abs(pk.x-b.x)<30 && pk.y>b.y-(HIT_H[b.id]||86)-12 && pk.y<b.y+10){
        pk.taken=true;
        if(pk.t==='cheese'){
          if(p.lives<3){ p.lives++; fx.push({t:'pts',x:pk.x,y:pk.y-18,txt:'+1 LIFE',age:0}); }   // cheese heals
          addScore(100,pk.x,pk.y); sfx('cheese'); }
        else { trophies[pk.id]=true; addScore(1000,pk.x,pk.y); sfx('trophy'); fx.push({t:'star',x:pk.x,y:pk.y,age:0,small:true}); }
      }
    }"""

new_pickups_handling = """    for(const pk of pickups){
      if(pk.taken) continue;
      if(Math.abs(pk.x-b.x)<30 && pk.y>b.y-(HIT_H[b.id]||86)-12 && pk.y<b.y+10){
        pk.taken=true;
        if(pk.t==='cheese'){
          if(p.lives<3){ p.lives++; fx.push({t:'pts',x:pk.x,y:pk.y-18,txt:'+1 LIFE',age:0}); }
          addScore(100,pk.x,pk.y); sfx('cheese');
        } else if(pk.t==='apple'){
          addScore(150,pk.x,pk.y); sfx('cheese');
          fx.push({t:'pts',x:pk.x,y:pk.y-18,txt:'+150',age:0});
        } else if(pk.t==='juice'){
          if(p.lives<3){ p.lives++; fx.push({t:'pts',x:pk.x,y:pk.y-18,txt:'+1 LIFE',age:0}); }
          else addScore(200,pk.x,pk.y);
          sfx('cheese'); fx.push({t:'pts',x:pk.x,y:pk.y-18,txt:'+1 LIFE',age:0});
        } else {
          trophies[pk.id]=true; addScore(1000,pk.x,pk.y); sfx('trophy'); fx.push({t:'star',x:pk.x,y:pk.y,age:0,small:true});
        }
      }
    }"""

assert old_pickups_handling in html, "Could not find old_pickups_handling"
html = html.replace(old_pickups_handling, new_pickups_handling)

# In tick(), update checkpoint and level 1 exit vs level 2 boss
old_checkpoint_boss = """  const maxX=Math.max(...live.map(p=>p.b.x)), avgX=live.reduce((a,p)=>a+p.b.x,0)/live.length;
  // checkpoint + arena
  if(maxX>CHECKPOINT_X && checkpoint<CHECKPOINT_X){
    checkpoint=CHECKPOINT_X; reviveAtCheckpoint();
    fx.push({t:'pts',x:CHECKPOINT_X,y:FEET-140,txt:'CHECKPOINT',age:0}); sfx('confirm');
  }
  if(!arenaLocked && maxX>ARENA_X+20){
    arenaLocked=true; leftWall=ARENA_X; rightWall=LEVEL_LEN; boss.state='enter'; setTrack(null);
    enemies.forEach(e=>{ if(e.x>ARENA_X-100) e.alive=false; });
    for(const p of live) p.b.x=Math.max(p.b.x,ARENA_X+30);     // pull stragglers into the arena
  }
  bossAI(); if(state==='play') bossCollide();"""

new_checkpoint_boss = """  const maxX=Math.max(...live.map(p=>p.b.x)), avgX=live.reduce((a,p)=>a+p.b.x,0)/live.length;
  if(currentLevel===1){
    if(maxX>CHECKPOINT_X && checkpoint<CHECKPOINT_X){
      checkpoint=CHECKPOINT_X; reviveAtCheckpoint();
      fx.push({t:'pts',x:CHECKPOINT_X,y:FEET-140,txt:'CHECKPOINT',age:0}); sfx('confirm');
    }
    if(!level1ExitActive && maxX>EXIT_DOOR_X-120){
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
    }
  } else {
    // Level 2 (Main Street original boss logic)
    if(maxX>CHECKPOINT_X && checkpoint<CHECKPOINT_X){
      checkpoint=CHECKPOINT_X; reviveAtCheckpoint();
      fx.push({t:'pts',x:CHECKPOINT_X,y:FEET-140,txt:'CHECKPOINT',age:0}); sfx('confirm');
    }
    if(!arenaLocked && maxX>ARENA_X+20){
      arenaLocked=true; leftWall=ARENA_X; rightWall=LEVEL_LEN; boss.state='enter'; setTrack(null);
      enemies.forEach(e=>{ if(e.x>ARENA_X-100) e.alive=false; });
      for(const p of live) p.b.x=Math.max(p.b.x,ARENA_X+30);
    }
    bossAI(); if(state==='play') bossCollide();
  }"""

assert old_checkpoint_boss in html, "Could not find old_checkpoint_boss"
html = html.replace(old_checkpoint_boss, new_checkpoint_boss)

# 9. Add drawing helper functions for school scenery, obstacles, enemies, and splash
school_draw_functions = """
// ================= School Hallway Rendering (Level 1) =================
function drawBackpack(x,y,color){
  const bodyCol = color==='blue'?COL.bpBlue:color==='green'?COL.bpGreen:COL.bpPurple;
  const darkCol = color==='blue'?'#1E65BA':color==='green'?'#63B01E':'#771FA8';
  const zipCol = color==='purple'?'#FCE838':'#FFFFFF';
  ctx.strokeStyle=darkCol; ctx.lineWidth=3; ctx.beginPath();
  ctx.arc(x,y+2,8,Math.PI,0); ctx.stroke();
  rrect(x-18,y+8,36,44,9); ctx.fillStyle=bodyCol; ctx.fill();
  rrect(x-13,y+26,26,22,5); ctx.fillStyle=darkCol; ctx.fill();
  rect(x-9,y+30,18,2,zipCol);
  rrect(x+15,y+24,6,18,2); ctx.fillStyle=darkCol; ctx.fill();
  rect(x+16,y+18,4,6,'#4AE3F5');
}

function drawClassroomDoor(sx,dr){
  const w=dr.isExit?130:94, h=212, dy=FEET-h;
  if(dr.isExit){
    rrect(sx-4,dy-4,w+8,h+4,18); ctx.fillStyle='#FFFFFF'; ctx.fill();
    rrect(sx+w/2-32,dy-34,64,24,4); ctx.fillStyle='#03A82E'; ctx.fill();
    rect(sx+w/2-30,dy-32,60,20,'#03CF39');
    text('EXIT',sx+w/2,dy-26,2,'#FFFFFF','c');
    if(level1ExitActive && level1ExitTimer>=50){
      const glowW=Math.min(240,(level1ExitTimer-50)*5);
      const g=ctx.createLinearGradient(sx,dy,sx-80,FEET);
      g.addColorStop(0,'rgba(255, 245, 180, 0.6)'); g.addColorStop(1,'rgba(255, 245, 180, 0.0)');
      ctx.fillStyle=g; ctx.beginPath();
      ctx.moveTo(sx+10,dy+20); ctx.lineTo(sx+w-10,dy+20);
      ctx.lineTo(sx+w+glowW,FEET+20); ctx.lineTo(sx-glowW,FEET+20);
      ctx.closePath(); ctx.fill();
      rect(sx+8,dy+8,w-16,h-8,COL.sky);
      disc(sx+w/2,dy+60,26,16,COL.cloud); disc(sx+w/2-20,dy+h-30,40,35,COL.canopy);
      rrect(sx-12,dy+8,20,h-8,4); ctx.fillStyle=COL.schoolDoor; ctx.fill();
      rrect(sx+w-8,dy+8,20,h-8,4); ctx.fillStyle=COL.schoolDoor; ctx.fill();
    } else {
      rrect(sx,dy,w/2-2,h,12); ctx.fillStyle=COL.schoolDoor; ctx.fill();
      rrect(sx+w/2+2,dy,w/2-2,h,12); ctx.fillStyle=COL.schoolDoor; ctx.fill();
      rrect(sx+12,dy+32,w/2-26,75,6); ctx.fillStyle=COL.schoolDoorWin; ctx.fill();
      rrect(sx+w/2+14,dy+32,w/2-26,75,6); ctx.fillStyle=COL.schoolDoorWin; ctx.fill();
      rect(sx+16,dy+45,16,2,'#FFFFFF'); rect(sx+w/2+18,dy+45,16,2,'#FFFFFF');
      rect(sx+6,dy+130,w/2-14,8,COL.schoolDoorHandle); rect(sx+w/2+8,dy+130,w/2-14,8,COL.schoolDoorHandle);
    }
  } else {
    rrect(sx-4,dy-4,w+8,h+4,18); ctx.fillStyle='#FFFFFF'; ctx.fill();
    rrect(sx,dy,w,h,14); ctx.fillStyle=COL.schoolDoor; ctx.fill();
    rrect(sx+16,dy+30,w-32,78,8); ctx.fillStyle=COL.schoolDoorWin; ctx.fill();
    ctx.save(); ctx.beginPath(); rrect(sx+16,dy+30,w-32,78,8); ctx.clip();
    ctx.strokeStyle='rgba(255,255,255,0.7)'; ctx.lineWidth=4;
    ctx.beginPath(); ctx.moveTo(sx+22,dy+110); ctx.lineTo(sx+w-24,dy+38); ctx.stroke(); ctx.restore();
    rrect(sx+8,dy+126,7,24,3); ctx.fillStyle=COL.schoolDoorHandle; ctx.fill();
    if(dr.label){ rrect(sx+w/2-28,dy+12,56,14,3); ctx.fillStyle='#FFFFFF'; ctx.fill(); text(dr.label,sx+w/2,dy+16,1,'#333','c'); }
  }
}

function drawHallwayScenery(){
  rect(0,0,WNAT,FEET,COL.hallWall);
  rect(0,270,WNAT,FEET-270,COL.hallWallDk);
  rect(0,268,WNAT,2,'rgba(0,0,0,0.06)');
  for(let lx=140;lx<LEVEL_LEN_1;lx+=280){
    const sx=lx-camX;
    if(sx>-40&&sx<WNAT+40){
      rect(sx-1,0,3,50,COL.hallLampDk);
      ctx.fillStyle=COL.hallLamp; ctx.beginPath(); ctx.moveTo(sx-16,68); ctx.quadraticCurveTo(sx,48,sx+16,68); ctx.closePath(); ctx.fill();
      rrect(sx-17,66,34,5,2); ctx.fillStyle=COL.hallLampDk; ctx.fill();
    }
  }
  for(const bb of L1_BOARDS){
    const sx=bb.x-camX;
    if(sx>-100&&sx<WNAT+100){
      rrect(sx,130,80,100,6); ctx.fillStyle='#4CAEAA'; ctx.fill();
      rrect(sx+5,135,70,90,4); ctx.fillStyle='#3E9B96'; ctx.fill();
      if(bb.t==='photos'){
        for(let py=0;py<2;py++) for(let px=0;px<2;px++){
          rrect(sx+10+px*32,142+py*42,26,34,3); ctx.fillStyle='#E3F8F6'; ctx.fill();
          disc(sx+23+px*32,153+py*42,6,6,'#368984'); disc(sx+23+px*32,168+py*42,10,8,'#368984');
        }
      } else if(bb.t==='poster'){
        rect(sx+12,144,56,72,'#FFFFFF');
        text('SQUAD',sx+40,150,1,COL.hud,'c'); text('RULES!',sx+40,162,1,'#DB5C66','c');
        disc(sx+40,185,12,8,COL.cheese);
      }
    }
  }
  for(const cr of L1_COATRACKS){
    const sx=cr.x-camX;
    if(sx>-cr.w&&sx<WNAT+60){
      rrect(sx,175,cr.w,14,5); ctx.fillStyle='#DA6D67'; ctx.fill();
      for(let px=sx+12;px<sx+cr.w-8;px+=24) rect(px-2,167,4,10,'#DA6D67');
      for(const bp of cr.backpacks) drawBackpack(sx+bp.off,177,bp.c);
    }
  }
  for(const dr of L1_DOORS){
    const sx=dr.x-camX;
    if(sx>-140&&sx<WNAT+140) drawClassroomDoor(sx,dr);
  }
  rect(0,362,WNAT,10,COL.hallTrim); rect(0,362,WNAT,2,COL.hallTrimBorder);
  rect(0,FEET,WNAT,HNAT-FEET,COL.hallFloor);
  const tileOff=((-camX)%88+88)%88;
  for(let tx=tileOff-88;tx<WNAT+88;tx+=88) rect(tx,FEET,2,HNAT-FEET,COL.hallGrout);
  rect(0,402,WNAT,2,'#D8DAAE');
}

function drawCubby(x,y,w,h){
  rrect(x,y,w,h,6); ctx.fillStyle=COL.cubby; ctx.fill();
  rect(x+4,y,w-8,3,COL.cubbyHi);
  const cols=Math.max(2,Math.floor(w/44)), rows=h>80?3:2;
  const cw=(w-8-(cols-1)*4)/cols, ch=(h-8-(rows-1)*4)/rows;
  const bookPal=['#1D49BF','#B02638','#E6A11C','#1E824C','#6C3483','#D35400'];
  for(let r=0;r<rows;r++) for(let c=0;c<cols;c++){
    const cx=x+4+c*(cw+4), cy=y+4+r*(ch+4);
    rrect(cx,cy,cw,ch,3); ctx.fillStyle=COL.cubbyDk; ctx.fill();
    const seed=(c*7+r*13)%4;
    if(seed===0){
      rect(cx+4,cy+ch-18,6,18,bookPal[(c+r)%bookPal.length]);
      rect(cx+12,cy+ch-16,7,16,bookPal[(c+r+2)%bookPal.length]);
      rect(cx+21,cy+ch-20,6,20,bookPal[(c+r+4)%bookPal.length]);
    } else if(seed===1){
      rect(cx+4,cy+ch-7,cw-8,7,bookPal[(c+r+1)%bookPal.length]);
      rect(cx+6,cy+ch-14,cw-12,7,bookPal[(c+r+3)%bookPal.length]);
    } else if(seed===2){
      rect(cx+6,cy+ch-18,7,18,bookPal[(c+r)%bookPal.length]);
      rect(cx+16,cy+ch-15,6,15,bookPal[(c+r+5)%bookPal.length]);
    }
  }
}

function drawTrashCan(x,y,w=48,h=62){
  const cx=x+w/2;
  ctx.fillStyle=COL.trashBlue; ctx.beginPath();
  ctx.moveTo(x+4,y+10); ctx.lineTo(x+w-4,y+10); ctx.lineTo(x+w-7,y+h); ctx.lineTo(x+7,y+h);
  ctx.closePath(); ctx.fill();
  for(let i=-1;i<=1;i++) rect(cx+i*11-2,y+14,4,h-20,COL.trashDk);
  rrect(x,y+6,w,8,3); ctx.fillStyle=COL.trashHi; ctx.fill();
  rrect(cx-9,y,18,7,3); ctx.fillStyle=COL.trashDk; ctx.fill();
  rect(cx-6,y+3,12,4,COL.trashHi);
}

function drawBookStack(x,y,w,h){
  const count=Math.max(2,Math.floor(h/14)), bh=h/count;
  const pal=['#D32F2F','#1976D2','#388E3C','#F57C00'];
  for(let i=0;i<count;i++){
    const by=y+h-(i+1)*bh, bw=w-(count-1-i)*3, bx=x+(w-bw)/2;
    rrect(bx,by,bw,bh,2); ctx.fillStyle=pal[i%pal.length]; ctx.fill();
    rect(bx+4,by+2,bw-6,bh-4,'#FDFDFD'); rect(bx+1,by+1,3,bh-2,'rgba(0,0,0,0.2)');
  }
}

function drawLocker(x,y,w,h){
  rrect(x,y,w,h,4); ctx.fillStyle='#4CAEAA'; ctx.fill();
  rect(x+2,y+2,w-4,h-4,'#3D9994');
  const doors=Math.max(1,Math.floor(w/32)), dw=(w-4-(doors-1)*2)/doors;
  for(let i=0;i<doors;i++){
    const dx=x+2+i*(dw+2);
    rrect(dx,y+3,dw,h-6,2); ctx.fillStyle='#4CAEAA'; ctx.fill();
    for(let v=0;v<3;v++) rect(dx+6,y+14+v*6,dw-12,2,'#2C7A76');
    rect(dx+dw-7,y+h/2-8,4,16,'#C0C0C0'); disc(dx+dw-5,y+h/2+12,3,3,'#111');
  }
}

function drawCone(x,y,w=32,h=44){
  ctx.fillStyle=COL.cautionYellow; ctx.beginPath();
  ctx.moveTo(x+w/2,y); ctx.lineTo(x+w,y+h); ctx.lineTo(x,y+h); ctx.closePath(); ctx.fill();
  ctx.fillStyle='#222'; ctx.beginPath();
  ctx.moveTo(x+w/2,y+10); ctx.lineTo(x+w/2+9,y+26); ctx.lineTo(x+w/2-9,y+26); ctx.closePath(); ctx.fill();
  rect(x+w/2-1,y+15,2,6,COL.cautionYellow); rect(x+w/2-1,y+23,2,2,COL.cautionYellow);
  text('!',x+w/2,y+32,1,'#111','c');
}

function drawApple(x,y){
  disc(x,y,11,11,'#FE2043'); disc(x-4,y-4,3,3,'#FF6B82');
  rect(x-1,y-14,2,5,'#8D5733'); disc(x+5,y-13,5,3,'#03CF39');
}

function drawJuiceBox(x,y){
  rect(x-11,y-14,22,22,COL.juiceBox); rect(x,y-14,11,22,COL.juiceDk);
  ctx.fillStyle=COL.juiceHi; ctx.beginPath();
  ctx.moveTo(x-11,y-14); ctx.lineTo(x-4,y-24); ctx.lineTo(x+4,y-24); ctx.lineTo(x+11,y-14);
  ctx.closePath(); ctx.fill();
  rect(x-3,y-26,6,3,'#FF8F00'); rect(x+3,y-32,3,10,'#FC3939');
}

function drawPaperPlane(x,y,vx){
  const dir=vx<0?-1:1;
  ctx.save(); ctx.translate(R(x),R(y)); ctx.scale(dir,1);
  const bob=Math.sin(frame*0.1)*0.1; ctx.rotate(bob);
  ctx.fillStyle='#FFFFFF'; ctx.beginPath();
  ctx.moveTo(22,0); ctx.lineTo(-18,-12); ctx.lineTo(-10,0); ctx.closePath(); ctx.fill();
  ctx.fillStyle='#E4E4E4'; ctx.beginPath();
  ctx.moveTo(22,0); ctx.lineTo(-10,0); ctx.lineTo(-18,10); ctx.closePath(); ctx.fill();
  ctx.strokeStyle='#BDBDBD'; ctx.lineWidth=1.5; ctx.beginPath(); ctx.moveTo(22,0); ctx.lineTo(-10,0); ctx.stroke();
  ctx.restore();
}

function renderSplash(){
  rect(0,0,WNAT,HNAT,'#000');
  const img=splashLevel===1?splashImg1:splashImg2;
  if(img && img.complete && img.naturalWidth>0){
    ctx.drawImage(img,0,0,WNAT,HNAT);
  }
  hudFrame();
  if(splashT>30 && Math.floor(frame/20)%2===0){
    text('PRESS A TO START',WNAT/2,HNAT-24,2,COL.hud,'c','#000');
  }
}
"""

if 'drawHallwayScenery' not in html:
    target = "// ================= rendering =================\nconst R=Math.round;"
    assert target in html, "Could not find rendering target"
    html = html.replace(target, target + "\n" + school_draw_functions)

# 10. In drawEnemy, add plane
old_draw_enemy = """function drawEnemy(e){
  const x=e.x-camX;
  if(!e.alive){ if(e.dead>0){ ctx.globalAlpha=e.dead/40; if(e.t==='eraser') rect(x-17,e.y-6,34,6,COL.eraser); else drawPencil(x,e.y-4,Math.PI/2,40); ctx.globalAlpha=1; } return; }
  if(e.t==='eraser'){"""

new_draw_enemy = """function drawEnemy(e){
  const x=e.x-camX;
  if(!e.alive){
    if(e.dead>0){
      ctx.globalAlpha=e.dead/40;
      if(e.t==='eraser') rect(x-17,e.y-6,34,6,COL.eraser);
      else if(e.t==='plane') drawPaperPlane(x,e.y+Math.sin(frame*0.2)*4,e.vx);
      else drawPencil(x,e.y-4,Math.PI/2,40);
      ctx.globalAlpha=1;
    }
    return;
  }
  if(e.t==='plane'){
    drawPaperPlane(x,e.y,e.vx);
    return;
  }
  if(e.t==='eraser'){"""

assert old_draw_enemy in html, "Could not find old_draw_enemy"
html = html.replace(old_draw_enemy, new_draw_enemy)

# 11. In renderPlay(), update scenery, obstacles, pickups, banner, and HUD
old_render_play = """function renderPlay(){
  ctx.save();
  if(shake) ctx.translate(R((Math.random()-0.5)*shake),R((Math.random()-0.5)*shake));
  drawScenery();
  for(const c of crates) if(c.x-camX>-CR&&c.x-camX<WNAT) drawCrate(R(c.x-camX),c.y);
  for(const p of pickups){ if(p.taken) continue; const x=p.x-camX; if(x<-30||x>WNAT+30) continue;
    const by=p.y+Math.sin(frame*0.08+p.ph)*3;
    if(p.t==='cheese') drawCheese(x,by);
    else { ctx.globalAlpha=0.35+0.15*Math.sin(frame*0.1); disc(x,by-14,24,24,'#FFF7A0'); ctx.globalAlpha=1; drawSpr('trophy',x,by); } }
  for(const e of enemies) if(Math.abs(e.x-camX-WNAT/2)<WNAT) drawEnemy(e);
  drawBoss();
  for(const s of shots) drawPencil(s.x-camX,s.y,s.rot,34);
  hudBossMeter();                       // under the players, never covering them
  drawPlayers();
  for(const k of koFx){ const img=(k.face<0?SPRL:SPR)[k.id+'_idle'];
    ctx.save(); ctx.translate(R(k.x-camX),R(k.y-50)); ctx.rotate(k.rot); ctx.drawImage(img,-img.width/2,-img.height/2); ctx.restore(); }
  drawFx();
  ctx.restore();
  hudFrame();
  const lp=alivePlayers(), lx=lp.length?Math.max(...lp.map(p=>p.b.x)):0;
  const prog=arenaLocked?16:Math.min(16,Math.floor(16*lx/ARENA_X));
  hudPanels('01',prog,score,true);
  if(banner>0){ ctx.globalAlpha=Math.min(1,banner/30);
    rrect(204,170,360,70,12); ctx.fillStyle='rgba(0,0,0,0.85)'; ctx.fill();
    text('LEVEL 01',WNAT/2,180,4,COL.hud,'c',null,true); text('MAIN STREET',WNAT/2,214,3,'#FFFFFF','c'); ctx.globalAlpha=1; }
}"""

new_render_play = """function renderPlay(){
  ctx.save();
  if(shake) ctx.translate(R((Math.random()-0.5)*shake),R((Math.random()-0.5)*shake));
  if(currentLevel===1) drawHallwayScenery(); else drawScenery();
  for(const c of crates){
    if(c.x-camX>-c.w&&c.x-camX<WNAT+100){
      if(c.t==='cubby') drawCubby(c.x-camX,c.y,c.w,c.h);
      else if(c.t==='trash') drawTrashCan(c.x-camX,c.y,c.w,c.h);
      else if(c.t==='book') drawBookStack(c.x-camX,c.y,c.w,c.h);
      else if(c.t==='locker') drawLocker(c.x-camX,c.y,c.w,c.h);
      else if(c.t==='cone') drawCone(c.x-camX,c.y,c.w,c.h);
      else drawCrate(R(c.x-camX),c.y);
    }
  }
  for(const p of pickups){
    if(p.taken) continue; const x=p.x-camX; if(x<-30||x>WNAT+30) continue;
    const by=p.y+Math.sin(frame*0.08+p.ph)*3;
    if(p.t==='cheese') drawCheese(x,by);
    else if(p.t==='apple') drawApple(x,by);
    else if(p.t==='juice') drawJuiceBox(x,by);
    else { ctx.globalAlpha=0.35+0.15*Math.sin(frame*0.1); disc(x,by-14,24,24,'#FFF7A0'); ctx.globalAlpha=1; drawSpr('trophy',x,by); }
  }
  for(const e of enemies) if(Math.abs(e.x-camX-WNAT/2)<WNAT) drawEnemy(e);
  if(currentLevel===2) drawBoss();
  for(const s of shots) drawPencil(s.x-camX,s.y,s.rot,34);
  if(currentLevel===2) hudBossMeter();
  drawPlayers();
  for(const k of koFx){ const img=(k.face<0?SPRL:SPR)[k.id+'_idle'];
    ctx.save(); ctx.translate(R(k.x-camX),R(k.y-50)); ctx.rotate(k.rot); ctx.drawImage(img,-img.width/2,-img.height/2); ctx.restore(); }
  drawFx();
  ctx.restore();
  hudFrame();
  const lp=alivePlayers(), lx=lp.length?Math.max(...lp.map(p=>p.b.x)):0;
  const prog=arenaLocked?16:Math.min(16,Math.floor(16*lx/ARENA_X));
  hudPanels(currentLevel===1?'01':'02',prog,score,true);
  if(banner>0){
    ctx.globalAlpha=Math.min(1,banner/30);
    rrect(204,170,360,70,12); ctx.fillStyle='rgba(0,0,0,0.85)'; ctx.fill();
    const lNum=currentLevel===1?'01':'02', lName=currentLevel===1?'SCHOOL HALLWAY':'MAIN STREET';
    text('LEVEL '+lNum,WNAT/2,180,4,COL.hud,'c',null,true); text(lName,WNAT/2,214,3,'#FFFFFF','c'); ctx.globalAlpha=1;
  }
  if(currentLevel===1 && level1ExitActive && level1ExitTimer>=40){
    rrect(154,140,460,86,14); ctx.fillStyle='rgba(0,0,0,0.88)'; ctx.fill();
    ctx.lineWidth=4; ctx.strokeStyle=COL.hud; ctx.stroke();
    text('SCHOOL IS OUT!',WNAT/2,154,4,COL.hud,'c',null,true);
    text('HEADING TO MAIN STREET!',WNAT/2,192,3,'#FFFFFF','c');
  }
}"""

assert old_render_play in html, "Could not find old_render_play"
html = html.replace(old_render_play, new_render_play)

# 12. In render(), add state === 'splash'
old_render = """function render(){
  ctx.imageSmoothingEnabled=false;
  if(state==='title'){ renderTitle(); return; }"""

new_render = """function render(){
  ctx.imageSmoothingEnabled=false;
  if(state==='splash'){ renderSplash(); return; }
  if(state==='title'){ renderTitle(); return; }"""

assert old_render in html, "Could not find old_render"
html = html.replace(old_render, new_render)

# 13. In boot, pass 1 to buildLevel
old_boot = "buildLevel(); spawnPlayers([{id:'cyan',src:'kb'}],80); resetBoss();"
new_boot = "buildLevel(1); spawnPlayers([{id:'cyan',src:'kb'}],80); resetBoss();"
assert old_boot in html, "Could not find old_boot"
html = html.replace(old_boot, new_boot)

with open('index.html', 'w') as f:
    f.write(html)

print('Updated index.html successfully, length:', len(html))
