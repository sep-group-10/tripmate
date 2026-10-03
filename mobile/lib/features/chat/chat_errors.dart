import '../../data/api/api_exception.dart';

const plannerUnreachableText =
    'Sorry, I couldn\'t reach the planner. Please try again.';

const planningTimeoutText =
    'Planning is taking longer than expected. Please try again in a moment.';

const planningFailedText =
    'I couldn\'t complete your trip plan. Please try again or adjust your trip details.';

/// What the chat should do about a failed send. Ported from
/// describeChatError in web/src/utils/chatErrors.js: it goes by the error
/// `code`, never the message text.
class ChatFailure {
  const ChatFailure({
    required this.text,
    this.isAuth = false,
    this.retryable = true,
    this.resetSession = false,
  });

  /// What TripMate says in the chat (empty for an auth failure).
  final String text;

  /// The login session is gone: show nothing; the API client has already
  /// cleared the tokens and the app returns to the login page.
  final bool isAuth;
  final bool retryable;

  /// Forget the planning session id.
  final bool resetSession;
}

const _authCodes = {'TOKEN_EXPIRED', 'UNAUTHORIZED', 'INVALID_REFRESH_TOKEN'};

ChatFailure describeChatError(Object error) {
  final code = error is ApiException ? error.code : null;
  final status = error is ApiException ? error.statusCode : null;

  if (_authCodes.contains(code) || status == 401) {
    return const ChatFailure(text: '', isAuth: true, retryable: false);
  }
  switch (code) {
    case 'NOT_FOUND':
      return const ChatFailure(
        text: 'That planning session has expired. Please try again to start a new one.',
        resetSession: true,
      );
    case 'VALIDATION_ERROR':
      return const ChatFailure(
        text: 'Sorry, I couldn\'t process that message. Try rewording it.',
        retryable: false,
      );
    case 'RATE_LIMITED':
      return const ChatFailure(
        text: 'You\'re sending messages too quickly. Please wait a moment and try again.',
      );
    case ApiException.timeoutErrorCode:
      return const ChatFailure(text: planningTimeoutText);
    case 'PLANNING_FAILED':
      return const ChatFailure(text: planningFailedText);
  }
  // Network failure, 5xx, EXTERNAL_SERVICE_UNAVAILABLE, INTERNAL_SERVER_ERROR...
  return const ChatFailure(text: plannerUnreachableText);
}
