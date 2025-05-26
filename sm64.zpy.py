from ursina import *
import math

app = Ursina()
window.title = 'Catsan MIPS Project (SM64 Physics)'
window.borderless = False
window.size = (1280, 720)

RED = color.rgb(200, 40, 40)
BLUE = color.rgb(60, 120, 255)
YELLOW = color.rgb(255, 240, 60)
GREEN = color.rgb(80, 200, 80)
WHITE = color.rgb(255,255,255)

# Tuned Mario 64 physics constants (slower)
GRAVITY = 0.19   # Lower gravity
WALK_ACC = 0.07  # Lower accel
RUN_ACC = 0.11
FRICTION = 0.08
MAX_WALK = 2.7
MAX_RUN = 4.3
JUMP_VEL = 0.14
TERM_VEL = -4.0

def clamp(n, smallest, largest): return max(smallest, min(n, largest))

class Mario(Entity):
    def __init__(self, **kwargs):
        super().__init__(
            model='cube', color=RED, scale_y=1.2, scale_x=0.6, scale_z=0.6, collider='box', position=(0,1,0), **kwargs
        )
        self.pants = Entity(parent=self, model='cube', color=BLUE, y=-0.5, scale_y=0.5, scale=(0.7,0.6,0.6))
        self.button1 = Entity(parent=self, model='sphere', color=YELLOW, x=0.17, y=-0.15, z=0.3, scale=0.08)
        self.button2 = Entity(parent=self, model='sphere', color=YELLOW, x=-0.17, y=-0.15, z=0.3, scale=0.08)
        self.vel = Vec3(0,0,0)
        self.facing = 0
        self.on_ground = False
        self.jump_timer = 0

    def mario_input(self):
        dx = held_keys['d'] - held_keys['a']
        dz = held_keys['w'] - held_keys['s']
        mag = math.sqrt(dx*dx + dz*dz)
        return (dx/mag if mag else 0, dz/mag if mag else 0, mag)

    def update(self):
        dx, dz, mag = self.mario_input()
        is_running = held_keys['shift']
        max_speed = MAX_RUN if is_running else MAX_WALK
        acc = RUN_ACC if is_running else WALK_ACC

        move_dir = Vec3(dx, 0, dz)
        if mag > 0:
            self.facing = math.degrees(math.atan2(dx, dz))
            move_dir = move_dir.normalized()
            self.vel.x += acc * move_dir.x
            self.vel.z += acc * move_dir.z
        else:
            self.vel.x -= FRICTION * self.vel.x
            self.vel.z -= FRICTION * self.vel.z

        # Clamp velocity to max speed
        speed = math.sqrt(self.vel.x ** 2 + self.vel.z ** 2)
        if speed > max_speed:
            factor = max_speed / speed
            self.vel.x *= factor
            self.vel.z *= factor

        # Mario 64 jump logic
        if self.on_ground:
            if held_keys['space']:
                if self.jump_timer == 0:
                    self.vel.y = JUMP_VEL + 0.025 * (speed/MAX_RUN)
                self.jump_timer += 1
            else:
                self.jump_timer = 0
        self.vel.y -= GRAVITY * time.dt * 60 * 0.6
        self.vel.y = max(self.vel.y, TERM_VEL)

        # Move Mario (remove *60 turbo mode)
        self.position += self.vel * time.dt

        # Ground check
        if self.y <= 1:
            self.y = 1
            self.vel.y = 0
            self.on_ground = True
        else:
            self.on_ground = False

        self.rotation_y = self.facing

player = Mario()

# Camera setup
camera.parent = player
camera.position = (0, 2.5, -10)
camera.rotation_x = 14
cam_yaw = 0

def update():
    global cam_yaw
    if held_keys['q']: cam_yaw += 60 * time.dt
    if held_keys['e']: cam_yaw -= 60 * time.dt
    camera.rotation_y = cam_yaw

def make_platform(x, y, z, sx, sy, sz, col=GREEN):
    return Entity(model='cube', color=col, scale=(sx, sy, sz), position=(x, y, z), collider='box')

ground = make_platform(0,0,0, 18,1,18, GREEN)
hill = make_platform(6,1,6, 4,2,4, color.lime)
block = make_platform(-4,1,4, 2,1,2, color.azure)
platform1 = make_platform(0,1,7, 3,1,2, color.gold)
platform2 = make_platform(-7,1,-5, 3,1,3, color.red)
coins = [Entity(model='sphere', color=YELLOW, scale=0.3, position=(x,1.5,z)) for x,z in [(-2,3), (5,5), (7,-7), (0,8), (-8,0)]]

def input(key):
    if key == 'escape': application.quit()

app.run()
