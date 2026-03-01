import 'package:flutter/material.dart';
import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:google_maps_flutter/google_maps_flutter.dart';
import 'package:openresq_app/widgets/add_team_member_dialog.dart';
import '../services/api_service.dart';

class TeamLeaderDashboard extends StatefulWidget {
  final String teamId;
  final String leaderUid;
  final String? name;

  const TeamLeaderDashboard({
    super.key,
    required this.teamId,
    required this.leaderUid,
    this.name,
  });

  @override
  State<TeamLeaderDashboard> createState() => _TeamLeaderDashboardState();
}

class _TeamLeaderDashboardState extends State<TeamLeaderDashboard> {
  final api = ApiService();

  GoogleMapController? mapController;

  BitmapDescriptor? leaderIcon;
  BitmapDescriptor? responderIcon;
  BitmapDescriptor? memberIcon;

  String? trackingUid; // Click-to-track mode

  @override
  void initState() {
    super.initState();
    _loadIcons();
  }

  Future<void> _loadIcons() async {
    leaderIcon = await BitmapDescriptor.asset(
      const ImageConfiguration(size: Size(48, 48)),
      "assets/leader.png",
    );
    responderIcon = await BitmapDescriptor.asset(
      const ImageConfiguration(size: Size(48, 48)),
      "assets/responder.png",
    );
    memberIcon = await BitmapDescriptor.asset(
      const ImageConfiguration(size: Size(48, 48)),
      "assets/member.png",
    );
    setState(() {});
  }
  LatLng _averageCenter(List<LatLng> points) {
    if (points.isEmpty) {
      return const LatLng(40.6401, 22.9444); // fallback
    }

    double lat = 0;
    double lng = 0;

    for (var p in points) {
      lat += p.latitude;
      lng += p.longitude;
    }

    return LatLng(lat / points.length, lng / points.length);
  }

  void _animateTo(LatLng target, {double zoom = 14}) {
    if (mapController != null) {
      mapController!.animateCamera(
        CameraUpdate.newCameraPosition(
          CameraPosition(target: target, zoom: zoom),
        ),
      );
    }
  }

  void _fitBounds(Set<Marker> markers) {
    if (markers.isEmpty || mapController == null) return;

    double minLat = markers.first.position.latitude;
    double maxLat = markers.first.position.latitude;
    double minLng = markers.first.position.longitude;
    double maxLng = markers.first.position.longitude;

    for (var m in markers) {
      minLat = m.position.latitude < minLat ? m.position.latitude : minLat;
      maxLat = m.position.latitude > maxLat ? m.position.latitude : maxLat;
      minLng = m.position.longitude < minLng ? m.position.longitude : minLng;
      maxLng = m.position.longitude > maxLng ? m.position.longitude : maxLng;
    }

    final bounds = LatLngBounds(
      southwest: LatLng(minLat, minLng),
      northeast: LatLng(maxLat, maxLng),
    );

    mapController!.animateCamera(CameraUpdate.newLatLngBounds(bounds, 80));
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
      title: Text( "${widget.name ?? "Unnamed Team"}'s Leader", 
                    style: const TextStyle( fontSize: 20, fontWeight: FontWeight.bold, ), 
              ),
      actions: [
          IconButton(
            icon: const Icon(Icons.logout),
            onPressed: () async {
              await FirebaseAuth.instance.signOut();
              if (!mounted) return;
              Navigator.pushNamedAndRemoveUntil(context, '/', (route) => false);
            },
          ),
        ]
        ),
      body: SingleChildScrollView(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [

            // TEAM INFO
            Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text("Team Name: ${widget.name ?? "Unnamed Team"}",
                      style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
                  Text(
                    "Team ID: ${widget.teamId}",
                    style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                  ),
                ],
              ),
            ),

            const Divider(),

            // TEAM MEMBERS LIST
            Padding(
              padding: const EdgeInsets.all(16),
              child: const Text(
                "Team Members",
                style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
              ),
            ),

            StreamBuilder(
              stream: FirebaseFirestore.instance
                  .collection("users")
                  .where("team_id", isEqualTo: widget.teamId)
                  .snapshots(),
              builder: (context, snapshot) {
                if (!snapshot.hasData) {
                  return const Center(child: CircularProgressIndicator());
                }

                final members = snapshot.data!.docs;

                return ListView.builder(
                  shrinkWrap: true,
                  physics: const NeverScrollableScrollPhysics(),
                  itemCount: members.length,
                  itemBuilder: (context, index) {
                    final user = members[index];
                    final data = user.data();

                    final name = data["displayName"]
                        ?? data["display_name"]
                        ?? data["email"]
                        ?? "Unknown User";

                    return ListTile(
                      leading: const Icon(Icons.person),
                      title: Text(name),
                      subtitle: Text("UID: ${user.id}"),
                    );
                  },
                );
              },
            ),

            const Divider(),

            // PENDING REQUESTS
            Padding(
              padding: const EdgeInsets.all(16),
              child: const Text(
                "Pending Requests",
                style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
              ),
            ),

            StreamBuilder(
              stream: FirebaseFirestore.instance
                  .collection("team_join_requests")
                  .where("team_id", isEqualTo: widget.teamId)
                  .snapshots(),
              builder: (context, snapshot) {
                if (!snapshot.hasData) {
                  return const Center(child: CircularProgressIndicator());
                }

                final requests = snapshot.data!.docs;

                if (requests.isEmpty) {
                  return const Padding(
                    padding: EdgeInsets.all(16),
                    child: Text("No pending join requests."),
                  );
                }

                return ListView.builder(
                  shrinkWrap: true,
                  physics: const NeverScrollableScrollPhysics(),
                  itemCount: requests.length,
                  itemBuilder: (context, index) {
                    final req = requests[index];
                    final data = req.data();

                    return ListTile(
                      leading: const Icon(Icons.person_add),
                      title: Text(data["responder_email"]),
                      trailing: Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          IconButton(
                            icon: const Icon(Icons.check, color: Colors.green),
                            onPressed: () async {
                              await api.post("/teams/approve_join", {
                                "request_id": req.id,
                              });
                            },
                          ),
                          IconButton(
                            icon: const Icon(Icons.close, color: Colors.red),
                            onPressed: () async {
                              await api.post("/teams/reject_join", {
                                "request_id": req.id,
                              });
                            },
                          ),
                        ],
                      ),
                    );
                  },
                );
              },
            ),

            const Divider(),

            // LIVE MAP
            Padding(
              padding: const EdgeInsets.all(16),
              child: const Text(
                "Live Map (Leader + On-Duty Responders + Members)",
                style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
              ),
            ),

            SizedBox(
              height: 350,
              child: StreamBuilder(
                stream: FirebaseFirestore.instance
                    .collection("users")
                    .where("team_id", isEqualTo: widget.teamId)
                    .snapshots(),
                builder: (context, snapshot) {
                  if (!snapshot.hasData || leaderIcon == null) {
                    return const Center(child: CircularProgressIndicator());
                  }

                  final users = snapshot.data!.docs;

                  Set<Marker> markers = {};
                  List<LatLng> onDutyLocations = [];
                  LatLng? leaderLocation;

                  for (var doc in users) {
                    final data = doc.data();
                    final loc = data["location"];
                    if (loc == null) continue;

                    final pos = LatLng(loc["lat"], loc["lng"]);

                    final bool isLeader = doc.id == widget.leaderUid;
                    final bool isResponder = data["role"] == "responder";
                    final bool isOnDuty = data["on_duty"] == true;

                    // Leader ALWAYS visible
                    if (isLeader) {
                      leaderLocation = pos;

                      markers.add(
                        Marker(
                          markerId: MarkerId(doc.id),
                          position: pos,
                          icon: leaderIcon!,
                          infoWindow: const InfoWindow(title: "Team Leader"),
                          onTap: () {
                            setState(() => trackingUid = doc.id);
                            _animateTo(pos);
                          },
                        ),
                      );
                      continue;
                    }

                    // Responders: ONLY show if on duty
                    if (isResponder && !isOnDuty) {
                      continue; // SKIP off-duty responders
                    }

                    // On-duty responders
                    if (isResponder && isOnDuty) {
                      onDutyLocations.add(pos);

                      markers.add(
                        Marker(
                          markerId: MarkerId(doc.id),
                          position: pos,
                          icon: responderIcon!,
                          infoWindow: InfoWindow(
                            title: data["displayName"] ?? "Responder",
                          ),
                          onTap: () {
                            setState(() => trackingUid = doc.id);
                            _animateTo(pos);
                          },
                        ),
                      );
                      continue;
                    }

                    // Team members (non-responders)
                    markers.add(
                      Marker(
                        markerId: MarkerId(doc.id),
                        position: pos,
                        icon: memberIcon!,
                        infoWindow: InfoWindow(
                          title: data["displayName"] ?? "Team Member",
                        ),
                        onTap: () {
                          setState(() => trackingUid = doc.id);
                          _animateTo(pos);
                        },
                      ),
                    );
                  }

                  // AUTO CENTER
                  LatLng center;

                  if (trackingUid != null) {
                    // Follow selected responder
                    final doc = users.firstWhere((d) => d.id == trackingUid);
                    final loc = (doc.data())["location"];
                    center = LatLng(loc["lat"], loc["lng"]);
                  } else if (onDutyLocations.isNotEmpty) {
                    center = _averageCenter(onDutyLocations);
                  } else if (leaderLocation != null) {
                    center = leaderLocation;
                  } else {
                    center = const LatLng(40.6401, 22.9444);
                  }

                  WidgetsBinding.instance.addPostFrameCallback((_) {
                    if (markers.isNotEmpty) {
                      _fitBounds(markers);
                    }
                  });

                  return GoogleMap(
                    onMapCreated: (c) => mapController = c,
                    initialCameraPosition: CameraPosition(
                      target: center,
                      zoom: 13,
                    ),
                    markers: markers,
                  );
                },
              ),
            ),

            const SizedBox(height: 40),

            Center(
              child: ElevatedButton(
                onPressed: () {
                  showDialog(
                    context: context,
                    builder: (_) => AddTeamMemberDialog(teamId: widget.teamId),
                  );
                },
                child: const Text("Add Team Member"),
              ),
            ),

            const SizedBox(height: 40),
          ],
        ),
      ),
    );
  }
}
