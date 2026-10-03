import 'dart:async';

import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:provider/provider.dart';

import 'core/router/app_router.dart';
import 'core/theme/app_theme.dart';
import 'data/api/api_client.dart';
import 'data/api/token_store.dart';
import 'data/repositories/api_auth_repository.dart';
import 'data/repositories/api_profile_repository.dart';
import 'data/repositories/auth_repository.dart';
import 'data/repositories/chat_repository.dart';
import 'data/repositories/destination_repository.dart';
import 'data/repositories/event_repository.dart';
import 'data/repositories/mock/mock_chat_repository.dart';
import 'data/repositories/mock/mock_destination_repository.dart';
import 'data/repositories/mock/mock_event_repository.dart';
import 'data/repositories/mock/mock_trip_repository.dart';
import 'data/repositories/profile_repository.dart';
import 'data/repositories/trip_repository.dart';

/// Root widget. This is the only place repositories are chosen: auth and
/// profile talk to the backend; chat, trips, destinations and events are still
/// mocks. Tests pass [authRepository] and [profileRepository] to stay offline.
class TripMateApp extends StatefulWidget {
  const TripMateApp({
    super.key,
    this.useWebFonts = true,
    this.authRepository,
    this.profileRepository,
  }) : assert(
         (authRepository == null) == (profileRepository == null),
         'Pass both auth and profile repositories, or neither.',
       );

  final bool useWebFonts;
  final AuthRepository? authRepository;
  final ProfileRepository? profileRepository;

  @override
  State<TripMateApp> createState() => _TripMateAppState();
}

class _TripMateAppState extends State<TripMateApp> {
  ApiClient? _apiClient;
  late final AuthRepository _auth;
  late final ProfileRepository _profile;
  late final GoRouter _router;
  StreamSubscription<void>? _sessionExpiredSub;

  @override
  void initState() {
    super.initState();
    if (widget.authRepository != null) {
      _auth = widget.authRepository!;
      _profile = widget.profileRepository!;
    } else {
      final api = _apiClient = ApiClient(tokenStore: SecureTokenStore());
      final session = UserSession();
      _auth = ApiAuthRepository(api, session);
      _profile = ApiProfileRepository(api, session);
    }
    _router = buildRouter(_auth);
    // An expired session that could not be refreshed sends the user to login.
    _sessionExpiredSub = _auth.sessionExpired.listen(
      (_) => _router.go('/login'),
    );
  }

  @override
  void dispose() {
    _sessionExpiredSub?.cancel();
    _router.dispose();
    _apiClient?.close();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return MultiProvider(
      providers: [
        Provider<AuthRepository>.value(value: _auth),
        Provider<ProfileRepository>.value(value: _profile),
        Provider<ChatRepository>(create: (_) => MockChatRepository()),
        Provider<TripRepository>(create: (_) => MockTripRepository()),
        // Not used by any page yet; kept for the destination/event screens
        // the web app will get.
        Provider<DestinationRepository>(
          create: (_) => MockDestinationRepository(),
        ),
        Provider<EventRepository>(create: (_) => MockEventRepository()),
      ],
      child: MaterialApp.router(
        title: 'TripMate',
        debugShowCheckedModeBanner: false,
        theme: AppTheme.light(useWebFonts: widget.useWebFonts),
        routerConfig: _router,
      ),
    );
  }
}
