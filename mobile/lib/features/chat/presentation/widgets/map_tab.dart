import 'dart:math' as math;

import 'package:flutter/material.dart';

import '../../../../core/theme/app_colors.dart';
import '../../../../core/theme/app_text.dart';
import '../../../../core/utils/formatters.dart';
import '../../../../core/widgets/empty_state.dart';
import '../../../../data/models/itinerary_day.dart';
import '../../../../data/models/itinerary_item.dart';
import 'tab_empty_states.dart';

const _dayColors = [
  AppColors.accent,
  AppColors.info,
  AppColors.muted500,
  AppColors.success,
  AppColors.warn,
];

class _Stop {
  const _Stop(this.item, this.dayNumber);

  final ItineraryItem item;
  final int dayNumber;
}

/// Great-circle distance between two points, in km.
double _straightLineKm(ItineraryItem a, ItineraryItem b) {
  double rad(double d) => d * math.pi / 180;
  final dLat = rad(b.latitude! - a.latitude!);
  final dLon = rad(b.longitude! - a.longitude!);
  final h =
      math.pow(math.sin(dLat / 2), 2) +
      math.cos(rad(a.latitude!)) *
          math.cos(rad(b.latitude!)) *
          math.pow(math.sin(dLon / 2), 2);
  return 2 * 6371 * math.asin(math.sqrt(h));
}

/// Mirrors web/src/components/chat/MapTab.jsx: day legend and the
/// straight-line legs between consecutive stops. The interactive map canvas of
/// the web (TripMap) is not part of this UI-only build.
class MapTab extends StatelessWidget {
  const MapTab({super.key, required this.days});

  final List<ItineraryDay> days;

  @override
  Widget build(BuildContext context) {
    if (days.isEmpty) {
      return EmptyStatePanel(
        title: tabEmptyStates['Map']!.$1,
        message: tabEmptyStates['Map']!.$2,
      );
    }
    final theme = Theme.of(context);
    final stops = [
      for (final day in days)
        for (final item in day.items)
          if (item.hasCoordinates) _Stop(item, day.dayNumber),
    ];
    final legs = [
      for (var i = 1; i < stops.length; i++)
        (
          from: stops[i - 1],
          to: stops[i],
          km: _straightLineKm(stops[i - 1].item, stops[i].item),
        ),
    ];
    final muted = theme.textTheme.bodyMedium?.copyWith(
      color: AppColors.muted700,
    );

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Wrap(
          spacing: 8,
          runSpacing: 8,
          children: [
            for (var i = 0; i < days.length; i++)
              Container(
                padding: const EdgeInsets.symmetric(
                  horizontal: 12,
                  vertical: 6,
                ),
                decoration: BoxDecoration(
                  borderRadius: BorderRadius.circular(AppRadii.pill),
                  border: Border.all(color: AppColors.border),
                ),
                child: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Container(
                      width: 8,
                      height: 8,
                      decoration: BoxDecoration(
                        color: _dayColors[i % _dayColors.length],
                        shape: BoxShape.circle,
                      ),
                    ),
                    const SizedBox(width: 8),
                    Text(
                      'Day ${days[i].dayNumber} · ${formatDate(days[i].date)}',
                      style: theme.textTheme.bodySmall?.copyWith(
                        fontSize: 12.5,
                        color: AppColors.ink,
                      ),
                    ),
                  ],
                ),
              ),
          ],
        ),
        const SizedBox(height: 14),
        if (legs.isEmpty)
          Container(
            padding: const EdgeInsets.only(top: 12),
            decoration: const BoxDecoration(
              border: Border(top: BorderSide(color: AppColors.divider)),
            ),
            child: Text(
              'Not enough stops with coordinates to show distances yet.',
              style: theme.textTheme.bodyMedium?.copyWith(
                color: AppColors.muted600,
              ),
            ),
          ),
        for (var i = 0; i < legs.length; i++)
          Container(
            padding: const EdgeInsets.symmetric(vertical: 10),
            decoration: const BoxDecoration(
              border: Border(top: BorderSide(color: AppColors.divider)),
            ),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                SizedBox(
                  width: 46,
                  child: Text(
                    'LEG ${i + 1}',
                    style: AppText.badge(color: AppColors.accent700),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Text(
                    '${legs[i].from.dayNumber == legs[i].to.dayNumber ? 'Day ${legs[i].from.dayNumber}' : 'Day ${legs[i].from.dayNumber} → Day ${legs[i].to.dayNumber}'} · ${legs[i].from.item.title} → ${legs[i].to.item.title}',
                    style: muted,
                  ),
                ),
                const SizedBox(width: 12),
                Text(
                  '≈ ${legs[i].km.toStringAsFixed(1)} km',
                  style: theme.textTheme.bodySmall?.copyWith(
                    fontSize: 12.5,
                    color: AppColors.muted500,
                  ),
                ),
              ],
            ),
          ),
        if (legs.isNotEmpty)
          Container(
            padding: const EdgeInsets.only(top: 10),
            decoration: const BoxDecoration(
              border: Border(top: BorderSide(color: AppColors.divider)),
            ),
            child: Text(
              'Straight-line distances between consecutive stops, not road routes.',
              style: theme.textTheme.bodySmall?.copyWith(
                fontSize: 12.5,
                color: AppColors.muted500,
              ),
            ),
          ),
      ],
    );
  }
}
