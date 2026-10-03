import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:provider/provider.dart';

import '../../../core/theme/app_colors.dart';
import '../../../core/utils/validation.dart';
import '../../../core/widgets/app_button.dart';
import '../../../core/widgets/auth_scaffold.dart';
import '../../../core/widgets/form_input.dart';
import '../../../data/repositories/auth_repository.dart';

/// Mirrors web/src/pages/ForgotPasswordPage.jsx.
class ForgotPasswordPage extends StatefulWidget {
  const ForgotPasswordPage({super.key});

  @override
  State<ForgotPasswordPage> createState() => _ForgotPasswordPageState();
}

class _ForgotPasswordPageState extends State<ForgotPasswordPage> {
  final _formKey = GlobalKey<FormState>();
  final _email = TextEditingController();
  bool _submitting = false;
  bool _sent = false;

  @override
  void dispose() {
    _email.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    if (!_formKey.currentState!.validate()) return;
    setState(() => _submitting = true);
    // The web page shows the same confirmation whether or not the address has
    // an account, so errors are not surfaced here either.
    try {
      await context.read<AuthRepository>().requestPasswordReset(
        _email.text.trim(),
      );
    } catch (_) {}
    if (mounted) {
      setState(() {
        _submitting = false;
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
    if (_sent) {
      return AuthScaffold(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.center,
          children: [
            Text('Check your inbox', style: theme.textTheme.headlineSmall),
            const SizedBox(height: 12),
            Text.rich(
              TextSpan(
                style: body,
                children: [
                  const TextSpan(text: 'If '),
                  TextSpan(
                    text: _email.text.trim(),
                    style: const TextStyle(fontWeight: FontWeight.w700),
                  ),
                  const TextSpan(
                    text: ' has an account, we sent a link to reset the password. It expires in 15 minutes.',
                  ),
                ],
              ),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 12),
            AccentLink('Back to log in', onTap: () => context.go('/login')),
          ],
        ),
      );
    }
    return AuthScaffold(
      child: Form(
        key: _formKey,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            const AuthHeading(
              title: 'Forgot your password?',
              subtitle: 'Enter your email and we\'ll send you a reset link.',
            ),
            const SizedBox(height: 22),
            FormInput(
              label: 'Email address',
              controller: _email,
              hint: 'you@example.com',
              keyboardType: TextInputType.emailAddress,
              validator: validateEmail,
              onSubmitted: (_) => _submit(),
            ),
            const SizedBox(height: 22),
            AppButton(
              label: _submitting ? 'Sending…' : 'Send reset link',
              size: AppButtonSize.large,
              busy: _submitting,
              onPressed: _submit,
            ),
            const SizedBox(height: 22),
            Wrap(
              alignment: WrapAlignment.center,
              crossAxisAlignment: WrapCrossAlignment.center,
              children: [
                Text('Remembered it? ', style: body),
                AccentLink('Log in', onTap: () => context.go('/login')),
              ],
            ),
          ],
        ),
      ),
    );
  }
}
