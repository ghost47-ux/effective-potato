from kivymd.app import MDApp
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, FadeTransition
from kivy.properties import StringProperty

from intro import IntroScreen
from home import HomeScreen
from game import GameScreen
from phone import PhoneScreen
from network import NetworkScreen, TouchScreen
from device import DeviceScreen
from settings import SettingsScreen
from advanced import AdvancedScreen
from gaming import GamingGuardianScreen


class PerformanceApp(MDApp):
    background = StringProperty("")

    def build(self):
        self.title = "DEIN-K PERFORMANCE X"
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "DeepPurple"
        Window.clearcolor = (0.055, 0.01, 0.10, 1)

        manager = ScreenManager(transition=FadeTransition(duration=0.18))
        manager.add_widget(IntroScreen(name="intro"))
        manager.add_widget(HomeScreen(name="home"))
        manager.add_widget(GameScreen(name="game"))
        manager.add_widget(PhoneScreen(name="phone"))
        manager.add_widget(NetworkScreen(name="network"))
        manager.add_widget(TouchScreen(name="touch"))
        manager.add_widget(DeviceScreen(name="device"))
        manager.add_widget(SettingsScreen(name="settings"))
        manager.add_widget(AdvancedScreen(name="advanced"))
        manager.add_widget(GamingGuardianScreen(name="guardian"))
        manager.current = "intro"
        return manager

    def go_to(self, name):
        if self.root:
            self.root.current = name

    def on_keyboard(self, window, key, scancode, codepoint, modifiers):
        if key in (27, 4) and self.root:
            if self.root.current != "home":
                self.root.current = "home"
                return True
        return False


if __name__ == "__main__":
    PerformanceApp().run()
