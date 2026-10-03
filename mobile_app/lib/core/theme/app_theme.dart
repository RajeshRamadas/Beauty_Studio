import 'package:flutter/material.dart';

/// "Champagne Noir": true black with champagne gold.
/// Neutral grounds keep skin tones, hair colour and makeup true in photos.
class AppTheme {
  static const Color background = Color(0xFF0C0C0C);
  static const Color surface = Color(0xFF181715);
  static const Color surfaceHigh = Color(0xFF22201D);
  static const Color lineBorder = Color(0xFF2A2824);
  static const Color textPrimary = Color(0xFFF5F1EA);
  static const Color mutedGrey = Color(0xFFA39E95);
  static const Color gold = Color(0xFFD9B66F);
  static const Color onGold = Color(0xFF1A1408);
  static const Color success = Color(0xFF8FD4A8);
  static const Color error = Color(0xFFF2998C);

  static const double radius = 20;

  static ThemeData get theme {
    final scheme = const ColorScheme.dark(
      primary: gold,
      onPrimary: onGold,
      secondary: gold,
      onSecondary: onGold,
      surface: surface,
      onSurface: textPrimary,
      error: error,
      onError: onGold,
      outline: lineBorder,
    );

    final pill = RoundedRectangleBorder(borderRadius: BorderRadius.circular(999));
    const buttonPadding = EdgeInsets.symmetric(vertical: 16, horizontal: 22);
    const buttonText = TextStyle(fontSize: 15, fontWeight: FontWeight.w700);

    OutlineInputBorder inputBorder(Color color) => OutlineInputBorder(
          borderRadius: BorderRadius.circular(14),
          borderSide: BorderSide(color: color),
        );

    return ThemeData(
      useMaterial3: true,
      brightness: Brightness.dark,
      colorScheme: scheme,
      scaffoldBackgroundColor: background,
      dividerColor: lineBorder,
      appBarTheme: const AppBarTheme(
        backgroundColor: background,
        surfaceTintColor: Colors.transparent,
        elevation: 0,
        centerTitle: false,
        iconTheme: IconThemeData(color: textPrimary),
        titleTextStyle: TextStyle(
          color: textPrimary,
          fontSize: 20,
          fontWeight: FontWeight.w600,
          letterSpacing: -0.3,
        ),
      ),
      cardTheme: CardThemeData(
        color: surface,
        surfaceTintColor: Colors.transparent,
        elevation: 0,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(radius),
          side: const BorderSide(color: lineBorder),
        ),
      ),
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          backgroundColor: gold,
          foregroundColor: onGold,
          disabledBackgroundColor: surfaceHigh,
          disabledForegroundColor: mutedGrey,
          elevation: 0,
          shape: pill,
          padding: buttonPadding,
          textStyle: buttonText,
        ),
      ),
      outlinedButtonTheme: OutlinedButtonThemeData(
        style: OutlinedButton.styleFrom(
          foregroundColor: textPrimary,
          side: const BorderSide(color: lineBorder),
          shape: pill,
          padding: buttonPadding,
          textStyle: buttonText,
        ),
      ),
      textButtonTheme: TextButtonThemeData(
        style: TextButton.styleFrom(foregroundColor: gold),
      ),
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: surface,
        labelStyle: const TextStyle(color: mutedGrey),
        hintStyle: const TextStyle(color: mutedGrey),
        floatingLabelStyle: const TextStyle(color: gold),
        border: inputBorder(lineBorder),
        enabledBorder: inputBorder(lineBorder),
        focusedBorder: inputBorder(gold),
        errorBorder: inputBorder(error),
      ),
      bottomNavigationBarTheme: const BottomNavigationBarThemeData(
        backgroundColor: surface,
        selectedItemColor: gold,
        unselectedItemColor: mutedGrey,
        type: BottomNavigationBarType.fixed,
        elevation: 0,
      ),
      snackBarTheme: const SnackBarThemeData(
        backgroundColor: surfaceHigh,
        contentTextStyle: TextStyle(color: textPrimary),
        behavior: SnackBarBehavior.floating,
      ),
      progressIndicatorTheme: const ProgressIndicatorThemeData(color: gold),
      listTileTheme: const ListTileThemeData(textColor: textPrimary, iconColor: mutedGrey),
    );
  }
}
