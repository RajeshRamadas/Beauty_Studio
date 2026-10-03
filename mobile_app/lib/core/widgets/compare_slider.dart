import 'package:flutter/material.dart';
import '../theme/app_theme.dart';

class CompareSliderWidget extends StatefulWidget {
  final ImageProvider beforeImage;
  final ImageProvider afterImage;

  const CompareSliderWidget({
    Key? key,
    required this.beforeImage,
    required this.afterImage,
  }) : super(key: key);

  @override
  State<CompareSliderWidget> createState() => _CompareSliderWidgetState();
}

class _CompareSliderWidgetState extends State<CompareSliderWidget> {
  double _sliderValue = 0.5;

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(
      builder: (context, constraints) {
        final width = constraints.maxWidth;
        final height = constraints.maxHeight;

        return GestureDetector(
          onHorizontalDragUpdate: (details) {
            setState(() {
              _sliderValue = (details.localPosition.dx / width).clamp(0.0, 1.0);
            });
          },
          child: Stack(
            children: [
              // After Image (Base)
              Positioned.fill(
                child: Image(
                  image: widget.afterImage,
                  fit: BoxFit.cover,
                ),
              ),
              // Before Image (Clipped)
              Positioned.fill(
                child: ClipRect(
                  clipper: _RectClipper(_sliderValue * width),
                  child: Image(
                    image: widget.beforeImage,
                    fit: BoxFit.cover,
                  ),
                ),
              ),
              // Slider Divider Handle Line
              Positioned(
                left: (_sliderValue * width) - 1.5,
                top: 0,
                bottom: 0,
                child: Container(
                  width: 3,
                  color: AppTheme.gold,
                ),
              ),
              // Slider Handle Circle
              Positioned(
                left: (_sliderValue * width) - 18,
                top: (height / 2) - 18,
                child: Container(
                  width: 36,
                  height: 36,
                  decoration: const BoxDecoration(
                    color: AppTheme.gold,
                    shape: BoxShape.circle,
                    boxShadow: [
                      BoxShadow(color: Colors.black26, blurRadius: 4),
                    ],
                  ),
                  child: const Icon(Icons.unfold_more, size: 20, color: AppTheme.onGold),
                ),
              ),
            ],
          ),
        );
      },
    );
  }
}

class _RectClipper extends CustomClipper<Rect> {
  final double width;

  _RectClipper(this.width);

  @override
  Rect getClip(Size size) {
    return Rect.fromLTRB(0, 0, width, size.height);
  }

  @override
  bool shouldReclip(_RectClipper oldClipper) => oldClipper.width != width;
}
