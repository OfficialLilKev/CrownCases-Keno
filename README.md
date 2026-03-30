# 👑 CrownCases Keno

A modern, fast-paced casino-style Keno web application branded for **CrownCases.GG**. Built with **Python (Flask)** and **SQLite**, featuring a sleek gold-and-dark UI, real-time statistics, and immersive sound effects.

![CrownCases Keno Screenshot](https://image2url.com/r2/default/images/1774907358927-33128cbe-1a1a-45d9-baa6-c7d961eb664a.png)

---

## 🎮 Features

* **Classic Mode Gameplay:** Select 1–10 numbers from a grid of 40.
* **Live Dashboard:** Real-time tracking of **Profit**, **Wins**, **Losses**, and **Total Wagered** displayed alongside the game.
* **Immersive Audio:** Custom Web Audio engine for:
    * *Soft click* (number selection)
    * *Mechanical ticks* (drawing numbers / misses)
    * *Crisp dings* (hits / gem reveals)
    * *Victory chime* (winning round)
* **Visual Feedback:**
    * **Green Gems** animate over matched numbers.
    * **Red text** highlights drawn numbers that were missed.
    * Dynamic Payout Bar updates live based on your selection count, with active highlight on result.
* **CrownCases Branding:** Gold gradient accents, dark metallic palette, Barlow Condensed / Rajdhani typography — fully on-brand with CrownCases.GG.
* **Persistent Database:** Auto-creates a local SQLite database (`crowncases_keno.db`) to save balance and full game history.
* **Provably Fair:** SHA-256 hash returned with every result for game integrity transparency.

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3, Flask |
| Database | SQLite3 |
| Frontend | HTML5, CSS3 (Flexbox/Grid), Vanilla JS (Fetch API) |
| Fonts | Barlow Condensed, Rajdhani (Google Fonts) |
| Icons | Lucide Icons |

---

## 🚀 Installation & Setup

1. **Clone or download** this repository.

2. **Install Flask:**
    ```bash
    pip install flask
    ```

3. **Run the application:**
    ```bash
    python app.py
    ```

4. **Open in your browser:**
    ```
    http://127.0.0.1:5000
    ```

The database (`crowncases_keno.db`) is created automatically on first run with a starting balance of **$1,000.00**.

---

## 📂 Project Structure

```
CrownCases_Keno/
│
├── app.py                    # Flask backend — game logic, DB handler, API routes
├── crowncases_keno.db        # Auto-generated SQLite database (balance & history)
├── README.md                 # This file
└── templates/
    └── index.html            # Complete frontend (UI, styles, scripts)
```

---

## 🎲 Payout Table

| Picks | Hits Required → Multiplier |
|---|---|
| 1 | 1→ 3.96× |
| 2 | 2→ 15× |
| 3 | 2→ 1.5×, 3→ 36× |
| 4 | 2→ 1.2×, 3→ 5×, 4→ 80× |
| 5 | 2→ 0.5×, 3→ 3×, 4→ 12×, 5→ 300× |
| 6 | 3→ 1×, 4→ 5×, 5→ 30×, 6→ 500× |
| 7 | 3→ 0.5×, 4→ 3×, 5→ 15×, 6→ 100×, 7→ 700× |
| 8 | 4→ 1.5×, 5→ 10×, 6→ 50×, 7→ 300×, 8→ 800× |
| 9 | 4→ 1×, 5→ 5×, 6→ 30×, 7→ 100×, 8→ 500×, 9→ 900× |
| 10 | 5→ 2×, 6→ 15×, 7→ 80×, 8→ 400×, 9→ 800×, 10→ 1000× |

---

## 🔒 Provably Fair

Every game result returns a `hash` field — a SHA-256 digest of the server seed combined with the drawn numbers. This allows verification that results were not manipulated after the fact.

---

*CrownCases Keno — Built for CrownCases.GG*
