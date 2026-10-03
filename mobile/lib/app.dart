import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:provider/provider.dart';

import 'core/router/app_router.dart';
import 'core/theme/app_theme.dart';
import 'data/repositories/auth_repository.dart';
import 'data/repositories/chat_repository.dart';
import 'data/repositories/destination_repository.dart';
import 'data/repositories/event_repository.dart';
import 'data/repositories/mock/mock_auth_repository.dart';
import 'data/repositories/mock/mock_chat_repository.dart';
import 'data/repositories/mock/mock_destination_repository.dart';
import 'data/repositories/mock/mock_event_repository.dart';
import 'data/repositories/mock/mock_trip_repository.dart';
import 'data/repositories/trip_repository.dart';

/// Root widget. This is the only place the mock repositories are chosen;
/// swap them for API-backed ones here when the backend is wired in.
class TripMateApp extends StatefulWidget {
  const TripMateApp({super.key, this.useWebFonts = true});

  final bool useWebFonts;

  @override
  State<TripMateApp> createState() => _TripMateAppState();
}

class _TripMateAppState extends State<TripMateApp> {
  final AuthRepository _auth = MockAuthRepository();
  late final GoRouter _router = buildRouter(_auth);

  @override
  void dispose() {
    _router.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return MultiProvider(
      providers: [
        Provider<AuthRepository>.value(value: _auth),
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
