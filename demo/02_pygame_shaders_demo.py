import random
import struct
from pathlib import Path

import moderngl
import numpy as np
import pygame
from pygame.locals import DOUBLEBUF, OPENGL

from natrix.core.fluid_simulator import FluidSimulator
from natrix.core.particle_area import ParticleArea
from natrix.core.utils.shaders_utils import read_shader_source

root_path = Path(__file__).parent / "shaders"

pygame.init()
pygame.display.set_mode((800, 600), DOUBLEBUF | OPENGL)

ctx = moderngl.create_context()

print(ctx.error)

canvas = np.array(
    [-1.0, -1.0, -1.0, 1.0, 1.0, -1.0, -1.0, 1.0, 1.0, 1.0, 1.0, -1.0]
).astype("f4")

prog = ctx.program(
    vertex_shader=read_shader_source("demo.VertexShader.vert", root_path),
    fragment_shader=read_shader_source("demo.FragmentShader.frag", root_path),
)

TEXTURE_SIZE = 512
pixels = np.zeros((TEXTURE_SIZE, TEXTURE_SIZE), dtype="f4")
texture = ctx.texture((TEXTURE_SIZE, TEXTURE_SIZE), 1, pixels.tobytes(), dtype="f4")
texture.filter = (moderngl.NEAREST, moderngl.NEAREST)
texture.swizzle = "RRR1"
texture.use()

vbo = ctx.buffer(struct.pack('12f', -1.0, -1.0, -1.0, 1.0, 1.0, -1.0, -1.0, 1.0, 1.0, 1.0, 1.0, -1.0))
vao = ctx.simple_vertex_array(prog, vbo, "pos")

fluid_simulator = FluidSimulator(ctx, 512, 512)
particle_area = ParticleArea(ctx, TEXTURE_SIZE, TEXTURE_SIZE)

fluid_simulator.vorticity = 10.0
fluid_simulator.viscosity = 0.000000000001
particle_area.dissipation = 0.99

clock = pygame.time.Clock()


def update(time_delta):
    vel_x = random.uniform(-0.08, 0.08)
    vel_y = random.uniform(-0.01, 0.2)
    strength = random.uniform(0.02, 0.1)

    fluid_simulator.add_velocity((0.5, 0.01), (vel_x, vel_y), 44.0)
    fluid_simulator.add_circle_obstacle((0.5, 0.5), 20)
    particle_area.add_particles((0.5, 0.1), 34.0, strength)

    fluid_simulator.update(time_delta)
    particle_area.update(time_delta)


running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    ctx.clear(0.9, 0.9, 0.9)
    update(clock.tick() / 1000)
    texture.write(particle_area.particles)
    vao.render()
    pygame.display.flip()

    print(clock.get_fps())
