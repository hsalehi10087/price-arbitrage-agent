"""
telegram_reporter.py — فرمت و ارسال گزارش به تلگرام
"""

import requests
import logging
from datetime import datetime
import jdatetime  # تاریخ شمسی

logger = logging.getLogger(__name__)


def _jalali_today() -> str:
    jd = jdatetime.datetime.now()
    months = [
        "فروردین", "اردیبهشت", "خرداد", "تیر", "مرداد", "شهریور",
        "مهر", "آبان", "آذر", "دی", "بهمن", "اسفند"
    ]
    return f"{jd.day} {months[jd.month - 1]} {jd.year}"


def _fmt_toman(amount: int) -> str:
    """فرمت تومان"""
    if amount >= 1_000_000:
        return f"{amount / 1_000_000:.1f}M"
    elif amount >= 1_000:
        return f"{amount / 1_000:.0f}K"
    return str(amount)


def _margin_emoji(pct: float) -> str:
    if pct >= 150:
        return "🔥"
    elif pct >= 100:
        return "🚀"
    elif pct >= 50:
        return "✅"
    elif pct >= 20:
        return "👍"
    return "📊"


def _business_recommendation(product_name: str, margin_pct: float, arb_type: str) -> str:
    """پیشنهاد کانال فروش برای هر کالا — یک خط زیر جدول"""
    if arb_type == "global":
        if margin_pct >= 150:
            return "🏪 کانال تلگرام اختصاصی + پیج اینستاگرام"
        elif margin_pct >= 100:
            return "🛒 فروشگاه اینستاگرام + ثبت در دیجی‌کالا مارکت"
        elif margin_pct >= 50:
            return "📦 دراپ‌شیپینگ از دیجی‌کالا"
        else:
            return "🔄 آربیتراژ کوچک — مناسب فروش اینترنتی"
    else:
        if margin_pct >= 30:
            return "🏬 خرید آنلاین، فروش در دیوار/شیپور اصفهان"
        else:
            return "📍 بازفروش محلی اصفهان"


# ═══════════════════════════════════════════════════════════
# بخش مشاوره کسب‌وکار — تحلیل هوشمند بر اساس داده روز
# ═══════════════════════════════════════════════════════════

def _get_business_model(product: str, margin_pct: float, arb_type: str) -> dict:
    """
    برای هر کالا: مدل کسب‌وکار پیشنهادی + سایت + درآمد تخمینی
    """
    # ── آربیتراژ بین‌المللی ──
    if arb_type == "global":
        if margin_pct >= 150:
            return {
                "model": "فروشگاه تخصصی (Niche Store)",
                "site": "سایت فروشگاهی روی دامنه .ir (وردپرس + ووکامرس)",
                "channels": ["اینستاگرام", "کانال تلگرام", "ثبت در ترب"],
                "steps": [
                    "۱. سفارش نمونه ۵ تایی از علی‌اکسپرس",
                    "۲. عکاسی حرفه‌ای و ساخت محتوا",
                    "۳. راه‌اندازی پیج اینستاگرام نیش",
                    "۴. ثبت در دیجی‌کالا مارکت‌پلیس",
                    "۵. افزایش حجم پس از اثبات فروش",
                ],
                "monthly_est": "با ۵۰ فروش/ماه → ۵۰ × سود هر واحد",
                "risk": "⚠️ ریسک: تاخیر گمرک، نوسان دلار",
            }
        elif margin_pct >= 80:
            return {
                "model": "دراپ‌شیپینگ یا واردات کوچک",
                "site": "پیج اینستاگرام + لینک‌تری + ثبت در باسلام",
                "channels": ["اینستاگرام", "باسلام", "دیوار"],
                "steps": [
                    "۱. ثبت در باسلام.com (رایگان)",
                    "۲. سفارش اولیه ۱۰–۲۰ واحد",
                    "۳. درج آگهی در دیوار (رایگان)",
                    "۴. تبلیغ در گروه‌های تلگرامی مرتبط",
                ],
                "monthly_est": "با ۳۰ فروش/ماه → درآمد معقول",
                "risk": "⚠️ ریسک: رقابت بالا در بازار",
            }
        else:
            return {
                "model": "فروش پراکنده / آربیتراژ فرصتی",
                "site": "دیوار + شیپور (رایگان، بدون سایت)",
                "channels": ["دیوار", "شیپور"],
                "steps": [
                    "۱. خرید گاه‌به‌گاه وقتی دلار پایین است",
                    "۲. فروش در دیوار/شیپور",
                ],
                "monthly_est": "درآمد متغیر — مناسب کار پاره‌وقت",
                "risk": "⚠️ ریسک: حاشیه کم — نیاز به حجم بالا",
            }

    # ── آربیتراژ داخلی ──
    else:
        if margin_pct >= 25:
            return {
                "model": "واسطه‌گری هوشمند (بدون انبار)",
                "site": "دیوار اصفهان + شیپور + گروه‌های اینستاگرام محلی",
                "channels": ["دیوار اصفهان", "شیپور", "واتس‌اپ محلی"],
                "steps": [
                    "۱. رصد روزانه قیمت آنلاین (همین گزارش)",
                    "۲. درج آگهی در دیوار اصفهان",
                    "۳. خرید از دیجی‌کالا پس از دریافت سفارش",
                    "۴. ارسال مستقیم به خریدار (بدون انبار)",
                ],
                "monthly_est": "با ۲۰ معامله/ماه → درآمد خوب",
                "risk": "⚠️ ریسک: تغییر قیمت آنلاین بین سفارش و تحویل",
            }
        else:
            return {
                "model": "فروش محلی فرصتی",
                "site": "دیوار (بدون سایت)",
                "channels": ["دیوار"],
                "steps": ["خرید آنلاین، فروش حضوری در اصفهان"],
                "monthly_est": "درآمد کم — توصیه: کالاهای با مارجین بالاتر",
                "risk": "⚠️ ریسک: رقابت محلی",
            }


def build_business_advisory(global_top5: list, local_top5: list, usd_rate: float) -> str:
    """
    بخش مشاوره کسب‌وکار — در پایین گزارش روزانه
    فقط ۲ فرصت برتر را عمیق تحلیل می‌کند تا پیام خیلی طولانی نشود
    """
    lines = [
        f"\n{'═' * 30}\n",
        "💼 <b>مشاور کسب‌وکار: بهترین فرصت امروز</b>\n",
    ]

    # بهترین فرصت بین‌المللی
    if global_top5:
        best_global = global_top5[0]
        bm = _get_business_model(best_global["product"], best_global["margin_pct"], "global")
        profit_per_unit = best_global["profit_toman"]

        # تخمین درآمد ماهانه ۳ سناریو
        low_sales, mid_sales, high_sales = 20, 50, 100
        low_income = low_sales * profit_per_unit
        mid_income = mid_sales * profit_per_unit
        high_income = high_sales * profit_per_unit

        lines.append(
            f"🌍 <b>فرصت واردات: {best_global['product']}</b>\n"
            f"   مدل پیشنهادی: <b>{bm['model']}</b>\n"
            f"   سایت/کانال: {bm['site']}\n"
            f"   کانال‌های فروش: {' | '.join(bm['channels'])}\n\n"
            f"   📋 <b>نقشه راه اجرا:</b>\n"
        )
        for step in bm["steps"]:
            lines.append(f"   {step}\n")

        lines.append(
            f"\n   💰 <b>تخمین درآمد ماهانه:</b>\n"
            f"   • سناریو محتاطانه ({low_sales} فروش): <code>{_fmt_toman(low_income)} تومان</code>\n"
            f"   • سناریو متوسط ({mid_sales} فروش): <code>{_fmt_toman(mid_income)} تومان</code>\n"
            f"   • سناریو خوش‌بینانه ({high_sales} فروش): <code>{_fmt_toman(high_income)} تومان</code>\n"
            f"   {bm['risk']}\n"
        )

    # بهترین فرصت داخلی
    if local_top5:
        best_local = local_top5[0]
        bm_l = _get_business_model(best_local["product"], best_local["margin_pct"], "local")
        profit_l = best_local["profit_toman"]

        low_l = 15 * profit_l
        mid_l = 30 * profit_l

        lines.append(
            f"\n{'─' * 25}\n"
            f"🏙️ <b>فرصت داخلی: {best_local['product']}</b>\n"
            f"   مدل پیشنهادی: <b>{bm_l['model']}</b>\n"
            f"   کانال‌های فروش: {' | '.join(bm_l['channels'])}\n\n"
            f"   📋 <b>نقشه راه:</b>\n"
        )
        for step in bm_l["steps"]:
            lines.append(f"   {step}\n")

        lines.append(
            f"\n   💰 <b>تخمین درآمد:</b>\n"
            f"   • ۱۵ معامله/ماه: <code>{_fmt_toman(low_l)} تومان</code>\n"
            f"   • ۳۰ معامله/ماه: <code>{_fmt_toman(mid_l)} تومان</code>\n"
            f"   {bm_l['risk']}\n"
        )

    # توصیه استراتژیک روزانه
    lines.append(
        f"\n{'─' * 25}\n"
        f"🧠 <b>توصیه استراتژیک امروز:</b>\n"
    )

    # منطق هوشمند توصیه بر اساس نرخ دلار
    usd_toman = usd_rate / 10
    if usd_toman >= 900_000:
        lines.append(
            "   دلار بالای ۹۰۰ هزار تومان است — <b>وقت طلایی واردات نیست.</b>\n"
            "   بهتر است روی آربیتراژ داخلی (بدون نیاز به دلار) تمرکز کنید.\n"
            "   اگر موجودی دلار دارید، الان وقت فروش کالا بهتر از خرید جدید است.\n"
        )
    elif usd_toman >= 700_000:
        lines.append(
            "   دلار در محدوده متوسط است — <b>واردات با احتیاط توجیه دارد.</b>\n"
            "   کالاهایی با مارجین بالای ۱۰۰٪ را پریوریتی کنید.\n"
            "   سفارش‌های کوچک (تست بازار) قبل از حجم بالا.\n"
        )
    else:
        lines.append(
            "   دلار پایین است — <b>بهترین فرصت برای خرید از علی‌اکسپرس!</b>\n"
            "   الان بخرید، وقتی دلار بالا رفت بفروشید.\n"
            "   کالاهایی با ماندگاری بالا (ابزار، الکترونیک) اولویت دارند.\n"
        )

    return "".join(lines)


def _fmt_rial(amount_toman: int) -> str:
    """فرمت ریال (تومان × ۱۰)"""
    rial = amount_toman * 10
    if rial >= 1_000_000_000:
        return f"{rial / 1_000_000_000:.1f}G ریال"
    elif rial >= 1_000_000:
        return f"{rial / 1_000_000:.0f}M ریال"
    elif rial >= 1_000:
        return f"{rial / 1_000:.0f}K ریال"
    return f"{rial:,} ریال"


def build_global_table(top5: list, usd_rate: float) -> str:
    """ساخت جدول آربیتراژ بین‌المللی با قیمت به ریال"""
    if not top5:
        return "⚠️ امروز فرصت آربیتراژ بین‌المللی یافت نشد.\n"

    usd_toman = usd_rate / 10
    lines = [
        f"🌍 <b>آربیتراژ بین‌المللی (خارج ← ایران)</b>\n"
        f"💱 دلار آزاد: <b>{usd_toman:,.0f} تومان</b> | <b>{usd_rate:,.0f} ریال</b>\n"
        f"{'─'*30}\n"
    ]

    for i, opp in enumerate(top5, 1):
        em = _margin_emoji(opp["margin_pct"])
        biz = _business_recommendation(opp["product"], opp["margin_pct"], "global")

        # محاسبه ریال
        ali_usd = opp['source_price_usd']
        landed_rial = opp['landed_cost_toman'] * 10
        iran_rial = opp['iran_market_price_toman'] * 10
        profit_rial = opp['profit_toman'] * 10

        source_label = opp.get("foreign_source", "خارجی")
        lines.append(
            f"\n{em} <b>{i}. {opp['product']}</b>  [{opp['category']}]\n"
            f"┌ قیمت {source_label}: <code>${ali_usd:.1f}</code> = <code>{ali_usd * usd_rate / 10:,.0f} ریال</code>\n"
            f"├ هزینه تمام‌شده (گمرک+ارسال): <code>{landed_rial:,.0f} ریال</code>\n"
            f"├ قیمت بازار ایران: <code>{iran_rial:,.0f} ریال</code>\n"
            f"├ 💰 سود خالص هر واحد: <b>{profit_rial:,.0f} ریال</b>\n"
            f"└ 📈 حاشیه: <b>{opp['margin_pct']:.0f}٪</b>  |  {biz}\n"
        )
    return "".join(lines)


def build_local_table(top5: list) -> str:
    """ساخت جدول آربیتراژ داخلی با قیمت به ریال"""
    if not top5:
        return "⚠️ امروز فرصت آربیتراژ داخلی یافت نشد.\n"

    lines = [
        f"🏙️ <b>آربیتراژ داخلی (آنلاین ← اصفهان)</b>\n"
        f"{'─'*30}\n"
    ]

    for i, opp in enumerate(top5, 1):
        em = _margin_emoji(opp["margin_pct"])
        biz = _business_recommendation(opp["product"], opp["margin_pct"], "local")

        online_rial = opp['online_price_toman'] * 10
        isfahan_rial = opp['isfahan_price_toman'] * 10
        profit_rial = opp['profit_toman'] * 10

        lines.append(
            f"\n{em} <b>{i}. {opp['product']}</b>  [{opp['category']}]\n"
            f"┌ قیمت آنلاین (ترب/دیجی‌کالا): <code>{online_rial:,.0f} ریال</code>\n"
            f"├ قیمت اصفهان (دیوار): <code>{isfahan_rial:,.0f} ریال</code>\n"
            f"├ 💰 سود هر معامله: <b>{profit_rial:,.0f} ریال</b>\n"
            f"└ 📈 حاشیه: <b>{opp['margin_pct']:.0f}٪</b>  |  {biz}\n"
        )
    return "".join(lines)


def _build_best_idea_banner(best_idea: dict) -> str:
    """
    بنر 'بهترین ایده امروز' — در بالای هر گزارش (ساعتی یا روزانه)
    تا کاربر هرگز مهم‌ترین فرصت روز را از دست ندهد.
    """
    if not best_idea:
        return ""

    em = _margin_emoji(best_idea.get("margin_pct", 0))
    arb_type_fa = "بین‌المللی 🌍" if best_idea.get("type") == "global" else "داخلی 🏙️"
    found_at = best_idea.get("found_at", "")

    banner = (
        f"{'🏆' * 10}\n"
        f"🏆 <b>بهترین ایده امروز</b>\n"
        f"{'🏆' * 10}\n"
        f"{em} <b>{best_idea.get('product', '—')}</b>  |  آربیتراژ {arb_type_fa}\n"
        f"   💰 حاشیه سود: <b>{best_idea.get('margin_pct', 0):.0f}٪</b>\n"
        f"   📈 سود هر واحد: <code>{_fmt_toman(best_idea.get('profit_toman', 0))} تومان</code>\n"
    )
    if best_idea.get("type") == "global" and best_idea.get("source_price_usd"):
        banner += f"   🛒 قیمت چین: <code>${best_idea['source_price_usd']:.1f}</code>  →  بازار ایران: <code>{_fmt_toman(best_idea.get('iran_price_toman', 0))} تومان</code>\n"
    if found_at:
        banner += f"   🕐 کشف شده در: {found_at}\n"
    banner += f"{'─' * 30}\n\n"
    return banner


def build_full_report(results: dict, usd_rate: float, best_idea: dict = None) -> str:
    today = _jalali_today()
    total = results["total_scanned"]
    g_found = results["global_found"]
    l_found = results["local_found"]

    header = (
        f"📦 <b>گزارش کامل آربیتراژ قیمت</b>\n"
        f"📅 {today}\n"
        f"🔍 {total} کالا بررسی شد | {g_found} فرصت بین‌المللی | {l_found} فرصت داخلی\n"
        f"{'─' * 30}\n\n"
    )

    best_banner = _build_best_idea_banner(best_idea) if best_idea else ""
    global_section = build_global_table(results["global_top5"], usd_rate)
    sep = f"\n{'─' * 30}\n\n"
    local_section = build_local_table(results["local_top5"])

    # بخش مشاوره کسب‌وکار — هوشمند و بر اساس داده روز
    advisory_section = build_business_advisory(
        results["global_top5"],
        results["local_top5"],
        usd_rate,
    )

    footer = (
        f"\n{'─' * 30}\n"
        f"⚡ <i>قیمت‌های خارجی: eBay → علی‌اکسپرس → قیمت پایه</i>\n"
        f"⚡ <i>قیمت‌های ایران: ترب → دیجی‌کالا → قیمت پایه ایران</i>\n"
        f"⚠️ <i>هزینه گمرک ۳۰٪ + ارسال ۵$ در محاسبه لحاظ شده</i>"
    )

    return header + best_banner + global_section + sep + local_section + advisory_section + footer


def build_hourly_snapshot(results: dict, usd_rate: float, best_idea: dict = None) -> str:
    """
    اسنپ‌شات ساعتی — فشرده و سریع‌خوان
    فقط TOP 1 از هر بخش + بنر بهترین ایده امروز
    مناسب برای وقتی کاربر می‌خواهد هر ساعت آپدیت بگیرد بدون غرق شدن در اطلاعات
    """
    now_str = datetime.now().strftime("%H:%M")
    today = _jalali_today()

    header = (
        f"⚡ <b>اسنپ‌شات ساعتی آربیتراژ — {now_str}</b>\n"
        f"📅 {today}  |  💱 دلار: <b>{usd_rate / 10:,.0f} تومان</b>\n"
        f"{'─' * 30}\n\n"
    )

    # بنر بهترین ایده روز (در صدر)
    best_banner = _build_best_idea_banner(best_idea) if best_idea else ""

    # TOP 5 بین‌المللی — با قیمت کامل
    global_part = ""
    if results["global_top5"]:
        usd_toman = usd_rate / 10
        global_part = f"🌍 <b>آربیتراژ بین‌المللی (علی‌اکسپرس → ایران)</b>\n"
        for i, opp in enumerate(results["global_top5"], 1):
            em = _margin_emoji(opp["margin_pct"])
            margin_str = f"{opp['margin_pct']:.0f}٪"
            if opp["margin_pct"] < 0:
                margin_str = f"<i>{margin_str}</i>"
            global_part += (
                f"\n{em} <b>{i}. {opp['product']}</b>\n"
                f"   🛒 قیمت چین: <code>${opp['source_price_usd']:.1f}</code>"
                f"  ≈ <code>{opp['source_price_usd'] * usd_toman:,.0f} تومان</code>\n"
                f"   🏷 هزینه تمام‌شده (گمرک+ارسال): <code>{_fmt_toman(opp['landed_cost_toman'])} تومان</code>\n"
                f"   🏪 قیمت ایران: <code>{_fmt_toman(opp['iran_market_price_toman'])} تومان</code>\n"
                f"   💰 سود: <b>{_fmt_toman(opp['profit_toman'])} تومان</b>  |  حاشیه: <b>{margin_str}</b>\n"
            )
    else:
        global_part = "🌍 بین‌المللی: قیمت‌های کالا در دسترس نیست.\n"

    sep = f"\n{'─' * 25}\n\n"

    # TOP 5 داخلی — با قیمت کامل
    local_part = ""
    if results["local_top5"]:
        local_part = f"🏙️ <b>آربیتراژ داخلی (آنلاین → اصفهان)</b>\n"
        for i, opp in enumerate(results["local_top5"], 1):
            em = _margin_emoji(opp["margin_pct"])
            local_part += (
                f"\n{em} <b>{i}. {opp['product']}</b>\n"
                f"   🌐 قیمت آنلاین: <code>{_fmt_toman(opp['online_price_toman'])} تومان</code>\n"
                f"   📍 قیمت اصفهان: <code>{_fmt_toman(opp['isfahan_price_toman'])} تومان</code>\n"
                f"   💰 سود: <b>{_fmt_toman(opp['profit_toman'])} تومان</b>  |  حاشیه: <b>{opp['margin_pct']:.0f}٪</b>\n"
            )
    else:
        local_part = "🏙️ داخلی: فرصت قابل‌توجهی این ساعت یافت نشد.\n"

    # اشاره کوتاه به تعداد کل فرصت‌ها
    intl_positive = results["global_found"]
    intl_total = results.get("global_all_count", results["global_found"])
    summary_line = (
        f"\n{'─' * 25}\n"
        f"📊 این ساعت: {intl_positive} فرصت مثبت بین‌المللی (از {intl_total} کالا دارای قیمت) | {results['local_found']} فرصت داخلی\n"
        f"<i>گزارش کامل با مشاوره کسب‌وکار: ساعت ۸ صبح</i>"
    )

    return header + best_banner + global_part + sep + local_part + summary_line


def send_to_telegram(bot_token: str, chat_id: str, text: str) -> bool:
    """ارسال پیام به تلگرام"""
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

    # تلگرام محدودیت ۴۰۹۶ کاراکتر دارد، اگر طولانی بود تقسیم کن
    max_len = 4000
    chunks = [text[i:i+max_len] for i in range(0, len(text), max_len)]

    success = True
    for chunk in chunks:
        payload = {
            "chat_id": chat_id,
            "text": chunk,
            "parse_mode": "HTML",
            "disable_web_page_preview": True,
        }
        try:
            resp = requests.post(url, json=payload, timeout=15)
            if resp.status_code != 200:
                logger.error(f"Telegram error {resp.status_code}: {resp.text}")
                success = False
        except Exception as e:
            logger.error(f"Telegram send failed: {e}")
            success = False

    return success
