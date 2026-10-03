import 'package:flutter/material.dart';

import '../../../../core/theme/app_colors.dart';

class Stat {
  const Stat(this.label, this.value, this.delta);

  final String label;
  final String value;
  final String delta;
}

/// Web StatRow: one white surface split into two columns by hairlines (the
/// narrow-screen layout of the web component).
class StatRow extends StatelessWidget {
  const StatRow({super.key, required this.stats});

  final List<Stat> stats;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Container(
      clipBehavior: Clip.antiAlias,
      decoration: BoxDecoration(
        color: AppColors.surface,
        borderRadius: BorderRadius.circular(AppRadii.card),
        boxShadow: AppShadows.control,
      ),
      child: LayoutBuilder(
        builder: (context, constraints) {
          final width = constraints.maxWidth / 2;
          return Wrap(
            children: [
              for (var i = 0; i < stats.length; i++)
                Container(
                  width: width,
                  padding: const EdgeInsets.all(20),
                  decoration: BoxDecoration(
                    border: Border(
                      top: i > 0
                          ? const BorderSide(color: AppColors.border)
                          : BorderSide.none,
                      left: i.isOdd
                          ? const BorderSide(color: AppColors.border)
                          : BorderSide.none,
                    ),
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        stats[i].label,
                        style: theme.textTheme.labelMedium?.copyWith(
                          color: AppColors.muted600,
                        ),
                      ),
                      const SizedBox(height: 4),
                      FittedBox(
                        fit: BoxFit.scaleDown,
                        alignment: Alignment.centerLeft,
                        child: Text(
                          stats[i].value,
                          style: theme.textTheme.headlineSmall?.copyWith(
                            fontFeatures: const [FontFeature.tabularFigures()],
                          ),
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        stats[i].delta,
                        style: theme.textTheme.bodySmall?.copyWith(
                          fontWeight: FontWeight.w500,
                          color: AppColors.muted500,
                        ),
                      ),
                    ],
                  ),
                ),
            ],
          );
        },
      ),
    );
  }
}
