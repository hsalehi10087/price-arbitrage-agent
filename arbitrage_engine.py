"""
arbitrage_engine.py — محاسبه آربیتراژ و رتبه‌بندی
"""

import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

# ───── هزینه‌های واقع‌بینانه واردات ─────
IMPORT_OVERHEAD = {
    "customs_percent": 0.30,    # ۳۰٪ گمرک تخمینی
    "shipping_usd": 5.0,        # حمل پایه ۵ دلار
    "risk_buffer": 0.10,        # ۱۰٪ ریسک و هزینه‌های جانبی
}

def calculate_global_arbitrage(
    product: dict,
    prices: dict,
    usd_rate: float,
) -> Optional[dict]:
    """
    آربیتراژ بین‌المللی: علی‌اکسپرس → ایران
    """
    ali_usd = prices.get("aliexpress_usd")
    iran_toman = prices.get("iran_online_toman")

    if not ali_usd or not iran_toman or ali_usd <= 0 or iran_toman <= 0:
        return None

    # محاسبه قیمت تمام‌شده واردات (تومان)
    total_usd = ali_usd + IMPORT_OVERHEAD["shipping_usd"]
    total_usd *= (1 + IMPORT_OVERHEAD["customs_percent"])
    total_usd *= (1 + IMPORT_OVERHEAD["risk_buffer"])
    cost_toman = total_usd * (usd_rate / 10)  # ریال → تومان

    if cost_toman <= 0:
        return None

    margin_pct = ((iran_toman - cost_toman) / cost_toman) * 100
    profit_toman = iran_toman - cost_toman

    return {
        "type": "global",
        "product": product["name"],
        "category": product["category"],
        "source_price_usd": round(ali_usd, 2),
        "landed_cost_toman": int(cost_toman),
        "iran_market_price_toman": int(iran_toman),
        "profit_toman": int(profit_toman),
        "margin_pct": round(margin_pct, 1),
        "foreign_source": prices.get("foreign_source", "خارجی"),
        "source": f"{prices.get('foreign_source', 'خارجی')} → ترب/دیجی‌کالا",
    }


def calculate_local_arbitrage(product: dict, prices: dict) -> Optional[dict]:
    """
    آربیتراژ داخلی: قیمت آنلاین ایران → اصفهان
    """
    iran_toman = prices.get("iran_online_toman")
    isfahan_toman = prices.get("isfahan_toman")

    if not iran_toman or not isfahan_toman or iran_toman <= 0 or isfahan_toman <= 0:
        return None

    # اگر قیمت اصفهان پایین‌تر باشد، آربیتراژ وجود ندارد
    if isfahan_toman <= iran_toman:
        return None

    # هزینه ارسال تخمینی (۳٪ از قیمت یا حداقل ۲۰ هزار تومان)
    shipping = max(iran_toman * 0.03, 20_000)
    actual_cost = iran_toman + shipping
    profit = isfahan_toman - actual_cost
    margin_pct = (profit / actual_cost) * 100

    if margin_pct < 5:  # زیر ۵٪ ارزش ندارد
        return None

    return {
        "type": "local",
        "product": product["name"],
        "category": product["category"],
        "online_price_toman": int(iran_toman),
        "isfahan_price_toman": int(isfahan_toman),
        "shipping_est_toman": int(shipping),
        "profit_toman": int(profit),
        "margin_pct": round(margin_pct, 1),
        "source": "دیجی‌کالا/ترب → دیوار اصفهان",
    }


def run_arbitrage_analysis(products_prices: List[dict], usd_rate: float) -> dict:
    """
    تحلیل کامل آربیتراژ برای همه کالاها
    خروجی: دیکشنری با بهترین فرصت‌های هر نوع
    """
    global_opps = []
    global_all = []   # همه کالاها (حتی مارجین منفی) برای نمایش
    local_opps = []

    for item in products_prices:
        product = item["product"]
        prices = item["prices"]

        g = calculate_global_arbitrage(product, prices, usd_rate)
        if g:
            global_all.append(g)
            if g["margin_pct"] > 0:
                global_opps.append(g)

        l = calculate_local_arbitrage(product, prices)
        if l:
            local_opps.append(l)

    # مرتب‌سازی بر اساس حاشیه سود
    global_all.sort(key=lambda x: x["margin_pct"], reverse=True)
    global_opps.sort(key=lambda x: x["margin_pct"], reverse=True)
    local_opps.sort(key=lambda x: x["margin_pct"], reverse=True)

    # اگر فرصت مثبت وجود نداشت، top5 از همه (حتی منفی) نشان بده
    top5_to_show = global_opps[:5] if global_opps else global_all[:5]

    return {
        "global_top5": top5_to_show,
        "local_top5": local_opps[:5],
        "total_scanned": len(products_prices),
        "global_found": len(global_opps),
        "local_found": len(local_opps),
        "global_all_count": len(global_all),
    }
