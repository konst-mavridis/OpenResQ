import 'package:flutter/material.dart';
import '../services/api_service.dart';
import 'package:firebase_auth/firebase_auth.dart';
import './chat_screen.dart';

class ReportDetail extends StatefulWidget {
  final String reportId;
  final String role;

  const ReportDetail({
    required this.reportId,
    required this.role,
    super.key,
  });

  @override
  State<ReportDetail> createState() => _ReportDetailState();
}

class _ReportDetailState extends State<ReportDetail> {
  final ApiService api = ApiService();
  Map<String, dynamic>? report;
  bool isOwner = false;

  final TextEditingController _noteCtrl = TextEditingController();
  final TextEditingController _descCtrl = TextEditingController();
  String? _newStatus;
  bool get isCitizenOwner => isOwner && widget.role == 'citizen';
  bool get isStaff => widget.role == 'responder' || widget.role == 'admin';


  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    try {
      final r = await api.getReport(widget.reportId);
      final uid = FirebaseAuth.instance.currentUser?.uid;

      setState(() {
        report = r;
        _descCtrl.text = r['description'] ?? '';
        isOwner = uid != null && r['uid'] == uid;
      });
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text("Το report έχει διαγραφεί")),
      );
      Navigator.pop(context);
    }
  }

  Future<void> _submitResponderUpdate() async {
    final patch = <String,dynamic>{};
    if (_newStatus != null) patch['status'] = _newStatus;
    if (_descCtrl.text.trim().isNotEmpty) patch['description'] = _descCtrl.text.trim();
    if (_noteCtrl.text.trim().isNotEmpty) patch['responder_note'] = _noteCtrl.text.trim();
    try {
      await api.responderUpdate(widget.reportId, patch);
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Updated')));
      await _load();
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Error: $e')));
    }
  }

  Future<void> _adminDelete() async {
    bool hardDelete = false;
    bool confirm = false;
    String reason = "";

    await showDialog(
      context: context,
      builder: (ctx) => StatefulBuilder(
        builder: (ctx, setState) {
          return AlertDialog(
            title: const Text("Delete report"),
            content: SingleChildScrollView(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  TextField(
                    decoration: const InputDecoration(
                      labelText: "Reason",
                    ),
                    onChanged: (v) => reason = v,
                  ),

                  const SizedBox(height: 12),

                  // 🔴 HARD DELETE (ADMIN ONLY)
                  SwitchListTile(
                    title: const Text(
                      "Hard delete (irreversible)",
                      style: TextStyle(color: Colors.red),
                    ),
                    value: hardDelete,
                    onChanged: (v) {
                      setState(() {
                        hardDelete = v;
                        if (!v) confirm = false;
                      });
                    },
                  ),

                  if (hardDelete)
                    CheckboxListTile(
                      title: const Text(
                        "I understand this will permanently delete the report",
                        style: TextStyle(color: Colors.red),
                      ),
                      value: confirm,
                      onChanged: (v) =>
                          setState(() => confirm = v ?? false),
                    ),
                ],
              ),
            ),
            actions: [
              TextButton(
                onPressed: () => Navigator.pop(ctx),
                child: const Text("Cancel"),
              ),
              ElevatedButton(
                style: ElevatedButton.styleFrom(
                  backgroundColor: hardDelete ? Colors.red : null,
                ),
                onPressed: hardDelete && !confirm
                    ? null
                    : () async {
                        try {
                          await api.deleteReport(
                            widget.reportId,
                            reason: reason.trim().isEmpty
                                ? "No reason provided"
                                : reason.trim(),
                            hard: hardDelete,
                            confirm: confirm,
                          );

                          Navigator.pop(ctx);
                          Navigator.pop(context, true);
                        } catch (e) {
                          Navigator.pop(ctx);
                          ScaffoldMessenger.of(context).showSnackBar(
                            SnackBar(content: Text("Error: $e")),
                          );
                        }
                      },
                child: Text(hardDelete ? "Hard delete" : "Delete"),
              ),
            ],
          );
        },
      ),
    );
  }

  Future<void> _deleteOwnReport() async {
    final confirm = await showDialog<bool>(
      context: context,
      builder: (_) => AlertDialog(
        title: const Text('Διαγραφή report'),
        content: const Text(
          'Θέλεις σίγουρα να διαγράψεις οριστικά το report σου;',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: const Text('Άκυρο'),
          ),
          ElevatedButton(
            style: ElevatedButton.styleFrom(backgroundColor: Colors.red),
            onPressed: () => Navigator.pop(context, true),
            child: const Text('Διαγραφή'),
          ),
        ],
      ),
    );

    if (confirm != true) return;

    try {
      await api.deleteOwnReport(widget.reportId, "Deleted by owner"); // 🔥 backend call
      if (!mounted) return;

      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Το report διαγράφηκε')),
      );
      Navigator.pop(context);
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Αποτυχία διαγραφής')),
      );
    }
  }


  @override
  Widget build(BuildContext context) {
    if (report == null) return const Scaffold(body: Center(child: CircularProgressIndicator()));
    

    return Scaffold(
      appBar: AppBar(title: Text(report!['title'] ?? 'Report')),
      body: Padding(
        padding: const EdgeInsets.all(12.0),
        child: Column(
          children: [
            // DESCRIPTION
            if (isCitizenOwner)
              TextField(
                controller: _descCtrl,
                maxLines: 4,
                decoration: const InputDecoration(
                  labelText: 'Περιγραφή',
                  border: OutlineInputBorder(),
                ),
              )
            else
              Text(report!['description'] ?? ''),
            const SizedBox(height: 12),

            // EVENT TYPE
            if (isCitizenOwner)
              DropdownButtonFormField<String>(
                initialValue: report!['event_type'],
                decoration: const InputDecoration(
                  labelText: 'Τύπος συμβάντος',
                ),
                items: const [
                  DropdownMenuItem(value: 'fire', child: Text('Fire')),
                  DropdownMenuItem(value: 'flood', child: Text('Flood')),
                  DropdownMenuItem(value: 'earthquake', child: Text('Earthquake')),
                  DropdownMenuItem(value: 'other', child: Text('Other')),
                ],
                onChanged: (v) {
                  setState(() {
                    report!['event_type'] = v;
                  });
                },
              )
            else
              Text('Type: ${report!['event_type']}'),
            const SizedBox(height: 12),
            // SEVERITY
            if (isCitizenOwner)
              DropdownButtonFormField<String>(
                value: report!['severity'],
                decoration: const InputDecoration(
                  labelText: 'Severity',
                ),
                items: const [
                  DropdownMenuItem(value: 'low', child: Text('Low')),
                  DropdownMenuItem(value: 'medium', child: Text('Medium')),
                  DropdownMenuItem(value: 'high', child: Text('High')),
                ],
                onChanged: (v) {
                  setState(() {
                    report!['severity'] = v;
                  });
                },
              )
            else
              Text('Severity: ${report!['severity']}'),
            Text('Status: ${report!['status']}'),
            const SizedBox(height: 20),
            if (widget.role == 'responder' || widget.role == 'admin') ...[
              DropdownButtonFormField<String>(
                initialValue: report!['status'],
                items: const [
                  DropdownMenuItem(value: 'pending', child: Text('pending')),
                  DropdownMenuItem(value: 'investigating', child: Text('investigating')),
                  DropdownMenuItem(value: 'resolved', child: Text('resolved')),
                ],
                onChanged: (v) => setState(()=> _newStatus = v),
                decoration: const InputDecoration(labelText: 'Change status'),
              ),
              const SizedBox(height: 10),
              TextField(controller: _descCtrl, maxLines: 3, decoration: const InputDecoration(labelText: 'Description')),
              const SizedBox(height: 8),
              TextField(controller: _noteCtrl, decoration: const InputDecoration(labelText: 'Responder note')),
              const SizedBox(height: 10),
              ElevatedButton(onPressed: _submitResponderUpdate, child: const Text('Save changes'))
            ],
            
            if (isCitizenOwner)
              ElevatedButton.icon(
                icon: const Icon(Icons.save),
                label: const Text('Update report'),
                onPressed: () async {
                  await api.editOwnReport(widget.reportId, {
                    "description": _descCtrl.text.trim(),
                    "event_type": report!['event_type'],
                    "severity": report!['severity'],
                  });

                  setState(() {
                    report!['description'] = _descCtrl.text.trim();
                  });

                    ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(content: Text('The report got updated')),
                    );
                    Navigator.pop(context);
                },
              ),
              if (isCitizenOwner)
                ElevatedButton.icon(
                  icon: const Icon(Icons.delete),
                  label: const Text('Delete my report'),
                  style: ElevatedButton.styleFrom(backgroundColor: Colors.red),
                  onPressed: _deleteOwnReport,
                ),

        if (widget.role == 'admin')
          ElevatedButton(
            onPressed: _adminDelete,
            style: ElevatedButton.styleFrom(backgroundColor: Colors.red),
            child: const Text('Admin delete'),
          ),

          ElevatedButton.icon(
            icon: const Icon(Icons.chat),
            label: const Text("Live chat"),
            onPressed: () {
              Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (_) => ChatScreen(
                    reportId: widget.reportId,
                    role: widget.role,
                  ),
                ),
              );
            },
          ),

          ],
        ),
      ),
    );
  }
}
