import 'package:flutter/material.dart';
import '../services/api_service.dart';

class LogsPage extends StatefulWidget {
  const LogsPage({super.key});

  @override
  State<LogsPage> createState() => _LogsPageState();
}

class _LogsPageState extends State<LogsPage> {
  final ApiService api = ApiService();
  List<Map<String, dynamic>> logs = [];
  bool loading = true;

  @override
  void initState() {
    super.initState();
    _loadLogs();
  }

  Future<void> _loadLogs() async {
    try {
      final l = await api.getLogs();
      setState(() {
        logs = List<Map<String, dynamic>>.from(l);
        loading = false;
      });
    } catch (e) {
      setState(() => loading = false);
      ScaffoldMessenger.of(context)
          .showSnackBar(SnackBar(content: Text("Error loading logs: $e")));
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text("System Logs"),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _loadLogs,
          )
        ],
      ),
      body: loading
          ? const Center(child: CircularProgressIndicator())
          : RefreshIndicator(
              onRefresh: _loadLogs,
              child: ListView.builder(
                itemCount: logs.length,
                itemBuilder: (context, index) {
                  final log = logs[index];

                  return Card(
                    margin: const EdgeInsets.symmetric(
                        horizontal: 12, vertical: 6),
                    child: ListTile(
                      leading: Icon(
                        log['status'] == 'success'
                            ? Icons.check_circle
                            : Icons.error,
                        color: log['status'] == 'success'
                            ? Colors.green
                            : Colors.red,
                      ),
                      title: Text(
                        "${log['action']} • ${log['status']}",
                        style: const TextStyle(fontWeight: FontWeight.bold),
                      ),
                      subtitle: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          if (log['user_id'] != null)
                            Text("User: ${log['user_id']}"),
                          if (log['resource_id'] != null)
                            Text("Resource: ${log['resource_id']}"),
                          if (log['role'] != null)
                            Text("Role: ${log['role']}"),
                          if (log['delete_type'] != null)
                            Text("Delete type: ${log['delete_type']}"),
                          if (log['reason'] != null)
                            Text("Reason: ${log['reason']}"),
                          if (log['timestamp'] != null)
                            Text(
                              "At: ${log['timestamp']}",
                              style: const TextStyle(fontSize: 12),
                            ),
                        ],
                      ),
                      isThreeLine: true,
                    ),
                  );
                },
              ),
            ),
    );
  }
}
