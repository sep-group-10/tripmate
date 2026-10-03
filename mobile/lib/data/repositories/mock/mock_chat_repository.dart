import '../../mock/mock_delay.dart';
import '../../mock/mock_plan.dart';
import '../../mock/mock_trips.dart';
import '../../models/chat_reply.dart';
import '../chat_repository.dart';

/// Mirrors web/src/services/chatMock.js: a message with "plan", "trip" or
/// "itinerary" returns the sample plan, "fail" throws, anything else is a
/// clarifying question.
class MockChatRepository implements ChatRepository {
  int _sessions = 0;

  @override
  Future<ChatReply> sendMessage(String text, {String? sessionId}) async {
    await mockDelay(1000);
    if (RegExp('fail', caseSensitive: false).hasMatch(text)) {
      throw const RepositoryException(
        'The planner is temporarily unavailable.',
      );
    }
    final id = sessionId ?? 'session-${++_sessions}';
    if (RegExp('plan|trip|itinerary', caseSensitive: false).hasMatch(text)) {
      return ChatReply(
        assistantMessage: 'Your trip plan is ready.\nI\'ve put together a relaxed hill-country itinerary with food stops and short walks.',
        sessionId: id,
        plan: mockPlan,
      );
    }
    return ChatReply(
      assistantMessage: 'To help me plan your trip, could you tell me when you\'re travelling, how many people are going and what you enjoy?',
      sessionId: id,
    );
  }

  @override
  Future<List<ChatMessage>> resumeTrip(String tripId) async {
    await mockDelay(300);
    final trip = mockTrips.where((t) => t.id == tripId).firstOrNull;
    if (trip == null) throw const RepositoryException('Trip not found');
    final prompt = trip.prompt;
    return [if (prompt != null) ChatMessage(fromUser: true, text: prompt)];
  }
}
