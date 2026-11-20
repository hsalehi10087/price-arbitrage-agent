"""
arbitrage_engine.py — محاسبه آربیتراژ و رتبه‌بندی
شامل سه نوع آربیتراژ:
  Type 1: واردات (AliExpress/Amazon → ایران)
  Type 2: داخلی (آنلاین → اصفهان)
  Type 3: صادرات (ایران → بازارهای خارجی)
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


def calculate_export_arbitrage(
    product: dict,
    usd_rate: float,
    target_market: Optional[str] = None,
) -> List[dict]:
    """
    آربیتراژ صادراتی: محصول ایرانی → بازار خارجی

    برای هر محصول، بهترین بازار هدف رو پیدا می‌کنه.
    فرمول:
      درآمد = قیمت بازار هدف (USD) × نرخ دلار (تومان)
      هزینه = قیمت عمده ایران (تومان) + هزینه حمل + گمرک مقصد
      سود = درآمد - هزینه
    """
    from export_products import EXPORT_COSTS

    iran_price_toman = product.get("iran_price_toman_fallback", 0)
    target_markets = product.get("target_markets", {})
    unit_weight_kg = product.get("unit_weight_kg", 0.5)

    if not iran_price_toman or not target_markets:
        return []

    results = []
    markets_to_check = [target_market] if target_market else list(target_markets.keys())

    for market_key in markets_to_check:
        if market_key not in target_markets or market_key not in EXPORT_COSTS:
            continue

        market_info = target_markets[market_key]
        cost_info = EXPORT_COSTS[market_key]

        # قیمت بازار هدف (تومان)
        target_price_usd = market_info.get("price_usd", 0)
        if not target_price_usd:
            continue

        # نرخ ارز (IRR → تومان: تقسیم بر ۱۰)
        usd_toman = usd_rate / 10
        revenue_toman = target_price_usd * usd_toman

        # هزینه حمل (تومان)
        shipping_usd = max(
            unit_weight_kg * cost_info["shipping_usd_per_kg"],
            cost_info["min_shipping_usd"]
        )
        shipping_toman = shipping_usd * usd_toman

        # گمرک مقصد (% از قیمت فروش)
        import_duty_toman = revenue_toman * cost_info["import_duty_pct"]

        # قیمت تمام‌شده کل (عمده ایران + حمل + گمرک)
        total_cost_toman = iran_price_toman + shipping_toman + import_duty_toman

        # ۵٪ هزینه‌های جانبی (بسته‌بندی، بیمه، etc)
        total_cost_toman *= 1.05

        profit_toman = revenue_toman - total_cost_toman
        if total_cost_toman <= 0:
            continue

        margin_pct = (profit_toman / total_cost_toman) * 100

        result = {
            "type": "export",
            "product": product["name"],
            "category": product["category"],
            "product_id": product["id"],
            "market": market_key,
            "market_name": cost_info["name"],
            "market_flag": cost_info.get("flag", "🌍"),
            "iran_cost_toman": int(iran_price_toman),
            "shipping_usd": round(shipping_usd, 2),
            "shipping_toman": int(shipping_toman),
            "target_price_usd": round(target_price_usd, 2),
            "revenue_toman": int(revenue_toman),
            "total_cost_toman": int(total_cost_toman),
            "profit_toman": int(profit_toman),
            "margin_pct": round(margin_pct, 1),
            "price_source": market_info.get("source", "market"),
            "source": f"ایران → {cost_info['name']} ({market_info.get('source', 'market')})",
            "note": cost_info.get("note", ""),
        }
        results.append(result)

    # مرتب‌سازی بر اساس حاشیه سود
    results.sort(key=lambda x: x["margin_pct"], reverse=True)
    return results


def run_export_analysis(export_products_list: list, usd_rate: float) -> dict:
    """
    تحلیل کامل آربیتراژ صادراتی برای همه محصولات
    """
    all_opportunities = []
    by_category: Dict[str, list] = {}

    for product in export_products_list:
        product_results = calculate_export_arbitrage(product, usd_rate)
        for r in product_results:
            # تحریم‌شده‌ها رو فیلتر می‌کنیم (USA)
            if r["market"] == "USA":
                continue
            all_opportunities.append(r)
            cat = r["category"]
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(r)

    # مرتب‌سازی کلی
    all_opportunities.sort(key=lambda x: x["margin_pct"], reverse=True)
    for cat in by_category:
        by_category[cat].sort(key=lambda x: x["margin_pct"], reverse=True)

    # بهترین بازار برای هر محصول (بدون تکرار)
    best_per_product: Dict[str, dict] = {}
    for opp in all_opportunities:
        pid = opp["product_id"]
        if pid not in best_per_product:
            best_per_product[pid] = opp

    top_export = sorted(
        best_per_product.values(),
        key=lambda x: x["margin_pct"],
        reverse=True
    )

    return {
        "top5_export": top_export[:5],
        "all_export": all_opportunities,
        "by_category": {cat: opps[:3] for cat, opps in by_category.items()},
        "total_scanned": len(export_products_list),
        "total_found": len(all_opportunities),
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
        # صادرات در run_export_analysis جداست
        "export_top5": [],
        "export_found": 0,
    }
