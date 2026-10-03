import 'dart:convert';

import '../../api/api_exception.dart';
import '../../mock/mock_delay.dart';
import '../../mock/mock_trips.dart';
import '../../models/user.dart';
import '../auth_repository.dart';
import '../profile_repository.dart';

/// In-memory auth and profile for tests and offline UI work. One instance can
/// be passed as both the [AuthRepository] and the [ProfileRepository].
class MockAuthRepository implements AuthRepository, ProfileRepository {
  final Map<String, String> _passwords = {
    MockAccount.user.email: MockAccount.password,
  };
  final Map<String, User> _users = {MockAccount.user.email: MockAccount.user};
  User? _current;

  User get _signedIn {
    final user = _current;
    if (user == null) {
      throw const ApiException(
        code: 'UNAUTHORIZED',
        message: 'Authentication required',
      );
    }
    return user;
  }

  @override
  Stream<void> get sessionExpired => const Stream.empty();

  @override
  Future<User?> currentUser() async {
    await mockDelay(150);
    return _current;
  }

  @override
  Future<User> signIn({required String email, required String password}) async {
    await mockDelay(600);
    final key = email.trim().toLowerCase();
    if (_passwords[key] != password) {
      throw const ApiException(
        code: 'INVALID_CREDENTIALS',
        message: 'Invalid email or password',
      );
    }
    return _current = _users[key]!;
  }

  @override
  Future<void> register({
    required String fullName,
    required String email,
    required String password,
  }) async {
    await mockDelay(600);
    final key = email.trim().toLowerCase();
    if (_users.containsKey(key)) {
      throw const ApiException(
        code: 'EMAIL_ALREADY_EXISTS',
        message: 'Email is already registered',
      );
    }
    _passwords[key] = password;
    _users[key] = User(
      id: 'u${_users.length + 1}',
      name: fullName.trim(),
      email: key,
    );
  }

  @override
  Future<void> resendVerification(String email) => mockDelay(400);

  @override
  Future<void> requestPasswordReset(String email) => mockDelay(500);

  @override
  Future<void> signOut() async {
    await mockDelay(200);
    _current = null;
  }

  @override
  Future<User> getProfile() async {
    await mockDelay(200);
    return _signedIn;
  }

  @override
  Future<User> updateName(String fullName) async {
    await mockDelay(400);
    final user = _signedIn.copyWith(name: fullName.trim());
    return _current = _users[user.email] = user;
  }

  @override
  Future<User> updatePreferences({
    required String budgetStyle,
    required String pace,
    required List<String> interests,
  }) async {
    await mockDelay(400);
    final user = _signedIn.copyWith(
      budgetStyle: budgetStyle,
      pace: pace,
      interests: interests,
    );
    return _current = _users[user.email] = user;
  }

  @override
  Future<void> changePassword({
    required String currentPassword,
    required String newPassword,
  }) async {
    await mockDelay(500);
    final email = _signedIn.email;
    if (_passwords[email] != currentPassword) {
      throw const ApiException(
        code: 'INVALID_CREDENTIALS',
        message: 'Current password is incorrect',
      );
    }
    _passwords[email] = newPassword;
  }

  @override
  Future<String> exportData() async {
    await mockDelay(500);
    final user = _signedIn;
    return const JsonEncoder.withIndent('  ').convert({
      'profile': {
        'full_name': user.name,
        'email': user.email,
        'typical_budget_range': user.budgetStyle,
        'preferred_pace': user.pace,
        'interests': user.interests,
      },
      'trips': <Object>[],
      'feedback': <Object>[],
    });
  }

  @override
  Future<void> deleteAccount({required String password}) async {
    await mockDelay(500);
    final email = _signedIn.email;
    if (_passwords[email] != password) {
      throw const ApiException(
        code: 'INVALID_CREDENTIALS',
        message: 'Current password is incorrect',
      );
    }
    _passwords.remove(email);
    _users.remove(email);
    _current = null;
  }
}
