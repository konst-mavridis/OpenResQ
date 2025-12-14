class Report {
  final String id;
  final String title;
  final String description;
  final String eventType;
  final String severity;
  final double latitude;
  final double longitude;
  final List<dynamic> media;
  final String status;

  Report({
    required this.id,
    required this.title,
    required this.description,
    required this.eventType,
    required this.severity,
    required this.latitude,
    required this.longitude,
    required this.media,
    required this.status,
  });

  factory Report.fromJson(Map<String, dynamic> json) {
    double toDoubleSafe(dynamic v) {
      if (v == null) return 0.0;
      if (v is double) return v;
      if (v is int) return v.toDouble();
      if (v is String) {
        return double.tryParse(v) ?? 0.0;
      }
      if (v is num) return v.toDouble();
      return 0.0;
    }

    // Support multiple shapes: top-level latitude/longitude, lat/lng or nested location map
    dynamic latVal = json['latitude'] ?? json['lat'];
    dynamic lngVal = json['longitude'] ?? json['lng'];
    if ((latVal == null || lngVal == null) && json['location'] is Map) {
      final loc = json['location'] as Map<String, dynamic>;
      latVal = latVal ?? loc['lat'] ?? loc['latitude'];
      lngVal = lngVal ?? loc['lng'] ?? loc['longitude'];
    }

    return Report(
      id: (json['id'] ?? '').toString(),
      title: (json['title'] ?? '').toString(),
      description: (json['description'] ?? '').toString(),
      eventType: (json['event_type'] ?? json['eventType'] ?? '').toString(),
      severity: (json['severity'] ?? 'low').toString(),
      latitude: toDoubleSafe(latVal),
      longitude: toDoubleSafe(lngVal),
      media: json['media'] ?? [],
      status: (json['status'] ?? 'pending').toString(),
    );
  }
}
