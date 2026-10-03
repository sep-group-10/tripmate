import 'package:flutter/material.dart';

import '../theme/app_colors.dart';
import '../theme/app_text.dart';

/// Uppercase mono eyebrow above a page title ("TripMate · Planner").
class Eyebrow extends StatelessWidget {
  const Eyebrow(this.text, {super.key, this.color = AppColors.muted600});

  final String text;
  final Color color;

  @override
  Widget build(BuildContext context) =>
      Text(text.toUpperCase(), style: AppText.eyebrow(color: color));
}

/// Small uppercase mono label (web `SectionLabel`).
class SectionLabel extends StatelessWidget {
  const SectionLabel(this.text, {super.key, this.color = AppColors.muted600});

  final String text;
  final Color color;

  @override
  Widget build(BuildContext context) =>
      Text(text.toUpperCase(), style: AppText.badge(color: color));
}

/// Grey mono badge (web SectionCard / chat-bubble badge).
class MonoBadge extends StatelessWidget {
  const MonoBadge(this.text, {super.key});

  final String text;

  @override
  Widget build(BuildContext context) => Container(
    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
    decoration: BoxDecoration(
      color: AppColors.muted300,
      borderRadius: BorderRadius.circular(AppRadii.badge),
    ),
    child: Text(
      text.toUpperCase(),
      style: AppText.badge(color: AppColors.muted700),
    ),
  );
}
