from __future__ import annotations

import pytest

from hal_effect.parser import EffectScriptParser
from hal_effect.types import OpCode


def hex_to_bytes(hex_str: str) -> bytes:
    """Convert a space-separated hex string to bytes."""
    return bytes.fromhex(hex_str.replace(" ", ""))


def test_parse_particle_script():
    """Test parsing a complete particle script file."""
    # This is a particle script with 2 effect scripts
    data = (
        # Header: count=2
        "00 00 00 02"
        # Script pointers
        " 00 00 00 0C"  # First script at offset 0x0C
        " 00 00 00 40"  # Second script at offset 0x40
        # First script at 0x0C
        " 00 00"  # kind=0
        " 00 00"  # texture_id=0
        " 00 14"  # effect_lifetime=20
        " 00 1E"  # particle_lifetime=30
        " 00 00 00 02"  # flags=2 (4 bytes)
        " 3F 80 00 00"  # gravity=1.0
        " 3F 7A E1 48"  # friction=0.98
        " 00 00 00 00"  # velocity.x=0.0
        " 40 C0 00 00"  # velocity.y=6.0
        " 00 00 00 00"  # velocity.z=0.0
        " 3D CC CC CD"  # unk20=0.1
        " 40 49 0F DA"  # unk24=3.14159
        " 40 40 00 00"  # unk28=3.0
        " 40 A0 00 00"  # size=5.0
        " FF"  # END instruction
        " 01 02 03"  # Padding
        # Second script at 0x40
        " 00 00"  # kind=0
        " 00 01"  # texture_id=1
        " 00 50"  # effect_lifetime=80
        " 00 64"  # particle_lifetime=100
        " 00 00 00 03"  # flags=3 (4 bytes)
        " 3C F5 C2 8F"  # gravity=0.03
        " 3F 7A E1 48"  # friction=0.98
        " 00 00 00 00"  # velocity.x=0.0
        " 3C 23 D7 0A"  # velocity.y=0.01
        " 40 00 00 00"  # velocity.z=2.0
        " 41 70 00 00"  # unk20=15.0
        " 3F 06 0A 92"  # unk24=0.523599
        " 3F 00 00 00"  # unk28=0.5
        " 41 A0 00 00"  # size=20.0
        " FF"  # END instruction
        " FE FD FC FB"  # Padding
        " FA F9 F8"  # More padding
        " 00 00 00 00"  # Padding
        " 00 00 00 00"  # Padding
    )

    parser = EffectScriptParser()
    result = parser.parse(hex_to_bytes(data))

    # Check overall structure
    assert len(result) == 2

    # Check first script
    script1 = result[0]
    assert script1.kind == 0
    assert script1.texture_id == 0
    assert script1.effect_lifetime == 20
    assert script1.particle_lifetime == 30
    assert script1.flags == 2
    assert script1.gravity == pytest.approx(1.0)
    assert script1.friction == pytest.approx(0.98)
    assert script1.velocity.x == pytest.approx(0.0)
    assert script1.velocity.y == pytest.approx(6.0)
    assert script1.velocity.z == pytest.approx(0.0)
    assert script1.size == pytest.approx(5.0)
    assert len(script1.bytecode) == 1
    assert script1.bytecode[0].opcode == OpCode.END

    # Check second script
    script2 = result[1]
    assert script2.kind == 0
    assert script2.texture_id == 1
    assert script2.effect_lifetime == 80
    assert script2.particle_lifetime == 100
    assert script2.flags == 3
    assert script2.gravity == pytest.approx(0.03)
    assert script2.friction == pytest.approx(0.98)
    assert script2.velocity.x == pytest.approx(0.0)
    assert script2.velocity.y == pytest.approx(0.01)
    assert script2.velocity.z == pytest.approx(2.0)
    assert script2.size == pytest.approx(20.0)

    # Check second script bytecode - only END instruction, rest is padding
    assert len(script2.bytecode) == 1
    assert script2.bytecode[0].opcode == OpCode.END
