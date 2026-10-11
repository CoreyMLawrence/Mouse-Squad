import sys, re

def inject_physics():
    with open('index.html', 'r') as f:
        html = f.read()
        
    start_str = "class Walker{"
    end_str = "// ---------- ring AI ----------"
    
    start_idx = html.find(start_str)
    end_idx = html.find(end_str)
    
    if start_idx == -1 or end_idx == -1:
        print("Could not find boundaries")
        return
        
    new_physics = """// ---------- AABB platformer physics ----------
class Body{
  constructor(x,y){
    this.x=x; this.y=y;               
    this.vx=0; this.vy=0;             
    this.w=22; this.h=44;
    this.face=1;                      
    this.air=false;
    this.animT=0;
    this.animState='idle';
    this.jheld=false;
    this.coyote=0;
    this.jumpBuf=0;
  }
  
  step(pad){
    // Constants
    const MAX_RUN=1.9, ACC=0.12, FRIC=0.80, SKID=0.30;
    const JUMP=4.2, GRAV_UP=0.13, GRAV_DN=0.30, TERM=4.5, AIR_CTRL=0.10;
    
    // Y movement & Gravity
    if(this.air){
      this.vy += (this.vy < 0 && this.jheld) ? GRAV_UP : GRAV_DN;
      if(this.vy > TERM) this.vy = TERM;
    } else {
      this.vy = 0;
      this.coyote = 6;
    }
    
    // Jump buffering
    const justJump = pad.jump && (!pad.prev || !pad.prev.jump);
    if(justJump) this.jumpBuf = 6;
    
    // Jumping
    if(this.jumpBuf > 0 && this.coyote > 0){
      this.vy = -JUMP;
      this.air = true;
      this.coyote = 0;
      this.jumpBuf = 0;
    }
    if(this.jumpBuf > 0) this.jumpBuf--;
    if(this.coyote > 0) this.coyote--;
    
    this.jheld = pad.jump;
    
    // X movement
    let ix = pad.gx; // -1, 0, 1
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
    
    // Apply velocity (no collision yet, just floor clamp)
    this.x += this.vx;
    this.y += this.vy;
    
    // Temp floor collision at y=188 (feet line)
    if(this.y > 188){
      this.y = 188;
      this.vy = 0;
      this.air = false;
    }
    
    this.animT++;
  }
}
"""
    
    html = html[:start_idx] + new_physics + html[end_idx:]
    html = html.replace('new Walker', 'new Body')
    
    with open('index.html', 'w') as f:
        f.write(html)
        
    print("Injected physics.")

if __name__ == '__main__':
    inject_physics()
