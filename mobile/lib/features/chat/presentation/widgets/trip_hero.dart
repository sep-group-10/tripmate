import 'package:flutter/material.dart';

import '../../../../core/theme/app_colors.dart';
import '../../../../core/theme/app_text.dart';
import '../../../../core/utils/formatters.dart';
import '../../../../core/widgets/mono_labels.dart';
import '../../../../data/models/trip_plan.dart';

/// Mirrors web/src/components/chat/TripHero.jsx: the dark hero card and the
/// facts grid beneath it, shared by the Summary and Budget tabs.
class TripHero extends StatelessWidget {
  const TripHero({super.key, required this.summary});

  final TripSummary summary;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final days = tripDurationDays(summary.startDate, summary.endDate);
    final facts = [
      ('Duration', '$days ${days == 1 ? 'day' : 'days'}'),
      (
        'Travellers',
        '${summary.travellers} ${summary.travellers == 1 ? 'traveller' : 'travellers'}',
      ),
      ('Dates', formatDateRange(summary.startDate, summary.endDate)),
      ('Pace', summary.pace),
    ];
    const onDark = Color(0x9EFFFFFF); // white/62

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Container(
          padding: const EdgeInsets.all(23),
          decoration: BoxDecoration(
            color: AppColors.muted900,
            borderRadius: BorderRadius.circular(16),
            boxShadow: AppShadows.card,
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Expanded(
                    child: Text(
                      summary.routeLabel.toUpperCase(),
                      style: AppText.mono(
                        10.5,
                        color: AppColors.accent300,
                        tracking: 0.1,
                        weight: FontWeight.w400,
                      ),
                    ),
                  ),
                  const SizedBox(width: 12),
                  Container(
                    padding: const EdgeInsets.symmetric(
                      horizontal: 10,
                      vertical: 4,
                    ),
                    decoration: BoxDecoration(
                      color: const Color(0x1FFFFFFF),
                      borderRadius: BorderRadius.circular(AppRadii.pill),
                    ),
                    child: Text(
                      'Generated today',
                      style: theme.textTheme.labelMedium?.copyWith(
                        fontSize: 11.5,
                        color: Colors.white,
                      ),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 8),
              Text(
                summary.title,
                style: theme.textTheme.headlineSmall?.copyWith(
                  fontSize: 24,
                  color: Colors.white,
                ),
              ),
              const SizedBox(height: 12),
              Container(
                padding: const EdgeInsets.only(top: 14),
                decoration: const BoxDecoration(
                  border: Border(top: BorderSide(color: Color(0x1AFFFFFF))),
                ),
                child: Row(
                  children: [
                    Expanded(
                      child: Text(
                        '${summary.occasion} · ${formatDateRange(summary.startDate, summary.endDate, withYear: true)}',
                        style: theme.textTheme.labelMedium?.copyWith(
                          color: onDark,
                        ),
                      ),
                    ),
                    const SizedBox(width: 8),
                    Text(
                      '${summary.stopCount} stops',
                      style: theme.textTheme.titleMedium?.copyWith(
                        color: AppColors.accent300,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
        const SizedBox(height: 14),
        Container(
          decoration: BoxDecoration(
            color: AppColors.inset,
            borderRadius: BorderRadius.circular(AppRadii.xl),
          ),
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
          child: LayoutBuilder(
            builder: (context, c) => Wrap(
              runSpacing: 14,
              children: [
                for (final (label, value) in facts)
                  SizedBox(
                    width: c.maxWidth / 2,
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        SectionLabel(label),
                        const SizedBox(height: 4),
                        Text(
                          value,
                          style: theme.textTheme.titleMedium?.copyWith(
                            fontSize: 16,
                            fontFeatures: const [FontFeature.tabularFigures()],
                          ),
                        ),
                      ],
                    ),
                  ),
              ],
            ),
          ),
        ),
      ],
    );
  }
}
