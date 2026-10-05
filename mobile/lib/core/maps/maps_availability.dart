import 'package:flutter/foundation.dart';
import 'package:flutter/services.dart';

/// Whether this build has a Google Maps key (the Android manifest placeholder
/// MAPS_API_KEY, read from the git-ignored android/local.properties).
///
/// Only a yes/no crosses the platform channel, never the key. Where the
/// channel does not exist (tests, other platforms) the answer is no, and the
/// Map tab falls back to its legs list instead of creating a map.
abstract final class MapsAvailability {
  static const _channel = MethodChannel('tripmate/maps');
  static Future<bool>? _cached;

  static Future<bool> hasApiKey() => _cached ??= _check();

  static Future<bool> _check() async {
    try {
      return await _channel.invokeMethod<bool>('hasApiKey') ?? false;
    } on MissingPluginException {
      return false;
    } on PlatformException {
      return false;
    }
  }

  @visibleForTesting
  static void resetForTest() => _cached = null;
}
