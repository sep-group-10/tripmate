import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:provider/provider.dart';

import '../../../core/theme/app_colors.dart';
import '../../../core/utils/validation.dart';
import '../../../core/widgets/app_button.dart';
import '../../../core/widgets/app_modal.dart';
import '../../../core/widgets/choice_chip.dart';
import '../../../core/widgets/error_banner.dart';
import '../../../core/widgets/form_input.dart';
import '../../../core/widgets/mono_labels.dart';
import '../../../core/widgets/section_card.dart';
import '../../../data/models/user.dart';
import '../../../data/repositories/auth_repository.dart';

const _budgetOptions = ['Budget', 'Moderate', 'Luxury'];
const _paceOptions = ['Relaxed', 'Balanced', 'Packed'];
const _interestOptions = [
  'Culture',
  'Nature',
  'Food',
  'Adventure',
  'Relaxation',
  'Nightlife',
];

/// Mirrors web/src/pages/ProfilePage.jsx (minus the photo upload, which needs
/// a file picker, and the Google-only account branches).
class ProfilePage extends StatefulWidget {
  const ProfilePage({super.key});

  @override
  State<ProfilePage> createState() => _ProfilePageState();
}

class _ProfilePageState extends State<ProfilePage> {
  User? _user;
  bool _loading = true;
  String? _loadError;

  final _profileKey = GlobalKey<FormState>();
  final _fullName = TextEditingController();
  final _email = TextEditingController();
  bool _savingProfile = false;
  bool _savedProfile = false;
  String? _saveError;

  final _passwordKey = GlobalKey<FormState>();
  final _currentPassword = TextEditingController();
  final _newPassword = TextEditingController();
  final _confirmPassword = TextEditingController();
  bool _savingPassword = false;
  bool _savedPassword = false;
  String? _currentPasswordError;
  String? _newPasswordError;

  String _budget = 'Moderate';
  String _pace = 'Balanced';
  List<String> _interests = [];
  bool _savingPrefs = false;
  bool _savedPrefs = false;
  String? _prefsError;

  bool _exporting = false;
  String? _exportError;

  @override
  void initState() {
    super.initState();
    _load();
  }

  @override
  void dispose() {
    _fullName.dispose();
    _email.dispose();
    _currentPassword.dispose();
    _newPassword.dispose();
    _confirmPassword.dispose();
    super.dispose();
  }

  void _apply(User user) {
    _user = user;
    _fullName.text = user.name;
    _email.text = user.email;
    _budget = user.budgetStyle;
    _pace = user.pace;
    _interests = [...user.interests];
  }

  Future<void> _load() async {
    try {
      final user = await context.read<AuthRepository>().currentUser();
      if (!mounted) return;
      if (user == null) {
        context.go('/login');
        return;
      }
      setState(() {
        _apply(user);
        _loading = false;
      });
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _loadError = '$e';
        _loading = false;
      });
    }
  }

  /// Shows [setter]'s flag for two seconds, like the web SavedMessage.
  void _flash(void Function(bool) setter) {
    setState(() => setter(true));
    Future<void>.delayed(const Duration(seconds: 2), () {
      if (mounted) setState(() => setter(false));
    });
  }

  Future<void> _saveProfile() async {
    if (!_profileKey.currentState!.validate()) return;
    setState(() {
      _savingProfile = true;
      _saveError = null;
    });
    try {
      final user = await context.read<AuthRepository>().updateName(
        _fullName.text,
      );
      if (!mounted) return;
      setState(() {
        _user = user;
        _savingProfile = false;
      });
      _flash((v) => _savedProfile = v);
    } catch (e) {
      if (mounted) {
        setState(() {
          _saveError = '$e';
          _savingProfile = false;
        });
      }
    }
  }

  Future<void> _changePassword() async {
    setState(() {
      _currentPasswordError = _currentPassword.text.isEmpty
          ? 'Enter your current password'
          : null;
      _newPasswordError = validatePassword(_newPassword.text);
    });
    final mismatch = _confirmPassword.text != _newPassword.text;
    if (_currentPasswordError != null || _newPasswordError != null) return;
    if (mismatch) {
      setState(() => _newPasswordError = null);
      _confirmKey.currentState?.validate();
      return;
    }
    setState(() => _savingPassword = true);
    try {
      await context.read<AuthRepository>().changePassword(
        currentPassword: _currentPassword.text,
        newPassword: _newPassword.text,
      );
      if (!mounted) return;
      _currentPassword.clear();
      _newPassword.clear();
      _confirmPassword.clear();
      setState(() => _savingPassword = false);
      _flash((v) => _savedPassword = v);
    } catch (e) {
      if (mounted) {
        setState(() {
          _currentPasswordError = '$e';
          _savingPassword = false;
        });
      }
    }
  }

  final _confirmKey = GlobalKey<FormState>();

  Future<void> _savePreferences() async {
    setState(() {
      _savingPrefs = true;
      _prefsError = null;
    });
    try {
      final user = await context.read<AuthRepository>().updatePreferences(
        budgetStyle: _budget,
        pace: _pace,
        interests: _interests,
      );
      if (!mounted) return;
      setState(() {
        _user = user;
        _savingPrefs = false;
      });
      _flash((v) => _savedPrefs = v);
    } catch (e) {
      if (mounted) {
        setState(() {
          _prefsError = '$e';
          _savingPrefs = false;
        });
      }
    }
  }

  Future<void> _export() async {
    setState(() {
      _exporting = true;
      _exportError = null;
    });
    try {
      final json = await context.read<AuthRepository>().exportData();
      if (!mounted) return;
      setState(() => _exporting = false);
      await showDialog<void>(
        context: context,
        builder: (context) => AppModal(
          title: 'Export your data',
          footer: [
            AppButton(
              label: 'Close',
              variant: AppButtonVariant.outline,
              onPressed: () => Navigator.pop(context),
            ),
          ],
          children: [SelectableText(json)],
        ),
      );
    } catch (e) {
      if (mounted) {
        setState(() {
          _exportError = '$e';
          _exporting = false;
        });
      }
    }
  }

  Future<void> _deleteAccount() async {
    final auth = context.read<AuthRepository>();
    final deleted = await showDialog<bool>(
      context: context,
      builder: (context) => _DeleteAccountModal(auth: auth),
    );
    if (deleted == true && mounted) context.go('/login');
  }

  Future<void> _logout() async {
    await context.read<AuthRepository>().signOut();
    if (mounted) context.go('/login');
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final user = _user;
    final muted = theme.textTheme.bodySmall?.copyWith(
      fontSize: 12.5,
      color: AppColors.muted600,
    );
    return ListView(
      padding: const EdgeInsets.fromLTRB(24, 32, 24, 32),
      children: [
        const Eyebrow('TripMate account'),
        const SizedBox(height: 8),
        Text(
          'Profile',
          style: theme.textTheme.headlineMedium?.copyWith(fontSize: 34),
        ),
        const SizedBox(height: 6),
        Text(
          'Manage your personal information, account settings and travel preferences.',
          style: theme.textTheme.bodyLarge?.copyWith(color: AppColors.muted600),
        ),
        const SizedBox(height: 24),
        SectionCard(
          title: 'Personal information',
          badge: 'Account',
          children: [
            Row(
              children: [
                Container(
                  width: 60,
                  height: 60,
                  alignment: Alignment.center,
                  decoration: const BoxDecoration(
                    color: AppColors.accent100,
                    shape: BoxShape.circle,
                  ),
                  child: Text(
                    user?.initials ?? '?',
                    style: theme.textTheme.titleLarge?.copyWith(
                      fontSize: 20,
                      letterSpacing: 0.5,
                      color: AppColors.accent700,
                    ),
                  ),
                ),
              ],
            ),
            if (_loading)
              Text(
                'Loading your profile…',
                style: theme.textTheme.bodyMedium?.copyWith(
                  fontSize: 14,
                  color: AppColors.muted600,
                ),
              ),
            if (_loadError != null) MessageBanner(_loadError!),
            if (user != null)
              Form(
                key: _profileKey,
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    FormInput(
                      label: 'Full name',
                      controller: _fullName,
                      validator: validateFullName,
                    ),
                    const SizedBox(height: 16),
                    FormInput(
                      label: 'Email address',
                      controller: _email,
                      enabled: false,
                    ),
                    const SizedBox(height: 6),
                    Text('Email address cannot be changed.', style: muted),
                    if (_saveError != null) ...[
                      const SizedBox(height: 24),
                      MessageBanner(_saveError!),
                    ],
                    const SizedBox(height: 24),
                    _SaveRow(
                      message: _savedProfile ? 'Saved' : null,
                      button: AppButton(
                        label: _savingProfile ? 'Saving…' : 'Save changes',
                        onPressed: _savingProfile ? null : _saveProfile,
                      ),
                    ),
                  ],
                ),
              ),
          ],
        ),
        const SizedBox(height: 24),
        SectionCard(
          title: 'Account settings',
          badge: 'Security',
          children: [
            Form(
              key: _passwordKey,
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  FormInput(
                    label: 'Current password',
                    controller: _currentPassword,
                    hint: '••••••••',
                    obscure: true,
                    errorText: _currentPasswordError,
                    onChanged: (_) {
                      if (_currentPasswordError != null) {
                        setState(() => _currentPasswordError = null);
                      }
                    },
                  ),
                  const SizedBox(height: 16),
                  FormInput(
                    label: 'New password',
                    controller: _newPassword,
                    hint: 'At least 8 characters',
                    obscure: true,
                    errorText: _newPasswordError,
                    onChanged: (_) {
                      if (_newPasswordError != null) {
                        setState(() => _newPasswordError = null);
                      }
                    },
                  ),
                  const SizedBox(height: 16),
                  Form(
                    key: _confirmKey,
                    child: FormInput(
                      label: 'Confirm new password',
                      controller: _confirmPassword,
                      hint: 'Re-enter new password',
                      obscure: true,
                      validator: (value) => value != _newPassword.text
                          ? 'Passwords do not match'
                          : null,
                    ),
                  ),
                  const SizedBox(height: 24),
                  _SaveRow(
                    message: _savedPassword ? 'Password updated' : null,
                    button: AppButton(
                      label: _savingPassword ? 'Updating…' : 'Update password',
                      variant: AppButtonVariant.dark,
                      onPressed: _savingPassword ? null : _changePassword,
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
        const SizedBox(height: 24),
        SectionCard(
          title: 'Travel preferences',
          badge: 'Planning',
          children: [
            _ChoiceGroup(
              label: 'Budget style',
              options: _budgetOptions,
              isActive: (o) => _budget == o,
              onTap: (o) => setState(() => _budget = o),
            ),
            _ChoiceGroup(
              label: 'Preferred pace',
              options: _paceOptions,
              isActive: (o) => _pace == o,
              onTap: (o) => setState(() => _pace = o),
            ),
            _ChoiceGroup(
              label: 'Interests',
              options: _interestOptions,
              isActive: _interests.contains,
              onTap: (o) => setState(
                () => _interests = _interests.contains(o)
                    ? _interests.where((i) => i != o).toList()
                    : [..._interests, o],
              ),
              footer:
                  '${_interests.length} selected — we weight your daily plans towards these.',
            ),
            if (_prefsError != null) MessageBanner(_prefsError!),
            _SaveRow(
              message: _savedPrefs ? 'Preferences saved' : null,
              button: AppButton(
                label: _savingPrefs ? 'Saving…' : 'Save preferences',
                onPressed: _savingPrefs || user == null
                    ? null
                    : _savePreferences,
              ),
            ),
          ],
        ),
        const SizedBox(height: 24),
        SectionCard(
          title: 'Your data',
          badge: 'Privacy',
          children: [
            _ActionRow(
              title: 'Export your data',
              description: 'Download everything TripMate holds about your account as a JSON file.',
              button: AppButton(
                label: _exporting ? 'Preparing…' : 'Export data',
                variant: AppButtonVariant.outline,
                onPressed: _exporting ? null : _export,
              ),
            ),
            if (_exportError != null) MessageBanner(_exportError!),
            Container(
              padding: const EdgeInsets.only(top: 24),
              decoration: const BoxDecoration(
                border: Border(top: BorderSide(color: AppColors.divider)),
              ),
              child: _ActionRow(
                title: 'Delete account',
                titleColor: AppColors.danger,
                description: 'Permanently deactivates your account. This cannot be undone.',
                button: AppButton(
                  label: 'Delete account',
                  variant: AppButtonVariant.dangerOutline,
                  onPressed: _deleteAccount,
                ),
              ),
            ),
          ],
        ),
        const SizedBox(height: 24),
        if (user != null)
          Container(
            padding: const EdgeInsets.only(top: 16),
            decoration: const BoxDecoration(
              border: Border(top: BorderSide(color: AppColors.divider)),
            ),
            child: Row(
              children: [
                Container(
                  width: 32,
                  height: 32,
                  alignment: Alignment.center,
                  decoration: const BoxDecoration(
                    color: AppColors.accent100,
                    shape: BoxShape.circle,
                  ),
                  child: Text(
                    user.initials,
                    style: theme.textTheme.labelMedium?.copyWith(
                      fontSize: 12,
                      fontWeight: FontWeight.w600,
                      color: AppColors.accent700,
                    ),
                  ),
                ),
                const SizedBox(width: 10),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        user.name.trim().isEmpty ? 'Traveller' : user.name,
                        style: theme.textTheme.bodyMedium?.copyWith(
                          fontWeight: FontWeight.w500,
                        ),
                      ),
                      Text(
                        user.email,
                        style: theme.textTheme.bodySmall?.copyWith(
                          fontSize: 11.5,
                        ),
                      ),
                    ],
                  ),
                ),
                AppButton(
                  label: 'Log out',
                  variant: AppButtonVariant.ghost,
                  size: AppButtonSize.small,
                  onPressed: _logout,
                ),
              ],
            ),
          ),
      ],
    );
  }
}

class _SaveRow extends StatelessWidget {
  const _SaveRow({required this.message, required this.button});

  final String? message;
  final Widget button;

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.end,
      children: [
        if (message != null) ...[
          Text(
            message!,
            style: Theme.of(context).textTheme.bodySmall
                ?.copyWith(fontSize: 12.5, color: AppColors.success),
          ),
          const SizedBox(width: 12),
        ],
        button,
      ],
    );
  }
}

class _ChoiceGroup extends StatelessWidget {
  const _ChoiceGroup({
    required this.label,
    required this.options,
    required this.isActive,
    required this.onTap,
    this.footer,
  });

  final String label;
  final List<String> options;
  final bool Function(String) isActive;
  final void Function(String) onTap;
  final String? footer;

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Eyebrow(label),
        const SizedBox(height: 10),
        Wrap(
          spacing: 8,
          runSpacing: 8,
          children: [
            for (final option in options)
              AppChoiceChip(
                label: option,
                active: isActive(option),
                onTap: () => onTap(option),
              ),
          ],
        ),
        if (footer != null) ...[
          const SizedBox(height: 10),
          Text(
            footer!,
            style: Theme.of(context).textTheme.bodySmall
                ?.copyWith(fontSize: 12.5, color: AppColors.muted600),
          ),
        ],
      ],
    );
  }
}

class _ActionRow extends StatelessWidget {
  const _ActionRow({
    required this.title,
    required this.description,
    required this.button,
    this.titleColor,
  });

  final String title;
  final String description;
  final Widget button;
  final Color? titleColor;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          title,
          style: theme.textTheme.bodyMedium?.copyWith(
            fontSize: 14,
            fontWeight: FontWeight.w500,
            color: titleColor,
          ),
        ),
        const SizedBox(height: 2),
        Text(
          description,
          style: theme.textTheme.bodySmall?.copyWith(
            fontSize: 12.5,
            color: AppColors.muted600,
          ),
        ),
        const SizedBox(height: 12),
        button,
      ],
    );
  }
}

class _DeleteAccountModal extends StatefulWidget {
  const _DeleteAccountModal({required this.auth});

  final AuthRepository auth;

  @override
  State<_DeleteAccountModal> createState() => _DeleteAccountModalState();
}

class _DeleteAccountModalState extends State<_DeleteAccountModal> {
  final _password = TextEditingController();
  bool _deleting = false;
  String? _error;

  @override
  void dispose() {
    _password.dispose();
    super.dispose();
  }

  Future<void> _delete() async {
    setState(() {
      _deleting = true;
      _error = null;
    });
    try {
      await widget.auth.deleteAccount(password: _password.text);
      if (mounted) Navigator.pop(context, true);
    } catch (e) {
      if (mounted) {
        setState(() {
          _error = '$e';
          _deleting = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return AppModal(
      title: 'Delete your account?',
      subtitle: 'This action cannot be undone.',
      footer: [
        AppButton(
          label: 'Cancel',
          variant: AppButtonVariant.outline,
          onPressed: _deleting ? null : () => Navigator.pop(context, false),
        ),
        AppButton(
          label: _deleting ? 'Deleting…' : 'Delete account',
          variant: AppButtonVariant.danger,
          onPressed: _deleting || _password.text.isEmpty ? null : _delete,
        ),
      ],
      children: [
        if (_error != null) MessageBanner(_error!),
        FormInput(
          label: 'Enter your password to confirm',
          controller: _password,
          hint: '••••••••',
          obscure: true,
          onChanged: (_) => setState(() {}),
        ),
      ],
    );
  }
}
