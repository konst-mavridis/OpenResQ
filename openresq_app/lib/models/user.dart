class AppUser {
  final String uid;
  final String email;
  final String displayName;
  final String role;

  AppUser({
    required this.uid,
    required this.email,
    required this.displayName,
    required this.role,
  });

  factory AppUser.fromJson(Map<String, dynamic> json) {
    return AppUser(
      uid: json["uid"],
      email: json["email"],
      displayName: json["displayName"],
      role: json["role"],
    );
  }
}
