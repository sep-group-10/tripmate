import 'package:flutter/material.dart';

import '../theme/app_colors.dart';

/// Tones from web/src/utils/pillTones.js.
enum PillTone { accent, info, success, warn, outline }

class PillTag extends StatelessWidget {
  const PillTag(this.text, {super.key, this.tone = PillTone.outline});

  final String text;
  final PillTone tone;

  @override
  Widget build(BuildContext context) {
    final (bg, fg) = switch (tone) {
      PillTone.accent => (AppColors.accent100, AppColors.accent700),
      PillTone.info => (AppColors.info100, AppColors.info),
      PillTone.success => (AppColors.success100, AppColors.success700),
      PillTone.warn => (AppColors.warn100, AppColors.warn),
      PillTone.outline => (null, AppColors.muted700),
    };
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
      decoration: BoxDecoration(
        color: bg,
        borderRadius: BorderRadius.circular(AppRadii.pill),
        border: tone == PillTone.outline
            ? Border.all(color: AppColors.border)
            : null,
      ),
      child: Text(
        text,
        style: Theme.of(context).textTheme.labelMedium
            ?.copyWith(fontSize: 11.5, fontWeight: FontWeight.w500, color: fg),
      ),
    );
  }
}
