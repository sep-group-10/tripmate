import '../models/user.dart';

/// The signed-in user's own profile (`/api/v1/users/me`).
abstract class ProfileRepository {
  Future<User> getProfile();

  Future<User> updateName(String fullName);

  Future<User> updatePreferences({
    required String budgetStyle,
    required String pace,
    required List<String> interests,
  });

  /// Pretty-printed JSON of everything the backend holds about the account.
  Future<String> exportData();
}
