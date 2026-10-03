import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../theme/app_colors.dart';
import '../theme/app_text.dart';
import 'app_button.dart';

/// Mirrors web/src/pages/NotFoundPage.jsx.
class NotFoundPage extends StatelessWidget {
  const NotFoundPage({super.key});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Scaffold(
      body: Center(
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 24),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Text(
                '404',
                style: AppText.mono(
                  14,
                  color: AppColors.muted600,
                  tracking: 0.1,
                ),
              ),
              const SizedBox(height: 16),
              Text('Page not found', style: theme.textTheme.headlineMedium),
              const SizedBox(height: 16),
              Text(
                'We couldn’t find the page you’re looking for.',
                textAlign: TextAlign.center,
                style: theme.textTheme.bodyMedium?.copyWith(
                  fontSize: 14,
                  color: AppColors.muted600,
                ),
              ),
              const SizedBox(height: 24),
              AppButton(label: 'Go home', onPressed: () => context.go('/chat')),
            ],
          ),
        ),
      ),
    );
  }
}
