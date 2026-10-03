import '../api/api_client.dart';
import '../api/api_exception.dart';
import '../models/user.dart';
import 'auth_repository.dart';

/// The signed-in user, shared by the auth and profile repositories so a
/// profile edit is visible to the router's session check.
class UserSession {
  User? user;
}

/// [AuthRepository] backed by `/api/v1/auth/*` and `GET /api/v1/users/me`.
class ApiAuthRepository implements AuthRepository {
  ApiAuthRepository(this._api, this._session);

  final ApiClient _api;
  final UserSession _session;

  @override
  Stream<void> get sessionExpired =>
      _api.sessionExpired.map((_) => _session.user = null);

  @override
  Future<User?> currentUser() async {
    final cached = _session.user;
    if (cached != null) return cached;
    final access = await _api.tokens.readAccessToken();
    final refresh = await _api.tokens.readRefreshToken();
    if ((access == null || access.isEmpty) &&
        (refresh == null || refresh.isEmpty)) {
      return null;
    }
    try {
      final data = await _api.get('/api/v1/users/me');
      return _session.user = User.fromJson(data as Map<String, dynamic>);
    } on ApiException catch (e) {
      // The client already cleared the tokens for an expired session; a
      // network failure keeps them so the next launch can try again.
      if (e.code == ApiException.networkErrorCode) rethrow;
      _session.user = null;
      return null;
    }
  }

  Future<User> _storeLogin(dynamic data) async {
    final map = data as Map<String, dynamic>;
    await _api.tokens.save(
      accessToken: map['access_token'] as String,
      refreshToken: map['refresh_token'] as String,
    );
    return _session.user = User.fromJson(map['user'] as Map<String, dynamic>);
  }

  @override
  Future<User> signIn({
    required String email,
    required String password,
  }) async => _storeLogin(
    await _api.post(
      '/api/v1/auth/login',
      body: {'email': email.trim(), 'password': password},
    ),
  );

  @override
  Future<void> register({
    required String fullName,
    required String email,
    required String password,
  }) async {
    await _api.post(
      '/api/v1/auth/register',
      body: {
        'full_name': fullName.trim(),
        'email': email.trim(),
        'password': password,
      },
    );
  }

  @override
  Future<void> resendVerification(String email) async {
    await _api.post(
      '/api/v1/auth/resend-verification',
      body: {'email': email.trim()},
    );
  }

  @override
  Future<void> requestPasswordReset(String email) async {
    await _api.post(
      '/api/v1/auth/forgot-password',
      body: {'email': email.trim()},
    );
  }

  @override
  Future<void> signOut() async {
    final refresh = await _api.tokens.readRefreshToken();
    try {
      // Always send the refresh token so the server can revoke it.
      await _api.post('/api/v1/auth/logout', body: {'refresh_token': ?refresh});
    } on ApiException {
      // Best effort, like the web: log out locally regardless.
    }
    await _api.tokens.clear();
    _session.user = null;
  }

  @override
  Future<void> changePassword({
    required String currentPassword,
    required String newPassword,
  }) async {
    // The backend rotates the session's tokens on success; keep the new pair.
    await _storeLogin(
      await _api.post(
        '/api/v1/auth/change-password',
        body: {
          'current_password': currentPassword,
          'new_password': newPassword,
        },
      ),
    );
  }

  @override
  Future<void> deleteAccount({required String password}) async {
    await _api.post(
      '/api/v1/auth/delete-account',
      body: {'current_password': password},
    );
    await _api.tokens.clear();
    _session.user = null;
  }
}
