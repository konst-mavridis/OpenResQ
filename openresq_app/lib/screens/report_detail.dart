import 'package:flutter/material.dart';
import '../services/api_service.dart';

class ReportDetail extends StatefulWidget {
  final String reportId;
  final String role;
  const ReportDetail({required this.reportId, required this.role, super.key});
  @override State<ReportDetail> createState() => _ReportDetailState();
}

class _ReportDetailState extends State<ReportDetail> {
  final ApiService api = ApiService();
  Map<String, dynamic>? report;
  final TextEditingController _noteCtrl = TextEditingController();
  final TextEditingController _descCtrl = TextEditingController();
  String? _newStatus;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    final r = await api.getReport(widget.reportId);
    setState(() {
      report = r;
      _descCtrl.text = r['description'] ?? '';
    });
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
    try {
      await api.deleteReport(widget.reportId);
      Navigator.pop(context, true);
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Error: $e')));
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
            Text(report!['description'] ?? ''),
            const SizedBox(height: 12),
            Text('Type: ${report!['event_type']}'),
            Text('Severity: ${report!['severity']}'),
            Text('Status: ${report!['status']}'),
            const SizedBox(height: 20),
            if (widget.role == 'responder' || widget.role == 'admin') ...[
              DropdownButtonFormField<String>(
                value: report!['status'],
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
            const Spacer(),
            if (widget.role == 'admin')
              ElevatedButton(onPressed: _adminDelete, style: ElevatedButton.styleFrom(backgroundColor: Colors.red), child: const Text('Delete report')),
          ],
        ),
      ),
    );
  }
}
