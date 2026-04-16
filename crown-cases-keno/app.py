import sqlite3
import random
import hashlib
import json
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)
DB_NAME = "crowncases_keno.db"

# ─── PAYOUT TABLES ───
PAYOUTS = {
    "low": {
        1:  {1: 3.96},
        2:  {2: 15.00},
        3:  {2: 1.5,  3: 36.00},
        4:  {2: 1.2,  3: 5.0,   4: 80.00},
        5:  {2: 0.5,  3: 3.0,   4: 12.0,  5: 300.00},
        6:  {3: 1.0,  4: 5.0,   5: 30.0,  6: 500.00},
        7:  {3: 0.5,  4: 3.0,   5: 15.0,  6: 100.0,  7: 700.00},
        8:  {4: 1.5,  5: 10.0,  6: 50.0,  7: 300.0,  8: 800.00},
        9:  {4: 1.0,  5: 5.0,   6: 30.0,  7: 100.0,  8: 500.0,  9: 900.00},
        10: {5: 2.0,  6: 15.0,  7: 80.0,  8: 400.0,  9: 800.0,  10: 1000.00}
    },
    "medium": {
        1:  {1: 3.96},
        2:  {2: 17.00},
        3:  {2: 2.0,  3: 50.00},
        4:  {2: 1.5,  3: 6.0,   4: 120.00},
        5:  {2: 0.5,  3: 4.0,   4: 18.0,  5: 450.00},
        6:  {3: 1.5,  4: 7.0,   5: 50.0,  6: 750.00},
        7:  {3: 0.75, 4: 5.0,   5: 25.0,  6: 150.0,  7: 1000.00},
        8:  {4: 2.0,  5: 15.0,  6: 80.0,  7: 450.0,  8: 1200.00},
        9:  {4: 1.5,  5: 8.0,   6: 50.0,  7: 160.0,  8: 750.0,  9: 1400.00},
        10: {5: 3.0,  6: 25.0,  7: 120.0, 8: 600.0,  9: 1200.0, 10: 2000.00}
    },
    "high": {
        1:  {1: 3.96},
        2:  {2: 22.00},
        3:  {2: 3.0,  3: 80.00},
        4:  {3: 8.0,  4: 240.00},
        5:  {3: 5.0,  4: 30.0,  5: 750.00},
        6:  {4: 10.0, 5: 100.0, 6: 1500.00},
        7:  {4: 7.0,  5: 50.0,  6: 300.0,  7: 2500.00},
        8:  {5: 25.0, 6: 150.0, 7: 800.0,  8: 4000.00},
        9:  {5: 15.0, 6: 80.0,  7: 400.0,  8: 2000.0, 9: 6000.00},
        10: {6: 40.0, 7: 250.0, 8: 1500.0, 9: 5000.0, 10: 10000.00}
    }
}

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS user
                 (id INTEGER PRIMARY KEY, balance REAL)''')
    c.execute('''CREATE TABLE IF NOT EXISTS history
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  bet_amount REAL,
                  picked TEXT,
                  drawn TEXT,
                  hits INTEGER,
                  multiplier REAL,
                  payout REAL,
                  risk TEXT DEFAULT 'low',
                  client_seed TEXT,
                  server_hash TEXT,
                  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    c.execute("SELECT * FROM user WHERE id=1")
    if not c.fetchone():
        c.execute("INSERT INTO user (id, balance) VALUES (1, 1000.00)")
    conn.commit()
    conn.close()

def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    conn = get_db()
    balance = conn.execute("SELECT balance FROM user WHERE id=1").fetchone()['balance']
    conn.close()
    return render_template('index.html', balance=balance)

@app.route('/api/stats')
def stats():
    conn = get_db()
    q = conn.execute("""
        SELECT
            COUNT(*) as total,
            SUM(bet_amount) as wagered,
            SUM(payout) as total_payout,
            SUM(CASE WHEN payout > 0 THEN 1 ELSE 0 END) as wins,
            SUM(CASE WHEN payout = 0 THEN 1 ELSE 0 END) as losses
        FROM history
    """).fetchone()
    bal = conn.execute("SELECT balance FROM user WHERE id=1").fetchone()['balance']
    conn.close()
    wagered     = q['wagered']     or 0.0
    total_payout= q['total_payout']or 0.0
    return jsonify({
        'profit':  total_payout - wagered,
        'wagered': wagered,
        'wins':    q['wins']   or 0,
        'losses':  q['losses'] or 0,
        'balance': bal
    })

@app.route('/api/play', methods=['POST'])
def play():
    data        = request.json
    bet         = float(data.get('bet', 0))
    picked      = data.get('picked', [])
    risk        = data.get('risk', 'low')
    client_seed = data.get('client_seed', 'default')

    if risk not in PAYOUTS:
        risk = 'low'

    conn    = get_db()
    balance = conn.execute("SELECT balance FROM user WHERE id=1").fetchone()['balance']

    if bet <= 0 or bet > balance:
        conn.close()
        return jsonify({'error': 'Invalid bet amount'}), 400
    if len(picked) < 1 or len(picked) > 10:
        conn.close()
        return jsonify({'error': 'Pick 1–10 numbers'}), 400

    # Deduct bet
    new_balance = balance - bet
    conn.execute("UPDATE user SET balance=? WHERE id=1", (new_balance,))

    # Provably fair draw
    server_seed = "CROWNCASES_SECRET_SEED_V2"
    nonce       = conn.execute("SELECT COUNT(*) FROM history").fetchone()[0]
    seed_hash   = hashlib.sha256(f"{server_seed}:{client_seed}:{nonce}".encode()).hexdigest()
    random.seed(int(seed_hash[:16], 16))
    drawn       = random.sample(range(1, 41), 10)
    random.seed()  # reset

    hits_count = len(set(picked) & set(drawn))
    num_picked = len(picked)
    table      = PAYOUTS[risk].get(num_picked, {})
    multiplier = table.get(hits_count, 0.0)
    payout     = round(bet * multiplier, 2)

    if payout > 0:
        new_balance = round(new_balance + payout, 2)
        conn.execute("UPDATE user SET balance=? WHERE id=1", (new_balance,))

    conn.execute(
        "INSERT INTO history (bet_amount,picked,drawn,hits,multiplier,payout,risk,client_seed,server_hash) VALUES (?,?,?,?,?,?,?,?,?)",
        (bet, json.dumps(picked), json.dumps(drawn), hits_count, multiplier, payout, risk, client_seed, seed_hash)
    )
    conn.commit()
    conn.close()

    return jsonify({
        'drawn':        drawn,
        'hits':         hits_count,
        'multiplier':   multiplier,
        'payout':       payout,
        'new_balance':  new_balance,
        'hash':         seed_hash,
        'revealed_seed': f"{server_seed}:{client_seed}:{nonce}"
    })

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)
