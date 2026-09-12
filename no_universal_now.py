"""
"There Is No Universal NOW" — a vertical (1080x1920, 60fps) Manim Community
Edition animation explaining the relativity of simultaneity.

Render with, e.g.:
    manim -pqh no_universal_now.py NoUniversalNow

Requires: manim (Community Edition) and a LaTeX distribution for MathTex.
No external images, fonts, or network access are used.
"""

from manim import *
import numpy as np

# --------------------------------------------------------------------------
# GLOBAL CONFIG — portrait 1080x1920 @ 60fps
# --------------------------------------------------------------------------
config.pixel_width = 1080
config.pixel_height = 1920
config.frame_rate = 60
config.frame_height = 8.0
config.frame_width = config.frame_height * config.pixel_width / config.pixel_height  # 4.5
config.background_color = "#050508"

# --------------------------------------------------------------------------
# PALETTE — cosmic dark / cyan / purple / magenta, matching brand identity
# --------------------------------------------------------------------------
BG = "#050508"
CYAN = "#2BE8FF"
MAGENTA = "#FF3EC9"
PURPLE = "#8B6BFF"
GOLD = "#FFD166"
DIM = "#4A4A57"
FUTURE_FILL = "#1B2A55"
PAST_FILL = "#2A1B4A"
ELSEWHERE_FILL = "#151522"
WHITE_SOFT = "#EAEAF2"

# Safe center column for portrait composition (~60% of frame width)
SAFE_W = config.frame_width * 0.86


def glow_line(start, end, color, width=4, glow_layers=3):
    """A worldline/light-ray with a soft additive glow, built from
    Manim primitives only (no external shaders/assets)."""
    group = VGroup()
    for i in range(glow_layers, 0, -1):
        layer = Line(start, end, color=color)
        layer.set_stroke(width=width + i * 5, opacity=0.10)
        group.add(layer)
    core = Line(start, end, color=color)
    core.set_stroke(width=width, opacity=1.0)
    group.add(core)
    return group


def scene_title(s, size=30, color=WHITE_SOFT):
    """A scene title that always fits inside the portrait safe column,
    shrinking to fit rather than spilling past the frame edges."""
    t = Text(s, font_size=size, color=color, weight=BOLD)
    if t.width > SAFE_W:
        t.set(width=SAFE_W)
    return t


def glow_dot(point, color, radius=0.07):
    group = VGroup()
    for i, (r_mult, op) in enumerate([(3.2, 0.08), (2.0, 0.16), (1.0, 1.0)]):
        group.add(Dot(point, radius=radius * r_mult, color=color, fill_opacity=op))
    return group


class NoUniversalNow(MovingCameraScene):
    """Six-beat explainer on the relativity of simultaneity."""

    def construct(self):
        self.camera.background_color = BG
        self.scene_1_hook()
        self.scene_2_spacetime()
        self.scene_3_observer_a()
        self.scene_4_observer_b()
        self.scene_5_equation()
        self.scene_6_final_punch()

    # ----------------------------------------------------------------
    # SCENE 1 — HOOK
    # ----------------------------------------------------------------
    def scene_1_hook(self):
        line1 = Text("There is no", font_size=52, color=WHITE_SOFT, weight=BOLD)
        line2 = Text("universal NOW.", font_size=52, color=CYAN, weight=BOLD)
        headline = VGroup(line1, line2).arrange(DOWN, buff=0.25)
        headline.set(width=SAFE_W)

        # faint drifting starfield dots for atmosphere (cheap, CI-safe)
        rng = np.random.default_rng(7)
        stars = VGroup(*[
            Dot(
                point=[rng.uniform(-SAFE_W / 2, SAFE_W / 2),
                       rng.uniform(-3.6, 3.6), 0],
                radius=rng.uniform(0.01, 0.03),
                color=WHITE_SOFT,
                fill_opacity=rng.uniform(0.15, 0.5),
            )
            for _ in range(40)
        ])

        self.play(FadeIn(stars, run_time=1.0))
        self.play(Write(line1), run_time=1.1)
        self.play(Write(line2), run_time=1.1)
        self.wait(0.7)

        sub = Text(
            "You're not sharing the same present\nwith a distant galaxy.",
            font_size=30, color=WHITE_SOFT, line_spacing=1.2,
        )
        sub.set(width=SAFE_W * 0.95)
        sub.next_to(headline, DOWN, buff=0.9)

        self.play(FadeIn(sub, shift=UP * 0.3), run_time=1.0)
        self.wait(1.4)

        self.play(
            *[FadeOut(m) for m in [headline, sub, stars]],
            run_time=0.8,
        )

    # ----------------------------------------------------------------
    # SCENE 2 — SPACETIME DIAGRAM (Minkowski diagram, c = 1 units)
    # ----------------------------------------------------------------
    def build_axes(self):
        """A Minkowski (x, ct) diagram with equal unit scale on both
        axes, so a slope of +-1 is a genuine 45-degree light ray."""
        axes = Axes(
            x_range=[-2.5, 2.5, 1],
            y_range=[-3.5, 3.5, 1],
            x_length=4.0,   # unit length 0.8
            y_length=5.6,   # unit length 0.8  -> equal scale on both axes
            axis_config={
                "color": DIM,
                "stroke_width": 2,
                "include_tip": True,
                "tip_width": 0.15,
                "tip_height": 0.15,
                "include_numbers": False,
            },
        )
        axes.scale(0.92)
        x_label = Text("x", font_size=28, color=DIM).next_to(axes.x_axis.get_end(), RIGHT, buff=0.12)
        ct_label = Text("ct", font_size=28, color=DIM).next_to(axes.y_axis.get_end(), UP, buff=0.12)
        return axes, VGroup(x_label, ct_label)

    def build_light_cone(self, axes):
        """The invariant light cone: ct = +-x, drawn once and never
        rotated for the rest of the animation."""
        p1 = axes.c2p(-2.3, -2.3)
        p2 = axes.c2p(2.3, 2.3)
        p3 = axes.c2p(-2.3, 2.3)
        p4 = axes.c2p(2.3, -2.3)
        ray_a = glow_line(p1, p2, CYAN, width=3)
        ray_b = glow_line(p3, p4, CYAN, width=3)
        return VGroup(ray_a, ray_b)

    def build_causal_shading(self, axes):
        """Subtle fills for future / past (timelike) and the two
        'elsewhere' (spacelike) wedges, so the causal structure reads
        at a glance without crowding the frame."""
        o = axes.c2p(0, 0)
        top = axes.c2p(0, 3.3)
        bottom = axes.c2p(0, -3.3)
        left = axes.c2p(-2.3, 0)
        right = axes.c2p(2.3, 0)
        ul = axes.c2p(-2.3, 2.3)
        ur = axes.c2p(2.3, 2.3)
        dl = axes.c2p(-2.3, -2.3)
        dr = axes.c2p(2.3, -2.3)

        future = Polygon(o, ul, top, ur, color=FUTURE_FILL, fill_opacity=0.55, stroke_width=0)
        past = Polygon(o, dl, bottom, dr, color=PAST_FILL, fill_opacity=0.55, stroke_width=0)
        elsewhere_l = Polygon(o, left, dl, ul, color=ELSEWHERE_FILL, fill_opacity=0.5, stroke_width=0)
        elsewhere_r = Polygon(o, right, dr, ur, color=ELSEWHERE_FILL, fill_opacity=0.5, stroke_width=0)
        return VGroup(elsewhere_l, elsewhere_r, past, future)

    def scene_2_spacetime(self):
        axes, axis_labels = self.build_axes()
        diagram = VGroup(axes, axis_labels).move_to(ORIGIN).shift(UP * 0.15)
        axes = diagram[0]

        shading = self.build_causal_shading(axes)
        cone = self.build_light_cone(axes)
        origin_dot = glow_dot(axes.c2p(0, 0), WHITE_SOFT, radius=0.05)

        title = scene_title("A spacetime diagram", size=28)
        title.to_edge(UP, buff=0.7)

        self.play(Write(title), run_time=0.8)
        self.play(Create(axes), Write(axis_labels), run_time=1.0)
        self.play(FadeIn(shading), run_time=0.8)
        self.play(*[Create(m) for m in cone], run_time=1.1)
        self.play(FadeIn(origin_dot), run_time=0.4)

        future_lbl = Text("future", font_size=22, color=CYAN).move_to(axes.c2p(0.9, 2.6))
        past_lbl = Text("past", font_size=22, color=CYAN).move_to(axes.c2p(0.9, -2.6))
        else_lbl = Text("elsewhere", font_size=20, color=PURPLE).move_to(axes.c2p(1.75, 0)).shift(DOWN * 0.1)

        self.play(FadeIn(future_lbl), FadeIn(past_lbl), FadeIn(else_lbl), run_time=0.9)
        self.wait(1.2)

        caption = Text(
            "Light rays (cyan) never move — every observer\nagrees on this cone.",
            font_size=24, color=WHITE_SOFT, line_spacing=1.2,
        ).set(width=SAFE_W * 0.95)
        caption.next_to(diagram, DOWN, buff=0.35)
        self.play(FadeIn(caption, shift=UP * 0.2), run_time=0.8)
        self.wait(1.3)

        self.play(
            FadeOut(title), FadeOut(future_lbl), FadeOut(past_lbl),
            FadeOut(else_lbl), FadeOut(caption), FadeOut(origin_dot),
            run_time=0.7,
        )

        # keep diagram + cone + shading alive for the next scenes
        self.axes = axes
        self.diagram = diagram
        self.cone = cone
        self.shading = shading

    # ----------------------------------------------------------------
    # SCENE 3 — OBSERVER A's SURFACE OF SIMULTANEITY
    # ----------------------------------------------------------------
    def scene_3_observer_a(self):
        axes = self.axes

        title = scene_title("Observer A, at rest", size=28)
        title.to_edge(UP, buff=0.7)
        self.play(Write(title), run_time=0.8)

        # distant location: a stationary object, worldline = vertical
        # line at x = 2.0 (drawn faint, it is NOT the moving observer)
        x_distant = 2.0
        distant_worldline = DashedLine(
            axes.c2p(x_distant, -3.2), axes.c2p(x_distant, 3.2),
            color=DIM, stroke_width=2, dash_length=0.08,
        )
        self.play(Create(distant_worldline), run_time=0.7)

        a_worldline = glow_line(axes.c2p(0, -3.2), axes.c2p(0, 3.2), WHITE_SOFT, width=3)
        self.play(Create(a_worldline), run_time=0.7)

        # A's line of simultaneity: the horizontal line ct = 0
        sim_a = glow_line(axes.c2p(-2.3, 0), axes.c2p(2.3, 0), MAGENTA, width=4)
        self.play(Create(sim_a), run_time=1.0)

        event1 = glow_dot(axes.c2p(-1.6, 0), GOLD)
        event2 = glow_dot(axes.c2p(x_distant, 0), GOLD)
        self.play(FadeIn(event1), FadeIn(event2), run_time=0.6)

        lbl = Text("simultaneous for A", font_size=24, color=MAGENTA, weight=BOLD)
        lbl.next_to(sim_a, DOWN, buff=0.22)
        self.play(FadeIn(lbl, shift=UP * 0.15), run_time=0.7)
        self.wait(1.4)

        self.play(FadeOut(title), FadeOut(lbl), run_time=0.6)

        # keep for next scene
        self.distant_worldline = distant_worldline
        self.a_worldline = a_worldline
        self.sim_a = sim_a
        self.event1 = event1
        self.event2_a = event2
        self.x_distant = x_distant

    # ----------------------------------------------------------------
    # SCENE 4 — OBSERVER B, MOVING
    # ----------------------------------------------------------------
    def scene_4_observer_b(self):
        axes = self.axes
        x_distant = self.x_distant

        title = scene_title("Observer B, moving", size=28)
        title.to_edge(UP, buff=0.7)
        self.play(Write(title), run_time=0.8)

        beta_final = 0.6  # v/c for observer B
        beta_tracker = ValueTracker(0.0)

        # B's worldline: ct = x / beta  (steeper than the light cone,
        # i.e. |slope| > 1, so it always stays inside the cone -
        # this keeps B properly timelike, never redrawing the cone itself)
        def b_worldline_updater():
            b = max(beta_tracker.get_value(), 1e-4)
            x_max = min(2.2, 3.2 * b)
            p1 = axes.c2p(-x_max, -x_max / b)
            p2 = axes.c2p(x_max, x_max / b)
            return glow_line(p1, p2, PURPLE, width=3)

        # B's simultaneity line: ct = beta * x  (shallower than the
        # cone, mirror-symmetric to the worldline about the light ray)
        def b_sim_updater():
            b = beta_tracker.get_value()
            p1 = axes.c2p(-2.3, -2.3 * b)
            p2 = axes.c2p(2.3, 2.3 * b)
            return glow_line(p1, p2, CYAN, width=4)

        b_worldline = always_redraw(b_worldline_updater)
        b_sim = always_redraw(b_sim_updater)

        self.add(b_worldline, b_sim)
        self.play(FadeIn(VGroup()), run_time=0.1)  # ensure add() registers before animating tracker

        note = Text(
            "As B's velocity grows, both lines tilt —\nsymmetrically about the light cone.",
            font_size=23, color=WHITE_SOFT, line_spacing=1.2,
        ).set(width=SAFE_W * 0.95)
        note.next_to(self.diagram, DOWN, buff=0.35)
        self.play(FadeIn(note), run_time=0.6)

        self.play(beta_tracker.animate.set_value(beta_final), run_time=2.2, rate_func=smooth)
        self.wait(0.4)

        # freeze B's simultaneity line as a static mobject at beta_final
        # so we can point to its intersection with the distant worldline
        frozen_sim_b = glow_line(
            axes.c2p(-2.3, -2.3 * beta_final), axes.c2p(2.3, 2.3 * beta_final), CYAN, width=4,
        )
        event2_b_ct = beta_final * x_distant
        event2_b = glow_dot(axes.c2p(x_distant, event2_b_ct), GOLD)

        self.remove(b_sim)
        self.add(frozen_sim_b)
        self.play(FadeIn(event2_b), run_time=0.6)

        lbl_b = Text("simultaneous for B", font_size=24, color=CYAN, weight=BOLD)
        lbl_b.next_to(frozen_sim_b[-1].get_end(), UR, buff=0.15).shift(LEFT * 0.3)
        self.play(FadeIn(lbl_b, shift=UP * 0.15), run_time=0.7)
        self.wait(0.6)

        # highlight the disagreement: two different events at the same
        # distant worldline
        brace_line = DashedLine(
            self.event2_a[-1].get_center(), event2_b[-1].get_center(),
            color=GOLD, stroke_width=2,
        )
        disagree = Text("A and B disagree about\n\"right now\" out there.",
                         font_size=24, color=GOLD, line_spacing=1.2, weight=BOLD)
        disagree.set(width=SAFE_W * 0.9)
        disagree.next_to(note, DOWN, buff=0.3)

        self.play(Create(brace_line), run_time=0.6)
        self.play(FadeIn(disagree, shift=UP * 0.15), run_time=0.8)
        self.wait(1.6)

        self.play(
            *[FadeOut(m) for m in [title, note, disagree, lbl_b, brace_line, b_worldline]],
            run_time=0.7,
        )

        # keep the essentials for later scenes
        self.b_worldline_frozen = None
        self.sim_b = frozen_sim_b
        self.event2_b = event2_b
        self.beta_final = beta_final

    # ----------------------------------------------------------------
    # SCENE 5 — THE EQUATION
    # ----------------------------------------------------------------
    def scene_5_equation(self):
        # shrink the diagram to make room for the equation, cinematic move
        group_on_screen = VGroup(
            self.diagram, self.cone, self.shading, self.distant_worldline,
            self.a_worldline, self.sim_a, self.event1, self.event2_a,
            self.sim_b, self.event2_b,
        )
        self.play(group_on_screen.animate.scale(0.6).to_edge(DOWN, buff=0.35), run_time=1.0)

        title = scene_title("Why distant \"now\" shifts", size=26)
        title.to_edge(UP, buff=0.6)
        self.play(Write(title), run_time=0.8)

        # Equation built from styled Text glyphs instead of MathTex, so
        # the animation never depends on a LaTeX installation being
        # present in the render environment.
        def sym(s, color=WHITE_SOFT, italic=True, size=52):
            return Text(s, font_size=size, color=color,
                        slant=ITALIC if italic else NORMAL, weight=BOLD)

        t_prime = sym("t\u2032")
        eq_sign = sym("=", italic=False)
        gamma = sym("\u03b3")
        open_paren = sym("(", italic=False)
        t_sym = sym("t")
        minus = sym("\u2212", italic=False)
        term = sym("vx / c\u00b2", color=WHITE_SOFT)
        close_paren = sym(")", italic=False)

        eq = VGroup(t_prime, eq_sign, gamma, open_paren, t_sym, minus, term, close_paren)
        eq.arrange(RIGHT, buff=0.14)
        eq.set(width=min(eq.width, SAFE_W * 0.98))
        eq.next_to(title, DOWN, buff=0.55)

        self.play(Write(eq), run_time=1.2)
        self.wait(0.5)

        box = SurroundingRectangle(term, color=GOLD, buff=0.08, stroke_width=3)
        self.play(term.animate.set_color(GOLD), Create(box), run_time=0.8)
        self.wait(0.4)

        explain = Text(
            "This term ties time to position.\nDifferent x means a different t'\nfor the same distant event.",
            font_size=24, color=WHITE_SOFT, line_spacing=1.25,
        ).set(width=SAFE_W * 0.92)
        explain.next_to(eq, DOWN, buff=0.5)
        self.play(FadeIn(explain, shift=UP * 0.2), run_time=0.9)
        self.wait(1.6)

        clarify = Text(
            "Nobody's own clock runs strangely —\nonly which faraway events count as \"now\" does.",
            font_size=22, color=CYAN, line_spacing=1.25, weight=BOLD,
        ).set(width=SAFE_W * 0.94)
        clarify.next_to(explain, DOWN, buff=0.4)
        self.play(FadeIn(clarify, shift=UP * 0.15), run_time=0.9)
        self.wait(1.8)

        self.play(
            *[FadeOut(m) for m in [title, eq, box, explain, clarify]],
            run_time=0.8,
        )
        self.play(group_on_screen.animate.scale(1 / 0.6).move_to(ORIGIN).shift(UP * 0.15), run_time=0.9)

    # ----------------------------------------------------------------
    # SCENE 6 — FINAL PUNCH
    # ----------------------------------------------------------------
    def scene_6_final_punch(self):
        axes = self.axes

        q_a = Text("What is happening\nTHERE right now?", font_size=22, color=MAGENTA,
                    line_spacing=1.15, weight=BOLD).set(width=SAFE_W * 0.6)
        q_a.next_to(self.sim_a, LEFT, buff=0.15).shift(UP * 0.5 + LEFT * 0.1)

        q_b = Text("What is happening\nTHERE right now?", font_size=22, color=CYAN,
                    line_spacing=1.15, weight=BOLD).set(width=SAFE_W * 0.6)
        q_b.next_to(self.sim_b, RIGHT, buff=0.15).shift(DOWN * 0.9 + RIGHT * 0.1)

        self.play(FadeIn(q_a, shift=RIGHT * 0.2), run_time=0.8)
        self.play(FadeIn(q_b, shift=LEFT * 0.2), run_time=0.8)
        self.wait(1.0)

        ans_a = Text("A says: NOW", font_size=22, color=MAGENTA, weight=BOLD)
        ans_a.next_to(self.event2_a, UP, buff=0.22)
        ans_b = Text("B says: LATER", font_size=22, color=CYAN, weight=BOLD)
        ans_b.next_to(self.event2_b, DOWN, buff=0.22)

        self.play(
            Indicate(self.event1[-1], color=GOLD, scale_factor=1.4),
            Indicate(self.event2_a[-1], color=GOLD, scale_factor=1.4),
            FadeIn(ans_a),
            run_time=0.9,
        )
        self.play(
            Indicate(self.event2_b[-1], color=GOLD, scale_factor=1.4),
            FadeIn(ans_b),
            run_time=0.9,
        )
        self.wait(1.6)

        self.play(
            *[FadeOut(m) for m in [
                q_a, q_b, ans_a, ans_b, self.diagram, self.cone, self.shading,
                self.distant_worldline, self.a_worldline, self.sim_a, self.sim_b,
                self.event1, self.event2_a, self.event2_b,
            ]],
            run_time=1.0,
        )

        final1 = Text("Local time is real.", font_size=46, color=WHITE_SOFT, weight=BOLD)
        final2 = Text("Universal NOW is not.", font_size=46, color=MAGENTA, weight=BOLD)
        final = VGroup(final1, final2).arrange(DOWN, buff=0.3)
        final.set(width=SAFE_W)

        self.play(FadeIn(final1, shift=UP * 0.2), run_time=1.0)
        self.play(FadeIn(final2, shift=UP * 0.2), run_time=1.0)
        self.wait(2.0)

        self.play(FadeOut(final), run_time=1.0)
