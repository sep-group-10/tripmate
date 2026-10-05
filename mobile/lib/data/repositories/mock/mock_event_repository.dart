import '../../mock/mock_data.dart';
import '../../mock/mock_delay.dart';
import '../../models/local_event.dart';
import '../event_repository.dart';

class MockEventRepository implements EventRepository {
  @override
  Future<List<LocalEvent>> getEvents({String? destinationId}) async {
    await mockDelay();
    final events =
        MockData.events
            .where(
              (e) => destinationId == null || e.destinationId == destinationId,
            )
            .toList()
          ..sort((a, b) => a.startDate.compareTo(b.startDate));
    return events;
  }
}
