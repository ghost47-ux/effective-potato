# DEIN-K PERFORMANCE X

DEIN-K PERFORMANCE X is a Python mobile app built with Kivy and KivyMD. It brings basic device-health readings, gaming-oriented guidance, and a few practical phone checks together in one Android interface. The project is in `DEIN-K_PERFORMANCE_X_AI_GUARDIAN_v3/deink/`.

## What It Does

The app is intended as a lightweight companion for everyday phone use and mobile gaming. It helps answer practical questions such as “Is my phone under memory or CPU pressure?”, “Is this connection responding?”, and “Does the touchscreen register taps across the area I tested?” Its readings are informational: it does not have privileged access to tune Android, and it cannot promise that a game will run faster.

The app opens with an animated logo and then shows these screens:

- **Performance Center:** Displays available RAM, CPU, storage, and battery percentages; calculates a simple performance score from those readings; and offers a progress animation for its safe cleanup action.
- **Game Booster:** On Android, looks for installed apps marked as games and can launch apps that expose a launch activity. Package visibility restrictions may limit the results.
- **Phone Booster:** Shows the same basic health readings, performs Python garbage collection for this app, and can open Android Settings.
- **Network:** Measures the time to establish a TCP connection to `1.1.1.1:443`. This is a simple connectivity/latency indicator, not a ping to a particular game server.
- **Touch Tester:** Counts taps inside a test area and displays their coordinates.
- **Device Information:** Shows Android manufacturer/model/version details when available, with host-system information as a fallback.
- **Settings:** Describes the app's current visual setup and links to the advanced screen.
- **ADB / Shizuku:** Explains whether Shizuku is installed and clarifies that an ordinary app cannot grant itself ADB or Shizuku privileges.
- **AI Gaming Guardian:** Combines device readings with local gaming suggestions. Optional online strategy and voice-response features use the configured Gemini API key.

## How It Relates to Daily Use

Before starting a demanding game, a user can check whether memory or CPU use is already high, see whether storage is nearly full, and use the Guardian's device-aware suggestions to choose more realistic graphics settings or close background apps manually. If a game does not connect smoothly, the network check can distinguish a failed general connection from one that is responding slowly. The touch test can help spot areas of a screen that do not register taps consistently. Device information and the Settings shortcut are useful when troubleshooting or sharing basic device details.

These checks support decisions; they do not diagnose every cause of lag, repair hardware, change game settings, or control other apps. Android intentionally limits what a normal app can do to other processes and device performance.

## Project Layout

All app source and Android packaging configuration live in `DEIN-K_PERFORMANCE_X_AI_GUARDIAN_v3/deink/`:

- `main.py` creates the KivyMD app, registers screens, and handles Android back navigation.
- `common.py` contains shared colors, backgrounds, panels, buttons, navigation, dialogs, device readings, and Android helper functions.
- `intro.py` implements the animated logo screen.
- `home.py` implements the Performance Center and its summary score.
- `game.py` scans for and launches visible installed games on Android.
- `phone.py` implements the Phone Booster and Android Settings shortcut.
- `network.py` implements the TCP connection check and touchscreen test.
- `device.py` displays device information.
- `settings.py` displays the app settings summary.
- `advanced.py` provides ADB/Shizuku status and capability information.
- `gaming.py` implements the AI Gaming Guardian, local advice, optional Gemini requests, and voice recognition.
- `buildozer.spec` defines the Android package, dependencies, permissions, SDK targets, and included asset types.
- `assets/` contains the app background and image assets.

## Capabilities and Limitations

- **Performance readings:** Android RAM and storage use `ActivityManager` and `StatFs`; CPU is sampled from `/proc/stat` when available. Desktop readings use `psutil` if installed. Individual readings may be unavailable on some devices. The displayed score is a simple heuristic, not a benchmark or an Android system score.
- **Boost action:** The current safe cleanup calls Python garbage collection for this app. The home-screen progress bar is a UI animation; it does not represent measurable system optimization. The app does not force-stop other apps, clear their caches, overclock hardware, or alter Android power/network policy.
- **Game FPS and temperature:** FPS for another app is not fabricated; it is shown as unavailable. Battery temperature is shown only if Android exposes it through the battery status intent.
- **Game discovery:** Android package visibility controls what can be listed. The project requests `QUERY_ALL_PACKAGES` for broad discovery, but distribution through Google Play is subject to Google's package-visibility policy and review.
- **Voice:** Android's speech-recognition service is used when available. Recognition behavior and whether processing stays on-device depend on the installed recognition provider.
- **Gemini:** Online advice is optional. When requested, the app sends the prompt and gathered device readings to the Gemini API. The key is stored in the app's private data directory; it is not embedded in the APK. Do not use a key you are not authorized to use.
- **ADB/Shizuku:** These are informational integrations only. The app does not silently enable debugging, obtain root, or perform privileged actions.

## Android Permissions

The Buildozer configuration requests:

- `INTERNET` for the connection check and optional Gemini requests.
- `ACCESS_NETWORK_STATE` for network-related Android capabilities.
- `QUERY_ALL_PACKAGES` for broad installed-game discovery, subject to Android and store policy.
- `RECORD_AUDIO` for the Android voice-recognition feature.

Review these permissions and applicable store policies before publishing a build.

## Build an Android APK

Use Linux with Python 3.12, Java/JDK 21, Git, Buildozer, and the Android SDK/NDK. Buildozer downloads Android toolchain components on the first build, so allow time and disk space for that setup.

From the repository root:

```bash
cd DEIN-K_PERFORMANCE_X_AI_GUARDIAN_v3/deink
buildozer android debug
```

The debug APK is written under `DEIN-K_PERFORMANCE_X_AI_GUARDIAN_v3/deink/bin/`. The project targets Android API 34, supports Android API 26 and newer, and configures an ARM64 build. Install the resulting debug APK on a compatible device for runtime testing; a successful package build alone does not validate device-specific sensors, speech recognition, or package visibility.

## Desktop Source Check

Python syntax can be checked from the repository root with:

```bash
python -m compileall -q DEIN-K_PERFORMANCE_X_AI_GUARDIAN_v3/deink
```