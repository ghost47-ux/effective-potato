import json
import os
import threading
import time
import urllib.request
import urllib.error

from kivy.clock import Clock
from kivy.app import App
from kivy.metrics import dp
from kivy.properties import BooleanProperty
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.uix.switch import Switch
from kivy.uix.scrollview import ScrollView
from kivy.uix.image import Image

from common import (
    BackgroundRoot, Panel, StyledButton, label, header, nav, stats, device_info,
    open_android_settings, VIOLET, GREEN, MUTED, WHITE, PURPLE2, asset
)

try:
    from kivy.utils import platform as kivy_platform
except Exception:
    kivy_platform = "unknown"


class GamingGuardianScreen(Screen):
    online = BooleanProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._touch_start = None
        self._voice_busy = False
        app = App.get_running_app()
        data_dir = app.user_data_dir if app else os.path.dirname(os.path.abspath(__file__))
        self._config_path = os.path.join(data_dir, "guardian_config.json")
        root = BackgroundRoot()
        page = BoxLayout(orientation="vertical", padding=dp(10), spacing=dp(7))
        page.add_widget(header("AI GAMING GUARDIAN", "LIGHTWEIGHT • ONLINE / OFFLINE"))

        scroll = ScrollView()
        body = BoxLayout(orientation="vertical", padding=dp(7), spacing=dp(9), size_hint_y=None)
        body.bind(minimum_height=body.setter("height"))

        ai_header = Panel(orientation="horizontal", size_hint_y=None, height=dp(72), padding=dp(8), spacing=dp(8))
        logo_path = asset("smart.jpg")
        if os.path.exists(logo_path):
            ai_header.add_widget(Image(source=logo_path, size_hint_x=None, width=dp(56), allow_stretch=True, keep_ratio=True))
        else:
            ai_header.add_widget(label("SMART AI", 14, VIOLET, True, "center", size_hint_x=None, width=dp(70)))
        ai_header.add_widget(label("SMART GAMING AI\nDevice-aware strategy + performance guidance", 12, WHITE, True, "left"))
        body.add_widget(ai_header)

        mode = Panel(orientation="horizontal", size_hint_y=None, height=dp(62), padding=dp(10))
        mode.add_widget(label("ONLINE MODE  (Gemini)", 13, WHITE, True))
        self.mode_switch = Switch(active=False, size_hint_x=None, width=dp(60))
        self.mode_switch.bind(active=self.set_mode)
        mode.add_widget(self.mode_switch)
        mode.add_widget(label("OFFLINE = lightweight local monitoring + commands", 10, MUTED))
        body.add_widget(mode)

        key_panel = Panel(orientation="vertical", size_hint_y=None, height=dp(110), padding=dp(10))
        self.api_key = TextInput(hint_text="Your Gemini API key (optional)", password=True, multiline=False,
                                 size_hint_y=None, height=dp(42), background_color=(0.06, 0.02, 0.09, 1), foreground_color=WHITE)
        self.api_key.text = self.load_key()
        key_panel.add_widget(self.api_key)
        save = StyledButton("SAVE API KEY", accent=PURPLE2, size_hint_y=None, height=dp(42))
        save.bind(on_release=self.save_key)
        key_panel.add_widget(save)
        body.add_widget(key_panel)

        metrics = GridLayout(cols=2, spacing=dp(8), size_hint_y=None, height=dp(150))
        self.ram = self.metric("RAM")
        self.cpu = self.metric("CPU")
        self.temp = self.metric("TEMP")
        self.fps = self.metric("GAME FPS")
        for w in (self.ram, self.cpu, self.temp, self.fps):
            metrics.add_widget(w)
        body.add_widget(metrics)

        advice = Panel(orientation="vertical", size_hint_y=None, height=dp(185), padding=dp(12))
        advice.add_widget(label("DEVICE-SPECIFIC GAMING ADVICE", 15, VIOLET, True, "center"))
        self.advice = label("Scanning device...", 12, WHITE, False, "left")
        advice.add_widget(self.advice)
        refresh = StyledButton("REFRESH ADVICE", accent=(0.48, 0.12, 0.82, 1), size_hint_y=None, height=dp(44))
        refresh.bind(on_release=lambda *_: self.update_metrics())
        advice.add_widget(refresh)
        body.add_widget(advice)

        strategy = Panel(orientation="vertical", size_hint_y=None, height=dp(220), padding=dp(12), spacing=dp(6))
        strategy.add_widget(label("MATCH STRATEGY AI", 15, VIOLET, True, "center"))
        self.strategy_text = label(
            "Tell the Guardian your game and situation. Example: \"I am low health with 2 enemies nearby. What should I do?\"",
            11, WHITE, False, "left"
        )
        strategy.add_widget(self.strategy_text)
        strategy_btn = StyledButton("GET GAME STRATEGY", accent=(0.48, 0.12, 0.82, 1), size_hint_y=None, height=dp(44))
        strategy_btn.bind(on_release=self.get_strategy)
        strategy.add_widget(strategy_btn)
        body.add_widget(strategy)

        voice = Panel(orientation="vertical", size_hint_y=None, height=dp(150), padding=dp(12))
        voice.add_widget(label("VOICE GUARDIAN", 15, VIOLET, True, "center"))
        self.transcript = label("Say something like: 'Why is my game lagging?'", 12, MUTED, False, "center")
        voice.add_widget(self.transcript)
        speak = StyledButton("🎙  TALK TO GUARDIAN", accent=(0.25, 0.055, 0.40, 0.96), size_hint_y=None, height=dp(48))
        speak.bind(on_release=self.start_voice)
        voice.add_widget(speak)
        body.add_widget(voice)

        close_panel = Panel(orientation="vertical", size_hint_y=None, height=dp(125), padding=dp(12))
        close_panel.add_widget(label("APP CONTROL", 14, VIOLET, True, "center"))
        close_panel.add_widget(label("The Guardian can recommend closing a heavy app. Android may block automatic force-stop; if blocked, it will tell you to close the app manually.", 10, MUTED, False, "center"))
        settings_btn = StyledButton("OPEN APP / ACCESSIBILITY SETTINGS", accent=PURPLE2, size_hint_y=None, height=dp(42))
        settings_btn.bind(on_release=lambda *_: open_android_settings())
        close_panel.add_widget(settings_btn)
        body.add_widget(close_panel)

        scroll.add_widget(body)
        page.add_widget(scroll)
        page.add_widget(nav())
        root.add_widget(page)
        self.add_widget(root)
        self.bind(on_touch_down=self._swipe_down, on_touch_up=self._swipe_up)
        Clock.schedule_interval(lambda *_: self.update_metrics(), 2)
        Clock.schedule_once(lambda *_: self.update_metrics(), 0.4)

    def metric(self, title):
        card = Panel(orientation="vertical", padding=dp(8))
        card.add_widget(label(title, 10, MUTED, True, "center"))
        value = label("--", 18, WHITE, True, "center")
        card.add_widget(value)
        return card

    def set_mode(self, *_):
        self.online = bool(self.mode_switch.active)
        if self.online:
            self.advice.text = "Online mode enabled. Gemini is used only when you request AI reasoning."
        else:
            self.advice.text = "Offline mode: lightweight local monitoring and device-specific rules."

    def load_key(self):
        try:
            with open(self._config_path, "r", encoding="utf-8") as f:
                return json.load(f).get("gemini_api_key", "")
        except Exception:
            return ""

    def save_key(self, *_):
        try:
            os.makedirs(os.path.dirname(self._config_path), exist_ok=True)
            with open(self._config_path, "w", encoding="utf-8") as f:
                json.dump({"gemini_api_key": self.api_key.text.strip()}, f)
            self.transcript.text = "Gemini API key saved locally."
        except Exception as e:
            self.transcript.text = f"Could not save key: {e}"

    def _device_profile(self):
        s = stats()
        total_ram = s.get("ram_total_gb")
        cpu_count = os.cpu_count() or 1
        return s, total_ram, cpu_count, dict(device_info())

    def update_metrics(self):
        s, total_ram, cpu_count, info = self._device_profile()
        self.ram.children[0].text = f"{s['ram']:.0f}%" if s['ram'] is not None else "--"
        self.cpu.children[0].text = f"{s['cpu']:.0f}%" if s['cpu'] is not None else "--"
        self.temp.children[0].text = self._temperature_text()
        # We never fake a game's FPS. A normal Kivy app cannot universally read another game's internal FPS.
        self.fps.children[0].text = "--"
        self.advice.text = self._local_advice(s, total_ram, cpu_count, info)

    def _temperature_text(self):
        if kivy_platform != "android":
            return "--"
        try:
            from jnius import autoclass
            Activity = autoclass("org.kivy.android.PythonActivity")
            Intent = autoclass("android.content.Intent")
            Filter = autoclass("android.content.IntentFilter")
            intent = Activity.mActivity.registerReceiver(None, Filter(Intent.ACTION_BATTERY_CHANGED))
            # Battery temperature is tenths of a degree Celsius.
            t = intent.getIntExtra("temperature", -1)
            return f"{t / 10:.1f}°C" if t >= 0 else "--"
        except Exception:
            return "--"

    def _local_advice(self, s, total_ram, cpu_count, info):
        tips = []
        if s.get("ram") is not None and s["ram"] >= 85:
            tips.append("RAM pressure is high: close heavy background apps before gaming.")
        elif s.get("ram") is not None and s["ram"] >= 70:
            tips.append("RAM is getting busy: avoid opening extra apps while gaming.")
        if s.get("cpu") is not None and s["cpu"] >= 85:
            tips.append("CPU load is high: reduce graphics effects and background activity.")
        if s.get("storage") is not None and s["storage"] >= 90:
            tips.append("Storage is nearly full: free space to reduce system pressure.")
        if total_ram is not None and total_ram <= 2:
            tips.append("This is a low-RAM device: use lower graphics, shadows and effects for steadier frames.")
        elif total_ram is not None and total_ram <= 4:
            tips.append("For steadier frames, prefer medium/low graphics and limit background apps.")
        if not tips:
            tips.append("Device conditions look reasonable. Keep graphics at the highest setting that remains stable, not simply the highest setting available.")
        tips.append("Game FPS: direct reading is unavailable unless the device/game exposes it; the app will not invent an FPS number.")
        return "\n• " + "\n• ".join(tips)

    def get_strategy(self, *_):
        prompt = "Give me a practical strategy for my current match. Consider my device performance and avoid generic advice. Ask for the game/situation if it is missing."
        if self.online and self.api_key.text.strip():
            self.strategy_text.text = "Thinking about your device and match situation..."
            threading.Thread(target=self._ask_gemini_strategy, args=(prompt,), daemon=True).start()
        else:
            s, total_ram, cpu_count, info = self._device_profile()
            self.strategy_text.text = self._offline_strategy(s, total_ram, info)

    def _offline_strategy(self, s, total_ram, info):
        tips = []
        if total_ram is not None and total_ram <= 2:
            tips.append("Use low graphics and prioritize stable frame rate over visual quality.")
        if s.get("cpu") is not None and s["cpu"] >= 85:
            tips.append("Avoid unnecessary fights while the phone is under heavy CPU load; reduce effects and background activity.")
        if s.get("ram") is not None and s["ram"] >= 80:
            tips.append("Keep only the game active and close heavy background apps before the match.")
        if not tips:
            tips.append("Prioritize cover, controlled movement and stable aim; avoid unnecessary fights when you have a positional disadvantage.")
        tips.append("Tell the Guardian your game mode, health, weapons and nearby enemies for more specific offline guidance.")
        return "Offline strategy:\n• " + "\n• ".join(tips)

    def _ask_gemini_strategy(self, text):
        s, total_ram, cpu_count, info = self._device_profile()
        payload = {
            "contents": [{"parts": [{"text": (
                "You are DEIN-K PERFORMANCE X's gaming strategy assistant. "
                "Give practical, situation-specific gameplay strategy, not promises of winning. "
                "Use the supplied device information to keep advice realistic for the hardware. "
                "Do not invent game telemetry such as FPS. Keep the response concise and actionable. "
                f"User request: {text}\nDevice: {info}\nRAM: {s.get('ram')}%, CPU: {s.get('cpu')}%, "
                f"Storage: {s.get('storage')}%, Battery: {s.get('battery')}%, Total RAM GB: {total_ram}"
            )}]}]
        }
        data = json.dumps(payload).encode("utf-8")
        url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=" + self.api_key.text.strip()
        req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=15) as response:
                result = json.loads(response.read().decode("utf-8"))
            text_out = result["candidates"][0]["content"]["parts"][0]["text"]
        except Exception:
            text_out = "Gemini is unavailable. Offline strategy mode is still available."
        Clock.schedule_once(lambda *_: setattr(self.strategy_text, "text", "Online strategy:\n" + text_out), 0)

    def start_voice(self, *_):
        if self._voice_busy:
            return
        if kivy_platform != "android":
            self.transcript.text = "Voice input is available after building the Android APK."
            return
        self._voice_busy = True
        self.transcript.text = "Listening..."
        threading.Thread(target=self._voice_worker, daemon=True).start()

    def _voice_worker(self):
        try:
            from jnius import autoclass, PythonJavaClass, java_method
            SpeechRecognizer = autoclass("android.speech.SpeechRecognizer")
            Intent = autoclass("android.content.Intent")
            RecognizerIntent = autoclass("android.speech.RecognizerIntent")
            Activity = autoclass("org.kivy.android.PythonActivity")

            class Listener(PythonJavaClass):
                __javainterfaces__ = ["android/speech/RecognitionListener"]
                __javacontext__ = "app"
                def __init__(self, owner):
                    super().__init__()
                    self.owner = owner
                @java_method("()V")
                def onReadyForSpeech(self, params): pass
                @java_method("()V")
                def onBeginningOfSpeech(self): pass
                @java_method("()V")
                def onRmsChanged(self, rmsdB): pass
                @java_method("([B)V")
                def onBufferReceived(self, buffer): pass
                @java_method("()V")
                def onEndOfSpeech(self): pass
                @java_method("(I)V")
                def onError(self, error):
                    Clock.schedule_once(lambda *_: self.owner._voice_done("Voice recognition failed. Try again."), 0)
                @java_method("(Landroid/os/Bundle;)V")
                def onResults(self, results):
                    arr = results.getStringArrayList("results_recognition")
                    text = str(arr.get(0)) if arr and arr.size() else "No speech detected."
                    Clock.schedule_once(lambda *_: self.owner._voice_result(text), 0)
                @java_method("(Landroid/os/Bundle;)V")
                def onPartialResults(self, results): pass
                @java_method("(I[Landroid/os/Parcelable;)V")
                def onEvent(self, eventType, params): pass

            recognizer = SpeechRecognizer.createSpeechRecognizer(Activity.mActivity)
            listener = Listener(self)
            recognizer.setRecognitionListener(listener)
            intent = Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH)
            intent.putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL, RecognizerIntent.LANGUAGE_MODEL_FREE_FORM)
            intent.putExtra(RecognizerIntent.EXTRA_PREFER_OFFLINE, True)
            recognizer.startListening(intent)
            self._voice_recognizer = recognizer
            self._voice_listener = listener
        except Exception as e:
            Clock.schedule_once(lambda *_: self._voice_done(f"Voice input unavailable: {e}"), 0)

    def _voice_result(self, text):
        self.transcript.text = f"You said: {text}"
        self._voice_busy = False
        if self.online and self.api_key.text.strip():
            threading.Thread(target=self._ask_gemini, args=(text,), daemon=True).start()
        else:
            self._offline_command(text)

    def _voice_done(self, text):
        self.transcript.text = text
        self._voice_busy = False

    def _offline_command(self, text):
        low = text.lower()
        if "scan" in low or "lag" in low or "fps" in low or "slow" in low:
            self.update_metrics()
            self.transcript.text += "\nOffline Guardian: " + self.advice.text
        elif "settings" in low:
            open_android_settings()
        else:
            self.transcript.text += "\nOffline Guardian: I can monitor the device and handle supported local commands."

    def _ask_gemini(self, text):
        s, total_ram, cpu_count, info = self._device_profile()
        payload = {
            "contents": [{"parts": [{"text": (
                "You are the lightweight gaming guardian in DEIN-K PERFORMANCE X. "
                "Give concise, practical gaming advice based only on the supplied device state. "
                "Do not invent FPS. If an action such as force-stopping another app is not permitted by Android, say so. "
                f"User said: {text}\nDevice: {info}\nRAM: {s.get('ram')}%, CPU: {s.get('cpu')}%, "
                f"Storage: {s.get('storage')}%, Battery: {s.get('battery')}%, Total RAM GB: {total_ram}"
            )}]}]
        }
        data = json.dumps(payload).encode("utf-8")
        url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=" + self.api_key.text.strip()
        req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=15) as response:
                result = json.loads(response.read().decode("utf-8"))
            text_out = result["candidates"][0]["content"]["parts"][0]["text"]
            Clock.schedule_once(lambda *_: self._set_ai_answer(text_out), 0)
        except Exception as e:
            Clock.schedule_once(lambda *_: self._set_ai_answer("Gemini unavailable. Offline Guardian remains active."), 0)

    def _set_ai_answer(self, text):
        self.transcript.text += "\nGuardian: " + text

    def _swipe_down(self, instance, touch):
        if touch.y >= self.height * 0.86:
            self._touch_start = (touch.x, touch.y)
        return False

    def _swipe_up(self, instance, touch):
        if not self._touch_start:
            return False
        x0, y0 = self._touch_start
        self._touch_start = None
        if y0 >= self.height * 0.86 and touch.x < x0 - dp(70):
            # This is an in-app quick panel gesture. It does not intercept Android's system shade.
            self.advice.text = self._local_advice(*self._device_profile()[:3], self._device_profile()[3])
        return False
