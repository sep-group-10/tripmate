import '../models/chat_reply.dart';

/// One entry of `error.details` (a field-level validation message).
class FieldDetail {
  const FieldDetail({required this.field, required this.message});

  final String field;
  final String message;
}

/// An error from the backend's `{ success: false, error: { code, message,
/// details } }` envelope, or [networkErrorCode] when the server was not
/// reached. Branch on [code], never on [message] (docs/api-contract.md).
/// Mirrors parseApiError in web/src/utils/apiError.js.
class ApiException extends RepositoryException {
  const ApiException({
    required this.code,
    required String message,
    this.details = const [],
    this.statusCode,
  }) : super(message);

  static const networkErrorCode = 'NETWORK_ERROR';
  static const unknownErrorCode = 'UNKNOWN_ERROR';

  /// Same text the web app shows when the request never reached the server.
  static const networkErrorMessage =
      'Could not reach the server. Please check your connection and try again.';

  factory ApiException.network() =>
      const ApiException(code: networkErrorCode, message: networkErrorMessage);

  /// Builds an exception from a decoded response body, falling back like the
  /// web helper when the body is not the structured envelope.
  factory ApiException.fromBody(Object? body, {int? statusCode}) {
    final error = body is Map ? body['error'] : null;
    if (error is Map) {
      final rawDetails = error['details'];
      return ApiException(
        code: (error['code'] as String?) ?? unknownErrorCode,
        message:
            (error['message'] as String?) ??
            'Something went wrong. Please try again.',
        details: [
          if (rawDetails is List)
            for (final d in rawDetails)
              if (d is Map)
                FieldDetail(
                  field: '${d['field'] ?? ''}',
                  message: '${d['message'] ?? ''}',
                ),
        ],
        statusCode: statusCode,
      );
    }
    return ApiException(
      code: unknownErrorCode,
      message: 'Something went wrong. Please try again.',
      statusCode: statusCode,
    );
  }

  final String code;
  final List<FieldDetail> details;
  final int? statusCode;

  /// The message for [field], or null.
  String? detailFor(String field) {
    for (final d in details) {
      if (d.field == field) return d.message;
    }
    return null;
  }
}
