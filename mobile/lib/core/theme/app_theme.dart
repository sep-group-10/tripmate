import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

import 'app_colors.dart';
import 'app_text.dart';

/// Material theme matching the web app: orange accent, Schibsted Grotesk,
/// pill buttons, 8px inputs and 22px cards.
abstract final class AppTheme {
  /// [useWebFonts] fetches Schibsted Grotesk through google_fonts. Tests pass
  /// false so they do not hit the network.
  static ThemeData light({bool useWebFonts = true}) {
    const scheme = ColorScheme(
      brightness: Brightness.light,
      primary: AppColors.accent,
      onPrimary: Colors.white,
      primaryContainer: AppColors.accent100,
      onPrimaryContainer: AppColors.accent700,
      secondary: AppColors.info,
      onSecondary: Colors.white,
      secondaryContainer: AppColors.info100,
      onSecondaryContainer: AppColors.info700,
      error: AppColors.danger,
      onError: Colors.white,
      errorContainer: AppColors.danger100,
      onErrorContainer: AppColors.danger700,
      surface: AppColors.surface,
      onSurface: AppColors.ink,
      onSurfaceVariant: AppColors.muted700,
      surfaceContainerLowest: AppColors.surface,
      surfaceContainerLow: AppColors.muted100,
      surfaceContainer: AppColors.inset,
      surfaceContainerHigh: AppColors.muted200,
      surfaceContainerHighest: AppColors.muted300,
      outline: AppColors.border,
      outlineVariant: AppColors.divider,
      shadow: AppColors.ink,
    );

    AppText.webFonts = useWebFonts;
    final base = _textTheme();
    final TextTheme textTheme = useWebFonts
        ? GoogleFonts.schibstedGroteskTextTheme(base)
        : base;

    const pill = StadiumBorder();
    const buttonPadding = EdgeInsets.symmetric(horizontal: 20, vertical: 10);
    final buttonText = textTheme.labelLarge;

    OutlineInputBorder inputBorder(Color color, [double width = 1]) =>
        OutlineInputBorder(
          borderRadius: BorderRadius.circular(AppRadii.input),
          borderSide: BorderSide(color: color, width: width),
        );

    return ThemeData(
      useMaterial3: true,
      colorScheme: scheme,
      textTheme: textTheme,
      scaffoldBackgroundColor: AppColors.bg,
      dividerColor: AppColors.divider,
      splashFactory: InkRipple.splashFactory,
      appBarTheme: AppBarTheme(
        backgroundColor: AppColors.bg,
        foregroundColor: AppColors.ink,
        elevation: 0,
        scrolledUnderElevation: 0,
        surfaceTintColor: Colors.transparent,
        centerTitle: false,
        titleTextStyle: textTheme.titleLarge,
      ),
      cardTheme: CardThemeData(
        color: AppColors.surface,
        elevation: 0,
        margin: EdgeInsets.zero,
        surfaceTintColor: Colors.transparent,
        clipBehavior: Clip.antiAlias,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(AppRadii.card),
        ),
      ),
      filledButtonTheme: FilledButtonThemeData(
        style: FilledButton.styleFrom(
          backgroundColor: AppColors.accent,
          foregroundColor: Colors.white,
          disabledBackgroundColor: AppColors.accent.withValues(alpha: 0.5),
          disabledForegroundColor: Colors.white,
          minimumSize: const Size(0, 48),
          padding: buttonPadding,
          shape: pill,
          textStyle: buttonText,
        ),
      ),
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          backgroundColor: AppColors.accent,
          foregroundColor: Colors.white,
          elevation: 0,
          minimumSize: const Size(0, 48),
          padding: buttonPadding,
          shape: pill,
          textStyle: buttonText,
        ),
      ),
      outlinedButtonTheme: OutlinedButtonThemeData(
        style: OutlinedButton.styleFrom(
          backgroundColor: AppColors.surface,
          foregroundColor: AppColors.ink,
          side: const BorderSide(color: AppColors.border),
          minimumSize: const Size(0, 48),
          padding: buttonPadding,
          shape: pill,
          textStyle: buttonText,
        ),
      ),
      textButtonTheme: TextButtonThemeData(
        style: TextButton.styleFrom(
          foregroundColor: AppColors.muted700,
          minimumSize: const Size(0, 44),
          padding: buttonPadding,
          shape: pill,
          textStyle: buttonText,
        ),
      ),
      inputDecorationTheme: InputDecorationThemeData(
        filled: true,
        fillColor: AppColors.surface,
        isDense: true,
        contentPadding: const EdgeInsets.symmetric(
          horizontal: 12,
          vertical: 14,
        ),
        hintStyle: textTheme.bodyMedium?.copyWith(color: AppColors.muted500),
        labelStyle: textTheme.labelMedium,
        floatingLabelStyle: textTheme.labelMedium?.copyWith(
          color: AppColors.accent700,
        ),
        errorStyle: textTheme.bodySmall?.copyWith(color: AppColors.danger),
        border: inputBorder(AppColors.border),
        enabledBorder: inputBorder(AppColors.border),
        focusedBorder: inputBorder(AppColors.accent, 1.5),
        errorBorder: inputBorder(AppColors.danger),
        focusedErrorBorder: inputBorder(AppColors.danger, 1.5),
      ),
      chipTheme: ChipThemeData(
        backgroundColor: AppColors.surface,
        selectedColor: AppColors.accent100,
        side: const BorderSide(color: AppColors.border),
        shape: pill,
        labelStyle: textTheme.labelMedium?.copyWith(color: AppColors.ink),
        secondaryLabelStyle: textTheme.labelMedium?.copyWith(
          color: AppColors.accent700,
        ),
        showCheckmark: true,
        checkmarkColor: AppColors.accent700,
      ),
      navigationBarTheme: NavigationBarThemeData(
        backgroundColor: AppColors.surface,
        surfaceTintColor: Colors.transparent,
        elevation: 0,
        height: 68,
        indicatorColor: AppColors.accent100,
        labelTextStyle: WidgetStateProperty.resolveWith(
          (states) => textTheme.labelSmall?.copyWith(
            letterSpacing: 0,
            fontSize: 11.5,
            color: states.contains(WidgetState.selected)
                ? AppColors.accent700
                : AppColors.muted600,
          ),
        ),
        iconTheme: WidgetStateProperty.resolveWith(
          (states) => IconThemeData(
            size: 24,
            color: states.contains(WidgetState.selected)
                ? AppColors.accent700
                : AppColors.muted600,
          ),
        ),
      ),
      dialogTheme: DialogThemeData(
        backgroundColor: AppColors.surface,
        surfaceTintColor: Colors.transparent,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(AppRadii.card),
        ),
      ),
      snackBarTheme: SnackBarThemeData(
        backgroundColor: AppColors.muted900,
        contentTextStyle: textTheme.bodyMedium?.copyWith(color: Colors.white),
        behavior: SnackBarBehavior.floating,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(AppRadii.panel),
        ),
      ),
      dividerTheme: const DividerThemeData(
        color: AppColors.divider,
        thickness: 1,
        space: 1,
      ),
      progressIndicatorTheme: const ProgressIndicatorThemeData(
        color: AppColors.accent,
      ),
    );
  }

  /// Sizes follow the web `--text-*` tokens.
  static TextTheme _textTheme() => const TextTheme(
    headlineMedium: TextStyle(
      fontSize: 28,
      fontWeight: FontWeight.w600,
      letterSpacing: -0.6,
      height: 1.15,
      color: AppColors.ink,
    ),
    headlineSmall: TextStyle(
      fontSize: 26,
      fontWeight: FontWeight.w600,
      letterSpacing: -0.5,
      height: 1.2,
      color: AppColors.ink,
    ),
    titleLarge: TextStyle(
      fontSize: 17,
      fontWeight: FontWeight.w600,
      letterSpacing: -0.2,
      color: AppColors.ink,
    ),
    titleMedium: TextStyle(
      fontSize: 15,
      fontWeight: FontWeight.w600,
      color: AppColors.ink,
    ),
    titleSmall: TextStyle(
      fontSize: 13.5,
      fontWeight: FontWeight.w600,
      color: AppColors.ink,
    ),
    bodyLarge: TextStyle(fontSize: 15, height: 1.45, color: AppColors.ink),
    bodyMedium: TextStyle(fontSize: 13.5, height: 1.45, color: AppColors.ink),
    bodySmall: TextStyle(
      fontSize: 12.5,
      height: 1.4,
      color: AppColors.muted600,
    ),
    labelLarge: TextStyle(fontSize: 14, fontWeight: FontWeight.w500),
    labelMedium: TextStyle(
      fontSize: 13,
      fontWeight: FontWeight.w500,
      color: AppColors.muted700,
    ),
    labelSmall: TextStyle(
      fontSize: 11,
      fontWeight: FontWeight.w500,
      letterSpacing: 0.8,
      color: AppColors.muted600,
    ),
  );
}
