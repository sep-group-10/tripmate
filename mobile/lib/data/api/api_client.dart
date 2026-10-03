import 'dart:async';
import 'dart:convert';

import 'package:http/http.dart' as http;

import 'api_config.dart';
import 'api_exception.dart';
import 'token_store.dart';

/// JSON client for the TripMate backend.
///
/// - Unwraps `{ success, data }` and throws [ApiException] for errors.
/// - Sends `Authorization: Bearer <access token>` on every request.
/// - On `401 TOKEN_EXPIRED` it calls `/api/v1/auth/refresh` once (shared by
///   concurrent requests, since refresh rotates the token) and retries the
///   request once. If the refresh fails, or a request gets `UNAUTHORIZED`,
///   the tokens are cleared and [sessionExpired] fires.
/// Mirrors web/src/services/api.js; see docs/auth-flow.md.
class ApiClient {
  ApiClient({
    required TokenStore tokenStore,
    http.Client? httpClient,
    String? baseUrl,
  }) : _tokens = tokenStore,
       _http = httpClient ?? http.Client(),
       _baseUrl = baseUrl ?? ApiConfig.baseUrl;

  static const _refreshPath = '/api/v1/auth/refresh';

  /// Public auth endpoints never trigger a refresh: a 401 from them is a real
  /// answer (wrong credentials, bad token), not an expired session.
  static const _publicAuthPaths = {
    '/api/v1/auth/login',
    '/api/v1/auth/register',
    '/api/v1/auth/google',
    _refreshPath,
    '/api/v1/auth/forgot-password',
    '/api/v1/auth/reset-password',
    '/api/v1/auth/verify-email',
    '/api/v1/auth/resend-verification',
  };

  final TokenStore _tokens;
  final http.Client _http;
  final String _baseUrl;
  final _sessionExpired = StreamController<void>.broadcast();
  Future<void>? _refreshing;

  TokenStore get tokens => _tokens;

  /// Fires when the session can no longer be recovered (tokens already
  /// cleared): the UI should go to the login page.
  Stream<void> get sessionExpired => _sessionExpired.stream;

  Future<dynamic> get(String path) => _request('GET', path);

  Future<dynamic> post(String path, {Map<String, dynamic>? body}) =>
      _request('POST', path, body: body);

  Future<dynamic> put(String path, {Map<String, dynamic>? body}) =>
      _request('PUT', path, body: body);

  Future<dynamic> patch(String path, {Map<String, dynamic>? body}) =>
      _request('PATCH', path, body: body);

  Future<dynamic> delete(String path) => _request('DELETE', path);

  Future<dynamic> _request(
    String method,
    String path, {
    Map<String, dynamic>? body,
    bool retried = false,
  }) async {
    final response = await _send(method, path, body);
    final decoded = _decode(response);

    if (response.statusCode >= 200 && response.statusCode < 300) {
      return decoded is Map ? decoded['data'] : null;
    }

    final error = ApiException.fromBody(
      decoded,
      statusCode: response.statusCode,
    );
    final isPublic = _publicAuthPaths.contains(path);

    if (response.statusCode == 401 && !isPublic) {
      if (error.code == 'TOKEN_EXPIRED' && !retried) {
        await _refreshSharing();
        return _request(method, path, body: body, retried: true);
      }
      if (error.code == 'TOKEN_EXPIRED' || error.code == 'UNAUTHORIZED') {
        await _expireSession();
      }
    }
    throw error;
  }

  Future<http.Response> _send(
    String method,
    String path,
    Map<String, dynamic>? body,
  ) async {
    final headers = <String, String>{
      'Accept': 'application/json',
      if (body != null) 'Content-Type': 'application/json',
    };
    final token = await _tokens.readAccessToken();
    if (token != null && token.isNotEmpty) {
      headers['Authorization'] = 'Bearer $token';
    }

    final request = http.Request(method, Uri.parse('$_baseUrl$path'))
      ..headers.addAll(headers);
    if (body != null) request.body = jsonEncode(body);

    try {
      final streamed = await _http
          .send(request)
          .timeout(ApiConfig.requestTimeout);
      return await http.Response.fromStream(streamed);
    } on Exception {
      // Socket errors, timeouts, DNS failures: the server was not reached.
      throw ApiException.network();
    }
  }

  Object? _decode(http.Response response) {
    if (response.body.isEmpty) return null;
    try {
      return jsonDecode(utf8.decode(response.bodyBytes));
    } on FormatException {
      return null;
    }
  }

  /// One in-flight refresh shared by all requests that hit TOKEN_EXPIRED.
  Future<void> _refreshSharing() {
    return _refreshing ??= _refresh().whenComplete(() => _refreshing = null);
  }

  Future<void> _refresh() async {
    final refreshToken = await _tokens.readRefreshToken();
    if (refreshToken == null || refreshToken.isEmpty) {
      await _expireSession();
      throw const ApiException(
        code: 'INVALID_REFRESH_TOKEN',
        message: 'Your session has expired. Please log in again.',
      );
    }
    try {
      final data = await _request(
        'POST',
        _refreshPath,
        body: {'refresh_token': refreshToken},
      );
      await _tokens.save(
        accessToken: data['access_token'] as String,
        refreshToken: data['refresh_token'] as String,
      );
    } on ApiException catch (e) {
      // A network failure leaves the session alone; anything else from the
      // refresh endpoint (INVALID_REFRESH_TOKEN, ACCOUNT_DEACTIVATED) means
      // the user has to log in again.
      if (e.code != ApiException.networkErrorCode) await _expireSession();
      rethrow;
    }
  }

  Future<void> _expireSession() async {
    await _tokens.clear();
    _sessionExpired.add(null);
  }

  void close() {
    _http.close();
    _sessionExpired.close();
  }
}
