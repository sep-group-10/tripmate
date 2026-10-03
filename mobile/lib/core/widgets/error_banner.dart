import 'package:flutter/material.dart';

import '../theme/app_colors.dart';

enum BannerTone { danger, success }

/// `rounded-lg bg-danger-100 px-3 py-2.5 text-sm text-danger` banner.
class MessageBanner extends StatelessWidget {
  const MessageBanner(this.text, {super.key, this.tone = BannerTone.danger});

  final String text;
  final BannerTone tone;

  @override
  Widget build(BuildContext context) {
    final danger = tone == BannerTone.danger;
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
      decoration: BoxDecoration(
        color: danger ? AppColors.danger100 : AppColors.success100,
        borderRadius: BorderRadius.circular(AppRadii.input),
      ),
      child: Text(
        text,
        style: Theme.of(context).textTheme.bodyMedium?.copyWith(
          fontSize: 14,
          color: danger ? AppColors.danger : AppColors.success,
        ),
      ),
    );
  }
}
