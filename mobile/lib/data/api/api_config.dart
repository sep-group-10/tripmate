/// Backend base URL. Defaults to the Android emulator's alias for the host
/// machine; override with `--dart-define=API_BASE_URL=http://<host>:8000`
/// (e.g. a LAN address for a physical device).
abstract final class ApiConfig {
  static const String baseUrl = String.fromEnvironment(
    'API_BASE_URL',
    defaultValue: 'http://10.0.2.2:8000',
  );

  static const Duration requestTimeout = Duration(seconds: 30);
}
