# ==============================================================================
# MANIM SCRIPT: MODULE 3 - BREAKING THE 100-DIMENSIONAL BARRIER
# Run with: manim -pql scenes.py <SceneName>
# ==============================================================================

from manim import *
import numpy as np

C_GRID = "#FFFFFF"
C_PATH = "#00FF00" # Lime Green
C_WEALTH = "#FFA500" # Orange
C_TARGET = "#0000FF" # Blue

class Scene1_CurseOfDimensionality(Scene):
    def construct(self):
        # [VOICEOVER]: In Module 2, we solved the Black-Scholes PDE by laying down 
        # a grid of collocation points across space and time. 
        
        # 1D Grid
        line = NumberLine(x_range=[0, 10, 1], length=6, color=C_GRID).shift(UP*2)
        dots_1d = VGroup(*[Dot(line.n2p(i), color=C_TARGET) for i in range(11)])
        label_1d = Text("1 Asset = 10 Points", font_size=24).next_to(line, UP)
        
        self.play(Create(line), FadeIn(dots_1d, lag_ratio=0.1), Write(label_1d))
        self.wait(1)

        # [VOICEOVER]: If we have one asset, and we slice its price into 10 points, 
        # that's easy. If we have two assets, our grid becomes 10 times 10. That's 100 points.
        
        # 2D Grid
        axes_2d = Axes(x_range=[0, 10, 2], y_range=[0, 10, 2], x_length=4, y_length=4).shift(DOWN*1.5)
        dots_2d = VGroup(*[Dot(axes_2d.c2p(x, y), color=C_TARGET, radius=0.04) 
                           for x in range(0, 11, 2) for y in range(0, 11, 2)])
        label_2d = Text("2 Assets = 100 Points", font_size=24).next_to(axes_2d, RIGHT)
        
        self.play(Create(axes_2d), FadeIn(dots_2d, lag_ratio=0.01), Write(label_2d))
        
        # [VOICEOVER]: If we have three assets, it's 1,000 points. 
        # But what if we want to price an S&P 100 basket option? 
        self.wait(1)
        
        # Explode to infinity
        eq = VGroup(
            MathTex("10^{100}"), 
            Text(" Points", font_size=36)
        ).arrange(RIGHT).scale(3).set_color(RED)
        
        # [VOICEOVER]: We would need ten to the power of one hundred grid points. 
        # That is vastly more than the number of atoms in the observable universe. 
        # The grid explodes. This is mathematically known as the Curse of Dimensionality.
        
        self.play(
            FadeOut(line), FadeOut(dots_1d), FadeOut(label_1d),
            FadeOut(axes_2d), FadeOut(dots_2d), FadeOut(label_2d),
            FadeIn(eq, scale=0.1)
        )
        self.play(eq.animate.scale(1.2), run_time=2)
        self.wait(2)


class Scene2_FeynmanKacPaths(ThreeDScene):
    def construct(self):
        # [VOICEOVER]: To break this barrier, we have to throw away the grid entirely. 
        # We need a new geometric intuition. 
        
        self.set_camera_orientation(phi=65 * DEGREES, theta=35 * DEGREES)
        axes = ThreeDAxes(axis_config={"include_numbers": True}).scale(0.8).shift(DOWN*0.5)
        self.play(Create(axes))

        # [VOICEOVER]: Instead of trying to calculate the value of the option at every single 
        # point in the universe, what if we just drop a single particle and watch where it goes?
        
        # Simulate a 3D random walk (Brownian Motion Path)
        path_points = [axes.c2p(0,0,0)]
        curr = np.array([0.0, 0.0, 0.0])
        for _ in range(50):
            curr += np.array([np.random.normal(0, 0.2), np.random.normal(0, 0.2), 0.1])
            path_points.append(axes.c2p(*curr))
            
        path = VMobject(color=C_PATH)
        path.set_points_as_corners(path_points)
        
        self.play(Create(path), run_time=3)
        
        # [VOICEOVER]: By simulating thousands of random market paths going forward in time, 
        # we only explore the areas of the universe that are actually statistically probable. 
        # This link between PDEs and random paths is called the Feynman-Kac formula.
        
        paths = VGroup(*[
            ParametricFunction(
                lambda t: axes.c2p(t * np.cos(t * np.random.uniform(1,3)), t * np.sin(t * np.random.uniform(1,3)), t),
                t_range=[0, 3], color=C_PATH, stroke_opacity=0.3
            ) for _ in range(10)
        ])
        
        self.play(FadeIn(paths, lag_ratio=0.1))
        self.begin_ambient_camera_rotation(rate=0.5)
        self.wait(4)
        self.stop_ambient_camera_rotation()


class Scene3_BSDEArchitecture(Scene):
    def construct(self):
        # [VOICEOVER]: But how does a neural network learn from a random path? 
        # We reframe the pricing problem into a Reinforcement Learning game. 
        
        # Target Payoff Box
        target = Rectangle(width=2, height=1, color=C_TARGET).shift(RIGHT*4)
        target_label = Text("True Payoff", font_size=24).move_to(target)
        
        self.play(Create(target), Write(target_label))
        
        # [VOICEOVER]: Imagine you are a trader. You start at day zero with a bank account. 
        # You want this bank account to exactly match the option's payoff at expiration.
        
        bank = Rectangle(width=2, height=1, color=C_WEALTH).shift(LEFT*4)
        bank_label = Text("Wealth (W_0)", font_size=24).move_to(bank)
        
        self.play(Create(bank), Write(bank_label))

        # [VOICEOVER]: At every tick of the clock, the neural network acts as your agent. 
        # It looks at the 100 stock prices, and it outputs 100 Deltas—your hedging strategy.
        
        agent = Circle(radius=0.8, color=WHITE).shift(DOWN*2)
        agent_label = Text("NN (Delta)", font_size=24).move_to(agent)
        
        arrow_in = Arrow(start=LEFT*2 + DOWN*3, end=agent.get_left(), color=C_PATH)
        label_S = MathTex("S_t").next_to(arrow_in, DOWN)
        
        arrow_out = Arrow(start=agent.get_top(), end=bank.get_bottom(), color=WHITE)
        
        self.play(FadeIn(agent, agent_label, arrow_in, label_S))
        self.play(GrowArrow(arrow_out))
        
        # [VOICEOVER]: Your wealth steps forward. You buy and sell. 
        # At the end of the simulation, we compare your final Wealth to the True Payoff. 
        # The difference is our loss.
        
        path_arrow = Arrow(start=bank.get_right(), end=target.get_left(), color=C_WEALTH)
        self.play(GrowArrow(path_arrow))
        
        loss_eq = MathTex(r"\text{Loss} = (W_T - \text{Payoff})^2", color=RED).shift(UP*2)
        self.play(Write(loss_eq))
        
        # [VOICEOVER]: And here is the beautiful part. The initial bankroll required to perfectly 
        # hedge this portfolio? That IS the exact price of the option. 
        
        highlight = SurroundingRectangle(bank, color=YELLOW, buff=0.2)
        self.play(Create(highlight))
        self.wait(2)


class Scene4_ConvergenceHistogram(Scene):
    def construct(self):
        # [VOICEOVER]: Let's look at the results. 
        # On the left, we have the true payoff distribution. 
        # On the right, the wealth of our Deep BSDE agent.
        
        axes = Axes(x_range=[80, 140, 10], y_range=[0, 100, 20], x_length=7, y_length=5, axis_config={"include_numbers": True})
        
        # Initial bad distribution
        curve_bad = axes.plot(lambda x: 80 * np.exp(-0.05 * (x - 110)**2), color=RED)
        
        # Converged distribution
        curve_good = axes.plot(lambda x: 90 * np.exp(-0.2 * (x - 105)**2), color=C_WEALTH)
        
        self.play(Create(axes), Create(curve_bad))
        
        # [VOICEOVER]: At Epoch 0, the agent is guessing. Its wealth distribution is totally random.
        # But as we train the network, it learns to hedge perfectly. The variance shrinks. 
        
        self.play(Transform(curve_bad, curve_good), run_time=3)
        
        # [VOICEOVER]: The final initial wealth parameter (V_0) has converged. 
        # We have just priced a 100-dimensional option in seconds.
        
        label = Text("Successful Hedging Replication", color=C_WEALTH).to_edge(UP)
        self.play(Write(label))
        self.wait(2)
