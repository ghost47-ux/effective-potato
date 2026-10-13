import os
from kivy.clock import Clock
from kivy.animation import Animation
from kivy.metrics import dp
from kivy.uix.screenmanager import Screen
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.graphics import Color, Rectangle
from kivy.utils import platform


class IntroScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        root = FloatLayout()

        with root.canvas.before:
            Color(0.03, 0.005, 0.06, 1)
            self.bg_rect = Rectangle(pos=root.pos, size=root.size)
        root.bind(pos=self._sync, size=self._sync)

        logo_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "assets", "d_logo.png"
        )

        self.logo = Image(
            source=logo_path,
            size_hint=(None, None),
            opacity=0,
            allow_stretch=True,
            keep_ratio=True,
        )
        root.add_widget(self.logo)
        self.add_widget(root)

        self.bind(size=self._place_logo)
        Clock.schedule_once(self.start_intro, 0.25)

    def _sync(self, *_):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size

    def _place_logo(self, *_):
        width = min(self.width * 0.68, dp(360))
        self.logo.size = (width, width)
        self.logo.center = self.center

    def start_intro(self, *_):
        self._place_logo()
        self.logo.opacity = 0
        fade_in = Animation(opacity=1, duration=1.0)
        fade_in.bind(on_complete=lambda *_: self.hold_logo())
        fade_in.start(self.logo)

    def hold_logo(self):
        Clock.schedule_once(self.fade_out, 2.5)

    def fade_out(self, *_):
        fade = Animation(opacity=0, duration=1.0)
        fade.bind(on_complete=lambda *_: self.open_home())
        fade.start(self.logo)

    def open_home(self):
        if self.manager:
            self.manager.current = "home"
