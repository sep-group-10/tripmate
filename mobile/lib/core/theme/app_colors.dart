import 'package:flutter/material.dart';

/// Design tokens mirrored from web/src/index.css (`@theme`).
abstract final class AppColors {
  static const bg = Color(0xFFECEDED);
  static const surface = Color(0xFFFFFFFF);
  static const inset = Color(0xFFF5F6F6);
  static const ink = Color(0xFF17191A);
  static const border = Color(0xFFE2E4E5);
  static const divider = Color(0xFFDFE1E2);

  static const accent = Color(0xFFE8532B);
  static const accent100 = Color(0xFFFDEFEB);
  static const accent200 = Color(0xFFFBDCD3);
  static const accent300 = Color(0xFFF8BDA9);
  static const accent400 = Color(0xFFF3937A);
  static const accent600 = Color(0xFFCF4220);
  static const accent700 = Color(0xFFA9331A);
  static const accent800 = Color(0xFF7C2614);

  static const muted100 = Color(0xFFF7F8F8);
  static const muted200 = Color(0xFFECEDED);
  static const muted300 = Color(0xFFDFE1E2);
  static const muted400 = Color(0xFFC3C7C9);
  static const muted500 = Color(0xFF9AA0A3);
  static const muted600 = Color(0xFF767C80);
  static const muted700 = Color(0xFF565C60);
  static const muted800 = Color(0xFF383D40);
  static const muted900 = Color(0xFF17191A);

  static const success = Color(0xFF12A26A);
  static const success100 = Color(0xFFE7F7F0);
  static const success700 = Color(0xFF0A6B45);
  static const danger = Color(0xFFD92D20);
  static const danger100 = Color(0xFFFDECEB);
  static const danger700 = Color(0xFF8F1C14);
  static const warn = Color(0xFFD68A00);
  static const warn100 = Color(0xFFFDF3E0);
  static const warn700 = Color(0xFF8A5A00);
  static const info = Color(0xFF2F6FF0);
  static const info100 = Color(0xFFEEF3FE);
  static const info700 = Color(0xFF1844A3);
}

/// Radii from the web theme (`--radius-*`).
abstract final class AppRadii {
  static const double input = 8;
  static const double badge = 6;
  static const double xl = 12;
  static const double panel = 14;
  static const double card = 22;
  static const double pill = 999;
}

/// Shadows from the web theme (`--shadow-*`).
abstract final class AppShadows {
  static const control = [
    BoxShadow(color: Color(0x0D17191A), blurRadius: 2, offset: Offset(0, 1)),
    BoxShadow(
      color: Color(0x0F17191A),
      blurRadius: 8,
      spreadRadius: -4,
      offset: Offset(0, 2),
    ),
  ];
  static const raised = [
    BoxShadow(color: Color(0x0A17191A), blurRadius: 4, offset: Offset(0, 2)),
    BoxShadow(
      color: Color(0x2417191A),
      blurRadius: 28,
      spreadRadius: -12,
      offset: Offset(0, 12),
    ),
  ];
  static const card = [
    BoxShadow(color: Color(0x0A17191A), blurRadius: 8, offset: Offset(0, 4)),
    BoxShadow(
      color: Color(0x3817191A),
      blurRadius: 64,
      spreadRadius: -24,
      offset: Offset(0, 32),
    ),
  ];
}
