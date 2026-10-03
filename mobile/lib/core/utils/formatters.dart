// Ported from web/src/utils/tripFormat.js.

const _months = [
  'Jan',
  'Feb',
  'Mar',
  'Apr',
  'May',
  'Jun',
  'Jul',
  'Aug',
  'Sep',
  'Oct',
  'Nov',
  'Dec',
];

/// "Sep 12".
String formatDate(DateTime date) => '${_months[date.month - 1]} ${date.day}';

/// "Sep 12–18" (same month) or "Sep 28 – Oct 4"; [withYear] appends ", 2026".
String formatDateRange(DateTime start, DateTime end, {bool withYear = false}) {
  final sameMonth = start.month == end.month && start.year == end.year;
  final range = sameMonth
      ? '${formatDate(start)}–${end.day}'
      : '${formatDate(start)} – ${formatDate(end)}';
  return withYear ? '$range, ${end.year}' : range;
}

/// Inclusive number of days (Sep 12 to Sep 18 is 7).
int tripDurationDays(DateTime start, DateTime end) =>
    DateTime.utc(
      end.year,
      end.month,
      end.day,
    ).difference(DateTime.utc(start.year, start.month, start.day)).inDays +
    1;

/// 310400 -> "LKR 310,400".
String formatMoney(num amount, {String currency = 'LKR'}) {
  final digits = amount.round().toString();
  final grouped = digits.replaceAllMapped(
    RegExp(r'\B(?=(\d{3})+(?!\d))'),
    (_) => ',',
  );
  return '$currency $grouped';
}
