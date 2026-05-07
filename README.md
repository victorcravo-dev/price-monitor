# 🔔 Mercado Livre Price Monitor

Automated price tracker that monitors Mercado Livre products and sends email alerts when the price drops to your target. Set it once, let it run, and get notified at the right moment to buy.

![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-Active-brightgreen)

---

## ✨ Features

- **Multi-product tracking** — monitor as many products as you want from a single config file
- **Email alerts** — rich HTML email with product name, current price, discount percentage, and direct buy link
- **Price history** — every check is logged to JSON for trend analysis
- **Configurable interval** — check every hour, every 30 minutes, whatever fits your use case
- **Detailed logs** — rotating log file + console output for easy debugging
- **Lightweight** — no database required, no heavy frameworks

---

## 📋 Requirements

- Python 3.11+
- Gmail account with [App Password](https://myaccount.google.com/apppasswords) enabled
- A Mercado Livre product URL

---

## 🚀 Quick Start

**1. Clone the repository**
```bash
git clone https://github.com/yourusername/price-monitor.git
cd price-monitor
```

**2. Install dependencies**
```bash
pip install -r requirements.txt
```

**3. Configure environment variables**
```bash
cp .env.example .env
# Edit .env with your Gmail credentials
```

**4. Add products to monitor**

Edit `data/products.json`:
```json
[
  {
    "name": "Sony WH-1000XM5 Headphones",
    "url": "https://www.mercadolivre.com.br/...",
    "target_price": 1400.00,
    "alert_email": "your@gmail.com"
  }
]
```

**5. Run the monitor**
```bash
python src/monitor.py
```

---

## 📁 Project Structure

```
price-monitor/
├── src/
│   ├── monitor.py      # Main scraper + alert engine
│   └── report.py       # CLI history report
├── data/
│   ├── products.json   # Products to monitor (your config)
│   └── price_history.json  # Auto-generated price log
├── logs/
│   └── monitor.log     # Runtime logs
├── .env.example        # Environment variables template
├── requirements.txt
└── README.md
```

---

## 📧 Email Alert Example

When a price drops to your target, you receive an email like this:

> **🔔 Price Alert: Sony WH-1000XM5 — R$ 1.350,00**
>
> | | |
> |---|---|
> | Current price | **R$ 1.350,00** |
> | Your target | R$ 1.400,00 |
> | Below target by | **3.6%** |
>
> [Buy on Mercado Livre →]

---

## ⚙️ Configuration

| Variable | Description | Default |
|---|---|---|
| `GMAIL_USER` | Your Gmail address | — |
| `GMAIL_APP_PASSWORD` | Gmail App Password (not your login password) | — |
| `CHECK_INTERVAL_MINUTES` | How often to check prices | `60` |

### How to get a Gmail App Password

1. Go to [Google Account → Security](https://myaccount.google.com/security)
2. Enable 2-Step Verification (required)
3. Go to [App Passwords](https://myaccount.google.com/apppasswords)
4. Create a new app password for "Mail"
5. Paste the 16-character code in your `.env`

---

## 📊 View Price History

```bash
python src/report.py
```

Output:
```
============================================================
  PRICE MONITOR — HISTORY REPORT
============================================================

📦 Sony WH-1000XM5
   Target price : R$ 1400.00
   Latest price : R$ 1489.90  (2024-05-01 14:32:00)
   Highest      : R$ 1589.90
   Lowest       : R$ 1350.00
   Checks done  : 48
   Alerts sent  : 2
```

---

## 🔧 Run as a Background Service (Linux/macOS)

To keep the monitor running continuously, use `nohup`:

```bash
nohup python src/monitor.py &
```

Or create a cron job to run it periodically:

```bash
crontab -e
# Add: 0 * * * * /usr/bin/python3 /path/to/price-monitor/src/monitor.py
```

---

## 🛠️ Tech Stack

| Tool | Purpose |
|---|---|
| `requests` | HTTP requests to Mercado Livre |
| `BeautifulSoup4` | HTML parsing and price extraction |
| `smtplib` | Email delivery via Gmail SMTP |
| `python-dotenv` | Environment variable management |
| `json` | Lightweight price history storage |

---

## 📌 Roadmap

- [ ] Telegram notification support
- [ ] Streamlit dashboard for price history visualization  
- [ ] Support for other Brazilian e-commerce sites (Amazon BR, KaBuM)
- [ ] Price trend chart in email body
- [ ] Docker support

---

## 📄 License

MIT License — feel free to use, modify, and distribute.

---

## 👨‍💻 Author

Built by **[Your Name]** — Python developer specializing in automation and web scraping.

📧 [your@email.com](mailto:your@email.com) · 💼 [LinkedIn](https://linkedin.com/in/yourprofile) · 🐙 [GitHub](https://github.com/yourusername)

> *Looking for a Python developer to automate your workflows? Feel free to reach out.*
