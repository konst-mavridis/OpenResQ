import 'package:flutter/material.dart';
import 'package:latlong2/latlong.dart';
import '../../services/api_service.dart';

class AddResponderDialog extends StatefulWidget {
  final LatLng? adminLocation;

  const AddResponderDialog({super.key, required this.adminLocation});

  @override
  State<AddResponderDialog> createState() => _AddResponderDialogState();
}

class _AddResponderDialogState extends State<AddResponderDialog> {
  final api = ApiService();
  List<dynamic> citizens = [];
  bool loading = true;
  String email = "";

  @override
  void initState() {
    super.initState();
    loadNearby();
  }

  Future<void> loadNearby() async {
    if (widget.adminLocation == null) return;

    final res = await api.fetchNearbyCitizens(
      widget.adminLocation!.latitude,
      widget.adminLocation!.longitude,
    );

    setState(() {
      citizens = res;
      loading = false;
    });
  }

  Future<void> invite() async {
    if (email.isEmpty) return;

    await api.inviteResponder(email);
    Navigator.pop(context);
  }

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: const Text("Add Responder"),
      content: SizedBox(
        width: 400,
        child: loading
            ? const Center(child: CircularProgressIndicator())
            : Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  const Text("Nearby Citizens (25km)"),
                  const SizedBox(height: 10),

                  SizedBox(
                    height: 200,
                    child: ListView(
                      children: citizens.map((c) {
                        return ListTile(
                          title: Text(c["displayName"] ?? c["email"]),
                          subtitle: Text(
                            "${c["distance"].toStringAsFixed(1)} km away",
                          ),
                          trailing: ElevatedButton(
                            onPressed: () async {
                              await api.promoteToResponder(c["uid"]);
                              Navigator.pop(context);
                            },
                            child: const Text("Add"),
                          ),
                        );
                      }).toList(),
                    ),
                  ),

                  const Divider(),
                  const Text("Invite by Email"),

                  TextField(
                    onChanged: (v) => email = v,
                    decoration: const InputDecoration(
                      labelText: "Email",
                    ),
                  ),

                  const SizedBox(height: 10),

                  ElevatedButton(
                    onPressed: invite,
                    child: const Text("Send Invite"),
                  ),
                ],
              ),
      ),
    );
  }
}
