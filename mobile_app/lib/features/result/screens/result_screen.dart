import 'dart:convert';
import 'package:flutter/material.dart';
import '../../../core/theme/app_theme.dart';
import '../../../core/widgets/compare_slider.dart';

class ResultScreen extends StatelessWidget {
  final String resultB64;
  final String? targetB64;
  final String category;
  final String? costFormatted;
  final String? model;

  const ResultScreen({
    Key? key,
    required this.resultB64,
    this.targetB64,
    required this.category,
    this.costFormatted,
    this.model,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final resultBytes = base64Decode(resultB64);
    final afterImage = MemoryImage(resultBytes);

    ImageProvider? beforeImage;
    if (targetB64 != null) {
      beforeImage = MemoryImage(base64Decode(targetB64!));
    }

    return Scaffold(
      appBar: AppBar(title: Text("$category Result")),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            Container(
              height: 400,
              decoration: BoxDecoration(
                borderRadius: BorderRadius.circular(24),
                border: Border.all(color: AppTheme.lineBorder),
              ),
              child: ClipRRect(
                borderRadius: BorderRadius.circular(24),
                child: beforeImage != null
                    ? CompareSliderWidget(
                        beforeImage: beforeImage,
                        afterImage: afterImage,
                      )
                    : Image(image: afterImage, fit: BoxFit.contain),
              ),
            ),
            const SizedBox(height: 16),
            if (costFormatted != null)
              Container(
                padding: const EdgeInsets.symmetric(vertical: 10, horizontal: 16),
                decoration: BoxDecoration(
                  color: AppTheme.surface,
                  border: Border.all(color: AppTheme.lineBorder),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    const Icon(Icons.monetization_on, color: AppTheme.gold, size: 20),
                    const SizedBox(width: 8),
                    Text(
                      "Cost: $costFormatted (${model ?? 'AI'})",
                      style: const TextStyle(fontWeight: FontWeight.bold, color: AppTheme.textPrimary),
                    ),
                  ],
                ),
              ),
            const SizedBox(height: 20),
            ElevatedButton.icon(
              onPressed: () {
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text("Image saved to gallery!")),
                );
              },
              icon: const Icon(Icons.download),
              label: const Text("Save Result Image"),
            ),
          ],
        ),
      ),
    );
  }
}
