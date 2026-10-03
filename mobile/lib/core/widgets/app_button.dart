import 'package:flutter/material.dart';

import '../theme/app_colors.dart';

/// Variants of web/src/components/Button.jsx.
enum AppButtonVariant { primary, dark, outline, danger, dangerOutline, ghost }

enum AppButtonSize {
  /// `px-5 py-2.5 text-sm`: the web Button default.
  regular,

  /// `px-3.5 py-1.5 text-xs`: card and header actions.
  small,

  /// `w-full px-6 py-3.5 text-md`: the auth form submit button.
  large,
}

class AppButton extends StatelessWidget {
  const AppButton({
    super.key,
    required this.label,
    required this.onPressed,
    this.variant = AppButtonVariant.primary,
    this.size = AppButtonSize.regular,
    this.busy = false,
    this.disabledOpacity = 0.7,
  });

  final String label;
  final VoidCallback? onPressed;
  final AppButtonVariant variant;
  final AppButtonSize size;

  /// Shows the small spinner the web submit buttons use.
  final bool busy;
  final double disabledOpacity;

  @override
  Widget build(BuildContext context) {
    final (bg, fg, border) = switch (variant) {
      AppButtonVariant.primary => (AppColors.accent, Colors.white, null),
      AppButtonVariant.dark => (AppColors.muted900, Colors.white, null),
      AppButtonVariant.outline => (
        AppColors.surface,
        AppColors.ink,
        AppColors.border,
      ),
      AppButtonVariant.danger => (AppColors.danger, Colors.white, null),
      AppButtonVariant.dangerOutline => (
        Colors.transparent,
        AppColors.danger,
        AppColors.danger,
      ),
      AppButtonVariant.ghost => (Colors.transparent, AppColors.muted700, null),
    };
    final (padding, fontSize) = switch (size) {
      AppButtonSize.regular => (
        const EdgeInsets.symmetric(horizontal: 20, vertical: 10),
        14.0,
      ),
      AppButtonSize.small => (
        const EdgeInsets.symmetric(horizontal: 14, vertical: 6),
        12.0,
      ),
      AppButtonSize.large => (
        const EdgeInsets.symmetric(horizontal: 24, vertical: 14),
        15.0,
      ),
    };
    final enabled = onPressed != null && !busy;
    final textStyle = Theme.of(context).textTheme.labelLarge!
        .copyWith(fontSize: fontSize, color: fg, fontWeight: FontWeight.w500);

    final content = Row(
      mainAxisSize: size == AppButtonSize.large
          ? MainAxisSize.max
          : MainAxisSize.min,
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        if (busy) ...[
          SizedBox(
            width: 14,
            height: 14,
            child: CircularProgressIndicator(
              strokeWidth: 2,
              color: fg,
              backgroundColor: fg.withValues(alpha: 0.35),
            ),
          ),
          const SizedBox(width: 8),
        ],
        Text(label, style: textStyle),
      ],
    );

    return Opacity(
      opacity: onPressed == null || busy ? disabledOpacity : 1,
      child: DecoratedBox(
        decoration: ShapeDecoration(
          color: bg,
          shape: StadiumBorder(
            side: border == null ? BorderSide.none : BorderSide(color: border),
          ),
          shadows: variant == AppButtonVariant.ghost
              ? null
              : AppShadows.control,
        ),
        child: Material(
          type: MaterialType.transparency,
          child: InkWell(
            customBorder: const StadiumBorder(),
            onTap: enabled ? onPressed : null,
            child: Padding(padding: padding, child: content),
          ),
        ),
      ),
    );
  }
}
