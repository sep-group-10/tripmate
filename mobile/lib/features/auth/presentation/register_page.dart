import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:provider/provider.dart';

import '../../../core/theme/app_colors.dart';
import '../../../core/utils/validation.dart';
import '../../../core/widgets/app_button.dart';
import '../../../core/widgets/auth_scaffold.dart';
import '../../../core/widgets/error_banner.dart';
import '../../../core/widgets/form_input.dart';
import '../../../data/api/api_exception.dart';
import '../../../data/repositories/auth_repository.dart';

/// Mirrors web/src/pages/RegisterPage.jsx.
class RegisterPage extends StatefulWidget {
  const RegisterPage({super.key});

  @override
  State<RegisterPage> createState() => _RegisterPageState();
}

class _RegisterPageState extends State<RegisterPage> {
  final _formKey = GlobalKey<FormState>();
  final _fullName = TextEditingController();
  final _email = TextEditingController();
  final _password = TextEditingController();
  bool _submitting = false;
  String? _error;

  // Server-side field errors from a VALIDATION_ERROR's details.
  String? _fullNameError;
  String? _emailError;
  String? _passwordError;

  @override
  void dispose() {
    _fullName.dispose();
    _email.dispose();
    _password.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    if (!_formKey.currentState!.validate()) return;
    setState(() {
      _submitting = true;
      _error = null;
      _fullNameError = _emailError = _passwordError = null;
    });
    final email = _email.text.trim();
    try {
      await context.read<AuthRepository>().register(
        fullName: _fullName.text.trim(),
        email: email,
        password: _password.text,
      );
      if (mounted) context.go('/check-inbox', extra: email);
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _submitting = false;
        if (e is ApiException &&
            e.code == 'VALIDATION_ERROR' &&
            e.details.isNotEmpty) {
          // Map the backend's field names to this form's fields.
          _fullNameError = e.detailFor('full_name');
          _emailError = e.detailFor('email');
          _passwordError = e.detailFor('password');
        } else {
          // EMAIL_ALREADY_EXISTS and anything else (network error,
          // unexpected server error) with the backend's own message.
          _error = '$e';
        }
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final muted = theme.textTheme.bodySmall?.copyWith(
      fontSize: 12.5,
      height: 1.6,
    );
    return AuthScaffold(
      child: Form(
        key: _formKey,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            const AuthHeading(
              title: 'Create your account',
              subtitle: 'Free while you plan your first trip.',
            ),
            const SizedBox(height: 22),
            if (_error != null) ...[
              MessageBanner(_error!),
              const SizedBox(height: 22),
            ],
            FormInput(
              label: 'Full name',
              controller: _fullName,
              hint: 'Alex Jordan',
              autofillHints: const [AutofillHints.name],
              validator: validateFullName,
              errorText: _fullNameError,
              textInputAction: TextInputAction.next,
            ),
            const SizedBox(height: 14),
            FormInput(
              label: 'Email address',
              controller: _email,
              hint: 'you@example.com',
              keyboardType: TextInputType.emailAddress,
              autofillHints: const [AutofillHints.email],
              validator: validateEmail,
              errorText: _emailError,
              textInputAction: TextInputAction.next,
            ),
            const SizedBox(height: 14),
            FormInput(
              label: 'Password',
              controller: _password,
              hint: 'At least 8 characters',
              obscure: true,
              autofillHints: const [AutofillHints.newPassword],
              validator: validatePassword,
              errorText: _passwordError,
              onSubmitted: (_) => _submit(),
            ),
            const SizedBox(height: 22),
            AppButton(
              label: _submitting ? 'Working…' : 'Create account',
              size: AppButtonSize.large,
              busy: _submitting,
              onPressed: _submit,
            ),
            const SizedBox(height: 12),
            Text.rich(
              TextSpan(
                style: muted,
                children: [
                  const TextSpan(
                    text: 'By creating an account you agree to our ',
                  ),
                  TextSpan(
                    text: 'Terms of Service',
                    style: muted?.copyWith(color: AppColors.accent700),
                  ),
                  const TextSpan(text: ' and '),
                  TextSpan(
                    text: 'Privacy Policy',
                    style: muted?.copyWith(color: AppColors.accent700),
                  ),
                  const TextSpan(text: '.'),
                ],
              ),
            ),
            const SizedBox(height: 22),
            Wrap(
              alignment: WrapAlignment.center,
              crossAxisAlignment: WrapCrossAlignment.center,
              children: [
                Text(
                  'Already have an account? ',
                  style: theme.textTheme.bodyMedium?.copyWith(
                    fontSize: 14,
                    color: AppColors.muted600,
                  ),
                ),
                AccentLink('Log in', onTap: () => context.go('/login')),
              ],
            ),
          ],
        ),
      ),
    );
  }
}
