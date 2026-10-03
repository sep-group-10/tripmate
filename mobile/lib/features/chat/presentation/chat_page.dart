import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:provider/provider.dart';

import '../../../core/theme/app_colors.dart';
import '../../../core/widgets/app_button.dart';
import '../../../core/widgets/empty_state.dart';
import '../../../core/widgets/mono_labels.dart';
import '../../../data/models/chat_reply.dart';
import '../../../data/models/trip_plan.dart';
import '../../../data/repositories/chat_repository.dart';
import 'widgets/budget_tab.dart';
import 'widgets/chat_panel.dart';
import 'widgets/itinerary_tab.dart';
import 'widgets/map_tab.dart';
import 'widgets/summary_tab.dart';
import 'widgets/tab_empty_states.dart';

enum _PlanStatus { draft, generated, saved }

/// Chat first, then the four detail tabs of web/src/pages/TripPlanChatPage.jsx
/// (which shows them side by side on a wide screen).
const _tabs = ['Chat', 'Summary', 'Map', 'Itinerary', 'Budget'];

/// Mirrors web/src/pages/TripPlanChatPage.jsx. [tripId] resumes a draft's
/// planning conversation (the web `?tripId=` query parameter).
class ChatPage extends StatefulWidget {
  const ChatPage({super.key, this.tripId});

  final String? tripId;

  @override
  State<ChatPage> createState() => _ChatPageState();
}

class _ChatPageState extends State<ChatPage> {
  TripPlan? _plan;
  _PlanStatus _status = _PlanStatus.draft;
  int _chatKey = 0;
  int _tab = 0;

  List<ChatMessage> _conversation = const [];
  bool _resuming = false;
  String? _resumeError;

  @override
  void initState() {
    super.initState();
    _resume();
  }

  @override
  void didUpdateWidget(ChatPage old) {
    super.didUpdateWidget(old);
    if (old.tripId != widget.tripId) {
      _plan = null;
      _status = _PlanStatus.draft;
      _chatKey++;
      _tab = 0;
      _resume();
    }
  }

  Future<void> _resume() async {
    final id = widget.tripId;
    if (id == null) {
      setState(() {
        _conversation = const [];
        _resuming = false;
        _resumeError = null;
      });
      return;
    }
    setState(() {
      _resuming = true;
      _resumeError = null;
    });
    try {
      final conversation = await context.read<ChatRepository>().resumeTrip(id);
      if (!mounted || widget.tripId != id) return;
      setState(() {
        _conversation = conversation;
        _resuming = false;
      });
    } catch (e) {
      if (!mounted || widget.tripId != id) return;
      setState(() {
        _resumeError = '$e';
        _resuming = false;
      });
    }
  }

  void _handlePlan(TripPlan plan) => setState(() {
    _plan = plan;
    // A SAVED trip stays SAVED when the chat refines it.
    if (_status != _PlanStatus.saved) _status = _PlanStatus.generated;
  });

  void _saveTrip() {
    setState(() => _status = _PlanStatus.saved);
    ScaffoldMessenger.of(context)
      ..hideCurrentSnackBar()
      ..showSnackBar(const SnackBar(content: Text('Trip saved')));
  }

  void _newTrip() {
    setState(() {
      _plan = null;
      _status = _PlanStatus.draft;
      _chatKey++;
      _tab = 0;
      _conversation = const [];
    });
    if (widget.tripId != null) context.go('/chat');
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final loading = widget.tripId != null && _resuming;
    final failed = widget.tripId != null && _resumeError != null;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Padding(
          padding: const EdgeInsets.fromLTRB(24, 16, 24, 12),
          child: Wrap(
            alignment: WrapAlignment.spaceBetween,
            crossAxisAlignment: WrapCrossAlignment.center,
            runSpacing: 8,
            children: [
              const MonoBadge('Trip planner'),
              Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  AppButton(
                    label: 'New trip',
                    variant: AppButtonVariant.outline,
                    size: AppButtonSize.small,
                    onPressed: _newTrip,
                  ),
                  const SizedBox(width: 8),
                  _SaveTripButton(
                    status: _status,
                    onSave: _status == _PlanStatus.generated ? _saveTrip : null,
                  ),
                ],
              ),
            ],
          ),
        ),
        if (loading)
          Padding(
            padding: const EdgeInsets.fromLTRB(24, 0, 24, 24),
            child: Text(
              'Loading your draft conversation…',
              style: theme.textTheme.bodyMedium?.copyWith(
                color: AppColors.muted600,
              ),
            ),
          ),
        if (failed)
          Padding(
            padding: const EdgeInsets.fromLTRB(24, 0, 24, 24),
            child: MessageCard(
              title: 'Draft conversation could not be loaded',
              message: _resumeError!,
              action: Wrap(
                spacing: 8,
                children: [
                  AppButton(
                    label: 'Try again',
                    variant: AppButtonVariant.outline,
                    size: AppButtonSize.small,
                    onPressed: _resume,
                  ),
                  AppButton(
                    label: 'Back to My Trips',
                    variant: AppButtonVariant.outline,
                    size: AppButtonSize.small,
                    onPressed: () => context.go('/trips'),
                  ),
                ],
              ),
            ),
          ),
        if (!loading && !failed) ...[
          _TabBar(selected: _tab, onSelect: (i) => setState(() => _tab = i)),
          Expanded(
            child: Padding(
              padding: const EdgeInsets.fromLTRB(16, 0, 16, 16),
              child: IndexedStack(
                index: _tab,
                sizing: StackFit.expand,
                children: [
                  ChatPanel(
                    key: ValueKey('chat-$_chatKey-${widget.tripId}'),
                    onPlan: _handlePlan,
                    initialConversation: _conversation,
                  ),
                  for (final tab in _tabs.skip(1)) _detailPanel(tab),
                ],
              ),
            ),
          ),
        ],
      ],
    );
  }

  /// One right-hand panel of the web page, as a full-width page on mobile.
  Widget _detailPanel(String tab) {
    final plan = _plan;
    final Widget content;
    if (plan == null) {
      final empty = tabEmptyStates[tab]!;
      content = EmptyStatePanel(title: empty.$1, message: empty.$2);
    } else {
      content = switch (tab) {
        'Summary' => SummaryTab(summary: plan.summary),
        'Map' => MapTab(days: plan.days),
        'Itinerary' => ItineraryTab(days: plan.days),
        _ => BudgetTab(summary: plan.summary, budget: plan.budget),
      };
    }
    return Container(
      clipBehavior: Clip.antiAlias,
      decoration: BoxDecoration(
        color: AppColors.surface,
        borderRadius: BorderRadius.circular(AppRadii.panel),
        boxShadow: AppShadows.control,
      ),
      child: SingleChildScrollView(
        padding: const EdgeInsets.all(18),
        child: content,
      ),
    );
  }
}

/// Web tab strip: accent underline and semibold text for the selected tab.
class _TabBar extends StatelessWidget {
  const _TabBar({required this.selected, required this.onSelect});

  final int selected;
  final ValueChanged<int> onSelect;

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.fromLTRB(16, 0, 16, 12),
      decoration: const BoxDecoration(
        border: Border(bottom: BorderSide(color: AppColors.divider)),
      ),
      child: SingleChildScrollView(
        scrollDirection: Axis.horizontal,
        child: Row(
          children: [
            for (var i = 0; i < _tabs.length; i++)
              Semantics(
                button: true,
                selected: selected == i,
                child: InkWell(
                  onTap: () => onSelect(i),
                  child: Container(
                    padding: const EdgeInsets.symmetric(
                      horizontal: 14,
                      vertical: 9,
                    ),
                    decoration: BoxDecoration(
                      border: Border(
                        bottom: BorderSide(
                          width: 2,
                          color: selected == i
                              ? AppColors.accent
                              : Colors.transparent,
                        ),
                      ),
                    ),
                    child: Text(
                      _tabs[i],
                      style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                        fontSize: 14,
                        fontWeight: selected == i
                            ? FontWeight.w600
                            : FontWeight.w400,
                        color: selected == i
                            ? AppColors.ink
                            : AppColors.muted600,
                      ),
                    ),
                  ),
                ),
              ),
          ],
        ),
      ),
    );
  }
}

/// Mirrors web SaveTripButton: disabled while DRAFT, enabled when GENERATED,
/// a non-clickable "Saved ✓" once SAVED.
class _SaveTripButton extends StatelessWidget {
  const _SaveTripButton({required this.status, required this.onSave});

  final _PlanStatus status;
  final VoidCallback? onSave;

  @override
  Widget build(BuildContext context) {
    if (status == _PlanStatus.saved) {
      return Container(
        padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 6),
        decoration: BoxDecoration(
          color: AppColors.success100,
          borderRadius: BorderRadius.circular(AppRadii.pill),
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(
              'Saved',
              style: Theme.of(context).textTheme.labelMedium
                  ?.copyWith(fontSize: 12, color: AppColors.success700),
            ),
            const SizedBox(width: 6),
            const Icon(Icons.check, size: 14, color: AppColors.success700),
          ],
        ),
      );
    }
    return AppButton(
      label: 'Save trip',
      size: AppButtonSize.small,
      disabledOpacity: 0.45,
      onPressed: onSave,
    );
  }
}
