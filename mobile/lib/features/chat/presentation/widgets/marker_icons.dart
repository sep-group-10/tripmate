import 'dart:ui' as ui;

import 'package:flutter/painting.dart';
import 'package:google_maps_flutter/google_maps_flutter.dart';

/// Numbered pins in a day's color: the code-drawn equivalent of the web's
/// `<Pin background=… glyph={number}>`, so no image assets or Map ID are needed.
abstract final class MarkerIcons {
  static const _width = 34.0;
  static const _height = 42.0;
  static const _ratio = 3.0; // render at 3x so the pin stays sharp
  static final _cache = <(int, int), BitmapDescriptor>{};

  static Future<BitmapDescriptor> numbered(Color color, int number) async {
    final key = (color.toARGB32(), number);
    final cached = _cache[key];
    if (cached != null) return cached;

    final recorder = ui.PictureRecorder();
    final canvas = Canvas(recorder)..scale(_ratio);
    const radius = 15.0;
    const centre = Offset(_width / 2, radius + 2);

    // Teardrop: circle plus a tail pointing at the stop's coordinates.
    final pin = Path()
      ..addOval(Rect.fromCircle(center: centre, radius: radius))
      ..moveTo(centre.dx - 8, centre.dy + 11)
      ..lineTo(centre.dx, _height - 1)
      ..lineTo(centre.dx + 8, centre.dy + 11)
      ..close();
    canvas
      ..drawPath(
        pin.shift(const Offset(0, 1)),
        Paint()
          ..color = const Color(0x40000000)
          ..maskFilter = const MaskFilter.blur(BlurStyle.normal, 2),
      )
      ..drawPath(pin, Paint()..color = color)
      ..drawCircle(
        centre,
        radius - 1,
        Paint()
          ..style = PaintingStyle.stroke
          ..strokeWidth = 2
          ..color = const Color(0xFFFFFFFF),
      );

    final text = TextPainter(
      text: TextSpan(
        text: '$number',
        style: TextStyle(
          color: const Color(0xFFFFFFFF),
          fontSize: number > 9 ? 13 : 16,
          fontWeight: FontWeight.w700,
        ),
      ),
      textDirection: TextDirection.ltr,
    )..layout();
    text.paint(canvas, centre - Offset(text.width / 2, text.height / 2));

    final image = await recorder.endRecording().toImage(
      (_width * _ratio).round(),
      (_height * _ratio).round(),
    );
    final bytes = await image.toByteData(format: ui.ImageByteFormat.png);
    return _cache[key] = BitmapDescriptor.bytes(
      bytes!.buffer.asUint8List(),
      width: _width,
      height: _height,
    );
  }
}
