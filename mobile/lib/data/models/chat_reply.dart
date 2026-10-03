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
    this.status,
    this.progressMessage,
    this.progressPercent = 0,
  });

  final String assistantMessage;
  final String sessionId;

  /// The planning session's status ("pending", "completed", "failed", ...).
  final String? status;

  /// The session's progress message and percentage, when the backend sets them.
  final String? progressMessage;
  final int progressPercent;

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
