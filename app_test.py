from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.widget import Widget
from kivy.core.window import Window
from kivy.properties import NumericProperty, ListProperty
from kivy.clock import Clock
from kivy.graphics import Color, Ellipse, Line
from kivy.graphics.vertex_instructions import Mesh
from kivy.lang import Builder
import random
import math

# Define o layout em KV Language
KV = """
#:import random random
#:import math math

<ParticleOrb>:
    canvas.before:
        Color:
            rgba: 0, 0, 0, 1
        Rectangle:
            pos: self.pos
            size: self.size
    
    OrbCore:
        id: orb_core
        pos_hint: {'center_x': .5, 'center_y': .5}
        size_hint: None, None
        size: 100, 100

<OrbCore>:
    canvas:
        Color:
            rgba: .2, .5, 1, .8
        Ellipse:
            pos: self.pos
            size: self.size
"""


class Particle:
    def __init__(self, x, y, angle, speed):
        self.x = x
        self.y = y
        self.angle = angle
        self.speed = speed
        self.life = 1.0
        self.decay = random.uniform(0.02, 0.05)


class OrbCore(Widget):
    particles = []
    max_particles = 100

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_interval(self.update_particles, 1 / 60)

    def on_size(self, *args):
        self.center = (self.x + self.width / 2, self.y + self.height / 2)

    def create_particle(self):
        if len(self.particles) < self.max_particles:
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2, 5)
            particle = Particle(self.center_x, self.center_y, angle, speed)
            self.particles.append(particle)

    def update_particles(self, dt):
        # Criar novas partículas
        self.create_particle()

        # Atualizar partículas existentes
        for particle in self.particles[:]:
            particle.x += math.cos(particle.angle) * particle.speed
            particle.y += math.sin(particle.angle) * particle.speed
            particle.life -= particle.decay

            if particle.life <= 0:
                self.particles.remove(particle)

        # Redesenhar
        self.draw_particles()

    def draw_particles(self):
        self.canvas.after.clear()
        with self.canvas.after:
            for particle in self.particles:
                Color(0.2, 0.5, 1, particle.life)
                size = 10 * particle.life
                Ellipse(
                    pos=(particle.x - size / 2, particle.y - size / 2),
                    size=(size, size),
                )


class ParticleOrb(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.state = "idle"  # idle, thinking, responding, searching
        Clock.schedule_interval(self.update_state, 1 / 30)

    def set_state(self, state):
        self.state = state
        orb = self.ids.orb_core

        if state == "thinking":
            orb.max_particles = 200
        elif state == "responding":
            orb.max_particles = 150
        elif state == "searching":
            orb.max_particles = 300
        else:  # idle
            orb.max_particles = 100

    def update_state(self, dt):
        # Aqui você pode adicionar lógica para mudar cores/comportamento
        # baseado no estado atual
        pass


class OrbApp(App):
    def build(self):
        Builder.load_string(KV)
        Window.clearcolor = (0, 0, 0, 1)
        return ParticleOrb()


if __name__ == "__main__":
    OrbApp().run()
