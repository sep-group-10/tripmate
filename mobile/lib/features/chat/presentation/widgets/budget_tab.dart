import 'package:flutter/material.dart';

import '../../../../core/theme/app_colors.dart';
import '../../../../core/utils/formatters.dart';
import '../../../../core/widgets/mono_labels.dart';
import '../../../../data/models/trip_plan.dart';
import 'trip_hero.dart';

const _categoryColors = {
  'accommodation': AppColors.accent,
  'dining': AppColors.info,
  'transport': AppColors.warn,
  'attractions': AppColors.accent300,
  'misc': AppColors.muted400,
};

/// Mirrors web/src/components/chat/BudgetTab.jsx.
class BudgetTab extends StatelessWidget {
  const BudgetTab({super.key, required this.summary, required this.budget});

  final TripSummary summary;
  final TripBudget budget;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    // Percentages come from the amounts, so they always match the bar.
    final sum = budget.categories.fold<int>(0, (n, c) => n + c.amount);
    double share(BudgetCategory c) => sum > 0 ? c.amount / sum * 100 : 0;
    Color colorOf(BudgetCategory c) =>
        _categoryColors[c.key] ?? AppColors.muted400;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        TripHero(summary: summary),
        const SizedBox(height: 14),
        Wrap(
          alignment: WrapAlignment.spaceBetween,
          crossAxisAlignment: WrapCrossAlignment.end,
          spacing: 12,
          runSpacing: 4,
          children: [
            const SectionLabel('Total planned spend'),
            Row(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.baseline,
              textBaseline: TextBaseline.alphabetic,
              children: [
                Text(
                  formatMoney(budget.total, currency: budget.currency),
                  style: theme.textTheme.headlineSmall?.copyWith(
                    color: AppColors.accent,
                    fontFeatures: const [FontFeature.tabularFigures()],
                  ),
                ),
                const SizedBox(width: 8),
                Text(
                  '${formatMoney(budget.perDay, currency: '').trim()} / day',
                  style: theme.textTheme.bodySmall?.copyWith(
                    fontSize: 12.5,
                    color: AppColors.muted500,
                  ),
                ),
              ],
            ),
          ],
        ),
        const SizedBox(height: 14),
        ClipRRect(
          borderRadius: BorderRadius.circular(AppRadii.pill),
          child: Container(
            height: 10,
            color: AppColors.inset,
            child: Row(
              children: [
                for (final c in budget.categories)
                  Expanded(
                    flex: (share(c) * 100).round().clamp(0, 1 << 30),
                    child: ColoredBox(color: colorOf(c)),
                  ),
              ],
            ),
          ),
        ),
        const SizedBox(height: 14),
        for (final c in budget.categories)
          Container(
            padding: const EdgeInsets.symmetric(vertical: 11),
            decoration: const BoxDecoration(
              border: Border(top: BorderSide(color: AppColors.divider)),
            ),
            child: Row(
              children: [
                Container(
                  width: 8,
                  height: 8,
                  decoration: BoxDecoration(
                    color: colorOf(c),
                    shape: BoxShape.circle,
                  ),
                ),
                const SizedBox(width: 10),
                Expanded(
                  child: Text(
                    c.label,
                    style: theme.textTheme.bodyMedium?.copyWith(
                      color: AppColors.muted700,
                    ),
                  ),
                ),
                Text(
                  '${share(c).round()}%',
                  style: theme.textTheme.bodySmall?.copyWith(
                    fontSize: 12.5,
                    color: AppColors.muted500,
                  ),
                ),
                const SizedBox(width: 10),
                SizedBox(
                  width: 88,
                  child: Text(
                    formatMoney(c.amount, currency: budget.currency),
                    textAlign: TextAlign.right,
                    style: theme.textTheme.bodyMedium?.copyWith(
                      fontWeight: FontWeight.w500,
                      fontFeatures: const [FontFeature.tabularFigures()],
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
