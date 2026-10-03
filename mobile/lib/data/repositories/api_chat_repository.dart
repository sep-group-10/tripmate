import '../api/api_client.dart';
import '../api/api_config.dart';
import '../mock/mock_plan.dart';
import '../models/chat_reply.dart';
import '../models/itinerary_day.dart';
import '../models/itinerary_item.dart';
import '../models/trip_plan.dart';
import 'chat_repository.dart';

/// [ChatRepository] backed by `POST /api/v1/chat` (new session) and
/// `POST /api/v1/chat/{session_id}` (follow-ups), as web/src/services/chatService.js.
///
/// Like the web, the Summary and Budget tabs use placeholder data (the chat
/// response carries no hero facts, trade-offs or costs); only the days come
/// from the backend. Resuming a draft stays on [resumeFallback] (mock) because
/// it would need the /trips endpoints.
class ApiChatRepository implements ChatRepository {
  ApiChatRepository(this._api, {required this.resumeFallback});

  final ApiClient _api;
  final ChatRepository resumeFallback;

  @override
  Future<ChatReply> sendMessage(String text, {String? sessionId}) async {
    final data = await _api.post(
      sessionId == null ? '/api/v1/chat' : '/api/v1/chat/$sessionId',
      body: {'message': text},
      timeout: ApiConfig.chatTimeout,
    ) as Map<String, dynamic>;
    final session = data['session'] as Map<String, dynamic>;
    final itinerary = data['itinerary'];
    return ChatReply(
      assistantMessage: data['assistant_message'] as String,
      sessionId: session['id'] as String,
      status: session['status'] as String?,
      progressMessage: session['progress_message'] as String?,
      progressPercent: (session['progress_percentage'] as num?)?.toInt() ?? 0,
      // A clarifying question or a failed plan returns itinerary: null.
      plan: itinerary is Map<String, dynamic> ? _plan(itinerary) : null,
    );
  }

  @override
  Future<List<ChatMessage>> resumeTrip(String tripId) =>
      resumeFallback.resumeTrip(tripId);

  TripPlan _plan(Map<String, dynamic> json) => TripPlan(
    days: [
      for (final d in (json['days'] as List? ?? const []))
        _day(d as Map<String, dynamic>),
    ],
    unscheduled: [
      for (final u in (json['unscheduled'] as List? ?? const []))
        UnscheduledItem(
          name: '${(u as Map)['name']}',
          reason: u['reason'] as String?,
        ),
    ],
    warnings: [for (final w in (json['warnings'] as List? ?? const [])) '$w'],
    // Placeholder content, exactly like the web (TRIP_DUMMY).
    summary: mockPlan.summary,
    budget: mockPlan.budget,
  );

  ItineraryDay _day(Map<String, dynamic> json) => ItineraryDay(
    dayNumber: json['day_number'] as int,
    date: DateTime.parse(json['date'] as String),
    dayType: json['day_type'] as String?,
    distanceKm:
        ((json['route_optimization'] as Map?)?['local_distance_km'] as num?)
            ?.toDouble(),
    warnings: [for (final w in (json['warnings'] as List? ?? const [])) '$w'],
    items: [
      for (final i in (json['items'] as List? ?? const []))
        _item(i as Map<String, dynamic>),
    ],
  );

  ItineraryItem _item(Map<String, dynamic> json) {
    final category = '${json['category']}';
    return ItineraryItem(
      id: '${json['candidate_id']}',
      type: switch (category) {
        'attraction' => ItineraryItemType.attraction,
        'restaurant' => ItineraryItemType.restaurant,
        'hotel' => ItineraryItemType.hotel,
        'local_event' => ItineraryItemType.localEvent,
        _ => ItineraryItemType.other,
      },
      rawCategory: category,
      title: '${json['name']}',
      startTime: json['start_time'] as String?,
      endTime: json['end_time'] as String?,
      latitude: (json['latitude'] as num?)?.toDouble(),
      longitude: (json['longitude'] as num?)?.toDouble(),
    );
  }
}
