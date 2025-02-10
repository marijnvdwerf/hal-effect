from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum
from typing import List, Optional, Union


@dataclass
class Vec3f:
    x: float
    y: float
    z: float


class OpCode(IntEnum):
    # Vector operations
    SET_POS = 0x80        # Set particle position
    ADD_POS = 0x88        # Add to particle position
    SET_VEL = 0x90        # Set particle velocity
    ADD_VEL = 0x98        # Add to particle velocity
    
    # Value operations
    SET_SIZE_LERP = 0xA0  # Set target size and interpolation length
    SET_FLAGS = 0xA1      # Set particle flag
    SET_GRAVITY = 0xA2    # Set gravity
    SET_FRICTION = 0xA3   # Set friction
    MAKE_SCRIPT = 0xA4    # Make new particle from script
    MAKE_GENERATOR = 0xA5 # Make new generator
    SET_LIFE_RAND = 0xA6  # Set random lifetime
    TRY_DEAD_RAND = 0xA7  # Random chance to destroy
    ADD_VEL_RAND = 0xA8   # Add random velocity
    SET_VEL_ANGLE = 0xA9  # Set velocity angle
    MAKE_RAND = 0xAA      # Make random particle
    MUL_VEL = 0xAB       # Multiply velocity uniformly
    SET_SIZE_RAND = 0xAC  # Set random size
    
    # Flags
    SET_FLAG_80 = 0xAD    # Set flag bit 0x80
    NO_MASK_ST = 0xAE     # Clear mask S/T flags
    MASK_S = 0xAF         # Set mask S flag
    MASK_T = 0xB0         # Set mask T flag
    MASK_ST = 0xB1        # Set both mask flags
    ALPHA_BLEND = 0xB2    # Set alpha blend flag
    NO_DITHER = 0xB3      # Clear dither flag
    DITHER = 0xB4        # Set dither flag
    NO_NOISE = 0xB5      # Clear noise flag
    NOISE = 0xB6         # Set noise flag
    
    # Advanced operations
    SET_DIST_VEL = 0xB7   # Set velocity from distance
    ADD_DIST_VEL_MAG = 0xB8 # Add distance magnitude to velocity
    MAKE_ID = 0xB9       # Make particle by ID
    PRIM_BLEND_RAND = 0xBA # Random primitive blend
    ENV_BLEND_RAND = 0xBB # Random environment blend
    SET_UNK_0B = 0xBC    # Set unknown byte value with random range
    SET_VEL_MAG = 0xBD   # Set velocity magnitude
    MUL_VEL_AXIS = 0xBE  # Multiply velocity per axis
    SET_ATTACH_ID = 0xBF  # Set attach object ID
    
    # Color blending
    SET_PRIM_BLEND = 0xC0 # Set primitive blend color
    SET_ENV_BLEND = 0xD0  # Set environment blend color
    
    # Flow control
    SET_LOOP = 0xFA      # Start loop
    LOOP = 0xFB          # Loop
    SET_RETURN = 0xFC    # Set return point
    RETURN = 0xFD        # Return to point
    DEAD = 0xFE         # Destroy particle
    END = 0xFF          # End script


# AST Node Classes
@dataclass
class WaitInstruction:
    frames: int
    data_id: Optional[int] = None

@dataclass
class VectorInstruction:
    x: Optional[float] = None
    y: Optional[float] = None
    z: Optional[float] = None

@dataclass
class SizeLerpInstruction:
    lerp_length: int
    target_size: float

@dataclass
class ColorBlendInstruction:
    lerp_length: int
    red: Optional[int] = None
    green: Optional[int] = None
    blue: Optional[int] = None
    alpha: Optional[int] = None

@dataclass
class ScriptInstruction:
    script_id: int

@dataclass
class LifeRandInstruction:
    base_life: int
    random_range: int

@dataclass
class TryDeadRandInstruction:
    probability: int

@dataclass
class VelRandInstruction:
    x_range: float
    y_range: float
    z_range: float

@dataclass
class VelAngleInstruction:
    angle: float

@dataclass
class VelMulInstruction:
    factor: float

@dataclass
class VelAxisMulInstruction:
    x_factor: float
    y_factor: float
    z_factor: float

@dataclass
class UnkInstruction:
    base_value: int
    random_range: int

@dataclass
class SetFlagsInstruction:
    flags: int

@dataclass
class SetLoopInstruction:
    count: int

@dataclass
class SimpleInstruction:
    """For instructions that take no parameters"""
    pass

@dataclass
class SetSizeRandInstruction:
    base_size: float
    random_range: float

@dataclass
class Instruction:
    opcode: OpCode
    args: Union[
        WaitInstruction,
        VectorInstruction,
        SizeLerpInstruction,
        ColorBlendInstruction,
        ScriptInstruction,
        LifeRandInstruction,
        TryDeadRandInstruction,
        VelRandInstruction,
        VelAngleInstruction,
        VelMulInstruction,
        VelAxisMulInstruction,
        UnkInstruction,
        SetFlagsInstruction,
        SetLoopInstruction,
        SimpleInstruction,
        SetSizeRandInstruction,
    ]

@dataclass
class EffectScript:
    kind: int
    texture_id: int
    effect_lifetime: int
    particle_lifetime: int
    flags: int
    gravity: float
    friction: float
    velocity: Vec3f
    size: float
    bytecode: List[Instruction]

@dataclass
class EffectScriptPtr:
    ptr_value: int
    target: Optional[EffectScript]

@dataclass
class ParticleScriptDesc:
    count: int
    scripts: List[EffectScriptPtr] 