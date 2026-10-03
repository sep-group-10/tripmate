import '../models/user.dart';

/// Methods throw [RepositoryException] with a message safe to show.
abstract class AuthRepository {
  /// The signed-in user, or null when signed out.
  Future<User?> currentUser();

  Future<User> signIn({required String email, required String password});

  Future<void> register({
    required String fullName,
    required String email,
    required String password,
  });

  Future<void> resendVerification(String email);

  Future<void> requestPasswordReset(String email);

  Future<void> signOut();

  Future<User> updateName(String fullName);

  Future<User> updatePreferences({
    required String budgetStyle,
    required String pace,
    required List<String> interests,
  });

  Future<void> changePassword({
    required String currentPassword,
    required String newPassword,
  });

  /// JSON text of everything held about the account.
  Future<String> exportData();

  Future<void> deleteAccount({required String password});
}
