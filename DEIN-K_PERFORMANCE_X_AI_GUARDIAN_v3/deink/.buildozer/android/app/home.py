from kivy.clock import Clock
from kivy.metrics import dp
from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout

from common import BackgroundRoot, Panel, StyledButton, ProgressBarX, label, header, nav, show_popup, stats, VIOLET, GREEN, MUTED, WHITE


class HomeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        root = BackgroundRoot()
        page = BoxLayout(orientation="vertical", padding=dp(10), spacing=dp(7))

        page.add_widget(header("DEIN-K PERFORMANCE X", "SMART GAMING • DEVICE • NETWORK"))

        scroll = ScrollView()
        body = BoxLayout(orientation="vertical", padding=dp(8), spacing=dp(12), size_hint_y=None)
        body.bind(minimum_height=body.setter("height"))

        hero = Panel(orientation="vertical", size_hint_y=None, height=dp(125), padding=dp(15))
        hero.add_widget(label("PERFORMANCE CENTER", 18, VIOLET, True, "center"))
        self.score = label("PERFORMANCE SCORE  --", 24, GREEN, True, "center")
        hero.add_widget(self.score)
        hero.add_widget(label("Live device health • safe optimization", 12, MUTED, False, "center"))
        body.add_widget(hero)

        grid = GridLayout(cols=2, spacing=dp(10), size_hint_y=None, height=dp(250))
        self.ram = self.metric("RAM", "RAM_logo.png")
        self.cpu = self.metric("CPU", "CPU_logo.png")
        self.storage = self.metric("STORAGE", "storage_logo.png")
        self.battery = self.metric("BATTERY", "battery_logo.png")
        for w in (self.ram, self.cpu, self.storage, self.battery):
            grid.add_widget(w)
        body.add_widget(grid)

        boost = Panel(orientation="vertical", size_hint_y=None, height=dp(145), padding=dp(15))
        boost.add_widget(label("BOOST ENGINE", 17, VIOLET, True, "center"))
        self.status = label("READY", 13, WHITE, True, "center")
        boost.add_widget(self.status)
        self.progress = ProgressBarX(size_hint_y=None, height=dp(10), value=0)
        boost.add_widget(self.progress)
        b = StyledButton("BOOST NOW", accent=(0.48, 0.12, 0.82, 1), size_hint_y=None, height=dp(48))
        b.bind(on_release=self.boost)
        boost.add_widget(b)
        body.add_widget(boost)

        actions = GridLayout(cols=2, spacing=dp(9), size_hint_y=None, height=dp(245))
        for text, screen in [
            ("SMART ANALYSIS", "home"),
            ("GAME BOOSTER", "game"),
            ("PHONE BOOSTER", "phone"),
            ("NETWORK", "network"),
            ("ADB / SHIZUKU", "advanced"),
            ("AI GAMING GUARDIAN", "guardian"),
            ("SETTINGS", "settings"),
        ]:
            b = StyledButton(text, accent=(0.25, 0.055, 0.40, 0.96))
            b.bind(on_release=lambda _, s=screen: self.manager.__setattr__("current", s))
            if text == "SMART ANALYSIS":
                b.bind(on_release=self.analysis)
            actions.add_widget(b)
        body.add_widget(actions)

        scroll.add_widget(body)
        page.add_widget(scroll)
        page.add_widget(nav())
        root.add_widget(page)
        self.add_widget(root)

        Clock.schedule_interval(self.update_stats, 2)

    def metric(self, title, logo):
        from kivy.uix.image import Image
        card = Panel(orientation="vertical", size_hint_y=None, height=dp(115), padding=dp(9), spacing=dp(3))
        img = Image(source=__import__("common").asset(logo), size_hint_y=None, height=dp(43), opacity=0.95)
        card.add_widget(img)
        card.add_widget(label(title, 11, MUTED, True, "center"))
        value = label("--", 18, WHITE, True, "center")
        card.add_widget(value)
        return card

    def update_stats(self, *_):
        s = stats()
        values = [
            (self.ram, s["ram"], "RAM"),
            (self.cpu, s["cpu"], "CPU"),
            (self.storage, s["storage"], "STORAGE"),
            (self.battery, s["battery"], "BATTERY"),
        ]
        for card, value, name in values:
            if value is not None:
                card.children[0].text = f"{value:.0f}%"
        ram = s["ram"] or 0
        cpu = s["cpu"] or 0
        storage = s["storage"] or 0
        score = max(0, min(100, int(100 - max(0, ram-60)*0.7 - max(0, cpu-60)*0.7 - max(0, storage-80)*0.5)))
        self.score.text = f"PERFORMANCE SCORE  {score}%"

    def boost(self, instance):
        self.status.text = "OPTIMIZING..."
        self.progress.value = 0
        Clock.schedule_interval(self.animate_boost, 0.035)

    def animate_boost(self, dt):
        self.progress.value += 2
        if self.progress.value >= 100:
            self.progress.value = 100
            self.status.text = "OPTIMIZATION COMPLETE"
            return False

    def analysis(self, *_):
        s = stats()
        msg = (
            f"RAM: {s['ram']:.0f}%\n" if s["ram"] is not None else "RAM: unavailable\n"
        )
        msg += f"CPU: {s['cpu']:.0f}%\n" if s["cpu"] is not None else "CPU: unavailable\n"
        msg += f"Storage: {s['storage']:.0f}%\n" if s["storage"] is not None else "Storage: unavailable\n"
        msg += "\nRecommendation: keep storage below about 85% and close heavy apps before gaming."
        show_popup("SMART ANALYSIS", msg)
