import 'package:flutter/material.dart';

import '../theme/app_colors.dart';
import 'app_button.dart';
import 'empty_state.dart';

/// Runs [load] once and renders loading / error / data states. Give it a new
/// `key` to force a reload (e.g. when a search query changes).
class AsyncBody<T> extends StatefulWidget {
  const AsyncBody({
    super.key,
    required this.load,
    required this.builder,
    this.loadingText,
    this.errorTitle = 'Something went wrong',
  });

  final Future<T> Function() load;
  final Widget Function(BuildContext context, T data) builder;

  /// Status line shown while loading (e.g. "Loading your trips…"). Without
  /// it a spinner is shown.
  final String? loadingText;
  final String errorTitle;

  @override
  State<AsyncBody<T>> createState() => _AsyncBodyState<T>();
}

class _AsyncBodyState<T> extends State<AsyncBody<T>> {
  late Future<T> _future = widget.load();

  void _retry() => setState(() => _future = widget.load());

  @override
  Widget build(BuildContext context) {
    return FutureBuilder<T>(
      future: _future,
      builder: (context, snapshot) {
        if (snapshot.hasError) {
          return MessageCard(
            title: widget.errorTitle,
            message: '${snapshot.error}',
            action: AppButton(
              label: 'Try again',
              variant: AppButtonVariant.outline,
              size: AppButtonSize.small,
              onPressed: _retry,
            ),
          );
        }
        if (snapshot.connectionState != ConnectionState.done) {
          if (widget.loadingText != null) {
            return Text(
              widget.loadingText!,
              style: Theme.of(context).textTheme.bodyMedium
                  ?.copyWith(color: AppColors.muted600),
            );
          }
          return const Center(child: CircularProgressIndicator());
        }
        return widget.builder(context, snapshot.requireData);
      },
    );
  }
}
