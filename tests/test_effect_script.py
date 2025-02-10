from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict

import pytest

from hal_effect.types import (
    OpCode, WaitInstruction, VectorInstruction, ColorBlendInstruction,
    SizeLerpInstruction, SetFlagsInstruction,
    VelMulInstruction, VelAngleInstruction, UnkInstruction, TryDeadRandInstruction, LifeRandInstruction,
    ScriptInstruction, SetSizeRandInstruction
)
from hal_effect.parser import EffectScriptParser


@dataclass
class InstructionTestCase:
    """Test case for instruction parsing."""
    name: str
    bytes_str: str
    opcode: OpCode
    args: Dict[str, Any]

    def __str__(self) -> str:
        """Return the test case name for pytest output."""
        return self.name



TEST_CASES = [
    InstructionTestCase(
        name="SET_PRIM_BLEND with all components",
        bytes_str="CF 3C FF FF FF 00",
        opcode=OpCode.SET_PRIM_BLEND,
        args={
            "type": ColorBlendInstruction,
            "lerp_length": 61,
            "red": 255,
            "green": 255,
            "blue": 255,
            "alpha": 0
        }
    ),
    InstructionTestCase(
        name="SET_ENV_BLEND with all components",
        bytes_str="DF 01 80 FF FF FF",
        opcode=OpCode.SET_ENV_BLEND,
        args={
            "type": ColorBlendInstruction,
            "lerp_length": 2,
            "red": 128,
            "green": 255,
            "blue": 255,
            "alpha": 255
        }
    ),
    InstructionTestCase(
        name="SET_SIZE_LERP",
        bytes_str="A0 14 43 7A 00 00",
        opcode=OpCode.SET_SIZE_LERP,
        args={
            "type": SizeLerpInstruction,
            "lerp_length": 21,
            "target_size": 250.0
        }
    ),
    InstructionTestCase(
        name="SET_FLAGS",
        bytes_str="A1 80",
        opcode=OpCode.SET_FLAGS,
        args={
            "type": SetFlagsInstruction,
            "flags": 0x80
        }
    ),
    InstructionTestCase(
        name="MUL_VEL",
        bytes_str="AB 40 00 00 00",
        opcode=OpCode.MUL_VEL,
        args={
            "type": VelMulInstruction,
            "factor": 2.0
        }
    ),
    InstructionTestCase(
        name="SET_VEL_ANGLE",
        bytes_str="A9 3E B2 B8 C2",
        opcode=OpCode.SET_VEL_ANGLE,
        args={
            "type": VelAngleInstruction,
            "angle": 0.34906584
        }
    ),
    InstructionTestCase(
        name="SET_SIZE_RAND",
        bytes_str="AC 00 40 A0 00 00 41 F0 00 00",
        opcode=OpCode.SET_SIZE_RAND,
        args={
            "type": SetSizeRandInstruction,
            "lerp_length": 1,
            "base": 5.0,
            "random_range": 30.0
        }
    ),
    InstructionTestCase(
        name="SET_PRIM_BLEND with alpha only",
        bytes_str="C8 64 00",
        opcode=OpCode.SET_PRIM_BLEND,
        args={
            "type": ColorBlendInstruction,
            "lerp_length": 101,
            "red": None,
            "green": None,
            "blue": None,
            "alpha": 0
        }
    ),
    InstructionTestCase(
        name="SET_POS with all components",
        bytes_str="87 42 4C 00 00 44 C2 00 00 C2 80 00 00",
        opcode=OpCode.SET_POS,
        args={
            "type": VectorInstruction,
            "x": 51.0,
            "y": 1552.0,
            "z": -64.0
        }
    ),
    InstructionTestCase(
        name="SET_UNK_0B",
        bytes_str="BC 00 03",
        opcode=OpCode.SET_UNK_0B,
        args={
            "type": UnkInstruction,
            "base_value": 0,
            "random_range": 3
        }
    ),
    InstructionTestCase(
        name="TRY_DEAD_RAND",
        bytes_str="A7 0A",
        opcode=OpCode.TRY_DEAD_RAND,
        args={
            "type": TryDeadRandInstruction,
            "probability": 10
        }
    ),
    InstructionTestCase(
        name="SET_LIFE_RAND",
        bytes_str="A6 00 32 00 32",
        opcode=OpCode.SET_LIFE_RAND,
        args={
            "type": LifeRandInstruction,
            "base_life": 50,
            "random_range": 50
        }
    ),
    InstructionTestCase(
        name="SET_ENV_BLEND with red and blue",
        bytes_str="D7 00 00 FF 15",
        opcode=OpCode.SET_ENV_BLEND,
        args={
            "type": ColorBlendInstruction,
            "lerp_length": 1,
            "red": 0,
            "green": 255,
            "blue": 21,
            "alpha": None
        }
    ),
    InstructionTestCase(
        name="MAKE_GENERATOR",
        bytes_str="A5 00 17",
        opcode=OpCode.MAKE_GENERATOR,
        args={
            "type": ScriptInstruction,
            "script_id": 23
        }
    ),
    InstructionTestCase(
        name="MAKE_SCRIPT",
        bytes_str="A4 00 48",
        opcode=OpCode.MAKE_SCRIPT,
        args={
            "type": ScriptInstruction,
            "script_id": 72
        }
    ),
]


def hex_to_bytes(hex_str: str) -> bytes:
    """Convert a space-separated hex string to bytes."""
    return bytes.fromhex(hex_str.replace(" ", ""))


@pytest.mark.parametrize("case", TEST_CASES, ids=str)
def test_parse_instructions(case: InstructionTestCase):
    """Test parsing various instructions with their arguments."""
    data = hex_to_bytes(case.bytes_str)
    parser = EffectScriptParser()
    instr = parser._parse_instruction(data)
    
    assert instr is not None
    assert instr.opcode == case.opcode
    
    # Check the type of the instruction arguments
    assert isinstance(instr.args, case.args["type"])
    
    # Check each expected argument value
    for key, value in case.args.items():
        if key != "type":
            if isinstance(value, float):
                # Floating point values need to be compared with a small tolerance
                assert abs(getattr(instr.args, key) - value) < 1e-6, f"Argument {key} mismatch"
            else:
                assert getattr(instr.args, key) == value, f"Argument {key} mismatch"


def test_parse_wait_instruction():
    """Test parsing various forms of wait instructions."""
    # Simple wait 
    data = bytes([0x05])  
    parser = EffectScriptParser()
    instr = parser._parse_instruction(data)
    assert isinstance(instr.args, WaitInstruction)
    assert instr.args.frames == 5
    assert instr.args.data_id is None

    # Wait with extra byte 
    data = bytes([0x2C, 0x01])
    parser = EffectScriptParser()
    instr = parser._parse_instruction(data)
    assert isinstance(instr.args, WaitInstruction)
    assert instr.args.frames == 3073
    assert instr.args.data_id is None

    # Wait with data ID
    data = bytes([0x45, 0x7B])  
    parser = EffectScriptParser()
    instr = parser._parse_instruction(data)
    assert isinstance(instr.args, WaitInstruction)
    assert instr.args.frames == 5
    assert instr.args.data_id == 123
