import '../../mock/mock_delay.dart';
import '../../mock/mock_trips.dart';
import '../../models/chat_reply.dart';
import '../../models/trip.dart';
import '../trip_repository.dart';

class MockTripRepository implements TripRepository {
  final List<Trip> _trips = [...mockTrips];

  int _indexOf(String id) {
    final index = _trips.indexWhere((t) => t.id == id);
    if (index == -1) throw const RepositoryException('Trip not found');
    return index;
  }

  @override
  Future<List<Trip>> getTrips() async {
    await mockDelay();
    return List.unmodifiable(_trips);
  }

  @override
  Future<Trip> getTrip(String id) async {
    await mockDelay(200);
    return _trips[_indexOf(id)];
  }

  @override
  Future<Trip> saveTrip(String id) async {
    await mockDelay(400);
    final i = _indexOf(id);
    if (_trips[i].status != TripStatus.generated) {
      throw const RepositoryException('Only generated trips can be saved.');
    }
    return _trips[i] = _trips[i].copyWith(status: TripStatus.saved);
  }

  @override
  Future<Trip> unsaveTrip(String id) async {
    await mockDelay(400);
    final i = _indexOf(id);
    if (_trips[i].status != TripStatus.saved) {
      throw const RepositoryException('Only saved trips can be unsaved.');
    }
    return _trips[i] = _trips[i].copyWith(status: TripStatus.generated);
  }

  @override
  Future<Trip> renameDraft(String id, String title) async {
    await mockDelay(400);
    final i = _indexOf(id);
    return _trips[i] = _trips[i].copyWith(title: title);
  }

  @override
  Future<void> discardDraft(String id) async {
    await mockDelay(300);
    _trips.removeAt(_indexOf(id));
  }
}
