import 'dart:async';
import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:mobile/app.dart';
import 'package:mobile/data/api/api_client.dart';
import 'package:mobile/data/api/api_exception.dart';
import 'package:mobile/data/api/token_store.dart';
import 'package:mobile/data/mock/mock_plan.dart';
import 'package:mobile/data/models/chat_reply.dart';
import 'package:mobile/data/models/itinerary_item.dart';
import 'package:mobile/data/repositories/api_chat_repository.dart';
import 'package:mobile/data/repositories/chat_repository.dart';
import 'package:mobile/data/repositories/mock/mock_auth_repository.dart';
import 'package:mobile/data/repositories/mock/mock_chat_repository.dart';
import 'package:mobile/features/chat/chat_errors.dart';

Map<String, dynamic> _chatData({
  String status = 'completed',
  String? progressMessage,
  int progress = 100,
  Map<String, dynamic>? itinerary,
  String message = 'Your trip plan is ready.',
}) => {
  'assistant_message': message,
  'session': {
    'id': 's1',
    'status': status,
    'iteration_count': 0,
    'progress_message': progressMessage,
    'progress_percentage': progress,
  },
  'itinerary': itinerary,
};

final _itinerary = {
  'status': 'partial',
  'hotel_by_destination': {},
  'warnings': ['Heads up'],
  'unscheduled': [
    {
      'candidate_id': 'u1',
      'name': 'World Buddhist Museum',
      'category': 'attraction',
      'reason': 'no day had a fitting, open time slot',
    },
  ],
  'days': [
    {
      'day_number': 1,
      'date': '2026-11-10',
      'day_type': 'arrival',
      'hotel_id': null,
      'hotel_location': null,
      'warnings': ['Tight schedule'],
      'route_optimization': {'local_distance_km': 3.2},
      'items': [
        {
          'candidate_id': 'a1',
          'category': 'attraction',
          'name': 'Temple of the Sacred Tooth Relic',
          'start_time': '09:00',
          'end_time': '11:00',
          'latitude': 7.2936,
          'longitude': 80.6413,
        },
        {
          'candidate_id': 'x1',
          'category': 'transport_hub',
          'name': 'Kandy station',
          'start_time': '12:00',
          'end_time': '12:30',
          'latitude': null,
          'longitude': null,
        },
      ],
    },
  ],
};

class _Seen {
  String? method;
  String? path;
  Object? body;
}

(ApiChatRepository, _Seen) _repo(http.Response Function() reply) {
  final seen = _Seen();
  final api = ApiClient(
    tokenStore: MemoryTokenStore()..accessToken = 'a',
    baseUrl: 'http://test',
    httpClient: MockClient((request) async {
      seen
        ..method = request.method
        ..path = request.url.path
        ..body = jsonDecode(request.body);
      return reply();
    }),
  );
  return (ApiChatRepository(api, resumeFallback: MockChatRepository()), seen);
}

http.Response _ok(Object data) =>
    http.Response(jsonEncode({'success': true, 'data': data}), 200);

http.Response _err(int status, String code, String message) => http.Response(
  jsonEncode({
    'success': false,
    'error': {'code': code, 'message': message},
  }),
  status,
);

/// Chat repository that replays scripted outcomes.
class _Scripted implements ChatRepository {
  _Scripted(this.outcomes);

  final List<Object> outcomes;
  final texts = <String>[];

  @override
  Future<ChatReply> sendMessage(String text, {String? sessionId}) async {
    texts.add(text);
    final outcome = outcomes.removeAt(0);
    if (outcome is ChatReply) return outcome;
    throw outcome;
  }

  @override
  Future<List<ChatMessage>> resumeTrip(String tripId) async => const [];
}

Future<void> _openChat(WidgetTester tester, ChatRepository chat) async {
  tester.view
    ..physicalSize = const Size(400, 3000)
    ..devicePixelRatio = 1;
  addTearDown(tester.view.reset);
  final auth = MockAuthRepository();
  // Mock delays are real timers, so run the sign-in outside fake time.
  await tester.runAsync(
    () => auth.signIn(email: 'nimali@example.com', password: 'password123'),
  );
  await tester.pumpWidget(
    TripMateApp(
      useWebFonts: false,
      authRepository: auth,
      profileRepository: auth,
      chatRepository: chat,
    ),
  );
  await tester.pump(const Duration(seconds: 1));
  await tester.pumpAndSettle();
}

Future<void> _send(WidgetTester tester, String text) async {
  await tester.enterText(find.byType(TextField).last, text);
  await tester.pump();
  await tester.tap(find.byIcon(Icons.send_rounded));
  await tester.pumpAndSettle();
}

void main() {
  group('ApiChatRepository', () {
    test(
      'first message POSTs /chat, follow-ups POST /chat/{session}',
      () async {
        final (repo, seen) = _repo(() => _ok(_chatData()));

        await repo.sendMessage('Plan Kandy');
        expect((seen.method, seen.path), ('POST', '/api/v1/chat'));
        expect(seen.body, {'message': 'Plan Kandy'});

        await repo.sendMessage('Swap a day', sessionId: 's1');
        expect(seen.path, '/api/v1/chat/s1');
      },
    );

    test('maps the itinerary, unscheduled items and warnings', () async {
      final (repo, _) = _repo(() => _ok(_chatData(itinerary: _itinerary)));
      final reply = await repo.sendMessage('Plan');

      expect(reply.sessionId, 's1');
      final plan = reply.plan!;
      expect(plan.days, hasLength(1));
      final day = plan.days.single;
      expect(day.dayType, 'arrival');
      expect(day.distanceKm, 3.2);
      expect(day.warnings, ['Tight schedule']);
      expect(day.items.first.type, ItineraryItemType.attraction);
      expect(day.items.first.hasCoordinates, isTrue);
      expect(day.items.first.startTime, '09:00');
      expect(day.items.last.type, ItineraryItemType.other);
      expect(day.items.last.rawCategory, 'transport_hub');
      expect(day.items.last.hasCoordinates, isFalse);
      expect(plan.unscheduled.single.name, 'World Buddhist Museum');
      expect(plan.warnings, ['Heads up']);
      // Summary and Budget are placeholders, like the web.
      expect(plan.summary, same(mockPlan.summary));
      expect(plan.budget, same(mockPlan.budget));
    });

    test(
      'a clarifying question has no plan; progress is passed through',
      () async {
        final (repo, _) = _repo(
          () => _ok(
            _chatData(
              status: 'pending',
              progressMessage: 'Choosing hotels',
              progress: 60,
              message: 'When are you travelling?',
            ),
          ),
        );
        final reply = await repo.sendMessage('Plan');
        expect(reply.plan, isNull);
        expect(reply.progressMessage, 'Choosing hotels');
        expect(reply.progressPercent, 60);
      },
    );

    test('backend errors keep their code', () async {
      final (repo, _) = _repo(
        () => _err(503, 'EXTERNAL_SERVICE_UNAVAILABLE', 'LLM down'),
      );
      await expectLater(
        repo.sendMessage('Plan'),
        throwsA(
          isA<ApiException>().having(
            (e) => e.code,
            'code',
            'EXTERNAL_SERVICE_UNAVAILABLE',
          ),
        ),
      );
    });

    test(
      'a request that exceeds the timeout becomes REQUEST_TIMEOUT',
      () async {
        final api = ApiClient(
          tokenStore: MemoryTokenStore(),
          baseUrl: 'http://test',
          httpClient: MockClient(
            (_) => Completer<http.Response>().future, // never answers
          ),
        );
        await expectLater(
          api.post(
            '/api/v1/chat',
            body: {'message': 'x'},
            timeout: const Duration(milliseconds: 50),
          ),
          throwsA(
            isA<ApiException>().having(
              (e) => e.code,
              'code',
              ApiException.timeoutErrorCode,
            ),
          ),
        );
      },
    );
  });

  group('describeChatError (web chatErrors.js)', () {
    ApiException error(String code, {int? status}) =>
        ApiException(code: code, message: 'x', statusCode: status);

    test('auth codes show nothing', () {
      for (final code in [
        'TOKEN_EXPIRED',
        'UNAUTHORIZED',
        'INVALID_REFRESH_TOKEN',
      ]) {
        expect(describeChatError(error(code)).isAuth, isTrue);
      }
      expect(describeChatError(error('X', status: 401)).isAuth, isTrue);
    });

    test('NOT_FOUND resets the session, VALIDATION_ERROR is not retryable', () {
      final notFound = describeChatError(error('NOT_FOUND'));
      expect(notFound.resetSession, isTrue);
      expect(notFound.retryable, isTrue);
      expect(describeChatError(error('VALIDATION_ERROR')).retryable, isFalse);
      expect(describeChatError(error('RATE_LIMITED')).retryable, isTrue);
    });

    test('service errors, planning failures and timeouts are retryable', () {
      expect(
        describeChatError(error('EXTERNAL_SERVICE_UNAVAILABLE')).text,
        plannerUnreachableText,
      );
      expect(
        describeChatError(error('PLANNING_FAILED')).text,
        planningFailedText,
      );
      expect(
        describeChatError(ApiException.timeout()).text,
        planningTimeoutText,
      );
      expect(describeChatError(ApiException.network()).retryable, isTrue);
      expect(
        describeChatError(StateError('boom')).text,
        plannerUnreachableText,
      );
    });
  });

  group('chat UI', () {
    testWidgets('a service error shows the web message with Retry', (
      tester,
    ) async {
      final chat = _Scripted([
        const ApiException(
          code: 'EXTERNAL_SERVICE_UNAVAILABLE',
          message: 'LLM down',
        ),
        const ChatReply(
          assistantMessage: 'Here you go.',
          sessionId: 's1',
          status: 'pending',
        ),
      ]);
      await _openChat(tester, chat);

      await _send(tester, 'Plan Kandy');
      expect(find.text(plannerUnreachableText), findsOneWidget);
      expect(find.text('Retry'), findsOneWidget);

      await tester.tap(find.text('Retry'));
      await tester.pumpAndSettle();
      expect(chat.texts, ['Plan Kandy', 'Plan Kandy']);
      expect(find.text('Here you go.'), findsOneWidget);
      expect(find.text(plannerUnreachableText), findsNothing);
    });

    testWidgets('a failed plan shows the message without Retry', (
      tester,
    ) async {
      await _openChat(
        tester,
        _Scripted([
          const ChatReply(
            assistantMessage:
                'I\'m sorry, but I couldn\'t complete your trip plan.',
            sessionId: 's1',
            status: 'failed',
          ),
        ]),
      );
      await _send(tester, 'Plan Ella and Kandy');
      expect(
        find.textContaining('couldn\'t complete your trip plan'),
        findsOneWidget,
      );
      expect(find.text('Retry'), findsNothing);
    });

    testWidgets('a slow plan shows a still-working note, then the progress', (
      tester,
    ) async {
      final slow = Completer<ChatReply>();
      final chat = _SlowChat(slow);
      await _openChat(tester, chat);

      await tester.enterText(find.byType(TextField).last, 'Plan Kandy');
      await tester.pump();
      await tester.tap(find.byIcon(Icons.send_rounded));
      await tester.pump(const Duration(seconds: 1));
      expect(find.text('TripMate is thinking…'), findsOneWidget);
      expect(find.textContaining('Still working'), findsNothing);

      await tester.pump(const Duration(seconds: 25));
      expect(find.textContaining('Still working'), findsOneWidget);

      slow.complete(
        const ChatReply(
          assistantMessage: 'Done.',
          sessionId: 's1',
          status: 'completed',
          progressMessage: 'Plan ready',
        ),
      );
      await tester.pumpAndSettle();
      expect(find.textContaining('Still working'), findsNothing);
      expect(find.text('Done.'), findsOneWidget);
      expect(find.text('Plan ready'), findsOneWidget);
    });
  });
}

class _SlowChat implements ChatRepository {
  _SlowChat(this.reply);

  final Completer<ChatReply> reply;

  @override
  Future<ChatReply> sendMessage(String text, {String? sessionId}) =>
      reply.future;

  @override
  Future<List<ChatMessage>> resumeTrip(String tripId) async => const [];
}
