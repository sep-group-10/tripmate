import 'package:flutter/material.dart';

import '../../../../core/theme/app_colors.dart';
import '../../../../core/theme/app_text.dart';
import '../../../../core/utils/formatters.dart';
import '../../../../core/widgets/app_button.dart';
import '../../../../core/widgets/pill_tag.dart';
import '../../../../data/models/trip.dart';

/// Mirrors web/src/components/GeneratedTripCard.jsx: cover with overlaid title,
/// quick facts, a day-by-day preview and actions. A generated trip can be saved
/// ([onSave]); a saved trip can be removed from saved ([onUnsave]).
class GeneratedTripCard extends StatelessWidget {
  const GeneratedTripCard({
    super.key,
    required this.trip,
    required this.onViewItinerary,
    this.onSave,
    this.onUnsave,
    this.onKeepRefining,
    this.actionPending = false,
  });

  final Trip trip;
  final ValueChanged<Trip> onViewItinerary;
  final ValueChanged<Trip>? onSave;
  final ValueChanged<Trip>? onUnsave;
  final ValueChanged<Trip>? onKeepRefining;
  final bool actionPending;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final isSaved = trip.status == TripStatus.saved;
    final facts = [
      ('Length', '${trip.dayCount} days'),
      ('Travellers', trip.travellers?.toString() ?? 'Not specified'),
      (
        'Budget',
        trip.budgetLkr > 0 ? formatMoney(trip.budgetLkr) : 'Not specified',
      ),
      (isSaved ? 'Updated' : 'Generated', trip.edited),
    ];

    return Container(
      clipBehavior: Clip.antiAlias,
      decoration: BoxDecoration(
        color: AppColors.surface,
        borderRadius: BorderRadius.circular(AppRadii.card),
        boxShadow: AppShadows.control,
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          SizedBox(
            height: 200,
            child: Stack(
              fit: StackFit.expand,
              children: [
                if (trip.coverImageUrl != null)
                  Image.network(trip.coverImageUrl!, fit: BoxFit.cover)
                else
                  CustomPaint(
                    painter: _StripePainter(),
                    child: Center(
                      child: Text(
                        (trip.where.isEmpty ? 'Trip itinerary' : trip.where)
                            .toUpperCase(),
                        textAlign: TextAlign.center,
                        style: AppText.mono(
                          11.5,
                          color: AppColors.muted500,
                          tracking: 0.05,
                        ),
                      ),
                    ),
                  ),
                const DecoratedBox(
                  decoration: BoxDecoration(
                    gradient: LinearGradient(
                      begin: Alignment.bottomCenter,
                      end: Alignment.topCenter,
                      stops: [0, 0.45, 0.7],
                      colors: [
                        Color(0xBF000000),
                        Color(0x1A000000),
                        Color(0x00000000),
                      ],
                    ),
                  ),
                ),
                Positioned(
                  top: 16,
                  left: 16,
                  child: PillTag(
                    isSaved ? 'Saved' : 'Generated',
                    tone: isSaved ? PillTone.success : PillTone.info,
                  ),
                ),
                Positioned(
                  left: 20,
                  right: 20,
                  bottom: 16,
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        trip.where.toUpperCase(),
                        style: AppText.mono(
                          11.5,
                          color: const Color(0xCCFFFFFF),
                          tracking: 0.1,
                        ),
                      ),
                      const SizedBox(height: 2),
                      Text(
                        trip.title,
                        style: theme.textTheme.titleLarge?.copyWith(
                          fontSize: 20,
                          color: Colors.white,
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
          Padding(
            padding: const EdgeInsets.all(22),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                Container(
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    color: AppColors.bg,
                    borderRadius: BorderRadius.circular(AppRadii.input),
                  ),
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
                                Text(
                                  label,
                                  style: theme.textTheme.labelMedium?.copyWith(
                                    fontSize: 11,
                                    color: AppColors.muted600,
                                  ),
                                ),
                                const SizedBox(height: 2),
                                Text(
                                  value,
                                  style: theme.textTheme.bodyMedium?.copyWith(
                                    fontWeight: FontWeight.w500,
                                  ),
                                ),
                              ],
                            ),
                          ),
                      ],
                    ),
                  ),
                ),
                const SizedBox(height: 16),
                if (trip.days.isEmpty)
                  Container(
                    padding: const EdgeInsets.only(top: 10),
                    decoration: const BoxDecoration(
                      border: Border(top: BorderSide(color: AppColors.divider)),
                    ),
                    child: Text(
                      'No itinerary has been saved for this trip yet.',
                      style: theme.textTheme.bodyMedium?.copyWith(
                        color: AppColors.muted600,
                      ),
                    ),
                  ),
                for (var i = 0; i < trip.days.length; i++)
                  Container(
                    padding: const EdgeInsets.symmetric(vertical: 10),
                    decoration: BoxDecoration(
                      border: i == 0
                          ? null
                          : const Border(
                              top: BorderSide(color: AppColors.divider),
                            ),
                    ),
                    child: Row(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        SizedBox(
                          width: 52,
                          child: Text(
                            'DAY ${trip.days[i].dayNumber}',
                            style: AppText.badge(color: AppColors.accent700),
                          ),
                        ),
                        const SizedBox(width: 16),
                        Expanded(
                          child: Text(
                            trip.days[i].items.isEmpty
                                ? (trip.days[i].summary ??
                                      'No activities recorded')
                                : trip.days[i].items
                                      .map((item) => item.title)
                                      .join(' · '),
                            style: theme.textTheme.bodyMedium?.copyWith(
                              height: 1.6,
                              color: AppColors.muted700,
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                const SizedBox(height: 16),
                Row(
                  children: [
                    Expanded(
                      child: Wrap(
                        spacing: 10,
                        runSpacing: 8,
                        children: [
                          AppButton(
                            label: 'View itinerary',
                            size: AppButtonSize.small,
                            onPressed: () => onViewItinerary(trip),
                          ),
                          if (!isSaved && onSave != null) ...[
                            AppButton(
                              label: actionPending ? 'Saving…' : 'Save trip',
                              variant: AppButtonVariant.outline,
                              size: AppButtonSize.small,
                              disabledOpacity: 0.6,
                              onPressed: actionPending
                                  ? null
                                  : () => onSave!(trip),
                            ),
                            AppButton(
                              label: 'Keep refining',
                              variant: AppButtonVariant.outline,
                              size: AppButtonSize.small,
                              onPressed: () => onKeepRefining?.call(trip),
                            ),
                          ],
                          if (isSaved && onUnsave != null)
                            AppButton(
                              label: actionPending ? 'Unsaving…' : 'Unsave',
                              variant: AppButtonVariant.outline,
                              size: AppButtonSize.small,
                              disabledOpacity: 0.6,
                              onPressed: actionPending
                                  ? null
                                  : () => onUnsave!(trip),
                            ),
                        ],
                      ),
                    ),
                    AppButton(
                      label: 'Share',
                      variant: AppButtonVariant.ghost,
                      size: AppButtonSize.small,
                      onPressed: () {},
                    ),
                  ],
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

/// The `repeating-linear-gradient(135deg, bg 0 7px, ink/5% 7px 8px)` cover
/// placeholder from the web card.
class _StripePainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    canvas.drawRect(Offset.zero & size, Paint()..color = AppColors.bg);
    final line = Paint()
      ..color = const Color(0x0D17191A)
      ..strokeWidth = 1;
    // 135deg stripes: step 8px measured across the stripes.
    const step = 8 * 1.4142;
    for (double x = -size.height; x < size.width + size.height; x += step) {
      canvas.drawLine(Offset(x, 0), Offset(x + size.height, size.height), line);
    }
  }

  @override
  bool shouldRepaint(_StripePainter oldDelegate) => false;
}
