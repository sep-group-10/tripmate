import '../models/user.dart';

/// Account session. Methods throw [ApiException] (a [RepositoryException])
/// carrying the backend's error code, message and field details.
abstract class AuthRepository {
  /// The signed-in user (restoring the session from stored tokens on first
  /// use), or null when signed out.
  Future<User?> currentUser();

  Future<User> signIn({required String email, required String password});

  Future<void> register({
    required String fullName,
    required String email,
    required String password,
  });

  Future<void> resendVerification(String email);

  Future<void> requestPasswordReset(String email);

  /// Revokes the session on the server (best effort) and clears local tokens.
  Future<void> signOut();

  Future<void> changePassword({
    required String currentPassword,
    required String newPassword,
  });

  Future<void> deleteAccount({required String password});

  /// Fires when the session expired and could not be refreshed, so the UI
  /// should return to the login page.
  Stream<void> get sessionExpired;
}
