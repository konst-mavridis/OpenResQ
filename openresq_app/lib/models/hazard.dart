class Hazard {
  final String id;
  final String title;
  final String description;
  final String level;

  Hazard({
    required this.id,
    required this.title,
    required this.description,
    required this.level,
  });

  factory Hazard.fromJson(Map<String, dynamic> json) {
    return Hazard(
      id: json["id"],
      title: json["title"],
      description: json["description"],
      level: json["level"],
    );
  }
}
