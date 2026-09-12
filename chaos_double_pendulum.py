"""
"Deterministic != Predictable" — a vertical (1080x1920, 60fps) Manim
Community Edition animation using a numerically-integrated double
pendulum to explain sensitive dependence on initial conditions.

Render with, e.g.:
    manim -pqh chaos_double_pendulum.py DeterministicNotPredictable

Requires only: manim (Community Edition) and NumPy. No LaTeX, no
external images/fonts/assets, no network access.
"""

from manim import *
import numpy as np

# ==========================================================================
# SECTION 1 — GLOBAL CONFIG (portrait 1080x1920 @ 60fps)
# ==========================================================================
config.pixel_width = 1080
config.pixel_height = 1920
config.frame_rate = 60
config.frame_height = 8.0
config.frame_width = config.frame_height * config.pixel_width / config.pixel_height  # 4.5
config.background_color = "#050508"

BG = "#050508"
CYAN = "#2BE8FF"
MAGENTA = "#FF3EC9"
PURPLE = "#8B6BFF"
GOLD = "#FFD166"
DIM = "#4A4A57"
WHITE_SOFT = "#EAEAF2"

SAFE_W = config.frame_width * 0.86  # portrait-safe column, ~60-86% of frame


def scene_title(s, size=28, color=WHITE_SOFT):
    """A scene title that always fits inside the portrait safe column."""
    t = Text(s, font_size=size, color=color, weight=BOLD)
    if t.width > SAFE_W:
        t.set(width=SAFE_W)
    return t


def wrap_body(s, size=24, color=WHITE_SOFT, weight=NORMAL, line_spacing=1.2):
    t = Text(s, font_size=size, color=color, weight=weight, line_spacing=line_spacing)
    if t.width > SAFE_W * 0.96:
        t.set(width=SAFE_W * 0.96)
    return t


def glow_line(start, end, color, width=4, glow_layers=3):
    """A worldline-style stroke with a soft additive glow, built only
    from Manim primitives (no external shaders or assets)."""
    group = VGroup()
    for i in range(glow_layers, 0, -1):
        layer = Line(start, end, color=color)
        layer.set_stroke(width=width + i * 5, opacity=0.10)
        group.add(layer)
    core = Line(start, end, color=color)
    core.set_stroke(width=width, opacity=1.0)
    group.add(core)
    return group


def glow_dot(point, color, radius=0.07):
    group = VGroup()
    for r_mult, op in [(3.0, 0.08), (1.9, 0.16), (1.0, 1.0)]:
        group.add(Dot(point, radius=radius * r_mult, color=color, fill_opacity=op))
    return group


# ==========================================================================
# SECTION 2 — PHYSICS SIMULATION (pure NumPy, 4th-order Runge-Kutta)
# ==========================================================================
def rk4_step(deriv, state, t, dt, params):
    """One classical RK4 step for an arbitrary first-order ODE system
    dstate/dt = deriv(state, t, params)."""
    k1 = deriv(state, t, params)
    k2 = deriv(state + 0.5 * dt * k1, t + 0.5 * dt, params)
    k3 = deriv(state + 0.5 * dt * k2, t + 0.5 * dt, params)
    k4 = deriv(state + dt * k3, t + dt, params)
    return state + (dt / 6.0) * (k1 + 2.0 * k2 + 2.0 * k3 + k4)


def double_pendulum_deriv(state, t, params):
    """Equations of motion for a planar double pendulum (two point
    masses on massless rigid rods), derived from the Lagrangian.
    state = [theta1, omega1, theta2, omega2]."""
    theta1, w1, theta2, w2 = state
    m1, m2, L1, L2, g = params
    delta = theta1 - theta2
    den = 2.0 * m1 + m2 - m2 * np.cos(2.0 * delta)

    den1 = L1 * den
    dw1 = (
        -g * (2.0 * m1 + m2) * np.sin(theta1)
        - m2 * g * np.sin(theta1 - 2.0 * theta2)
        - 2.0 * np.sin(delta) * m2 * (w2 ** 2 * L2 + w1 ** 2 * L1 * np.cos(delta))
    ) / den1

    den2 = L2 * den
    dw2 = (
        2.0 * np.sin(delta)
        * (w1 ** 2 * L1 * (m1 + m2) + g * (m1 + m2) * np.cos(theta1)
           + w2 ** 2 * L2 * m2 * np.cos(delta))
    ) / den2

    return np.array([w1, dw1, w2, dw2])


def single_pendulum_deriv(state, t, params):
    """Equations of motion for a simple (single, undamped) pendulum:
    theta'' = -(g / L) * sin(theta). state = [theta, omega]."""
    theta, w = state
    L, g = params
    return np.array([w, -(g / L) * np.sin(theta)])


def simulate(deriv, state0, t_max, dt, params):
    """Precompute a full trajectory with fixed-step RK4. Returns an
    (n, len(state0)) array of states, one row per time step."""
    n_steps = int(round(t_max / dt)) + 1
    states = np.zeros((n_steps, len(state0)))
    states[0] = state0
    t = 0.0
    for i in range(1, n_steps):
        states[i] = rk4_step(deriv, states[i - 1], t, dt, params)
        t += dt
    return states


def double_pendulum_positions(states, L1, L2):
    theta1 = states[:, 0]
    theta2 = states[:, 2]
    x1 = L1 * np.sin(theta1)
    y1 = -L1 * np.cos(theta1)
    x2 = x1 + L2 * np.sin(theta2)
    y2 = y1 - L2 * np.cos(theta2)
    return x1, y1, x2, y2


# --- Physical parameters -------------------------------------------------
M1, M2 = 1.0, 1.0
L1, L2 = 1.0, 1.0
G = 9.8
PARAMS = (M1, M2, L1, L2, G)

DT = 0.001
T_MAX = 14.0          # seconds of physical time simulated
DELTA_THETA = 0.001 * np.pi / 180.0   # 0.001 degrees, in radians

THETA1_0 = 2.0         # radians (~114.6 degrees) - energetic, chaotic regime
THETA2_0 = 2.0

state0_A = np.array([THETA1_0, 0.0, THETA2_0, 0.0])
state0_B = np.array([THETA1_0 + DELTA_THETA, 0.0, THETA2_0, 0.0])

# Two trajectories, identical equations, near-identical initial angle.
states_A = simulate(double_pendulum_deriv, state0_A, T_MAX, DT, PARAMS)
states_B = simulate(double_pendulum_deriv, state0_B, T_MAX, DT, PARAMS)

x1A, y1A, x2A, y2A = double_pendulum_positions(states_A, L1, L2)
x1B, y1B, x2B, y2B = double_pendulum_positions(states_B, L1, L2)

W1A, W1B = states_A[:, 1], states_B[:, 1]
THETA1_A, THETA1_B = states_A[:, 0], states_B[:, 0]

# A single (non-chaotic) pendulum, for the calm opening comparison.
SINGLE_L, SINGLE_G = 1.2, 9.8
single_state0 = np.array([0.9, 0.0])
single_states = simulate(single_pendulum_deriv, single_state0, 6.0, DT, (SINGLE_L, SINGLE_G))
x_single = SINGLE_L * np.sin(single_states[:, 0])
y_single = -SINGLE_L * np.cos(single_states[:, 0])


def idx_at(t_val, dt=DT, n_max=None):
    i = int(round(t_val / dt))
    if n_max is not None:
        i = min(i, n_max - 1)
    return max(i, 0)


# ==========================================================================
# SECTION 3 — VISUALIZATION HELPERS (physics coords -> screen coords)
# ==========================================================================
PIVOT = np.array([0.0, 1.55, 0.0])
DRAW_SCALE = 0.85


def p2s(x, y):
    """Map a physics-space (x, y) offset from the pivot to a screen
    point. Manim's +y is up, matching our y = -L*cos(theta) convention
    (theta = 0 hangs straight down), so no axis flip is needed."""
    return PIVOT + DRAW_SCALE * np.array([x, y, 0.0])


def build_pendulum(x1, y1, x2, y2, idx, color, rod_width=4, bob_r=0.095, glow=True):
    idx = min(idx, len(x1) - 1)
    p0 = PIVOT
    p1 = p2s(x1[idx], y1[idx])
    p2 = p2s(x2[idx], y2[idx])
    if glow:
        rod1 = glow_line(p0, p1, color, width=rod_width, glow_layers=2)
        rod2 = glow_line(p1, p2, color, width=rod_width, glow_layers=2)
    else:
        rod1 = Line(p0, p1, color=color, stroke_width=rod_width)
        rod2 = Line(p1, p2, color=color, stroke_width=rod_width)
    bob1 = Dot(p1, radius=bob_r * 0.75, color=color, fill_opacity=1.0)
    bob2 = Dot(p2, radius=bob_r, color=color, fill_opacity=1.0)
    return VGroup(rod1, rod2, bob1, bob2)


def build_single_pendulum(x, y, idx, color, rod_width=4, bob_r=0.11):
    idx = min(idx, len(x) - 1)
    p0 = PIVOT
    p1 = p2s(x[idx], y[idx])
    rod = glow_line(p0, p1, color, width=rod_width, glow_layers=2)
    bob = Dot(p1, radius=bob_r, color=color, fill_opacity=1.0)
    return VGroup(rod, bob)


# ==========================================================================
# SECTION 4 — MANIM SCENE
# ==========================================================================
class DeterministicNotPredictable(MovingCameraScene):
    """Eight-beat explainer: a deterministic system that is still
    impossible to predict, told through a chaotic double pendulum."""

    def construct(self):
        self.camera.background_color = BG
        self.scene_1_hook()
        self.scene_2_single_pendulum()
        self.scene_3_double_pendulum()
        self.scene_4_two_systems()
        self.scene_5_divergence()
        self.scene_6_phase_space()
        self.scene_7_lyapunov()
        self.scene_8_final_punch()

    # ----------------------------------------------------------------
    # SCENE 1 — HOOK
    # ----------------------------------------------------------------
    def scene_1_hook(self):
        l1 = wrap_body("Same laws.", size=34, color=WHITE_SOFT, weight=BOLD)
        l2 = wrap_body("Almost the same starting point.", size=34, color=WHITE_SOFT, weight=BOLD)
        l3 = wrap_body("Completely different future.", size=34, color=CYAN, weight=BOLD)
        group = VGroup(l1, l2, l3).arrange(DOWN, buff=0.35)
        group.move_to(ORIGIN)

        self.play(FadeIn(l1, shift=UP * 0.2), run_time=0.9)
        self.wait(0.5)
        self.play(FadeIn(l2, shift=UP * 0.2), run_time=0.9)
        self.wait(0.5)
        self.play(FadeIn(l3, shift=UP * 0.2), run_time=0.9)
        self.wait(1.1)
        self.play(FadeOut(group), run_time=0.7)

        not_random = wrap_body("This isn't randomness.", size=36, color=WHITE_SOFT, weight=BOLD)
        self.play(FadeIn(not_random), run_time=0.9)
        self.wait(1.2)
        self.play(FadeOut(not_random), run_time=0.6)
        self.wait(0.3)

        chaos = Text("It's chaos.", font_size=58, color=MAGENTA, weight=BOLD)
        if chaos.width > SAFE_W:
            chaos.set(width=SAFE_W)
        self.play(FadeIn(chaos, scale=1.15), run_time=1.0)
        self.wait(1.2)
        self.play(FadeOut(chaos), run_time=0.7)

    # ----------------------------------------------------------------
    # SCENE 2 — ONE PENDULUM (predictable, regular)
    # ----------------------------------------------------------------
    def scene_2_single_pendulum(self):
        title = scene_title("A single pendulum", size=28)
        title.to_edge(UP, buff=0.7)
        self.play(Write(title), run_time=0.8)

        pivot_dot = Dot(PIVOT, radius=0.05, color=WHITE_SOFT)
        self.play(FadeIn(pivot_dot), run_time=0.4)

        t_tracker = ValueTracker(0.0)
        n_single = len(x_single)

        pendulum = always_redraw(
            lambda: build_single_pendulum(
                x_single, y_single, idx_at(t_tracker.get_value(), n_max=n_single), CYAN,
            )
        )
        trail = TracedPath(
            lambda: p2s(
                x_single[idx_at(t_tracker.get_value(), n_max=n_single)],
                y_single[idx_at(t_tracker.get_value(), n_max=n_single)],
            ),
            stroke_color=CYAN, stroke_width=2, stroke_opacity=0.5,
            dissipating_time=1.0,
        )

        self.add(trail, pendulum)

        caption = wrap_body(
            "Predictable. Regular. Easy to forecast.",
            size=24, color=WHITE_SOFT,
        )
        caption.to_edge(DOWN, buff=1.0)
        self.play(FadeIn(caption), run_time=0.7)

        self.play(t_tracker.animate.set_value(5.4), run_time=4.2, rate_func=linear)
        self.wait(0.3)

        self.play(
            FadeOut(title), FadeOut(caption), FadeOut(pendulum),
            FadeOut(trail), FadeOut(pivot_dot),
            run_time=0.7,
        )

    # ----------------------------------------------------------------
    # SCENE 3 — DOUBLE PENDULUM (still deterministic)
    # ----------------------------------------------------------------
    def scene_3_double_pendulum(self):
        title = scene_title("Add a second joint", size=28)
        title.to_edge(UP, buff=0.7)
        self.play(Write(title), run_time=0.8)

        pivot_dot = Dot(PIVOT, radius=0.05, color=WHITE_SOFT)

        idx0 = 0
        p0 = PIVOT
        p1 = p2s(x1A[idx0], y1A[idx0])
        rod1 = glow_line(p0, p1, CYAN, width=4, glow_layers=2)
        bob1 = Dot(p1, radius=0.075, color=CYAN)

        self.play(FadeIn(pivot_dot), Create(rod1), FadeIn(bob1), run_time=0.9)
        self.wait(0.3)

        # attach the second rod and mass
        p2 = p2s(x2A[idx0], y2A[idx0])
        rod2 = glow_line(p1, p2, CYAN, width=4, glow_layers=2)
        bob2 = Dot(p2, radius=0.095, color=CYAN)
        self.play(Create(rod2), FadeIn(bob2), run_time=0.8)

        label = wrap_body("deterministic", size=24, color=GOLD, weight=BOLD)
        label.next_to(pivot_dot, RIGHT, buff=0.25).shift(UP * 0.1)
        self.play(FadeIn(label, shift=RIGHT * 0.15), run_time=0.6)
        self.wait(0.6)

        self.remove(rod1, rod2, bob1, bob2)

        t_tracker = ValueTracker(0.0)
        n_a = len(x1A)
        pendulum = always_redraw(
            lambda: build_pendulum(
                x1A, y1A, x2A, y2A, idx_at(t_tracker.get_value(), n_max=n_a), CYAN,
            )
        )
        trail = TracedPath(
            lambda: p2s(
                x2A[idx_at(t_tracker.get_value(), n_max=n_a)],
                y2A[idx_at(t_tracker.get_value(), n_max=n_a)],
            ),
            stroke_color=CYAN, stroke_width=2, stroke_opacity=0.55,
            dissipating_time=1.1,
        )
        self.add(trail, pendulum)

        self.play(t_tracker.animate.set_value(3.0), run_time=2.6, rate_func=linear)
        self.wait(0.3)

        self.play(
            FadeOut(title), FadeOut(label), FadeOut(pendulum),
            FadeOut(trail), FadeOut(pivot_dot),
            run_time=0.7,
        )

    # ----------------------------------------------------------------
    # SCENE 4 — TWO NEARLY IDENTICAL SYSTEMS
    # ----------------------------------------------------------------
    def scene_4_two_systems(self):
        title = scene_title("Two nearly identical starts", size=26)
        title.to_edge(UP, buff=0.7)
        self.play(Write(title), run_time=0.8)

        note = wrap_body(
            "System A (cyan) and System B (magenta)\nstart almost exactly the same.",
            size=22, color=WHITE_SOFT,
        )
        note.next_to(title, DOWN, buff=0.35)
        self.play(FadeIn(note), run_time=0.7)

        pivot_dot = Dot(PIVOT, radius=0.05, color=WHITE_SOFT)
        pend_a = build_pendulum(x1A, y1A, x2A, y2A, 0, CYAN)
        pend_b = build_pendulum(x1B, y1B, x2B, y2B, 0, MAGENTA)

        self.play(FadeIn(pivot_dot), FadeIn(pend_a), run_time=0.7)
        self.play(FadeIn(pend_b), run_time=0.7)
        self.wait(0.6)

        # --- magnified schematic of the tiny initial angle gap ---
        inset_center = np.array([0.0, -2.15, 0.0])
        inset_r = 0.95
        inset_circle = Circle(radius=inset_r, color=DIM, stroke_width=2)
        inset_circle.move_to(inset_center)

        mag_len = 0.8
        base = inset_center + DOWN * 0.1
        dir_a = np.array([np.sin(THETA1_0), -np.cos(THETA1_0), 0.0])
        dir_b = np.array([np.sin(THETA1_0 + DELTA_THETA), -np.cos(THETA1_0 + DELTA_THETA), 0.0])
        # exaggerate the angular gap ~8000x so a 0.001-degree difference
        # becomes a clearly visible wedge at this drawing scale
        exaggeration = 8000.0
        ang_a = np.arctan2(dir_a[0], -dir_a[1])
        ang_b = ang_a + (np.arctan2(dir_b[0], -dir_b[1]) - ang_a) * exaggeration
        dir_b_vis = np.array([np.sin(ang_b), -np.cos(ang_b), 0.0])

        line_a = glow_line(base, base + mag_len * dir_a, CYAN, width=4, glow_layers=1)
        line_b = glow_line(base, base + mag_len * dir_b_vis, MAGENTA, width=4, glow_layers=1)
        hinge = Dot(base, radius=0.04, color=WHITE_SOFT)

        delta_label = wrap_body("\u0394\u03b8 = 0.001\u00b0", size=22, color=GOLD, weight=BOLD)
        delta_label.next_to(inset_circle, UP, buff=0.16)
        exag_label = wrap_body("(gap magnified to be visible)", size=15, color=DIM)
        exag_label.next_to(inset_circle, DOWN, buff=0.16)

        self.play(Create(inset_circle), run_time=0.6)
        self.play(Create(line_a), Create(line_b), FadeIn(hinge), run_time=0.8)
        self.play(FadeIn(delta_label), FadeIn(exag_label), run_time=0.6)
        self.wait(1.6)

        self.play(
            *[FadeOut(m) for m in [
                title, note, pend_a, pend_b, pivot_dot, inset_circle,
                line_a, line_b, hinge, delta_label, exag_label,
            ]],
            run_time=0.8,
        )

    # ----------------------------------------------------------------
    # SCENE 5 — DIVERGENCE
    # ----------------------------------------------------------------
    def scene_5_divergence(self):
        title = scene_title("Let them run", size=28)
        title.to_edge(UP, buff=0.7)
        self.play(Write(title), run_time=0.7)

        pivot_dot = Dot(PIVOT, radius=0.05, color=WHITE_SOFT)

        t_tracker = ValueTracker(0.0)
        n_a, n_b = len(x1A), len(x1B)

        pend_a = always_redraw(
            lambda: build_pendulum(
                x1A, y1A, x2A, y2A, idx_at(t_tracker.get_value(), n_max=n_a), CYAN,
            )
        )
        pend_b = always_redraw(
            lambda: build_pendulum(
                x1B, y1B, x2B, y2B, idx_at(t_tracker.get_value(), n_max=n_b), MAGENTA,
            )
        )
        trail_a = TracedPath(
            lambda: p2s(
                x2A[idx_at(t_tracker.get_value(), n_max=n_a)],
                y2A[idx_at(t_tracker.get_value(), n_max=n_a)],
            ),
            stroke_color=CYAN, stroke_width=3, stroke_opacity=0.65, dissipating_time=1.6,
        )
        trail_b = TracedPath(
            lambda: p2s(
                x2B[idx_at(t_tracker.get_value(), n_max=n_b)],
                y2B[idx_at(t_tracker.get_value(), n_max=n_b)],
            ),
            stroke_color=MAGENTA, stroke_width=3, stroke_opacity=0.65, dissipating_time=1.6,
        )

        timer_label = always_redraw(
            lambda: wrap_body(f"t = {t_tracker.get_value():4.1f} s", size=24, color=WHITE_SOFT)
            .to_edge(DOWN, buff=0.7)
        )

        self.add(trail_a, trail_b, pend_a, pend_b, pivot_dot, timer_label)

        stage1 = wrap_body("almost identical", size=22, color=WHITE_SOFT)
        stage1.next_to(title, DOWN, buff=0.35)
        self.play(FadeIn(stage1), run_time=0.6)
        self.play(t_tracker.animate.set_value(3.0), run_time=2.8, rate_func=linear)

        stage2 = wrap_body("slightly different", size=22, color=GOLD)
        stage2.move_to(stage1)
        self.play(FadeOut(stage1), FadeIn(stage2), run_time=0.5)
        self.play(t_tracker.animate.set_value(7.0), run_time=3.6, rate_func=linear)

        stage3 = wrap_body("dramatically different", size=22, color=MAGENTA, weight=BOLD)
        stage3.move_to(stage2)
        self.play(FadeOut(stage2), FadeIn(stage3), run_time=0.5)
        self.play(t_tracker.animate.set_value(12.5), run_time=5.4, rate_func=linear)
        self.wait(0.5)

        self.play(
            FadeOut(title), FadeOut(stage3), FadeOut(pend_a), FadeOut(pend_b),
            FadeOut(trail_a), FadeOut(trail_b), FadeOut(pivot_dot), FadeOut(timer_label),
            run_time=0.8,
        )

        # remember where the systems ended up, for later scenes
        self.t_after_divergence = 12.5

    # ----------------------------------------------------------------
    # SCENE 6 — PHASE SPACE (theta_1 vs omega_1)
    # ----------------------------------------------------------------
    def scene_6_phase_space(self):
        title = scene_title("The same split, in phase space", size=24)
        title.to_edge(UP, buff=0.7)
        self.play(Write(title), run_time=0.8)

        n_show = idx_at(self.t_after_divergence, n_max=len(x1A))
        step = max(n_show // 500, 1)  # subsample for a light, smooth curve
        theta1_a_s = THETA1_A[0:n_show:step]
        w1_a_s = W1A[0:n_show:step]
        theta1_b_s = THETA1_B[0:n_show:step]
        w1_b_s = W1B[0:n_show:step]

        axes = Axes(
            x_range=[-4, 4, 2],
            y_range=[-8, 8, 4],
            x_length=3.6,
            y_length=4.6,
            axis_config={"color": DIM, "stroke_width": 2, "include_tip": True,
                         "tip_width": 0.15, "tip_height": 0.15},
        )
        axes.move_to(ORIGIN).shift(DOWN * 0.35)
        x_lbl = Text("\u03b8\u2081", font_size=26, color=DIM).next_to(axes.x_axis.get_end(), RIGHT, buff=0.1)
        y_lbl = Text("\u03c9\u2081", font_size=26, color=DIM).next_to(axes.y_axis.get_end(), UP, buff=0.1)

        self.play(Create(axes), FadeIn(x_lbl), FadeIn(y_lbl), run_time=1.0)

        reveal = ValueTracker(1)
        n_pts = len(theta1_a_s)

        def curve_a():
            k = max(int(reveal.get_value()), 2)
            k = min(k, n_pts)
            pts = [axes.c2p(theta1_a_s[i], w1_a_s[i]) for i in range(k)]
            return VMobject(color=CYAN, stroke_width=3).set_points_as_corners(pts)

        def curve_b():
            k = max(int(reveal.get_value()), 2)
            k = min(k, n_pts)
            pts = [axes.c2p(theta1_b_s[i], w1_b_s[i]) for i in range(k)]
            return VMobject(color=MAGENTA, stroke_width=3).set_points_as_corners(pts)

        path_a = always_redraw(curve_a)
        path_b = always_redraw(curve_b)
        self.add(path_a, path_b)

        self.play(reveal.animate.set_value(n_pts), run_time=4.0, rate_func=linear)
        self.wait(0.6)

        caption = wrap_body(
            "Two curves from identical physics,\nseparating in state space.",
            size=22, color=WHITE_SOFT,
        )
        caption.to_edge(DOWN, buff=0.8)
        self.play(FadeIn(caption), run_time=0.7)
        self.wait(1.5)

        self.play(
            *[FadeOut(m) for m in [title, axes, x_lbl, y_lbl, path_a, path_b, caption]],
            run_time=0.8,
        )

    # ----------------------------------------------------------------
    # SCENE 7 — LYAPUNOV EXPONENT (conceptual, not screen-filling)
    # ----------------------------------------------------------------
    def scene_7_lyapunov(self):
        title = scene_title("Why it explodes so fast", size=26)
        title.to_edge(UP, buff=0.7)
        self.play(Write(title), run_time=0.8)

        def sym(s, color=WHITE_SOFT, italic=True, size=46):
            return Text(s, font_size=size, color=color,
                        slant=ITALIC if italic else NORMAL, weight=BOLD)

        d_x = sym("\u03b4x(t)")
        approx = sym("\u2248", italic=False)
        d_x0 = sym("\u03b4x\u2080")
        exp_term = sym("e", color=GOLD)
        lam = sym("\u03bbt", color=GOLD, size=32)

        exp_group = VGroup(exp_term, lam).arrange(RIGHT, buff=0.03, aligned_edge=DOWN)
        lam.shift(UP * 0.32)

        eq = VGroup(d_x, approx, d_x0, exp_group).arrange(RIGHT, buff=0.16)
        if eq.width > SAFE_W:
            eq.set(width=SAFE_W)
        eq.next_to(title, DOWN, buff=0.6)
        self.play(Write(eq), run_time=1.1)
        self.wait(0.5)

        explain = wrap_body(
            "\u03bb is the Lyapunov exponent.\nWhen \u03bb > 0, tiny gaps grow exponentially.",
            size=23, color=WHITE_SOFT,
        )
        explain.next_to(eq, DOWN, buff=0.5)
        self.play(FadeIn(explain, shift=UP * 0.2), run_time=0.8)
        self.wait(1.2)

        # small illustrative exponential-growth curve (schematic, not a fit)
        axes = Axes(
            x_range=[0, 5, 1], y_range=[0, 8, 2],
            x_length=3.2, y_length=2.6,
            axis_config={"color": DIM, "stroke_width": 2, "include_tip": True,
                         "tip_width": 0.12, "tip_height": 0.12},
        )
        axes.next_to(explain, DOWN, buff=0.55)
        curve = axes.plot(lambda x: 0.25 * np.exp(0.75 * x), x_range=[0, 4.35], color=GOLD)
        curve.set_stroke(width=4)
        curve_lbl = wrap_body("separation", size=18, color=GOLD)
        curve_lbl.next_to(axes, UP, buff=0.12)

        self.play(Create(axes), run_time=0.7)
        self.play(Create(curve), FadeIn(curve_lbl), run_time=1.1)
        self.wait(1.3)

        caveat = wrap_body(
            "This is the characteristic shape near\nchaos \u2014 not an exact law for every system.",
            size=18, color=DIM,
        )
        caveat.next_to(axes, DOWN, buff=0.3)
        self.play(FadeIn(caveat), run_time=0.7)
        self.wait(1.6)

        self.play(
            *[FadeOut(m) for m in [title, eq, explain, axes, curve, curve_lbl, caveat]],
            run_time=0.8,
        )

    # ----------------------------------------------------------------
    # SCENE 8 — FINAL PUNCH
    # ----------------------------------------------------------------
    def scene_8_final_punch(self):
        pivot_dot = Dot(PIVOT, radius=0.05, color=WHITE_SOFT)
        idx_final = idx_at(12.0, n_max=len(x1A))
        pend_a = build_pendulum(x1A, y1A, x2A, y2A, idx_final, CYAN)
        idx_final_b = idx_at(12.0, n_max=len(x1B))
        pend_b = build_pendulum(x1B, y1B, x2B, y2B, idx_final_b, MAGENTA)

        self.play(FadeIn(pivot_dot), FadeIn(pend_a), FadeIn(pend_b), run_time=0.8)
        self.wait(1.0)

        line1 = wrap_body("Deterministic \u2260 predictable", size=34, color=WHITE_SOFT, weight=BOLD)
        line1.to_edge(UP, buff=0.9)
        self.play(FadeIn(line1, shift=UP * 0.15), run_time=0.9)
        self.wait(1.4)

        line2 = wrap_body(
            "Chaos is what happens when tiny\ndifferences matter enormously.",
            size=26, color=MAGENTA, weight=BOLD,
        )
        line2.to_edge(DOWN, buff=1.1)
        self.play(FadeIn(line2, shift=UP * 0.15), run_time=0.9)
        self.wait(2.0)

        self.play(
            *[FadeOut(m) for m in [pivot_dot, pend_a, pend_b, line1, line2]],
            run_time=1.0,
        )
        self.wait(0.4)
