from flask import Flask, jsonify, request, send_file
import sqlite3, random, string, os

app = Flask(__name__)
DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'splittrack.db')

def get_conn():
    c = sqlite3.connect(DB)
    c.row_factory = sqlite3.Row
    c.execute('PRAGMA foreign_keys = ON')
    c.execute('PRAGMA journal_mode = WAL')
    return c

def init_db():
    with get_conn() as c:
        c.executescript('''
            CREATE TABLE IF NOT EXISTS groups (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                icon TEXT DEFAULT '📦',
                currency TEXT DEFAULT '₹',
                code TEXT UNIQUE NOT NULL
            );
            CREATE TABLE IF NOT EXISTS members (
                group_id TEXT NOT NULL,
                name TEXT NOT NULL,
                PRIMARY KEY (group_id, name),
                FOREIGN KEY (group_id) REFERENCES groups(id) ON DELETE CASCADE
            );
            CREATE TABLE IF NOT EXISTS expenses (
                id TEXT PRIMARY KEY,
                group_id TEXT NOT NULL,
                description TEXT NOT NULL,
                amount REAL NOT NULL,
                date TEXT NOT NULL,
                category TEXT DEFAULT '📦',
                paid_by TEXT NOT NULL,
                notes TEXT DEFAULT '',
                FOREIGN KEY (group_id) REFERENCES groups(id) ON DELETE CASCADE
            );
            CREATE TABLE IF NOT EXISTS splits (
                expense_id TEXT NOT NULL,
                member TEXT NOT NULL,
                amount REAL NOT NULL,
                PRIMARY KEY (expense_id, member),
                FOREIGN KEY (expense_id) REFERENCES expenses(id) ON DELETE CASCADE
            );
            CREATE TABLE IF NOT EXISTS settlements (
                id TEXT PRIMARY KEY,
                group_id TEXT NOT NULL,
                from_member TEXT NOT NULL,
                to_member TEXT NOT NULL,
                amount REAL NOT NULL,
                date TEXT NOT NULL,
                FOREIGN KEY (group_id) REFERENCES groups(id) ON DELETE CASCADE
            );
        ''')

def uid():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))

def gen_code():
    return ''.join(random.choices('ABCDEFGHJKLMNPQRSTUVWXYZ23456789', k=6))

# ── Frontend ────────────────────────────────────────────────────

@app.route('/')
def index():
    return send_file('contributions.html')

# ── Groups ──────────────────────────────────────────────────────

@app.route('/api/groups', methods=['GET'])
def list_groups():
    with get_conn() as c:
        rows = c.execute('SELECT * FROM groups ORDER BY rowid').fetchall()
        out = []
        for g in rows:
            members = [r['name'] for r in c.execute(
                'SELECT name FROM members WHERE group_id=? ORDER BY rowid', (g['id'],))]
            out.append({**dict(g), 'members': members})
        return jsonify(out)

@app.route('/api/groups', methods=['POST'])
def create_group():
    d = request.json or {}
    name = (d.get('name') or '').strip()
    if not name:
        return jsonify({'error': 'Name required'}), 400
    gid, code = uid(), gen_code()
    with get_conn() as c:
        c.execute('INSERT INTO groups VALUES (?,?,?,?,?)',
                  (gid, name, d.get('icon', '📦'), d.get('currency', '₹'), code))
        for m in d.get('members', []):
            if m.strip():
                c.execute('INSERT OR IGNORE INTO members VALUES (?,?)', (gid, m.strip()))
    return jsonify({'id': gid, 'code': code}), 201

@app.route('/api/groups/<gid>', methods=['DELETE'])
def delete_group(gid):
    with get_conn() as c:
        c.execute('DELETE FROM groups WHERE id=?', (gid,))
    return jsonify({'ok': True})

@app.route('/api/groups/join/<code>')
def join_by_code(code):
    with get_conn() as c:
        row = c.execute('SELECT id FROM groups WHERE code=?', (code.upper(),)).fetchone()
        if not row:
            return jsonify({'error': 'Invalid invite code'}), 404
        return jsonify({'id': row['id']})

# ── Members ─────────────────────────────────────────────────────

@app.route('/api/groups/<gid>/members', methods=['POST'])
def add_member(gid):
    name = ((request.json or {}).get('name') or '').strip()
    if not name:
        return jsonify({'error': 'Name required'}), 400
    with get_conn() as c:
        c.execute('INSERT OR IGNORE INTO members VALUES (?,?)', (gid, name))
    return jsonify({'ok': True})

@app.route('/api/groups/<gid>/members/<name>', methods=['DELETE'])
def remove_member(gid, name):
    with get_conn() as c:
        c.execute('DELETE FROM members WHERE group_id=? AND name=?', (gid, name))
    return jsonify({'ok': True})

# ── Expenses ────────────────────────────────────────────────────

@app.route('/api/groups/<gid>/expenses', methods=['GET'])
def list_expenses(gid):
    with get_conn() as c:
        rows = c.execute(
            'SELECT * FROM expenses WHERE group_id=? ORDER BY date DESC, rowid DESC', (gid,)).fetchall()
        out = []
        for e in rows:
            splits = {r['member']: r['amount'] for r in
                      c.execute('SELECT * FROM splits WHERE expense_id=?', (e['id'],))}
            out.append({**dict(e), 'splits': splits})
        return jsonify(out)

@app.route('/api/groups/<gid>/expenses', methods=['POST'])
def add_expense(gid):
    d = request.json or {}
    eid = uid()
    with get_conn() as c:
        c.execute('INSERT INTO expenses VALUES (?,?,?,?,?,?,?,?)',
                  (eid, gid, d['description'], float(d['amount']), d['date'],
                   d.get('category', '📦'), d['paid_by'], d.get('notes', '')))
        for m, amt in (d.get('splits') or {}).items():
            c.execute('INSERT INTO splits VALUES (?,?,?)', (eid, m, float(amt)))
    return jsonify({'id': eid}), 201

@app.route('/api/groups/<gid>/expenses/<eid>', methods=['PUT'])
def update_expense(gid, eid):
    d = request.json or {}
    with get_conn() as c:
        c.execute(
            'UPDATE expenses SET description=?,amount=?,date=?,category=?,paid_by=?,notes=? WHERE id=? AND group_id=?',
            (d['description'], float(d['amount']), d['date'], d.get('category', '📦'),
             d['paid_by'], d.get('notes', ''), eid, gid))
        c.execute('DELETE FROM splits WHERE expense_id=?', (eid,))
        for m, amt in (d.get('splits') or {}).items():
            c.execute('INSERT INTO splits VALUES (?,?,?)', (eid, m, float(amt)))
    return jsonify({'ok': True})

@app.route('/api/groups/<gid>/expenses/<eid>', methods=['DELETE'])
def delete_expense(gid, eid):
    with get_conn() as c:
        c.execute('DELETE FROM expenses WHERE id=? AND group_id=?', (eid, gid))
    return jsonify({'ok': True})

# ── Settlements ─────────────────────────────────────────────────

@app.route('/api/groups/<gid>/settlements', methods=['GET'])
def list_settlements(gid):
    with get_conn() as c:
        return jsonify([dict(r) for r in
                        c.execute('SELECT * FROM settlements WHERE group_id=? ORDER BY rowid', (gid,))])

@app.route('/api/groups/<gid>/settlements', methods=['POST'])
def add_settlement(gid):
    d = request.json or {}
    sid = uid()
    with get_conn() as c:
        c.execute('INSERT INTO settlements VALUES (?,?,?,?,?,?)',
                  (sid, gid, d['from'], d['to'], float(d['amount']), d['date']))
    return jsonify({'id': sid}), 201

@app.route('/api/groups/<gid>/settlements/<sid>', methods=['DELETE'])
def delete_settlement(gid, sid):
    with get_conn() as c:
        c.execute('DELETE FROM settlements WHERE id=? AND group_id=?', (sid, gid))
    return jsonify({'ok': True})

# ────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    init_db()
    print('\n  SplitTrack running →  http://0.0.0.0:5000\n')
    app.run(host='0.0.0.0', port=5000, debug=False)
