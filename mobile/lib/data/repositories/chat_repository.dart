import '../models/chat_reply.dart';

abstract class ChatRepository {
  /// Sends [text] to the planner. Pass the [sessionId] of the previous reply to
  /// continue the same planning session. Throws [RepositoryException] when the
  /// planner cannot be reached.
  Future<ChatReply> sendMessage(String text, {String? sessionId});

  /// Earlier messages of a draft or generated trip's planning session.
  Future<List<ChatMessage>> resumeTrip(String tripId);
}
