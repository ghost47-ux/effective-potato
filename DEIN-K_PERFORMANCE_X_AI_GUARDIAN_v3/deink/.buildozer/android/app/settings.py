from kivy.metrics import dp
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout

from common import BackgroundRoot, Panel, StyledButton, label, header, nav, VIOLET, MUTED


class SettingsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        root = BackgroundRoot()
        page = BoxLayout(orientation="vertical", padding=dp(10), spacing=dp(7))
        page.add_widget(header("SETTINGS", "DEIN-K PERFORMANCE X"))

        card = Panel(orientation="vertical", padding=dp(18))
        card.add_widget(label(
            "THEME\nPurple Futuristic\n\n"
            "BACKGROUND\nAnime Gaming Visual\n\n"
            "INTRO\nAnimated d_logo.png\n\n"
            "VERSION\n1.0.0",
            15, MUTED
        ))
        page.add_widget(card)

        advanced = StyledButton("ADB / SHIZUKU", size_hint_y=None, height=dp(50))
        advanced.bind(on_release=lambda *_: setattr(self.manager, "current", "advanced"))
        page.add_widget(advanced)

        page.add_widget(nav())
        root.add_widget(page)
        self.add_widget(root)
