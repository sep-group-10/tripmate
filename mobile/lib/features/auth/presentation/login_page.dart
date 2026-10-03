import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:provider/provider.dart';

import '../../../core/theme/app_colors.dart';
import '../../../core/utils/validation.dart';
import '../../../core/widgets/app_button.dart';
import '../../../core/widgets/auth_scaffold.dart';
import '../../../core/widgets/error_banner.dart';
import '../../../core/widgets/form_input.dart';
import '../../../data/repositories/auth_repository.dart';

/// Mirrors web/src/pages/LoginPage.jsx (without the Google button, which is a
/// web-only widget).
class LoginPage extends StatefulWidget {
  const LoginPage({super.key});

  @override
  State<LoginPage> createState() => _LoginPageState();
}

class _LoginPageState extends State<LoginPage> {
  final _formKey = GlobalKey<FormState>();
  final _email = TextEditingController();
  final _password = TextEditingController();
  bool _submitting = false;
  String? _error;

  @override
  void dispose() {
    _email.dispose();
    _password.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    if (!_formKey.currentState!.validate()) return;
    setState(() {
      _submitting = true;
      _error = null;
    });
    try {
      await context.read<AuthRepository>().signIn(
        email: _email.text.trim(),
        password: _password.text,
      );
      if (mounted) context.go('/chat');
    } catch (e) {
      if (mounted) {
        setState(() {
          _submitting = false;
          _error = '$e';
        });
      }
    }
  }

  void _clearError(String _) {
    if (_error != null) setState(() => _error = null);
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return AuthScaffold(
      child: Form(
        key: _formKey,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            const AuthHeading(
              title: 'Welcome back',
              subtitle: 'Pick up where your last plan left off.',
            ),
            const SizedBox(height: 22),
            if (_error != null) ...[
              MessageBanner(_error!),
              const SizedBox(height: 22),
            ],
            FormInput(
              label: 'Email address',
              controller: _email,
              hint: 'you@example.com',
              keyboardType: TextInputType.emailAddress,
              autofillHints: const [AutofillHints.email],
              validator: validateEmail,
              onChanged: _clearError,
              textInputAction: TextInputAction.next,
            ),
            const SizedBox(height: 14),
            FormInput(
              label: 'Password',
              controller: _password,
              hint: 'Your password',
              obscure: true,
              autofillHints: const [AutofillHints.password],
              validator: validateLoginPassword,
              onChanged: _clearError,
              onSubmitted: (_) => _submit(),
            ),
            const SizedBox(height: 14),
            Align(
              alignment: Alignment.centerRight,
              child: AccentLink(
                'Forgot password?',
                onTap: () => context.push('/forgot-password'),
              ),
            ),
            const SizedBox(height: 22),
            AppButton(
              label: _submitting ? 'Working…' : 'Log in',
              size: AppButtonSize.large,
              busy: _submitting,
              onPressed: _submit,
            ),
            const SizedBox(height: 22),
            Wrap(
              alignment: WrapAlignment.center,
              crossAxisAlignment: WrapCrossAlignment.center,
              children: [
                Text(
                  'Don\'t have an account? ',
                  style: theme.textTheme.bodyMedium?.copyWith(
                    fontSize: 14,
                    color: AppColors.muted600,
                  ),
                ),
                AccentLink('Register', onTap: () => context.go('/register')),
              ],
            ),
          ],
        ),
      ),
    );
  }
}
