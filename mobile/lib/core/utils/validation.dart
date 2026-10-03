// Ported from web/src/utils/validation.js. Each validator returns an error
// message, or null when the value is valid.

final emailPattern = RegExp(r'^[^\s@]+@[^\s@]+\.[^\s@]{2,}$');

String? validateFullName(String? value) {
  final v = value ?? '';
  if (v.isEmpty) return 'Full name is required';
  if (v.length > 255) return 'Full name must be 255 characters or fewer';
  if (v.trim().isEmpty) return 'Full name cannot be blank or only whitespace';
  return null;
}

String? validateEmail(String? value) {
  final v = (value ?? '').trim();
  if (v.isEmpty) return 'Email is required';
  if (!emailPattern.hasMatch(v)) return 'Enter a valid email address';
  return null;
}

String? validatePassword(String? value) {
  final v = value ?? '';
  if (v.isEmpty) return 'Password is required';
  if (v.length < 8) return 'Password must be at least 8 characters';
  if (v.length > 72) return 'Password must be 72 characters or fewer';
  if (v.trim().isEmpty) return 'Password cannot be blank or only whitespace';
  if (!RegExp(r'\p{L}', unicode: true).hasMatch(v) ||
      !RegExp(r'\p{N}', unicode: true).hasMatch(v)) {
    return 'Password must contain at least one letter and one number';
  }
  return null;
}

String? validateLoginPassword(String? value) =>
    (value ?? '').isEmpty ? 'Password is required' : null;
