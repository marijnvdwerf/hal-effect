meta:
  id: n64_effect_script
  title: N64 Effect Script Format
  file-extension: bin
  endian: be

seq:
  - id: name
    type: particle_script_desc

types:
  particle_script_desc:
    seq:
      - id: count
        type: s4
      - id: scripts
        type: effect_script_ptr
        repeat: expr
        repeat-expr: count

  effect_script_ptr:
    seq:
      - id: ptr_value
        type: u4
        doc: Memory address pointing to an effect_script
    instances:
      target:
        type: effect_script
        pos: ptr_value
        if: ptr_value != 0
        doc: The EffectScript data this pointer references

  effect_script:
    seq:
      - id: kind
        type: u2
        doc: Effect kind
      - id: texture_id
        type: u2
      - id: effect_lifetime
        type: u2
      - id: particle_lifetime
        type: u2
      - id: flags
        type: u4
      - id: gravity
        type: f4
      - id: friction
        type: f4
      - id: vel
        type: vec3f
      - id: unk_20
        type: f4
      - id: unk_24
        type: f4
      - id: unk_28
        type: f4
      - id: size
        type: f4
      - id: bytecode
        type: instruction
        repeat: until
        repeat-until: _.base_opcode == opcode::end

  vec3f:
    seq:
      - id: x
        type: f4
      - id: y
        type: f4
      - id: z
        type: f4

  instruction:
    doc: |
      Base instruction type that contains an opcode and its corresponding data.
      The opcode determines how the following bytes are interpreted.

      Opcode ranges:
      - 0x00-0x7F: Wait commands
      - 0x80-0x9F: Vector operations
      - 0xA0-0xBF: Value and flag operations
      - 0xC0-0xDF: Color blend operations
      - 0xFA-0xFF: Flow control operations
    -webide-representation: "{base_opcode} {args}"
    seq:
      - id: opcode_raw
        type: u1
      - id: args
        type:
          switch-on: base_opcode
          cases:
            "opcode::wait": wait_args # 0x00-0x7F
            "opcode::set_pos": vector_args # 0x80-0x87
            "opcode::add_pos": vector_args # 0x88-0x8F
            "opcode::set_vel": vector_args # 0x90-0x97
            "opcode::add_vel": vector_args # 0x98-0x9F
            "opcode::set_size_lerp": size_lerp_args
            "opcode::set_size_rand": size_rand_args
            "opcode::set_flags": set_flags_args
            "opcode::set_gravity": set_gravity_args
            "opcode::set_friction": set_friction_args
            "opcode::make_script": make_script_args
            "opcode::make_generator": make_script_args
            "opcode::set_life_rand": life_rand_args
            "opcode::try_dead_rand": try_dead_rand_args
            "opcode::add_vel_rand": add_vel_rand_args
            "opcode::set_vel_angle": set_vel_angle_args
            "opcode::make_rand": empty_args
            "opcode::mul_vel": mul_vel_args
            "opcode::set_flag_80": empty_args
            "opcode::no_mask_st": empty_args
            "opcode::mask_s": empty_args
            "opcode::mask_t": empty_args
            "opcode::mask_st": empty_args
            "opcode::alpha_blend": empty_args
            "opcode::no_dither": empty_args
            "opcode::dither": empty_args
            "opcode::no_noise": empty_args
            "opcode::noise": empty_args
            "opcode::set_dist_vel": empty_args
            "opcode::add_dist_vel_mag": empty_args
            "opcode::make_id": make_script_args
            "opcode::prim_blend_rand": empty_args
            "opcode::env_blend_rand": empty_args
            "opcode::set_unk_0b": set_unk_0b_args
            "opcode::set_vel_mag": set_vel_mag_args
            "opcode::mul_vel_axis": mul_vel_axis_args
            "opcode::set_attach_id": set_attach_id_args
            "opcode::color_blend_prim": color_blend_args
            "opcode::color_blend_env": color_blend_args
            "opcode::set_loop": set_loop_args
            "opcode::loop": empty_args
            "opcode::set_return": empty_args
            "opcode::return": empty_args
            "opcode::dead": empty_args
            "opcode::end": empty_args
    instances:
      base_opcode:
        value: |
          opcode_raw < 0x80 ? opcode::wait :
          opcode_raw < 0x88 ? opcode::set_pos :
          opcode_raw < 0x90 ? opcode::add_pos :
          opcode_raw < 0x98 ? opcode::set_vel :
          opcode_raw < 0xA0 ? opcode::add_vel :
          (opcode_raw & 0xF0) == 0xC0 ? opcode::color_blend_prim :
          (opcode_raw & 0xF0) == 0xD0 ? opcode::color_blend_env :
          opcode_raw
        enum: opcode

  # Empty args type for opcodes that take no parameters
  empty_args:
    doc: No parameters

  # Argument types for each instruction
  wait_args:
    doc: |
      Arguments for wait command (0x00-0x7F):
      - Bit 6 (E): Extra byte flag - adds (Extra << 5) to frame count
      - Bit 5 (X): Extra data flag - includes a data ID byte
      - Bits 0-4 (N): Base frame count

      Total frames = N + (Extra << 5) if E=1
    -webide-representation: "len:{frames:dec} idx:{data_id:dec}"
    instances:
      has_extra:
        value: (_parent.opcode_raw & 0x40) != 0
        doc: True if command includes extra frames byte
      has_data:
        value: (_parent.opcode_raw & 0x20) != 0
        doc: True if command includes data ID byte
      base_frames:
        value: _parent.opcode_raw & 0x1F
        doc: Base number of frames to wait (bits 0-4)
      frames:
        value: base_frames + extra_frames << 5
    seq:
      - id: extra_frames
        type: u1
        if: has_extra
        doc: Additional frames, shifted left by 5 bits
      - id: data_id
        type: u1
        if: has_data
        doc: Optional data identifier

  vector_args:
    doc: |
      Arguments for vector operations (position/velocity).
      The low 3 bits of the opcode determine which components (X,Y,Z) are present.
    instances:
      has_x:
        value: (_parent.opcode_raw & 0x01) != 0
        doc: True if X component is present
      has_y:
        value: (_parent.opcode_raw & 0x02) != 0
        doc: True if Y component is present
      has_z:
        value: (_parent.opcode_raw & 0x04) != 0
        doc: True if Z component is present
    seq:
      - id: x
        type: f4
        if: has_x
        doc: X component value (32-bit float)
      - id: y
        type: f4
        if: has_y
        doc: Y component value (32-bit float)
      - id: z
        type: f4
        if: has_z
        doc: Z component value (32-bit float)

  size_lerp_args:
    doc: Arguments for size interpolation
    -webide-representation: "steps:{steps} target:{target_size:dec}"
    seq:
      - id: steps
        type: var_length
        doc: Duration of size interpolation
      - id: target_size
        type: f4
        doc: Target size value (32-bit float)

  size_rand_args:
    -webide-representation: "steps:{steps} {base_size:dec} {scale:dec}"
    seq:
      - id: steps
        type: var_length
        doc: Duration of size interpolation
      - id: base_size
        type: f4
      - id: scale
        type: f4

  set_flags_args:
    -webide-representation: "{flags}"
    seq:
      - id: flags
        type: u1
        doc: Flag bits to set

  set_gravity_args:
    seq:
      - id: gravity
        type: f4
        doc: Gravity value (32-bit float)

  set_friction_args:
    seq:
      - id: friction
        type: f4
        doc: Friction value (32-bit float)

  make_script_args:
    seq:
      - id: script_id
        type: u2
        doc: ID of script to create particle from

  life_rand_args:
    seq:
      - id: base_life
        type: u2
        doc: Base lifetime value
      - id: random_range
        type: u2
        doc: Random range to add to base

  try_dead_rand_args:
    seq:
      - id: probability
        type: u1
        doc: Probability of destruction (0-255)

  add_vel_rand_args:
    seq:
      - id: x_range
        type: f4
        doc: Random range for X velocity
      - id: y_range
        type: f4
        doc: Random range for Y velocity
      - id: z_range
        type: f4
        doc: Random range for Z velocity

  set_vel_angle_args:
    -webide-representation: "{angle}"
    seq:
      - id: angle
        type: f4
        doc: Angle in radians (32-bit float)

  mul_vel_args:
    -webide-representation: "{factor:dec}"
    seq:
      - id: factor
        type: f4
        doc: Multiplication factor (32-bit float)

  set_unk_0b_args:
    seq:
      - id: base_value
        type: u1
        doc: Base value
      - id: random_range
        type: u1
        doc: Random range to add

  set_vel_mag_args:
    seq:
      - id: magnitude
        type: f4
        doc: Velocity magnitude (32-bit float)

  mul_vel_axis_args:
    seq:
      - id: x_factor
        type: f4
        doc: X velocity multiplier
      - id: y_factor
        type: f4
        doc: Y velocity multiplier
      - id: z_factor
        type: f4
        doc: Z velocity multiplier

  set_attach_id_args:
    seq:
      - id: attach_id
        type: u2
        doc: ID of object to attach to

  set_loop_args:
    seq:
      - id: count
        type: u1
        doc: Number of times to repeat the loop

  color_blend_args:
    doc: |
      Arguments for color blend operations.
      The low 4 bits of the opcode determine which color components are present:
      - Bit 0: Red component
      - Bit 1: Green component
      - Bit 2: Blue component
      - Bit 3: Alpha component
    -webide-representation: "r:{red:dec} g:{green:dec} b:{blue:dec} a:{alpha:dec} steps:{steps}"
    instances:
      has_red:
        value: (_parent.opcode_raw & 0x01) != 0
        doc: True if red component is present
      has_green:
        value: (_parent.opcode_raw & 0x02) != 0
        doc: True if green component is present
      has_blue:
        value: (_parent.opcode_raw & 0x04) != 0
        doc: True if blue component is present
      has_alpha:
        value: (_parent.opcode_raw & 0x08) != 0
        doc: True if alpha component is present
    seq:
      - id: steps
        type: var_length
        doc: Color interpolation duration
      - id: red
        type: u1
        if: has_red
        doc: Red component (0-255)
      - id: green
        type: u1
        if: has_green
        doc: Green component (0-255)
      - id: blue
        type: u1
        if: has_blue
        doc: Blue component (0-255)
      - id: alpha
        type: u1
        if: has_alpha
        doc: Alpha component (0-255)

  var_length:
    doc: |
      Variable length value encoding used for interpolation lengths.

      Format:
      - If first byte < 0x80: value = first byte + 1
      - If first byte >= 0x80: value = ((first byte & 0x7F) << 8) + second byte + 1
    -webide-representation: "{value:dec}"
    seq:
      - id: first_byte
        type: u1
        doc: First byte of encoded value
      - id: second_byte
        type: u1
        if: first_byte >= 0x80
        doc: Second byte (present if first byte >= 0x80)
    instances:
      value:
        value: |
          first_byte >= 0x80 ? 
            (((first_byte & 0x7F) << 8) | second_byte) + 1 :
            first_byte + 1
        doc: Decoded value

enums:
  opcode:
    0x00:
      id: wait
    # Vector operations
    0x80:
      id: set_pos
      doc: Set absolute particle position
    0x88:
      id: add_pos
      doc: Add to current position
    0x90:
      id: set_vel
      doc: Set absolute velocity
    0x98:
      id: add_vel
      doc: Add to current velocity
    # Value operations
    0xa0:
      id: set_size_lerp
      doc: Interpolate to new size over time
    0xa1:
      id: set_flags
      doc: Set particle flags directly
    0xa2:
      id: set_gravity
      doc: Set particle gravity value
    0xa3:
      id: set_friction
      doc: Set particle friction coefficient
    0xa4:
      id: make_script
      doc: Spawn child particle from script
    0xa5:
      id: make_generator
      doc: Create new particle generator
    0xa6:
      id: set_life_rand
      doc: Set random lifetime range
    0xa7:
      id: try_dead_rand
      doc: Random chance to destroy particle
    0xa8:
      id: add_vel_rand
      doc: Add random velocity components
    0xa9:
      id: set_vel_angle
      doc: Set velocity angle in radians
    0xaa:
      id: make_rand
      doc: Create particle with random properties
    0xab:
      id: mul_vel
      doc: Scale velocity uniformly
    0xac:
      id: set_size_rand
    # Flag operations
    0xad:
      id: set_flag_80
      doc: Set flag bit 0x80
    0xae:
      id: no_mask_st
      doc: Clear mask S/T flags
    0xaf:
      id: mask_s
      doc: Set mask S flag
    0xb0:
      id: mask_t
      doc: Set mask T flag
    0xb1:
      id: mask_st
      doc: Set both mask flags
    0xb2:
      id: alpha_blend
      doc: Set alpha blend flag
    0xb3:
      id: no_dither
      doc: Clear dither flag
    0xb4:
      id: dither
      doc: Set dither flag
    0xb5:
      id: no_noise
      doc: Clear noise flag
    0xb6:
      id: noise
      doc: Set noise flag
    # Advanced operations
    0xb7:
      id: set_dist_vel
      doc: Set velocity from distance
    0xb8:
      id: add_dist_vel_mag
      doc: Add distance magnitude to velocity
    0xb9:
      id: make_id
      doc: Make particle by ID
    0xba:
      id: prim_blend_rand
      doc: Random primitive color blend
    0xbb:
      id: env_blend_rand
      doc: Random environment color blend
    0xbc:
      id: set_unk_0b
      doc: Set unknown byte with random range
    0xbd:
      id: set_vel_mag
      doc: Set velocity magnitude
    0xbe:
      id: mul_vel_axis
      doc: Scale velocity per axis
    0xbf:
      id: set_attach_id
      doc: Set attach object ID
    # Color blend operations
    0xc0:
      id: color_blend_prim
      doc: Color blend command
    0xd0:
      id: color_blend_env
      doc: Color blend command
    # Flow control
    0xfa:
      id: set_loop
      doc: Start loop block
    0xfb:
      id: loop
      doc: Return to loop start
    0xfc:
      id: set_return
      doc: Set return point
    0xfd:
      id: return
      doc: Return to set point
    0xfe:
      id: dead
      doc: Destroy particle
    0xff:
      id: end
      doc: End script execution
