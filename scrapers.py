"""
scrapers.py — توابع scraping برای هر سایت
استراتژی: هر سایت روش مخصوص خودش را دارد
"""

import requests
import random
import time
import re
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# ───── تنظیمات User-Agent ─────
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
]

def _get_headers():
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }

def _safe_get(url, timeout=15, retries=2):
    for attempt in range(retries):
        try:
            resp = requests.get(url, headers=_get_headers(), timeout=timeout)
            if resp.status_code == 200:
                return resp
            time.sleep(2 + attempt * 2)
        except Exception as e:
            logger.warning(f"Request failed ({attempt+1}/{retries}): {url} — {e}")
            time.sleep(3)
    return None

# ═══════════════════════════════════════
# قیمت دلار آزاد
# ═══════════════════════════════════════
def get_usd_to_irr() -> float:
    """نرخ دلار از bonbast.com (بازار آزاد)"""
    url = "https://bonbast.com/"
    try:
        resp = _safe_get(url, timeout=20)
        if resp:
            # bonbast نرخ دلار را در JSON خودش دارد
            match = re.search(r'"usd1":\s*"?(\d+)"?', resp.text)
            if match:
                rate = int(match.group(1)) * 10  # تومان → ریال
                logger.info(f"USD rate: {rate:,} IRR")
                return float(rate)
    except Exception as e:
        logger.error(f"USD rate error: {e}")

    # fallback: نرخ ثابت پشتیبان (به‌روز شود)
    logger.warning("Using fallback USD rate: 820,000 IRR")
    return 820_000.0

# ═══════════════════════════════════════
# علی‌اکسپرس
# ═══════════════════════════════════════
def get_aliexpress_price(query_en: str) -> Optional[float]:
    """
    قیمت از علی‌اکسپرس — از API خلاصه‌ی عمومی
    خروجی: قیمت دلار (float) یا None
    """
    url = f"https://www.aliexpress.com/wholesale?trafficChannel=main&d=y&CatId=0&SearchText={requests.utils.quote(query_en)}&ltype=wholesale&SortType=default&page=1"
    resp = _safe_get(url, timeout=20)
    if not resp:
        return None
    try:
        # الگو: "price":{"min":"1.5","max":"3.0"} یا "salePrice":{"minAmount":"2.5"...}
        patterns = [
            r'"minAmount":\s*"([\d.]+)"',
            r'"min":\s*"([\d.]+)"',
            r'"price":\s*"([\d.]+)"',
            r'\$\s*([\d.]+)',
        ]
        for pat in patterns:
            m = re.search(pat, resp.text)
            if m:
                price = float(m.group(1))
                if 0.5 <= price <= 2000:
                    logger.info(f"AliExpress [{query_en}]: ${price}")
                    return price
    except Exception as e:
        logger.error(f"AliExpress parse error: {e}")
    return None

# ═══════════════════════════════════════
# ترب ایران
# ═══════════════════════════════════════
def get_torob_price(query_fa: str) -> Optional[float]:
    """
    قیمت از ترب — قیمت‌یاب ایران
    خروجی: قیمت تومان (float) یا None
    """
    url = f"https://torob.com/api/v4/search/product/?query={requests.utils.quote(query_fa)}&page=0&sort=price_asc"
    headers = _get_headers()
    headers["Accept"] = "application/json"
    try:
        resp = requests.get(url, headers=headers, timeout=20)
        if resp.status_code == 200:
            data = resp.json()
            results = data.get("results", [])
            # پایین‌ترین قیمت معتبر را پیدا کن
            prices = []
            for item in results[:10]:
                p = item.get("price1") or item.get("min_price")
                if p and 10_000 < p < 500_000_000:
                    prices.append(p)
            if prices:
                price = min(prices)
                logger.info(f"Torob [{query_fa}]: {price:,} Toman")
                return float(price)
    except Exception as e:
        logger.error(f"Torob error: {e}")
    return None

# ═══════════════════════════════════════
# دیجی‌کالا
# ═══════════════════════════════════════
def get_digikala_price(query_fa: str) -> Optional[float]:
    """
    قیمت از دیجی‌کالا
    خروجی: قیمت تومان یا None
    """
    url = f"https://api.digikala.com/v1/search/?q={requests.utils.quote(query_fa)}&sort=1"
    headers = _get_headers()
    headers["Accept"] = "application/json"
    try:
        resp = requests.get(url, headers=headers, timeout=25)
        if resp.status_code == 200:
            data = resp.json()
            products = data.get("data", {}).get("products", [])
            prices = []
            for p in products[:8]:
                price_info = p.get("price", {})
                selling_price = price_info.get("selling_price")
                if selling_price and 10_000 < selling_price < 500_000_000:
                    prices.append(selling_price)
            if prices:
                price = min(prices) / 10  # ریال → تومان
                logger.info(f"Digikala [{query_fa}]: {price:,} Toman")
                return float(price)
    except Exception as e:
        logger.error(f"Digikala error: {e}")
    return None

# ═══════════════════════════════════════
# دیوار اصفهان
# ═══════════════════════════════════════
def get_divar_isfahan_price(query_fa: str) -> Optional[float]:
    """
    قیمت از دیوار اصفهان
    خروجی: میانگین قیمت‌های فعال (تومان) یا None
    """
    url = f"https://api.divar.ir/v8/search/isfahan?q={requests.utils.quote(query_fa)}&sort=sort_date"
    headers = _get_headers()
    headers["Accept"] = "application/json"
    try:
        resp = requests.get(url, headers=headers, timeout=20)
        if resp.status_code == 200:
            data = resp.json()
            posts = data.get("widget_list", []) or data.get("list_widgets", [])
            prices = []
            for post in posts[:15]:
                try:
                    # ساختار دیوار: data.top_description_row.text
                    desc = str(post)
                    price_matches = re.findall(r'(\d[\d,]{4,})', desc)
                    for pm in price_matches:
                        val = int(pm.replace(",", ""))
                        if 100_000 < val < 2_000_000_000:
                            prices.append(val)
                            break
                except Exception:
                    pass
            if prices:
                # مدیان بهتر از میانگین برای حذف اشتباهات
                prices.sort()
                median_price = prices[len(prices) // 2]
                logger.info(f"Divar Isfahan [{query_fa}]: {median_price:,} Toman")
                return float(median_price)
    except Exception as e:
        logger.error(f"Divar error: {e}")
    return None

# ═══════════════════════════════════════
# قیمت نهایی هر کالا
# ═══════════════════════════════════════
def get_all_prices(product: dict) -> dict:
    """
    دریافت تمام قیمت‌ها برای یک کالا
    خروجی: دیکشنری قیمت‌ها
    """
    time.sleep(random.uniform(1.5, 3.5))  # ضد بلاک شدن

    ali_usd = get_aliexpress_price(product["query_en"])
    time.sleep(random.uniform(1.0, 2.0))

    torob = get_torob_price(product["query_fa"])
    if not torob:
        torob = get_digikala_price(product["query_fa"])
    time.sleep(random.uniform(1.0, 2.0))

    divar_isf = get_divar_isfahan_price(product["query_fa"])

    return {
        "aliexpress_usd": ali_usd,
        "iran_online_toman": torob,
        "isfahan_toman": divar_isf,
    }
