import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:provider/provider.dart';

import '../../../core/theme/app_colors.dart';
import '../../../core/utils/formatters.dart';
import '../../../core/widgets/async_body.dart';
import '../../../core/widgets/empty_state.dart';
import '../../../core/widgets/mono_labels.dart';
import '../../../data/models/itinerary_item.dart';
import '../../../data/models/trip.dart';
import '../../../data/repositories/trip_repository.dart';

/// Mirrors web/src/pages/TripItineraryPage.jsx.
class TripItineraryPage extends StatelessWidget {
  const TripItineraryPage({super.key, required this.tripId});

  final String tripId;

  static String _isoDate(DateTime d) =>
      '${d.year}-${d.month.toString().padLeft(2, '0')}-${d.day.toString().padLeft(2, '0')}';

  static String _typeName(ItineraryItemType type) => switch (type) {
    ItineraryItemType.attraction => 'attraction',
    ItineraryItemType.restaurant => 'restaurant',
    ItineraryItemType.hotel => 'hotel',
    ItineraryItemType.localEvent => 'local_event',
    ItineraryItemType.other => 'other',
  };

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final repo = context.read<TripRepository>();
    final muted = theme.textTheme.bodyMedium?.copyWith(
      color: AppColors.muted600,
    );
    return ListView(
      padding: const EdgeInsets.fromLTRB(24, 32, 24, 32),
      children: [
        Align(
          alignment: Alignment.centerLeft,
          child: InkWell(
            onTap: () => context.go('/trips'),
            child: Text(
              '← Back to My trips',
              style: theme.textTheme.bodyMedium?.copyWith(
                fontWeight: FontWeight.w500,
                color: AppColors.accent700,
              ),
            ),
          ),
        ),
        const SizedBox(height: 24),
        AsyncBody<Trip>(
          load: () => repo.getTrip(tripId),
          loadingText: 'Loading itinerary…',
          errorTitle: 'Itinerary could not be loaded',
          builder: (context, trip) => Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Container(
                padding: const EdgeInsets.all(24),
                decoration: BoxDecoration(
                  color: AppColors.surface,
                  borderRadius: BorderRadius.circular(AppRadii.card),
                  boxShadow: AppShadows.control,
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Eyebrow(
                      trip.where.isEmpty ? 'Trip destination' : trip.where,
                    ),
                    const SizedBox(height: 8),
                    Text(trip.title, style: theme.textTheme.headlineMedium),
                    const SizedBox(height: 16),
                    Wrap(
                      spacing: 28,
                      runSpacing: 8,
                      children: [
                        for (final line in [
                          formatDateRange(
                            trip.startDate,
                            trip.endDate,
                            withYear: true,
                          ),
                          '${trip.dayCount} days',
                          'Budget: ${formatMoney(trip.budgetLkr)}',
                        ])
                          Text(
                            line,
                            style: theme.textTheme.bodyMedium?.copyWith(
                              color: AppColors.muted700,
                            ),
                          ),
                      ],
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 24),
              if (trip.days.isEmpty)
                MessageCard(
                  title: 'No itinerary available',
                  message: 'This trip does not have a persisted itinerary yet.',
                )
              else
                for (final day in trip.days) ...[
                  Container(
                    padding: const EdgeInsets.all(24),
                    margin: const EdgeInsets.only(bottom: 16),
                    decoration: BoxDecoration(
                      color: AppColors.surface,
                      borderRadius: BorderRadius.circular(AppRadii.card),
                      boxShadow: AppShadows.control,
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.stretch,
                      children: [
                        Text(
                          'Day ${day.dayNumber}${day.title != null ? ' · ${day.title}' : ''}',
                          style: theme.textTheme.titleLarge,
                        ),
                        Text(_isoDate(day.date), style: muted),
                        const Padding(
                          padding: EdgeInsets.only(top: 12),
                          child: Divider(),
                        ),
                        if (day.summary != null)
                          Padding(
                            padding: const EdgeInsets.only(top: 12),
                            child: Text(day.summary!, style: muted),
                          ),
                        if (day.items.isEmpty)
                          Padding(
                            padding: const EdgeInsets.only(top: 12),
                            child: Text(
                              'No activities are recorded for this day.',
                              style: muted,
                            ),
                          ),
                        for (var i = 0; i < day.items.length; i++)
                          Container(
                            padding: EdgeInsets.only(
                              top: i == 0 ? 12 : 12,
                              bottom: 0,
                            ),
                            margin: EdgeInsets.only(top: i == 0 ? 0 : 12),
                            decoration: BoxDecoration(
                              border: i == 0
                                  ? null
                                  : const Border(
                                      top: BorderSide(color: AppColors.divider),
                                    ),
                            ),
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(
                                  [
                                        day.items[i].startTime,
                                        day.items[i].endTime,
                                      ].whereType<String>().join(' – ').isEmpty
                                      ? _typeName(day.items[i].type)
                                      : [
                                          day.items[i].startTime,
                                          day.items[i].endTime,
                                        ].whereType<String>().join(' – '),
                                  style: theme.textTheme.bodyMedium?.copyWith(
                                    fontWeight: FontWeight.w500,
                                    color: AppColors.accent700,
                                  ),
                                ),
                                const SizedBox(height: 4),
                                Text(
                                  day.items[i].title,
                                  style: theme.textTheme.titleSmall,
                                ),
                                if (day.items[i].description.isNotEmpty)
                                  Padding(
                                    padding: const EdgeInsets.only(top: 4),
                                    child: Text(
                                      day.items[i].description,
                                      style: muted,
                                    ),
                                  ),
                                if (day.items[i].location != null)
                                  Padding(
                                    padding: const EdgeInsets.only(top: 4),
                                    child: Text(
                                      day.items[i].location!,
                                      style: theme.textTheme.bodySmall
                                          ?.copyWith(fontSize: 11.5),
                                    ),
                                  ),
                              ],
                            ),
                          ),
                      ],
                    ),
                  ),
                ],
            ],
          ),
        ),
      ],
    );
  }
}
