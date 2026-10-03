import 'trip_plan.dart';

class ChatMessage {
  const ChatMessage({required this.fromUser, required this.text});

  final bool fromUser;
  final String text;
}

class ChatReply {
  const ChatReply({
    required this.assistantMessage,
    required this.sessionId,
    this.plan,
  });

  final String assistantMessage;
  final String sessionId;

  /// Null for a clarifying question; set once a trip has been planned.
  final TripPlan? plan;
}

/// Thrown by repositories; [message] is safe to show.
class RepositoryException implements Exception {
  const RepositoryException(this.message);

  final String message;

  @override
  String toString() => message;
}
