/// Simulates network latency so loading states are visible in the UI.
Future<void> mockDelay([int milliseconds = 350]) =>
    Future<void>.delayed(Duration(milliseconds: milliseconds));
