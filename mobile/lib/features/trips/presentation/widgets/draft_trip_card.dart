import 'package:flutter/material.dart';

import '../../../../core/theme/app_colors.dart';
import '../../../../core/theme/app_text.dart';
import '../../../../core/widgets/app_button.dart';
import '../../../../data/models/trip.dart';

/// Mirrors web/src/components/DraftTripCard.jsx: a planning session in
/// progress with stage, progress bar, the opening prompt and actions.
class DraftTripCard extends StatefulWidget {
  const DraftTripCard({
    super.key,
    required this.trip,
    required this.onContinue,
    required this.onRename,
    required this.onDiscard,
    this.actionPending = false,
  });

  final Trip trip;
  final ValueChanged<Trip> onContinue;

  /// Returns true when the new name was saved.
  final Future<bool> Function(Trip trip, String title) onRename;
  final Future<void> Function(Trip trip) onDiscard;
  final bool actionPending;

  @override
  State<DraftTripCard> createState() => _DraftTripCardState();
}

class _DraftTripCardState extends State<DraftTripCard> {
  bool _renaming = false;
  String? _renameError;
  late final TextEditingController _title = TextEditingController(
    text: widget.trip.title,
  );

  @override
  void dispose() {
    _title.dispose();
    super.dispose();
  }

  Color get _barColor => switch (widget.trip.stage) {
    'Collecting preferences' => AppColors.warn,
    'Choosing hotels' => AppColors.info,
    'Budget optimisation' => AppColors.accent,
    _ => AppColors.muted300,
  };

  void _startRename() {
    _title.text = widget.trip.title;
    setState(() {
      _renameError = null;
      _renaming = true;
    });
  }

  Future<void> _saveTitle() async {
    final next = _title.text.trim();
    if (next.isEmpty) {
      setState(() => _renameError = 'Enter a trip name.');
      return;
    }
    if (next.length > 255) {
      setState(
        () => _renameError = 'Trip names must be 255 characters or fewer.',
      );
      return;
    }
    setState(() => _renameError = null);
    final saved = await widget.onRename(widget.trip, next);
    if (!mounted) return;
    if (saved) {
      setState(() => _renaming = false);
    } else {
      setState(
        () => _renameError =
            'The trip name could not be saved. Please try again.',
      );
    }
  }

  Future<void> _discard() async {
    final trip = widget.trip;
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        content: Text(
          'Discard “${trip.title.isEmpty ? 'Untitled trip' : trip.title}”? This also deletes its planning conversation.',
        ),
        actions: [
          AppButton(
            label: 'Cancel',
            variant: AppButtonVariant.outline,
            size: AppButtonSize.small,
            onPressed: () => Navigator.pop(context, false),
          ),
          AppButton(
            label: 'Discard',
            variant: AppButtonVariant.danger,
            size: AppButtonSize.small,
            onPressed: () => Navigator.pop(context, true),
          ),
        ],
      ),
    );
    if (confirmed == true) await widget.onDiscard(trip);
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final trip = widget.trip;
    final pending = widget.actionPending;
    return Container(
      clipBehavior: Clip.antiAlias,
      decoration: BoxDecoration(
        color: AppColors.surface,
        borderRadius: BorderRadius.circular(AppRadii.card),
        boxShadow: AppShadows.control,
      ),
      child: IntrinsicHeight(
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Container(width: 4, color: _barColor),
            Expanded(
              child: Padding(
                padding: const EdgeInsets.all(22),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Wrap(
                      spacing: 8,
                      runSpacing: 4,
                      crossAxisAlignment: WrapCrossAlignment.center,
                      children: [
                        Container(
                          padding: const EdgeInsets.symmetric(
                            horizontal: 10,
                            vertical: 4,
                          ),
                          decoration: BoxDecoration(
                            color: AppColors.warn100,
                            borderRadius: BorderRadius.circular(AppRadii.pill),
                          ),
                          child: Text(
                            'Draft',
                            style: theme.textTheme.labelMedium?.copyWith(
                              fontSize: 11.5,
                              color: AppColors.warn,
                            ),
                          ),
                        ),
                        if (trip.stage != null)
                          Text(
                            trip.stage!.toUpperCase(),
                            style: AppText.badge(),
                          ),
                      ],
                    ),
                    const SizedBox(height: 8),
                    if (_renaming)
                      _renameForm(theme, pending)
                    else
                      Text(trip.title, style: theme.textTheme.titleMedium),
                    const SizedBox(height: 8),
                    Text(
                      '${trip.where} · Edited ${trip.edited}',
                      style: theme.textTheme.labelMedium?.copyWith(
                        color: AppColors.muted600,
                      ),
                    ),
                    if (trip.prompt != null) ...[
                      const SizedBox(height: 14),
                      Container(
                        padding: const EdgeInsets.only(left: 14),
                        decoration: const BoxDecoration(
                          border: Border(
                            left: BorderSide(
                              color: AppColors.muted300,
                              width: 2,
                            ),
                          ),
                        ),
                        child: Text(
                          trip.prompt!,
                          style: theme.textTheme.bodyMedium?.copyWith(
                            fontStyle: FontStyle.italic,
                            color: AppColors.muted700,
                            height: 1.6,
                          ),
                        ),
                      ),
                    ],
                    if (trip.progressPercent != null) ...[
                      const SizedBox(height: 14),
                      ClipRRect(
                        borderRadius: BorderRadius.circular(AppRadii.pill),
                        child: LinearProgressIndicator(
                          value: trip.progressPercent! / 100,
                          minHeight: 6,
                          backgroundColor: AppColors.bg,
                          color: AppColors.accent,
                        ),
                      ),
                      const SizedBox(height: 8),
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Text(
                            'STARTED',
                            style: AppText.badge(color: AppColors.muted500),
                          ),
                          Text(
                            '${trip.progressPercent}% COMPLETE',
                            style: AppText.badge(color: AppColors.muted500),
                          ),
                          Text(
                            'GENERATED',
                            style: AppText.badge(color: AppColors.muted500),
                          ),
                        ],
                      ),
                    ],
                    const SizedBox(height: 14),
                    Wrap(
                      spacing: 6,
                      runSpacing: 6,
                      crossAxisAlignment: WrapCrossAlignment.center,
                      children: [
                        AppButton(
                          label: 'Continue planning',
                          variant: AppButtonVariant.outline,
                          size: AppButtonSize.small,
                          onPressed: () => widget.onContinue(trip),
                        ),
                        AppButton(
                          label: pending && _renaming ? 'Saving…' : 'Rename',
                          variant: AppButtonVariant.ghost,
                          size: AppButtonSize.small,
                          onPressed: pending || _renaming ? null : _startRename,
                        ),
                        AppButton(
                          label: pending ? 'Discarding…' : 'Discard',
                          variant: AppButtonVariant.ghost,
                          size: AppButtonSize.small,
                          onPressed: pending ? null : _discard,
                        ),
                      ],
                    ),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _renameForm(ThemeData theme, bool pending) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        TextField(
          controller: _title,
          autofocus: true,
          enabled: !pending,
          maxLength: 255,
          onSubmitted: (_) => _saveTitle(),
          style: theme.textTheme.bodyMedium,
          decoration: InputDecoration(
            counterText: '',
            semanticCounterText: 'Trip name',
            contentPadding: const EdgeInsets.symmetric(
              horizontal: 10,
              vertical: 8,
            ),
            border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(6),
              borderSide: const BorderSide(color: AppColors.border),
            ),
            enabledBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(6),
              borderSide: const BorderSide(color: AppColors.border),
            ),
          ),
        ),
        const SizedBox(height: 8),
        Row(
          children: [
            AppButton(
              label: pending ? 'Saving…' : 'Save name',
              size: AppButtonSize.small,
              onPressed: pending ? null : _saveTitle,
              disabledOpacity: 0.6,
            ),
            const SizedBox(width: 6),
            AppButton(
              label: 'Cancel',
              variant: AppButtonVariant.ghost,
              size: AppButtonSize.small,
              onPressed: pending
                  ? null
                  : () => setState(() {
                      _title.text = widget.trip.title;
                      _renameError = null;
                      _renaming = false;
                    }),
            ),
          ],
        ),
        if (_renameError != null)
          Padding(
            padding: const EdgeInsets.only(top: 6),
            child: Text(
              _renameError!,
              style: theme.textTheme.labelMedium?.copyWith(
                color: AppColors.danger,
              ),
            ),
          ),
      ],
    );
  }
}
