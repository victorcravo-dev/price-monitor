"""
Amazon Brasil Price Monitor
Monitora preços e envia alerta por e-mail quando cair abaixo do alvo.

Como encontrar o ASIN do produto:
1. Abra o produto na Amazon Brasil
2. Na URL vai ter /dp/XXXXXXXXXX
3. Copie apenas os 10 caracteres: ex B0GWNFMG5L
4. Cole no products.json como "asin"
"""

import json
import logging
import os
import re
import smtplib
import subprocess
import time
from dataclasses import dataclass, asdict
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

# ── Logging ───────────────────────────────────────────────────────────────────
LOG_DIR = Path(__file__).parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / "monitor.log"),
        logging.StreamHandler(),
    ],
)
log = logging.getLogger(__name__)

DATA_DIR = Path(__file__).parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)
HISTORY_FILE = DATA_DIR / "price_history.json"
PRODUCTS_FILE = DATA_DIR / "products.json"


@dataclass
class Product:
    name: str
    asin: str           # Ex: B0GWNFMG5L
    target_price: float
    alert_email: str


@dataclass
class PriceRecord:
    product_name: str
    asin: str
    price: float
    target_price: float
    checked_at: str
    product_url: str = ""
    alert_sent: bool = False


# ── Scraper usando curl nativo do Windows ─────────────────────────────────────
def fetch_page_with_curl(url: str) -> str | None:
    """
    Usa o curl nativo do Windows para buscar a página.
    Mais difícil de bloquear que requests puro.
    """
    try:
        result = subprocess.run(
            [
                "curl", "-s", "-L",
                "-H", "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
                "-H", "Accept-Language: pt-BR,pt;q=0.9",
                "-H", "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "-H", "Accept-Encoding: gzip, deflate, br",
                "--compressed",
                "--max-time", "20",
                url,
            ],
            capture_output=True,
            timeout=25,
        )
        if result.returncode == 0:
            return result.stdout.decode("utf-8", errors="ignore")
        log.error("curl falhou com código %d", result.returncode)
        return None
    except (subprocess.TimeoutExpired, FileNotFoundError) as e:
        log.error("Erro ao executar curl: %s", e)
        return None


def parse_amazon_price(html: str) -> float | None:
    """
    Extrai o preço de uma página da Amazon Brasil.
    Tenta múltiplos seletores para ser robusto a mudanças de layout.
    """
    soup = BeautifulSoup(html, "html.parser")

    # Detecta CAPTCHA ou bloqueio
    if "captcha" in html.lower() or "sorry" in soup.get_text().lower()[:500]:
        log.warning("Amazon retornou CAPTCHA ou página de bloqueio.")
        return None

    # Seletores em ordem de prioridade
    selectors = [
        ".a-price .a-offscreen",
        "#corePrice_feature_div .a-offscreen",
        "#apex_desktop .a-offscreen",
        "span.a-price-whole",
        "#priceblock_ourprice",
        "#priceblock_dealprice",
    ]

    for sel in selectors:
        el = soup.select_one(sel)
        if el:
            raw = el.get_text(strip=True)
            # Remove R$, pontos de milhar, substitui vírgula por ponto
            cleaned = re.sub(r"[R$\s\.]", "", raw).replace(",", ".")
            try:
                price = float(cleaned)
                if price > 0:
                    log.debug("Preço encontrado com seletor '%s': R$ %.2f", sel, price)
                    return price
            except ValueError:
                continue

    # Fallback: busca no texto com regex
    matches = re.findall(r"R\$\s*([\d\.]+,\d{2})", html)
    if matches:
        raw = matches[0].replace(".", "").replace(",", ".")
        try:
            return float(raw)
        except ValueError:
            pass

    log.warning("Nenhum preço encontrado na página.")
    return None


def fetch_price(asin: str) -> tuple[float | None, str]:
    url = f"https://www.amazon.com.br/dp/{asin}"
    html = fetch_page_with_curl(url)
    if not html:
        return None, url
    price = parse_amazon_price(html)
    return price, url


# ── E-mail ────────────────────────────────────────────────────────────────────
def send_alert_email(record: PriceRecord, recipient: str) -> bool:
    sender = os.getenv("GMAIL_USER")
    password = os.getenv("GMAIL_APP_PASSWORD")
    if not sender or not password:
        log.error("GMAIL_USER ou GMAIL_APP_PASSWORD não configurado no .env")
        return False

    discount_pct = round((1 - record.price / record.target_price) * 100, 1)
    subject = f"🔔 Alerta Amazon: {record.product_name} — R$ {record.price:.2f}"

    html_body = f"""
    <html><body style="font-family:Arial,sans-serif;max-width:600px;margin:auto;padding:20px">
      <h2 style="color:#FF9900;background:#232F3E;padding:16px;border-radius:8px;margin:0">
        🔔 Alerta de Queda de Preço — Amazon
      </h2>
      <div style="background:#f9f9f9;padding:20px;border-radius:8px;margin-top:16px">
        <h3 style="margin-top:0">{record.product_name}</h3>
        <table style="width:100%;border-collapse:collapse">
          <tr>
            <td style="padding:8px 0;color:#666">Preço atual</td>
            <td style="padding:8px 0;font-size:24px;font-weight:bold;color:#B12704">
              R$ {record.price:.2f}
            </td>
          </tr>
          <tr>
            <td style="padding:8px 0;color:#666">Seu alvo</td>
            <td style="padding:8px 0">R$ {record.target_price:.2f}</td>
          </tr>
          <tr>
            <td style="padding:8px 0;color:#666">Abaixo do alvo em</td>
            <td style="padding:8px 0;color:#007600;font-weight:bold">{discount_pct}%</td>
          </tr>
          <tr>
            <td style="padding:8px 0;color:#666">Verificado em</td>
            <td style="padding:8px 0">{record.checked_at}</td>
          </tr>
        </table>
        <a href="{record.product_url}"
           style="display:inline-block;margin-top:16px;padding:12px 24px;
                  background:#FF9900;color:#232F3E;text-decoration:none;
                  border-radius:6px;font-weight:bold">
          Comprar na Amazon →
        </a>
      </div>
    </body></html>
    """

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = recipient
    msg.attach(MIMEText(html_body, "html"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender, password)
            server.sendmail(sender, recipient, msg.as_string())
        log.info("E-mail enviado para %s", recipient)
        return True
    except smtplib.SMTPException as e:
        log.error("Falha ao enviar e-mail: %s", e)
        return False


# ── Histórico ─────────────────────────────────────────────────────────────────
def load_history() -> list[dict]:
    if HISTORY_FILE.exists():
        with open(HISTORY_FILE) as f:
            return json.load(f)
    return []


def save_history(history: list[dict]) -> None:
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2, ensure_ascii=False)


def load_products() -> list[Product]:
    if PRODUCTS_FILE.exists():
        with open(PRODUCTS_FILE) as f:
            data = json.load(f)
        return [Product(**p) for p in data]
    log.warning("products.json não encontrado.")
    return []


# ── Loop principal ────────────────────────────────────────────────────────────
def run_monitor(interval_minutes: int = 60) -> None:
    log.info("Iniciando Amazon Price Monitor. Verificando a cada %d minutos.", interval_minutes)
    products = load_products()
    if not products:
        log.error("Nenhum produto em data/products.json.")
        return

    log.info("Monitorando %d produto(s).", len(products))

    while True:
        history = load_history()
        for product in products:
            log.info("Verificando: %s (ASIN: %s)", product.name, product.asin)
            price, url = fetch_price(product.asin)

            if price is None:
                log.warning("Não foi possível obter o preço de '%s'.", product.name)
                continue

            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            record = PriceRecord(
                product_name=product.name,
                asin=product.asin,
                price=price,
                target_price=product.target_price,
                checked_at=now,
                product_url=url,
            )

            log.info("  '%s' → R$ %.2f (alvo: R$ %.2f)", product.name, price, product.target_price)

            if price <= product.target_price:
                log.info("  ✅ Preço atingiu o alvo! Enviando alerta...")
                record.alert_sent = send_alert_email(record, product.alert_email)
            else:
                log.info("  ⏳ Ainda R$ %.2f acima do alvo.", price - product.target_price)

            history.append(asdict(record))

        save_history(history)
        log.info("Ciclo completo. Aguardando %d min...\n", interval_minutes)
        time.sleep(interval_minutes * 60)


if __name__ == "__main__":
    interval = int(os.getenv("CHECK_INTERVAL_MINUTES", "60"))
    run_monitor(interval_minutes=interval)
