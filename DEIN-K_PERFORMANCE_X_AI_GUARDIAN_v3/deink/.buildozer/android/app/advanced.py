from kivy.metrics import dp
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.utils import platform

from common import BackgroundRoot, Panel, StyledButton, label, header, nav, VIOLET, MUTED, show_popup


class AdvancedScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        root = BackgroundRoot()
        page = BoxLayout(orientation="vertical", padding=dp(10), spacing=dp(7))
        page.add_widget(header("ADB / SHIZUKU", "ADVANCED ANDROID ACCESS"))

        card = Panel(orientation="vertical", padding=dp(16), size_hint_y=None, height=dp(350))
        self.status = label("Checking Android environment...", 14, VIOLET, True, "center")
        card.add_widget(self.status)

        shizuku = StyledButton("CHECK SHIZUKU", size_hint_y=None, height=dp(48))
        shizuku.bind(on_release=self.check_shizuku)
        card.add_widget(shizuku)

        adb = StyledButton("ADB INFORMATION", size_hint_y=None, height=dp(48))
        adb.bind(on_release=self.adb_info)
        card.add_widget(adb)

        note = label(
            "ADB/Shizuku cannot be silently enabled by an ordinary APK.\n"
            "The user must enable/authorize them separately. This screen is prepared "
            "for those advanced permissions rather than pretending the app has them.",
            12, MUTED, False, "center"
        )
        card.add_widget(note)

        page.add_widget(card)
        page.add_widget(nav())
        root.add_widget(page)
        self.add_widget(root)
        self.check_shizuku()

    def check_shizuku(self, *_):
        if platform != "android":
            self.status.text = "ANDROID APK REQUIRED\n\nShizuku status will be checked here."
            return
        try:
            from jnius import autoclass
            PythonActivity = autoclass("org.kivy.android.PythonActivity")
            pm = PythonActivity.mActivity.getPackageManager()
            pm.getPackageInfo("moe.shizuku.privileged.api", 0)
            self.status.text = "SHIZUKU APP DETECTED\n\nAuthorization still needs to be granted."
        except Exception:
            self.status.text = "SHIZUKU NOT DETECTED\n\nInstall and authorize Shizuku first."

    def adb_info(self, *_):
        if platform != "android":
            show_popup("ADB", "ADB controls become meaningful when the application is running on Android.")
        else:
            show_popup(
                "ADB",
                "ADB is a computer-side debugging bridge. The APK cannot simply grant itself ADB privileges. "
                "Use authorized ADB or Shizuku access for advanced operations."
            )
