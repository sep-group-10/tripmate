import 'package:flutter/material.dart';

import '../../../../core/theme/app_colors.dart';
import '../../../../core/theme/app_text.dart';
import '../../../../core/utils/formatters.dart';
import '../../../../core/widgets/app_button.dart';
import '../../../../core/widgets/empty_state.dart';
import '../../../../core/widgets/pill_tag.dart';
import '../../../../data/models/itinerary_day.dart';
import '../../../../core/widgets/mono_labels.dart';
import '../../../../data/models/itinerary_item.dart';
import '../../../../data/models/trip_plan.dart';
import 'tab_empty_states.dart';

(String, PillTone) _categoryTag(ItineraryItem item) => switch (item.type) {
  ItineraryItemType.attraction => ('Attraction', PillTone.info),
  ItineraryItemType.restaurant => ('Dining', PillTone.warn),
  ItineraryItemType.hotel => ('Stay', PillTone.outline),
  ItineraryItemType.localEvent => ('Event', PillTone.accent),
  ItineraryItemType.other => (
    item.rawCategory == null || item.rawCategory!.isEmpty
        ? 'Stop'
        : _humanize(item.rawCategory!),
    PillTone.outline,
  ),
};

String _humanize(String value) {
  final spaced = value.replaceAll('_', ' ');
  return spaced.isEmpty
      ? spaced
      : spaced[0].toUpperCase() + spaced.substring(1);
}

/// Mirrors web/src/components/chat/ItineraryTab.jsx.
class ItineraryTab extends StatefulWidget {
  const ItineraryTab({
    super.key,
    required this.days,
    this.unscheduled = const [],
    this.warnings = const [],
  });

  final List<ItineraryDay> days;
  final List<UnscheduledItem> unscheduled;
  final List<String> warnings;

  @override
  State<ItineraryTab> createState() => _ItineraryTabState();
}

class _ItineraryTabState extends State<ItineraryTab> {
  // null means "not chosen yet": default to the first day. 0 means "closed".
  int? _activeDay;
  int? _openDay;

  @override
  Widget build(BuildContext context) {
    final days = widget.days;
    if (days.isEmpty) {
      return EmptyStatePanel(
        title: tabEmptyStates['Itinerary']!.$1,
        message: tabEmptyStates['Itinerary']!.$2,
      );
    }
    final theme = Theme.of(context);
    final currentDay = _activeDay ?? days.first.dayNumber;
    final expandedDay = _openDay ?? days.first.dayNumber;
    final stopCount = days.fold<int>(0, (n, d) => n + d.items.length);

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Row(
          crossAxisAlignment: CrossAxisAlignment.end,
          children: [
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    '${days.length}-day itinerary',
                    style: theme.textTheme.titleLarge?.copyWith(fontSize: 19),
                  ),
                  Text(
                    days.length > 1
                        ? '${formatDate(days.first.date)} – ${formatDate(days.last.date)}'
                        : formatDate(days.first.date),
                    style: theme.textTheme.bodySmall?.copyWith(fontSize: 12.5),
                  ),
                ],
              ),
            ),
            Text(
              '$stopCount stops',
              style: theme.textTheme.bodySmall?.copyWith(fontSize: 12.5),
            ),
          ],
        ),
        const SizedBox(height: 16),
        SingleChildScrollView(
          scrollDirection: Axis.horizontal,
          child: Row(
            children: [
              for (final day in days)
                InkWell(
                  onTap: () => setState(() {
                    _activeDay = day.dayNumber;
                    _openDay = day.dayNumber;
                  }),
                  child: Container(
                    constraints: const BoxConstraints(minWidth: 56),
                    padding: const EdgeInsets.symmetric(
                      horizontal: 4,
                      vertical: 8,
                    ),
                    child: Column(
                      children: [
                        Container(
                          width: 30,
                          height: 30,
                          alignment: Alignment.center,
                          decoration: BoxDecoration(
                            shape: BoxShape.circle,
                            color: currentDay == day.dayNumber
                                ? AppColors.accent
                                : AppColors.surface,
                            border: Border.all(
                              color: currentDay == day.dayNumber
                                  ? AppColors.accent
                                  : AppColors.border,
                            ),
                          ),
                          child: Text(
                            '${day.dayNumber}',
                            style: theme.textTheme.labelMedium?.copyWith(
                              fontWeight: FontWeight.w600,
                              color: currentDay == day.dayNumber
                                  ? Colors.white
                                  : AppColors.muted600,
                            ),
                          ),
                        ),
                        const SizedBox(height: 6),
                        Text(
                          formatDate(day.date),
                          style: theme.textTheme.bodySmall?.copyWith(
                            fontSize: 11,
                            color: currentDay == day.dayNumber
                                ? AppColors.ink
                                : AppColors.muted500,
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
            ],
          ),
        ),
        const SizedBox(height: 10),
        for (final day in days) ...[
          _DaySection(
            day: day,
            open: expandedDay == day.dayNumber,
            onToggle: () => setState(() {
              _activeDay = day.dayNumber;
              _openDay = expandedDay == day.dayNumber ? 0 : day.dayNumber;
            }),
          ),
          const SizedBox(height: 10),
        ],
        if (widget.unscheduled.isNotEmpty)
          _NoteBox(
            title: 'Couldn\'t fit in',
            children: [
              for (final item in widget.unscheduled)
                Text.rich(
                  TextSpan(
                    children: [
                      TextSpan(
                        text: item.name,
                        style: const TextStyle(
                          fontWeight: FontWeight.w500,
                          color: AppColors.ink,
                        ),
                      ),
                      if (item.reason != null && item.reason!.isNotEmpty)
                        TextSpan(text: ' — ${item.reason}'),
                    ],
                  ),
                  style: theme.textTheme.bodyMedium?.copyWith(
                    color: AppColors.muted700,
                  ),
                ),
            ],
          ),
        if (widget.warnings.isNotEmpty)
          _NoteBox(
            title: 'Heads up',
            children: [
              for (final warning in widget.warnings)
                Text(
                  warning,
                  style: theme.textTheme.bodyMedium?.copyWith(
                    color: AppColors.warn,
                  ),
                ),
            ],
          ),
      ],
    );
  }
}

/// Inset box with a mono label and lines of text ("Couldn't fit in", "Heads up").
class _NoteBox extends StatelessWidget {
  const _NoteBox({required this.title, required this.children});

  final String title;
  final List<Widget> children;

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      margin: const EdgeInsets.only(bottom: 10),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppColors.inset,
        borderRadius: BorderRadius.circular(AppRadii.xl),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SectionLabel(title),
          for (final child in children)
            Padding(padding: const EdgeInsets.only(top: 8), child: child),
        ],
      ),
    );
  }
}

class _DaySection extends StatelessWidget {
  const _DaySection({
    required this.day,
    required this.open,
    required this.onToggle,
  });

  final ItineraryDay day;
  final bool open;
  final VoidCallback onToggle;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final items = day.items;
    final distance = day.distanceKm;
    return Container(
      clipBehavior: Clip.antiAlias,
      decoration: BoxDecoration(
        color: open ? AppColors.inset : AppColors.surface,
        borderRadius: BorderRadius.circular(AppRadii.panel),
        border: Border.all(
          color: open ? AppColors.accent200 : AppColors.border,
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          InkWell(
            onTap: onToggle,
            child: Padding(
              padding: const EdgeInsets.fromLTRB(18, 16, 18, 16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Container(
                        width: 8,
                        height: 8,
                        decoration: BoxDecoration(
                          shape: BoxShape.circle,
                          color: open ? AppColors.accent : AppColors.muted400,
                        ),
                      ),
                      const SizedBox(width: 10),
                      Text(
                        'Day ${day.dayNumber}',
                        style: theme.textTheme.titleMedium?.copyWith(
                          fontSize: 15.5,
                        ),
                      ),
                      const SizedBox(width: 10),
                      Expanded(
                        child: Text(
                          '${formatDate(day.date)}${day.dayType != null ? ' · ${_humanize(day.dayType!)}' : ''}',
                          overflow: TextOverflow.ellipsis,
                          style: theme.textTheme.labelMedium?.copyWith(
                            color: AppColors.muted600,
                          ),
                        ),
                      ),
                      Icon(
                        open ? Icons.expand_less : Icons.expand_more,
                        size: 16,
                        color: AppColors.muted600,
                      ),
                    ],
                  ),
                  const SizedBox(height: 8),
                  Padding(
                    padding: const EdgeInsets.only(left: 18),
                    child: Text(
                      '${items.length} stops${distance != null ? ' · ${distance.toStringAsFixed(1)} km' : ''}',
                      style: theme.textTheme.bodySmall?.copyWith(
                        fontSize: 12.5,
                        color: AppColors.muted700,
                      ),
                    ),
                  ),
                  if (items.isNotEmpty) ...[
                    const SizedBox(height: 8),
                    Padding(
                      padding: const EdgeInsets.only(left: 18),
                      child: Wrap(
                        spacing: 6,
                        runSpacing: 6,
                        children: [
                          for (var i = 0; i < items.length; i++)
                            Container(
                              padding: const EdgeInsets.fromLTRB(6, 5, 10, 5),
                              decoration: BoxDecoration(
                                color: AppColors.surface,
                                borderRadius: BorderRadius.circular(
                                  AppRadii.pill,
                                ),
                                border: Border.all(color: AppColors.border),
                              ),
                              child: Row(
                                mainAxisSize: MainAxisSize.min,
                                children: [
                                  Container(
                                    width: 16,
                                    height: 16,
                                    alignment: Alignment.center,
                                    decoration: const BoxDecoration(
                                      color: AppColors.accent100,
                                      shape: BoxShape.circle,
                                    ),
                                    child: Text(
                                      '${i + 1}',
                                      style: theme.textTheme.labelSmall
                                          ?.copyWith(
                                            fontSize: 10,
                                            letterSpacing: 0,
                                            fontWeight: FontWeight.w600,
                                            color: AppColors.accent700,
                                          ),
                                    ),
                                  ),
                                  const SizedBox(width: 6),
                                  Flexible(
                                    child: Text(
                                      items[i].title,
                                      style: theme.textTheme.bodySmall
                                          ?.copyWith(
                                            fontSize: 12.5,
                                            color: AppColors.ink,
                                          ),
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
          ),
          if (open) ...[
            const Divider(),
            Padding(
              padding: const EdgeInsets.fromLTRB(18, 4, 18, 18),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  for (var i = 0; i < items.length; i++)
                    _TimelineRow(
                      number: i + 1,
                      item: items[i],
                      isLast: i == items.length - 1,
                    ),
                  for (final warning in day.warnings)
                    Padding(
                      padding: const EdgeInsets.only(left: 38, top: 8),
                      child: Text(
                        warning,
                        style: theme.textTheme.bodySmall?.copyWith(
                          fontSize: 12.5,
                          color: AppColors.warn,
                        ),
                      ),
                    ),
                  const SizedBox(height: 8),
                  Padding(
                    padding: const EdgeInsets.only(left: 38),
                    child: Wrap(
                      spacing: 8,
                      runSpacing: 8,
                      children: [
                        // Display-only on the web too: editing a single day
                        // needs backend support.
                        AppButton(
                          label: 'Add a stop',
                          variant: AppButtonVariant.outline,
                          size: AppButtonSize.small,
                          onPressed: () {},
                        ),
                        AppButton(
                          label: 'Regenerate this day',
                          variant: AppButtonVariant.ghost,
                          size: AppButtonSize.small,
                          onPressed: () {},
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
    );
  }
}

class _TimelineRow extends StatelessWidget {
  const _TimelineRow({
    required this.number,
    required this.item,
    required this.isLast,
  });

  final int number;
  final ItineraryItem item;
  final bool isLast;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final (label, tone) = _categoryTag(item);
    return IntrinsicHeight(
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          SizedBox(
            width: 26,
            child: Column(
              children: [
                const SizedBox(height: 14),
                Container(
                  width: 22,
                  height: 22,
                  alignment: Alignment.center,
                  decoration: const BoxDecoration(
                    color: AppColors.accent,
                    shape: BoxShape.circle,
                  ),
                  child: Text(
                    '$number',
                    style: theme.textTheme.labelSmall?.copyWith(
                      fontSize: 11,
                      letterSpacing: 0,
                      fontWeight: FontWeight.w600,
                      color: Colors.white,
                    ),
                  ),
                ),
                if (!isLast)
                  Expanded(child: Container(width: 1, color: AppColors.border)),
              ],
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Container(
              margin: const EdgeInsets.only(top: 8),
              padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
              decoration: BoxDecoration(
                color: AppColors.surface,
                borderRadius: BorderRadius.circular(AppRadii.xl),
                border: Border.all(color: AppColors.border),
              ),
              child: Row(
                children: [
                  if (item.startTime != null) ...[
                    Text(
                      '${item.startTime}${item.endTime != null ? '–${item.endTime}' : ''}',
                      style: AppText.mono(
                        12,
                        color: AppColors.accent700,
                        weight: FontWeight.w400,
                      ),
                    ),
                    const SizedBox(width: 12),
                  ],
                  Expanded(
                    child: Text(
                      item.title,
                      style: theme.textTheme.bodyMedium?.copyWith(
                        fontSize: 14,
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                  ),
                  const SizedBox(width: 12),
                  PillTag(label, tone: tone),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}
