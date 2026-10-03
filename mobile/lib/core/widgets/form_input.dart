import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

import '../theme/app_colors.dart';

/// Labelled text field matching web/src/components/FormInput.jsx. Validates
/// when focus leaves the field (like the web's onBlur) and shows the error in
/// a row below with an alert icon. Set [obscure] for a password field with the
/// show/hide eye button.
class FormInput extends StatefulWidget {
  const FormInput({
    super.key,
    required this.label,
    required this.controller,
    this.hint,
    this.validator,
    this.keyboardType,
    this.obscure = false,
    this.enabled = true,
    this.errorText,
    this.onChanged,
    this.maxLength,
    this.autofillHints,
    this.textInputAction,
    this.onSubmitted,
  });

  final String label;
  final TextEditingController controller;
  final String? hint;
  final String? Function(String?)? validator;
  final TextInputType? keyboardType;
  final bool obscure;
  final bool enabled;

  /// An error from outside the form (e.g. the server); shown when the
  /// validator finds nothing.
  final String? errorText;
  final ValueChanged<String>? onChanged;
  final int? maxLength;
  final Iterable<String>? autofillHints;
  final TextInputAction? textInputAction;
  final ValueChanged<String>? onSubmitted;

  @override
  State<FormInput> createState() => _FormInputState();
}

class _FormInputState extends State<FormInput> {
  bool _showText = false;

  OutlineInputBorder _border(Color color) => OutlineInputBorder(
    borderRadius: BorderRadius.circular(AppRadii.input),
    borderSide: BorderSide(color: color),
  );

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return FormField<String>(
      initialValue: widget.controller.text,
      validator: (_) => widget.validator?.call(widget.controller.text),
      autovalidateMode: AutovalidateMode.onUnfocus,
      builder: (state) {
        final error = state.errorText ?? widget.errorText;
        final borderColor = error == null ? AppColors.border : AppColors.danger;
        return Opacity(
          opacity: widget.enabled ? 1 : 0.7,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Padding(
                padding: const EdgeInsets.only(bottom: 6),
                child: Text(widget.label, style: theme.textTheme.labelMedium),
              ),
              TextField(
                controller: widget.controller,
                enabled: widget.enabled,
                obscureText: widget.obscure && !_showText,
                keyboardType: widget.keyboardType,
                autofillHints: widget.autofillHints,
                textInputAction: widget.textInputAction,
                onSubmitted: widget.onSubmitted,
                maxLength: widget.maxLength,
                inputFormatters: widget.maxLength == null
                    ? null
                    : [LengthLimitingTextInputFormatter(widget.maxLength)],
                style: theme.textTheme.bodyMedium?.copyWith(fontSize: 14),
                onChanged: (value) {
                  state.didChange(value);
                  widget.onChanged?.call(value);
                },
                decoration: InputDecoration(
                  hintText: widget.hint,
                  counterText: '',
                  border: _border(borderColor),
                  enabledBorder: _border(borderColor),
                  disabledBorder: _border(borderColor),
                  focusedBorder: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(AppRadii.input),
                    borderSide: BorderSide(
                      color: error == null
                          ? AppColors.accent
                          : AppColors.danger,
                      width: 1.5,
                    ),
                  ),
                  contentPadding: EdgeInsets.fromLTRB(
                    12,
                    12,
                    widget.obscure ? 44 : 12,
                    12,
                  ),
                  suffixIcon: widget.obscure
                      ? IconButton(
                          tooltip: _showText
                              ? 'Hide password'
                              : 'Show password',
                          onPressed: () =>
                              setState(() => _showText = !_showText),
                          icon: Icon(
                            _showText
                                ? Icons.visibility_off_outlined
                                : Icons.visibility_outlined,
                            size: 16,
                            color: AppColors.muted600,
                          ),
                        )
                      : null,
                ),
              ),
              if (error != null)
                Padding(
                  padding: const EdgeInsets.only(top: 6),
                  child: Row(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Padding(
                        padding: EdgeInsets.only(top: 1),
                        child: Icon(
                          Icons.error_outline,
                          size: 14,
                          color: AppColors.danger,
                        ),
                      ),
                      const SizedBox(width: 6),
                      Expanded(
                        child: Text(
                          error,
                          style: theme.textTheme.bodySmall?.copyWith(
                            fontSize: 12,
                            color: AppColors.danger,
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
            ],
          ),
        );
      },
    );
  }
}
