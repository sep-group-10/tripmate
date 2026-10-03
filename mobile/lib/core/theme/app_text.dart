import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

import 'app_colors.dart';

/// Text styles that the Material TextTheme does not cover: the uppercase mono
/// micro-labels (`font-mono` in web/src/index.css) and the heading weight.
abstract final class AppText {
  /// Set by [AppTheme.light]; false in tests so nothing hits the network.
  static bool webFonts = true;

  /// IBM Plex Mono. [tracking] is in em, like Tailwind's `tracking-*`.
  static TextStyle mono(
    double size, {
    Color color = AppColors.muted600,
    FontWeight weight = FontWeight.w500,
    double tracking = 0,
  }) {
    final style = TextStyle(
      fontSize: size,
      fontWeight: weight,
      color: color,
      letterSpacing: size * tracking,
    );
    return webFonts
        ? GoogleFonts.ibmPlexMono(textStyle: style)
        : style.copyWith(fontFamily: 'monospace');
  }

  /// `font-mono text-eyebrow tracking-widest uppercase`.
  static TextStyle eyebrow({Color color = AppColors.muted600}) =>
      mono(11, color: color, tracking: 0.1);

  /// `font-mono text-badge tracking-wider uppercase` (section labels, badges).
  static TextStyle badge({Color color = AppColors.muted600}) =>
      mono(10, color: color, tracking: 0.05);
}
