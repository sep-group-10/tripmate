import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../theme/app_colors.dart';

/// Tourist sections, in the order of NAV_ITEMS in web/src/pages/UserLayout.jsx.
const _navLabels = ['Chat', 'My trips', 'Profile'];

/// Scaffold with the bottom navigation. Mirrors the web sidebar: text-only
/// items, the active one is a white pill with a control shadow. Each tab keeps
/// its own stack and state via [StatefulNavigationShell].
class AppShell extends StatelessWidget {
  const AppShell({super.key, required this.navigationShell});

  final StatefulNavigationShell navigationShell;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(bottom: false, child: navigationShell),
      bottomNavigationBar: SafeArea(
        child: Padding(
          padding: const EdgeInsets.fromLTRB(16, 8, 16, 8),
          child: Row(
            children: [
              for (var i = 0; i < _navLabels.length; i++)
                Expanded(
                  child: Padding(
                    padding: const EdgeInsets.symmetric(horizontal: 2),
                    child: _NavPill(
                      label: _navLabels[i],
                      active: navigationShell.currentIndex == i,
                      onTap: () => navigationShell.goBranch(
                        i,
                        // Tapping the active tab returns to its root.
                        initialLocation: i == navigationShell.currentIndex,
                      ),
                    ),
                  ),
                ),
            ],
          ),
        ),
      ),
    );
  }
}

class _NavPill extends StatelessWidget {
  const _NavPill({
    required this.label,
    required this.active,
    required this.onTap,
  });

  final String label;
  final bool active;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return Semantics(
      button: true,
      selected: active,
      child: DecoratedBox(
        decoration: ShapeDecoration(
          color: active ? AppColors.surface : Colors.transparent,
          shape: const StadiumBorder(),
          shadows: active ? AppShadows.control : null,
        ),
        child: Material(
          type: MaterialType.transparency,
          child: InkWell(
            customBorder: const StadiumBorder(),
            onTap: onTap,
            child: Padding(
              padding: const EdgeInsets.symmetric(vertical: 12),
              child: Center(
                heightFactor: 1,
                child: Text(
                  label,
                  style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                    fontWeight: active ? FontWeight.w500 : FontWeight.w400,
                    color: active ? AppColors.ink : AppColors.muted700,
                  ),
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }
}
