import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:provider/provider.dart';

import '../../../core/theme/app_colors.dart';
import '../../../core/widgets/app_button.dart';
import '../../../core/widgets/auth_scaffold.dart';
import '../../../core/widgets/error_banner.dart';
import '../../../data/repositories/auth_repository.dart';

/// Mirrors web/src/pages/CheckInboxPage.jsx. [email] is the address the
/// verification link was sent to.
class CheckInboxPage extends StatefulWidget {
  const CheckInboxPage({super.key, required this.email});

  final String email;

  @override
  State<CheckInboxPage> createState() => _CheckInboxPageState();
}

class _CheckInboxPageState extends State<CheckInboxPage> {
  bool _sending = false;
  bool _sent = false;

  Future<void> _resend() async {
    setState(() => _sending = true);
    try {
      await context.read<AuthRepository>().resendVerification(widget.email);
    } catch (_) {}
    if (mounted) {
      setState(() {
        _sending = false;
        _sent = true;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final body = theme.textTheme.bodyMedium?.copyWith(
      fontSize: 14,
      color: AppColors.muted600,
    );
    return AuthScaffold(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.center,
        children: [
          Container(
            width: 48,
            height: 48,
            decoration: const BoxDecoration(
              color: AppColors.accent100,
              shape: BoxShape.circle,
            ),
            child: const Icon(
              Icons.mark_email_read_outlined,
              size: 22,
              color: AppColors.accent700,
            ),
          ),
          const SizedBox(height: 16),
          Text('Check your inbox', style: theme.textTheme.headlineSmall),
          const SizedBox(height: 6),
          Text.rich(
            TextSpan(
              style: body,
              children: [
                const TextSpan(text: 'We sent a verification link to '),
                TextSpan(
                  text: widget.email,
                  style: const TextStyle(fontWeight: FontWeight.w700),
                ),
                const TextSpan(text: '. Click it to activate your account.'),
              ],
            ),
            textAlign: TextAlign.center,
          ),
          if (_sent) ...[
            const SizedBox(height: 16),
            const MessageBanner(
              'A new verification email is on its way.',
              tone: BannerTone.success,
            ),
          ],
          const SizedBox(height: 16),
          AppButton(
            label: _sending ? 'Sending…' : 'Resend email',
            variant: AppButtonVariant.outline,
            onPressed: _sending ? null : _resend,
          ),
          const SizedBox(height: 16),
          Wrap(
            alignment: WrapAlignment.center,
            crossAxisAlignment: WrapCrossAlignment.center,
            children: [
              Text('Already verified? ', style: body),
              AccentLink('Log in', onTap: () => context.go('/login')),
            ],
          ),
        ],
      ),
    );
  }
}
