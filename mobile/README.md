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

The app reads the backend URL from the `API_BASE_URL` compile-time variable
(see [lib/utils/constants.dart](lib/utils/constants.dart)), defaulting to
`http://localhost:8000`. To reach a backend running on your development
machine from a physical Android device, use one of the two methods below.

### Method 1: ADB Reverse Port Forwarding (USB)

Forwards the device's `localhost:8000` to your machine's `localhost:8000`,
so the app can use the default `localhost` URL unchanged.

```bash
adb devices                     # confirm device is connected
adb reverse tcp:8000 tcp:8000   # create the tunnel
adb reverse --list              # verify
```

Run the backend normally (`uvicorn main:app --port 8000`) and launch the app:

```bash
flutter run
```

Remove the tunnel when done:

```bash
adb reverse --remove tcp:8000
```

**Pros:** no IP/firewall/Wi-Fi dependency, works with the default `localhost` URL, doesn't expose the backend on the network.

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
