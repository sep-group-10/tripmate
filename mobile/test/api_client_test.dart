import 'dart:convert';

import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:mobile/data/api/api_client.dart';
import 'package:mobile/data/api/api_exception.dart';
import 'package:mobile/data/api/token_store.dart';
import 'package:mobile/data/models/user.dart';
import 'package:mobile/data/repositories/api_auth_repository.dart';
import 'package:mobile/data/repositories/api_profile_repository.dart';

http.Response _json(int status, Object body) => http.Response(
  jsonEncode(body),
  status,
  headers: {'content-type': 'application/json'},
);

Map<String, dynamic> _error(String code, String message, [List? details]) => {
  'success': false,
  'error': {'code': code, 'message': message, 'details': ?details},
};

Map<String, dynamic> _userJson({String name = 'Nimali Perera'}) => {
  'id': 'u1',
  'full_name': name,
  'email': 'tourist@demo.com',
  'role': 'TOURIST',
  'typical_budget_range': null,
  'preferred_pace': 'Packed',
  'interests': null,
  'profile_picture_url': null,
};

ApiClient _client(MockClient mock, MemoryTokenStore tokens) =>
    ApiClient(tokenStore: tokens, httpClient: mock, baseUrl: 'http://test');

void main() {
  test('unwraps data and sends the Bearer token', () async {
    final tokens = MemoryTokenStore()
      ..accessToken = 'a1'
      ..refreshToken = 'r1';
    late http.BaseRequest seen;
    final api = _client(
      MockClient((request) async {
        seen = request;
        return _json(200, {
          'success': true,
          'data': {'ok': 1},
        });
      }),
      tokens,
    );

    expect(await api.get('/api/v1/users/me'), {'ok': 1});
    expect(seen.headers['Authorization'], 'Bearer a1');
    expect(seen.url.toString(), 'http://test/api/v1/users/me');
  });

  test('throws ApiException with code, message and field details', () async {
    final api = _client(
      MockClient(
        (_) async => _json(
          400,
          _error('VALIDATION_ERROR', 'Some fields are invalid', [
            {'field': 'full_name', 'message': 'Field required'},
          ]),
        ),
      ),
      MemoryTokenStore(),
    );

    await expectLater(
      api.post('/api/v1/auth/register', body: {}),
      throwsA(
        isA<ApiException>()
            .having((e) => e.code, 'code', 'VALIDATION_ERROR')
            .having((e) => e.message, 'message', 'Some fields are invalid')
            .having(
              (e) => e.detailFor('full_name'),
              'detail',
              'Field required',
            ),
      ),
    );
  });

  test('network failure becomes the web\'s "Could not reach" error', () async {
    final api = _client(
      MockClient((_) async => throw http.ClientException('down')),
      MemoryTokenStore(),
    );
    await expectLater(
      api.get('/health'),
      throwsA(
        isA<ApiException>()
            .having((e) => e.code, 'code', ApiException.networkErrorCode)
            .having(
              (e) => e.message,
              'message',
              ApiException.networkErrorMessage,
            ),
      ),
    );
  });

  test(
    'TOKEN_EXPIRED refreshes once, stores the new pair and retries',
    () async {
      final tokens = MemoryTokenStore()
        ..accessToken = 'old'
        ..refreshToken = 'r1';
      var refreshCalls = 0;
      final api = _client(
        MockClient((request) async {
          if (request.url.path == '/api/v1/auth/refresh') {
            refreshCalls++;
            expect(jsonDecode(request.body), {'refresh_token': 'r1'});
            return _json(200, {
              'success': true,
              'data': {'access_token': 'new', 'refresh_token': 'r2'},
            });
          }
          return request.headers['Authorization'] == 'Bearer new'
              ? _json(200, {
                  'success': true,
                  'data': {'ok': true},
                })
              : _json(401, _error('TOKEN_EXPIRED', 'Access token has expired'));
        }),
        tokens,
      );

      // Two concurrent requests share one refresh (it rotates the token).
      final results = await Future.wait([
        api.get('/api/v1/trips'),
        api.get('/api/v1/users/me'),
      ]);
      expect(results, [
        {'ok': true},
        {'ok': true},
      ]);
      expect(refreshCalls, 1);
      expect(tokens.accessToken, 'new');
      expect(tokens.refreshToken, 'r2');
    },
  );

  test(
    'INVALID_REFRESH_TOKEN clears tokens and signals session expiry',
    () async {
      final tokens = MemoryTokenStore()
        ..accessToken = 'old'
        ..refreshToken = 'r1';
      final api = _client(
        MockClient(
          (request) async => request.url.path == '/api/v1/auth/refresh'
              ? _json(
                  401,
                  _error('INVALID_REFRESH_TOKEN', 'Invalid refresh token'),
                )
              : _json(401, _error('TOKEN_EXPIRED', 'Access token has expired')),
        ),
        tokens,
      );
      final expired = expectLater(api.sessionExpired, emits(null));

      await expectLater(
        api.get('/api/v1/users/me'),
        throwsA(
          isA<ApiException>().having(
            (e) => e.code,
            'code',
            'INVALID_REFRESH_TOKEN',
          ),
        ),
      );
      await expired;
      expect(tokens.accessToken, isNull);
      expect(tokens.refreshToken, isNull);
    },
  );

  test(
    'UNAUTHORIZED clears tokens, but a wrong login does not refresh',
    () async {
      final tokens = MemoryTokenStore()
        ..accessToken = 'a'
        ..refreshToken = 'r';
      var calls = 0;
      final api = _client(
        MockClient((request) async {
          calls++;
          return request.url.path.endsWith('/login')
              ? _json(
                  401,
                  _error('INVALID_CREDENTIALS', 'Invalid email or password'),
                )
              : _json(401, _error('UNAUTHORIZED', 'Invalid access token'));
        }),
        tokens,
      );

      await expectLater(
        api.post('/api/v1/auth/login', body: {}),
        throwsA(
          isA<ApiException>().having(
            (e) => e.code,
            'code',
            'INVALID_CREDENTIALS',
          ),
        ),
      );
      expect(calls, 1);
      expect(tokens.accessToken, 'a');

      await expectLater(
        api.get('/api/v1/users/me'),
        throwsA(isA<ApiException>()),
      );
      expect(tokens.accessToken, isNull);
    },
  );

  test('User.fromJson applies the web profile defaults', () {
    final user = User.fromJson(_userJson());
    expect(user.name, 'Nimali Perera');
    expect(user.budgetStyle, 'Moderate');
    expect(user.pace, 'Packed');
    expect(user.interests, ['Culture', 'Nature', 'Food']);
  });

  test(
    'login stores tokens, logout sends the refresh token and clears them',
    () async {
      final tokens = MemoryTokenStore();
      Map<String, dynamic>? logoutBody;
      final api = _client(
        MockClient((request) async {
          final body = request.body;
          switch (request.url.path) {
            case '/api/v1/auth/login':
              return _json(200, {
                'success': true,
                'data': {
                  'access_token': 'a',
                  'refresh_token': 'r',
                  'user': _userJson(),
                },
              });
            case '/api/v1/auth/logout':
              logoutBody = jsonDecode(body) as Map<String, dynamic>;
              return _json(200, {'success': true, 'data': {}});
          }
          return _json(404, _error('NOT_FOUND', 'nope'));
        }),
        tokens,
      );
      final session = UserSession();
      final auth = ApiAuthRepository(api, session);

      final user = await auth.signIn(email: 'a@b.co', password: 'pw');
      expect(user.email, 'tourist@demo.com');
      expect(tokens.accessToken, 'a');
      expect((await auth.currentUser())?.id, 'u1');

      await auth.signOut();
      expect(logoutBody, {'refresh_token': 'r'});
      expect(tokens.accessToken, isNull);
      expect(await auth.currentUser(), isNull);
    },
  );

  test('profile update sends only full_name and maps the response', () async {
    final tokens = MemoryTokenStore()..accessToken = 'a';
    Object? sent;
    final api = _client(
      MockClient((request) async {
        sent = jsonDecode(request.body);
        return _json(200, {
          'success': true,
          'data': _userJson(name: 'Nimali P'),
        });
      }),
      tokens,
    );
    final profile = ApiProfileRepository(api, UserSession());

    final user = await profile.updateName('  Nimali P ');
    expect(sent, {'full_name': 'Nimali P'});
    expect(user.name, 'Nimali P');
  });
}
