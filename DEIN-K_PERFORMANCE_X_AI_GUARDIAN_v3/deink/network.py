import socket
import time

from kivy.metrics import dp
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget
from kivy.graphics import Color, RoundedRectangle

from common import BackgroundRoot, Panel, StyledButton, label, header, nav, MUTED, VIOLET, show_popup


class NetworkScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        root = BackgroundRoot()
        page = BoxLayout(orientation="vertical", padding=dp(10), spacing=dp(7))
        page.add_widget(header("NETWORK", "CONNECTION & LATENCY TEST"))

        card = Panel(orientation="vertical", size_hint_y=None, height=dp(235), padding=dp(18))
        self.result = label("READY\n\nPress TEST CONNECTION", 17, VIOLET, True, "center")
        card.add_widget(self.result)
        b = StyledButton("TEST CONNECTION", size_hint_y=None, height=dp(52))
        b.bind(on_release=self.test)
        card.add_widget(b)
        page.add_widget(card)
        page.add_widget(label(
            "This is a connection test, not a guaranteed game-server ping.",
            11, MUTED, False, "center", size_hint_y=None, height=dp(50)
        ))
        page.add_widget(nav())
        root.add_widget(page)
        self.add_widget(root)

    def test(self, *_):
        try:
            start = time.perf_counter()
            sock = socket.create_connection(("1.1.1.1", 443), timeout=3)
            sock.close()
            ms = (time.perf_counter() - start) * 1000
            self.result.text = f"CONNECTION OK\n\nTCP LATENCY\n{ms:.0f} ms"
        except Exception:
            self.result.text = "CONNECTION FAILED\n\nCheck mobile data or Wi-Fi."


class TouchArea(Widget):
    def __init__(self, callback, **kwargs):
        super().__init__(**kwargs)
        self.callback = callback
        with self.canvas:
            Color(0.13, 0.03, 0.22, 0.96)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(22)])
        self.bind(pos=self.sync, size=self.sync)

    def sync(self, *_):
        self.rect.pos = self.pos
        self.rect.size = self.size

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.callback(touch.x, touch.y)
            return True
        return super().on_touch_down(touch)


class TouchScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        root = BackgroundRoot()
        page = BoxLayout(orientation="vertical", padding=dp(10), spacing=dp(7))
        page.add_widget(header("TOUCH TESTER", "CHECK YOUR SCREEN RESPONSE"))

        self.count = 0
        self.info = label("TAPS: 0\n\nTouch anywhere inside the test area.", 15, VIOLET, True, "center",
                           size_hint_y=None, height=dp(75))
        page.add_widget(self.info)

        area = TouchArea(self.touch, size_hint_y=None, height=dp(360))
        page.add_widget(area)

        reset = StyledButton("RESET", size_hint_y=None, height=dp(45))
        reset.bind(on_release=self.reset)
        page.add_widget(reset)
        page.add_widget(nav())
        root.add_widget(page)
        self.add_widget(root)

    def touch(self, x, y):
        self.count += 1
        self.info.text = f"TAPS: {self.count}\n\nLast touch: X {x:.0f}   Y {y:.0f}"

    def reset(self, *_):
        self.count = 0
        self.info.text = "TAPS: 0\n\nTouch anywhere inside the test area."
