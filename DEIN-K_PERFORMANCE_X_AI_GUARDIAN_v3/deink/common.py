import os
import gc
import platform as host_platform
import shutil
import time

from kivy.app import App
from kivy.metrics import dp
from kivy.utils import platform as kivy_platform
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.properties import NumericProperty

try:
    import psutil
except Exception:
    psutil = None

_cpu_sample = None
_cpu_sample_at = 0.0
_cpu_percent_cached = None

PURPLE = (0.42, 0.10, 0.72, 1)
PURPLE2 = (0.28, 0.05, 0.48, 1)
DARK = (0.055, 0.01, 0.10, 1)
CARD = (0.10, 0.025, 0.17, 0.94)
VIOLET = (0.72, 0.32, 1.0, 1)
GREEN = (0.30, 1.0, 0.60, 1)
WHITE = (1, 1, 1, 1)
MUTED = (0.72, 0.67, 0.80, 1)


def asset(name):
    here = os.path.dirname(os.path.abspath(__file__))
    candidates = [
        os.path.join(here, "assets", name),
        os.path.join(here, name),
    ]
    for p in candidates:
        if os.path.exists(p):
            return p
    return ""


class BackgroundRoot(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            Color(*DARK)
            self.base = Rectangle(pos=self.pos, size=self.size)

        source = asset("anime.jpg")
        if source:
            self.image = Image(
                source=source,
                size_hint=(1, 1),
                allow_stretch=True,
                keep_ratio=True,
                fit_mode="cover",
                opacity=0.48,
            )
            self.add_widget(self.image)

        self.overlay = Widget()
        with self.overlay.canvas:
            Color(0.08, 0.01, 0.15, 0.67)
            self.overlay_rect = Rectangle(
                pos=self.overlay.pos, size=self.overlay.size
            )
        self.add_widget(self.overlay)
        self.bind(pos=self._sync, size=self._sync)

    def _sync(self, *_):
        self.base.pos = self.pos
        self.base.size = self.size
        self.overlay_rect.pos = self.overlay.pos
        self.overlay_rect.size = self.overlay.size


class Panel(BoxLayout):
    def __init__(self, panel_color=CARD, **kwargs):
        super().__init__(**kwargs)
        self.padding = kwargs.pop("padding", dp(12)) if "padding" not in kwargs else self.padding
        self.spacing = kwargs.pop("spacing", dp(8)) if "spacing" not in kwargs else self.spacing
        with self.canvas.before:
            Color(0.01, 0, 0.025, 0.42)
            self.shadow = RoundedRectangle(
                pos=(self.x + dp(2), self.y - dp(2)),
                size=self.size,
                radius=[dp(18)],
            )
            Color(*panel_color)
            self.rect = RoundedRectangle(
                pos=self.pos, size=self.size, radius=[dp(18)]
            )
        self.bind(pos=self._sync, size=self._sync)

    def _sync(self, *_):
        self.shadow.pos = (self.x + dp(2), self.y - dp(2))
        self.shadow.size = self.size
        self.rect.pos = self.pos
        self.rect.size = self.size


class StyledButton(Button):
    def __init__(self, text="", accent=PURPLE, **kwargs):
        super().__init__(text=text, **kwargs)
        self.background_normal = ""
        self.background_down = ""
        self.background_color = (0, 0, 0, 0)
        self.color = WHITE
        self.bold = True
        self.font_size = dp(14)
        self.halign = "center"
        self.valign = "middle"
        self._accent = accent
        with self.canvas.before:
            self.fill_color = Color(*accent)
            self.rect = RoundedRectangle(
                pos=self.pos, size=self.size, radius=[dp(15)]
            )
        self.bind(pos=self._sync, size=self._sync, state=self._state)

    def _sync(self, *_):
        self.rect.pos = self.pos
        self.rect.size = self.size

    def _state(self, *_):
        if self.state == "down":
            self.fill_color.rgba = tuple(max(0, c * 0.72) for c in self._accent[:3]) + (1,)
        else:
            self.fill_color.rgba = self._accent


class ProgressBarX(Widget):
    value = NumericProperty(0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas:
            Color(0.13, 0.03, 0.20, 1)
            self.bg = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(8)])
            Color(*VIOLET)
            self.fg = RoundedRectangle(pos=self.pos, size=(0, self.height), radius=[dp(8)])
        self.bind(pos=self._sync, size=self._sync, value=self._sync)

    def _sync(self, *_):
        self.bg.pos = self.pos
        self.bg.size = self.size
        w = max(0, self.width * max(0, min(100, self.value)) / 100.0)
        self.fg.pos = self.pos
        self.fg.size = (w, self.height)


def label(text="", size=14, color=WHITE, bold=False, halign="left", **kwargs):
    x = Label(
        text=text,
        font_size=dp(size),
        color=color,
        bold=bold,
        halign=halign,
        valign="middle",
        **kwargs
    )
    x.bind(size=lambda inst, val: setattr(inst, "text_size", (inst.width, None)))
    return x


def header(title, subtitle=""):
    box = BoxLayout(
        orientation="vertical",
        size_hint_y=None,
        height=dp(70),
        spacing=dp(2),
    )
    box.add_widget(label(title, 24, VIOLET, True, "center"))
    if subtitle:
        box.add_widget(label(subtitle, 11, MUTED, False, "center"))
    return box


def nav():
    box = BoxLayout(size_hint_y=None, height=dp(54), spacing=dp(5), padding=(dp(5), dp(4)))
    for text, screen in [
        ("HOME", "home"),
        ("GAMES", "game"),
        ("BOOST", "phone"),
        ("NET", "network"),
        ("DEVICE", "device"),
    ]:
        b = StyledButton(text=text, accent=PURPLE2, font_size=dp(10))
        b.bind(on_release=lambda _, s=screen: go(s))
        box.add_widget(b)
    return box


def go(screen):
    app = App.get_running_app()
    if app and app.root:
        app.root.current = screen


def show_popup(title, message):
    box = BoxLayout(orientation="vertical", padding=dp(15), spacing=dp(12))
    box.add_widget(label(message, 14, WHITE, False, "center"))
    close = StyledButton("OK", size_hint_y=None, height=dp(45))
    box.add_widget(close)
    pop = Popup(
        title=title,
        content=box,
        size_hint=(0.88, 0.45),
        separator_color=VIOLET,
    )
    close.bind(on_release=pop.dismiss)
    pop.open()


def stats():
    data = {
        "ram": None,
        "ram_total_gb": None,
        "cpu": None,
        "storage": None,
        "battery": None,
    }
    if psutil:
        try:
            memory = psutil.virtual_memory()
            data["ram"] = memory.percent
            data["ram_total_gb"] = memory.total / (1024 ** 3)
        except Exception:
            pass
        try:
            data["cpu"] = psutil.cpu_percent(interval=None)
        except Exception:
            pass
        try:
            data["storage"] = psutil.disk_usage("/").percent
        except Exception:
            try:
                data["storage"] = psutil.disk_usage(os.path.expanduser("~")).percent
            except Exception:
                pass

    if kivy_platform == "android":
        try:
            from jnius import autoclass
            PythonActivity = autoclass("org.kivy.android.PythonActivity")
            Context = autoclass("android.content.Context")
            MemoryInfo = autoclass("android.app.ActivityManager$MemoryInfo")
            activity = PythonActivity.mActivity
            activity_manager = activity.getSystemService(Context.ACTIVITY_SERVICE)
            memory = MemoryInfo()
            activity_manager.getMemoryInfo(memory)
            if memory.totalMem > 0:
                data["ram"] = 100.0 * (memory.totalMem - memory.availMem) / memory.totalMem
                data["ram_total_gb"] = memory.totalMem / (1024 ** 3)
        except Exception:
            pass
        try:
            from jnius import autoclass
            Environment = autoclass("android.os.Environment")
            StatFs = autoclass("android.os.StatFs")
            storage = StatFs(Environment.getDataDirectory().getAbsolutePath())
            total_bytes = storage.getTotalBytes()
            if total_bytes > 0:
                data["storage"] = 100.0 * (total_bytes - storage.getAvailableBytes()) / total_bytes
        except Exception:
            pass
        data["cpu"] = _android_cpu_percent()

    if psutil:
        try:
            b = psutil.sensors_battery()
            if b:
                data["battery"] = b.percent
        except Exception:
            pass

    if data["battery"] is None and kivy_platform == "android":
        try:
            from jnius import autoclass
            PythonActivity = autoclass("org.kivy.android.PythonActivity")
            Intent = autoclass("android.content.Intent")
            IntentFilter = autoclass("android.content.IntentFilter")
            activity = PythonActivity.mActivity
            intent = activity.registerReceiver(
                None, IntentFilter(Intent.ACTION_BATTERY_CHANGED)
            )
            level = intent.getIntExtra("level", -1)
            scale = intent.getIntExtra("scale", -1)
            if level >= 0 and scale > 0:
                data["battery"] = level * 100.0 / scale
        except Exception:
            pass
    return data


def _android_cpu_percent():
    global _cpu_sample, _cpu_sample_at, _cpu_percent_cached

    try:
        with open("/proc/stat", "r", encoding="ascii") as cpu_stats:
            fields = cpu_stats.readline().split()
        if not fields or fields[0] != "cpu":
            return None
        counters = [int(value) for value in fields[1:]]
        if len(counters) < 4:
            return None
    except Exception:
        return None

    now = time.monotonic()
    if _cpu_sample is None:
        _cpu_sample = counters
        _cpu_sample_at = now
        return None
    if now - _cpu_sample_at < 1.0:
        return _cpu_percent_cached

    previous = _cpu_sample
    total = sum(counters)
    previous_total = sum(previous)
    idle = counters[3] + (counters[4] if len(counters) > 4 else 0)
    previous_idle = previous[3] + (previous[4] if len(previous) > 4 else 0)
    total_delta = total - previous_total
    if total_delta > 0:
        _cpu_percent_cached = 100.0 * (total_delta - (idle - previous_idle)) / total_delta

    _cpu_sample = counters
    _cpu_sample_at = now
    return _cpu_percent_cached


def device_info():
    info = []
    if kivy_platform == "android":
        try:
            from jnius import autoclass
            Build = autoclass("android.os.Build")
            info += [
                ("Manufacturer", str(Build.MANUFACTURER)),
                ("Model", str(Build.MODEL)),
                ("Android", str(Build.VERSION.RELEASE)),
                ("SDK", str(Build.VERSION.SDK_INT)),
            ]
        except Exception:
            pass
    if not info:
        info += [
            ("System", host_platform.system()),
            ("Release", host_platform.release()),
            ("Machine", host_platform.machine()),
            ("Processor", host_platform.processor() or "Unknown"),
        ]
    info += [("Python", host_platform.python_version())]
    return info


def safe_cleanup():
    gc.collect()
    return "Safe app-memory cleanup completed. Android system apps were not force-killed."


def open_android_settings():
    if kivy_platform != "android":
        show_popup("ANDROID SETTINGS", "This action is available after building the APK.")
        return
    try:
        from jnius import autoclass
        PythonActivity = autoclass("org.kivy.android.PythonActivity")
        Intent = autoclass("android.content.Intent")
        Settings = autoclass("android.provider.Settings")
        PythonActivity.mActivity.startActivity(Intent(Settings.ACTION_SETTINGS))
    except Exception:
        show_popup("ANDROID SETTINGS", "Android Settings could not be opened.")
