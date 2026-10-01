import 'package:flutter/material.dart';

class AppTheme {
  static const Color pinkPrimary = Color(0xFFDF3975);
  static const Color pinkLight = Color(0xFFFAF7F8);
  static const Color inkDark = Color(0xFF28232B);
  static const Color mutedGrey = Color(0xFF746D77);
  static const Color lineBorder = Color(0xFFEEE5EA);

  static ThemeData get lightTheme {
    return ThemeData(
      useMaterial3: true,
      colorScheme: ColorScheme.fromSeed(
        seedColor: pinkPrimary,
        primary: pinkPrimary,
        surface: pinkLight,
      ),
      scaffoldBackgroundColor: const Color(0xFFECE8EB),
      appBarTheme: const AppBarTheme(
        backgroundColor: Colors.white,
        elevation: 0,
        centerTitle: false,
        iconTheme: IconThemeData(color: inkDark),
        titleTextStyle: TextStyle(
          color: inkDark,
          fontSize: 20,
          fontWeight: FontWeight.bold,
        ),
      ),
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          backgroundColor: pinkPrimary,
          foregroundColor: Colors.white,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
          ),
          padding: const EdgeInsets.symmetric(vertical: 14, horizontal: 20),
          textStyle: const TextStyle(
            fontSize: 16,
            fontWeight: FontWeight.bold,
          ),
        ),
      ),
    );
  }
}
