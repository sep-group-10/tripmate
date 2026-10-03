import 'dart:convert';

import '../api/api_client.dart';
import '../models/user.dart';
import 'api_auth_repository.dart';
import 'profile_repository.dart';

/// [ProfileRepository] backed by `/api/v1/users/me`.
class ApiProfileRepository implements ProfileRepository {
  ApiProfileRepository(this._api, this._session);

  final ApiClient _api;
  final UserSession _session;

  User _store(dynamic data) =>
      _session.user = User.fromJson(data as Map<String, dynamic>);

  @override
  Future<User> getProfile() async => _store(await _api.get('/api/v1/users/me'));

  @override
  Future<User> updateName(String fullName) async => _store(
    await _api.put('/api/v1/users/me', body: {'full_name': fullName.trim()}),
  );

  @override
  Future<User> updatePreferences({
    required String budgetStyle,
    required String pace,
    required List<String> interests,
  }) async => _store(
    await _api.put(
      '/api/v1/users/me',
      body: {
        'typical_budget_range': budgetStyle,
        'preferred_pace': pace,
        'interests': interests,
      },
    ),
  );

  @override
  Future<String> exportData() async {
    final data = await _api.get('/api/v1/users/me/export');
    return const JsonEncoder.withIndent('  ').convert(data);
  }
}
