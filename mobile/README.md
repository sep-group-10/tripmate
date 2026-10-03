# Mobile App

Flutter client for the backend API.

## Prerequisites

- Flutter SDK (Dart ^3.13.0)
- Android device or emulator
- Backend running locally (see `backend/`)

## Setup

```bash
flutter pub get
```

## Backend Connection Setup

Auth and profile talk to the real backend (`docker compose up` in `backend/`,
then seed with `python -m app.core.seed`); My trips is still mock data. AI chat
talks to `POST /api/v1/chat` (needs `OPENROUTER_API_KEY` in `backend/.env`); run
with `--dart-define=MOCK_CHAT=true` to use the in-app mock chat instead.
Demo account: `tourist@demo.com` / `Demo1234`.

The app reads the backend URL from the `API_BASE_URL` compile-time variable
(see [lib/data/api/api_config.dart](lib/data/api/api_config.dart)), defaulting
to `http://10.0.2.2:8000`, which is how the **Android emulator** reaches the
backend on your machine. Plain HTTP is allowed in debug builds only. For a
physical device use one of the methods below (with `adb reverse` pass
`--dart-define=API_BASE_URL=http://localhost:8000`).

### Method 1: ADB Reverse Port Forwarding (USB)

Forwards the device's `localhost:8000` to your machine's `localhost:8000`,
so the app can use `http://localhost:8000`.

```bash
adb devices                     # confirm device is connected
adb reverse tcp:8000 tcp:8000   # create the tunnel
adb reverse --list              # verify
```

Run the backend and launch the app:

```bash
flutter run --dart-define=API_BASE_URL=http://localhost:8000
```

Remove the tunnel when done:

```bash
adb reverse --remove tcp:8000
```

**Pros:** no IP/firewall/Wi-Fi dependency, doesn't expose the backend on the network.

### Method 2: Direct LAN IP

Use when testing over Wi-Fi or with multiple devices at once.

1. Find your machine's LAN IP:

   ```bash
   hostname -I        # Linux
   ```

2. Run the backend bound to all interfaces:

   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000
   ```

3. Run the app pointing at that IP:

   ```bash
   flutter run --dart-define=API_BASE_URL=http://192.168.1.25:8000
   ```

Device and machine must be on the same Wi-Fi network.

## Running Tests

```bash
flutter test
```
