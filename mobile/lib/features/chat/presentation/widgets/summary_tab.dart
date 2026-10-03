import 'package:flutter/material.dart';

import '../../../../core/theme/app_colors.dart';
import '../../../../core/widgets/mono_labels.dart';
import '../../../../core/widgets/pill_tag.dart';
import '../../../../data/models/trip_plan.dart';
import 'trip_hero.dart';

/// Mirrors web/src/components/chat/SummaryTab.jsx.
class SummaryTab extends StatelessWidget {
  const SummaryTab({super.key, required this.summary});

  final TripSummary summary;

  static (String, PillTone) _pill(TradeoffType type) => switch (type) {
    TradeoffType.swapped => ('Swapped', PillTone.info),
    TradeoffType.kept => ('Kept', PillTone.success),
    TradeoffType.dropped => ('Dropped', PillTone.warn),
  };

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        TripHero(summary: summary),
        const SizedBox(height: 14),
        Container(
          padding: const EdgeInsets.all(18),
          decoration: BoxDecoration(
            color: AppColors.inset,
            borderRadius: BorderRadius.circular(AppRadii.xl),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const SectionLabel('What TripMate optimised for'),
              const SizedBox(height: 8),
              Text(
                summary.optimisedFor,
                style: theme.textTheme.bodyMedium?.copyWith(
                  fontSize: 14,
                  height: 1.62,
                  color: AppColors.muted700,
                ),
              ),
            ],
          ),
        ),
        const SizedBox(height: 14),
        const SectionLabel('Trade-offs it made'),
        const SizedBox(height: 10),
        for (final item in summary.tradeoffs)
          Container(
            padding: const EdgeInsets.symmetric(vertical: 12),
            decoration: const BoxDecoration(
              border: Border(top: BorderSide(color: AppColors.divider)),
            ),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                PillTag(_pill(item.type).$1, tone: _pill(item.type).$2),
                const SizedBox(width: 12),
                Expanded(
                  child: Text(
                    item.text,
                    style: theme.textTheme.bodyMedium?.copyWith(
                      height: 1.55,
                      color: AppColors.muted700,
                    ),
                  ),
                ),
              ],
            ),
          ),
      ],
    );
  }
}
