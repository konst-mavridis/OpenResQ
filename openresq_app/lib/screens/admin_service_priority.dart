import 'package:flutter/material.dart';
import 'package:flutter/cupertino.dart';
import '../services/api_service.dart';

class AdminServicePriorityScreen extends StatefulWidget {
  final String serviceId;
  final String serviceName;

  const AdminServicePriorityScreen({
    super.key,
    required this.serviceId,
    required this.serviceName,
  });

  @override
  State<AdminServicePriorityScreen> createState() =>
      _AdminServicePriorityScreenState();
}

class _AdminServicePriorityScreenState
    extends State<AdminServicePriorityScreen> {
  final api = ApiService();

  List<String> eventTypes = [
    "fire",
    "flood",
    "accident",
    "hazard",
    "medical",
    "smoke",
  ];

  bool loading = true;
  bool saving = false;

  @override
  void initState() {
    super.initState();
    _loadPriorities();
  }

  Future<void> _loadPriorities() async {
    try {
      final res = await api.get(
        "/admin/dispatch/service-priority/get",
        params: {"service_id": widget.serviceId},
      );

      final priorities = Map<String, dynamic>.from(res["priorities"]);

      eventTypes.sort((a, b) {
        final pa = priorities[a] ?? 999;
        final pb = priorities[b] ?? 999;
        return pa.compareTo(pb);
      });
    } catch (_) {
      // ignore if no config exists yet
    }

    setState(() => loading = false);
  }

  Future<void> _save() async {
    setState(() => saving = true);

    final body = {
      "service_id": widget.serviceId,
      "priorities": {
        for (int i = 0; i < eventTypes.length; i++) eventTypes[i]: i + 1
      }
    };

    await api.post("/admin/dispatch/service-priority/set", body);

    setState(() => saving = false);

    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text("Saved successfully")),
    );
  }

  Future<void> _aiSuggest() async {
    final res = await api.get(
      "/admin/dispatch/service-priority/ai_suggest",
      params: {"service_name": widget.serviceName},
    );

    final priorities = Map<String, dynamic>.from(res["priorities"]);

    setState(() {
      eventTypes.sort((a, b) {
        final pa = priorities[a] ?? 999;
        final pb = priorities[b] ?? 999;
        return pa.compareTo(pb);
      });
    });
  }

  // 🔥 Slide Picker Logic
  Future<void> _changePriority(String type, int currentIndex) async {
    final newIndex = await showModalBottomSheet<int>(
      context: context,
      builder: (_) {
        return Container(
          height: 250,
          padding: const EdgeInsets.all(16),
          child: Column(
            children: [
              const Text(
                "Select new priority",
                style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
              ),
              Expanded(
                child: CupertinoPicker(
                  scrollController: FixedExtentScrollController(
                    initialItem: currentIndex,
                  ),
                  itemExtent: 40,
                  onSelectedItemChanged: (value) {
                    Navigator.pop(context, value);
                  },
                  children: List.generate(
                    eventTypes.length,
                    (i) => Center(child: Text("Position ${i + 1}")),
                  ),
                ),
              ),
            ],
          ),
        );
      },
    );

    if (newIndex == null || newIndex == currentIndex) return;

    setState(() {
      eventTypes.remove(type);
      eventTypes.insert(newIndex, type);
    });
  }

  @override
  Widget build(BuildContext context) {
    if (loading) {
      return const Scaffold(
        body: Center(child: CircularProgressIndicator()),
      );
    }

    return Scaffold(
      appBar: AppBar(
        title: Text("Priorities for ${widget.serviceName}"),
        actions: [
          IconButton(
            icon: const Icon(Icons.auto_fix_high),
            onPressed: _aiSuggest,
            tooltip: "AI Suggest",
          ),
          IconButton(
            icon: const Icon(Icons.save),
            onPressed: saving ? null : _save,
          ),
        ],
      ),

      // 🔥 NO REORDERABLE LIST — ONLY TAP + SLIDE PICKER
      body: ListView.builder(
        itemCount: eventTypes.length,
        itemBuilder: (context, index) {
          final type = eventTypes[index];

          return ListTile(
            title: Text(type.toUpperCase()),
            subtitle: Text("Priority: ${index + 1}"),
            trailing: const Icon(Icons.chevron_right),
            onTap: () => _changePriority(type, index),
          );
        },
      ),
    );
  }
}
