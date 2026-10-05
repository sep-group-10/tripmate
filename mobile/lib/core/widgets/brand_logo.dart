import 'package:flutter/material.dart';

import '../theme/app_colors.dart';

/// The accent map-pin square and "TripMate" wordmark from the web header.
class BrandLogo extends StatelessWidget {
  const BrandLogo({super.key, this.size = 18});

  final double size;

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Container(
          width: 26,
          height: 26,
          decoration: BoxDecoration(
            color: AppColors.accent,
            borderRadius: BorderRadius.circular(AppRadii.input),
          ),
          child: const Icon(
            Icons.location_on_outlined,
            size: 15,
            color: Colors.white,
          ),
        ),
        const SizedBox(width: 10),
        Text(
          'TripMate',
          style: Theme.of(context).textTheme.titleLarge
              ?.copyWith(fontSize: size),
        ),
      ],
    );
  }
}
