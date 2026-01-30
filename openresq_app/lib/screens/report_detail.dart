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

  int upvotes = 0;
  int downvotes = 0;

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
        upvotes = r['votes_up'] ?? 0;
        downvotes = r['votes_down'] ?? 0;
      });
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text("Το report έχει διαγραφεί")),
      );
      Navigator.pop(context);
    }
  }

  Future<void> _vote(int vote) async {
    try {
      await api.vote(widget.reportId, vote);
      setState(() {
        if (vote > 0) upvotes += 1;
        if (vote < 0) downvotes += 1;
      });
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(vote > 0 ? 'Voted YES' : 'Voted NO')),
      );
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error voting: $e')),
      );
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



  Future<void> adminDelete() async {
    try {
      await api.deleteReport(widget.reportId, reason: "Deleted by admin", hard: true, confirm: true);
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Report deleted')));
      Navigator.pop(context);
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Error: $e')));
    }
  }

  Future<void> deleteOwnReport() async {
    try {
      await api.deleteReport(widget.reportId, reason: "Deleted by owner", hard: true, confirm: true);
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Your report has been deleted')));
      Navigator.pop(context);
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Error: $e')));
    }
  }

  @override
  Widget build(BuildContext context) {
    if (report == null) return const Scaffold(body: Center(child: CircularProgressIndicator()));

    final theme = Theme.of(context);
    final status = report!['status'] ?? 'pending';

    return Scaffold(
      body: CustomScrollView(
        slivers: [
          // HEADER IMAGE
          SliverAppBar(
            expandedHeight: 220,
            pinned: true,
            flexibleSpace: FlexibleSpaceBar(
              title: Text(report!['title'] ?? 'Report'),
              background: Stack(
                fit: StackFit.expand,
                children: [
                  if (report!['media'] != null && report!['media'].isNotEmpty)
                    Image.network(
                      report!['media'][0]['url'],
                      fit: BoxFit.cover,
                    )
                  else
                    Container(color: theme.colorScheme.primaryContainer),
                  Container(
                    decoration: const BoxDecoration(
                      gradient: LinearGradient(
                        begin: Alignment.bottomCenter,
                        end: Alignment.topCenter,
                        colors: [Colors.black54, Colors.transparent],
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ),

          SliverPadding(
            padding: const EdgeInsets.all(12),
            sliver: SliverList(
              delegate: SliverChildListDelegate([
                // INFO CARDS
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    _infoCard(Icons.fireplace, 'Type', report!['event_type']),
                    _infoCard(Icons.warning_amber_rounded, 'Severity', report!['severity']),
                    _infoCard(Icons.flash_on, 'AI Score', (report!['ai_score'] ?? 'N/A').toString()),
                  ],
                ),
                const SizedBox(height: 12),

                // STATUS CHIP
                Align(
                  alignment: Alignment.centerRight,
                  child: Chip(
                    label: Text(status.toUpperCase(), style: const TextStyle(color: Colors.white)),
                    backgroundColor: status == 'rejected'
                        ? Colors.red
                        : status == 'approved'
                            ? Colors.green
                            : Colors.orange,
                  ),
                ),
                const SizedBox(height: 12),

                // DESCRIPTION
                Card(
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                  child: Padding(
                    padding: const EdgeInsets.all(12),
                    child: isCitizenOwner
                        ? TextField(
                            controller: _descCtrl,
                            maxLines: 4,
                            decoration: InputDecoration(
                              labelText: 'Description',
                              prefixIcon: const Icon(Icons.description),
                              border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
                            ),
                          )
                        : Text(report!['description'] ?? ''),
                  ),
                ),
                const SizedBox(height: 12),

                // VOTING SECTION
                Card(
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                  color: theme.colorScheme.surfaceContainerHighest,
                  child: Padding(
                    padding: const EdgeInsets.all(12),
                    child: Column(
                      children: [
                        const Text("Does this report reflect reality?", style: TextStyle(fontWeight: FontWeight.bold)),
                        const SizedBox(height: 8),
                        Row(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            Column(
                              children: [
                                IconButton(
                                  icon: const Icon(Icons.thumb_up, color: Colors.green),
                                  onPressed: () => _vote(1),
                                ),
                                Text(upvotes.toString()),
                              ],
                            ),
                            const SizedBox(width: 40),
                            Column(
                              children: [
                                IconButton(
                                  icon: const Icon(Icons.thumb_down, color: Colors.red),
                                  onPressed: () => _vote(-1),
                                ),
                                Text(downvotes.toString()),
                              ],
                            ),
                          ],
                        ),
                      ],
                    ),
                  ),
                ),
                const SizedBox(height: 12),

                // STAFF ACTIONS
                if (isStaff)
                  Card(
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                    color: theme.colorScheme.primaryContainer.withValues(alpha: 0.1),
                    child: Padding(
                      padding: const EdgeInsets.all(12),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          const Text('Responder Actions', style: TextStyle(fontWeight: FontWeight.bold)),
                          const SizedBox(height: 8),
                          DropdownButtonFormField<String>(
                            initialValue: report!['status'],
                            decoration: InputDecoration(
                              labelText: 'Status',
                              prefixIcon: const Icon(Icons.change_circle),
                              border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
                            ),
                            items: const [
                              DropdownMenuItem(value: 'pending', child: Text('Pending')),
                              DropdownMenuItem(value: 'investigating', child: Text('Investigating')),
                              DropdownMenuItem(value: 'resolved', child: Text('Resolved')),
                              DropdownMenuItem(value: 'rejected', child: Text('Rejected')),
                            ],
                            onChanged: (v) => setState(() => _newStatus = v),
                          ),
                          const SizedBox(height: 8),
                          TextField(
                            controller: _noteCtrl,
                            decoration: InputDecoration(
                              labelText: 'Responder Note',
                              prefixIcon: const Icon(Icons.note_alt),
                              border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
                            ),
                          ),
                          const SizedBox(height: 12),
                          FilledButton(
                            onPressed: _submitResponderUpdate,
                            child: const Text('Save Changes'),
                          ),
                        ],
                      ),
                    ),
                  ),

                const SizedBox(height: 12),

                // OWNER ACTIONS
                if (isCitizenOwner)
                  Card(
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                    child: Padding(
                      padding: const EdgeInsets.all(12),
                      child: Row(
                        mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                        children: [
                          FilledButton.icon(
                            onPressed: () async {
                              await api.editOwnReport(widget.reportId, {
                                "description": _descCtrl.text.trim(),
                                "event_type": report!['event_type'],
                                "severity": report!['severity'],
                              });
                              await _load();
                            },
                            icon: const Icon(Icons.save),
                            label: const Text('Update'),
                          ),
                          OutlinedButton.icon(
                            onPressed: deleteOwnReport,
                            icon: const Icon(Icons.delete),
                            label: const Text('Delete'),
                            style: OutlinedButton.styleFrom(foregroundColor: Colors.red),
                          ),
                        ],
                      ),
                    ),
                  ),

                const SizedBox(height: 12),

                // ADMIN DELETE
                if (widget.role == 'admin')
                  ElevatedButton(
                    onPressed: adminDelete,
                    style: ElevatedButton.styleFrom(backgroundColor: Colors.red),
                    child: const Text('Admin delete'),
                  ),

                const SizedBox(height: 12),

                // CHAT BUTTON
                FilledButton.icon(
                  onPressed: () {
                    Navigator.push(
                      context,
                      MaterialPageRoute(
                        builder: (context) => ChatScreen(reportId: widget.reportId, role: widget.role),
                      ),
                    );
                  },
                  icon: const Icon(Icons.chat),
                  label: const Text("Live Chat"),
                ),

                const SizedBox(height: 40),
              ]),
            ),
          ),
        ],
      ),
    );
  }

  Widget _infoCard(IconData icon, String label, String value) {
    return Expanded(
      child: Card(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
        color: Theme.of(context).colorScheme.surfaceVariant,
        child: Padding(
          padding: const EdgeInsets.all(12),
          child: Column(
            children: [
              Icon(icon, size: 28),
              const SizedBox(height: 4),
              Text(label, style: const TextStyle(fontWeight: FontWeight.bold)),
              const SizedBox(height: 4),
              Text(value),
            ],
          ),
        ),
      ),
    );
  }
}
