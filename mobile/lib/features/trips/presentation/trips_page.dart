import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:provider/provider.dart';

import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_text.dart';
import '../../../core/utils/formatters.dart';
import '../../../core/widgets/app_button.dart';
import '../../../core/widgets/empty_state.dart';
import '../../../core/widgets/mono_labels.dart';
import '../../../data/models/trip.dart';
import '../../../data/repositories/trip_repository.dart';
import 'trip_filters.dart';
import 'widgets/draft_trip_card.dart';
import 'widgets/generated_trip_card.dart';
import 'widgets/stat_row.dart';

/// Mirrors web/src/pages/MyTripsPage.jsx.
class TripsPage extends StatefulWidget {
  const TripsPage({super.key});

  @override
  State<TripsPage> createState() => _TripsPageState();
}

class _TripsPageState extends State<TripsPage> {
  String _query = '';
  String _sort = 'Recent';
  String _filter = 'All';
  List<Trip> _trips = [];
  bool _loading = true;
  String? _loadError;
  final Set<String> _pending = {};

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    setState(() {
      _loading = true;
      _loadError = null;
    });
    try {
      final trips = await context.read<TripRepository>().getTrips();
      if (!mounted) return;
      setState(() {
        _trips = trips;
        _loading = false;
      });
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _loadError = '$e';
        _loading = false;
      });
    }
  }

  void _toast(String message) => ScaffoldMessenger.of(context)
    ..hideCurrentSnackBar()
    ..showSnackBar(SnackBar(content: Text(message)));

  void _replace(Trip updated) =>
      _trips = [for (final t in _trips) t.id == updated.id ? updated : t];

  /// Runs [action] for [trip] while showing its pending state.
  Future<bool> _run(Trip trip, Future<void> Function() action) async {
    setState(() => _pending.add(trip.id));
    try {
      await action();
      return true;
    } catch (e) {
      if (mounted) _toast('$e');
      return false;
    } finally {
      if (mounted) setState(() => _pending.remove(trip.id));
    }
  }

  Future<void> _changeStatus(
    Trip trip,
    Future<Trip> Function(String id) action,
  ) => _run(trip, () async {
    final updated = await action(trip.id);
    if (mounted) setState(() => _replace(updated));
  });

  Future<bool> _rename(Trip trip, String title) {
    final repo = context.read<TripRepository>();
    return _run(trip, () async {
      final updated = await repo.renameDraft(trip.id, title);
      if (!mounted) return;
      setState(() => _replace(updated));
      _toast('Draft renamed');
    });
  }

  Future<void> _discard(Trip trip) {
    final repo = context.read<TripRepository>();
    return _run(trip, () async {
      await repo.discardDraft(trip.id);
      if (!mounted) return;
      setState(() => _trips = _trips.where((t) => t.id != trip.id).toList());
      _toast('Draft discarded');
    });
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final repo = context.read<TripRepository>();
    final grouped = groupTrips(
      _trips,
      filter: _filter,
      query: _query.trim().toLowerCase(),
      sort: _sort,
    );
    final stats = [
      Stat('Trips planned', '${_trips.length}', 'In your account'),
      Stat(
        'Drafts open',
        '${_trips.where((t) => t.status == TripStatus.draft).length}',
        'Still in progress',
      ),
      Stat(
        'Days itinerated',
        '${_trips.where((t) => t.status != TripStatus.draft).fold<int>(0, (n, t) => n + t.dayCount)}',
        'Generated and saved trips',
      ),
      Stat(
        'Planned spend',
        formatMoney(_trips.fold<int>(0, (n, t) => n + t.budgetLkr)),
        'Sum of trip budgets',
      ),
    ];

    return ListView(
      padding: const EdgeInsets.fromLTRB(24, 32, 24, 32),
      children: [
        const Eyebrow('TripMate · Planner'),
        const SizedBox(height: 8),
        Text('My trips', style: theme.textTheme.headlineMedium),
        const SizedBox(height: 6),
        Text(
          'Pick up a planning session where you left it, or revisit an itinerary TripMate has already generated.',
          style: theme.textTheme.bodyMedium?.copyWith(
            color: AppColors.muted600,
          ),
        ),
        const SizedBox(height: 16),
        Align(
          alignment: Alignment.centerLeft,
          child: AppButton(
            label: 'New trip',
            onPressed: () => context.go('/chat'),
          ),
        ),
        const SizedBox(height: 28),
        if (!_loading && _loadError == null) ...[
          StatRow(stats: stats),
          const SizedBox(height: 28),
        ],
        _controls(theme, grouped.shownCount),
        const SizedBox(height: 28),
        if (_loading)
          Text(
            'Loading your trips…',
            style: theme.textTheme.bodyMedium?.copyWith(
              color: AppColors.muted600,
            ),
          ),
        if (_loadError != null)
          MessageCard(
            title: 'Trips could not be loaded',
            message: _loadError!,
            action: AppButton(
              label: 'Try again',
              variant: AppButtonVariant.outline,
              size: AppButtonSize.small,
              onPressed: _load,
            ),
          ),
        if (!_loading && _loadError == null) ...[
          _section(
            theme,
            title: 'Saved trips',
            subtitle:
                'Itineraries you\'ve kept. Ready to view, share or export.',
            trips: grouped.saved,
            card: (trip) => GeneratedTripCard(
              trip: trip,
              actionPending: _pending.contains(trip.id),
              onUnsave: (t) => _changeStatus(t, repo.unsaveTrip),
              onViewItinerary: (t) => context.push('/trips/${t.id}'),
            ),
          ),
          _section(
            theme,
            title: 'Generated itineraries',
            subtitle: 'Trips with generated itineraries.',
            trips: grouped.generated,
            card: (trip) => GeneratedTripCard(
              trip: trip,
              actionPending: _pending.contains(trip.id),
              onSave: (t) => _changeStatus(t, repo.saveTrip),
              onKeepRefining: (t) => context.go('/chat?tripId=${t.id}'),
              onViewItinerary: (t) => context.push('/trips/${t.id}'),
            ),
          ),
          _section(
            theme,
            title: 'Drafts',
            subtitle: 'Planning sessions that haven\'t produced a final itinerary yet.',
            trips: grouped.drafts,
            card: (trip) => DraftTripCard(
              trip: trip,
              actionPending: _pending.contains(trip.id),
              onRename: _rename,
              onDiscard: _discard,
              onContinue: (t) => context.go('/chat?tripId=${t.id}'),
            ),
          ),
          if (grouped.shownCount == 0)
            MessageCard(
              title: _trips.isEmpty ? 'No trips yet' : 'No trips match that',
              message: _trips.isEmpty
                  ? 'Trips you create will appear here. Start planning your first trip.'
                  : 'Try a different search term, or clear the filter to see every trip in your account.',
              action: _trips.isEmpty
                  ? null
                  : AppButton(
                      label: 'Clear filters',
                      variant: AppButtonVariant.outline,
                      size: AppButtonSize.small,
                      onPressed: () => setState(() {
                        _query = '';
                        _filter = 'All';
                      }),
                    ),
            ),
        ],
      ],
    );
  }

  Widget _controls(ThemeData theme, int shown) {
    final pillBorder = OutlineInputBorder(
      borderRadius: BorderRadius.circular(AppRadii.pill),
      borderSide: const BorderSide(color: AppColors.border),
    );
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        DecoratedBox(
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(AppRadii.pill),
            boxShadow: AppShadows.control,
          ),
          child: TextField(
            onChanged: (value) => setState(() => _query = value),
            style: theme.textTheme.bodyMedium,
            decoration: InputDecoration(
              hintText: 'Search trips…',
              contentPadding: const EdgeInsets.symmetric(
                horizontal: 14,
                vertical: 12,
              ),
              border: pillBorder,
              enabledBorder: pillBorder,
              focusedBorder: pillBorder.copyWith(
                borderSide: const BorderSide(color: AppColors.accent),
              ),
            ),
          ),
        ),
        const SizedBox(height: 12),
        Row(
          children: [
            DecoratedBox(
              decoration: ShapeDecoration(
                color: AppColors.surface,
                shape: const StadiumBorder(
                  side: BorderSide(color: AppColors.border),
                ),
                shadows: AppShadows.control,
              ),
              child: Padding(
                padding: const EdgeInsets.symmetric(horizontal: 14),
                child: DropdownButton<String>(
                  value: _sort,
                  underline: const SizedBox.shrink(),
                  isDense: true,
                  borderRadius: BorderRadius.circular(AppRadii.panel),
                  style: theme.textTheme.bodyMedium,
                  items: [
                    for (final e in tripSortLabels.entries)
                      DropdownMenuItem(value: e.key, child: Text(e.value)),
                  ],
                  onChanged: (value) => setState(() => _sort = value ?? _sort),
                ),
              ),
            ),
            const Spacer(),
            Text(
              '$shown ${shown == 1 ? 'trip' : 'trips'}'.toUpperCase(),
              style: AppText.badge(),
            ),
          ],
        ),
        const SizedBox(height: 12),
        SingleChildScrollView(
          scrollDirection: Axis.horizontal,
          child: Container(
            padding: const EdgeInsets.all(3),
            decoration: BoxDecoration(
              color: AppColors.muted300,
              borderRadius: BorderRadius.circular(AppRadii.pill),
            ),
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                for (final label in tripFilters)
                  _FilterSegment(
                    label: label,
                    selected: _filter == label,
                    onTap: () => setState(() => _filter = label),
                  ),
              ],
            ),
          ),
        ),
      ],
    );
  }

  Widget _section(
    ThemeData theme, {
    required String title,
    required String subtitle,
    required List<Trip> trips,
    required Widget Function(Trip) card,
  }) {
    if (trips.isEmpty) return const SizedBox.shrink();
    return Padding(
      padding: const EdgeInsets.only(bottom: 28),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Row(
            children: [
              Flexible(child: Text(title, style: theme.textTheme.titleLarge)),
              const SizedBox(width: 10),
              Container(
                padding: const EdgeInsets.symmetric(
                  horizontal: 10,
                  vertical: 2,
                ),
                decoration: BoxDecoration(
                  color: AppColors.surface,
                  borderRadius: BorderRadius.circular(AppRadii.pill),
                  border: Border.all(color: AppColors.border),
                ),
                child: Text(
                  '${trips.length}',
                  style: theme.textTheme.labelMedium?.copyWith(
                    fontSize: 11.5,
                    fontFeatures: const [FontFeature.tabularFigures()],
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 4),
          Text(
            subtitle,
            style: theme.textTheme.bodyMedium?.copyWith(
              color: AppColors.muted600,
            ),
          ),
          const SizedBox(height: 16),
          for (var i = 0; i < trips.length; i++) ...[
            if (i > 0) const SizedBox(height: 16),
            card(trips[i]),
          ],
        ],
      ),
    );
  }
}

class _FilterSegment extends StatelessWidget {
  const _FilterSegment({
    required this.label,
    required this.selected,
    required this.onTap,
  });

  final String label;
  final bool selected;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return DecoratedBox(
      decoration: ShapeDecoration(
        color: selected ? AppColors.surface : Colors.transparent,
        shape: const StadiumBorder(),
        shadows: selected ? AppShadows.control : null,
      ),
      child: Material(
        type: MaterialType.transparency,
        child: InkWell(
          customBorder: const StadiumBorder(),
          onTap: onTap,
          child: Padding(
            padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 6),
            child: Text(
              label,
              style: Theme.of(context).textTheme.labelMedium?.copyWith(
                color: selected ? AppColors.ink : AppColors.muted700,
              ),
            ),
          ),
        ),
      ),
    );
  }
}
