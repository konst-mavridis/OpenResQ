import 'package:sqflite/sqflite.dart';
import 'package:path_provider/path_provider.dart';
import 'package:path/path.dart';
import 'dart:convert';

class LocalQueue {
  static Database? _db;

  Future<Database> get db async {
    if (_db != null) return _db!;
    final documentsDirectory = await getApplicationDocumentsDirectory();
    final path = join(documentsDirectory.path, "openresq_queue.db");
    _db = await openDatabase(path, version: 1, onCreate: (db, v) async {
      await db.execute('''
        CREATE TABLE queue (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          path TEXT,
          method TEXT,
          body TEXT,
          created_at INTEGER
        )
      ''');
    });
    return _db!;
  }

  Future<void> enqueue(Map<String, dynamic> item) async {
    final database = await db;
    await database.insert("queue", {
      "path": item['path'],
      "method": item['method'],
      "body": jsonEncode(item['body'] ?? {}),
      "created_at": DateTime.now().millisecondsSinceEpoch
    });
  }

  Future<List<Map<String, dynamic>>> getAll() async {
    final database = await db;
    final rows = await database.query("queue");
    return rows.map((r) {
      return {
        "id": r['id'],
        "path": r['path'],
        "method": r['method'],
        "body": jsonDecode(r['body'] as String)
      };
    }).toList();
  }

  Future<void> remove(int id) async {
    final database = await db;
    await database.delete("queue", where: "id=?", whereArgs: [id]);
  }
}
