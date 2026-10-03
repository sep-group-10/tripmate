import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../../data/repositories/auth_repository.dart';
import '../../features/auth/presentation/check_inbox_page.dart';
import '../../features/auth/presentation/forgot_password_page.dart';
import '../../features/auth/presentation/login_page.dart';
import '../../features/auth/presentation/register_page.dart';
import '../../features/chat/presentation/chat_page.dart';
import '../../features/profile/presentation/profile_page.dart';
import '../../features/trips/presentation/trip_itinerary_page.dart';
import '../../features/trips/presentation/trips_page.dart';
import '../widgets/app_shell.dart';
import '../widgets/not_found_page.dart';

/// Routes follow web/src/routes/AppRoutes.jsx. The tourist shell has the same
/// three sections as the web sidebar: Chat, My trips and Profile.
GoRouter buildRouter(AuthRepository auth) {
  final rootKey = GlobalKey<NavigatorState>(debugLabel: 'root');
  const publicPaths = {
    '/login',
    '/register',
    '/check-inbox',
    '/forgot-password',
  };

  return GoRouter(
    navigatorKey: rootKey,
    initialLocation: '/chat',
    errorBuilder: (_, _) => const NotFoundPage(),
    // Like web's ProtectedRoute: signed-out users are sent to /login.
    redirect: (context, state) async {
      if (publicPaths.contains(state.matchedLocation)) return null;
      try {
        return await auth.currentUser() == null ? '/login' : null;
      } catch (_) {
        // The session could not be checked (e.g. backend unreachable).
        return '/login';
      }
    },
    routes: [
      GoRoute(path: '/login', builder: (_, _) => const LoginPage()),
      GoRoute(path: '/register', builder: (_, _) => const RegisterPage()),
      GoRoute(
        path: '/forgot-password',
        builder: (_, _) => const ForgotPasswordPage(),
      ),
      GoRoute(
        path: '/check-inbox',
        // Without an email there is nothing to confirm, like the web page.
        redirect: (_, state) => state.extra is String ? null : '/register',
        builder: (_, state) => CheckInboxPage(email: state.extra! as String),
      ),
      StatefulShellRoute.indexedStack(
        builder: (_, _, shell) => AppShell(navigationShell: shell),
        branches: [
          StatefulShellBranch(
            routes: [
              GoRoute(
                path: '/chat',
                builder: (_, state) =>
                    ChatPage(tripId: state.uri.queryParameters['tripId']),
              ),
            ],
          ),
          StatefulShellBranch(
            routes: [
              GoRoute(
                path: '/trips',
                builder: (_, _) => const TripsPage(),
                routes: [
                  GoRoute(
                    path: ':tripId',
                    builder: (_, state) => TripItineraryPage(
                      tripId: state.pathParameters['tripId']!,
                    ),
                  ),
                ],
              ),
            ],
          ),
          StatefulShellBranch(
            routes: [
              GoRoute(path: '/profile', builder: (_, _) => const ProfilePage()),
            ],
          ),
        ],
      ),
    ],
  );
}
