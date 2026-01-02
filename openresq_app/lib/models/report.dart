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
  final String? assignedTo;
  final DateTime? assignedAt;

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
    required this.assignedTo,
    required this.assignedAt,
  });

  Report copyWithFromMap(Map<String, dynamic> data) {
    return Report(
      id: id,
      title: data["title"] ?? title,
      description: data["description"] ?? description,
      severity: data["severity"] ?? severity,
      status: data["status"] ?? status,
      latitude: data["latitude"] ?? latitude,
      longitude: data["longitude"] ?? longitude,
      media: data["media"] ?? media,
      eventType: data["event_type"] ?? eventType,
      assignedTo: data["assigned_to"] ?? assignedTo,
      assignedAt: data["assigned_at"] != null
          ? DateTime.tryParse(data["assigned_at"])
          : null,
    );
  }

  Report copyWithAssigned(String uid) {
    return Report(
      id: id,
      title: title,
      description: description,
      eventType: eventType,
      severity: severity,
      status: status,
      media: media,
      latitude: latitude,
      longitude: longitude,
      assignedTo: uid,
      assignedAt: DateTime.now(),
    );
  }


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
      assignedTo: json['assigned_to']?.toString(),
      assignedAt: json['assigned_at'] != null
          ? DateTime.tryParse(json['assigned_at'])
          : null,
    );
  }
}
