# 🔔 Amazon Brasil Price Monitor

Automated price tracker that monitors Amazon Brasil products and sends email alerts when the price drops to your target. Set it once, let it run, and get notified at the right moment to buy.

![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-Active-brightgreen)

## ✨ Features

- **Multi-product tracking** — monitor as many products as you want
- **Email alerts** — HTML email with product name, current price, discount % and direct buy link
- **Price history** — every check logged to JSON
- **Configurable interval** — check every hour or every 30 minutes
- **Lightweight** — no database, no heavy frameworks

## 🚀 Quick Start

1. Clone the repository and install dependencies:
```bash
git clone https://github.com/victorcravo-dev/price-monitor.git
cd price-monitor
pip install -r requirements.txt
```

2. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your Gmail credentials
```

3. Add products to `data/products.json`:
```json
[
  {
    "name": "PS5 Slim",
    "asin": "B0GWNFMG5L",
    "target_price": 2500.00,
    "alert_email": "your@gmail.com"
  }
]
```

4. Run the monitor:
```bash
python src/monitor.py
```

## ⚙️ Configuration

| Variable | Description |
|---|---|
| `GMAIL_USER` | Your Gmail address |
| `GMAIL_APP_PASSWORD` | Gmail App Password (16 chars) |
| `CHECK_INTERVAL_MINUTES` | How often to check (default: 60) |

## 🛠️ Tech Stack

`Python` `BeautifulSoup4` `smtplib` `curl` `python-dotenv`

## 📄 License

MIT License
