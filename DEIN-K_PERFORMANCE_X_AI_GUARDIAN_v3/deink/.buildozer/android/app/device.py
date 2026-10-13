from kivy.metrics import dp
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout

from common import BackgroundRoot, Panel, StyledButton, label, header, nav, device_info, VIOLET, MUTED


class DeviceScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        root = BackgroundRoot()
        page = BoxLayout(orientation="vertical", padding=dp(10), spacing=dp(7))
        page.add_widget(header("DEVICE INFORMATION", "HARDWARE & SOFTWARE"))

        card = Panel(orientation="vertical", padding=dp(18))
        lines = []
        for key, value in device_info():
            lines.append(f"{key.upper()}\n{value}")
        card.add_widget(label("\n\n".join(lines), 14, MUTED))
        page.add_widget(card)

        touch = StyledButton("TOUCH TESTER", size_hint_y=None, height=dp(48))
        touch.bind(on_release=lambda *_: setattr(self.manager, "current", "touch"))
        page.add_widget(touch)
        page.add_widget(nav())
        root.add_widget(page)
        self.add_widget(root)
