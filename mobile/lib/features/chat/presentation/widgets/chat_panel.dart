import 'dart:async';

import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../../../core/theme/app_colors.dart';
import '../../../../core/widgets/mono_labels.dart';
import '../../../../data/models/chat_reply.dart';
import '../../../../data/models/trip_plan.dart';
import '../../../../data/repositories/chat_repository.dart';
import '../../chat_errors.dart';

const _suggestions = ['Swap a day', 'Cut LKR 10,000', 'Add a tea estate visit'];

/// After this long without a reply, tell the user planning is still running.
const _slowAfter = Duration(seconds: 20);

const _welcome = ChatMessage(
  fromUser: false,
  text: 'Hi! Tell me where you\'d like to go, for how long and what you enjoy, and I\'ll plan it for you.',
);

class _Bubble {
  _Bubble({
    required this.message,
    this.isError = false,
    this.retryText,
    this.caption,
  });

  final ChatMessage message;
  final bool isError;
  final String? retryText;

  /// Small status line under the bubble (the session's progress info).
  final String? caption;
}

/// Mirrors web/src/components/chat/ChatPanel.jsx. [onPlan] is called whenever a
/// reply carries a plan, so the page can hand it to the tabs. Give it a new
/// key to start a new trip.
class ChatPanel extends StatefulWidget {
  const ChatPanel({
    super.key,
    required this.onPlan,
    this.initialConversation = const [],
  });

  final ValueChanged<TripPlan> onPlan;
  final List<ChatMessage> initialConversation;

  @override
  State<ChatPanel> createState() => _ChatPanelState();
}

class _ChatPanelState extends State<ChatPanel> {
  late final List<_Bubble> _messages = [
    for (final m
        in widget.initialConversation.isEmpty
            ? [_welcome]
            : widget.initialConversation)
      _Bubble(message: m),
  ];
  final _input = TextEditingController();
  final _scroll = ScrollController();
  bool _thinking = false;
  bool _slow = false;
  String? _sessionId;
  Timer? _slowTimer;

  @override
  void dispose() {
    _slowTimer?.cancel();
    _input.dispose();
    _scroll.dispose();
    super.dispose();
  }

  void _scrollToEnd() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (_scroll.hasClients) {
        _scroll.animateTo(
          _scroll.position.maxScrollExtent,
          duration: const Duration(milliseconds: 200),
          curve: Curves.easeOut,
        );
      }
    });
  }

  /// Sends [text] and appends TripMate's reply, or an error bubble with a
  /// Retry button. The caller has already put the user's message in the chat.
  Future<void> _deliver(String text) async {
    final chat = context.read<ChatRepository>();
    setState(() {
      _thinking = true;
      _slow = false;
    });
    _slowTimer?.cancel();
    _slowTimer = Timer(_slowAfter, () {
      if (mounted && _thinking) setState(() => _slow = true);
    });
    _scrollToEnd();
    try {
      final reply = await chat.sendMessage(text, sessionId: _sessionId);
      if (!mounted) return;
      _sessionId ??= reply.sessionId;
      // A clarifying question or a failed plan returns no plan; keep whatever
      // was showing.
      if (reply.plan != null) widget.onPlan(reply.plan!);
      final failed = reply.status == 'failed';
      setState(() {
        _messages.add(
          _Bubble(
            message: ChatMessage(fromUser: false, text: reply.assistantMessage),
            // The planner could not finish: shown as an error, but a plain
            // resend would not help, so there is no Retry.
            isError: failed,
            caption: _progressCaption(reply),
          ),
        );
      });
    } catch (err) {
      if (!mounted) return;
      final failure = describeChatError(err);
      if (failure.isAuth) {
        // The session is gone; the API client already cleared it and the app
        // is heading back to the login page.
        return;
      }
      if (failure.resetSession) _sessionId = null;
      setState(() {
        _messages.add(
          _Bubble(
            message: ChatMessage(fromUser: false, text: failure.text),
            isError: true,
            // Only a retryable error offers Retry, which resends this text.
            retryText: failure.retryable ? text : null,
          ),
        );
      });
    } finally {
      _slowTimer?.cancel();
      if (mounted) {
        setState(() {
          _thinking = false;
          _slow = false;
        });
      }
      _scrollToEnd();
    }
  }

  /// The session's progress message / percentage, when the backend sets them.
  String? _progressCaption(ChatReply reply) {
    final parts = [
      if (reply.progressMessage != null && reply.progressMessage!.isNotEmpty)
        reply.progressMessage!,
      if (reply.progressPercent > 0 && reply.progressPercent < 100)
        '${reply.progressPercent}%',
    ];
    return parts.isEmpty ? null : parts.join(' · ');
  }

  void _send(String raw) {
    final text = raw.trim();
    if (text.isEmpty || _thinking) return;
    setState(() {
      // A new message replaces any earlier error (and its Retry button).
      _messages.removeWhere((b) => b.isError);
      _messages.add(_Bubble(message: ChatMessage(fromUser: true, text: text)));
      _input.clear();
    });
    _deliver(text);
  }

  /// Retry resends the same text without adding the user's message again.
  void _retry(String text) {
    if (_thinking) return;
    setState(() => _messages.removeWhere((b) => b.isError));
    _deliver(text);
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final canSend = _input.text.trim().isNotEmpty && !_thinking;
    return Container(
      clipBehavior: Clip.antiAlias,
      decoration: BoxDecoration(
        color: AppColors.surface,
        borderRadius: BorderRadius.circular(AppRadii.panel),
        boxShadow: AppShadows.control,
      ),
      child: Column(
        children: [
          Expanded(
            child: ListView(
              controller: _scroll,
              padding: const EdgeInsets.all(22),
              children: [
                for (final bubble in _messages) ...[
                  _MessageBubble(
                    bubble: bubble,
                    onRetry: _retry,
                    retryDisabled: _thinking,
                  ),
                  const SizedBox(height: 18),
                ],
                if (_thinking)
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          Container(
                            width: 6,
                            height: 6,
                            decoration: const BoxDecoration(
                              color: AppColors.accent,
                              shape: BoxShape.circle,
                            ),
                          ),
                          const SizedBox(width: 10),
                          Text(
                            'TripMate is thinking…',
                            style: theme.textTheme.bodyMedium?.copyWith(
                              color: AppColors.muted600,
                            ),
                          ),
                        ],
                      ),
                      if (_slow)
                        Padding(
                          padding: const EdgeInsets.only(top: 6, left: 16),
                          child: Text(
                            'Planning a trip can take a minute or two. Still working on it…',
                            style: theme.textTheme.bodySmall,
                          ),
                        ),
                    ],
                  ),
              ],
            ),
          ),
          const Divider(),
          Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                Wrap(
                  spacing: 8,
                  runSpacing: 8,
                  children: [
                    for (final label in _suggestions)
                      _SuggestionChip(
                        label: label,
                        onTap: _thinking ? null : () => _send(label),
                      ),
                  ],
                ),
                const SizedBox(height: 12),
                Row(
                  crossAxisAlignment: CrossAxisAlignment.end,
                  children: [
                    Expanded(
                      child: TextField(
                        controller: _input,
                        enabled: !_thinking,
                        minLines: 1,
                        maxLines: 5,
                        onChanged: (_) => setState(() {}),
                        textInputAction: TextInputAction.send,
                        onSubmitted: _send,
                        style: theme.textTheme.bodyMedium?.copyWith(
                          fontSize: 14,
                        ),
                        decoration: InputDecoration(
                          hintText: 'Ask for a change — \'swap Day 3 for something quieter\'',
                          hintMaxLines: 1,
                          contentPadding: const EdgeInsets.symmetric(
                            horizontal: 16,
                            vertical: 10,
                          ),
                          border: _cardBorder(AppColors.border),
                          enabledBorder: _cardBorder(AppColors.border),
                          disabledBorder: _cardBorder(AppColors.border),
                          focusedBorder: _cardBorder(AppColors.accent),
                        ),
                      ),
                    ),
                    const SizedBox(width: 8),
                    Semantics(
                      button: true,
                      label: 'Send message',
                      child: Material(
                        color: canSend ? AppColors.accent : AppColors.muted400,
                        shape: const CircleBorder(),
                        child: InkWell(
                          customBorder: const CircleBorder(),
                          onTap: canSend ? () => _send(_input.text) : null,
                          child: const SizedBox(
                            width: 38,
                            height: 38,
                            child: Icon(
                              Icons.send_rounded,
                              size: 16,
                              color: Colors.white,
                            ),
                          ),
                        ),
                      ),
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

  OutlineInputBorder _cardBorder(Color color) => OutlineInputBorder(
    borderRadius: BorderRadius.circular(AppRadii.card),
    borderSide: BorderSide(color: color),
  );
}

class _SuggestionChip extends StatelessWidget {
  const _SuggestionChip({required this.label, required this.onTap});

  final String label;
  final VoidCallback? onTap;

  @override
  Widget build(BuildContext context) {
    return Opacity(
      opacity: onTap == null ? 0.45 : 1,
      child: DecoratedBox(
        decoration: ShapeDecoration(
          color: AppColors.surface,
          shape: const StadiumBorder(side: BorderSide(color: AppColors.border)),
          shadows: AppShadows.control,
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
                style: Theme.of(context).textTheme.labelMedium
                    ?.copyWith(fontSize: 12, color: AppColors.ink),
              ),
            ),
          ),
        ),
      ),
    );
  }
}

class _MessageBubble extends StatelessWidget {
  const _MessageBubble({
    required this.bubble,
    required this.onRetry,
    required this.retryDisabled,
  });

  final _Bubble bubble;
  final void Function(String) onRetry;
  final bool retryDisabled;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final isUser = bubble.message.fromUser;
    final bg = isUser
        ? AppColors.muted900
        : bubble.isError
        ? AppColors.danger100
        : AppColors.inset;
    final border = isUser
        ? null
        : Border.all(
            color: bubble.isError
                ? AppColors.danger.withValues(alpha: 0.4)
                : AppColors.border,
          );
    final radius = BorderRadius.only(
      topLeft: const Radius.circular(16),
      topRight: const Radius.circular(16),
      bottomLeft: Radius.circular(isUser ? 16 : 4),
      bottomRight: Radius.circular(isUser ? 4 : 16),
    );
    return Column(
      crossAxisAlignment: isUser
          ? CrossAxisAlignment.end
          : CrossAxisAlignment.start,
      children: [
        MonoBadge(isUser ? 'You' : 'TripMate'),
        const SizedBox(height: 8),
        ConstrainedBox(
          constraints: BoxConstraints(
            maxWidth: MediaQuery.sizeOf(context).width * 0.86,
          ),
          child: Container(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
            decoration: BoxDecoration(
              color: bg,
              borderRadius: radius,
              border: border,
            ),
            child: Text(
              bubble.message.text,
              style: theme.textTheme.bodyLarge?.copyWith(
                fontSize: 14.5,
                height: 1.62,
                color: isUser ? Colors.white : AppColors.ink,
              ),
            ),
          ),
        ),
        if (bubble.caption != null)
          Padding(
            padding: const EdgeInsets.only(top: 6),
            child: Text(bubble.caption!, style: theme.textTheme.bodySmall),
          ),
        if (bubble.retryText != null) ...[
          const SizedBox(height: 8),
          Opacity(
            opacity: retryDisabled ? 0.45 : 1,
            child: Material(
              color: AppColors.accent100,
              shape: const StadiumBorder(),
              child: InkWell(
                customBorder: const StadiumBorder(),
                onTap: retryDisabled ? null : () => onRetry(bubble.retryText!),
                child: Padding(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 13,
                    vertical: 7,
                  ),
                  child: Text(
                    'Retry',
                    style: theme.textTheme.labelMedium?.copyWith(
                      color: AppColors.accent700,
                    ),
                  ),
                ),
              ),
            ),
          ),
        ],
      ],
    );
  }
}
