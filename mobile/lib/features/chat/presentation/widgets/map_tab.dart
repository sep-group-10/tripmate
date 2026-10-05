import 'dart:math' as math;

import 'package:flutter/material.dart';

import '../../../../core/maps/maps_availability.dart';
import '../../../../core/theme/app_colors.dart';
import '../../../../core/theme/app_text.dart';
import '../../../../core/utils/formatters.dart';
import '../../../../core/widgets/empty_state.dart';
import '../../../../data/models/itinerary_day.dart';
import '../../../../data/models/itinerary_item.dart';
import 'tab_empty_states.dart';
import 'trip_map.dart';
import 'trip_map_model.dart';

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

/// Mirrors web/src/components/chat/MapTab.jsx: a Google Map of the stops, the
/// day chips (which here also filter the map), and the straight-line legs
/// between consecutive stops. Without a Maps key it shows the chips and legs
/// only.
class MapTab extends StatefulWidget {
  const MapTab({super.key, required this.days});

  final List<ItineraryDay> days;

  @override
  State<MapTab> createState() => _MapTabState();
}

class _MapTabState extends State<MapTab> {
  late final Future<bool> _hasMap = MapsAvailability.hasApiKey();

  /// Day numbers shown on the map. All days until the user filters.
  late Set<int> _visible = _allDays;

  Set<int> get _allDays => {for (final d in widget.days) d.dayNumber};

  @override
  void didUpdateWidget(MapTab old) {
    super.didUpdateWidget(old);
    // A new plan shows every day again.
    if (old.days != widget.days) _visible = _allDays;
  }

  /// Tapping a chip while every day is shown focuses that day; after that it
  /// toggles the day. Emptying the selection shows every day again.
  void _toggleDay(int dayNumber) {
    setState(() {
      final all = _allDays;
      if (_visible.length == all.length) {
        _visible = {dayNumber};
      } else if (_visible.contains(dayNumber)) {
        _visible = {..._visible}..remove(dayNumber);
        if (_visible.isEmpty) _visible = all;
      } else {
        _visible = {..._visible, dayNumber};
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    final days = widget.days;
    if (days.isEmpty) {
      return EmptyStatePanel(
        title: tabEmptyStates['Map']!.$1,
        message: tabEmptyStates['Map']!.$2,
      );
    }
    final theme = Theme.of(context);
    final allStops = [
      for (final day in days)
        for (final item in day.items)
          if (item.hasCoordinates) _Stop(item, day.dayNumber),
    ];
    final legs = [
      for (var i = 1; i < allStops.length; i++)
        (
          from: allStops[i - 1],
          to: allStops[i],
          km: _straightLineKm(allStops[i - 1].item, allStops[i].item),
        ),
    ];
    final muted = theme.textTheme.bodyMedium?.copyWith(
      color: AppColors.muted700,
    );

    return FutureBuilder<bool>(
      future: _hasMap,
      builder: (context, snapshot) {
        final hasMap = snapshot.data ?? false;
        return Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            if (hasMap) ...[
              TripMap(stops: visibleStops(mapStops(days), _visible)),
              const SizedBox(height: 14),
            ],
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: [
                for (var i = 0; i < days.length; i++)
                  _DayChip(
                    day: days[i],
                    color: dayColor(i),
                    active: _visible.contains(days[i].dayNumber),
                    onTap: hasMap ? () => _toggleDay(days[i].dayNumber) : null,
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
      },
    );
  }
}

/// The web's day legend chip. With a map it is also the day filter: a hidden
/// day is dimmed.
class _DayChip extends StatelessWidget {
  const _DayChip({
    required this.day,
    required this.color,
    required this.active,
    required this.onTap,
  });

  final ItineraryDay day;
  final Color color;
  final bool active;
  final VoidCallback? onTap;

  @override
  Widget build(BuildContext context) {
    return Opacity(
      opacity: active ? 1 : 0.4,
      child: Material(
        type: MaterialType.transparency,
        child: InkWell(
          customBorder: const StadiumBorder(),
          onTap: onTap,
          child: Container(
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
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
                    color: color,
                    shape: BoxShape.circle,
                  ),
                ),
                const SizedBox(width: 8),
                Text(
                  'Day ${day.dayNumber} · ${formatDate(day.date)}',
                  style: Theme.of(context).textTheme.bodySmall
                      ?.copyWith(fontSize: 12.5, color: AppColors.ink),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
