from __future__ import annotations

import struct
from typing import Optional

from .types import (
    Vec3f,
    OpCode,
    Instruction,
    EffectScript,
    EffectScriptPtr,
    ParticleScriptDesc,
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
)


class BinaryReader:
    """Helper class for reading binary data with a position cursor."""

    def __init__(self, data: bytes):
        self.data = data
        self.offset = 0

    def read_float(self) -> float:
        value = struct.unpack(">f", self.data[self.offset : self.offset + 4])[0]
        self.offset += 4
        return value

    def read_u16(self) -> int:
        value = struct.unpack(">H", self.data[self.offset : self.offset + 2])[0]
        self.offset += 2
        return value

    def read_u32(self) -> int:
        value = struct.unpack(">I", self.data[self.offset : self.offset + 4])[0]
        self.offset += 4
        return value

    def read_s32(self) -> int:
        value = struct.unpack(">i", self.data[self.offset : self.offset + 4])[0]
        self.offset += 4
        return value

    def read_u8(self) -> int:
        value = self.data[self.offset]
        self.offset += 1
        return value

    def read_vec3f(self) -> Vec3f:
        x = self.read_float()
        y = self.read_float()
        z = self.read_float()
        return Vec3f(x, y, z)

    def read_var_length_u16(self) -> int:
        if self.offset >= len(self.data):
            return 0

        first_byte = self.read_u8()

        if first_byte & 0x80:
            if self.offset >= len(self.data):
                return 0
            value = ((first_byte & 0x7F) << 8) + self.read_u8()
        else:
            value = first_byte

        return value + 1

    def skip(self, count: int):
        """Skip a number of bytes."""
        self.offset += count

    def seek(self, offset: int):
        """Set absolute position."""
        self.offset = offset

    def can_read(self, size: int) -> bool:
        """Check if we can read size bytes from current position."""
        return self.offset + size <= len(self.data)


class EffectScriptParser:
    """Parser for effect script binary format."""

    def __init__(self):
        self.reader = None

    def parse(self, data: bytes) -> ParticleScriptDesc:
        """Parse a particle script description from binary data."""
        self.reader = BinaryReader(data)
        return self._parse_particle_script_desc()

    def _parse_instruction(self, data: Optional[bytes] = None) -> Optional[Instruction]:
        """Parse a single instruction from the current position or from provided bytes data.

        Args:
            data: Optional bytes to parse. If provided, creates a new reader for just this instruction.
        """
        reader = BinaryReader(data) if data is not None else self.reader

        if not reader.can_read(1):
            return None

        opcode = reader.read_u8()

        # Wait command (0x00-0x7F)
        if opcode < 0x80:
            frames = opcode & 0x1F
            if opcode & 0x20:
                extra = reader.read_u8()
                frames = (frames << 8) | extra
            data_id = None
            if opcode & 0x40:
                data_id = reader.read_u8()
            return Instruction(OpCode.END, WaitInstruction(frames, data_id))

        # Vector operations
        if opcode & 0xF8 in [
            OpCode.SET_POS,
            OpCode.ADD_POS,
            OpCode.SET_VEL,
            OpCode.ADD_VEL,
        ]:
            args = VectorInstruction()
            if opcode & 1:
                args.x = reader.read_float()
            if opcode & 2:
                args.y = reader.read_float()
            if opcode & 4:
                args.z = reader.read_float()
            return Instruction(OpCode(opcode & 0xF8), args)

        # Color blend operations
        if opcode & 0xF0 in [OpCode.SET_PRIM_BLEND, OpCode.SET_ENV_BLEND]:
            length = reader.read_var_length_u16()
            args = ColorBlendInstruction(length)
            if opcode & 1:
                args.red = reader.read_u8()
            if opcode & 2:
                args.green = reader.read_u8()
            if opcode & 4:
                args.blue = reader.read_u8()
            if opcode & 8:
                args.alpha = reader.read_u8()
            return Instruction(OpCode(opcode & 0xF0), args)

        # Other instructions based on exact opcode
        try:
            op = OpCode(opcode)
        except ValueError:
            return None

        if op in [OpCode.MAKE_SCRIPT, OpCode.MAKE_GENERATOR, OpCode.MAKE_ID]:
            script_id = reader.read_u16()
            return Instruction(op, ScriptInstruction(script_id))

        elif op == OpCode.SET_SIZE_LERP:
            length = reader.read_var_length_u16()
            size = reader.read_float()
            return Instruction(op, SizeLerpInstruction(length, size))

        elif op == OpCode.SET_LIFE_RAND:
            base = reader.read_u16()
            range_val = reader.read_u16()
            return Instruction(op, LifeRandInstruction(base, range_val))

        elif op == OpCode.TRY_DEAD_RAND:
            prob = reader.read_u8()
            return Instruction(op, TryDeadRandInstruction(prob))

        elif op == OpCode.ADD_VEL_RAND:
            x = reader.read_float()
            y = reader.read_float()
            z = reader.read_float()
            return Instruction(op, VelRandInstruction(x, y, z))

        elif op == OpCode.SET_VEL_ANGLE:
            angle = reader.read_float()
            return Instruction(op, VelAngleInstruction(angle))

        elif op == OpCode.MUL_VEL:
            factor = reader.read_float()
            return Instruction(op, VelMulInstruction(factor))

        elif op == OpCode.MUL_VEL_AXIS:
            x = reader.read_float()
            y = reader.read_float()
            z = reader.read_float()
            return Instruction(op, VelAxisMulInstruction(x, y, z))

        elif op == OpCode.SET_UNK_0B:
            base = reader.read_u8()
            range_val = reader.read_u8()
            return Instruction(op, UnkInstruction(base, range_val))

        elif op == OpCode.SET_FLAGS:
            flags = reader.read_u8()
            return Instruction(op, SetFlagsInstruction(flags))

        elif op == OpCode.SET_LOOP:
            count = reader.read_u8()
            return Instruction(op, SetLoopInstruction(count))

        elif op == OpCode.SET_SIZE_RAND:
            length = reader.read_var_length_u16()
            base = reader.read_float()
            range_val = reader.read_float()
            return Instruction(op, SetSizeRandInstruction(length, base, range_val))

        # Simple instructions with no parameters
        elif op in [
            OpCode.LOOP,
            OpCode.SET_RETURN,
            OpCode.RETURN,
            OpCode.DEAD,
            OpCode.END,
        ]:
            return Instruction(op, SimpleInstruction())

        return None

    def _parse_effect_script(self, next_ptr: Optional[int] = None) -> EffectScript:
        kind = self.reader.read_u16()
        texture_id = self.reader.read_u16()
        effect_lifetime = self.reader.read_u16()
        particle_lifetime = self.reader.read_u16()
        flags = self.reader.read_u32()
        gravity = self.reader.read_float()
        friction = self.reader.read_float()
        velocity = self.reader.read_vec3f()

        # Skip unknown fields
        self.reader.skip(12)  # 3 unknown float fields

        size = self.reader.read_float()

        # Parse bytecode until next effect or end of file
        bytecode = []
        while True:
            if next_ptr is not None and self.reader.offset >= next_ptr:
                break

            instr = self._parse_instruction()
            if instr is None:
                break

            bytecode.append(instr)
            if instr.opcode == OpCode.END:
                break

        return EffectScript(
            kind=kind,
            texture_id=texture_id,
            effect_lifetime=effect_lifetime,
            particle_lifetime=particle_lifetime,
            flags=flags,
            gravity=gravity,
            friction=friction,
            velocity=velocity,
            size=size,
            bytecode=bytecode,
        )

    def _parse_particle_script_desc(self) -> ParticleScriptDesc:
        count = self.reader.read_s32()
        scripts = []

        # First read all pointers
        for _ in range(count):
            ptr_value = self.reader.read_u32()
            scripts.append(EffectScriptPtr(ptr_value=ptr_value, target=None))

        # Now parse each script at its pointer location
        for i, script in enumerate(scripts):
            if script.ptr_value != 0:
                # Get the next pointer location if there is one
                next_ptr = None
                for next_script in scripts[i + 1 :]:
                    if next_script.ptr_value != 0:
                        next_ptr = next_script.ptr_value
                        break

                old_offset = self.reader.offset
                self.reader.seek(script.ptr_value)
                script.target = self._parse_effect_script(next_ptr)
                self.reader.seek(old_offset)

        return ParticleScriptDesc(count=count, scripts=scripts)
