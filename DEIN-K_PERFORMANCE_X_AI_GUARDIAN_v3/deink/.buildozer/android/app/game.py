from kivy.metrics import dp
from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label

from common import BackgroundRoot, Panel, StyledButton, label, header, nav, show_popup, MUTED, VIOLET
from kivy.utils import platform


class GameScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        root = BackgroundRoot()
        page = BoxLayout(orientation="vertical", padding=dp(10), spacing=dp(7))
        page.add_widget(header("GAME BOOSTER", "AUTOMATIC INSTALLED-GAME DETECTION"))

        top = BoxLayout(size_hint_y=None, height=dp(52), spacing=dp(8))
        self.status = label("Ready to scan", 12, MUTED, False, "center")
        top.add_widget(self.status)
        scan = StyledButton("SCAN", size_hint_x=None, width=dp(95))
        scan.bind(on_release=lambda *_: self.scan_games())
        top.add_widget(scan)
        page.add_widget(top)

        scroll = ScrollView()
        self.list_box = BoxLayout(orientation="vertical", spacing=dp(9), padding=dp(6), size_hint_y=None)
        self.list_box.bind(minimum_height=self.list_box.setter("height"))
        scroll.add_widget(self.list_box)
        page.add_widget(scroll)
        page.add_widget(nav())
        root.add_widget(page)
        self.add_widget(root)

    def on_pre_enter(self, *args):
        self.scan_games()

    def scan_games(self):
        self.list_box.clear_widgets()
        if platform != "android":
            self.status.text = "Android scan activates inside the APK."
            self.list_box.add_widget(Panel(
                orientation="vertical", size_hint_y=None, height=dp(110),
                children=[]
            ))
            return
        try:
            from jnius import autoclass
            PythonActivity = autoclass("org.kivy.android.PythonActivity")
            PackageManager = autoclass("android.content.pm.PackageManager")
            ApplicationInfo = autoclass("android.content.pm.ApplicationInfo")
            activity = PythonActivity.mActivity
            pm = activity.getPackageManager()
            apps = pm.getInstalledApplications(PackageManager.GET_META_DATA)
            games = []
            for info in apps:
                try:
                    launch = pm.getLaunchIntentForPackage(info.packageName)
                    category = info.category
                    flags = info.flags
                    if launch and (category == ApplicationInfo.CATEGORY_GAME or (flags & 0x02000000)):
                        name = str(pm.getApplicationLabel(info))
                        games.append((name, str(info.packageName)))
                except Exception:
                    continue
            games.sort(key=lambda x: x[0].lower())
            self.status.text = f"{len(games)} game(s) detected"
            if not games:
                self.list_box.add_widget(label(
                    "No games were detected.\nAndroid package visibility may be limiting the scan.",
                    14, MUTED, False, "center", size_hint_y=None, height=dp(100)
                ))
                return
            for name, package in games:
                row = Panel(orientation="vertical", size_hint_y=None, height=dp(94), padding=dp(9))
                row.add_widget(label(name, 15, VIOLET, True))
                row.add_widget(label(package, 10, MUTED))
                b = StyledButton("LAUNCH", size_hint_y=None, height=dp(40))
                b.bind(on_release=lambda _, p=package: self.launch(p))
                row.add_widget(b)
                self.list_box.add_widget(row)
        except Exception as e:
            self.status.text = "Game detection unavailable"
            show_popup("GAME BOOSTER", "Could not read installed Android games.\n\nBuild the APK with QUERY_ALL_PACKAGES for broad package visibility when sideloading.")

    def launch(self, package):
        try:
            from jnius import autoclass
            PythonActivity = autoclass("org.kivy.android.PythonActivity")
            activity = PythonActivity.mActivity
            intent = activity.getPackageManager().getLaunchIntentForPackage(package)
            if intent:
                activity.startActivity(intent)
        except Exception:
            show_popup("GAME LAUNCH", "Unable to launch this game.")
