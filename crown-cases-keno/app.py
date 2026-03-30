import sqlite3
import random
import hashlib
import json
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)
DB_NAME = "crowncases_keno.db"

# --- CONFIGURATION ---
PICK_PAYOUTS = {
    1: { 1: 3.96 },
    2: { 2: 15.00 },
    3: { 2: 1.5, 3: 36.00 },
    4: { 2: 1.2, 3: 5.0, 4: 80.00 },
    5: { 2: 0.5, 3: 3.0, 4: 12.0, 5: 300.00 },
    6: { 3: 1.0, 4: 5.0, 5: 30.0, 6: 500.00 },
    7: { 3: 0.5, 4: 3.0, 5: 15.0, 6: 100.0, 7: 700.00 },
    8: { 4: 1.5, 5: 10.0, 6: 50.0, 7: 300.0, 8: 800.00 },
    9: { 4: 1.0, 5: 5.0, 6: 30.0, 7: 100.0, 8: 500.0, 9: 900.00 },
    10: { 5: 2.0, 6: 15.0, 7: 80.0, 8: 400.0, 9: 800.0, 10: 1000.00 }
}

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS user (id INTEGER PRIMARY KEY, balance REAL)''')
    c.execute('''CREATE TABLE IF NOT EXISTS history
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  bet_amount REAL,
                  picked TEXT,
                  drawn TEXT,
                  hits INTEGER,
                  multiplier REAL,
                  payout REAL,
                  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    c.execute("SELECT * FROM user WHERE id=1")
    if not c.fetchone():
        c.execute("INSERT INTO user (id, balance) VALUES (1, 1000.00)")
    conn.commit()
    conn.close()

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    conn = get_db_connection()
    balance = conn.execute("SELECT balance FROM user WHERE id=1").fetchone()['balance']
    conn.close()
    return render_template('index.html', balance=balance)

@app.route('/api/stats')
def stats():
    conn = get_db_connection()
    stats_query = conn.execute("""
        SELECT
            COUNT(*) as total_games,
            SUM(bet_amount) as total_wagered,
            SUM(payout) as total_payout,
            SUM(CASE WHEN payout > 0 THEN 1 ELSE 0 END) as wins,
            SUM(CASE WHEN payout = 0 THEN 1 ELSE 0 END) as losses
        FROM history
    """).fetchone()
    conn.close()
    total_wagered = stats_query['total_wagered'] or 0.0
    total_payout = stats_query['total_payout'] or 0.0
    profit = total_payout - total_wagered
    return jsonify({
        'profit': profit,
        'wagered': total_wagered,
        'wins': stats_query['wins'] or 0,
        'losses': stats_query['losses'] or 0
    })

@app.route('/api/play', methods=['POST'])
def play():
    data = request.json
    bet = float(data.get('bet', 0))
    picked = data.get('picked', [])
    conn = get_db_connection()
    balance = conn.execute("SELECT balance FROM user WHERE id=1").fetchone()['balance']
    if bet <= 0 or bet > balance:
        conn.close()
        return jsonify({'error': 'Invalid bet amount'}), 400
    if len(picked) < 1 or len(picked) > 10:
        conn.close()
        return jsonify({'error': 'Invalid selection count'}), 400
    new_balance = balance - bet
    conn.execute("UPDATE user SET balance = ? WHERE id=1", (new_balance,))
    drawn = random.sample(range(1, 41), 10)
    hits_count = len(set(picked) & set(drawn))
    num_picked = len(picked)
    table = PICK_PAYOUTS.get(num_picked, {})
    multiplier = table.get(hits_count, 0.0)
    payout = bet * multiplier
    if payout > 0:
        new_balance += payout
        conn.execute("UPDATE user SET balance = ? WHERE id=1", (new_balance,))
    conn.execute("INSERT INTO history (bet_amount, picked, drawn, hits, multiplier, payout) VALUES (?, ?, ?, ?, ?, ?)",
              (bet, json.dumps(picked), json.dumps(drawn), hits_count, multiplier, payout))
    conn.commit()
    conn.close()
    server_seed = "CROWNCASES_SECRET_KEY_999"
    result_str = f"{server_seed}-{drawn}"
    pf_hash = hashlib.sha256(result_str.encode()).hexdigest()
    return jsonify({
        'drawn': drawn,
        'hits': hits_count,
        'multiplier': multiplier,
        'payout': payout,
        'new_balance': new_balance,
        'hash': pf_hash
    })

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)
