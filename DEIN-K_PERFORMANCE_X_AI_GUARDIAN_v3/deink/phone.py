from kivy.metrics import dp
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock

from common import BackgroundRoot, Panel, StyledButton, label, header, nav, stats, safe_cleanup, open_android_settings, VIOLET, GREEN, MUTED


class PhoneScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        root = BackgroundRoot()
        page = BoxLayout(orientation="vertical", padding=dp(10), spacing=dp(7))
        page.add_widget(header("PHONE BOOSTER", "SAFE OPTIMIZATION CENTER"))

        card = Panel(orientation="vertical", size_hint_y=None, height=dp(260), padding=dp(16))
        card.add_widget(label("DEVICE HEALTH", 18, VIOLET, True, "center"))
        self.info = label("Loading...", 14, MUTED, False, "center")
        card.add_widget(self.info)

        boost = StyledButton("OPTIMIZE PHONE", accent=(0.48, 0.12, 0.82, 1), size_hint_y=None, height=dp(50))
        boost.bind(on_release=self.optimize)
        card.add_widget(boost)

        settings = StyledButton("OPEN ANDROID SETTINGS", accent=(0.22, 0.05, 0.34, 1), size_hint_y=None, height=dp(46))
        settings.bind(on_release=lambda *_: open_android_settings())
        card.add_widget(settings)

        page.add_widget(card)
        page.add_widget(label(
            "No-root mode: the app only performs actions Android allows.\n"
            "ADB/Shizuku advanced controls are in the Advanced section.",
            12, MUTED, False, "center", size_hint_y=None, height=dp(70)
        ))
        page.add_widget(nav())
        root.add_widget(page)
        self.add_widget(root)
        Clock.schedule_interval(self.update, 2)

    def update(self, *_):
        s = stats()
        self.info.text = (
            f"RAM     {s['ram']:.0f}%\n" if s["ram"] is not None else "RAM     --\n"
        )
        self.info.text += f"CPU     {s['cpu']:.0f}%\n" if s["cpu"] is not None else "CPU     --\n"
        self.info.text += f"STORAGE {s['storage']:.0f}%\n" if s["storage"] is not None else "STORAGE --\n"
        self.info.text += f"BATTERY {s['battery']:.0f}%" if s["battery"] is not None else "BATTERY --"

    def optimize(self, *_):
        self.info.text = safe_cleanup()
