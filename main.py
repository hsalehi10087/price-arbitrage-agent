"""
main.py — نقطه ورود اصلی ایجنت
اجرا: python main.py
حالت‌ها:
  - هر ساعت: گزارش فشرده (فقط TOP 1 هر بخش + بهترین ایده)
  - هر روز ساعت ۸ تهران (UTC 4): گزارش کامل با مشاوره کسب‌وکار
"""

import os
import logging
import time
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import List

from products import PRODUCTS
from export_products import EXPORT_PRODUCTS
from scrapers import get_all_prices, get_usd_to_irr, get_export_target_price
from arbitrage_engine import run_arbitrage_analysis, run_export_analysis
from telegram_reporter import (
    build_full_report,
    build_hourly_snapshot,
    send_to_telegram,
)

# ───── لاگینگ ─────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

# فایل ذخیره بهترین ایده روز
BEST_IDEA_FILE = Path("best_idea_today.json")


def _is_full_report_hour() -> bool:
    """آیا الان ساعت گزارش کامل روزانه است؟ (۸ صبح تهران = ۴:۳۰ UTC)"""
    now_utc = datetime.now(timezone.utc)
    return now_utc.hour == 4


def _load_best_idea() -> dict:
    """بارگذاری بهترین ایده ذخیره‌شده"""
    if BEST_IDEA_FILE.exists():
        try:
            return json.loads(BEST_IDEA_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}


def _save_best_idea(idea: dict):
    """ذخیره بهترین ایده روز"""
    try:
        BEST_IDEA_FILE.write_text(
            json.dumps(idea, ensure_ascii=False, indent=2), encoding="utf-8"
        )
    except Exception as e:
        logger.warning(f"ذخیره best_idea ناموفق: {e}")


def _update_best_idea(results: dict, usd_rate: float):
    """
    اگر فرصت بهتری از best_idea فعلی پیدا شد، آپدیت کن.
    هر روز در گزارش کامل، best_idea ریست می‌شود.
    """
    new_best = {}

    # بهترین بین‌المللی
    if results["global_top5"]:
        top_g = results["global_top5"][0]
        new_best = {
            "type": "global",
            "product": top_g["product"],
            "margin_pct": top_g["margin_pct"],
            "profit_toman": top_g["profit_toman"],
            "source_price_usd": top_g["source_price_usd"],
            "iran_price_toman": top_g["iran_market_price_toman"],
            "usd_rate": usd_rate,
            "found_at": datetime.now(timezone.utc).strftime("%H:%M UTC"),
        }

    # مقایسه با best_idea قبلی
    old_best = _load_best_idea()
    if not old_best or new_best.get("margin_pct", 0) > old_best.get("margin_pct", 0):
        _save_best_idea(new_best)
        return new_best
    return old_best


def main():
    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
    chat_id   = os.environ.get("TELEGRAM_CHAT_ID", "")

    if not bot_token or not chat_id:
        logger.error("TELEGRAM_BOT_TOKEN یا TELEGRAM_CHAT_ID تنظیم نشده!")
        return

    is_full = _is_full_report_hour()
    logger.info("=" * 50)
    logger.info(f"حالت: {'گزارش کامل روزانه' if is_full else 'اسنپ‌شات ساعتی'}")
    logger.info(f"اسکن {len(PRODUCTS)} کالا ...")
    logger.info("=" * 50)

    # ── نرخ دلار ──
    usd_rate = get_usd_to_irr()
    logger.info(f"نرخ دلار: {usd_rate / 10:,.0f} تومان")

    # ── دریافت قیمت‌ها ──
    products_prices: List[dict] = []
    for i, product in enumerate(PRODUCTS, 1):
        logger.info(f"[{i}/{len(PRODUCTS)}] {product['name']}")
        prices = get_all_prices(product)
        products_prices.append({"product": product, "prices": prices})
        time.sleep(1.5)

    # ── تحلیل آربیتراژ واردات ──
    results = run_arbitrage_analysis(products_prices, usd_rate)
    logger.info(f"فرصت‌های بین‌المللی: {results['global_found']} | داخلی: {results['local_found']}")

    # ── اسکن محصولات صادراتی (فقط در گزارش کامل — برای صرفه‌جویی در time) ──
    export_results = {"top5_export": [], "by_category": {}, "total_scanned": 0, "total_found": 0}
    if is_full:
        logger.info(f"اسکن {len(EXPORT_PRODUCTS)} محصول صادراتی ...")
        for product in EXPORT_PRODUCTS:
            # قیمت‌های scrape شده رو در target_markets به‌روز می‌کنیم
            for market in list(product.get("target_markets", {}).keys()):
                if market == "USA":
                    continue
                scraped = get_export_target_price(product, market)
                if scraped:
                    product["target_markets"][market]["price_usd"] = scraped
                    product["target_markets"][market]["source"] = f"live-{market.lower()}"
            time.sleep(1.0)

        export_results = run_export_analysis(EXPORT_PRODUCTS, usd_rate)
        logger.info(f"فرصت‌های صادراتی: {export_results['total_found']}")
    else:
        # در اسنپ‌شات ساعتی فقط از قیمت fallback استفاده می‌کنیم
        export_results = run_export_analysis(EXPORT_PRODUCTS, usd_rate)

    # ترکیب نتایج صادراتی با results
    results["export_top5"] = export_results.get("top5_export", [])
    results["export_found"] = export_results.get("total_found", 0)
    results["export_by_category"] = export_results.get("by_category", {})

    # ── آپدیت بهترین ایده روز ──
    if is_full:
        # ریست روزانه
        best_idea = _update_best_idea(results, usd_rate)
        _save_best_idea(best_idea)
    else:
        best_idea = _update_best_idea(results, usd_rate)

    # ── ساخت و ارسال گزارش ──
    if is_full:
        report = build_full_report(results, usd_rate, best_idea)
    else:
        report = build_hourly_snapshot(results, usd_rate, best_idea)

    logger.info(f"گزارش: {len(report)} کاراکتر")

    ok = send_to_telegram(bot_token, chat_id, report)
    logger.info("✅ ارسال موفق" if ok else "❌ ارسال ناموفق")

    # خلاصه لاگ
    for opp in results["global_top5"][:3]:
        logger.info(f"  🌍 {opp['product']}: {opp['margin_pct']:.0f}٪")
    for opp in results["local_top5"][:3]:
        logger.info(f"  🏙️ {opp['product']}: {opp['margin_pct']:.0f}٪")
    for opp in results.get("export_top5", [])[:3]:
        logger.info(f"  📦 {opp['product']} → {opp['market_name']}: {opp['margin_pct']:.0f}٪")


if __name__ == "__main__":
    main()
