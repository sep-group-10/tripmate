import 'package:flutter/material.dart';

import '../theme/app_colors.dart';

/// Web ChoiceChip: accent-tinted with a check when active, otherwise a bordered
/// white pill.
class AppChoiceChip extends StatelessWidget {
  const AppChoiceChip({
    super.key,
    required this.label,
    required this.active,
    required this.onTap,
  });

  final String label;
  final bool active;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final style = Theme.of(context).textTheme.labelMedium?.copyWith(
      fontSize: 12,
      fontWeight: FontWeight.w500,
      color: active ? AppColors.accent700 : AppColors.ink,
    );
    return Semantics(
      button: true,
      selected: active,
      child: DecoratedBox(
        decoration: ShapeDecoration(
          color: active ? AppColors.accent100 : AppColors.surface,
          shape: StadiumBorder(
            side: active
                ? BorderSide.none
                : const BorderSide(color: AppColors.border),
          ),
          shadows: active ? null : AppShadows.control,
        ),
        child: Material(
          type: MaterialType.transparency,
          child: InkWell(
            customBorder: const StadiumBorder(),
            onTap: onTap,
            child: Padding(
              padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 6),
              child: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  if (active) ...[
                    Text(
                      '✓',
                      style: style?.copyWith(fontWeight: FontWeight.w700),
                    ),
                    const SizedBox(width: 6),
                  ],
                  Text(label, style: style),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}
