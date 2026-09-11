"""
Earth Is Falling Around the Sun
--------------------------------
Manim Community Edition script for a 9:16 short-form physics reel.
Trimmed to ~25s and 30fps so it renders quickly on Replit's CPU.
Bump PIXEL dims / fps back up once you're rendering locally.

Physics: Newtonian gravity, a = -GM/r^2 * r_hat, integrated with
velocity-Verlet. The orbit is the literal output of the simulation
below, not a hand-drawn ellipse.

Render (Replit-friendly draft):
    manim -ql --fps 30 earth_falling.py EarthFallingAroundSun

Render (final, local machine with MiKTeX):
    manim -qh -r 1080,1920 --fps 60 earth_falling.py EarthFallingAroundSun

Dependencies:
    pip install manim
    A LaTeX distribution for the one MathTex line in the final frame.
"""

import numpy as np
from manim import *

# ---------------------------------------------------------------------------
# CONFIG -- vertical 1080x1920. fps kept at 30 by default to stay light
# on Replit; override with --fps 60 on the command line when you render
# the final pass locally.
# ---------------------------------------------------------------------------
config.pixel_width = 1080
config.pixel_height = 1920
config.frame_rate = 30
config.frame_height = 8.0
config.background_color = "#03040A"

G = 1.0
M = 1.0

VEL_VIS_SCALE = 1.0
ACC_VIS_SCALE = 3.0
VEL_ARROW_CAP = 0.9
ACC_ARROW_CAP = 0.9


def _unit(v):
    n = np.linalg.norm(v)
    return v / n if n > 1e-8 else v


class OrbitalSimulator:
    """Velocity-Verlet integrator for a test mass orbiting a fixed mass at the origin."""

    def __init__(self, r0, v0, dt=0.01, steps=3000):
        self.dt = dt
        self.steps = steps
        self.positions = np.zeros((steps, 2))
        self.velocities = np.zeros((steps, 2))
        self.accelerations = np.zeros((steps, 2))

        pos = np.array(r0, dtype=float)
        vel = np.array(v0, dtype=float)
        acc = self._acceleration(pos)

        for i in range(steps):
            self.positions[i] = pos
            self.velocities[i] = vel
            self.accelerations[i] = acc

            pos_next = pos + vel * dt + 0.5 * acc * dt ** 2
            acc_next = self._acceleration(pos_next)
            vel_next = vel + 0.5 * (acc + acc_next) * dt

            pos, vel, acc = pos_next, vel_next, acc_next

    @staticmethod
    def _acceleration(pos):
        r = np.linalg.norm(pos)
        r = max(r, 1e-3)
        return -G * M * pos / r ** 3


# Normalized initial conditions: Earth starts at aphelion (2.0, 0) with
# 85% of circular speed, which gives a stable, visually clear ellipse.
R0 = (2.0, 0.0)
V_CIRC = np.sqrt(G * M / R0[0])
V0 = (0.0, 0.85 * V_CIRC)


class EarthFallingAroundSun(MovingCameraScene):
    def construct(self):
        self.sim = OrbitalSimulator(r0=R0, v0=V0, dt=0.01, steps=3000)
        self.earth_index = ValueTracker(0)

        self.scene_1_hook()
        self.scene_2_misconception()
        self.scene_3_simulation_reveal()
        self.scene_4_falling_demo()
        self.scene_5_orbit_emerges()
        self.scene_6_big_reveal()
        self.final_frame()

    # -- trajectory lookups ------------------------------------------------
    def point_at(self, idx):
        i = int(np.clip(idx, 0, self.sim.steps - 1))
        x, y = self.sim.positions[i]
        return np.array([x, y, 0.0])

    def vel_at(self, idx):
        i = int(np.clip(idx, 0, self.sim.steps - 1))
        x, y = self.sim.velocities[i]
        return np.array([x, y, 0.0])

    def acc_at(self, idx):
        i = int(np.clip(idx, 0, self.sim.steps - 1))
        x, y = self.sim.accelerations[i]
        return np.array([x, y, 0.0])

    # -- visual object builders --------------------------------------------
    def _make_sun(self):
        core = Circle(radius=0.32, color=YELLOW, fill_color=YELLOW,
                       fill_opacity=1.0, stroke_width=0)
        glow_mid = Circle(radius=0.44, color=YELLOW, fill_color=YELLOW,
                           fill_opacity=0.25, stroke_width=0)
        glow_outer = Circle(radius=0.60, color=YELLOW, fill_color=YELLOW,
                             fill_opacity=0.12, stroke_width=0)
        return VGroup(glow_outer, glow_mid, core).move_to(ORIGIN)

    def _make_earth_dot(self):
        earth = Dot(radius=0.11, color=BLUE_D)
        earth.set_stroke(color=BLUE_B, width=1.5, opacity=0.6)
        return earth

    def _compute_velocity_arrow(self):
        idx = self.earth_index.get_value()
        pos = self.point_at(idx)
        vel = self.vel_at(idx)
        direction = _unit(vel)
        length = min(np.linalg.norm(vel) * VEL_VIS_SCALE, VEL_ARROW_CAP)
        end = pos + direction * length
        return Arrow(pos, end, buff=0, color=YELLOW, stroke_width=6,
                     max_tip_length_to_length_ratio=0.3)

    def _compute_velocity_label(self):
        arrow = self._compute_velocity_arrow()
        label = Text("velocity", font_size=26, color=YELLOW)
        direction = _unit(arrow.get_vector())
        label.move_to(arrow.get_end() + direction * 0.32)
        return label

    def _compute_acceleration_arrow(self):
        idx = self.earth_index.get_value()
        pos = self.point_at(idx)
        acc = self.acc_at(idx)
        direction = _unit(acc)
        length = min(np.linalg.norm(acc) * ACC_VIS_SCALE, ACC_ARROW_CAP)
        end = pos + direction * length
        return Arrow(pos, end, buff=0, color=RED, stroke_width=6,
                     max_tip_length_to_length_ratio=0.3)

    def _compute_acceleration_label(self):
        arrow = self._compute_acceleration_arrow()
        label = Text("gravity", font_size=26, color=RED)
        direction = _unit(arrow.get_vector())
        label.move_to(arrow.get_end() + direction * 0.32)
        return label

    def _clear_vectors(self):
        for m in (self.vel_arrow, self.vel_label, self.acc_arrow, self.acc_label):
            m.clear_updaters()
        self.play(
            FadeOut(self.vel_arrow), FadeOut(self.vel_label),
            FadeOut(self.acc_arrow), FadeOut(self.acc_label),
            run_time=0.3,
        )
        self.remove(self.vel_arrow, self.vel_label, self.acc_arrow, self.acc_label)

    def _show_vectors(self, run_time=0.6):
        self.vel_arrow = self._compute_velocity_arrow()
        self.vel_label = self._compute_velocity_label()
        self.acc_arrow = self._compute_acceleration_arrow()
        self.acc_label = self._compute_acceleration_label()
        self.play(
            GrowArrow(self.vel_arrow), FadeIn(self.vel_label),
            GrowArrow(self.acc_arrow), FadeIn(self.acc_label),
            run_time=run_time,
        )
        self.vel_arrow.add_updater(lambda m: m.become(self._compute_velocity_arrow()))
        self.vel_label.add_updater(lambda m: m.become(self._compute_velocity_label()))
        self.acc_arrow.add_updater(lambda m: m.become(self._compute_acceleration_arrow()))
        self.acc_label.add_updater(lambda m: m.become(self._compute_acceleration_label()))

    # -- SCENE 1: hook (~0-3s) -----------------------------------------------
    def scene_1_hook(self):
        earth_start = self.point_at(0)
        self.earth_dot = self._make_earth_dot()
        self.earth_dot.move_to(earth_start)
        self.earth_dot.add_updater(
            lambda m: m.move_to(self.point_at(self.earth_index.get_value()))
        )

        self.camera.frame.move_to(earth_start).scale(0.35)
        self.play(FadeIn(self.earth_dot, scale=0.5), run_time=0.3)

        text1 = Text("Earth is falling.", font_size=40, color=WHITE)
        text1.move_to(earth_start + UP * 0.9)
        self.play(Write(text1), run_time=0.6)

        text2 = Text("Right now.", font_size=40, color=WHITE)
        text2.next_to(text1, DOWN, buff=0.25)
        self.play(Write(text2), run_time=0.5)

        self.sun = self._make_sun()
        self.play(
            FadeOut(text1), FadeOut(text2),
            FadeIn(self.sun, scale=0.6),
            self.camera.frame.animate.move_to(ORIGIN).scale(1 / 0.35),
            run_time=1.0,
        )

    # -- SCENE 2: the misconception (~3-6s) -----------------------------------
    def scene_2_misconception(self):
        self._show_vectors(run_time=0.8)
        self.wait(0.5)
        caption = Text("Both happen at once.", font_size=28, color=GRAY_B)
        caption.to_edge(DOWN, buff=0.6)
        self.play(FadeIn(caption), run_time=0.3)
        self.wait(0.4)
        self.play(FadeOut(caption), run_time=0.3)
        self._clear_vectors()

    # -- SCENE 3: don't draw the orbit yet (~6-10s) --------------------------
    def scene_3_simulation_reveal(self):
        self.trace = TracedPath(
            self.earth_dot.get_center,
            stroke_color=BLUE_C,
            stroke_width=3,
            stroke_opacity=0.85,
        )
        self.add(self.trace)

        caption = Text("Gravity bends the path, step by step.",
                        font_size=28, color=GRAY_B)
        caption.to_edge(DOWN, buff=0.6)
        self.play(FadeIn(caption), run_time=0.3)
        self.play(self.earth_index.animate.set_value(700),
                   run_time=3.0, rate_func=linear)
        self.play(FadeOut(caption), run_time=0.3)

    # -- SCENE 4: show the "falling" part (~10-14s) ---------------------------
    def scene_4_falling_demo(self):
        self.play(self.trace.animate.set_stroke(opacity=0.15), run_time=0.3)
        self._show_vectors(run_time=0.5)

        caption = Text("If the sideways motion vanished...",
                        font_size=28, color=GRAY_B)
        caption.to_edge(DOWN, buff=0.6)
        self.play(FadeIn(caption), run_time=0.3)

        idx = self.earth_index.get_value()
        pos = self.point_at(idx)
        toward_sun = _unit(-pos)
        ghost_end = pos + toward_sun * 1.1
        ghost_line = DashedLine(pos, ghost_end, color=GRAY_C, stroke_width=3)
        ghost_dot = Dot(pos, radius=0.06, color=GRAY_C)

        self.play(Create(ghost_line), run_time=0.3)
        self.play(ghost_dot.animate.move_to(ghost_end),
                   run_time=0.6, rate_func=rush_into)
        self.play(FadeOut(ghost_line), FadeOut(ghost_dot),
                   FadeOut(caption), run_time=0.3)

        caption2 = Text("Its real velocity bends the fall into a curve.",
                         font_size=26, color=GRAY_B)
        caption2.to_edge(DOWN, buff=0.6)
        self.play(FadeIn(caption2), run_time=0.3)
        self.play(self.trace.animate.set_stroke(opacity=0.85), run_time=0.3)
        self.wait(0.4)
        self.play(FadeOut(caption2), run_time=0.3)
        self._clear_vectors()

    # -- SCENE 5: the orbit emerges (~14-17s) ---------------------------------
    def scene_5_orbit_emerges(self):
        self.play(
            self.earth_index.animate.set_value(2000),
            self.camera.frame.animate.scale(1.25),
            run_time=3.0,
            rate_func=linear,
        )

    # -- SCENE 6: the big reveal (~17-22s) ------------------------------------
    def scene_6_big_reveal(self):
        self.play(self.camera.frame.animate.scale(1.15).move_to(ORIGIN),
                   run_time=0.6)
        self.play(self.earth_index.animate.set_value(2250),
                   run_time=1.5, rate_func=linear)

        q_text = Text("So why doesn't Earth fall into the Sun?",
                       font_size=30, color=WHITE)
        q_text.to_edge(UP, buff=0.9)
        self.play(Write(q_text), run_time=0.7)

        a_text = Text("It IS falling.", font_size=36, color=YELLOW)
        a_text.move_to(q_text.get_center())
        self.play(FadeOut(q_text), FadeIn(a_text), run_time=0.4)

        b_text = Text("It just keeps missing.", font_size=36, color=YELLOW)
        b_text.move_to(a_text.get_center())
        self.play(FadeOut(a_text), FadeIn(b_text), run_time=0.4)

        self._show_vectors(run_time=0.5)
        self.wait(0.4)
        self.play(FadeOut(b_text), run_time=0.3)

        self.play(self.earth_index.animate.set_value(2500),
                   run_time=1.0, rate_func=linear)
        self._clear_vectors()

    # -- FINAL FRAME ----------------------------------------------------------
    def final_frame(self):
        self.earth_dot.clear_updaters()
        self.play(FadeOut(self.trace), run_time=0.3)
        self.play(FadeOut(self.sun), FadeOut(self.earth_dot), run_time=0.3)

        final_text = Text("An orbit is falling while constantly missing.",
                           font_size=32, color=WHITE)
        if final_text.width > config.frame_width - 0.6:
            final_text.set(width=config.frame_width - 0.6)

        sub_text = MathTex(r"\text{Newtonian gravity}", font_size=26, color=GRAY_B)
        sub_text.next_to(final_text, DOWN, buff=0.35)
        VGroup(final_text, sub_text).move_to(ORIGIN)

        self.play(Write(final_text), run_time=0.8)
        self.play(FadeIn(sub_text), run_time=0.4)
        self.wait(1.2)
