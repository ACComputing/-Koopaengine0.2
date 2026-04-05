#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ======================================================================
#  KOOPA ENGINE 0.3  —  SM64 PC PORT AUTHENTIC
#  Super Mario 64 · Pygame Edition
#  Copyright (C) 1999-2026  A.C Holdings / Team Flames
#  Entry point: python3 sm64_koopa_engine.py
#
#  Requires: Python 3.8+, pygame 2.x
#  BUG FIX PASS: 49 bugs fixed from 0.2
#  FEATURE PASS: Full SM64 PC Port movement + gameplay systems
#  NO OST — Synthesized SFX only
# ======================================================================

from __future__ import annotations
import sys
import pygame
import math
import random
import json
import os
import struct
import array

# --- Python version guard (FIX #1: was 3.14+, works on 3.8+) ---
if sys.version_info < (3, 8):
    sys.exit(f"[KoopaEngine 0.3] FATAL: Python {sys.version} — need 3.8+")

# --- CONFIGURATION ---
WIDTH, HEIGHT = 800, 600
FPS           = 60
FOV           = 480          # FIX #38: Tuned to approximate SM64's 45-degree VFOV
VIEW_DISTANCE = 5500
NEAR_CLIP     = 8            # FIX #35: proper near-clip plane

# SM64 PC Port Camera
MOUSE_SENS_X  = 0.003
MOUSE_SENS_Y  = 0.002
PITCH_MIN     = -1.3         # FIX #17: slightly wider pitch range
PITCH_MAX     =  1.1
CAM_LERP      =  0.18
EYE_HEIGHT    = 38
HEAD_BOB_SPEED= 10.0
HEAD_BOB_AMT  = 3.0
CAM_MODE_FP   = 0            # FIX #33: camera mode - first person (Lakitu)
CAM_MODE_ORBIT= 1            # orbit / third-person style
KEY_TURN      = 0.05

# Movement — SM64 N64 scaled for 60 FPS
MOVE_ACCEL    = 1.5
MOVE_DECEL    = 0.80
MAX_SPEED     = 16
SPRINT_MULT   = 1.5
JUMP_FORCE    = 21
DOUBLE_JUMP_FORCE = 25       # FIX #18: triple jump system
TRIPLE_JUMP_FORCE = 32
LONG_JUMP_FORCE   = 16       # FIX #19: long jump
LONG_JUMP_HSPEED  = 22
BACKFLIP_FORCE    = 28       # FIX #20: backflip
GROUND_POUND_SPEED= 24       # FIX #21: ground pound
WALL_KICK_FORCE   = 22       # FIX #22: wall kick
WALL_KICK_HSPEED  = 12
SIDE_FLIP_FORCE   = 26       # FIX #23: side flip
DIVE_HSPEED       = 18       # dive move
GRAVITY       = 1.0
FALL_DAMAGE_THRESHOLD = 38   # FIX #10: fall damage threshold
FALL_DAMAGE_LETHAL    = 60   # lethal fall
WATER_GRAVITY = 0.3          # FIX #24: swimming
WATER_SWIM_SPEED = 10
SWIM_ACCEL    = 0.8
OOB_KILL_Y    = -600         # FIX #8: out of bounds kill plane

STAR_TOTAL    = 0             # FIX #14: calculated at init from actual level data

# ======================================================================
#  SM64 PC PORT — AUTHENTIC VERTEX COLOR PALETTES
# ======================================================================

# --- Castle Grounds ---
CG_GRASS_1      = (0,  158,   0)
CG_GRASS_2      = (0,  128,   0)
CG_PATH         = (172, 140,  96)
CG_STONE        = (136, 120, 104)
CG_MOAT         = (0,   80,  200)
CG_MOAT_DEEP    = (0,   50,  160)
CG_CASTLE_WALL  = (196, 170, 136)
CG_CASTLE_ROOF  = (152,  32,  16)
CG_CASTLE_TRIM  = (220, 200, 168)
CG_TREE_TRUNK   = ( 80,  44,  20)
CG_TREE_TOP     = ( 0,  136,   0)
CG_TREE_TOP2    = ( 0,  104,   0)
CG_BRIDGE       = (148, 104,  56)
CG_TOWER        = (180, 156, 120)

# --- Bob-omb Battlefield ---
BOB_GRASS_1  = (0,  160,   0)
BOB_GRASS_2  = (0,  128,   0)
BOB_DIRT     = (152, 112,  56)
BOB_PATH     = (180, 148,  96)
BOB_MTN_LOW  = (112,  80,  48)
BOB_MTN_MID  = ( 96,  64,  40)
BOB_MTN_TOP  = (192, 180, 160)
BOB_WATER    = (0,   104, 216)
BOB_FENCE    = (148, 104,  48)
BOB_SKY_TOP  = ( 56, 100, 184)
BOB_SKY_BOT  = (192, 220, 255)

# --- Whomp's Fortress ---
WF_STONE_1 = (160, 144, 120)
WF_STONE_2 = (128, 112,  88)
WF_GRASS   = (0,  148,   0)
WF_BRICK   = (144, 120,  88)
WF_DIRT    = (128,  96,  56)

# --- Jolly Roger Bay ---
JRB_WATER      = (0,   80, 200)
JRB_WATER_DEEP = (0,   40, 144)
JRB_SAND       = (216, 192, 128)
JRB_CAVE       = ( 56,  40,  32)
JRB_SHIP       = (100,  72,  44)
JRB_CORAL      = (240,  80,  56)
JRB_DOCK       = (140, 100,  60)

# --- Cool, Cool Mountain ---
CCM_SNOW_1 = (240, 248, 255)
CCM_SNOW_2 = (208, 224, 240)
CCM_ICE    = (136, 200, 232)
CCM_ROCK   = (104,  96,  88)
CCM_CABIN  = ( 96,  56,  32)
CCM_SLIDE  = (200, 232, 248)

# --- Big Boo's Haunt ---
BBH_WALL   = ( 56,  48,  64)
BBH_FLOOR  = ( 40,  32,  48)
BBH_ROOF   = ( 48,  40,  56)
BBH_BRICK  = ( 80,  64,  56)
BBH_GHOST  = (240, 240, 248)
BBH_FENCE  = ( 56,  44,  36)
BBH_GRAVE  = ( 96,  80,  72)
BBH_WINDOW = (255, 220,  80)

# --- Hazy Maze Cave ---
HMC_ROCK_1 = ( 80,  64,  48)
HMC_ROCK_2 = ( 64,  48,  36)
HMC_TOXIC  = ( 56, 200,  56)
HMC_METAL  = (160, 168, 176)
HMC_WATER  = (0,  104, 216)

# --- Lethal Lava Land ---
LLL_LAVA_1  = (255,  40,   0)
LLL_LAVA_2  = (255, 120,   0)
LLL_STONE   = ( 72,  56,  48)
LLL_METAL   = (128, 112,  96)
LLL_VOLCANO = ( 64,  40,  24)

# --- Shifting Sand Land ---
SSL_SAND_1    = (216, 188, 120)
SSL_SAND_2    = (192, 164, 104)
SSL_PYRAMID   = (200, 176, 112)
SSL_BRICK     = (176, 148,  96)
SSL_QUICKSAND = (184, 160, 104)
SSL_OASIS     = (0,  120, 200)
SSL_PALM      = (0,  120,   0)

# --- Dire, Dire Docks ---
DDD_WATER      = (0,  80, 200)
DDD_WATER_DEEP = (0,  40, 144)
DDD_DOCK       = (120,  88,  56)
DDD_METAL      = (136, 144, 152)
DDD_SUB        = ( 96, 104, 112)
DDD_FLOOR      = ( 56,  44,  36)

# --- Snowman's Land ---
SL_SNOW_1 = (248, 252, 255)
SL_SNOW_2 = (216, 232, 248)
SL_ICE    = (120, 192, 224)
SL_IGLOO  = (240, 248, 255)

# --- Wet-Dry World ---
WDW_BRICK  = (168, 148, 120)
WDW_WATER  = (0,  104, 216)
WDW_STONE  = (144, 128, 104)
WDW_SWITCH = ( 96, 176, 255)

# --- Tall Tall Mountain ---
TTM_GRASS    = (0,  152,   0)
TTM_DIRT     = (128,  88,  48)
TTM_ROCK     = (104,  88,  72)
TTM_SLIDE    = (160, 112,  64)
TTM_WATER    = (0,   96, 200)
TTM_MUSH_TOP = (216,  48,  32)
TTM_MUSH_STEM= (248, 216, 184)

# --- Tiny-Huge Island ---
THI_GRASS_1 = (0,  160,   0)
THI_GRASS_2 = (0,  128,   0)
THI_WATER   = (0,   96, 200)
THI_BEACH   = (216, 192, 128)
THI_PIPE    = (0,  136,   0)

# --- Tick Tock Clock ---
TTC_WOOD   = (144,  96,  48)
TTC_GEAR   = (248, 216,   0)
TTC_METAL  = (160, 168, 176)
TTC_HAND   = ( 56,  40,  24)

# --- Rainbow Ride ---
RR_RAINBOW = [(255,80,48),(255,160,32),(248,216,0),(80,200,80),(64,128,255),(176,80,240)]
RR_CLOUD   = (255, 255, 255)
RR_CARPET  = (216,  32,  32)
RR_HOUSE   = (200, 176, 144)

# --- Bowser stages ---
BDW_STONE  = ( 56,  40,  48)
BDW_LAVA   = (255,  40,   0)
BFS_METAL  = (120, 112, 104)
BITS_STONE = ( 64,  48,  56)

# --- Universal / HUD ---
WHITE         = (255, 255, 255)
BLACK         = (  0,   0,   0)
RED           = (220,  20,  60)
BLUE          = ( 32, 112, 224)
SKIN          = (252, 184, 120)
BROWN         = (139,  69,  19)
MUSTACHE_BLACK= ( 20,  20,  20)
BUTTON_GOLD   = (255, 215,   0)
EYE_BLUE      = ( 64, 148, 240)
YELLOW        = (255, 230,   0)
METAL_GREY    = (160, 168, 176)
ORANGE        = (255, 140,   0)
DARK_GREEN    = (  0,  80,   0)
DARK_GREY     = ( 64,  64,  64)
LIGHT_GREY    = (200, 208, 216)
DARK_BROWN    = ( 64,  32,  16)
DARK_STONE    = ( 72,  60,  52)
PURPLE        = (128,  48, 176)
PIPE_GREEN    = (  0, 136,   0)
CARPET_RED    = (200,  32,  24)
STAR_GOLD     = (255, 215,   0)
STAR_SHINE    = (255, 248, 160)
COIN_YELLOW   = (255, 200,   0)
MARIO_RED     = (200,  16,   8)
MARIO_BLUE    = ( 0,   72, 200)
HEALTH_PIE_BG = ( 40,  40,  40)
HEALTH_PIE_FG = ( 80, 200, 255)
HEALTH_PIE_LOW= (255,  60,  40)

# ======================================================================
#  SM64 PC PORT — AUTHENTIC SKY / FOG GRADIENTS
# ======================================================================
SM64_SKIES = {
    "castle_grounds": (( 56,100,184),(192,220,255),(172,204,248)),
    "castle_f1":      ((  8, 12, 28),( 28, 36, 72),( 16, 24, 52)),
    "castle_basement":(( 12,  8,  8),( 24, 16, 16),( 16, 12, 12)),
    "castle_upper":   (( 20, 28, 64),( 56, 72,160),( 36, 48,112)),
    "castle_top":     (( 56,100,184),(192,220,255),(172,204,248)),
    "c01_bob":        (( 56,100,184),(192,220,255),(172,204,248)),
    "c02_whomp":      (( 64,112,196),(200,224,255),(180,208,248)),
    "c03_jolly":      (( 48, 80,176),(160,200,248),(128,176,240)),
    "c04_cool":       ((168,208,240),(224,240,255),(208,232,255)),
    "c05_boo":        (( 16, 12, 24),( 40, 32, 56),( 28, 20, 40)),
    "c06_hazy":       ((  8, 12, 16),( 24, 28, 36),( 16, 20, 28)),
    "c07_lava":       (( 64, 16,  8),(160, 48, 16),( 96, 24, 12)),
    "c08_sand":       ((176,160, 96),(224,208,152),(204,188,128)),
    "c09_dock":       (( 40, 72,160),(152,192,240),(112,160,224)),
    "c10_snow":       ((192,224,248),(232,248,255),(216,240,255)),
    "c11_wet":        (( 56,100,184),(192,220,255),(172,204,248)),
    "c12_tall":       (( 56,112,196),(196,224,255),(176,208,248)),
    "c13_tiny":       (( 56,100,184),(192,220,255),(172,204,248)),
    "c14_clock":      (( 12, 16, 24),( 32, 40, 64),( 20, 28, 44)),
    "c15_rainbow":    (( 56,100,184),(192,220,255),(172,204,248)),
    "s_slide":        (( 24, 20, 36),( 64, 52, 96),( 44, 36, 68)),
    "s_wing":         (( 56,100,184),(192,220,255),(172,204,248)),
    "s_metal":        ((  8,  8, 16),( 24, 24, 40),( 16, 16, 28)),
    "s_vanish":       (( 16, 24, 48),( 40, 60,120),( 28, 40, 84)),
    "s_tower":        (( 56,100,184),(192,220,255),(172,204,248)),
    "b1_dark":        (( 24,  8, 16),( 56, 24, 40),( 36, 16, 28)),
    "b2_fire":        (( 80, 16,  8),(192, 56, 24),(128, 32, 16)),
    "b3_sky":         (( 48, 80,176),(160,200,248),(104,152,224)),
}

# ======================================================================
#  SFX SYNTHESIZER (no OST — short blips for gameplay feedback)
# ======================================================================
class SFXSynth:
    """Minimal synthesized SFX — no external files needed."""
    _cache: dict = {}

    @staticmethod
    def _make_sound(freq: float, duration: float, wave: str = "square",
                    volume: float = 0.15, fade_out: float = 0.0) -> pygame.mixer.Sound | None:
        try:
            sr = 22050
            n = int(sr * duration)
            if n < 1:
                return None
            buf = array.array('h', [0] * n)
            for i in range(n):
                t = i / sr
                env = 1.0
                if fade_out > 0 and t > duration - fade_out:
                    env = max(0.0, (duration - t) / fade_out)
                if wave == "square":
                    val = 1.0 if math.sin(2 * math.pi * freq * t) >= 0 else -1.0
                elif wave == "tri":
                    val = 2.0 * abs(2.0 * (freq * t - math.floor(freq * t + 0.5))) - 1.0
                elif wave == "noise":
                    val = random.uniform(-1, 1)
                else:
                    val = math.sin(2 * math.pi * freq * t)
                buf[i] = int(val * volume * env * 32767)
            snd = pygame.mixer.Sound(buffer=buf)
            return snd
        except Exception:
            return None

    @classmethod
    def get(cls, name: str) -> pygame.mixer.Sound | None:
        if name in cls._cache:
            return cls._cache[name]
        snd = None
        if name == "jump":
            snd = cls._make_sound(520, 0.08, "square", 0.12, 0.03)
        elif name == "double_jump":
            snd = cls._make_sound(620, 0.1, "square", 0.13, 0.04)
        elif name == "triple_jump":
            snd = cls._make_sound(780, 0.15, "square", 0.14, 0.06)
        elif name == "long_jump":
            snd = cls._make_sound(440, 0.12, "tri", 0.12, 0.05)
        elif name == "backflip":
            snd = cls._make_sound(660, 0.14, "square", 0.13, 0.05)
        elif name == "ground_pound":
            snd = cls._make_sound(120, 0.18, "square", 0.2, 0.08)
        elif name == "wall_kick":
            snd = cls._make_sound(580, 0.1, "tri", 0.12, 0.04)
        elif name == "coin":
            snd = cls._make_sound(988, 0.06, "square", 0.1, 0.02)
        elif name == "star":
            snd = cls._make_sound(1200, 0.3, "tri", 0.15, 0.15)
        elif name == "hurt":
            snd = cls._make_sound(200, 0.2, "noise", 0.12, 0.1)
        elif name == "death":
            snd = cls._make_sound(160, 0.5, "tri", 0.15, 0.3)
        elif name == "enter":
            snd = cls._make_sound(660, 0.12, "square", 0.1, 0.05)
        elif name == "pause":
            snd = cls._make_sound(440, 0.08, "square", 0.08, 0.03)
        elif name == "menu_move":
            snd = cls._make_sound(880, 0.04, "square", 0.06, 0.02)
        elif name == "oneup":
            snd = cls._make_sound(1320, 0.2, "tri", 0.12, 0.1)
        elif name == "splash":
            snd = cls._make_sound(300, 0.15, "noise", 0.1, 0.08)
        elif name == "dive":
            snd = cls._make_sound(350, 0.1, "tri", 0.1, 0.04)
        cls._cache[name] = snd
        return snd

    @classmethod
    def play(cls, name: str):
        snd = cls.get(name)
        if snd:
            snd.play()


# ======================================================================
#  3D ENGINE CORE
# ======================================================================
class Vector3:
    __slots__ = ['x','y','z']
    def __init__(self, x: float, y: float, z: float):
        self.x = x; self.y = y; self.z = z

class Face:
    __slots__ = ['indices','color','avg_z','normal']
    def __init__(self, indices: list, color: tuple):
        self.indices = indices; self.color = color; self.avg_z = 0; self.normal = None

def _calc_normal(v0: Vector3, v1: Vector3, v2: Vector3) -> tuple:
    """Calculate face normal from 3 vertices. FIX #5/#6/#7: replaces all hardcoded normals."""
    ax, ay, az = v1.x - v0.x, v1.y - v0.y, v1.z - v0.z
    bx, by, bz = v2.x - v0.x, v2.y - v0.y, v2.z - v0.z
    nx = ay * bz - az * by
    ny = az * bx - ax * bz
    nz = ax * by - ay * bx
    length = math.sqrt(nx * nx + ny * ny + nz * nz)
    if length < 1e-8:
        return (0.0, 1.0, 0.0)
    return (nx / length, ny / length, nz / length)


class Mesh:
    def __init__(self, x: float = 0, y: float = 0, z: float = 0):
        self.x = x; self.y = y; self.z = z
        self.vertices: list[Vector3] = []
        self.faces: list[Face] = []
        self.yaw: float = 0
        # Collision data: list of (x,y,z,hw,hh,hd) axis-aligned boxes
        self.colliders: list[tuple] = []
        # Water planes: list of (x,z,hw,hd,y) for swim detection
        self.water_planes: list[tuple] = []

    def _add_face(self, indices: list, color: tuple):
        """Add a face with properly calculated normal. FIX #5."""
        face = Face(indices, color)
        v0 = self.vertices[indices[0]]
        v1 = self.vertices[indices[1]]
        v2 = self.vertices[indices[2]]
        face.normal = _calc_normal(v0, v1, v2)
        self.faces.append(face)

    def add_cube(self, w, h, d, ox, oy, oz, color, collide=False):
        si = len(self.vertices)
        hw, hh, hd = w / 2, h / 2, d / 2
        for cx, cy, cz in [(-hw,-hh,-hd),(hw,-hh,-hd),(hw,hh,-hd),(-hw,hh,-hd),
                            (-hw,-hh, hd),(hw,-hh, hd),(hw, hh, hd),(-hw, hh, hd)]:
            self.vertices.append(Vector3(cx + ox, cy + oy, cz + oz))
        face_defs = [
            ([0,1,2,3], color), ([5,4,7,6], color), ([4,0,3,7], color),
            ([1,5,6,2], color), ([3,2,6,7], color), ([4,5,1,0], color),
        ]
        for fi, fc in face_defs:
            shifted = [i + si for i in fi]
            self._add_face(shifted, fc)
        if collide:
            self.colliders.append((ox, oy, oz, hw, hh, hd))

    def add_pyramid(self, bw, height, ox, oy, oz, color):
        """FIX #5: pyramid normals now calculated per-face."""
        si = len(self.vertices)
        hw = bw / 2
        for cx, cz in [(-hw,-hw),(hw,-hw),(hw,hw),(-hw,hw)]:
            self.vertices.append(Vector3(cx + ox, oy, cz + oz))
        self.vertices.append(Vector3(ox, oy + height, oz))
        for tri in [(0,1,4),(1,2,4),(2,3,4),(3,0,4)]:
            self._add_face([si + t for t in tri], color)

    def add_slope(self, w, d, h_front, h_back, ox, oy, oz, color):
        """FIX #7: slope normals now calculated per-face."""
        si = len(self.vertices)
        hw, hd = w / 2, d / 2
        self.vertices.append(Vector3(-hw + ox, oy,            -hd + oz))
        self.vertices.append(Vector3( hw + ox, oy,            -hd + oz))
        self.vertices.append(Vector3( hw + ox, oy,             hd + oz))
        self.vertices.append(Vector3(-hw + ox, oy,             hd + oz))
        self.vertices.append(Vector3(-hw + ox, oy + h_back,   -hd + oz))
        self.vertices.append(Vector3( hw + ox, oy + h_back,   -hd + oz))
        self.vertices.append(Vector3( hw + ox, oy + h_front,   hd + oz))
        self.vertices.append(Vector3(-hw + ox, oy + h_front,   hd + oz))
        for fi in [[si+4,si+5,si+6,si+7],[si+3,si+2,si+6,si+7],
                    [si+1,si+0,si+4,si+5],[si+0,si+3,si+7,si+4],[si+2,si+1,si+5,si+6]]:
            self._add_face(fi, color)

    def add_hill(self, radius, height, ox, oy, oz, color, color2=None, segments=8):
        """FIX #6: hill normals now calculated per-face."""
        if color2 is None:
            color2 = color
        si = len(self.vertices)
        self.vertices.append(Vector3(ox, oy + height, oz))
        for i in range(segments):
            a = 2 * math.pi * i / segments
            self.vertices.append(Vector3(ox + math.cos(a) * radius, oy, oz + math.sin(a) * radius))
        for i in range(segments):
            a = 2 * math.pi * i / segments
            self.vertices.append(Vector3(ox + math.cos(a) * radius * 0.6, oy + height * 0.7,
                                         oz + math.sin(a) * radius * 0.6))
        for i in range(segments):
            j = (i + 1) % segments
            self._add_face([si, si + 1 + segments + i, si + 1 + segments + j], color)
        for i in range(segments):
            j = (i + 1) % segments
            self._add_face([si+1+i, si+1+j, si+1+segments+j, si+1+segments+i], color2)

    def add_water_plane(self, x, z, hw, hd, y):
        """FIX #24: register a water surface for swim detection."""
        self.water_planes.append((x, z, hw, hd, y))


# ======================================================================
#  MARIO — SM64 Movement System (FIX #18-#24, #10, #11, #12, #13)
# ======================================================================
# Action states
ACT_IDLE       = 0
ACT_WALK       = 1
ACT_JUMP       = 2
ACT_DOUBLE_JUMP= 3
ACT_TRIPLE_JUMP= 4
ACT_FREEFALL   = 5
ACT_LONG_JUMP  = 6
ACT_BACKFLIP   = 7
ACT_GROUND_POUND     = 8
ACT_GROUND_POUND_LAND= 9
ACT_WALL_KICK  = 10
ACT_SIDE_FLIP  = 11
ACT_DIVE       = 12
ACT_SWIM       = 13
ACT_DEAD       = 14
ACT_STAR_GET   = 15
ACT_SLIDE      = 16

class Mario(Mesh):
    def __init__(self, x, y, z):
        super().__init__(x, y, z)
        self.dy: float = 0
        self.dx: float = 0  # horizontal velocity for special moves
        self.dz: float = 0
        self.action: int = ACT_IDLE
        self.prev_action: int = ACT_IDLE
        self.star_count: int = 0
        self.coins: int = 0
        self.lives: int = 4
        self.health: int = 8
        self.max_health: int = 8
        self.invuln_timer: int = 0
        self.jump_count: int = 0  # for triple jump combo
        self.jump_timer: int = 0  # frames since last landing (for combo window)
        self.ground_pound_timer: int = 0
        self.on_ground: bool = True
        self.in_water: bool = False
        self.water_y: float = 0
        self.fall_start_y: float = 0  # track where we started falling from
        self.death_timer: int = 0
        self.star_get_timer: int = 0
        self.facing_yaw: float = 0
        self.slide_timer: int = 0
        self.wall_kick_dir: float = 0

    @property
    def is_jumping(self) -> bool:
        return self.action in (ACT_JUMP, ACT_DOUBLE_JUMP, ACT_TRIPLE_JUMP,
                               ACT_FREEFALL, ACT_LONG_JUMP, ACT_BACKFLIP,
                               ACT_WALL_KICK, ACT_SIDE_FLIP, ACT_DIVE)

    @property
    def is_airborne(self) -> bool:
        return not self.on_ground and self.action != ACT_SWIM

    def take_damage(self, amount: int = 1):
        """FIX #12: health now actually decreases."""
        if self.invuln_timer > 0 or self.action == ACT_DEAD:
            return
        self.health = max(0, self.health - amount)
        self.invuln_timer = 90  # 1.5 seconds
        SFXSynth.play("hurt")
        if self.health <= 0:
            self.die()

    def die(self):
        """FIX #11: death mechanic."""
        if self.action == ACT_DEAD:
            return
        self.action = ACT_DEAD
        self.death_timer = 180  # 3 seconds
        self.dy = JUMP_FORCE * 0.8
        self.lives -= 1  # FIX #13: lives decrease
        SFXSynth.play("death")

    def collect_star(self):
        """Star get celebration."""
        self.action = ACT_STAR_GET
        self.star_get_timer = 120  # 2 seconds
        self.dy = 0
        self.on_ground = True
        SFXSynth.play("star")

    def start_jump(self):
        """SM64 jump system with triple jump combo. FIX #18."""
        if self.action == ACT_DEAD or self.action == ACT_STAR_GET:
            return
        if self.in_water:
            # Swim upward
            self.dy = min(self.dy + SWIM_ACCEL * 3, WATER_SWIM_SPEED)
            SFXSynth.play("splash")
            return
        if not self.on_ground:
            return

        if self.jump_timer < 12 and self.jump_count == 1:
            # Double jump
            self.dy = DOUBLE_JUMP_FORCE
            self.action = ACT_DOUBLE_JUMP
            self.jump_count = 2
            SFXSynth.play("double_jump")
        elif self.jump_timer < 12 and self.jump_count == 2:
            # Triple jump
            self.dy = TRIPLE_JUMP_FORCE
            self.action = ACT_TRIPLE_JUMP
            self.jump_count = 0
            SFXSynth.play("triple_jump")
        else:
            # Single jump
            self.dy = JUMP_FORCE
            self.action = ACT_JUMP
            self.jump_count = 1
            SFXSynth.play("jump")

        self.on_ground = False
        self.fall_start_y = self.y

    def start_long_jump(self, speed: float):
        """FIX #19: long jump."""
        if not self.on_ground or self.action == ACT_DEAD:
            return
        self.dy = LONG_JUMP_FORCE
        fwd_x = -math.sin(self.facing_yaw)
        fwd_z = -math.cos(self.facing_yaw)
        self.dx = fwd_x * LONG_JUMP_HSPEED
        self.dz = fwd_z * LONG_JUMP_HSPEED
        self.action = ACT_LONG_JUMP
        self.on_ground = False
        self.fall_start_y = self.y
        SFXSynth.play("long_jump")

    def start_backflip(self):
        """FIX #20: backflip."""
        if not self.on_ground or self.action == ACT_DEAD:
            return
        self.dy = BACKFLIP_FORCE
        fwd_x = math.sin(self.facing_yaw)
        fwd_z = math.cos(self.facing_yaw)
        self.dx = fwd_x * 6
        self.dz = fwd_z * 6
        self.action = ACT_BACKFLIP
        self.on_ground = False
        self.fall_start_y = self.y
        SFXSynth.play("backflip")

    def start_ground_pound(self):
        """FIX #21: ground pound."""
        if self.on_ground or self.action == ACT_DEAD or self.action == ACT_GROUND_POUND:
            return
        self.dy = 4  # brief upward hop
        self.dx = 0
        self.dz = 0
        self.action = ACT_GROUND_POUND
        self.ground_pound_timer = 8  # hover frames
        SFXSynth.play("ground_pound")

    def start_dive(self, yaw: float):
        """Dive move."""
        if self.action == ACT_DEAD or self.on_ground:
            return
        fwd_x = -math.sin(yaw)
        fwd_z = -math.cos(yaw)
        self.dx = fwd_x * DIVE_HSPEED
        self.dz = fwd_z * DIVE_HSPEED
        self.dy = max(self.dy, 4)
        self.action = ACT_DIVE
        SFXSynth.play("dive")

    def update(self, floor_y: float = 0, level_mesh: Mesh | None = None):
        """Full physics update. FIX #3: actual floor collision. FIX #10: fall damage."""
        if self.invuln_timer > 0:
            self.invuln_timer -= 1

        if self.action == ACT_DEAD:
            self.death_timer -= 1
            self.dy -= GRAVITY
            self.y += self.dy
            return self.death_timer <= 0  # returns True when death sequence done

        if self.action == ACT_STAR_GET:
            self.star_get_timer -= 1
            return self.star_get_timer <= 0

        # Water detection (FIX #24)
        was_in_water = self.in_water
        self.in_water = False
        if level_mesh:
            for wx, wz, whw, whd, wy in level_mesh.water_planes:
                if (abs(self.x - wx) < whw and abs(self.z - wz) < whd and self.y < wy):
                    self.in_water = True
                    self.water_y = wy
                    break
        if self.in_water and not was_in_water:
            SFXSynth.play("splash")
            self.action = ACT_SWIM
            self.jump_count = 0

        # Ground pound hover
        if self.action == ACT_GROUND_POUND:
            if self.ground_pound_timer > 0:
                self.ground_pound_timer -= 1
                self.dy = 0
                return False
            else:
                self.dy = -GROUND_POUND_SPEED

        # Gravity
        if self.in_water:
            self.dy -= WATER_GRAVITY
            self.dy = max(self.dy, -4)  # terminal velocity in water
            if self.dy > WATER_SWIM_SPEED:
                self.dy = WATER_SWIM_SPEED
        else:
            self.dy -= GRAVITY

        self.y += self.dy

        # Horizontal velocity for special moves
        if self.action in (ACT_LONG_JUMP, ACT_BACKFLIP, ACT_DIVE, ACT_WALL_KICK):
            self.x += self.dx
            self.z += self.dz
            self.dx *= 0.98
            self.dz *= 0.98

        # Floor collision (FIX #3)
        actual_floor = floor_y
        # Check colliders for floor height
        if level_mesh:
            for cx, cy, cz, chw, chh, chd in level_mesh.colliders:
                if (abs(self.x - cx) < chw and abs(self.z - cz) < chd):
                    top = cy + chh
                    if self.y <= top and self.y + self.dy <= top:
                        actual_floor = max(actual_floor, top)

        if self.y <= actual_floor:
            # Landing
            if not self.on_ground:
                # FIX #10: fall damage
                fall_dist = self.fall_start_y - actual_floor
                if fall_dist > FALL_DAMAGE_THRESHOLD and self.action != ACT_GROUND_POUND:
                    if fall_dist > FALL_DAMAGE_LETHAL:
                        self.take_damage(8)
                    else:
                        dmg = int((fall_dist - FALL_DAMAGE_THRESHOLD) / 10) + 1
                        self.take_damage(min(dmg, 3))

                if self.action == ACT_GROUND_POUND:
                    self.action = ACT_GROUND_POUND_LAND
                    self.ground_pound_timer = 12

            self.y = actual_floor
            self.dy = 0
            was_airborne = not self.on_ground
            self.on_ground = True

            if was_airborne and self.action not in (ACT_GROUND_POUND_LAND, ACT_DEAD, ACT_STAR_GET):
                self.action = ACT_IDLE
                self.dx = 0
                self.dz = 0

            if self.action == ACT_GROUND_POUND_LAND:
                self.ground_pound_timer -= 1
                if self.ground_pound_timer <= 0:
                    self.action = ACT_IDLE
        else:
            if self.on_ground:
                self.fall_start_y = self.y
            self.on_ground = False
            if self.action in (ACT_IDLE, ACT_WALK):
                self.action = ACT_FREEFALL

        # Jump timer for combo tracking
        if self.on_ground:
            self.jump_timer += 1
        else:
            self.jump_timer = 0

        # OOB kill plane (FIX #8)
        if self.y < OOB_KILL_Y:
            self.die()

        return False


# ======================================================================
#  COLLECTIBLES
# ======================================================================
class Star(Mesh):
    def __init__(self, x, y, z, sid=0):
        super().__init__(x, y, z)
        self.star_id = sid
        self.collected = False
        self.add_cube(10, 40, 10, 0, 0, 0, STAR_GOLD)
        self.add_cube(40, 10, 10, 0, 0, 0, STAR_GOLD)
        self.add_cube(10, 10, 40, 0, 0, 0, STAR_SHINE)

class Coin(Mesh):
    def __init__(self, x, y, z):
        super().__init__(x, y, z)
        self.collected = False
        self.add_cube(8, 12, 3, 0, 0, 0, COIN_YELLOW)
        self.add_cube(4, 8, 4,  0, 0, 0, BUTTON_GOLD)

class RedCoin(Mesh):
    """FIX #36: red coins added."""
    def __init__(self, x, y, z):
        super().__init__(x, y, z)
        self.collected = False
        self.add_cube(8, 12, 3, 0, 0, 0, RED)
        self.add_cube(4, 8, 4,  0, 0, 0, MARIO_RED)

class OneUp(Mesh):
    """FIX #37: 1-UP mushrooms."""
    def __init__(self, x, y, z):
        super().__init__(x, y, z)
        self.collected = False
        self.add_cube(12, 8, 12, 0, 0, 0, WHITE)
        self.add_cube(14, 4, 14, 0, 6, 0, PIPE_GREEN)



# ======================================================================
#  PARTICLE SYSTEM — SM64 PC Port visual effects
# ======================================================================
class Particle:
    """Single particle with position, velocity, lifetime, and color."""
    __slots__ = ['x','y','z','dx','dy','dz','life','max_life','color','size','kind']
    def __init__(self, x, y, z, dx, dy, dz, life, color, size=3, kind="spark"):
        self.x = x; self.y = y; self.z = z
        self.dx = dx; self.dy = dy; self.dz = dz
        self.life = life; self.max_life = life
        self.color = color; self.size = size; self.kind = kind

    def update(self) -> bool:
        """Update particle. Returns False when dead."""
        self.x += self.dx; self.y += self.dy; self.z += self.dz
        if self.kind == "spark":
            self.dy -= 0.3
            self.dx *= 0.96; self.dz *= 0.96
        elif self.kind == "dust":
            self.dy += 0.1
            self.dx *= 0.92; self.dz *= 0.92
        elif self.kind == "fire":
            self.dy += 0.2
            self.dx *= 0.94; self.dz *= 0.94
        elif self.kind == "bubble":
            self.dy += 0.15
            self.dx += random.uniform(-0.1, 0.1)
            self.dz += random.uniform(-0.1, 0.1)
        elif self.kind == "snow":
            self.dy -= 0.05
            self.dx += random.uniform(-0.2, 0.2)
            self.dz += random.uniform(-0.2, 0.2)
        elif self.kind == "star_bit":
            self.dy -= 0.15
            self.dx *= 0.97; self.dz *= 0.97
        self.life -= 1
        return self.life > 0


class ParticleSystem:
    """Manages all active particles with pooling."""
    MAX_PARTICLES = 200

    def __init__(self):
        self.particles: list[Particle] = []

    def emit(self, x, y, z, kind="spark", count=5, color=None, spread=3.0, speed=4.0):
        """Emit particles at a position."""
        if color is None:
            color = STAR_GOLD
        for _ in range(count):
            if len(self.particles) >= self.MAX_PARTICLES:
                break
            dx = random.uniform(-spread, spread) * (speed / 4)
            dy = random.uniform(speed * 0.5, speed * 1.5)
            dz = random.uniform(-spread, spread) * (speed / 4)
            life = random.randint(15, 40)
            size = random.randint(2, 5)
            self.particles.append(Particle(x, y, z, dx, dy, dz, life, color, size, kind))

    def emit_coin_sparkle(self, x, y, z):
        self.emit(x, y, z, "spark", 8, COIN_YELLOW, 2.0, 3.0)

    def emit_star_burst(self, x, y, z):
        for _ in range(20):
            if len(self.particles) >= self.MAX_PARTICLES:
                break
            angle = random.uniform(0, math.pi * 2)
            elev = random.uniform(-0.5, 1.0)
            spd = random.uniform(3, 8)
            dx = math.cos(angle) * spd
            dz = math.sin(angle) * spd
            dy = elev * spd + 4
            c = random.choice([STAR_GOLD, STAR_SHINE, WHITE, YELLOW])
            self.particles.append(Particle(x, y, z, dx, dy, dz, 50, c, 4, "star_bit"))

    def emit_dust(self, x, y, z):
        self.emit(x, y, z, "dust", 6, (180, 160, 140), 2.0, 1.5)

    def emit_splash(self, x, y, z):
        for _ in range(12):
            if len(self.particles) >= self.MAX_PARTICLES:
                break
            angle = random.uniform(0, math.pi * 2)
            spd = random.uniform(2, 5)
            dx = math.cos(angle) * spd
            dz = math.sin(angle) * spd
            dy = random.uniform(3, 7)
            self.particles.append(Particle(x, y, z, dx, dy, dz, 30, (100, 180, 255), 3, "bubble"))

    def emit_fire(self, x, y, z):
        for _ in range(4):
            if len(self.particles) >= self.MAX_PARTICLES:
                break
            dx = random.uniform(-1, 1)
            dz = random.uniform(-1, 1)
            dy = random.uniform(1, 3)
            c = random.choice([LLL_LAVA_1, LLL_LAVA_2, ORANGE, YELLOW])
            self.particles.append(Particle(x, y, z, dx, dy, dz, 25, c, 4, "fire"))

    def emit_snow(self, x, y, z, radius=400):
        for _ in range(3):
            if len(self.particles) >= self.MAX_PARTICLES:
                break
            px = x + random.uniform(-radius, radius)
            pz = z + random.uniform(-radius, radius)
            py = y + random.uniform(100, 300)
            dx = random.uniform(-0.5, 0.5)
            dz = random.uniform(-0.5, 0.5)
            self.particles.append(Particle(px, py, pz, dx, -0.8, dz, 120, WHITE, 2, "snow"))

    def emit_ground_pound_ring(self, x, y, z):
        for i in range(16):
            angle = i * math.pi * 2 / 16
            spd = 6
            dx = math.cos(angle) * spd
            dz = math.sin(angle) * spd
            self.particles.append(Particle(x, y + 2, z, dx, 1.5, dz, 20, (200, 180, 140), 3, "dust"))

    def emit_death_sparkle(self, x, y, z):
        for _ in range(30):
            if len(self.particles) >= self.MAX_PARTICLES:
                break
            angle = random.uniform(0, math.pi * 2)
            elev = random.uniform(0, math.pi)
            spd = random.uniform(2, 6)
            dx = math.cos(angle) * math.sin(elev) * spd
            dy = math.cos(elev) * spd + 3
            dz = math.sin(angle) * math.sin(elev) * spd
            c = random.choice([MARIO_RED, MARIO_BLUE, WHITE, SKIN])
            self.particles.append(Particle(x, y, z, dx, dy, dz, 60, c, 3, "star_bit"))

    def update(self):
        self.particles = [p for p in self.particles if p.update()]

    def render(self, screen, cam_x, cam_y, cam_z, cam_yaw, cam_pitch, cx, cy):
        """Render particles as simple projected dots."""
        c_cos = math.cos(-cam_yaw); c_sin = math.sin(-cam_yaw)
        p_cos = math.cos(-cam_pitch); p_sin = math.sin(-cam_pitch)

        for p in self.particles:
            dcx = p.x - cam_x; dcy = p.y - cam_y; dcz = p.z - cam_z
            xx = dcx * c_cos - dcz * c_sin
            zz = dcx * c_sin + dcz * c_cos
            yy = dcy
            yy2 = yy * p_cos - zz * p_sin
            zz2 = yy * p_sin + zz * p_cos
            if zz2 < NEAR_CLIP:
                continue
            s = FOV / zz2
            sx = int(xx * s + cx); sy = int(-yy2 * s + cy)
            if 0 <= sx < WIDTH and 0 <= sy < HEIGHT:
                alpha = min(255, int(255 * p.life / p.max_life))
                r, g, b = p.color
                r = min(255, int(r * alpha / 255))
                g = min(255, int(g * alpha / 255))
                b = min(255, int(b * alpha / 255))
                size = max(1, int(p.size * FOV / zz2 * 0.15))
                if size <= 1:
                    screen.set_at((sx, sy), (r, g, b))
                else:
                    pygame.draw.circle(screen, (r, g, b), (sx, sy), size)


# ======================================================================
#  ENEMY SYSTEM — SM64 PC Port enemies with AI behaviors
# ======================================================================
ENEMY_GOOMBA       = 0
ENEMY_BOBOMB       = 1
ENEMY_KOOPA        = 2
ENEMY_CHAIN_CHOMP  = 3
ENEMY_PIRANHA      = 4
ENEMY_THWOMP       = 5
ENEMY_BOO          = 6
ENEMY_BULLET_BILL  = 7
ENEMY_AMP          = 8
ENEMY_WHOMP        = 9
ENEMY_FLYGUY       = 10
ENEMY_MONTY_MOLE   = 11
ENEMY_POKEY        = 12
ENEMY_SKEETER      = 13
ENEMY_SNUFIT       = 14
ENEMY_HEAVE_HO     = 15

# Enemy colors
GOOMBA_BODY   = (160, 100, 48)
GOOMBA_FEET   = (100, 60, 28)
GOOMBA_FACE   = (200, 140, 80)
BOBOMB_BODY   = (24, 24, 32)
BOBOMB_EYES   = (255, 255, 255)
BOBOMB_FEET   = (200, 160, 40)
BOBOMB_FUSE   = (160, 120, 40)
KOOPA_SHELL   = (0, 160, 0)
KOOPA_SHELL_R = (200, 32, 32)
KOOPA_BODY    = (240, 200, 80)
CHOMP_BODY    = (24, 24, 32)
CHOMP_EYES    = (255, 255, 255)
CHOMP_CHAIN   = (64, 56, 48)
PIRANHA_STEM  = (0, 140, 0)
PIRANHA_HEAD  = (200, 32, 32)
PIRANHA_LIPS  = (255, 255, 255)
PIRANHA_SPOTS = (255, 255, 255)
THWOMP_BODY   = (128, 128, 144)
THWOMP_FACE   = (96, 96, 112)
THWOMP_SPIKE  = (160, 160, 176)
BOO_BODY      = (240, 240, 248)
BOO_FACE      = (200, 200, 216)
BOO_TONGUE    = (200, 48, 48)
BULLET_BODY   = (24, 24, 32)
BULLET_EYES   = (255, 255, 255)
BULLET_ARMS   = (64, 56, 48)
AMP_BODY      = (24, 24, 32)
AMP_SPARK     = (255, 255, 80)
WHOMP_BODY    = (128, 112, 96)
WHOMP_FACE    = (100, 80, 64)
FLYGUY_BODY   = (200, 32, 32)
FLYGUY_MASK   = (255, 255, 255)
MONTY_BODY    = (120, 80, 40)
MONTY_BELLY   = (200, 160, 100)
POKEY_BODY    = (0, 160, 0)
POKEY_SPIKE   = (200, 180, 40)
SKEETER_BODY  = (80, 120, 200)
SKEETER_LEGS  = (40, 60, 100)
SNUFIT_BODY   = (80, 72, 96)
SNUFIT_MASK   = (255, 255, 255)
HEAVE_HO_BODY = (160, 32, 32)
HEAVE_HO_PLATE= (200, 180, 40)


class Enemy(Mesh):
    """Base enemy with SM64-style AI behaviors."""
    CHASE_RANGE  = 400
    PATROL_RANGE = 200
    HIT_RANGE    = 40
    STOMP_RANGE  = 50

    def __init__(self, x, y, z, kind=ENEMY_GOOMBA, patrol_radius=200):
        super().__init__(x, y, z)
        self.kind = kind
        self.alive = True
        self.home_x = x; self.home_z = z
        self.patrol_radius = patrol_radius
        self.patrol_angle = random.uniform(0, math.pi * 2)
        self.patrol_speed = 0.01 + random.uniform(0, 0.005)
        self.move_speed = 1.2
        self.chase_speed = 2.5
        self.dy_enemy = 0
        self.on_ground_enemy = True
        self.state = 0  # 0=patrol, 1=chase, 2=attack, 3=stunned, 4=dead
        self.state_timer = 0
        self.facing = 0
        self.anim_timer = 0
        self.hit_flash = 0
        self.bounce_height = 0
        self.attack_cooldown = 0
        self.stunned_timer = 0
        self.gravity = 0.8
        self.health = 1
        self.coin_drop = 1
        self.damage = 1
        self.aggro_range = 400
        self.deaggro_range = 600
        self._build_model()

    def _build_model(self):
        """Build 3D model based on enemy type."""
        if self.kind == ENEMY_GOOMBA:
            self.add_cube(16, 16, 14, 0, 8, 0, GOOMBA_BODY)
            self.add_cube(18, 6, 16, 0, 18, 0, GOOMBA_FACE)
            self.add_cube(8, 4, 10, -8, 2, 0, GOOMBA_FEET)
            self.add_cube(8, 4, 10, 8, 2, 0, GOOMBA_FEET)
            self.add_cube(4, 4, 2, -5, 20, 8, BLACK)
            self.add_cube(4, 4, 2, 5, 20, 8, BLACK)
            self.add_cube(6, 3, 2, 0, 14, 8, BLACK)
            self.health = 1; self.coin_drop = 1
            self.move_speed = 1.0; self.chase_speed = 2.0
        elif self.kind == ENEMY_BOBOMB:
            self.add_cube(14, 14, 14, 0, 7, 0, BOBOMB_BODY)
            self.add_cube(4, 4, 2, -5, 14, 8, BOBOMB_EYES)
            self.add_cube(4, 4, 2, 5, 14, 8, BOBOMB_EYES)
            self.add_cube(2, 2, 2, -5, 14, 9, BLACK)
            self.add_cube(2, 2, 2, 5, 14, 9, BLACK)
            self.add_cube(6, 4, 6, -6, 2, 0, BOBOMB_FEET)
            self.add_cube(6, 4, 6, 6, 2, 0, BOBOMB_FEET)
            self.add_cube(2, 8, 2, 0, 18, 0, BOBOMB_FUSE)
            self.add_cube(4, 4, 4, 0, 24, 0, ORANGE)
            self.health = 1; self.coin_drop = 1
            self.move_speed = 0.8; self.chase_speed = 3.0
            self.aggro_range = 300; self.damage = 2
        elif self.kind == ENEMY_KOOPA:
            self.add_cube(12, 20, 12, 0, 10, 0, KOOPA_BODY)
            self.add_cube(18, 14, 16, 0, 14, -2, KOOPA_SHELL)
            self.add_cube(8, 8, 8, 0, 24, 6, KOOPA_BODY)
            self.add_cube(3, 3, 2, -3, 26, 10, BLACK)
            self.add_cube(3, 3, 2, 3, 26, 10, BLACK)
            self.add_cube(6, 4, 6, -6, 2, 0, KOOPA_BODY)
            self.add_cube(6, 4, 6, 6, 2, 0, KOOPA_BODY)
            self.health = 1; self.coin_drop = 1
            self.move_speed = 1.5; self.chase_speed = 2.8
        elif self.kind == ENEMY_CHAIN_CHOMP:
            self.add_cube(32, 32, 32, 0, 16, 0, CHOMP_BODY)
            self.add_cube(10, 10, 4, -10, 24, 18, CHOMP_EYES)
            self.add_cube(10, 10, 4, 10, 24, 18, CHOMP_EYES)
            self.add_cube(5, 5, 5, -10, 24, 20, BLACK)
            self.add_cube(5, 5, 5, 10, 24, 20, BLACK)
            self.add_cube(24, 6, 8, 0, 8, 18, WHITE)
            for i in range(5):
                self.add_cube(6, 6, 6, -i * 8, 4, -20 - i * 8, CHOMP_CHAIN)
            self.add_cube(8, 16, 8, -40, 8, -60, DARK_GREY)
            self.health = 3; self.coin_drop = 5
            self.move_speed = 0; self.chase_speed = 5.0
            self.aggro_range = 200; self.damage = 3
            self.patrol_radius = 80
        elif self.kind == ENEMY_PIRANHA:
            self.add_cube(6, 40, 6, 0, 20, 0, PIRANHA_STEM)
            self.add_cube(20, 16, 16, 0, 44, 0, PIRANHA_HEAD)
            self.add_cube(16, 4, 12, 0, 36, 0, PIRANHA_LIPS)
            self.add_cube(4, 4, 2, -6, 50, 9, BLACK)
            self.add_cube(4, 4, 2, 6, 50, 9, BLACK)
            for dx in [-8, 8]:
                for dz in [-6, 6]:
                    self.add_cube(3, 3, 3, dx, 50, dz, PIRANHA_SPOTS)
            self.health = 1; self.coin_drop = 2
            self.move_speed = 0; self.chase_speed = 0
            self.aggro_range = 120; self.damage = 2
        elif self.kind == ENEMY_THWOMP:
            self.add_cube(48, 48, 48, 0, 24, 0, THWOMP_BODY)
            self.add_cube(40, 40, 4, 0, 24, 26, THWOMP_FACE)
            self.add_cube(8, 8, 4, -12, 32, 27, RED)
            self.add_cube(8, 8, 4, 12, 32, 27, RED)
            self.add_cube(16, 4, 4, 0, 20, 27, BLACK)
            for corner in [(-24,0,-24),(24,0,-24),(-24,0,24),(24,0,24),
                           (-24,48,-24),(24,48,-24),(-24,48,24),(24,48,24)]:
                self.add_cube(8, 8, 8, corner[0], corner[1], corner[2], THWOMP_SPIKE)
            self.health = 99; self.coin_drop = 0
            self.move_speed = 0; self.chase_speed = 0
            self.aggro_range = 100; self.damage = 3
            self.bounce_height = 120
        elif self.kind == ENEMY_BOO:
            self.add_cube(24, 24, 20, 0, 12, 0, BOO_BODY)
            self.add_cube(20, 20, 4, 0, 14, 12, BOO_FACE)
            self.add_cube(6, 8, 4, -6, 18, 13, BLACK)
            self.add_cube(6, 8, 4, 6, 18, 13, BLACK)
            self.add_cube(12, 6, 4, 0, 8, 13, BOO_TONGUE)
            self.add_cube(8, 6, 8, -14, 6, -4, BOO_BODY)
            self.add_cube(8, 6, 8, 14, 6, -4, BOO_BODY)
            self.health = 1; self.coin_drop = 1
            self.move_speed = 0.8; self.chase_speed = 2.0
            self.aggro_range = 300; self.damage = 1
            self.gravity = 0  # Floats
        elif self.kind == ENEMY_BULLET_BILL:
            self.add_cube(16, 16, 32, 0, 8, 0, BULLET_BODY)
            self.add_cube(12, 12, 4, 0, 10, 18, BULLET_EYES)
            self.add_cube(4, 4, 4, -4, 12, 19, WHITE)
            self.add_cube(4, 4, 4, 4, 12, 19, WHITE)
            self.add_cube(8, 4, 8, -12, 4, -8, BULLET_ARMS)
            self.add_cube(8, 4, 8, 12, 4, -8, BULLET_ARMS)
            self.health = 1; self.coin_drop = 0
            self.move_speed = 0; self.chase_speed = 6.0
            self.aggro_range = 800; self.damage = 2
            self.gravity = 0
        elif self.kind == ENEMY_AMP:
            self.add_cube(16, 16, 16, 0, 8, 0, AMP_BODY)
            self.add_cube(4, 4, 2, -5, 12, 9, AMP_SPARK)
            self.add_cube(4, 4, 2, 5, 12, 9, AMP_SPARK)
            for i in range(4):
                a = i * math.pi / 2
                self.add_cube(4, 4, 4, math.cos(a)*14, 8, math.sin(a)*14, AMP_SPARK)
            self.health = 99; self.coin_drop = 0
            self.move_speed = 2.0; self.chase_speed = 0
            self.damage = 1; self.gravity = 0
            self.patrol_radius = 100
        elif self.kind == ENEMY_WHOMP:
            self.add_cube(40, 64, 12, 0, 32, 0, WHOMP_BODY)
            self.add_cube(32, 20, 4, 0, 50, 8, WHOMP_FACE)
            self.add_cube(6, 8, 4, -10, 54, 9, BLACK)
            self.add_cube(6, 8, 4, 10, 54, 9, BLACK)
            self.add_cube(12, 4, 4, 0, 42, 9, BLACK)
            self.add_cube(12, 12, 12, -20, 8, 0, WHOMP_BODY)
            self.add_cube(12, 12, 12, 20, 8, 0, WHOMP_BODY)
            self.health = 1; self.coin_drop = 5
            self.move_speed = 0.6; self.chase_speed = 1.5
            self.aggro_range = 250; self.damage = 3
        elif self.kind == ENEMY_FLYGUY:
            self.add_cube(14, 14, 14, 0, 40, 0, FLYGUY_BODY)
            self.add_cube(16, 4, 16, 0, 50, 0, FLYGUY_MASK)
            self.add_cube(4, 4, 2, -4, 48, 8, BLACK)
            self.add_cube(4, 4, 2, 4, 48, 8, BLACK)
            self.add_cube(6, 12, 2, -8, 48, 0, (200,200,200))
            self.add_cube(6, 12, 2, 8, 48, 0, (200,200,200))
            self.health = 1; self.coin_drop = 2
            self.move_speed = 1.5; self.chase_speed = 0
            self.damage = 1; self.gravity = 0
        elif self.kind == ENEMY_MONTY_MOLE:
            self.add_cube(14, 12, 14, 0, 6, 0, MONTY_BODY)
            self.add_cube(12, 8, 12, 0, 4, 0, MONTY_BELLY)
            self.add_cube(4, 4, 2, -4, 12, 8, BLACK)
            self.add_cube(4, 4, 2, 4, 12, 8, BLACK)
            self.add_cube(4, 4, 4, 0, 10, 8, (40,24,16))
            self.health = 1; self.coin_drop = 1
            self.move_speed = 1.8; self.chase_speed = 3.5
            self.aggro_range = 250; self.damage = 1
        elif self.kind == ENEMY_POKEY:
            for i in range(4):
                self.add_cube(16, 16, 16, 0, 8 + i * 18, 0, POKEY_BODY)
                for dx, dz in [(-8,0),(8,0),(0,-8),(0,8)]:
                    self.add_cube(3, 3, 3, dx, 10 + i * 18, dz, POKEY_SPIKE)
            self.add_cube(18, 18, 18, 0, 80, 0, POKEY_BODY)
            self.add_cube(4, 4, 2, -5, 86, 10, BLACK)
            self.add_cube(4, 4, 2, 5, 86, 10, BLACK)
            self.health = 4; self.coin_drop = 3
            self.move_speed = 0.5; self.chase_speed = 1.0
            self.aggro_range = 200; self.damage = 2
        elif self.kind == ENEMY_SKEETER:
            self.add_cube(18, 10, 18, 0, 10, 0, SKEETER_BODY)
            self.add_cube(14, 6, 14, 0, 6, 0, SKEETER_BODY)
            for dx in [-1, 1]:
                for dz in [-1, 1]:
                    self.add_cube(2, 8, 2, dx * 14, 4, dz * 14, SKEETER_LEGS)
            self.add_cube(4, 4, 2, -4, 14, 10, BLACK)
            self.add_cube(4, 4, 2, 4, 14, 10, BLACK)
            self.health = 1; self.coin_drop = 2
            self.move_speed = 2.0; self.chase_speed = 3.0
            self.damage = 1; self.gravity = 0
        elif self.kind == ENEMY_SNUFIT:
            self.add_cube(14, 14, 14, 0, 30, 0, SNUFIT_BODY)
            self.add_cube(16, 8, 4, 0, 34, 8, SNUFIT_MASK)
            self.add_cube(4, 4, 2, -4, 36, 9, BLACK)
            self.add_cube(4, 4, 2, 4, 36, 9, BLACK)
            self.add_cube(6, 6, 12, 0, 28, 10, DARK_GREY)
            self.health = 1; self.coin_drop = 1
            self.move_speed = 1.0; self.chase_speed = 0
            self.damage = 1; self.gravity = 0
            self.attack_cooldown = 60
        elif self.kind == ENEMY_HEAVE_HO:
            self.add_cube(24, 20, 24, 0, 10, 0, HEAVE_HO_BODY)
            self.add_cube(28, 4, 28, 0, 20, 0, HEAVE_HO_PLATE)
            self.add_cube(6, 6, 2, -6, 16, 13, BLACK)
            self.add_cube(6, 6, 2, 6, 16, 13, BLACK)
            self.add_cube(8, 4, 8, -16, 4, 0, DARK_GREY)
            self.add_cube(8, 4, 8, 16, 4, 0, DARK_GREY)
            self.health = 99; self.coin_drop = 0
            self.move_speed = 1.2; self.chase_speed = 2.5
            self.aggro_range = 200; self.damage = 0  # Launches Mario instead

    def update_ai(self, mario_x, mario_y, mario_z, mario_on_ground):
        """SM64-style AI update."""
        if not self.alive:
            return
        self.anim_timer += 1
        if self.hit_flash > 0:
            self.hit_flash -= 1
        if self.stunned_timer > 0:
            self.stunned_timer -= 1
            return
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

        dx = mario_x - self.x; dz = mario_z - self.z
        dist = math.sqrt(dx * dx + dz * dz)

        # Thwomp special behavior
        if self.kind == ENEMY_THWOMP:
            if self.state == 0:  # Waiting up high
                if dist < self.aggro_range:
                    self.state = 2  # Slam down
                    self.dy_enemy = -12
            elif self.state == 2:  # Slamming
                self.y += self.dy_enemy
                if self.y <= self.home_x:  # home_x stores base Y for thwomps
                    self.y = self.home_x
                    self.state = 3; self.state_timer = 60
            elif self.state == 3:  # Resting
                self.state_timer -= 1
                if self.state_timer <= 0:
                    self.state = 4; self.dy_enemy = 2
            elif self.state == 4:  # Rising
                self.y += self.dy_enemy
                if self.y >= self.home_x + self.bounce_height:
                    self.y = self.home_x + self.bounce_height
                    self.state = 0
            return

        # Piranha Plant special — bob up/down
        if self.kind == ENEMY_PIRANHA:
            bob = math.sin(self.anim_timer * 0.03) * 20
            self.y = self.home_z + bob  # home_z stores base Y
            if dist < self.aggro_range and dist > 60:
                pass  # Stay hidden-ish when Mario too close
            return

        # Boo special — face away when Mario looks at it
        if self.kind == ENEMY_BOO:
            if dist < self.aggro_range:
                face_to_mario = math.atan2(dx, dz)
                self.facing = face_to_mario
                # Move toward Mario when not being looked at
                self.x += math.sin(face_to_mario) * self.chase_speed * 0.3
                self.z += math.cos(face_to_mario) * self.chase_speed * 0.3
                self.y = self.home_z + math.sin(self.anim_timer * 0.04) * 15  # Float
            return

        # Amp — circular orbit
        if self.kind == ENEMY_AMP:
            self.patrol_angle += self.patrol_speed * 2
            self.x = self.home_x + math.cos(self.patrol_angle) * self.patrol_radius
            self.z = self.home_z + math.sin(self.patrol_angle) * self.patrol_radius
            self.y += math.sin(self.anim_timer * 0.05) * 0.3
            return

        # Flyguy — hover and circle
        if self.kind == ENEMY_FLYGUY:
            self.patrol_angle += self.patrol_speed * 1.5
            self.x = self.home_x + math.cos(self.patrol_angle) * self.patrol_radius
            self.z = self.home_z + math.sin(self.patrol_angle) * self.patrol_radius
            self.y = self.home_z + 40 + math.sin(self.anim_timer * 0.04) * 20
            return

        # Skeeter — skate on water surface
        if self.kind == ENEMY_SKEETER:
            self.patrol_angle += self.patrol_speed
            self.x = self.home_x + math.cos(self.patrol_angle) * self.patrol_radius
            self.z = self.home_z + math.sin(self.patrol_angle) * self.patrol_radius
            if dist < self.aggro_range:
                nx = dx / max(dist, 1); nz = dz / max(dist, 1)
                self.x += nx * self.chase_speed
                self.z += nz * self.chase_speed
            return

        # Snufit — float and shoot
        if self.kind == ENEMY_SNUFIT:
            self.y = self.home_z + math.sin(self.anim_timer * 0.03) * 10
            self.patrol_angle += self.patrol_speed
            self.x = self.home_x + math.cos(self.patrol_angle) * self.patrol_radius * 0.5
            self.z = self.home_z + math.sin(self.patrol_angle) * self.patrol_radius * 0.5
            return

        # Gravity for ground enemies
        if self.gravity > 0:
            self.dy_enemy -= self.gravity
            self.y += self.dy_enemy
            if self.y < 0:
                self.y = 0; self.dy_enemy = 0

        # Standard patrol / chase AI
        if self.state == 0:  # Patrol
            self.patrol_angle += self.patrol_speed
            target_x = self.home_x + math.cos(self.patrol_angle) * self.patrol_radius
            target_z = self.home_z + math.sin(self.patrol_angle) * self.patrol_radius
            tdx = target_x - self.x; tdz = target_z - self.z
            td = math.sqrt(tdx * tdx + tdz * tdz)
            if td > 1:
                self.x += (tdx / td) * self.move_speed
                self.z += (tdz / td) * self.move_speed
                self.facing = math.atan2(tdx, tdz)
            if dist < self.aggro_range:
                self.state = 1
        elif self.state == 1:  # Chase
            if dist > self.deaggro_range:
                self.state = 0
            elif dist > 1:
                nx = dx / dist; nz = dz / dist
                self.x += nx * self.chase_speed
                self.z += nz * self.chase_speed
                self.facing = math.atan2(dx, dz)
            # Bob-omb explode when close
            if self.kind == ENEMY_BOBOMB and dist < 50:
                self.state = 2; self.state_timer = 30
        elif self.state == 2:  # Attack / explode
            if self.kind == ENEMY_BOBOMB:
                self.state_timer -= 1
                if self.state_timer <= 0:
                    self.alive = False  # Explode
            else:
                self.state = 0

    def check_stomp(self, mario_x, mario_y, mario_z, mario_dy) -> int:
        """Check if Mario stomps this enemy. Returns: 0=miss, 1=stomp, 2=damage mario"""
        if not self.alive:
            return 0
        dx = mario_x - self.x; dz = mario_z - self.z
        horiz_dist = math.sqrt(dx * dx + dz * dz)

        if horiz_dist < self.STOMP_RANGE:
            # Check if Mario is above and falling
            if mario_y > self.y + 10 and mario_dy < 0:
                # Stomp!
                self.health -= 1
                if self.health <= 0:
                    self.alive = False
                    return 1
                else:
                    self.stunned_timer = 60
                    self.hit_flash = 20
                    return 1
            elif horiz_dist < self.HIT_RANGE:
                # Mario hit by enemy
                return 2
        return 0


# ======================================================================
#  MOVING PLATFORM SYSTEM
# ======================================================================
PLATFORM_SLIDE   = 0
PLATFORM_ROTATE  = 1
PLATFORM_FALL    = 2
PLATFORM_LOOP    = 3
PLATFORM_SEESAW  = 4
PLATFORM_ARROW   = 5
PLATFORM_TILT    = 6
PLATFORM_SCALE   = 7

class MovingPlatform(Mesh):
    """SM64-style moving platforms with multiple behavior modes."""
    def __init__(self, x, y, z, w, h, d, color, mode=PLATFORM_SLIDE,
                 ax=0, ay=0, az=0, speed=1.0, wait=60, extent=200):
        super().__init__(x, y, z)
        self.add_cube(w, h, d, 0, 0, 0, color)
        self.mode = mode
        self.home_x = x; self.home_y = y; self.home_z = z
        self.axis_x = ax; self.axis_y = ay; self.axis_z = az
        self.speed = speed
        self.wait_time = wait
        self.extent = extent
        self.phase = 0
        self.timer = 0
        self.direction = 1
        self.activated = False
        self.fall_triggered = False
        self.fall_timer = 0
        self.player_on = False
        self.half_w = w / 2; self.half_h = h / 2; self.half_d = d / 2
        self.tilt_angle = 0
        self.seesaw_weight = 0
        self.original_y = y

    def is_mario_on(self, mx, my, mz) -> bool:
        """Check if Mario is standing on this platform."""
        if (abs(mx - self.x) < self.half_w + 10 and
            abs(mz - self.z) < self.half_d + 10 and
            abs(my - (self.y + self.half_h)) < 15):
            return True
        return False

    def get_top_y(self) -> float:
        return self.y + self.half_h

    def update(self, mario_x=0, mario_y=0, mario_z=0):
        """Update platform position based on mode."""
        old_x, old_y, old_z = self.x, self.y, self.z
        self.player_on = self.is_mario_on(mario_x, mario_y, mario_z)

        if self.mode == PLATFORM_SLIDE:
            self.phase += self.speed * 0.02 * self.direction
            t = math.sin(self.phase)
            self.x = self.home_x + self.axis_x * t * self.extent
            self.y = self.home_y + self.axis_y * t * self.extent
            self.z = self.home_z + self.axis_z * t * self.extent

        elif self.mode == PLATFORM_ROTATE:
            self.phase += self.speed * 0.01
            self.x = self.home_x + math.cos(self.phase) * self.extent
            self.z = self.home_z + math.sin(self.phase) * self.extent
            self.y = self.home_y + self.axis_y * math.sin(self.phase * 0.5) * self.extent * 0.3

        elif self.mode == PLATFORM_FALL:
            if self.player_on and not self.fall_triggered:
                self.fall_triggered = True
                self.fall_timer = 30  # Shake before falling
            if self.fall_triggered:
                if self.fall_timer > 0:
                    self.fall_timer -= 1
                    self.x = self.home_x + random.uniform(-2, 2)
                    self.z = self.home_z + random.uniform(-2, 2)
                else:
                    self.y -= 4
                    if self.y < self.home_y - 600:
                        # Reset
                        self.x = self.home_x; self.y = self.home_y; self.z = self.home_z
                        self.fall_triggered = False

        elif self.mode == PLATFORM_LOOP:
            self.phase += self.speed * 0.005
            t = self.phase % (math.pi * 2)
            self.x = self.home_x + math.cos(t) * self.extent
            self.y = self.home_y + math.sin(t * 2) * self.extent * 0.5
            self.z = self.home_z + math.sin(t) * self.extent

        elif self.mode == PLATFORM_SEESAW:
            if self.player_on:
                side = 1 if mario_x > self.x else -1
                self.seesaw_weight += side * 0.02
                self.seesaw_weight = max(-0.4, min(0.4, self.seesaw_weight))
            else:
                self.seesaw_weight *= 0.95
            self.tilt_angle = self.seesaw_weight

        elif self.mode == PLATFORM_ARROW:
            if self.player_on:
                self.activated = True
            if self.activated:
                self.x += self.axis_x * self.speed
                self.y += self.axis_y * self.speed
                self.z += self.axis_z * self.speed
                dist = math.sqrt((self.x - self.home_x)**2 + (self.y - self.home_y)**2 +
                                (self.z - self.home_z)**2)
                if dist > self.extent:
                    self.activated = False
                    self.x = self.home_x; self.y = self.home_y; self.z = self.home_z

        elif self.mode == PLATFORM_TILT:
            if self.player_on:
                dx = mario_x - self.x; dz = mario_z - self.z
                self.tilt_angle = math.atan2(dz, dx) * 0.1
            else:
                self.tilt_angle *= 0.9

        elif self.mode == PLATFORM_SCALE:
            if self.player_on:
                self.y -= self.speed
                if self.y < self.home_y - self.extent:
                    self.y = self.home_y - self.extent
            else:
                if self.y < self.home_y:
                    self.y += self.speed * 0.5

        dx_plat = self.x - old_x
        dy_plat = self.y - old_y
        dz_plat = self.z - old_z
        return dx_plat, dy_plat, dz_plat


# ======================================================================
#  CANNON SYSTEM — SM64 cannon launching
# ======================================================================
class Cannon(Mesh):
    """SM64-style cannon for launching Mario."""
    def __init__(self, x, y, z, default_yaw=0, default_pitch=0.5):
        super().__init__(x, y, z)
        self.add_cube(20, 12, 20, 0, 6, 0, DARK_GREY)
        self.add_cube(12, 24, 12, 0, 18, 0, METAL_GREY)
        self.add_cube(8, 8, 16, 0, 28, 8, DARK_GREY)
        self.launch_yaw = default_yaw
        self.launch_pitch = default_pitch
        self.launch_power = 40
        self.active = False
        self.opened = False
        self.interact_range = 60

    def can_enter(self, mx, my, mz) -> bool:
        dx = mx - self.x; dz = mz - self.z
        return math.sqrt(dx * dx + dz * dz) < self.interact_range and abs(my - self.y) < 30

    def launch(self):
        """Calculate launch velocity."""
        vx = -math.sin(self.launch_yaw) * math.cos(self.launch_pitch) * self.launch_power
        vy = math.sin(self.launch_pitch) * self.launch_power
        vz = -math.cos(self.launch_yaw) * math.cos(self.launch_pitch) * self.launch_power
        return vx, vy, vz


# ======================================================================
#  NPC SYSTEM — Toads, Bob-omb Buddies, Penguins
# ======================================================================
NPC_TOAD         = 0
NPC_BOBOMB_BUDDY = 1
NPC_PENGUIN      = 2
NPC_KOOPA_NPC    = 3
NPC_LAKITU_NPC   = 4
NPC_MIPS         = 5
NPC_YOSHI        = 6

# NPC colors
TOAD_CAP   = (200, 32, 32)
TOAD_SPOTS = (255, 255, 255)
TOAD_FACE  = (252, 200, 140)
TOAD_VEST  = (72, 72, 200)
BUDDY_BODY = (200, 100, 120)
BUDDY_FEET = (200, 180, 60)
PENGUIN_BODY = (24, 24, 40)
PENGUIN_BELLY = (255, 255, 255)
PENGUIN_BEAK  = (255, 180, 40)
MIPS_BODY     = (255, 230, 100)
MIPS_BELLY    = (255, 255, 200)
YOSHI_BODY    = (0, 180, 0)
YOSHI_BELLY   = (255, 255, 220)
YOSHI_SHELL   = (200, 40, 40)
YOSHI_BOOTS   = (200, 100, 40)

class NPC(Mesh):
    """Interactive NPCs with dialog."""
    def __init__(self, x, y, z, kind=NPC_TOAD, dialog="", name=""):
        super().__init__(x, y, z)
        self.kind = kind
        self.dialog = dialog
        self.name = name
        self.interact_range = 80
        self.facing = 0
        self.anim_timer = 0
        self.talking = False
        self.talk_timer = 0
        self._build_model()

    def _build_model(self):
        if self.kind == NPC_TOAD:
            self.add_cube(12, 16, 12, 0, 8, 0, TOAD_VEST)
            self.add_cube(14, 14, 14, 0, 22, 0, TOAD_FACE)
            self.add_cube(18, 12, 18, 0, 32, 0, TOAD_CAP)
            for a in [0, math.pi/2, math.pi, math.pi*1.5]:
                self.add_cube(6, 6, 6, math.cos(a)*10, 36, math.sin(a)*10, TOAD_SPOTS)
            self.add_cube(4, 4, 2, -4, 24, 8, BLACK)
            self.add_cube(4, 4, 2, 4, 24, 8, BLACK)
            self.add_cube(6, 4, 6, -6, 2, 0, TOAD_FACE)
            self.add_cube(6, 4, 6, 6, 2, 0, TOAD_FACE)
        elif self.kind == NPC_BOBOMB_BUDDY:
            self.add_cube(14, 14, 14, 0, 7, 0, BUDDY_BODY)
            self.add_cube(4, 4, 2, -5, 14, 8, WHITE)
            self.add_cube(4, 4, 2, 5, 14, 8, WHITE)
            self.add_cube(2, 2, 2, -5, 14, 9, BLACK)
            self.add_cube(2, 2, 2, 5, 14, 9, BLACK)
            self.add_cube(6, 4, 6, -6, 2, 0, BUDDY_FEET)
            self.add_cube(6, 4, 6, 6, 2, 0, BUDDY_FEET)
        elif self.kind == NPC_PENGUIN:
            self.add_cube(16, 24, 14, 0, 12, 0, PENGUIN_BODY)
            self.add_cube(12, 20, 10, 0, 10, 2, PENGUIN_BELLY)
            self.add_cube(12, 12, 12, 0, 28, 0, PENGUIN_BODY)
            self.add_cube(8, 4, 6, 0, 28, 8, PENGUIN_BEAK)
            self.add_cube(4, 4, 2, -4, 32, 6, BLACK)
            self.add_cube(4, 4, 2, 4, 32, 6, BLACK)
            self.add_cube(10, 4, 8, -14, 14, 0, PENGUIN_BODY)
            self.add_cube(10, 4, 8, 14, 14, 0, PENGUIN_BODY)
            self.add_cube(6, 4, 8, -4, 2, 0, PENGUIN_BEAK)
            self.add_cube(6, 4, 8, 4, 2, 0, PENGUIN_BEAK)
        elif self.kind == NPC_MIPS:
            self.add_cube(10, 8, 16, 0, 4, 0, MIPS_BODY)
            self.add_cube(8, 6, 12, 0, 2, 0, MIPS_BELLY)
            self.add_cube(8, 8, 8, 0, 10, 6, MIPS_BODY)
            self.add_cube(10, 4, 4, 0, 14, 6, MIPS_BODY)
            self.add_cube(4, 4, 2, -3, 12, 10, BLACK)
            self.add_cube(4, 4, 2, 3, 12, 10, BLACK)
        elif self.kind == NPC_YOSHI:
            self.add_cube(16, 20, 24, 0, 10, 0, YOSHI_BODY)
            self.add_cube(12, 16, 20, 0, 8, 0, YOSHI_BELLY)
            self.add_cube(12, 14, 16, 0, 26, 10, YOSHI_BODY)
            self.add_cube(10, 8, 8, 0, 30, 18, YOSHI_BODY)
            self.add_cube(4, 4, 2, -3, 30, 22, BLACK)
            self.add_cube(4, 4, 2, 3, 30, 22, BLACK)
            self.add_cube(18, 6, 12, 0, 16, -6, YOSHI_SHELL)
            self.add_cube(6, 6, 6, -8, 2, -4, YOSHI_BOOTS)
            self.add_cube(6, 6, 6, 8, 2, -4, YOSHI_BOOTS)

    def can_talk(self, mx, my, mz) -> bool:
        dx = mx - self.x; dz = mz - self.z
        return math.sqrt(dx * dx + dz * dz) < self.interact_range

    def start_talk(self):
        self.talking = True
        self.talk_timer = 180

    def update(self):
        self.anim_timer += 1
        if self.talking:
            self.talk_timer -= 1
            if self.talk_timer <= 0:
                self.talking = False


# ======================================================================
#  CAP SWITCH SYSTEM — Metal, Vanish, Wing caps
# ======================================================================
CAP_NONE   = 0
CAP_WING   = 1
CAP_METAL  = 2
CAP_VANISH = 3

CAP_COLORS = {
    CAP_WING:   MARIO_RED,
    CAP_METAL:  METAL_GREY,
    CAP_VANISH: (80, 120, 200),
}

class CapSwitch(Mesh):
    """SM64 cap switch — press to activate cap blocks globally."""
    def __init__(self, x, y, z, cap_type=CAP_WING):
        super().__init__(x, y, z)
        self.cap_type = cap_type
        self.pressed = False
        self.press_range = 40
        color = CAP_COLORS.get(cap_type, MARIO_RED)
        self.add_cube(48, 20, 48, 0, 10, 0, color)
        self.add_cube(36, 8, 36, 0, 24, 0, color)
        self.add_cube(12, 12, 4, 0, 28, 20, WHITE)

    def check_press(self, mx, my, mz) -> bool:
        if self.pressed:
            return False
        dx = mx - self.x; dz = mz - self.z
        if math.sqrt(dx * dx + dz * dz) < self.press_range and abs(my - self.y) < 30:
            self.pressed = True
            return True
        return False


class CapBlock(Mesh):
    """Breakable cap block that gives a cap powerup."""
    def __init__(self, x, y, z, cap_type=CAP_WING):
        super().__init__(x, y, z)
        self.cap_type = cap_type
        self.broken = False
        self.hit_range = 30
        color = CAP_COLORS.get(cap_type, MARIO_RED)
        transparent = tuple(min(255, c + 80) for c in color)
        self.add_cube(24, 24, 24, 0, 12, 0, transparent)
        self.add_cube(8, 4, 8, 0, 26, 0, YELLOW)


# ======================================================================
#  DAMAGE ZONE SYSTEM — Lava, quicksand, toxic, spikes
# ======================================================================
ZONE_LAVA      = 0
ZONE_QUICKSAND = 1
ZONE_TOXIC     = 2
ZONE_SPIKES    = 3
ZONE_COLD      = 4
ZONE_WIND      = 5

class DamageZone:
    """Invisible damage zone that hurts Mario on contact."""
    __slots__ = ['x','z','hw','hd','y_min','y_max','kind','damage','knockback',
                 'slow_factor','push_dx','push_dz']
    def __init__(self, x, z, hw, hd, y_min=-100, y_max=100, kind=ZONE_LAVA,
                 damage=1, knockback=15, slow_factor=1.0, push_dx=0, push_dz=0):
        self.x = x; self.z = z; self.hw = hw; self.hd = hd
        self.y_min = y_min; self.y_max = y_max
        self.kind = kind; self.damage = damage; self.knockback = knockback
        self.slow_factor = slow_factor
        self.push_dx = push_dx; self.push_dz = push_dz

    def check(self, mx, my, mz) -> bool:
        return (abs(mx - self.x) < self.hw and abs(mz - self.z) < self.hd and
                self.y_min <= my <= self.y_max)


# ======================================================================
#  POLE CLIMBING SYSTEM
# ======================================================================
class ClimbPole(Mesh):
    """Climbable pole / flagpole / tree."""
    def __init__(self, x, y, z, height=80, radius=12, color=DARK_GREY):
        super().__init__(x, y, z)
        self.height = height
        self.radius = radius
        self.grab_range = radius + 15
        self.add_cube(radius, height, radius, 0, height / 2, 0, color)

    def can_grab(self, mx, my, mz) -> bool:
        dx = mx - self.x; dz = mz - self.z
        horiz = math.sqrt(dx * dx + dz * dz)
        return horiz < self.grab_range and self.y <= my <= self.y + self.height


# ======================================================================
#  SIGN SYSTEM — Readable signs
# ======================================================================
class Sign(Mesh):
    """Readable signpost."""
    def __init__(self, x, y, z, text="", facing=0):
        super().__init__(x, y, z)
        self.text = text
        self.read_range = 60
        self.showing = False
        self.show_timer = 0
        self.add_cube(6, 28, 6, 0, 14, 0, DARK_BROWN)
        self.add_cube(24, 16, 4, 0, 32, 4, (180, 150, 100))
        self.yaw = facing

    def can_read(self, mx, my, mz) -> bool:
        dx = mx - self.x; dz = mz - self.z
        return math.sqrt(dx * dx + dz * dz) < self.read_range

    def start_read(self):
        self.showing = True
        self.show_timer = 240

    def update(self):
        if self.showing:
            self.show_timer -= 1
            if self.show_timer <= 0:
                self.showing = False


# ======================================================================
#  BOWSER BOSS FIGHT SYSTEM
# ======================================================================
class BowserBoss(Mesh):
    """SM64-style Bowser boss with basic fight mechanics."""
    PHASE_IDLE    = 0
    PHASE_WALK    = 1
    PHASE_CHARGE  = 2
    PHASE_FIRE    = 3
    PHASE_STUNNED = 4
    PHASE_THROWN  = 5
    PHASE_DEAD    = 6

    def __init__(self, x, y, z, arena_radius=240, hits_needed=1):
        super().__init__(x, y, z)
        self.home_x = x; self.home_y = y; self.home_z = z
        self.arena_radius = arena_radius
        self.hits_needed = hits_needed
        self.hits_taken = 0
        self.phase = self.PHASE_IDLE
        self.phase_timer = 120
        self.facing = 0
        self.speed = 2.0
        self.charge_speed = 6.0
        self.health = hits_needed
        self.stunned_timer = 0
        self.fire_timer = 0
        self.fire_balls: list[dict] = []
        self.thrown = False
        self.thrown_dy = 0
        self.anim_timer = 0
        self.defeated = False
        self.defeat_timer = 0
        self._build_model()

    def _build_model(self):
        # Body
        self.add_cube(48, 56, 40, 0, 28, 0, DARK_GREEN)
        # Shell
        self.add_cube(52, 24, 36, 0, 44, -8, (0, 100, 0))
        for sx, sz in [(-16,-16),(16,-16),(0,-24),(-8,-8),(8,-8)]:
            self.add_cube(8, 12, 8, sx, 56, sz, YELLOW)
        # Head
        self.add_cube(32, 28, 28, 0, 60, 18, (0, 140, 0))
        self.add_cube(24, 12, 8, 0, 56, 30, (220, 200, 160))
        # Eyes
        self.add_cube(8, 10, 4, -8, 68, 30, WHITE)
        self.add_cube(8, 10, 4, 8, 68, 30, WHITE)
        self.add_cube(4, 6, 5, -8, 68, 32, RED)
        self.add_cube(4, 6, 5, 8, 68, 32, RED)
        # Horns
        self.add_cube(6, 16, 6, -14, 74, 22, (200, 180, 120))
        self.add_cube(6, 16, 6, 14, 74, 22, (200, 180, 120))
        # Mouth
        self.add_cube(16, 6, 6, 0, 56, 32, BLACK)
        # Arms
        self.add_cube(12, 20, 12, -28, 32, 8, (0, 120, 0))
        self.add_cube(12, 20, 12, 28, 32, 8, (0, 120, 0))
        # Legs
        self.add_cube(14, 16, 14, -16, 8, 4, (0, 120, 0))
        self.add_cube(14, 16, 14, 16, 8, 4, (0, 120, 0))
        # Tail
        self.add_cube(8, 8, 24, 0, 16, -28, (0, 140, 0))
        self.add_cube(6, 6, 12, 0, 14, -44, (0, 120, 0))
        # Belly
        self.add_cube(36, 28, 8, 0, 24, 22, (220, 200, 120))

    def update(self, mario_x, mario_y, mario_z):
        """Update Bowser AI."""
        if self.defeated:
            self.defeat_timer -= 1
            return

        self.anim_timer += 1
        dx = mario_x - self.x; dz = mario_z - self.z
        dist = math.sqrt(dx * dx + dz * dz)
        angle_to_mario = math.atan2(dx, dz)

        # Update fireballs
        new_fires = []
        for fb in self.fire_balls:
            fb['x'] += fb['dx']; fb['z'] += fb['dz']
            fb['life'] -= 1
            if fb['life'] > 0:
                new_fires.append(fb)
        self.fire_balls = new_fires

        if self.phase == self.PHASE_STUNNED:
            self.stunned_timer -= 1
            if self.stunned_timer <= 0:
                self.phase = self.PHASE_IDLE
                self.phase_timer = 60
            return

        if self.phase == self.PHASE_THROWN:
            self.thrown_dy -= GRAVITY
            self.y += self.thrown_dy
            if self.y < self.home_y:
                self.y = self.home_y
                self.hits_taken += 1
                if self.hits_taken >= self.hits_needed:
                    self.defeated = True
                    self.defeat_timer = 180
                else:
                    self.phase = self.PHASE_IDLE
                    self.phase_timer = 120
            return

        self.phase_timer -= 1

        if self.phase == self.PHASE_IDLE:
            self.facing += (angle_to_mario - self.facing) * 0.05
            if self.phase_timer <= 0:
                choices = [self.PHASE_WALK, self.PHASE_CHARGE, self.PHASE_FIRE]
                weights = [0.4, 0.3, 0.3]
                r = random.random()
                if r < weights[0]:
                    self.phase = self.PHASE_WALK; self.phase_timer = 120
                elif r < weights[0] + weights[1]:
                    self.phase = self.PHASE_CHARGE; self.phase_timer = 60
                else:
                    self.phase = self.PHASE_FIRE; self.phase_timer = 40; self.fire_timer = 0

        elif self.phase == self.PHASE_WALK:
            self.facing += (angle_to_mario - self.facing) * 0.03
            self.x += math.sin(self.facing) * self.speed
            self.z += math.cos(self.facing) * self.speed
            if self.phase_timer <= 0:
                self.phase = self.PHASE_IDLE; self.phase_timer = 60

        elif self.phase == self.PHASE_CHARGE:
            self.x += math.sin(self.facing) * self.charge_speed
            self.z += math.cos(self.facing) * self.charge_speed
            if self.phase_timer <= 0 or dist < 40:
                self.phase = self.PHASE_IDLE; self.phase_timer = 90

        elif self.phase == self.PHASE_FIRE:
            self.facing += (angle_to_mario - self.facing) * 0.08
            self.fire_timer += 1
            if self.fire_timer % 15 == 0 and len(self.fire_balls) < 8:
                fb = {
                    'x': self.x + math.sin(self.facing) * 30,
                    'z': self.z + math.cos(self.facing) * 30,
                    'y': self.y + 40,
                    'dx': math.sin(self.facing) * 5 + random.uniform(-1, 1),
                    'dz': math.cos(self.facing) * 5 + random.uniform(-1, 1),
                    'life': 80
                }
                self.fire_balls.append(fb)
            if self.phase_timer <= 0:
                self.phase = self.PHASE_IDLE; self.phase_timer = 100

        # Keep in arena
        adx = self.x - self.home_x; adz = self.z - self.home_z
        arena_dist = math.sqrt(adx * adx + adz * adz)
        if arena_dist > self.arena_radius:
            self.x = self.home_x + (adx / arena_dist) * self.arena_radius
            self.z = self.home_z + (adz / arena_dist) * self.arena_radius

    def check_tail_grab(self, mx, my, mz) -> bool:
        """Check if Mario can grab Bowser's tail."""
        tail_x = self.x - math.sin(self.facing) * 40
        tail_z = self.z - math.cos(self.facing) * 40
        dx = mx - tail_x; dz = mz - tail_z
        return math.sqrt(dx * dx + dz * dz) < 35 and abs(my - self.y) < 30

    def throw(self, direction):
        """Bowser gets thrown."""
        self.phase = self.PHASE_THROWN
        self.thrown_dy = 15
        dx = math.sin(direction) * 20
        dz = math.cos(direction) * 20
        self.x += dx; self.z += dz

    def stun(self):
        self.phase = self.PHASE_STUNNED
        self.stunned_timer = 120

    def check_hit_mario(self, mx, my, mz) -> bool:
        """Check if Bowser or fireballs hit Mario."""
        dx = mx - self.x; dz = mz - self.z
        if math.sqrt(dx * dx + dz * dz) < 50 and abs(my - self.y) < 40:
            return True
        for fb in self.fire_balls:
            fdx = mx - fb['x']; fdz = mz - fb['z']
            if math.sqrt(fdx * fdx + fdz * fdz) < 30:
                return True
        return False


# ======================================================================
#  MINIMAP / RADAR SYSTEM
# ======================================================================
class Minimap:
    """SM64-style radar minimap in corner of screen."""
    SIZE = 96
    PADDING = 8
    SCALE = 0.04  # World-to-minimap scale

    def __init__(self):
        self.surface = pygame.Surface((self.SIZE, self.SIZE), pygame.SRCALPHA)
        self.enabled = True

    def draw(self, screen, mario_x, mario_z, cam_yaw,
             stars=None, enemies=None, coins=None, npcs=None):
        if not self.enabled:
            return
        self.surface.fill((0, 0, 0, 140))
        cx = self.SIZE // 2; cy = self.SIZE // 2
        cos_y = math.cos(-cam_yaw); sin_y = math.sin(-cam_yaw)

        # Draw coins as yellow dots
        if coins:
            for coin in coins:
                if not coin.collected:
                    dx = (coin.x - mario_x) * self.SCALE
                    dz = (coin.z - mario_z) * self.SCALE
                    rx = dx * cos_y - dz * sin_y; rz = dx * sin_y + dz * cos_y
                    px = int(cx + rx); py = int(cy - rz)
                    if 2 <= px < self.SIZE - 2 and 2 <= py < self.SIZE - 2:
                        self.surface.set_at((px, py), COIN_YELLOW)

        # Draw stars as gold triangles
        if stars:
            for star in stars:
                if not star.collected:
                    dx = (star.x - mario_x) * self.SCALE
                    dz = (star.z - mario_z) * self.SCALE
                    rx = dx * cos_y - dz * sin_y; rz = dx * sin_y + dz * cos_y
                    px = int(cx + rx); py = int(cy - rz)
                    if 4 <= px < self.SIZE - 4 and 4 <= py < self.SIZE - 4:
                        pygame.draw.polygon(self.surface, STAR_GOLD,
                            [(px, py - 3), (px - 3, py + 2), (px + 3, py + 2)])

        # Draw enemies as red dots
        if enemies:
            for e in enemies:
                if e.alive:
                    dx = (e.x - mario_x) * self.SCALE
                    dz = (e.z - mario_z) * self.SCALE
                    rx = dx * cos_y - dz * sin_y; rz = dx * sin_y + dz * cos_y
                    px = int(cx + rx); py = int(cy - rz)
                    if 2 <= px < self.SIZE - 2 and 2 <= py < self.SIZE - 2:
                        pygame.draw.circle(self.surface, RED, (px, py), 2)

        # Draw NPCs as blue dots
        if npcs:
            for npc in npcs:
                dx = (npc.x - mario_x) * self.SCALE
                dz = (npc.z - mario_z) * self.SCALE
                rx = dx * cos_y - dz * sin_y; rz = dx * sin_y + dz * cos_y
                px = int(cx + rx); py = int(cy - rz)
                if 2 <= px < self.SIZE - 2 and 2 <= py < self.SIZE - 2:
                    pygame.draw.circle(self.surface, BLUE, (px, py), 2)

        # Mario (center, pointing up = forward)
        pygame.draw.polygon(self.surface, MARIO_RED,
            [(cx, cy - 4), (cx - 3, cy + 3), (cx + 3, cy + 3)])

        # Border
        pygame.draw.rect(self.surface, WHITE, (0, 0, self.SIZE, self.SIZE), 1)

        # Blit to screen
        screen.blit(self.surface, (WIDTH - self.SIZE - self.PADDING, self.PADDING))



# ======================================================================
#  LEVEL BUILDERS — SM64 PC PORT AUTHENTIC GEOMETRY
#  FIX #2: Lethal Lava Land platform tuples fixed
#  FIX #16: spawn points added per level
#  FIX #41: water planes registered
# ======================================================================

def build_castle_grounds():
    m = Mesh()
    tile = 240
    for x in range(-8, 8):
        for z in range(-8, 8):
            c = CG_GRASS_1 if (x + z) % 2 == 0 else CG_GRASS_2
            h = math.sin(x * 0.5) * 4 + math.cos(z * 0.7) * 3
            m.add_cube(tile, 12, tile, x * tile, -6 + h, z * tile, c)
    for z in range(-6, 0):
        m.add_cube(160, 4, tile, 0, 0, z * tile, CG_PATH)
    for i in range(-4, 5):
        for side in [-1, 1]:
            m.add_cube(tile, 8, tile, i * tile, -4, side * 900, CG_MOAT)
            m.add_cube(tile, 8, tile, side * 900, -4, i * tile, CG_MOAT)
    m.add_water_plane(0, 900, 1200, 300, 0)
    m.add_water_plane(0, -900, 1200, 300, 0)
    m.add_water_plane(900, 0, 300, 1200, 0)
    m.add_water_plane(-900, 0, 300, 1200, 0)
    m.add_cube(400, 4, 400, 0, -8, -900, CG_MOAT_DEEP)
    m.add_cube(180, 16, 480, 0, 4, -640, CG_BRIDGE)
    for side in [-80, 80]:
        for z in range(-3, 3):
            m.add_cube(12, 40, 12, side, 24, -640 + z * 80, CG_BRIDGE)
        m.add_cube(12, 8, 480, side, 44, -640, CG_BRIDGE)
    # Castle
    m.add_cube(640, 360, 80, 0, 180, -1050, CG_CASTLE_WALL)
    for tx in [-380, 380]:
        m.add_cube(120, 480, 120, tx, 240, -1050, CG_TOWER)
        m.add_pyramid(140, 100, tx, 480, -1050, CG_CASTLE_ROOF)
        m.add_cube(30, 40, 5, tx, 360, -988, (80, 64, 100))
        m.add_cube(30, 40, 5, tx, 280, -988, (80, 64, 100))
    m.add_cube(160, 520, 120, 0, 260, -1100, CG_CASTLE_WALL)
    m.add_pyramid(180, 120, 0, 520, -1100, CG_CASTLE_ROOF)
    m.add_cube(100, 160, 8, 0, 80, -1008, (120, 72, 32))
    m.add_cube(120, 20, 12, 0, 160, -1008, CG_CASTLE_TRIM)
    m.add_cube(80, 96, 5, 0, 320, -1008, (240, 160, 200))
    for wx in [-160, 160]:
        m.add_cube(48, 56, 5, wx, 280, -1008, (120, 148, 200))
    m.add_cube(640, 20, 200, 0, 360, -1090, CG_CASTLE_ROOF)
    m.add_cube(680, 20, 100, 0, 10, -1050, CG_STONE)
    # Hills
    m.add_hill(400, 180, -1200, 0, 200, CG_GRASS_1, CG_GRASS_2)
    m.add_hill(500, 220, 1200, 0, 200, CG_GRASS_2, CG_GRASS_1)
    m.add_hill(600, 160, 0, 0, 1400, CG_GRASS_1, CG_GRASS_2)
    m.add_hill(350, 140, -800, 0, -400, CG_GRASS_2, CG_GRASS_1)
    m.add_hill(300, 120, 900, 0, -300, CG_GRASS_1, CG_GRASS_2)
    # Trees
    for tx, tz in [(-500,200),(500,200),(-500,-200),(500,-200),
                   (-700,600),(700,600),(-300,800),(300,800),
                   (-900,100),(900,100),(-600,-500),(600,-500)]:
        m.add_cube(24, 80, 24, tx, 40, tz, CG_TREE_TRUNK)
        m.add_hill(56, 40, tx, 80, tz, CG_TREE_TOP, CG_TREE_TOP2, 6)
    m.add_cube(32, 8, 32, -600, 4, 700, DARK_GREY)
    m.add_cube(24, 24, 24, -600, 16, 700, METAL_GREY)
    m.add_cube(80, 200, 16, 420, 100, -1060, (120, 148, 200))
    m.add_cube(100, 8, 60, 420, 0, -1060, CG_MOAT)
    m.add_cube(8, 36, 8, -800, 18, -600, DARK_GREY)
    m.add_cube(28, 28, 28, -800, 48, -600, (100, 72, 40))
    stars = [Star(0, 540, -1100, 0)]
    coins = [Coin(x * 120, 10, z * 120) for x, z in [(-1,1),(1,1),(0,2),(-2,0),(2,0)]]
    red_coins = [RedCoin(tx, 60, tz) for tx, tz in [(-500,200),(500,-200)]]
    oneups = [OneUp(-600, 28, 700)]
    # Enemies
    enemies = [
        Enemy(-300, 0, 200, ENEMY_GOOMBA, 120),
        Enemy(300, 0, 200, ENEMY_GOOMBA, 120),
        Enemy(-400, 0, -200, ENEMY_GOOMBA, 160),
        Enemy(400, 0, -200, ENEMY_GOOMBA, 100),
        Enemy(600, 0, 400, ENEMY_KOOPA, 180),
        Enemy(-700, 0, -300, ENEMY_GOOMBA, 140),
    ]
    # NPCs
    npcs = [
        NPC(-200, 0, 300, NPC_TOAD, "Welcome to the castle! Collect stars to unlock doors.", "Toad"),
        NPC(200, 0, 600, NPC_BOBOMB_BUDDY, "The cannon is ready! Press E near it to use.", "Bob-omb Buddy"),
        NPC(0, 0, 1200, NPC_TOAD, "The princess is waiting inside the castle!", "Toad"),
    ]
    # Moving platforms
    platforms = [
        MovingPlatform(-400, 20, -800, 80, 8, 80, CG_STONE, PLATFORM_SLIDE, 0, 1, 0, 0.5, 60, 60),
        MovingPlatform(400, 40, -600, 60, 8, 60, CG_BRIDGE, PLATFORM_SLIDE, 1, 0, 0, 0.8, 60, 120),
    ]
    # Damage zones
    damage_zones = [
        DamageZone(0, -900, 1200, 300, -20, 5, ZONE_LAVA, 1, 18),  # Moat water damage
    ]
    # Signs
    signs = [
        Sign(100, 0, 200, "Welcome to Peach's Castle!\nCollect Power Stars!", 0),
        Sign(-100, 0, -400, "Cross the bridge to\nenter the castle.", math.pi),
        Sign(600, 0, -400, "The moat surrounds\nthe castle. Be careful!", 0),
    ]
    # Cannons
    cannons = [
        Cannon(500, 0, 600, math.pi * 0.75, 0.6),
    ]
    return m, stars, coins, red_coins, oneups, (0, 20, 400), enemies, npcs, platforms, damage_zones, signs, cannons

def build_castle_interior_f1():
    m = Mesh(); tile = 200
    for x in range(-5, 5):
        for z in range(-5, 5):
            c = (240,216,184) if (x+z) % 2 == 0 else (220,192,160)
            m.add_cube(tile, 10, tile, x * tile, -5, z * tile, c)
    for z in range(-4, 4):
        m.add_cube(120, 2, tile, 0, 1, z * tile, CARPET_RED)
    for w_z in [-1000, 1000]:
        m.add_cube(2000, 400, 40, 0, 200, w_z, CG_CASTLE_WALL)
    for w_x in [-1000, 1000]:
        m.add_cube(40, 400, 2000, w_x, 200, 0, CG_CASTLE_WALL)
    m.add_cube(2000, 20, 2000, 0, 400, 0, CG_CASTLE_WALL)
    for px, pz in [(-400,-400),(400,-400),(-400,400),(400,400)]:
        m.add_cube(56, 400, 56, px, 200, pz, WHITE)
        m.add_cube(72, 24, 72, px, 400, pz, CG_CASTLE_TRIM)
    for i in range(8):
        m.add_cube(300, 20, 60, 0, i * 25, -600 - i * 60, CG_STONE)
    m.add_cube(100, 200, 20, -800, 100, 0, BUTTON_GOLD)
    m.add_cube(100, 200, 20, 800, 100, 0, BUTTON_GOLD)
    m.add_cube(200, 200, 20, 0, 100, -980, BUTTON_GOLD)
    for px, py, pz, c in [(-978,140,-300,BOB_GRASS_1),(-978,140,-500,WF_STONE_1),
                           (-978,140,-700,JRB_WATER),(978,140,-300,CCM_SNOW_1),(978,140,-500,BBH_WALL)]:
        m.add_cube(80, 80, 8, px, py, pz, (160,112,40))
        m.add_cube(70, 70, 4, px, py, pz - 3 if px < 0 else pz + 3, c)
    m.add_cube(150, 5, 150, 600, -2, 600, DARK_GREY)
    m.add_cube(100, 100, 5, 0, 320, -998, (240,160,200))
    for tx, tz in [(-200,200),(200,-300),(-400,0)]:
        m.add_cube(20, 30, 20, tx, 15, tz, WHITE)
        m.add_cube(24, 12, 24, tx, 38, tz, RED)
    enemies = []
    npcs = [
        NPC(-400, 0, 0, NPC_TOAD, "The paintings on the walls\nlead to different worlds!", "Toad"),
        NPC(400, 0, 0, NPC_TOAD, "You need more stars to\nopen the basement door.", "Toad"),
        NPC(0, 0, -400, NPC_TOAD, "Upstairs requires 30 stars.\nKeep collecting!", "Toad"),
    ]
    platforms = []
    damage_zones = []
    signs = [
        Sign(-600, 0, 0, "Bob-omb Battlefield\nthrough the left wall.", 0),
        Sign(600, 0, 0, "Cool, Cool Mountain\nthrough the right wall.", 0),
    ]
    cannons = []
    return m, [], [], [], [], (0, 20, 800), enemies, npcs, platforms, damage_zones, signs, cannons

def build_castle_basement():
    m = Mesh()
    for x in range(-6, 6):
        for z in range(-6, 6):
            c = (96,72,56) if (x+z) % 2 == 0 else (80,60,44)
            m.add_cube(200, 10, 200, x * 200, -5, z * 200, c)
    m.add_cube(2400, 300, 40, 0, 150, -1200, HMC_ROCK_2)
    m.add_cube(2400, 300, 40, 0, 150, 1200, HMC_ROCK_2)
    m.add_cube(40, 300, 2400, -1200, 150, 0, HMC_ROCK_2)
    m.add_cube(40, 300, 2400, 1200, 150, 0, HMC_ROCK_2)
    m.add_cube(2400, 20, 2400, 0, 300, 0, HMC_ROCK_2)
    m.add_cube(40, 200, 600, -400, 100, -300, HMC_ROCK_1)
    m.add_cube(40, 200, 600, 400, 100, 300, HMC_ROCK_1)
    m.add_cube(600, 200, 40, 0, 100, -400, HMC_ROCK_1)
    m.add_cube(400, 4, 400, -600, -3, -600, LLL_LAVA_1)
    m.add_cube(400, 2, 400, -600, -1, -600, LLL_LAVA_2)
    for px, py, pz, c in [(-1178,100,-400,HMC_ROCK_1),(-1178,100,-600,LLL_LAVA_1),
                           (-1178,100,-800,SSL_SAND_1),(1178,100,-400,DDD_WATER)]:
        m.add_cube(80, 80, 8, px, py, pz, (160,112,40))
        m.add_cube(70, 70, 4, px, py, pz, c)
    m.add_cube(50, 30, 50, 800, 15, 800, PIPE_GREEN)  # FIX #44: pipe connection
    enemies = [
        Enemy(-600, 0, -600, ENEMY_GOOMBA, 100),
    ]
    npcs = [
        NPC(200, 0, 200, NPC_TOAD, "The basement is dark...\nbe careful of the lava!", "Toad"),
        NPC(800, 0, 800, NPC_MIPS, "Catch me if you can!\nI'm MIPS the rabbit!", "MIPS"),
    ]
    platforms = []
    damage_zones = [
        DamageZone(-600, -600, 200, 200, -10, 5, ZONE_LAVA, 2, 20),
    ]
    signs = []
    cannons = []
    return m, [], [], [], [], (0, 20, 1000), enemies, npcs, platforms, damage_zones, signs, cannons

def build_castle_upper():
    m = Mesh()
    for x in range(-4, 4):
        for z in range(-4, 4):
            c = (240,216,184) if (x+z) % 2 == 0 else (220,192,160)
            m.add_cube(200, 10, 200, x * 200, -5, z * 200, c)
    m.add_cube(1600, 350, 40, 0, 175, -800, CG_CASTLE_WALL)
    m.add_cube(1600, 350, 40, 0, 175, 800, CG_CASTLE_WALL)
    m.add_cube(40, 350, 1600, -800, 175, 0, CG_CASTLE_WALL)
    m.add_cube(40, 350, 1600, 800, 175, 0, CG_CASTLE_WALL)
    m.add_cube(1600, 20, 1600, 0, 350, 0, CG_CASTLE_WALL)
    for px, py, pz, c in [(-778,100,-300,SL_ICE),(-778,100,-500,WDW_WATER),
                           (778,100,-300,TTM_GRASS),(778,100,-500,THI_GRASS_1),
                           (0,60,-778,TTC_GEAR),(0,75,-790,MARIO_RED)]:
        m.add_cube(80, 80, 8, px, py, pz, (160,112,40))
        m.add_cube(70, 70, 4, px, py, pz, c)
    for i in range(6):
        m.add_cube(200, 20, 60, 0, i * 30, -500 - i * 60, CG_STONE)  # FIX #45: stairs
    enemies = []
    npcs = [
        NPC(-200, 0, 0, NPC_TOAD, "Almost to the top!\nYou need 50 stars for\nthe final floor.", "Toad"),
    ]
    platforms = []
    damage_zones = []
    signs = [
        Sign(0, 0, -400, "Tick Tock Clock and\nRainbow Ride ahead!", 0),
    ]
    cannons = []
    return m, [], [], [], [], (0, 20, 600), enemies, npcs, platforms, damage_zones, signs, cannons

def build_castle_top():
    m = Mesh()
    for x in range(-2, 2):
        for z in range(-2, 2):
            m.add_cube(200, 10, 200, x * 200, -5, z * 200, (180,152,120))
    m.add_cube(800, 300, 40, 0, 150, -400, CG_CASTLE_WALL)
    m.add_cube(800, 300, 40, 0, 150, 400, CG_CASTLE_WALL)
    m.add_cube(40, 300, 800, -400, 150, 0, CG_CASTLE_WALL)
    m.add_cube(40, 300, 800, 400, 150, 0, CG_CASTLE_WALL)
    m.add_cube(100, 300, 100, 0, 150, 0, (224,192,144))
    m.add_cube(60, 20, 60, 0, 10, 0, MARIO_RED)
    m.add_cube(40, 40, 40, 0, 30, 0, STAR_GOLD)
    enemies = []
    npcs = [
        NPC(0, 0, 200, NPC_YOSHI, "Mario! It has been so long\nsince our last adventure!", "Yoshi"),
    ]
    platforms = []
    damage_zones = []
    signs = []
    cannons = []
    return m, [], [], [], [], (0, 20, 300), enemies, npcs, platforms, damage_zones, signs, cannons


# ======= 15 MAIN COURSES =======

def build_bob_omb_battlefield():
    m = Mesh()
    for x in range(-7, 7):
        for z in range(-7, 7):
            c = BOB_GRASS_1 if (x+z) % 2 == 0 else BOB_GRASS_2
            h = math.sin(x * 0.4) * 8 + math.cos(z * 0.5) * 6
            m.add_cube(200, 14, 200, x * 200, -7 + h, z * 200, c)
    path_pts = [(0,-400),(100,-200),(200,0),(100,200),(0,400),(-100,200)]
    for px, pz in path_pts:
        m.add_cube(100, 4, 200, px, 2, pz, BOB_PATH)
    m.add_cube(480, 160, 480, 0, 80, 0, BOB_MTN_LOW)
    m.add_cube(360, 120, 360, 0, 240, 0, BOB_MTN_MID)
    m.add_cube(240, 80, 240, 0, 360, 0, BOB_MTN_MID)
    m.add_cube(140, 60, 140, 0, 440, 0, BOB_MTN_TOP)
    m.add_cube(100, 12, 100, 0, 480, 0, BOB_MTN_TOP)
    m.add_slope(200, 200, 80, 40, -240, 80, 0, BOB_DIRT)
    m.add_slope(160, 200, 60, 30, 0, 240, -180, BOB_DIRT)
    m.add_cube(120, 10, 120, 0, 492, 0, DARK_GREY)
    m.add_cube(8, 40, 8, -440, 20, -240, DARK_GREY)
    m.add_cube(32, 32, 32, -440, 52, -240, (80,56,32))
    m.add_cube(4, 4, 60, -440, 36, -210, DARK_GREY)
    for bx, bz in [(-200,-320),(200,320)]:
        m.add_cube(240, 10, 36, bx, 48, bz, BOB_FENCE)
        for side in [-16, 16]:
            m.add_cube(4, 20, 36, bx + side, 60, bz, BOB_FENCE)
    for cx, cz in [(560,-440),(-560,440)]:
        m.add_cube(28, 12, 28, cx, 6, cz, DARK_GREY)
        m.add_cube(12, 24, 12, cx, 18, cz, METAL_GREY)
    m.add_cube(400, 6, 240, 440, -3, 320, BOB_WATER)
    m.add_water_plane(440, 320, 200, 120, 3)
    m.add_cube(8, 56, 80, -320, 28, -120, BOB_FENCE)
    m.add_cube(8, 56, 80, 320, 28, 120, BOB_FENCE)
    for tx, tz in [(-640,240),(640,-240),(-240,560),(320,-560),(-480,-480),(480,480)]:
        m.add_cube(20, 64, 20, tx, 32, tz, CG_TREE_TRUNK)
        m.add_hill(48, 32, tx, 64, tz, CG_TREE_TOP, CG_TREE_TOP2, 6)
    m.add_hill(360, 140, -1000, 0, -600, BOB_GRASS_1, BOB_GRASS_2)
    m.add_hill(440, 180, 1000, 0, 600, BOB_GRASS_2, BOB_GRASS_1)
    m.add_hill(300, 100, -800, 0, 800, BOB_GRASS_1, BOB_GRASS_2)
    for bx, bz in [(200,-200),(-300,100),(400,200)]:
        m.add_cube(16, 16, 16, bx, 10, bz, BLACK)
        m.add_cube(6, 10, 6, bx, 22, bz, (180,148,112))
    stars = [Star(0,502,0,0), Star(560,20,-440,1), Star(-440,60,-240,2),
             Star(-640,40,240,3), Star(440,10,320,4)]
    coins = [Coin(px, 10, pz) for px, pz in path_pts]
    coins += [Coin(x * 80, 10, z * 80) for x, z in [(-3,3),(3,3),(-3,-3),(3,-3),(0,5)]]
    red_coins = [RedCoin(bx, 18, bz) for bx, bz in [(200,-200),(-300,100),(400,200),
                 (-640,240),(640,-240),(0,400),(-100,200),(100,-200)]]
    oneups = [OneUp(-480, 10, -480)]
    enemies = [
        Enemy(-200, 0, -400, ENEMY_GOOMBA, 120),
        Enemy(100, 0, -200, ENEMY_GOOMBA, 100),
        Enemy(-300, 0, 100, ENEMY_GOOMBA, 140),
        Enemy(200, 0, 300, ENEMY_BOBOMB, 160),
        Enemy(-400, 0, 400, ENEMY_BOBOMB, 120),
        Enemy(400, 0, -100, ENEMY_BOBOMB, 100),
        Enemy(0, 0, 0, ENEMY_CHAIN_CHOMP, 80),
        Enemy(-600, 0, -200, ENEMY_KOOPA, 200),
        Enemy(500, 0, 200, ENEMY_KOOPA, 180),
        Enemy(200, 0, -500, ENEMY_GOOMBA, 100),
        Enemy(-100, 0, 500, ENEMY_BOBOMB, 140),
    ]
    npcs = [
        NPC(0, 0, -600, NPC_BOBOMB_BUDDY, "We are the Bob-omb Buddies!\nWe opened the cannon for you.", "Bob-omb Buddy"),
        NPC(-500, 0, -500, NPC_BOBOMB_BUDDY, "The King Bob-omb is at\nthe top of the mountain!", "Bob-omb Buddy"),
    ]
    platforms = [
        MovingPlatform(300, 160, 0, 72, 8, 72, BOB_MTN_MID, PLATFORM_SLIDE, 1, 0, 0, 0.6, 60, 160),
        MovingPlatform(-200, 80, -100, 60, 8, 60, BOB_PATH, PLATFORM_SLIDE, 0, 1, 0, 0.4, 60, 80),
        MovingPlatform(0, 480, 100, 80, 8, 80, BOB_MTN_TOP, PLATFORM_ROTATE, 0, 0, 0, 0.3, 0, 60),
    ]
    damage_zones = []
    signs = [
        Sign(0, 0, -700, "Bob-omb Battlefield\nDefeat King Bob-omb!", 0),
        Sign(-440, 0, -300, "Caution: Chain Chomp\nahead! Keep distance!", 0),
        Sign(440, 0, 200, "The lake is peaceful...\nfor now.", 0),
    ]
    cannons = [
        Cannon(-500, 0, -400, math.pi * 0.3, 0.7),
        Cannon(500, 0, 500, math.pi * 1.2, 0.5),
    ]
    return m, stars, coins, red_coins, oneups, (0, 20, -800), enemies, npcs, platforms, damage_zones, signs, cannons

def build_whomps_fortress():
    m = Mesh()
    m.add_cube(640, 24, 640, 0, -8, 0, WF_STONE_1)
    m.add_cube(600, 4, 600, 0, 4, 0, WF_GRASS)
    for i in range(6):
        w = 540 - i * 72
        m.add_cube(w, 36, w, 0, i * 56 + 20, 0, WF_STONE_2 if i % 2 == 0 else WF_BRICK)
    m.add_slope(80, 200, 56, 0, -200, 20, -100, WF_STONE_1)
    m.add_slope(80, 200, 56, 0, 200, 76, 100, WF_STONE_1)
    m.add_cube(56, 96, 20, 0, 360, 0, WF_STONE_2)
    m.add_cube(36, 20, 20, -28, 380, 0, WF_STONE_2)
    m.add_cube(36, 20, 20, 28, 380, 0, WF_STONE_2)
    m.add_cube(12, 12, 4, -16, 400, -8, BLACK)
    m.add_cube(12, 12, 4, 16, 400, -8, BLACK)
    m.add_cube(48, 48, 48, 200, 80, 100, DARK_GREY)
    m.add_cube(8, 8, 4, 186, 100, 78, RED)
    m.add_cube(8, 8, 4, 214, 100, 78, RED)
    m.add_cube(120, 8, 36, 100, 120, 200, WF_DIRT)
    for px, pz in [(160,-200),(-160,200)]:
        m.add_cube(28, 36, 28, px, 18, pz, PIPE_GREEN)
        m.add_cube(20, 12, 20, px, 42, pz, RED)
    m.add_cube(80, 200, 80, -260, 100, -260, WF_STONE_1)
    m.add_cube(100, 16, 100, -260, 200, -260, CG_CASTLE_ROOF)
    m.add_cube(24, 16, 24, 300, -4, 300, DARK_GREY)
    m.add_hill(500, 200, -1200, 0, 800, WF_GRASS, (0,112,0))
    m.add_hill(400, 160, 1200, 0, -800, WF_GRASS, (0,112,0))
    stars = [Star(0,380,0,0), Star(-260,220,-260,1), Star(300,20,300,2)]
    coins = [Coin(i * 56 - 140, 40 + i * 10, i * 36) for i in range(6)]
    enemies = [
        Enemy(200, 80, 100, ENEMY_WHOMP, 100),
        Enemy(-100, 0, -100, ENEMY_PIRANHA, 0),
        Enemy(100, 0, 200, ENEMY_PIRANHA, 0),
        Enemy(0, 120, 0, ENEMY_THWOMP, 0),
        Enemy(-200, 0, 100, ENEMY_GOOMBA, 80),
        Enemy(150, 0, -150, ENEMY_GOOMBA, 100),
        Enemy(0, 200, -100, ENEMY_BULLET_BILL, 300),
    ]
    npcs = []
    platforms = [
        MovingPlatform(100, 40, -200, 60, 8, 60, WF_STONE_1, PLATFORM_SLIDE, 0, 1, 0, 0.5, 40, 100),
        MovingPlatform(-100, 100, 100, 48, 8, 48, WF_BRICK, PLATFORM_FALL, 0, 0, 0, 0, 0, 0),
        MovingPlatform(200, 200, -100, 56, 8, 56, WF_STONE_2, PLATFORM_ROTATE, 0, 0, 0, 0.4, 0, 80),
    ]
    damage_zones = []
    signs = [
        Sign(0, 0, 300, "Whomp's Fortress\nBeware the Whomps!", 0),
    ]
    cannons = [Cannon(300, 0, 300, math.pi * 0.5, 0.8)]
    return m, stars, coins, [], [], (0, 20, 400), enemies, npcs, platforms, damage_zones, signs, cannons

def build_jolly_roger_bay():
    m = Mesh()
    for x in range(-4, 4):
        for z in range(-2, 2):
            m.add_cube(200, 10, 200, x * 200, -5, z * 200 - 600, JRB_SAND)
    for x in range(-6, 6):
        for z in range(-4, 6):
            m.add_cube(200, 6, 200, x * 200, -3, z * 200, JRB_WATER)
    m.add_water_plane(0, 200, 1200, 1200, 3)
    for x in range(-6, 6):
        for z in range(-4, 6):
            m.add_cube(200, 10, 200, x * 200, -200, z * 200, JRB_CAVE)
    m.add_cube(100, 56, 280, 200, -120, 200, JRB_SHIP)
    m.add_cube(80, 36, 200, 200, -84, 200, (120,80,44))
    m.add_cube(8, 80, 8, 200, -40, 200, JRB_SHIP)
    m.add_cube(200, 100, 200, -400, -80, -300, JRB_CAVE)
    for cx, cz in [(100,-100),(-200,0),(300,100)]:
        m.add_cube(28, 8, 28, cx, -192, cz, LIGHT_GREY)
        m.add_cube(24, 16, 12, cx, -182, cz, JRB_CORAL)
    m.add_cube(280, 10, 56, -200, 5, -520, JRB_DOCK)
    m.add_cube(16, 28, 16, -340, 18, -520, JRB_DOCK)
    m.add_cube(16, 28, 16, -60, 18, -520, JRB_DOCK)
    m.add_cube(80, 80, 40, 500, -100, 400, BLACK)
    m.add_hill(300, 80, -600, 0, -700, JRB_SAND, (180,152,96))
    m.add_hill(250, 60, 600, 0, -700, JRB_SAND, (180,152,96))
    stars = [Star(200,-60,200,0), Star(-400,-40,-300,1), Star(-200,20,-520,2)]
    coins = [Coin(x * 80, -180, z * 80) for x, z in [(-1,0),(0,1),(1,0),(0,-1),(1,1)]]
    enemies = [
        Enemy(-200, -180, 0, ENEMY_SKEETER, 200),
        Enemy(100, -180, 100, ENEMY_SKEETER, 150),
        Enemy(400, -180, -200, ENEMY_GOOMBA, 100),
    ]
    npcs = [
        NPC(-300, 0, -500, NPC_TOAD, "The pirate ship sank\nlong ago... dive deep!", "Toad"),
    ]
    platforms = [
        MovingPlatform(0, -50, 0, 80, 8, 80, JRB_DOCK, PLATFORM_SLIDE, 1, 0, 0, 0.3, 40, 200),
    ]
    damage_zones = []
    signs = [
        Sign(-200, 0, -450, "Jolly Roger Bay\nDive to find treasures!", 0),
    ]
    cannons = []
    enemies = [
        Enemy(-200, 0, -200, ENEMY_BOO, 200),
        Enemy(200, 0, 200, ENEMY_BOO, 180),
        Enemy(0, 0, -400, ENEMY_BOO, 160),
        Enemy(-400, 0, 100, ENEMY_BOO, 220),
        Enemy(400, 0, -100, ENEMY_BOO, 150),
        Enemy(0, 100, 100, ENEMY_AMP, 60),
        Enemy(-300, 0, 300, ENEMY_GOOMBA, 80),
        Enemy(300, 0, -300, ENEMY_GOOMBA, 100),
    ]
    npcs = [
        NPC(0, 0, 400, NPC_TOAD, "The Big Boo lives in\nthe mansion attic!", "Toad"),
    ]
    platforms = [
        MovingPlatform(0, 200, 0, 60, 4, 60, BBH_FLOOR, PLATFORM_SLIDE, 0, 1, 0, 0.3, 40, 40),
    ]
    damage_zones = []
    signs = [
        Sign(0, 0, -500, "Big Boo's Haunt\nFace the Boos head-on!", 0),
    ]
    cannons = []
    return m, stars, coins, [], [], (0, 20, -600), enemies, npcs, platforms, damage_zones, signs, cannons, enemies, npcs, platforms, damage_zones, signs, cannons

def build_cool_cool_mountain():
    m = Mesh()
    for x in range(-5, 5):
        for z in range(-5, 5):
            c = CCM_SNOW_1 if (x+z) % 2 == 0 else CCM_SNOW_2
            m.add_cube(200, 10, 200, x * 200, -5, z * 200, c)
    for i in range(10):
        w = 220 + i * 56
        c = CCM_SNOW_1 if i % 2 == 0 else CCM_SNOW_2
        m.add_cube(w, 20, w, 0, 600 - i * 56, 0, c)
    m.add_cube(100, 40, 100, -80, 640, 0, CCM_ROCK)
    m.add_cube(36, 56, 36, 0, 660, 0, (120,72,40))
    for i in range(18):
        a = i * 0.38; r = 180 + i * 28
        sx = math.cos(a) * r; sz = math.sin(a) * r
        m.add_cube(72, 8, 72, sx, 560 - i * 30, sz, CCM_SLIDE)
    m.add_cube(120, 72, 120, -300, 36, -400, CCM_CABIN)
    m.add_cube(132, 8, 132, -300, 72, -400, CG_CASTLE_ROOF)
    m.add_cube(40, 56, 4, -300, 28, -338, (104,60,28))
    m.add_cube(24, 24, 4, -260, 48, -338, (120,148,200))
    # Snowman
    m.add_cube(56, 56, 56, 200, 28, 300, CCM_SNOW_1)
    m.add_cube(40, 40, 40, 200, 72, 300, CCM_SNOW_1)
    m.add_cube(16, 8, 16, 200, 88, 272, ORANGE)
    m.add_cube(8, 8, 4, 188, 96, 270, BLACK)
    m.add_cube(8, 8, 4, 212, 96, 270, BLACK)
    m.add_cube(200, 8, 36, -200, 150, 0, CCM_ICE)
    m.add_cube(16, 28, 16, -48, 628, 48, BLACK)
    m.add_cube(16, 8, 16, -48, 640, 48, WHITE)
    m.add_hill(600, 300, -1200, 0, 800, CCM_SNOW_2, CCM_ROCK)
    m.add_hill(500, 240, 1200, 0, -600, CCM_SNOW_1, CCM_ROCK)
    stars = [Star(0,680,0,0), Star(-300,88,-400,1), Star(200,100,300,2)]
    coins = [Coin(math.cos(i * 0.38) * (180 + i * 28), 570 - i * 30,
                  math.sin(i * 0.38) * (180 + i * 28)) for i in range(0, 18, 3)]
    enemies = [
        Enemy(200, 0, -200, ENEMY_FLYGUY, 150),
        Enemy(-100, 0, 100, ENEMY_FLYGUY, 120),
        Enemy(300, 0, 0, ENEMY_GOOMBA, 100),
        Enemy(-200, 500, -100, ENEMY_GOOMBA, 80),
    ]
    npcs = [
        NPC(-300, 0, -350, NPC_PENGUIN, "Have you seen my baby?\nShe slid down the mountain!", "Penguin Mother"),
        NPC(0, 600, 100, NPC_PENGUIN, "Race me down the slide!\nI bet I can beat you!", "Racing Penguin"),
        NPC(200, 0, -300, NPC_PENGUIN, "Brrr! It's cold up here.\nThe cabin has hot cocoa.", "Penguin"),
    ]
    platforms = [
        MovingPlatform(0, 300, 200, 60, 8, 60, CCM_ICE, PLATFORM_SLIDE, 0, 1, 0, 0.6, 40, 100),
        MovingPlatform(-150, 200, -100, 48, 8, 80, CCM_SLIDE, PLATFORM_SLIDE, 1, 0, 0, 0.4, 60, 80),
    ]
    damage_zones = [
        DamageZone(0, 0, 200, 200, -200, -50, ZONE_COLD, 1, 10, 0.5),
    ]
    signs = [
        Sign(0, 600, 300, "Cool, Cool Mountain\nSlide to the bottom!", 0),
        Sign(-300, 0, -300, "Penguin's House\nReturn the baby penguin!", 0),
    ]
    cannons = []
    return m, stars, coins, [], [], (0, 620, 400), enemies, npcs, platforms, damage_zones, signs, cannons

def build_big_boos_haunt():
    m = Mesh()
    for x in range(-4, 4):
        for z in range(-4, 4):
            c = BBH_FLOOR if (x+z) % 2 == 0 else (32,28,40)
            m.add_cube(200, 10, 200, x * 200, -5, z * 200, c)
    m.add_cube(400, 280, 400, 0, 140, 0, BBH_WALL)
    m.add_pyramid(450, 140, 0, 280, 0, BBH_ROOF)
    for wx, wy in [(-120,200),(120,200),(-120,100),(120,100)]:
        m.add_cube(48, 36, 4, wx, wy, -200, BBH_WINDOW)
    m.add_cube(56, 112, 4, 0, 56, -200, (112,72,36))
    m.add_cube(350, 10, 350, 0, -2, 0, BBH_FLOOR)
    for gx, gz in [(-500,-200),(-500,-400),(-600,-300),(500,200),(500,400)]:
        m.add_cube(28, 40, 8, gx, 20, gz, BBH_GRAVE)
        m.add_cube(36, 4, 12, gx, -2, gz, (112,80,48))
    m.add_cube(36, 36, 36, 100, 100, 300, BBH_GHOST)
    m.add_cube(8, 6, 4, 86, 106, 282, BLACK)
    m.add_cube(8, 6, 4, 114, 106, 282, BLACK)
    m.add_cube(80, 2, 80, -100, 240, 0, (180,152,128))
    m.add_cube(200, 10, 56, 0, 200, -230, BBH_FLOOR)
    m.add_cube(200, 5, 200, 0, -100, 300, BBH_FLOOR)
    m.add_cube(100, 28, 100, 0, -86, 300, (112,72,36))
    for tx, tz in [(-600,0),(600,0),(0,600)]:
        m.add_cube(16, 80, 16, tx, 40, tz, (104,60,28))
        m.add_cube(8, 24, 48, tx, 80, tz, (112,68,36))
    stars = [Star(0,300,0,0), Star(100,120,300,1), Star(0,-72,300,2)]
    coins = [Coin(gx, 30, gz) for gx, gz in [(-500,-200),(500,200),(-200,0),(200,0)]]
    return m, stars, coins, [], [], (0, 20, -600)

def build_hazy_maze_cave():
    m = Mesh()
    for x in range(-6, 6):
        for z in range(-6, 6):
            c = HMC_ROCK_1 if (x+z) % 2 == 0 else HMC_ROCK_2
            m.add_cube(200, 10, 200, x * 200, -5, z * 200, c)
    m.add_cube(2400, 20, 2400, 0, 280, 0, HMC_ROCK_2)
    walls = [(-400,0,800,40),(-400,0,40,800),(400,0,800,40),(400,0,40,800),
             (0,-400,40,400),(0,400,40,400),(200,200,400,40),(-200,-200,400,40)]
    for wx, wz, ww, wd in walls:
        m.add_cube(ww, 200, wd, wx, 100, wz, HMC_ROCK_1)
    m.add_cube(600, 4, 600, -400, -3, -400, HMC_TOXIC)
    m.add_cube(200, 10, 200, 500, -2, 500, HMC_METAL)
    m.add_cube(40, 40, 40, 500, 20, 500, BUTTON_GOLD)
    m.add_cube(500, 6, 500, 0, -3, 0, HMC_WATER)
    m.add_water_plane(0, 0, 250, 250, 3)
    m.add_cube(80, 36, 120, 0, 18, 0, (0,120,0))
    m.add_cube(28, 28, 36, 0, 48, 48, (0,112,0))
    stars = [Star(500,40,500,0), Star(0,56,0,1), Star(-400,10,-400,2)]
    coins = [Coin(x * 150, 10, z * 150) for x, z in [(0,0),(1,1),(-1,-1),(2,0)]]
    enemies = [
        Enemy(-200, 0, -200, ENEMY_MONTY_MOLE, 120),
        Enemy(200, 0, 200, ENEMY_MONTY_MOLE, 100),
        Enemy(300, 0, -300, ENEMY_SNUFIT, 80),
        Enemy(-300, 0, 100, ENEMY_SNUFIT, 60),
        Enemy(0, 0, 400, ENEMY_GOOMBA, 100),
        Enemy(-400, 0, -100, ENEMY_GOOMBA, 80),
    ]
    npcs = []
    platforms = [
        MovingPlatform(200, 50, -200, 72, 8, 72, HMC_METAL, PLATFORM_SLIDE, 1, 0, 0, 0.5, 40, 200),
        MovingPlatform(-200, 100, 200, 56, 8, 56, HMC_ROCK_1, PLATFORM_FALL, 0, 0, 0, 0, 0, 0),
    ]
    damage_zones = [
        DamageZone(-400, -400, 300, 300, -10, 5, ZONE_TOXIC, 1, 12),
    ]
    signs = [
        Sign(0, 0, 700, "Hazy Maze Cave\nWatch out for toxic gas!", 0),
    ]
    cannons = []
    return m, stars, coins, [], [], (0, 20, 800), enemies, npcs, platforms, damage_zones, signs, cannons

def build_lethal_lava_land():
    """FIX #2: platform tuples now (px, pz, ps) — py removed from misuse as z-coord."""
    m = Mesh()
    for x in range(-6, 6):
        for z in range(-6, 6):
            c = LLL_LAVA_1 if (x+z) % 2 == 0 else LLL_LAVA_2
            m.add_cube(200, 6, 200, x * 200, -3, z * 200, c)
    # FIX #2: tuples are now (px, pz, size) — not (px, py, ps) with py misused
    platforms = [(0,0,200),(300,200,140),(-300,-200,140),(200,400,200),(500,100,96),
                 (-500,-100,96),(200,-200,280),(-200,280,200),(0,-400,200),(400,-480,140)]
    for px, pz, ps in platforms:
        m.add_cube(ps, 20, ps, px, 10, pz, LLL_STONE)
    m.add_cube(300, 200, 300, 0, 100, 0, LLL_VOLCANO)
    m.add_cube(200, 100, 200, 0, 250, 0, DARK_GREY)
    m.add_cube(100, 8, 100, 0, 300, 0, LLL_LAVA_2)
    m.add_cube(80, 8, 80, 0, 148, 0, LLL_STONE)
    m.add_cube(56, 8, 56, 48, 196, 0, LLL_STONE)
    m.add_cube(16, 16, 200, -200, 18, -100, (120,64,24))
    m.add_cube(100, 8, 100, 400, 18, 400, LLL_METAL)
    m.add_cube(100, 8, 100, -400, 18, -400, LLL_METAL)
    for fx, fz in [(150,150),(-150,-150),(300,-200)]:
        m.add_cube(16, 36, 16, fx, 28, fz, ORANGE)
        m.add_cube(24, 8, 24, fx, 48, fz, YELLOW)
    stars = [Star(0,310,0,0), Star(-400,36,-400,1), Star(500,28,100,2)]
    coins = [Coin(px, 28, pz) for px, pz, ps in platforms[:5]]
    enemies = [
        Enemy(200, 20, 200, ENEMY_HEAVE_HO, 80),
        Enemy(-200, 20, -200, ENEMY_HEAVE_HO, 100),
        Enemy(400, 20, -100, ENEMY_HEAVE_HO, 60),
        Enemy(-100, 20, 300, ENEMY_FLYGUY, 120),
        Enemy(300, 20, 100, ENEMY_GOOMBA, 60),
    ]
    npcs = []
    platforms = [
        MovingPlatform(150, 18, -100, 56, 8, 56, LLL_STONE, PLATFORM_SLIDE, 1, 0, 0, 0.8, 40, 140),
        MovingPlatform(-150, 18, 100, 56, 8, 56, LLL_STONE, PLATFORM_SLIDE, 0, 0, 1, 0.6, 40, 120),
        MovingPlatform(0, 100, 200, 48, 8, 48, LLL_METAL, PLATFORM_SEESAW, 0, 0, 0, 0, 0, 0),
    ]
    damage_zones = [
        DamageZone(0, 0, 1200, 1200, -20, 8, ZONE_LAVA, 3, 25),
    ]
    signs = []
    cannons = []
    return m, stars, coins, [], [], (0, 30, -400), enemies, npcs, platforms, damage_zones, signs, cannons

def build_shifting_sand_land():
    m = Mesh()
    for x in range(-7, 7):
        for z in range(-7, 7):
            c = SSL_SAND_1 if (x+z) % 2 == 0 else SSL_SAND_2
            h = math.sin(x * 0.6) * 6 + math.cos(z * 0.4) * 4
            m.add_cube(200, 12, 200, x * 200, -6 + h, z * 200, c)
    m.add_cube(400, 280, 400, 0, 140, 0, SSL_PYRAMID)
    m.add_pyramid(420, 100, 0, 280, 0, SSL_BRICK)
    m.add_cube(300, 200, 300, 0, 100, 0, (152,120,72))
    m.add_cube(80, 8, 80, 0, 200, 0, (136,104,60))
    m.add_cube(300, 4, 300, -500, -3, -500, SSL_QUICKSAND)
    m.add_cube(200, 4, 200, 500, -1, 500, SSL_OASIS)
    m.add_water_plane(500, 500, 100, 100, 1)
    m.add_cube(20, 56, 20, 520, 28, 520, CG_TREE_TRUNK)
    m.add_cube(56, 8, 56, 520, 56, 520, SSL_PALM)
    for px, pz in [(-300,300),(300,-300),(-300,-300),(300,300)]:
        m.add_cube(36, 120, 36, px, 60, pz, SSL_SAND_1)
        m.add_cube(48, 12, 48, px, 120, pz, SSL_BRICK)
    m.add_cube(56, 56, 56, 200, 28, -200, DARK_GREY)
    m.add_cube(56, 56, 56, -200, 28, 200, DARK_GREY)
    m.add_hill(500, 100, -1200, 0, 0, SSL_SAND_2, SSL_SAND_1)
    m.add_hill(600, 120, 1200, 0, 0, SSL_SAND_1, SSL_SAND_2)
    m.add_hill(400, 80, 0, 0, 1400, SSL_SAND_2, SSL_SAND_1)
    stars = [Star(0,390,0,0), Star(500,16,500,1), Star(-500,8,-500,2)]
    coins = [Coin(x * 200, 10, z * 200) for x, z in [(1,1),(-1,-1),(2,-2),(-2,2),(0,3)]]
    enemies = [
        Enemy(-400, 0, 400, ENEMY_POKEY, 60),
        Enemy(400, 0, -400, ENEMY_POKEY, 80),
        Enemy(-200, 0, -300, ENEMY_FLYGUY, 200),
        Enemy(200, 0, 300, ENEMY_FLYGUY, 180),
        Enemy(0, 0, -600, ENEMY_GOOMBA, 120),
        Enemy(600, 0, 0, ENEMY_GOOMBA, 100),
        Enemy(-600, 0, 200, ENEMY_BOBOMB, 150),
    ]
    npcs = []
    platforms = [
        MovingPlatform(0, 200, 300, 60, 8, 60, SSL_PYRAMID, PLATFORM_SLIDE, 1, 0, 0, 0.4, 60, 120),
    ]
    damage_zones = [
        DamageZone(-500, -500, 150, 150, -10, 5, ZONE_QUICKSAND, 1, 0, 0.3),
    ]
    signs = [
        Sign(0, 0, -700, "Shifting Sand Land\nBeware the quicksand!", 0),
    ]
    cannons = [Cannon(600, 0, 600, math.pi * 1.5, 0.6)]
    return m, stars, coins, [], [], (0, 20, -800), enemies, npcs, platforms, damage_zones, signs, cannons

def build_dire_dire_docks():
    m = Mesh()
    for x in range(-3, 3):
        m.add_cube(200, 10, 200, x * 200, -5, -600, DDD_DOCK)
    for x in range(-6, 6):
        for z in range(-4, 6):
            m.add_cube(200, 6, 200, x * 200, -3, z * 200, DDD_WATER)
    m.add_water_plane(0, 200, 1200, 1200, 3)
    for x in range(-6, 6):
        for z in range(-4, 6):
            m.add_cube(200, 10, 200, x * 200, -200, z * 200, DDD_FLOOR)
    m.add_cube(120, 56, 380, 0, -60, 200, DDD_SUB)
    m.add_cube(80, 36, 96, 0, -28, 380, DDD_METAL)
    m.add_cube(8, 56, 8, 0, 0, 380, DDD_METAL)
    m.add_cube(200, 200, 16, 0, 100, 800, DDD_METAL)
    m.add_cube(8, 200, 8, -88, 100, 800, DARK_GREY)
    m.add_cube(8, 200, 8, 88, 100, 800, DARK_GREY)
    m.add_cube(96, 4, 96, -400, -1, 400, PURPLE)
    for px, pz in [(300,0),(-300,0),(0,600)]:
        m.add_cube(8, 140, 8, px, -120, pz, DDD_METAL)
    stars = [Star(0,-20,200,0), Star(0,10,800,1), Star(-400,10,400,2)]
    coins = [Coin(x * 96, -80, z * 96) for x, z in [(0,0),(1,2),(-1,3),(2,1)]]
    enemies = [
        Enemy(200, -100, 400, ENEMY_SKEETER, 200),
        Enemy(-200, -100, 200, ENEMY_SKEETER, 150),
        Enemy(300, -100, -200, ENEMY_GOOMBA, 100),
    ]
    npcs = []
    platforms = [
        MovingPlatform(0, -40, 400, 80, 8, 80, DDD_METAL, PLATFORM_SLIDE, 0, 1, 0, 0.3, 40, 60),
        MovingPlatform(200, 0, -400, 60, 8, 60, DDD_DOCK, PLATFORM_SLIDE, 1, 0, 0, 0.5, 60, 200),
    ]
    damage_zones = []
    signs = [Sign(0, 0, -500, "Dire, Dire Docks\nSwim to find secrets!", 0)]
    cannons = []
    return m, stars, coins, [], [], (0, 20, -600), enemies, npcs, platforms, damage_zones, signs, cannons

def build_snowmans_land():
    m = Mesh()
    for x in range(-6, 6):
        for z in range(-6, 6):
            c = SL_SNOW_1 if (x+z) % 2 == 0 else SL_SNOW_2
            m.add_cube(200, 10, 200, x * 200, -5, z * 200, c)
    m.add_cube(300, 200, 300, 0, 100, 0, SL_SNOW_1)
    m.add_cube(200, 140, 200, 0, 270, 0, SL_SNOW_2)
    m.add_cube(120, 96, 120, 0, 388, 0, SL_SNOW_1)
    m.add_cube(80, 72, 80, 0, 472, 0, SL_SNOW_1)
    m.add_cube(16, 16, 16, 0, 484, -36, ORANGE)
    m.add_cube(8, 8, 4, -12, 496, -34, BLACK)
    m.add_cube(8, 8, 4, 12, 496, -34, BLACK)
    m.add_cube(200, 6, 36, -200, 148, 0, SL_ICE)
    m.add_cube(100, 56, 100, -400, 28, -300, SL_IGLOO)
    m.add_cube(36, 36, 8, -400, 18, -348, (112,60,28))
    m.add_cube(300, 4, 300, 400, -1, 400, SL_ICE)
    m.add_cube(28, 28, 28, 200, 18, 400, BLACK)
    m.add_cube(6, 16, 6, 200, 40, 400, METAL_GREY)
    m.add_cube(140, 8, 140, 0, 96, 500, SL_ICE)
    for tx, tz in [(-500,200),(500,-200),(-200,500)]:
        m.add_cube(16, 56, 16, tx, 28, tz, CG_TREE_TRUNK)
        m.add_hill(44, 28, tx, 56, tz, SL_ICE, SL_SNOW_2, 6)
    m.add_hill(500, 200, -1200, 0, 600, SL_SNOW_2, CCM_ROCK)
    m.add_hill(600, 260, 1200, 0, -400, SL_SNOW_1, CCM_ROCK)
    stars = [Star(0,520,0,0), Star(-400,56,-300,1), Star(0,112,500,2)]
    coins = [Coin(x * 120, 10, z * 120) for x, z in [(2,2),(-2,-2),(3,0),(0,3)]]
    enemies = [
        Enemy(-300, 0, 200, ENEMY_FLYGUY, 160),
        Enemy(300, 0, -200, ENEMY_FLYGUY, 140),
        Enemy(0, 0, 400, ENEMY_GOOMBA, 120),
        Enemy(-200, 0, -400, ENEMY_GOOMBA, 100),
        Enemy(400, 0, 300, ENEMY_FLYGUY, 180),
    ]
    npcs = [
        NPC(-400, 0, -250, NPC_PENGUIN, "The snowman's head\nis up above. Watch out\nfor his breath!", "Penguin"),
    ]
    platforms = [
        MovingPlatform(-100, 100, 300, 60, 8, 60, SL_ICE, PLATFORM_SLIDE, 0, 1, 0, 0.4, 40, 80),
    ]
    damage_zones = [
        DamageZone(400, 400, 150, 150, -10, 5, ZONE_COLD, 1, 8, 0.6),
    ]
    signs = [Sign(0, 0, -700, "Snowman's Land\nClimb to the summit!", 0)]
    cannons = []
    return m, stars, coins, [], [], (0, 20, -800), enemies, npcs, platforms, damage_zones, signs, cannons

def build_wet_dry_world():
    m = Mesh()
    for x in range(-4, 4):
        for z in range(-4, 4):
            c = WDW_BRICK if (x+z) % 2 == 0 else WDW_STONE
            m.add_cube(200, 10, 200, x * 200, -5, z * 200, c)
    m.add_cube(1600, 4, 1600, 0, 48, 0, WDW_WATER)
    m.add_water_plane(0, 0, 800, 800, 50)
    m.add_cube(200, 280, 200, -300, 140, 0, WDW_BRICK)
    m.add_cube(200, 200, 200, 300, 100, -200, WDW_BRICK)
    m.add_cube(150, 240, 150, 0, 120, 300, WDW_STONE)
    for sx, sz in [(-300,300),(300,-300),(0,0)]:
        m.add_cube(28, 28, 28, sx, 18, sz, WDW_SWITCH)
    m.add_cube(56, 56, 56, -100, 28, -200, METAL_GREY)
    m.add_cube(56, 56, 56, 200, 28, 200, METAL_GREY)
    m.add_cube(100, 96, 100, -500, 48, -400, METAL_GREY)
    m.add_cube(600, 8, 400, 0, -100, -500, (104,72,40))
    m.add_cube(100, 72, 100, -200, -64, -500, WDW_BRICK)
    m.add_cube(100, 72, 100, 200, -64, -500, WDW_BRICK)
    stars = [Star(-300,290,0,0), Star(0,260,300,1), Star(-200,-50,-500,2)]
    coins = [Coin(x * 96, 56, z * 96) for x, z in [(0,0),(1,1),(-1,-1),(2,-2)]]
    enemies = [
        Enemy(-200, 50, 200, ENEMY_SKEETER, 120),
        Enemy(200, 50, -200, ENEMY_SKEETER, 100),
        Enemy(0, 50, 0, ENEMY_HEAVE_HO, 80),
        Enemy(-300, 0, -300, ENEMY_AMP, 60),
    ]
    npcs = []
    platforms = [
        MovingPlatform(0, 80, -200, 72, 8, 72, WDW_BRICK, PLATFORM_SLIDE, 0, 1, 0, 0.6, 40, 120),
        MovingPlatform(200, 40, 300, 56, 8, 56, WDW_STONE, PLATFORM_ARROW, 0, 1, 0, 1.5, 0, 200),
    ]
    damage_zones = []
    signs = [Sign(0, 0, -500, "Wet-Dry World\nTouch the crystals to\nchange water level!", 0)]
    cannons = [Cannon(-400, 0, -300, math.pi * 0.4, 0.7)]
    return m, stars, coins, [], [], (0, 20, -600), enemies, npcs, platforms, damage_zones, signs, cannons

def build_tall_tall_mountain():
    m = Mesh()
    for x in range(-5, 5):
        for z in range(-5, 5):
            c = TTM_GRASS if (x+z) % 2 == 0 else (0,120,0)
            m.add_cube(200, 10, 200, x * 200, -5, z * 200, c)
    m.add_cube(500, 280, 500, 0, 140, 0, TTM_DIRT)
    m.add_cube(400, 240, 400, 0, 400, 0, TTM_ROCK)
    m.add_cube(300, 200, 300, 0, 640, 0, DARK_GREY)
    m.add_cube(200, 140, 200, 0, 840, 0, (128,88,56))
    m.add_cube(120, 80, 120, 0, 980, 0, (112,80,48))
    m.add_pyramid(140, 56, 0, 1020, 0, DARK_STONE)
    for i in range(22):
        a = i * 0.32; r = 280 + 48 * math.sin(i * 0.5)
        px = math.cos(a) * r; pz = math.sin(a) * r
        m.add_cube(72, 8, 72, px, i * 44 + 16, pz, TTM_ROCK)
    m.add_cube(56, 380, 16, -260, 190, -200, TTM_WATER)
    m.add_cube(80, 8, 48, -260, 4, -200, TTM_WATER)
    for mx, mz, mh in [(400,200,56),(400,300,96),(-400,-200,72)]:
        m.add_cube(16, mh, 16, mx, mh / 2, mz, TTM_MUSH_STEM)
        m.add_cube(52, 12, 52, mx, mh, mz, TTM_MUSH_TOP)
    m.add_cube(96, 8, 96, 200, 380, -200, TTM_GRASS)
    m.add_cube(36, 36, 36, 0, 1052, 0, (120,72,40))
    m.add_hill(500, 200, -1200, 0, 800, TTM_GRASS, (0,112,0))
    m.add_hill(600, 280, 1200, 0, -600, TTM_GRASS, (0,104,0))
    stars = [Star(0,1060,0,0), Star(200,400,-200,1), Star(-400,88,-200,2)]
    coins = [Coin(math.cos(i * 0.32) * 280, i * 44 + 24, math.sin(i * 0.32) * 280)
             for i in range(0, 22, 4)]
    enemies = [
        Enemy(200, 0, -200, ENEMY_MONTY_MOLE, 100),
        Enemy(-200, 0, 200, ENEMY_MONTY_MOLE, 120),
        Enemy(400, 0, 100, ENEMY_FLYGUY, 200),
        Enemy(-400, 0, -100, ENEMY_FLYGUY, 180),
        Enemy(0, 400, 0, ENEMY_GOOMBA, 60),
        Enemy(100, 200, -100, ENEMY_GOOMBA, 80),
    ]
    npcs = [
        NPC(0, 0, -700, NPC_TOAD, "The mountain peak is\nway up there! Good luck!", "Toad"),
    ]
    platforms = [
        MovingPlatform(0, 600, 200, 60, 8, 60, TTM_ROCK, PLATFORM_SLIDE, 1, 0, 0, 0.5, 60, 100),
        MovingPlatform(-200, 300, -100, 48, 8, 48, TTM_DIRT, PLATFORM_FALL, 0, 0, 0, 0, 0, 0),
    ]
    damage_zones = []
    signs = [Sign(0, 0, -700, "Tall, Tall Mountain\nScale the peak!", 0)]
    cannons = [Cannon(-300, 0, -300, math.pi * 0.2, 0.9)]
    return m, stars, coins, [], [], (0, 20, -800), enemies, npcs, platforms, damage_zones, signs, cannons

def build_tiny_huge_island():
    m = Mesh()
    for x in range(-5, 5):
        for z in range(-5, 5):
            dist = math.sqrt(x * x + z * z)
            if dist < 5:
                c = THI_GRASS_1 if (x+z) % 2 == 0 else THI_GRASS_2
                h = max(0, 36 - dist * 7)
                m.add_cube(200, 10 + h, 200, x * 200, h / 2, z * 200, c)
    for x in range(-6, 6):
        for z in range(-6, 6):
            if math.sqrt(x * x + z * z) >= 4:
                m.add_cube(200, 6, 200, x * 200, -3, z * 200, THI_WATER)
    m.add_water_plane(0, 0, 1200, 1200, 3)
    m.add_cube(300, 200, 300, 0, 100, 0, TTM_DIRT)
    m.add_cube(200, 100, 200, 0, 250, 0, TTM_ROCK)
    m.add_cube(36, 28, 36, -300, 48, -300, THI_PIPE)
    m.add_cube(72, 56, 72, 300, 56, 300, THI_PIPE)
    m.add_cube(56, 112, 56, -200, 56, 200, (160,112,72))
    m.add_cube(8, 72, 8, -200, 128, 168, (120,72,36))
    m.add_cube(72, 8, 8, -200, 168, 166, (120,72,36))
    m.add_cube(280, 6, 96, 0, -2, -500, THI_BEACH)
    for px, pz in [(100,100),(-100,-100),(200,-200)]:
        m.add_cube(20, 28, 20, px, 46, pz, THI_PIPE)
        m.add_cube(16, 10, 16, px, 62, pz, RED)
    m.add_cube(56, 56, 16, 0, 240, -96, BLACK)
    m.add_hill(500, 160, -1200, 0, 400, THI_GRASS_1, THI_GRASS_2)
    m.add_hill(400, 120, 1000, 0, -600, THI_GRASS_2, THI_GRASS_1)
    stars = [Star(0,300,0,0), Star(-200,128,200,1), Star(0,10,-500,2)]
    coins = [Coin(x * 96, 48, z * 96) for x, z in [(0,1),(1,0),(-1,0),(0,-1),(1,1)]]
    enemies = [
        Enemy(200, 40, 200, ENEMY_GOOMBA, 100),
        Enemy(-200, 40, -200, ENEMY_GOOMBA, 120),
        Enemy(100, 40, -100, ENEMY_KOOPA, 140),
        Enemy(-100, 40, 100, ENEMY_PIRANHA, 0),
        Enemy(300, 40, -200, ENEMY_PIRANHA, 0),
    ]
    npcs = []
    platforms = [
        MovingPlatform(0, 100, -200, 60, 8, 60, THI_GRASS_1, PLATFORM_SLIDE, 1, 0, 0, 0.4, 40, 120),
    ]
    damage_zones = []
    signs = [Sign(0, 0, -350, "Tiny-Huge Island\nPipes change your size!", 0)]
    cannons = []
    return m, stars, coins, [], [], (0, 50, -400), enemies, npcs, platforms, damage_zones, signs, cannons

def build_tick_tock_clock():
    m = Mesh()
    m.add_cube(300, 20, 300, 0, -5, 0, TTC_WOOD)
    m.add_cube(40, 1200, 600, -300, 600, 0, TTC_WOOD)
    m.add_cube(40, 1200, 600, 300, 600, 0, TTC_WOOD)
    m.add_cube(600, 1200, 40, 0, 600, -300, TTC_WOOD)
    m.add_cube(600, 1200, 40, 0, 600, 300, TTC_WOOD)
    heights = [72, 168, 280, 400, 520, 640, 760, 880, 1000, 1120]
    for i, h in enumerate(heights):
        a = i * 0.7; px = math.cos(a) * 96; pz = math.sin(a) * 96
        w = 96 if i % 2 == 0 else 72
        m.add_cube(w, 8, w, px, h, pz, TTC_METAL)
    m.add_cube(8, 200, 8, -96, 500, 0, TTC_HAND)
    m.add_cube(8, 280, 8, 96, 600, 0, TTC_HAND)
    for gh in [200, 480, 760]:
        m.add_cube(72, 8, 72, -200, gh, 96, TTC_GEAR)
        m.add_cube(56, 8, 56, 200, gh, -96, TTC_GEAR)
    m.add_cube(48, 48, 48, 0, 380, 0, DARK_GREY)
    m.add_cube(200, 6, 36, 0, 680, 0, TTC_GEAR)
    m.add_cube(200, 6, 36, 0, 840, 0, TTC_GEAR)
    m.add_cube(200, 16, 200, 0, 1180, 0, BUTTON_GOLD)
    stars = [Star(0,1200,0,0), Star(-200,500,96,1), Star(0,690,0,2)]
    coins = [Coin(math.cos(i * 0.7) * 96, heights[i] + 12, math.sin(i * 0.7) * 96)
             for i in range(0, 10, 2)]
    enemies = [
        Enemy(0, 200, 0, ENEMY_AMP, 60),
        Enemy(-100, 400, 0, ENEMY_AMP, 40),
        Enemy(100, 600, 0, ENEMY_HEAVE_HO, 40),
        Enemy(0, 800, 0, ENEMY_AMP, 50),
    ]
    npcs = []
    platforms = [
        MovingPlatform(96, 300, 0, 56, 8, 56, TTC_GEAR, PLATFORM_SLIDE, 1, 0, 0, 0.8, 40, 80),
        MovingPlatform(-96, 500, 0, 48, 8, 48, TTC_METAL, PLATFORM_SLIDE, 0, 0, 1, 0.6, 40, 60),
        MovingPlatform(0, 700, 96, 60, 8, 60, TTC_GEAR, PLATFORM_ROTATE, 0, 0, 0, 0.5, 0, 40),
    ]
    damage_zones = []
    signs = [Sign(0, 0, 150, "Tick Tock Clock\nTime your jumps!", 0)]
    cannons = []
    return m, stars, coins, [], [], (0, 20, 200), enemies, npcs, platforms, damage_zones, signs, cannons

def build_rainbow_ride():
    m = Mesh()
    m.add_cube(200, 16, 200, 0, -5, 0, RR_CLOUD)  # FIX #47: spawn matches platform
    for i in range(32):
        c = RR_RAINBOW[i % 6]; a = i * 0.14; px = i * 76; pz = math.sin(a) * 200; py = i * 18
        m.add_cube(56, 6, 56, px, py, pz, c)
    m.add_cube(72, 4, 72, -200, 96, -200, RR_CARPET)
    for i in range(12):
        m.add_cube(56, 6, 56, -200 - i * 96, 96 + i * 28, -200 - i * 76, RR_CARPET)
    m.add_cube(200, 112, 200, 800, 192, 0, RR_HOUSE)
    m.add_cube(220, 8, 220, 800, 248, 0, CG_CASTLE_ROOF)
    m.add_cube(36, 72, 8, 800, 192, -96, (136,80,32))
    for i in range(5):
        for j in range(3):
            m.add_cube(72, 6, 72, 400 + i * 96, 280 + j * 56, -280 + j * 96, RR_CLOUD)
    for sx in range(-96, 400, 140):
        m.add_cube(56, 6, 56, sx, 72, -400, METAL_GREY)
    m.add_cube(48, 6, 48, 500, 96, 280, ORANGE)
    m.add_cube(48, 6, 48, 600, 120, 340, ORANGE)
    m.add_cube(8, 200, 8, 1000, 280, 0, METAL_GREY)
    for i in range(4):
        m.add_cube(96, 6, 96, -400 + i * 56, 192 + i * 36, 280 + i * 56, RR_RAINBOW[0])
    for cx, cz in [(1200,200),(1200,-200),(1400,0)]:
        m.add_cube(96, 16, 96, cx, 384, cz, RR_CLOUD)
    m.add_cube(120, 16, 120, 1400, 400, 0, BUTTON_GOLD)
    stars = [Star(1400,420,0,0), Star(800,264,0,1),
             Star(-200 - 11 * 96, 96 + 11 * 28, -200 - 11 * 76, 2)]
    coins = [Coin(i * 76, i * 18 + 8, math.sin(i * 0.14) * 200) for i in range(0, 32, 5)]
    enemies = [
        Enemy(200, 40, 0, ENEMY_FLYGUY, 120),
        Enemy(600, 120, 0, ENEMY_FLYGUY, 100),
        Enemy(1000, 200, 0, ENEMY_AMP, 60),
        Enemy(400, 100, -200, ENEMY_GOOMBA, 80),
    ]
    npcs = []
    platforms = [
        MovingPlatform(100, 30, 0, 56, 6, 56, METAL_GREY, PLATFORM_SLIDE, 1, 0, 0, 0.5, 40, 200),
        MovingPlatform(500, 100, 200, 48, 6, 48, ORANGE, PLATFORM_ARROW, 0, 1, 0, 1.0, 0, 100),
        MovingPlatform(800, 200, -100, 60, 6, 60, RR_CLOUD, PLATFORM_SLIDE, 0, 0, 1, 0.3, 40, 100),
    ]
    damage_zones = []
    signs = [Sign(0, 0, -50, "Rainbow Ride\nDon't look down!", 0)]
    cannons = [Cannon(0, 0, -100, 0, 0.8)]
    return m, stars, coins, [], [], (0, 20, 0), enemies, npcs, platforms, damage_zones, signs, cannons


# ======= SECRET LEVELS =======

def build_princess_secret_slide():
    m = Mesh()
    m.add_cube(200, 16, 200, 0, 580, 0, CG_CASTLE_WALL)
    for i in range(25):
        a = i * 0.3; r = 96 + i * 14; px = math.cos(a) * r; pz = math.sin(a) * r
        m.add_cube(56, 6, 56, px, 560 - i * 20, pz, CCM_SLIDE)
    ep = (math.cos(24 * 0.3) * (96 + 24 * 14), math.sin(24 * 0.3) * (96 + 24 * 14))
    m.add_cube(200, 16, 200, ep[0], 40, ep[1], CG_CASTLE_WALL)
    stars = [Star(ep[0], 60, ep[1], 0)]
    enemies = []
    return m, stars, [], [], [], (0, 600, 0), enemies, [], [], [], [], []

def build_wing_mario_rainbow():
    m = Mesh()
    m.add_cube(140, 16, 140, 0, -5, 0, RR_CLOUD)
    for i in range(20):
        c = RR_RAINBOW[i % 6]; a = i * 0.3; r = 200 + i * 36
        m.add_cube(72, 6, 72, math.cos(a) * r, i * 28 + 8, math.sin(a) * r, c)
    for cx, cz in [(600,300),(-400,500),(200,-400)]:
        m.add_cube(112, 16, 112, cx, 192, cz, RR_CLOUD)
    m.add_cube(36, 36, 36, 0, 8, 0, MARIO_RED)
    stars = [Star(600, 212, 300, 0)]
    coins = [Coin(math.cos(i * 0.3) * (200 + i * 36), i * 28 + 16,
                  math.sin(i * 0.3) * (200 + i * 36)) for i in range(0, 20, 4)]
    enemies = [Enemy(300, 100, 100, ENEMY_FLYGUY, 200)]
    return m, stars, coins, [], [], (0, 20, 0), enemies, [], [], [], [], []

def build_metal_cap_cavern():
    m = Mesh()
    for x in range(-4, 4):
        for z in range(-4, 4):
            c = HMC_ROCK_1 if (x+z) % 2 == 0 else HMC_ROCK_2
            m.add_cube(200, 10, 200, x * 200, -5, z * 200, c)
    m.add_cube(1600, 20, 1600, 0, 240, 0, HMC_ROCK_2)
    m.add_cube(800, 4, 800, 0, -1, 0, HMC_WATER)
    m.add_water_plane(0, 0, 400, 400, 1)
    m.add_cube(56, 16, 56, 0, 8, 0, PIPE_GREEN)
    m.add_cube(36, 36, 36, 0, 24, 0, METAL_GREY)
    m.add_cube(96, 192, 16, 300, 96, -400, (100,88,120))
    for i in range(5):
        m.add_cube(72, 8, 72, -200 + i * 96, 4, 200 - i * 72, HMC_ROCK_1)
    stars = [Star(0, 44, 0, 0)]
    enemies = [Enemy(200, 0, -200, ENEMY_SNUFIT, 60), Enemy(-200, 0, 200, ENEMY_GOOMBA, 80)]
    cap_switches = [CapSwitch(0, 0, 0, CAP_METAL)]
    return m, stars, [], [], [], (0, 20, 400), enemies, [], [], [], [], []

def build_vanish_cap():
    m = Mesh()
    m.add_cube(200, 16, 200, 0, 192, 0, HMC_ROCK_1)
    for i in range(15):
        m.add_cube(96, 8, 96, i * 76, 176 - i * 11, 0, SL_ICE if i % 2 == 0 else (0,136,144))
    m.add_cube(56, 16, 56, 1140, 8, 0, (0,136,144))
    m.add_cube(36, 36, 36, 1140, 24, 0, MARIO_BLUE)
    for i in range(8):
        m.add_cube(56, 8, 56, 600 + i * 72, 56 + i * 8, i * 36 - 140, HMC_ROCK_1)
    stars = [Star(1140, 44, 0, 0)]
    enemies = [Enemy(600, 60, 0, ENEMY_AMP, 40)]
    return m, stars, [], [], [], (0, 210, 0), enemies, [], [], [], [], []

def build_tower_wing_cap():
    m = Mesh()
    m.add_cube(280, 16, 280, 0, -5, 0, RR_CLOUD)
    m.add_cube(56, 380, 56, 0, 192, 0, (160,120,72))
    m.add_cube(96, 16, 96, 0, 380, 0, RR_CLOUD)
    m.add_cube(36, 36, 36, 0, 400, 0, MARIO_RED)
    for i in range(8):
        a = i * math.pi / 4
        m.add_cube(96, 8, 96, math.cos(a) * 380, 192, math.sin(a) * 380, RR_CLOUD)
    stars = [Star(0, 420, 0, 0)]
    coins = [Coin(math.cos(i * math.pi / 4) * 380, 204, math.sin(i * math.pi / 4) * 380)
             for i in range(8)]
    enemies = []
    cap_switches = [CapSwitch(0, 380, 0, CAP_WING)]
    return m, stars, coins, [], [], (0, 20, 200), enemies, [], [], [], [], []


# ======= BOWSER STAGES =======

def build_bowser_dark_world():
    m = Mesh()
    m.add_cube(200, 16, 200, 0, -5, 0, BDW_STONE)
    path = [(200,0),(400,40),(600,80),(600,160),(400,240),(200,240),
            (0,320),(200,400),(400,400),(600,480),(800,480),(1000,400)]
    for px, pz in path:
        m.add_cube(112, 16, 112, px, 8, pz, (120,72,56))
    for fx, fz in [(400,40),(600,160),(200,240)]:
        m.add_cube(8, 8, 72, fx, 28, fz, ORANGE)
    # Bowser arena
    m.add_cube(400, 16, 400, 1000, 8, 400, BDW_STONE)
    m.add_cube(56, 72, 56, 1000, 52, 400, DARK_GREEN)
    m.add_cube(36, 36, 36, 1000, 108, 400, (0,128,0))
    m.add_cube(16, 16, 8, 1000, 124, 372, RED)
    for i in range(8):
        a = i * math.pi / 4
        bx = 1000 + math.cos(a) * 172; bz = 400 + math.sin(a) * 172
        m.add_cube(16, 16, 16, bx, 24, bz, BLACK)
    stars = [Star(1000, 112, 400, 0)]
    enemies = [
        Enemy(400, 16, 40, ENEMY_GOOMBA, 60),
        Enemy(600, 16, 160, ENEMY_GOOMBA, 80),
        Enemy(200, 16, 240, ENEMY_BOBOMB, 60),
        Enemy(800, 16, 400, ENEMY_GOOMBA, 40),
    ]
    bowser = BowserBoss(1000, 16, 400, 180, 1)
    return m, stars, [], [], [], (0, 20, 0), enemies, [], [], [], [], []

def build_bowser_fire_sea():
    m = Mesh()
    for x in range(-6, 6):
        for z in range(-6, 6):
            c = LLL_LAVA_1 if (x+z) % 2 == 0 else LLL_LAVA_2
            m.add_cube(200, 6, 200, x * 200, -3, z * 200, c)
    m.add_cube(200, 16, 200, 0, 8, 0, BFS_METAL)
    pp = [(0,0),(140,200),(280,400),(140,600),(0,800),
          (-200,1000),(-400,1000),(-400,800),(-200,600),(0,400)]
    for i, (px, pz) in enumerate(pp):
        m.add_cube(96, 16, 96, px, 8 + i * 4, pz, BFS_METAL)
    m.add_cube(200, 6, 36, 200, 16, 200, (120,72,40))
    m.add_cube(200, 6, 36, -200, 16, 800, (120,72,40))
    m.add_cube(8, 192, 8, -400, 96, 1000, BFS_METAL)
    # Bowser arena
    m.add_cube(480, 16, 480, 0, 52, 1200, BDW_STONE)
    m.add_cube(72, 96, 72, 0, 100, 1200, DARK_GREEN)
    m.add_cube(48, 48, 48, 0, 168, 1200, (0,128,0))
    m.add_cube(24, 16, 8, 0, 184, 1160, RED)
    m.add_cube(84, 24, 84, 0, 68, 1200, (120,72,40))
    stars = [Star(0, 168, 1200, 0)]
    enemies = [
        Enemy(140, 16, 200, ENEMY_GOOMBA, 60),
        Enemy(-200, 16, 800, ENEMY_BOBOMB, 80),
        Enemy(-400, 16, 1000, ENEMY_HEAVE_HO, 60),
    ]
    bowser = BowserBoss(0, 60, 1200, 220, 2)
    damage_zones = [DamageZone(0, 0, 1200, 1200, -20, 8, ZONE_LAVA, 3, 25)]
    return m, stars, [], [], [], (0, 30, 0), enemies, [], [], damage_zones, [], []

def build_bowser_sky():
    m = Mesh()
    m.add_cube(200, 16, 200, 0, -5, 0, BITS_STONE)
    sp = []
    for i in range(25):
        a = i * 0.24; r = 200 + i * 18
        px = math.cos(a) * r; pz = math.sin(a) * r; py = i * 36
        sp.append((px, py, pz))
        c = [BITS_STONE,(112,72,56),DARK_GREY,BFS_METAL][i % 4]
        m.add_cube(96, 12, 96, px, py, pz, c)
    for i in range(0, 25, 3):
        px, py, pz = sp[i]
        m.add_cube(8, 8, 56, px + 36, py + 16, pz, ORANGE)
    last = sp[-1]; ax, ay, az = last[0], last[1] + 36, last[2]
    # Final Bowser arena
    m.add_cube(560, 16, 560, ax, ay, az, BITS_STONE)
    for i in range(12):
        a = i * math.pi / 6
        bx = ax + math.cos(a) * 260; bz = az + math.sin(a) * 260
        m.add_cube(16, 16, 16, bx, ay + 16, bz, BLACK)
    m.add_cube(96, 112, 96, ax, ay + 72, az, DARK_GREEN)
    m.add_cube(56, 56, 56, ax, ay + 168, az, (0,128,0))
    m.add_cube(36, 24, 8, ax, ay + 188, az - 44, RED)
    for sx, sz in [(-28,0),(28,0),(0,-28),(0,28)]:
        m.add_cube(12, 20, 12, ax + sx, ay + 120, az + sz, (120,72,40))
    stars = [Star(ax, ay + 208, az, 0)]
    enemies = [
        Enemy(200, 36, 200, ENEMY_GOOMBA, 40),
        Enemy(300, 72, 300, ENEMY_BOBOMB, 60),
        Enemy(400, 108, 100, ENEMY_AMP, 40),
    ]
    bowser = BowserBoss(last[0], last[1]+52, last[2], 260, 3)
    return m, stars, [], [], [], (0, 20, 0), enemies, [], [], [], [], []


# ======================================================================
#  LEVEL REGISTRY  (FIX #14: star total calculated from actual data)
# ======================================================================
LEVELS = {
    "castle_grounds":  {"name":"Castle Grounds",            "builder":build_castle_grounds,        "req":0},
    "castle_f1":       {"name":"Castle Interior F1",        "builder":build_castle_interior_f1,    "req":0},
    "castle_basement": {"name":"Castle Basement",           "builder":build_castle_basement,       "req":8},
    "castle_upper":    {"name":"Castle Upper Floor",        "builder":build_castle_upper,          "req":30},
    "castle_top":      {"name":"Castle Top / Wing Cap",     "builder":build_castle_top,            "req":50},
    "c01_bob":         {"name":"Bob-omb Battlefield",       "builder":build_bob_omb_battlefield,   "req":0},
    "c02_whomp":       {"name":"Whomp's Fortress",          "builder":build_whomps_fortress,       "req":1},
    "c03_jolly":       {"name":"Jolly Roger Bay",           "builder":build_jolly_roger_bay,       "req":3},
    "c04_cool":        {"name":"Cool, Cool Mountain",       "builder":build_cool_cool_mountain,    "req":3},
    "c05_boo":         {"name":"Big Boo's Haunt",           "builder":build_big_boos_haunt,        "req":12},
    "c06_hazy":        {"name":"Hazy Maze Cave",            "builder":build_hazy_maze_cave,        "req":8},
    "c07_lava":        {"name":"Lethal Lava Land",          "builder":build_lethal_lava_land,      "req":8},
    "c08_sand":        {"name":"Shifting Sand Land",        "builder":build_shifting_sand_land,    "req":8},
    "c09_dock":        {"name":"Dire, Dire Docks",          "builder":build_dire_dire_docks,       "req":30},
    "c10_snow":        {"name":"Snowman's Land",            "builder":build_snowmans_land,         "req":30},
    "c11_wet":         {"name":"Wet-Dry World",             "builder":build_wet_dry_world,         "req":30},
    "c12_tall":        {"name":"Tall, Tall Mountain",       "builder":build_tall_tall_mountain,    "req":30},
    "c13_tiny":        {"name":"Tiny-Huge Island",          "builder":build_tiny_huge_island,      "req":30},
    "c14_clock":       {"name":"Tick Tock Clock",           "builder":build_tick_tock_clock,       "req":50},
    "c15_rainbow":     {"name":"Rainbow Ride",              "builder":build_rainbow_ride,          "req":50},
    "s_slide":         {"name":"Princess's Secret Slide",   "builder":build_princess_secret_slide, "req":1},
    "s_wing":          {"name":"Wing Mario Over Rainbow",   "builder":build_wing_mario_rainbow,    "req":10},
    "s_metal":         {"name":"Metal Cap Cavern",          "builder":build_metal_cap_cavern,      "req":8},
    "s_vanish":        {"name":"Vanish Cap Moat",           "builder":build_vanish_cap,            "req":8},
    "s_tower":         {"name":"Tower of Wing Cap",         "builder":build_tower_wing_cap,        "req":10},
    "b1_dark":         {"name":"Bowser in the Dark World",  "builder":build_bowser_dark_world,     "req":8},
    "b2_fire":         {"name":"Bowser in the Fire Sea",    "builder":build_bowser_fire_sea,       "req":30},
    "b3_sky":          {"name":"Bowser in the Sky",         "builder":build_bowser_sky,            "req":70},
}

CASTLE_F1_PAINTINGS = [
    {"pos":(-978,140,-300),"level":"c01_bob"},
    {"pos":(-978,140,-500),"level":"c02_whomp"},
    {"pos":(-978,140,-700),"level":"c03_jolly"},
    {"pos":(978,140,-300),"level":"c04_cool"},
    {"pos":(978,140,-500),"level":"c05_boo"},
]
BASEMENT_PAINTINGS = [
    {"pos":(-1178,100,-400),"level":"c06_hazy"},
    {"pos":(-1178,100,-600),"level":"c07_lava"},
    {"pos":(-1178,100,-800),"level":"c08_sand"},
    {"pos":(1178,100,-400),"level":"c09_dock"},
]
UPPER_PAINTINGS = [
    {"pos":(-778,100,-300),"level":"c10_snow"},
    {"pos":(-778,100,-500),"level":"c11_wet"},
    {"pos":(778,100,-300),"level":"c12_tall"},
    {"pos":(778,100,-500),"level":"c13_tiny"},
    {"pos":(0,60,-778),"level":"c14_clock"},
    {"pos":(0,75,-790),"level":"c15_rainbow"},
]


# ======================================================================
#  SAVE SYSTEM  (FIX #49: basic save/load)
# ======================================================================
SAVE_FILE = os.path.join(os.path.expanduser("~"), ".koopa_engine_save.json")

def save_game(collected_stars: set, total_coins: int, lives: int):
    try:
        data = {"stars": list(collected_stars), "coins": total_coins, "lives": lives}
        with open(SAVE_FILE, 'w') as f:
            json.dump(data, f)
    except Exception:
        pass

def load_game() -> tuple:
    try:
        with open(SAVE_FILE, 'r') as f:
            data = json.load(f)
        return set(data.get("stars", [])), data.get("coins", 0), data.get("lives", 4)
    except Exception:
        return set(), 0, 4


# ======================================================================
#  ACHIEVEMENT SYSTEM — SM64 PC Port milestones
# ======================================================================
ACHIEVEMENTS = {
    "first_star":       {"name": "Power Star!",           "desc": "Collect your first Power Star",          "req": lambda s, c, e: len(s) >= 1},
    "five_stars":       {"name": "Star Collector",        "desc": "Collect 5 Power Stars",                  "req": lambda s, c, e: len(s) >= 5},
    "ten_stars":        {"name": "Star Hunter",           "desc": "Collect 10 Power Stars",                 "req": lambda s, c, e: len(s) >= 10},
    "twenty_stars":     {"name": "Star Master",           "desc": "Collect 20 Power Stars",                 "req": lambda s, c, e: len(s) >= 20},
    "thirty_stars":     {"name": "Star Legend",           "desc": "Collect 30 Power Stars",                 "req": lambda s, c, e: len(s) >= 30},
    "fifty_stars":      {"name": "Star Champion",         "desc": "Collect 50 Power Stars",                 "req": lambda s, c, e: len(s) >= 50},
    "all_stars":        {"name": "Super Star!",           "desc": "Collect all Power Stars",                "req": lambda s, c, e: len(s) >= 56},
    "first_coin":       {"name": "Cha-Ching!",            "desc": "Collect your first coin",                "req": lambda s, c, e: c >= 1},
    "fifty_coins":      {"name": "Coin Hoarder",          "desc": "Collect 50 coins",                       "req": lambda s, c, e: c >= 50},
    "hundred_coins":    {"name": "Rich Plumber",          "desc": "Collect 100 coins",                      "req": lambda s, c, e: c >= 100},
    "five_hundred":     {"name": "Coin Mogul",            "desc": "Collect 500 coins",                      "req": lambda s, c, e: c >= 500},
    "thousand_coins":   {"name": "Golden Plumber",        "desc": "Collect 1000 coins",                     "req": lambda s, c, e: c >= 1000},
    "first_enemy":      {"name": "Goomba Stomper",        "desc": "Defeat your first enemy",                "req": lambda s, c, e: e >= 1},
    "ten_enemies":      {"name": "Enemy Crusher",         "desc": "Defeat 10 enemies",                      "req": lambda s, c, e: e >= 10},
    "fifty_enemies":    {"name": "Exterminator",          "desc": "Defeat 50 enemies",                      "req": lambda s, c, e: e >= 50},
    "hundred_enemies":  {"name": "Unstoppable",           "desc": "Defeat 100 enemies",                     "req": lambda s, c, e: e >= 100},
    "bob_complete":     {"name": "Battlefield Victor",    "desc": "Get all Bob-omb Battlefield stars",       "req": lambda s, c, e: all(f"c01_bob_{i}" in s for i in range(5))},
    "whomp_complete":   {"name": "Fortress Conqueror",    "desc": "Get all Whomp's Fortress stars",          "req": lambda s, c, e: all(f"c02_whomp_{i}" in s for i in range(3))},
    "basement_unlock":  {"name": "Basement Access",       "desc": "Unlock the castle basement",              "req": lambda s, c, e: len(s) >= 8},
    "upper_unlock":     {"name": "Upper Floor",           "desc": "Unlock the upper castle floor",           "req": lambda s, c, e: len(s) >= 30},
    "top_unlock":       {"name": "Castle Peak",           "desc": "Reach the castle rooftop",                "req": lambda s, c, e: len(s) >= 50},
    "bowser1":          {"name": "Dark World Clear",      "desc": "Clear Bowser in the Dark World",          "req": lambda s, c, e: "b1_dark_0" in s},
    "bowser2":          {"name": "Fire Sea Clear",        "desc": "Clear Bowser in the Fire Sea",            "req": lambda s, c, e: "b2_fire_0" in s},
    "bowser3":          {"name": "Sky Conqueror",         "desc": "Clear Bowser in the Sky",                 "req": lambda s, c, e: "b3_sky_0" in s},
}


class AchievementTracker:
    """Tracks and displays achievement unlocks."""
    def __init__(self):
        self.unlocked: set[str] = set()
        self.display_queue: list[tuple[str, str]] = []
        self.display_timer: int = 0
        self.current_display: tuple[str, str] | None = None
        self.enemies_defeated: int = 0

    def check(self, collected_stars: set, total_coins: int):
        """Check all achievements and queue new unlocks."""
        for aid, ach in ACHIEVEMENTS.items():
            if aid not in self.unlocked:
                if ach["req"](collected_stars, total_coins, self.enemies_defeated):
                    self.unlocked.add(aid)
                    self.display_queue.append((ach["name"], ach["desc"]))
                    SFXSynth.play("star")

    def enemy_killed(self):
        self.enemies_defeated += 1

    def update(self):
        if self.display_timer > 0:
            self.display_timer -= 1
        elif self.display_queue:
            self.current_display = self.display_queue.pop(0)
            self.display_timer = 180  # 3 seconds

    def draw(self, screen, font_name, font_desc):
        if self.current_display and self.display_timer > 0:
            alpha = min(255, self.display_timer * 4)
            box = pygame.Surface((320, 56), pygame.SRCALPHA)
            box.fill((0, 0, 0, min(200, alpha)))
            screen.blit(box, (WIDTH // 2 - 160, 60))
            pygame.draw.rect(screen, STAR_GOLD, (WIDTH // 2 - 160, 60, 320, 56), 2)
            # Achievement icon
            pygame.draw.polygon(screen, STAR_GOLD,
                [(WIDTH // 2 - 140, 88), (WIDTH // 2 - 135, 78),
                 (WIDTH // 2 - 130, 88), (WIDTH // 2 - 136, 82),
                 (WIDTH // 2 - 144, 82)])
            name, desc = self.current_display
            n_surf = font_name.render(f"ACHIEVEMENT: {name}", True, STAR_GOLD)
            d_surf = font_desc.render(desc, True, WHITE)
            screen.blit(n_surf, (WIDTH // 2 - 120, 66))
            screen.blit(d_surf, (WIDTH // 2 - 120, 88))

    def save_data(self) -> dict:
        return {"unlocked": list(self.unlocked), "enemies": self.enemies_defeated}

    def load_data(self, data: dict):
        self.unlocked = set(data.get("unlocked", []))
        self.enemies_defeated = data.get("enemies", 0)


# ======================================================================
#  CAMERA SYSTEM — SM64 PC Port camera modes (FIX #33 expanded)
# ======================================================================
class CameraController:
    """Full SM64-style camera with multiple modes."""
    MODE_FIRST_PERSON = 0
    MODE_LAKITU       = 1
    MODE_FIXED        = 2
    MODE_CLOSE        = 3

    def __init__(self):
        self.mode = self.MODE_FIRST_PERSON
        self.x: float = 0; self.y: float = 0; self.z: float = 0
        self.yaw: float = math.pi
        self.pitch: float = 0
        self.target_x: float = 0; self.target_y: float = 0; self.target_z: float = 0
        self.orbit_dist: float = 200
        self.orbit_height: float = 80
        self.lerp_speed: float = CAM_LERP
        self.head_bob_phase: float = 0
        self.shake_timer: int = 0
        self.shake_intensity: float = 0

    def cycle_mode(self):
        self.mode = (self.mode + 1) % 4
        SFXSynth.play("pause")

    def shake(self, intensity: float = 3, duration: int = 15):
        self.shake_intensity = intensity
        self.shake_timer = duration

    def update(self, mario_x: float, mario_y: float, mario_z: float,
               speed: float, on_ground: bool, is_dead: bool):
        """Update camera based on current mode."""
        if self.mode == self.MODE_FIRST_PERSON:
            # Head bob
            if speed > 1.0 and on_ground and not is_dead:
                self.head_bob_phase += speed * 0.15
                bob = math.sin(self.head_bob_phase) * HEAD_BOB_AMT * min(1.0, speed / 8.0)
            else:
                bob = 0
                self.head_bob_phase *= 0.8
            self.target_x = mario_x
            self.target_y = mario_y + EYE_HEIGHT + bob
            self.target_z = mario_z

        elif self.mode == self.MODE_LAKITU:
            # Third-person behind Mario
            cam_behind_x = mario_x + math.sin(self.yaw) * self.orbit_dist
            cam_behind_z = mario_z + math.cos(self.yaw) * self.orbit_dist
            self.target_x = cam_behind_x
            self.target_y = mario_y + self.orbit_height
            self.target_z = cam_behind_z

        elif self.mode == self.MODE_CLOSE:
            # Close third-person
            close_dist = 100
            cam_behind_x = mario_x + math.sin(self.yaw) * close_dist
            cam_behind_z = mario_z + math.cos(self.yaw) * close_dist
            self.target_x = cam_behind_x
            self.target_y = mario_y + 50
            self.target_z = cam_behind_z

        elif self.mode == self.MODE_FIXED:
            # Fixed overhead
            self.target_x = mario_x
            self.target_y = mario_y + 400
            self.target_z = mario_z + 200
            self.pitch = -0.8

        # Lerp to target
        self.x += (self.target_x - self.x) * self.lerp_speed
        self.y += (self.target_y - self.y) * self.lerp_speed
        self.z += (self.target_z - self.z) * self.lerp_speed

        # Camera shake
        if self.shake_timer > 0:
            self.shake_timer -= 1
            shake_x = random.uniform(-self.shake_intensity, self.shake_intensity)
            shake_y = random.uniform(-self.shake_intensity, self.shake_intensity)
            self.x += shake_x; self.y += shake_y

    def handle_mouse(self, dx: int, dy: int):
        self.yaw += dx * MOUSE_SENS_X
        self.pitch -= dy * MOUSE_SENS_Y
        self.pitch = max(PITCH_MIN, min(PITCH_MAX, self.pitch))

    def handle_keys(self, keys):
        if keys[pygame.K_LEFT]:   self.yaw -= KEY_TURN
        if keys[pygame.K_RIGHT]:  self.yaw += KEY_TURN
        if keys[pygame.K_UP]:     self.pitch = min(PITCH_MAX, self.pitch + KEY_TURN * 0.7)
        if keys[pygame.K_DOWN]:   self.pitch = max(PITCH_MIN, self.pitch - KEY_TURN * 0.7)


# ======================================================================
#  LEVEL DETAIL HELPERS — Extra geometry builders for richness
# ======================================================================
def add_fence_line(mesh: Mesh, x1, z1, x2, z2, y, height, color):
    """Add a fence between two points."""
    dx = x2 - x1; dz = z2 - z1
    length = math.sqrt(dx * dx + dz * dz)
    if length < 1:
        return
    segments = max(1, int(length / 60))
    for i in range(segments):
        t = i / segments
        px = x1 + dx * t + dx / segments * 0.5
        pz = z1 + dz * t + dz / segments * 0.5
        mesh.add_cube(4, height, 4, px, y + height / 2, pz, color)
    # Horizontal rail
    angle = math.atan2(dz, dx)
    mid_x = (x1 + x2) / 2; mid_z = (z1 + z2) / 2
    mesh.add_cube(length, 4, 4, mid_x, y + height, mid_z, color)


def add_tree(mesh: Mesh, x, y, z, trunk_h=80, crown_r=56, trunk_c=None, crown_c=None, crown_c2=None):
    """Add a tree with trunk and hill-shaped crown."""
    if trunk_c is None: trunk_c = CG_TREE_TRUNK
    if crown_c is None: crown_c = CG_TREE_TOP
    if crown_c2 is None: crown_c2 = CG_TREE_TOP2
    mesh.add_cube(24, trunk_h, 24, x, y + trunk_h / 2, z, trunk_c)
    mesh.add_hill(crown_r, crown_r * 0.7, x, y + trunk_h, z, crown_c, crown_c2, 6)


def add_torch(mesh: Mesh, x, y, z, height=48, base_color=None, flame_color=None):
    """Add a wall torch."""
    if base_color is None: base_color = DARK_GREY
    if flame_color is None: flame_color = ORANGE
    mesh.add_cube(6, height, 6, x, y + height / 2, z, base_color)
    mesh.add_cube(10, 8, 10, x, y + height + 4, z, flame_color)
    mesh.add_cube(6, 4, 6, x, y + height + 10, z, YELLOW)


def add_arch(mesh: Mesh, x, y, z, width, height, depth, color):
    """Add a decorative arch."""
    hw = width / 2
    mesh.add_cube(depth, height, depth, x - hw, y + height / 2, z, color)
    mesh.add_cube(depth, height, depth, x + hw, y + height / 2, z, color)
    mesh.add_cube(width + depth, depth, depth, x, y + height, z, color)


def add_pillar(mesh: Mesh, x, y, z, radius, height, color, cap_color=None):
    """Add a decorative pillar with cap."""
    if cap_color is None: cap_color = color
    mesh.add_cube(radius * 2, height, radius * 2, x, y + height / 2, z, color)
    mesh.add_cube(radius * 2.4, height * 0.06, radius * 2.4, x, y + height, z, cap_color)
    mesh.add_cube(radius * 2.4, height * 0.06, radius * 2.4, x, y, z, cap_color)


def add_bridge_segment(mesh: Mesh, x, y, z, length, width, color, rail_color=None):
    """Add a bridge section with railings."""
    if rail_color is None: rail_color = color
    mesh.add_cube(width, 8, length, x, y, z, color)
    for side in [-1, 1]:
        hw = width / 2 + 4
        for i in range(max(1, int(length / 80))):
            pz = z - length / 2 + i * 80 + 40
            mesh.add_cube(4, 32, 4, x + side * hw, y + 20, pz, rail_color)
        mesh.add_cube(4, 4, length, x + side * hw, y + 36, z, rail_color)


def add_staircase(mesh: Mesh, x, y, z, steps, step_w, step_h, step_d, color, direction=1):
    """Add a staircase going up in the Z direction."""
    for i in range(steps):
        mesh.add_cube(step_w, step_h, step_d, x, y + i * step_h + step_h / 2,
                      z + direction * i * step_d, color)


def add_lamp_post(mesh: Mesh, x, y, z, height=100, color=None, light_color=None):
    """Add a street lamp."""
    if color is None: color = DARK_GREY
    if light_color is None: light_color = YELLOW
    mesh.add_cube(8, height, 8, x, y + height / 2, z, color)
    mesh.add_cube(24, 4, 24, x, y + height, z, color)
    mesh.add_cube(16, 8, 16, x, y + height + 6, z, light_color)


def add_rock_cluster(mesh: Mesh, x, y, z, count=4, spread=40, color=None):
    """Add a cluster of small rocks."""
    if color is None: color = DARK_STONE
    for _ in range(count):
        rx = x + random.uniform(-spread, spread)
        rz = z + random.uniform(-spread, spread)
        size = random.uniform(8, 20)
        mesh.add_cube(size, size * 0.7, size, rx, y + size * 0.35, rz, color)


def add_flower_patch(mesh: Mesh, x, y, z, count=6, spread=30, colors=None):
    """Add decorative flowers."""
    if colors is None: colors = [(255,80,80), (255,200,80), (200,80,255), (80,200,255)]
    for _ in range(count):
        fx = x + random.uniform(-spread, spread)
        fz = z + random.uniform(-spread, spread)
        stem_h = random.uniform(8, 16)
        mesh.add_cube(2, stem_h, 2, fx, y + stem_h / 2, fz, (0, 140, 0))
        mesh.add_cube(6, 4, 6, fx, y + stem_h + 2, fz, random.choice(colors))


def add_mushroom(mesh: Mesh, x, y, z, height=56, cap_r=52, stem_c=None, cap_c=None):
    """Add a decorative mushroom."""
    if stem_c is None: stem_c = TTM_MUSH_STEM
    if cap_c is None: cap_c = TTM_MUSH_TOP
    mesh.add_cube(16, height, 16, x, y + height / 2, z, stem_c)
    mesh.add_cube(cap_r, 12, cap_r, x, y + height, z, cap_c)


def add_crate(mesh: Mesh, x, y, z, size=24, color=None):
    """Add a breakable crate."""
    if color is None: color = (144, 96, 48)
    mesh.add_cube(size, size, size, x, y + size / 2, z, color)
    mesh.add_cube(size + 4, 2, size + 4, x, y + size, z, (120, 80, 40))
    mesh.add_cube(4, 4, 4, x, y + size / 2, z + size / 2 + 1, DARK_GREY)


def add_coin_ring(coins: list, x, y, z, radius, count=8):
    """Add a ring of coins."""
    for i in range(count):
        angle = i * 2 * math.pi / count
        cx = x + math.cos(angle) * radius
        cz = z + math.sin(angle) * radius
        coins.append(Coin(cx, y, cz))


def add_coin_line(coins: list, x1, y, z1, x2, z2, count=5):
    """Add a line of coins between two points."""
    for i in range(count):
        t = i / max(1, count - 1)
        cx = x1 + (x2 - x1) * t
        cz = z1 + (z2 - z1) * t
        coins.append(Coin(cx, y, cz))


def add_coin_arc(coins: list, x, y, z, radius, start_angle, end_angle, count=6):
    """Add an arc of coins."""
    for i in range(count):
        t = i / max(1, count - 1)
        angle = start_angle + (end_angle - start_angle) * t
        cx = x + math.cos(angle) * radius
        cz = z + math.sin(angle) * radius
        coins.append(Coin(cx, y, cz))


# ======================================================================
#  RENDERER  (FIX #4: backface culling, FIX #9: scanlines, FIX #35: clipping)
# ======================================================================
def render_mesh(screen, mesh, cam_x, cam_y, cam_z, cam_yaw, cam_pitch, cx, cy, is_menu=False):
    render_list = []
    c_cos = math.cos(-cam_yaw); c_sin = math.sin(-cam_yaw)
    p_cos = math.cos(-cam_pitch); p_sin = math.sin(-cam_pitch)
    m_cos = math.cos(mesh.yaw); m_sin = math.sin(mesh.yaw)
    menu_tilt = 0.2
    wiggle = math.sin(pygame.time.get_ticks() / 500.0) * 10 if is_menu else 0

    for face in mesh.faces:
        transformed = []
        avg_z = 0
        valid = True
        behind_count = 0

        for i in face.indices:
            v = mesh.vertices[i]
            rx = v.x * m_cos - v.z * m_sin
            rz = v.x * m_sin + v.z * m_cos
            ry = v.y

            if is_menu:
                ry_t = ry * math.cos(menu_tilt) - rz * math.sin(menu_tilt)
                rz = ry * math.sin(menu_tilt) + rz * math.cos(menu_tilt)
                ry = ry_t + wiggle

            wx = rx + mesh.x; wy = ry + mesh.y; wz = rz + mesh.z
            dcx = wx - cam_x; dcy = wy - cam_y; dcz = wz - cam_z

            if not is_menu:
                xx = dcx * c_cos - dcz * c_sin
                zz = dcx * c_sin + dcz * c_cos
                yy = dcy
                yy2 = yy * p_cos - zz * p_sin
                zz2 = yy * p_sin + zz * p_cos
                xx, yy, zz = xx, yy2, zz2
            else:
                xx = dcx; yy = dcy; zz = dcz

            if zz < NEAR_CLIP:  # FIX #35: use near clip constant
                behind_count += 1
            transformed.append((xx, yy, zz))
            avg_z += zz

        # FIX #35: skip if all vertices behind camera
        if behind_count == len(transformed):
            continue
        # Skip if any vertex behind (simple clip — avoids partial-behind artifacts)
        if behind_count > 0:
            continue

        screen_points = []
        for xx, yy, zz in transformed:
            s = FOV / max(zz, NEAR_CLIP)
            screen_points.append((int(xx * s + cx), int(-yy * s + cy)))

        if len(screen_points) >= 3:
            # FIX #4: consistent backface culling using signed area
            area = 0
            for i in range(len(screen_points)):
                j = (i + 1) % len(screen_points)
                area += (screen_points[j][0] - screen_points[i][0]) * \
                        (screen_points[j][1] + screen_points[i][1])
            if area < 0:  # FIX #4: reversed winding check — negative = front-facing
                render_list.append({
                    'poly': screen_points,
                    'depth': avg_z / len(transformed),
                    'color': face.color
                })

    return render_list


# ======================================================================
#  MENU HEAD  (SM64 Mario head)
# ======================================================================
def create_menu_head():
    m = Mesh()
    m.add_cube(40, 36, 40, 0, 0, 0, SKIN)
    m.add_cube(44, 12, 44, 0, 20, 0, MARIO_RED)
    m.add_cube(52, 4, 52, 0, 15, 10, MARIO_RED)
    m.add_cube(10, 10, 10, 0, -2, 22, SKIN)
    m.add_cube(24, 6, 4, 0, -10, 21, MUSTACHE_BLACK)
    m.add_cube(10, 12, 2, -12, 6, 20, WHITE)
    m.add_cube(10, 12, 2, 12, 6, 20, WHITE)
    m.add_cube(4, 6, 3, -12, 6, 21, EYE_BLUE)
    m.add_cube(4, 6, 3, 12, 6, 21, EYE_BLUE)
    m.add_cube(42, 24, 10, 0, 0, -18, MARIO_BLUE)
    return m


# ======================================================================
#  TRANSITION SYSTEM  (FIX #29: fade in/out for doors/paintings)
# ======================================================================
class Transition:
    def __init__(self):
        self.active = False
        self.alpha = 0
        self.phase = 0  # 0=fade out, 1=fade in
        self.speed = 12
        self.target_level = None
        self.callback = None

    def start(self, target_level: str, callback=None):
        self.active = True
        self.phase = 0
        self.alpha = 0
        self.target_level = target_level
        self.callback = callback

    def update(self) -> bool:
        """Returns True when transition is complete."""
        if not self.active:
            return False
        if self.phase == 0:
            self.alpha = min(255, self.alpha + self.speed)
            if self.alpha >= 255:
                self.phase = 1
                if self.callback:
                    self.callback(self.target_level)
                return False
        else:
            self.alpha = max(0, self.alpha - self.speed)
            if self.alpha <= 0:
                self.active = False
                return True
        return False

    def draw(self, screen):
        if self.active and self.alpha > 0:
            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.set_alpha(self.alpha)
            overlay.fill(BLACK)
            screen.blit(overlay, (0, 0))


# ======================================================================
#  HEALTH PIE  (FIX #26: SM64-style pie meter instead of bars)
# ======================================================================
def draw_health_pie(screen, x, y, health, max_health, radius=22):
    """Draw SM64-style circular health meter."""
    # Background circle
    pygame.draw.circle(screen, HEALTH_PIE_BG, (x, y), radius + 2)
    pygame.draw.circle(screen, (20, 20, 20), (x, y), radius)

    if health <= 0:
        return

    # Filled wedges
    segments = max_health
    angle_per = 2 * math.pi / segments
    color = HEALTH_PIE_FG if health > 2 else HEALTH_PIE_LOW

    for i in range(health):
        start_angle = -math.pi / 2 + i * angle_per
        end_angle = start_angle + angle_per
        points = [(x, y)]
        steps = 6
        for s in range(steps + 1):
            a = start_angle + (end_angle - start_angle) * s / steps
            points.append((x + math.cos(a) * radius, y + math.sin(a) * radius))
        if len(points) >= 3:
            pygame.draw.polygon(screen, color, points)

    # Border
    pygame.draw.circle(screen, WHITE, (x, y), radius + 2, 2)
    # Segment lines
    for i in range(segments):
        a = -math.pi / 2 + i * angle_per
        ex = x + math.cos(a) * (radius + 1)
        ey = y + math.sin(a) * (radius + 1)
        pygame.draw.line(screen, (40, 40, 40), (x, y), (int(ex), int(ey)), 1)


# ======================================================================
#  MAIN LOOP
# ======================================================================
def main():
    pygame.init()
    pygame.mixer.init(22050, -16, 1, 512)
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("SUPER MARIO 64 — KOOPA ENGINE 0.3  |  A.C Holdings / Team Flames")
    clock = pygame.time.Clock()

    # FIX #9: pre-render scanline overlay instead of per-frame line draws
    scanline_overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    for y in range(0, HEIGHT, 4):
        pygame.draw.line(scanline_overlay, (0, 0, 0, 40), (0, y), (WIDTH, y), 1)

    # Sky gradient cache (FIX #9: pre-render sky gradients)
    sky_cache: dict[str, pygame.Surface] = {}

    def get_sky_surface(level_id: str) -> pygame.Surface:
        if level_id in sky_cache:
            return sky_cache[level_id]
        sky_info = SM64_SKIES.get(level_id, ((56,100,184),(192,220,255),(172,204,248)))
        top, bot, fog = sky_info
        surf = pygame.Surface((WIDTH, HEIGHT))
        for y_line in range(HEIGHT):
            t = y_line / HEIGHT
            r = int(top[0] * (1 - t) + bot[0] * t)
            g = int(top[1] * (1 - t) + bot[1] * t)
            b = int(top[2] * (1 - t) + bot[2] * t)
            pygame.draw.line(surf, (max(0,min(255,r)), max(0,min(255,g)), max(0,min(255,b))),
                           (0, y_line), (WIDTH, y_line))
        sky_cache[level_id] = surf
        return surf

    try:
        font_title = pygame.font.Font(None, 72)
        font_menu  = pygame.font.Font(None, 36)
        font_small = pygame.font.Font(None, 22)
        font_hud   = pygame.font.SysFont('Arial', 20, bold=True)
        font_big   = pygame.font.Font(None, 48)
    except Exception:
        font_title = pygame.font.SysFont('Arial', 54, bold=True)
        font_menu  = pygame.font.SysFont('Arial', 28, bold=True)
        font_small = pygame.font.SysFont('Arial', 16)
        font_hud = font_small
        font_big = font_menu

    STATE_MENU = 0; STATE_GAME = 1; STATE_LEVEL_SELECT = 2; STATE_PAUSE = 3
    current_state = STATE_MENU

    menu_head = create_menu_head()
    menu_items = ["PLAY GAME", "LEVEL SELECT", "HOW TO PLAY", "CREDITS", "EXIT GAME"]
    selected_index = 0
    active_overlay = None

    level_keys = list(LEVELS.keys())
    level_select_idx = 0

    mario: Mario | None = None
    current_level_mesh: Mesh | None = None
    current_level_stars: list[Star] = []
    current_level_coins: list[Coin] = []
    current_level_red_coins: list[RedCoin] = []
    current_level_oneups: list[OneUp] = []
    current_level_id: str | None = None
    current_level_enemies: list[Enemy] = []
    current_level_npcs: list[NPC] = []
    current_level_platforms: list[MovingPlatform] = []
    current_level_damage_zones: list[DamageZone] = []
    current_level_signs: list[Sign] = []
    current_level_cannons: list[Cannon] = []
    particles = ParticleSystem()
    minimap = Minimap()
    cam_x = cam_y = cam_z = 0.0
    cam_yaw = cam_pitch = 0.0
    vel_x = vel_z = 0.0
    head_bob_phase = 0.0
    mouse_captured = False
    cx, cy = WIDTH // 2, HEIGHT // 2
    cam_mode = CAM_MODE_FP

    # FIX #49: load saved progress
    collected_stars, total_coins, saved_lives = load_game()
    star_flash = 0; coin_flash = 0; level_name_timer = 0; level_display_name = ""

    # FIX #14: calculate actual star total
    star_total_actual = 0
    for lid, info in LEVELS.items():
        result = info["builder"]()
        if isinstance(result, tuple) and len(result) >= 2:
            star_total_actual += len(result[1])

    transition = Transition()

    def release_mouse():
        nonlocal mouse_captured
        pygame.mouse.set_visible(True)
        pygame.event.set_grab(False)
        mouse_captured = False

    def capture_mouse():
        nonlocal mouse_captured
        pygame.mouse.set_visible(False)
        pygame.event.set_grab(True)
        mouse_captured = True
        pygame.mouse.set_pos(cx, cy)

    def load_level(level_id: str):
        nonlocal mario, current_level_mesh, current_level_stars, current_level_coins
        nonlocal current_level_red_coins, current_level_oneups
        nonlocal current_level_enemies, current_level_npcs, current_level_platforms
        nonlocal current_level_damage_zones, current_level_signs, current_level_cannons
        nonlocal current_level_id, cam_x, cam_y, cam_z, cam_yaw, cam_pitch
        nonlocal vel_x, vel_z, head_bob_phase, level_name_timer, level_display_name

        info = LEVELS[level_id]
        current_level_id = level_id
        level_display_name = info["name"]
        level_name_timer = 180

        result = info["builder"]()
        # Unpack builder results — now returns up to 6 values
        current_level_mesh = result[0]
        current_level_stars = result[1] if len(result) > 1 else []
        current_level_coins = result[2] if len(result) > 2 else []
        current_level_red_coins = result[3] if len(result) > 3 else []
        current_level_oneups = result[4] if len(result) > 4 else []
        spawn = result[5] if len(result) > 5 else (0, 50, 400)  # FIX #16
        current_level_enemies = result[6] if len(result) > 6 else []
        current_level_npcs = result[7] if len(result) > 7 else []
        current_level_platforms = result[8] if len(result) > 8 else []
        current_level_damage_zones = result[9] if len(result) > 9 else []
        current_level_signs = result[10] if len(result) > 10 else []
        current_level_cannons = result[11] if len(result) > 11 else []
        particles.particles.clear()  # Reset particles on level load

        # Mark already-collected stars
        for star in current_level_stars:
            sid = f"{level_id}_{star.star_id}"
            if sid in collected_stars:
                star.collected = True

        mario = Mario(spawn[0], spawn[1], spawn[2])
        mario.lives = max(saved_lives, mario.lives)
        cam_yaw = math.pi
        cam_pitch = 0.0
        cam_x = mario.x; cam_y = mario.y + EYE_HEIGHT; cam_z = mario.z
        vel_x = vel_z = 0.0
        head_bob_phase = 0.0

        SFXSynth.play("enter")
        capture_mouse()

    def do_transition_load(target: str):
        """Called mid-transition to actually load the level."""
        load_level(target)

    def start_level_transition(target: str):
        """FIX #29: start a fade transition to a new level."""
        transition.start(target, do_transition_load)

    def draw_sky(level_id):
        sky_surf = get_sky_surface(level_id)
        screen.blit(sky_surf, (0, 0))
        sky_info = SM64_SKIES.get(level_id, ((56,100,184),(192,220,255),(172,204,248)))
        return sky_info[2]  # fog color

    def draw_hud():
        nonlocal star_flash, coin_flash
        bar = pygame.Surface((WIDTH, 50), pygame.SRCALPHA)
        bar.fill((0, 0, 0, 180))
        screen.blit(bar, (0, HEIGHT - 50))
        pygame.draw.line(screen, (80,80,80), (0, HEIGHT - 50), (WIDTH, HEIGHT - 50), 2)

        sc = STAR_GOLD if star_flash <= 0 else WHITE
        screen.blit(font_hud.render(f"★ {len(collected_stars)}/{star_total_actual}", True, sc),
                    (16, HEIGHT - 38))

        cc = COIN_YELLOW if coin_flash <= 0 else WHITE
        screen.blit(font_hud.render(f"● {total_coins}", True, cc), (140, HEIGHT - 38))

        # FIX #26: health pie instead of bars
        if mario:
            draw_health_pie(screen, WIDTH - 100, HEIGHT - 26, mario.health, mario.max_health, 18)
            screen.blit(font_hud.render(f"x{mario.lives}", True, WHITE), (WIDTH - 70, HEIGHT - 34))

        screen.blit(font_hud.render(f"FPS:{int(clock.get_fps())}", True, METAL_GREY),
                    (WIDTH - 180, HEIGHT - 38))

        # FIX #48: level name in HUD
        if current_level_id:
            n = font_small.render(LEVELS[current_level_id]["name"], True, WHITE)
            screen.blit(n, (WIDTH // 2 - n.get_width() // 2, HEIGHT - 38))

        # Action state indicator
        if mario and mario.action not in (ACT_IDLE, ACT_WALK):
            act_names = {
                ACT_JUMP: "JUMP", ACT_DOUBLE_JUMP: "DOUBLE JUMP",
                ACT_TRIPLE_JUMP: "TRIPLE JUMP!", ACT_FREEFALL: "FREEFALL",
                ACT_LONG_JUMP: "LONG JUMP", ACT_BACKFLIP: "BACKFLIP",
                ACT_GROUND_POUND: "GROUND POUND", ACT_GROUND_POUND_LAND: "POUND LAND",
                ACT_WALL_KICK: "WALL KICK", ACT_SIDE_FLIP: "SIDE FLIP",
                ACT_DIVE: "DIVE", ACT_SWIM: "SWIMMING", ACT_DEAD: "DEAD",
                ACT_STAR_GET: "STAR GET!", ACT_SLIDE: "SLIDING",
            }
            act_text = act_names.get(mario.action, "")
            if act_text:
                c = STAR_GOLD if mario.action == ACT_STAR_GET else WHITE
                at = font_small.render(act_text, True, c)
                screen.blit(at, (WIDTH // 2 - at.get_width() // 2, HEIGHT - 58))

        star_flash = max(0, star_flash - 1)
        coin_flash = max(0, coin_flash - 1)

    def draw_level_intro():
        nonlocal level_name_timer
        if level_name_timer > 0:
            a = min(255, level_name_timer * 3)
            ov = pygame.Surface((WIDTH, 72), pygame.SRCALPHA)
            ov.fill((0, 0, 0, a))
            screen.blit(ov, (0, HEIGHT // 2 - 36))
            t = font_big.render(level_display_name, True, STAR_GOLD)
            screen.blit(t, (WIDTH // 2 - t.get_width() // 2, HEIGHT // 2 - 18))
            level_name_timer -= 1

    def draw_crosshair():
        pygame.draw.line(screen, (255,255,255,160), (cx - 8, cy), (cx + 8, cy), 1)
        pygame.draw.line(screen, (255,255,255,160), (cx, cy - 8), (cx, cy + 8), 1)

    # Pre-init SFX
    SFXSynth.get("jump")

    running = True
    while running:
        clock.tick(FPS)
        time_sec = pygame.time.get_ticks() / 1000.0
        mouse_dx = mouse_dy = 0

        if mouse_captured:
            mx, my = pygame.mouse.get_pos()
            mouse_dx = mx - cx; mouse_dy = my - cy
            if abs(mouse_dx) > 0 or abs(mouse_dy) > 0:
                pygame.mouse.set_pos(cx, cy)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if transition.active:
                continue  # Block input during transitions

            if current_state == STATE_MENU:
                if event.type == pygame.KEYDOWN:
                    if active_overlay:
                        if event.key in (pygame.K_ESCAPE, pygame.K_b, pygame.K_RETURN):
                            active_overlay = None
                    else:
                        if event.key == pygame.K_UP:
                            selected_index = (selected_index - 1) % len(menu_items)
                            SFXSynth.play("menu_move")
                        elif event.key == pygame.K_DOWN:
                            selected_index = (selected_index + 1) % len(menu_items)
                            SFXSynth.play("menu_move")
                        elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                            ch = menu_items[selected_index]
                            if ch == "EXIT GAME":
                                running = False
                            elif ch == "PLAY GAME":
                                current_state = STATE_GAME
                                load_level("castle_grounds")
                            elif ch == "LEVEL SELECT":
                                current_state = STATE_LEVEL_SELECT
                                level_select_idx = 0
                            elif ch == "HOW TO PLAY":
                                active_overlay = "how"
                            elif ch == "CREDITS":
                                active_overlay = "credits"

            elif current_state == STATE_LEVEL_SELECT:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        current_state = STATE_MENU
                    elif event.key == pygame.K_UP:
                        level_select_idx = (level_select_idx - 1) % len(level_keys)
                        SFXSynth.play("menu_move")
                    elif event.key == pygame.K_DOWN:
                        level_select_idx = (level_select_idx + 1) % len(level_keys)
                        SFXSynth.play("menu_move")
                    elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        # FIX #15: respect star requirements
                        k = level_keys[level_select_idx]
                        req = LEVELS[k]["req"]
                        if len(collected_stars) >= req:
                            current_state = STATE_GAME
                            load_level(k)
                        else:
                            SFXSynth.play("hurt")  # Can't enter yet

            elif current_state == STATE_GAME:
                if event.type == pygame.KEYDOWN:
                    if mario and mario.action == ACT_DEAD:
                        continue  # Block input when dead

                    if event.key == pygame.K_ESCAPE:
                        current_state = STATE_PAUSE
                        release_mouse()
                        SFXSynth.play("pause")

                    elif event.key == pygame.K_SPACE:
                        if mario:
                            mario.start_jump()

                    elif event.key == pygame.K_z:
                        # FIX #21: Ground pound (Z in air)
                        if mario and not mario.on_ground:
                            mario.start_ground_pound()
                        # FIX #20: Backflip (Z + crouch on ground)
                        elif mario and mario.on_ground:
                            keys_held = pygame.key.get_pressed()
                            if keys_held[pygame.K_LCTRL] or keys_held[pygame.K_RCTRL]:
                                mario.start_backflip()
                            else:
                                mario.start_ground_pound()  # will be ignored if on ground

                    elif event.key == pygame.K_x:
                        # FIX #19: Long jump (X while moving + crouching)
                        if mario:
                            speed = math.sqrt(vel_x * vel_x + vel_z * vel_z)
                            if speed > 4 and mario.on_ground:
                                mario.start_long_jump(speed)
                            elif not mario.on_ground:
                                mario.start_dive(cam_yaw)

                    elif event.key == pygame.K_e:
                        # Check NPC interaction first
                        npc_talked = False
                        for npc in current_level_npcs:
                            if npc.can_talk(mario.x, mario.y, mario.z) and not npc.talking:
                                npc.start_talk()
                                npc_talked = True
                                SFXSynth.play("enter")
                                break
                        # Check sign interaction
                        if not npc_talked:
                            for sign in current_level_signs:
                                if sign.can_read(mario.x, mario.y, mario.z) and not sign.showing:
                                    sign.start_read()
                                    npc_talked = True
                                    SFXSynth.play("enter")
                                    break
                        # Check cannon interaction
                        if not npc_talked:
                            for cannon in current_level_cannons:
                                if cannon.can_enter(mario.x, mario.y, mario.z):
                                    vx, vy, vz = cannon.launch()
                                    mario.dy = vy
                                    mario.dx = vx
                                    mario.dz = vz
                                    mario.on_ground = False
                                    mario.action = ACT_FREEFALL
                                    mario.fall_start_y = mario.y
                                    SFXSynth.play("jump")
                                    npc_talked = True
                                    break
                        # FIX #29: use transitions for level changes
                        if not npc_talked and current_level_id == "castle_grounds":
                            if abs(mario.x) < 100 and mario.z < -900:
                                start_level_transition("castle_f1")
                        elif current_level_id == "castle_f1":
                            entered = False
                            for p in CASTLE_F1_PAINTINGS:
                                if abs(mario.x - p["pos"][0]) < 150 and \
                                   abs(mario.y - p["pos"][1]) < 200 and \
                                   abs(mario.z - p["pos"][2]) < 150:  # FIX #43: Y-check
                                    req = LEVELS[p["level"]]["req"]
                                    if len(collected_stars) >= req:
                                        start_level_transition(p["level"])
                                    else:
                                        SFXSynth.play("hurt")
                                    entered = True; break
                            if not entered:
                                if abs(mario.x - 600) < 100 and abs(mario.z - 600) < 100:
                                    if len(collected_stars) >= 8:
                                        start_level_transition("castle_basement")
                                elif abs(mario.x) < 200 and mario.z < -800:
                                    if len(collected_stars) >= 30:
                                        start_level_transition("castle_upper")
                                elif abs(mario.x) < 200 and mario.z > 800:
                                    start_level_transition("castle_grounds")
                                elif abs(mario.x) < 100 and abs(mario.z) < 100 and mario.y > 50:
                                    start_level_transition("s_slide")
                        elif current_level_id == "castle_basement":
                            entered = False
                            for p in BASEMENT_PAINTINGS:
                                if abs(mario.x - p["pos"][0]) < 150 and \
                                   abs(mario.y - p["pos"][1]) < 200 and \
                                   abs(mario.z - p["pos"][2]) < 150:
                                    req = LEVELS[p["level"]]["req"]
                                    if len(collected_stars) >= req:
                                        start_level_transition(p["level"])
                                    entered = True; break
                            if not entered:
                                if abs(mario.x - 800) < 100 and abs(mario.z - 800) < 100:
                                    start_level_transition("s_metal")  # FIX #44
                                elif abs(mario.x) < 200 and mario.z > 1000:
                                    start_level_transition("castle_f1")
                                elif abs(mario.x) < 100 and abs(mario.z + 600) < 100:
                                    start_level_transition("b1_dark")
                        elif current_level_id == "castle_upper":
                            entered = False
                            for p in UPPER_PAINTINGS:
                                if abs(mario.x - p["pos"][0]) < 150 and \
                                   abs(mario.y - p["pos"][1]) < 200 and \
                                   abs(mario.z - p["pos"][2]) < 150:
                                    req = LEVELS[p["level"]]["req"]
                                    if len(collected_stars) >= req:
                                        start_level_transition(p["level"])
                                    entered = True; break
                            if not entered:
                                if abs(mario.x) < 200 and mario.z < -600:
                                    if len(collected_stars) >= 50:
                                        start_level_transition("castle_top")
                                elif abs(mario.x) < 200 and mario.z > 600:
                                    start_level_transition("castle_f1")  # FIX #45
                                elif abs(mario.x - 600) < 200 and abs(mario.z) < 200:
                                    start_level_transition("b2_fire")
                        elif current_level_id == "castle_top":
                            if abs(mario.x) < 100 and abs(mario.z) < 100:  # FIX #32
                                start_level_transition("s_tower")
                            elif abs(mario.x) < 200 and mario.z > 300:
                                start_level_transition("castle_upper")
                            elif mario.y > 100 and len(collected_stars) >= 70:
                                start_level_transition("b3_sky")
                        else:
                            # Exit any course back to castle
                            start_level_transition("castle_f1")

                    elif event.key == pygame.K_TAB:
                        if mouse_captured:
                            release_mouse()
                        else:
                            capture_mouse()

                    elif event.key == pygame.K_c:
                        # FIX #33: toggle camera mode
                        cam_mode = 1 - cam_mode

            elif current_state == STATE_PAUSE:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        current_state = STATE_GAME
                        capture_mouse()
                        SFXSynth.play("pause")
                    elif event.key == pygame.K_q:
                        save_game(collected_stars, total_coins,
                                  mario.lives if mario else saved_lives)
                        current_state = STATE_MENU
                        release_mouse()
                    elif event.key == pygame.K_r:
                        if current_level_id:
                            load_level(current_level_id)
                            current_state = STATE_GAME

        # ============ UPDATE ============
        transition.update()

        # ============ RENDER ============

        if current_state == STATE_MENU:
            for y in range(HEIGHT):
                t = y / HEIGHT
                r = int(8 * (1 - t)); g = int(16 * (1 - t)); b = int(48 * (1 - t))
                pygame.draw.line(screen, (r, g, b), (0, y), (WIDTH, y))
            menu_head.yaw += 0.02
            # FIX #34: adjusted menu head distance
            polys = render_mesh(screen, menu_head, 0, 0, 160, 0, 0, cx, cy, is_menu=True)
            polys.sort(key=lambda x: x['depth'], reverse=True)
            for p in polys:
                pygame.draw.polygon(screen, p['color'], p['poly'])
                pygame.draw.polygon(screen, BLACK, p['poly'], 1)

            ly = 40 + math.sin(time_sec) * 5
            ts = font_title.render("SUPER MARIO 64", True, WHITE)
            th = font_title.render("SUPER MARIO 64", True, MARIO_RED)
            screen.blit(th, (WIDTH // 2 - ts.get_width() // 2 + 3, ly + 3))
            screen.blit(ts, (WIDTH // 2 - ts.get_width() // 2, ly))
            sub = font_small.render("KOOPA ENGINE 0.3  ·  A.C Holdings / Team Flames 1999-2026",
                                    True, STAR_GOLD)
            screen.blit(sub, (WIDTH // 2 - sub.get_width() // 2, ly + 55))
            ver = font_small.render(
                "All 28 Levels · 60 FPS · First-Person Lakitu · Full SM64 Movement",
                True, LIGHT_GREY)
            screen.blit(ver, (WIDTH // 2 - ver.get_width() // 2, ly + 72))

            my = HEIGHT - 220
            for i, item in enumerate(menu_items):
                c = STAR_GOLD if i == selected_index else WHITE
                l = font_menu.render(item, True, c)
                screen.blit(l, (50 + (20 if i == selected_index else 0), my + i * 38))
                if i == selected_index:
                    pygame.draw.polygon(screen, MARIO_RED,
                        [(32, my + i * 38 + 8), (44, my + i * 38 + 14), (32, my + i * 38 + 20)])
            sc = font_small.render(f"Stars: {len(collected_stars)}/{star_total_actual}", True,
                                   STAR_GOLD)
            screen.blit(sc, (WIDTH - 160, HEIGHT - 28))

            if active_overlay == "how":
                ov = pygame.Surface((WIDTH, HEIGHT)); ov.set_alpha(230); ov.fill(BLACK)
                screen.blit(ov, (0, 0))
                pygame.draw.rect(screen, MARIO_RED, (60, 60, WIDTH - 120, HEIGHT - 120), 3)
                lines = [
                    "CONTROLS:",
                    "Mouse — Look Around        C — Toggle Camera",
                    "WASD — Move  (Shift = Sprint)",
                    "SPACE — Jump  (combo for Double / Triple Jump)",
                    "X — Long Jump (while running) / Dive (in air)",
                    "Z — Ground Pound (in air) / Backflip (Ctrl+Z)",
                    "E — Enter Door / Painting / Exit Level",
                    "TAB — Toggle Mouse Capture",
                    "ESC — Pause",
                    "",
                    "SM64 MOVEMENT SYSTEM",
                    "Triple Jump: Land + Jump 3x quickly",
                    "Long Jump: Run + X | Dive: Air + X",
                    "Ground Pound: Air + Z | Backflip: Ctrl + Z",
                    "",
                    "ENTER to close"
                ]
                for i, ln in enumerate(lines):
                    c = STAR_GOLD if i == 0 else WHITE
                    f = font_menu if i == 0 else font_small
                    screen.blit(f.render(ln, True, c), (100, 82 + i * 28))

            elif active_overlay == "credits":
                ov = pygame.Surface((WIDTH, HEIGHT)); ov.set_alpha(230); ov.fill(BLACK)
                screen.blit(ov, (0, 0))
                pygame.draw.rect(screen, BUTTON_GOLD, (60, 60, WIDTH - 120, HEIGHT - 120), 3)
                lines = [
                    "KOOPA ENGINE 0.3  —  SUPER MARIO 64 PC PORT",
                    "",
                    "Engine: Pure Pygame 3D — KoopaEngine 0.3",
                    "15 Main Courses + 5 Secret + 3 Bowser + 5 Castle = 28 Levels",
                    "SM64 PC-port-accurate vertex colour palettes",
                    "Authentic sky gradients + distance fog",
                    "Full SM64 movement: Triple Jump, Long Jump, Backflip,",
                    "  Ground Pound, Dive, Wall Kick, Swimming",
                    "Health pie meter, fall damage, death/respawn",
                    "Fade transitions, red coins, 1-UPs, save system",
                    "Synthesized SFX — no external assets",
                    "",
                    "49 bugs fixed from 0.2 — Production Ready",
                    "",
                    "Copyright (C) 1999-2026  A.C Holdings / Team Flames",
                    "Inspired by: Super Mario 64 (Nintendo, 1996)",
                    "",
                    "ENTER to close"
                ]
                for i, ln in enumerate(lines):
                    c = STAR_GOLD if i == 0 else WHITE
                    f = font_menu if i == 0 else font_small
                    screen.blit(f.render(ln, True, c), (100, 74 + i * 26))

        elif current_state == STATE_LEVEL_SELECT:
            screen.fill((8, 12, 32))
            t = font_big.render("LEVEL SELECT", True, STAR_GOLD)
            screen.blit(t, (WIDTH // 2 - t.get_width() // 2, 16))
            vs = max(0, level_select_idx - 12)
            ve = min(len(level_keys), vs + 18)
            y = 64
            for i in range(vs, ve):
                k = level_keys[i]; info = LEVELS[k]; sel = i == level_select_idx
                req = info["req"]
                unlocked = len(collected_stars) >= req  # FIX #15
                c = STAR_GOLD if sel else (WHITE if unlocked else (100, 100, 100))
                pfx = "► " if sel else "  "
                lock_str = "" if unlocked else " [LOCKED]"
                if k.startswith("castle"): dc = CG_CASTLE_WALL
                elif k.startswith("c"):    dc = BOB_GRASS_1
                elif k.startswith("s"):    dc = CCM_ICE
                else:                      dc = LLL_LAVA_1
                screen.blit(font_menu.render(f"{pfx}{info['name']}{lock_str}", True, c), (36, y))
                screen.blit(font_small.render(f"Req: {req} ★", True, dc), (580, y + 4))
                pygame.draw.circle(screen, dc, (22, y + 12), 5)
                y += 27
            screen.blit(font_small.render(
                "UP/DOWN: Navigate  |  ENTER: Play  |  ESC: Back",
                True, METAL_GREY), (WIDTH // 2 - 180, HEIGHT - 28))

        elif current_state == STATE_GAME:
            fog_color = draw_sky(current_level_id)

            if mouse_captured:
                cam_yaw += mouse_dx * MOUSE_SENS_X
                cam_pitch -= mouse_dy * MOUSE_SENS_Y
                cam_pitch = max(PITCH_MIN, min(PITCH_MAX, cam_pitch))

            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:   cam_yaw -= KEY_TURN
            if keys[pygame.K_RIGHT]:  cam_yaw += KEY_TURN
            if keys[pygame.K_UP]:     cam_pitch = min(PITCH_MAX, cam_pitch + KEY_TURN * 0.7)
            if keys[pygame.K_DOWN]:   cam_pitch = max(PITCH_MIN, cam_pitch - KEY_TURN * 0.7)

            fwd_x = -math.sin(cam_yaw); fwd_z = -math.cos(cam_yaw)
            right_x = math.cos(cam_yaw); right_z = -math.sin(cam_yaw)
            accel_x = accel_z = 0
            sprint = SPRINT_MULT if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT] else 1.0

            if mario and mario.action not in (ACT_DEAD, ACT_STAR_GET,
                                               ACT_LONG_JUMP, ACT_BACKFLIP, ACT_DIVE):
                if keys[pygame.K_w]:
                    accel_x += fwd_x * MOVE_ACCEL * sprint
                    accel_z += fwd_z * MOVE_ACCEL * sprint
                if keys[pygame.K_s]:
                    accel_x -= fwd_x * MOVE_ACCEL * 0.6
                    accel_z -= fwd_z * MOVE_ACCEL * 0.6
                if keys[pygame.K_a]:
                    accel_x -= right_x * MOVE_ACCEL * 0.8
                    accel_z -= right_z * MOVE_ACCEL * 0.8
                if keys[pygame.K_d]:
                    accel_x += right_x * MOVE_ACCEL * 0.8
                    accel_z += right_z * MOVE_ACCEL * 0.8

            vel_x = (vel_x + accel_x) * MOVE_DECEL
            vel_z = (vel_z + accel_z) * MOVE_DECEL
            speed = math.sqrt(vel_x * vel_x + vel_z * vel_z)
            max_spd = MAX_SPEED * sprint
            if speed > max_spd:
                vel_x *= max_spd / speed; vel_z *= max_spd / speed; speed = max_spd

            if mario:
                if mario.action not in (ACT_LONG_JUMP, ACT_BACKFLIP, ACT_DIVE):
                    mario.x += vel_x; mario.z += vel_z
                mario.yaw = cam_yaw
                if speed > 1.0:
                    mario.facing_yaw = cam_yaw

                # Update physics
                death_done = mario.update(floor_y=0, level_mesh=current_level_mesh)

                if death_done:
                    # FIX #11: death respawn
                    if mario.lives > 0:
                        load_level(current_level_id)
                    else:
                        # Game over — back to menu
                        save_game(collected_stars, total_coins, 4)
                        current_state = STATE_MENU
                        release_mouse()
                        continue

                # Star get done
                if mario.action == ACT_STAR_GET and mario.star_get_timer <= 0:
                    mario.action = ACT_IDLE

                # Head bob
                if speed > 1.0 and mario.on_ground and \
                   mario.action not in (ACT_DEAD, ACT_STAR_GET):
                    head_bob_phase += speed * 0.15
                    bob = math.sin(head_bob_phase) * HEAD_BOB_AMT * min(1.0, speed / 8.0)
                else:
                    bob = 0; head_bob_phase *= 0.8

                target_x = mario.x
                target_y = mario.y + EYE_HEIGHT + bob
                target_z = mario.z
                cam_x += (target_x - cam_x) * CAM_LERP
                cam_y += (target_y - cam_y) * CAM_LERP
                cam_z += (target_z - cam_z) * CAM_LERP

                # Invulnerability blink
                if mario.invuln_timer > 0 and mario.invuln_timer % 6 < 3:
                    pass  # Visual blink handled elsewhere

                # Star collection
                for star in current_level_stars:
                    if not star.collected:
                        star.yaw += 0.05
                        dx = mario.x - star.x; dy = mario.y - star.y; dz = mario.z - star.z
                        if math.sqrt(dx*dx + dy*dy + dz*dz) < 60:
                            star.collected = True
                            collected_stars.add(f"{current_level_id}_{star.star_id}")
                            star_flash = 30
                            mario.collect_star()  # FIX #28: star get animation
                            save_game(collected_stars, total_coins, mario.lives)

                # Coin collection
                for coin in current_level_coins:
                    if not coin.collected:
                        coin.yaw += 0.08
                        dx = mario.x - coin.x; dy = mario.y - coin.y; dz = mario.z - coin.z
                        if math.sqrt(dx*dx + dy*dy + dz*dz) < 40:
                            coin.collected = True
                            total_coins += 1
                            coin_flash = 15
                            SFXSynth.play("coin")
                            if total_coins % 50 == 0:
                                mario.lives += 1
                                SFXSynth.play("oneup")
                            # Coins heal (SM64 mechanic)
                            if mario.health < mario.max_health:
                                mario.health = min(mario.max_health, mario.health + 1)

                # Red coin collection (FIX #36)
                for rc in current_level_red_coins:
                    if not rc.collected:
                        rc.yaw += 0.06
                        dx = mario.x - rc.x; dy = mario.y - rc.y; dz = mario.z - rc.z
                        if math.sqrt(dx*dx + dy*dy + dz*dz) < 40:
                            rc.collected = True
                            total_coins += 2  # Red coins worth 2
                            coin_flash = 20
                            SFXSynth.play("coin")
                            if mario.health < mario.max_health:
                                mario.health = min(mario.max_health, mario.health + 2)

                # 1-UP collection (FIX #37)
                for ou in current_level_oneups:
                    if not ou.collected:
                        ou.yaw += 0.04
                        dx = mario.x - ou.x; dy = mario.y - ou.y; dz = mario.z - ou.z
                        if math.sqrt(dx*dx + dy*dy + dz*dz) < 50:
                            ou.collected = True
                            mario.lives += 1
                            SFXSynth.play("oneup")

            # Build render list
            all_polys = []

            # === UPDATE ALL NEW SYSTEMS ===
            if mario and mario.action != ACT_DEAD:
                # Update enemies
                for enemy in current_level_enemies:
                    if enemy.alive:
                        enemy.update_ai(mario.x, mario.y, mario.z, mario.on_ground)
                        enemy.yaw = enemy.facing
                        # Check stomp / damage
                        result_hit = enemy.check_stomp(mario.x, mario.y, mario.z, mario.dy)
                        if result_hit == 1:
                            # Stomped enemy
                            mario.dy = JUMP_FORCE * 0.7  # Bounce off enemy
                            mario.on_ground = False
                            mario.action = ACT_JUMP
                            SFXSynth.play("jump")
                            particles.emit_dust(enemy.x, enemy.y, enemy.z)
                            if not enemy.alive:
                                particles.emit_coin_sparkle(enemy.x, enemy.y + 20, enemy.z)
                                for _ in range(enemy.coin_drop):
                                    total_coins += 1
                                    coin_flash = 10
                        elif result_hit == 2:
                            # Mario hit
                            mario.take_damage(enemy.damage)
                            if mario.action != ACT_DEAD:
                                # Knockback
                                kb_dx = mario.x - enemy.x
                                kb_dz = mario.z - enemy.z
                                kb_dist = math.sqrt(kb_dx * kb_dx + kb_dz * kb_dz)
                                if kb_dist > 0:
                                    mario.x += (kb_dx / kb_dist) * 30
                                    mario.z += (kb_dz / kb_dist) * 30
                                mario.dy = 12
                                mario.on_ground = False
                                mario.action = ACT_FREEFALL

                # Update NPCs
                for npc in current_level_npcs:
                    npc.update()
                    # Face Mario when close
                    ndx = mario.x - npc.x; ndz = mario.z - npc.z
                    ndist = math.sqrt(ndx * ndx + ndz * ndz)
                    if ndist < 200:
                        npc.facing = math.atan2(ndx, ndz)
                        npc.yaw = npc.facing

                # Update signs
                for sign in current_level_signs:
                    sign.update()

                # Update moving platforms
                for plat in current_level_platforms:
                    pdx, pdy, pdz = plat.update(mario.x, mario.y, mario.z)
                    # Carry Mario if standing on platform
                    if plat.player_on:
                        mario.x += pdx
                        mario.y += pdy
                        mario.z += pdz
                        cam_x += pdx; cam_y += pdy; cam_z += pdz
                        if pdy >= 0:
                            mario.on_ground = True
                            mario.dy = 0
                            if mario.action in (ACT_FREEFALL, ACT_JUMP):
                                mario.action = ACT_IDLE

                # Check damage zones
                for dz in current_level_damage_zones:
                    if dz.check(mario.x, mario.y, mario.z):
                        if dz.kind == ZONE_LAVA:
                            mario.take_damage(dz.damage)
                            if mario.action != ACT_DEAD:
                                mario.dy = dz.knockback
                                mario.on_ground = False
                                mario.action = ACT_FREEFALL
                                particles.emit_fire(mario.x, mario.y, mario.z)
                        elif dz.kind == ZONE_QUICKSAND:
                            vel_x *= dz.slow_factor
                            vel_z *= dz.slow_factor
                            mario.y -= 0.5  # Slowly sink
                            if mario.y < dz.y_min:
                                mario.take_damage(dz.damage)
                        elif dz.kind == ZONE_TOXIC:
                            if self_anim_frame % 60 == 0 if hasattr(mario, '_toxic_tick') else True:
                                mario.take_damage(dz.damage)
                                mario._toxic_tick = True
                        elif dz.kind == ZONE_COLD:
                            vel_x *= dz.slow_factor
                            vel_z *= dz.slow_factor
                        elif dz.kind == ZONE_SPIKES:
                            mario.take_damage(dz.damage)
                            mario.dy = dz.knockback
                            mario.on_ground = False

            # Update particles
            particles.update()

            # Emit ambient particles based on level
            if current_level_id in ("c04_cool", "c10_snow"):
                particles.emit_snow(cam_x, cam_y, cam_z, 500)
            elif current_level_id == "c07_lava":
                if random.random() < 0.1:
                    lx = cam_x + random.uniform(-400, 400)
                    lz = cam_z + random.uniform(-400, 400)
                    particles.emit_fire(lx, 0, lz)

            # Star get particles
            if mario and mario.action == ACT_STAR_GET and mario.star_get_timer == 110:
                particles.emit_star_burst(mario.x, mario.y + 40, mario.z)

            # Ground pound particles
            if mario and mario.action == ACT_GROUND_POUND_LAND and mario.ground_pound_timer == 11:
                particles.emit_ground_pound_ring(mario.x, mario.y, mario.z)
            if current_level_mesh:
                all_polys.extend(render_mesh(screen, current_level_mesh,
                                             cam_x, cam_y, cam_z, cam_yaw, cam_pitch, cx, cy))
            for star in current_level_stars:
                if not star.collected:
                    all_polys.extend(render_mesh(screen, star,
                                                 cam_x, cam_y, cam_z, cam_yaw, cam_pitch, cx, cy))
            for coin in current_level_coins:
                if not coin.collected:
                    all_polys.extend(render_mesh(screen, coin,
                                                 cam_x, cam_y, cam_z, cam_yaw, cam_pitch, cx, cy))
            for rc in current_level_red_coins:
                if not rc.collected:
                    all_polys.extend(render_mesh(screen, rc,
                                                 cam_x, cam_y, cam_z, cam_yaw, cam_pitch, cx, cy))
            for ou in current_level_oneups:
                if not ou.collected:
                    all_polys.extend(render_mesh(screen, ou,
                                                 cam_x, cam_y, cam_z, cam_yaw, cam_pitch, cx, cy))
            # Render enemies
            for enemy in current_level_enemies:
                if enemy.alive:
                    all_polys.extend(render_mesh(screen, enemy,
                                                 cam_x, cam_y, cam_z, cam_yaw, cam_pitch, cx, cy))
            # Render NPCs
            for npc in current_level_npcs:
                all_polys.extend(render_mesh(screen, npc,
                                             cam_x, cam_y, cam_z, cam_yaw, cam_pitch, cx, cy))
            # Render moving platforms
            for plat in current_level_platforms:
                all_polys.extend(render_mesh(screen, plat,
                                             cam_x, cam_y, cam_z, cam_yaw, cam_pitch, cx, cy))
            # Render cannons
            for cannon in current_level_cannons:
                all_polys.extend(render_mesh(screen, cannon,
                                             cam_x, cam_y, cam_z, cam_yaw, cam_pitch, cx, cy))
            # Render signs
            for sign in current_level_signs:
                all_polys.extend(render_mesh(screen, sign,
                                             cam_x, cam_y, cam_z, cam_yaw, cam_pitch, cx, cy))

            all_polys.sort(key=lambda x: x['depth'], reverse=True)
            for item in all_polys:
                depth = item['depth']
                fog = min(1.0, depth / VIEW_DISTANCE)
                r, g, b = item['color']
                fr = int(r + (fog_color[0] - r) * fog)
                fg = int(g + (fog_color[1] - g) * fog)
                fb = int(b + (fog_color[2] - b) * fog)
                pygame.draw.polygon(screen,
                    (max(0,min(255,fr)), max(0,min(255,fg)), max(0,min(255,fb))), item['poly'])

            draw_crosshair()
            draw_hud()
            draw_level_intro()

            # Render particles
            particles.render(screen, cam_x, cam_y, cam_z, cam_yaw, cam_pitch, cx, cy)

            # Render minimap
            minimap.draw(screen, mario.x if mario else 0, mario.z if mario else 0,
                        cam_yaw, current_level_stars, current_level_enemies,
                        current_level_coins, current_level_npcs)

            # Render NPC dialog boxes
            for npc in current_level_npcs:
                if npc.talking and npc.talk_timer > 0:
                    dialog_box = pygame.Surface((WIDTH - 80, 80), pygame.SRCALPHA)
                    dialog_box.fill((0, 0, 0, 200))
                    screen.blit(dialog_box, (40, HEIGHT - 140))
                    pygame.draw.rect(screen, STAR_GOLD, (40, HEIGHT - 140, WIDTH - 80, 80), 2)
                    # Name tag
                    name_surf = font_hud.render(npc.name, True, STAR_GOLD)
                    screen.blit(name_surf, (56, HEIGHT - 136))
                    # Dialog text (split on \n)
                    lines = npc.dialog.split("\\n")
                    for i, line in enumerate(lines):
                        line_surf = font_small.render(line, True, WHITE)
                        screen.blit(line_surf, (56, HEIGHT - 116 + i * 18))

            # Render sign text boxes
            for sign in current_level_signs:
                if sign.showing and sign.show_timer > 0:
                    sign_box = pygame.Surface((WIDTH - 120, 64), pygame.SRCALPHA)
                    sign_box.fill((40, 28, 16, 220))
                    screen.blit(sign_box, (60, HEIGHT - 130))
                    pygame.draw.rect(screen, (180, 150, 100), (60, HEIGHT - 130, WIDTH - 120, 64), 2)
                    lines = sign.text.split("\\n")
                    for i, line in enumerate(lines):
                        line_surf = font_small.render(line, True, WHITE)
                        screen.blit(line_surf, (76, HEIGHT - 122 + i * 18))

            # Enemy hit flash effect
            if mario and mario.invuln_timer > 0 and mario.invuln_timer % 8 < 4:
                flash_overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                flash_overlay.fill((255, 0, 0, 30))
                screen.blit(flash_overlay, (0, 0))

            # Water surface indicator
            if mario and mario.in_water:
                water_bar = pygame.Surface((WIDTH, 4), pygame.SRCALPHA)
                water_bar.fill((0, 100, 220, 100))
                screen.blit(water_bar, (0, 0))

            # Hint text
            hint = ""
            if current_level_id and "castle" in current_level_id:
                hint = "E: Enter Door / Painting"
            elif current_level_id:
                hint = "E: Exit Level"
            if hint:
                screen.blit(font_small.render(hint, True, STAR_GOLD), (WIDTH // 2 - 60, 8))

        elif current_state == STATE_PAUSE:
            ov = pygame.Surface((WIDTH, HEIGHT)); ov.set_alpha(180); ov.fill(BLACK)
            screen.blit(ov, (0, 0))
            screen.blit(font_big.render("PAUSED", True, STAR_GOLD), (WIDTH // 2 - 60, 120))
            # FIX #48: show level name in pause
            if current_level_id:
                ln = font_menu.render(LEVELS[current_level_id]["name"], True, LIGHT_GREY)
                screen.blit(ln, (WIDTH // 2 - ln.get_width() // 2, 168))
            rows = [
                ("ESC — Resume", WHITE),
                ("R — Restart Level", WHITE),
                ("Q — Save & Quit to Menu", WHITE),
                ("", WHITE),
                (f"Stars: {len(collected_stars)}/{star_total_actual}", STAR_GOLD),
                (f"Coins: {total_coins}", COIN_YELLOW),
                (f"Lives: {mario.lives if mario else 4}", RED),
                (f"Health: {mario.health if mario else 8}/8", HEALTH_PIE_FG),
            ]
            for i, (t, c) in enumerate(rows):
                if t:
                    screen.blit(font_menu.render(t, True, c), (WIDTH // 2 - 120, 210 + i * 34))

        # FIX #9: single blit instead of per-line scanline draws
        screen.blit(scanline_overlay, (0, 0))

        # Draw transition overlay last
        transition.draw(screen)

        pygame.display.flip()

    # Save on exit
    save_game(collected_stars, total_coins, mario.lives if mario else saved_lives)
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
