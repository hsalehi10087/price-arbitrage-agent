"""
scrapers.py — توابع scraping برای هر سایت
استراتژی چندلایه برای قیمت‌گیری:
  ۱. eBay scraping (بدون API key — کاربردی از GitHub Actions)
  ۲. AliExpress direct scraping (تلاش می‌کند)
  ۳. Fallback: قیمت‌های دستی واقعی از products.py
برای قیمت‌های ایران: Torob → Digikala → None
"""

import os
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
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0",
]

def _get_headers(extra: dict = None) -> dict:
    h = {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Cache-Control": "no-cache",
    }
    if extra:
        h.update(extra)
    return h

def _safe_get(url, timeout=20, retries=2, headers=None):
    for attempt in range(retries):
        try:
            resp = requests.get(
                url,
                headers=headers or _get_headers(),
                timeout=timeout,
                allow_redirects=True,
            )
            if resp.status_code == 200:
                return resp
            elif resp.status_code in (429, 503):
                logger.warning(f"Rate limited ({resp.status_code}), sleeping...")
                time.sleep(5 + attempt * 5)
            else:
                logger.debug(f"HTTP {resp.status_code} for {url[:80]}")
                return None
        except requests.exceptions.Timeout:
            logger.warning(f"Timeout ({attempt+1}/{retries}): {url[:80]}")
            time.sleep(3)
        except Exception as e:
            logger.warning(f"Request failed ({attempt+1}/{retries}): {e}")
            time.sleep(3)
    return None


# ═══════════════════════════════════════
# نرخ دلار آزاد
# ═══════════════════════════════════════
def _get_usd_from_telegram_channel() -> Optional[float]:
    """قیمت دلار از کانال عمومی @DO_L4 (قیمت‌لحظه‌ای دلار طلا خودرو و سکه)
    4.4 میلیون subscriber — کانال اصلی قیمت‌دهی لحظه‌ای دلار تهران

    پیام‌های کانال شبیه این هستند:
      دلار: 266,200 تومان
      دلار فردایی تهران 💵 271,400 خرید

    این کانال PUBLIC است — نیاز به عضویت bot ندارد.
    از t.me/s/DO_L4 (web preview) استفاده می‌کنیم.
    """
    try:
        url = "https://t.me/s/DO_L4"
        resp = requests.get(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Accept-Language": "fa,en;q=0.9",
            },
            timeout=15,
        )
        if resp.status_code != 200:
            logger.debug(f"t.me/s/DO_L4 failed: {resp.status_code}")
            return None

        text = resp.text

        # Pattern 1: "دلار: 266,200 تومان" یا "دلار فردایی: 266,200"
        patterns = [
            r'دلار\s*فردایی[^\d]*(\d{3}[,،]\d{3})',   # دلار فردایی ... 271,400
            r'دلار\s*:\s*(\d{3}[,،]\d{3})\s*تومان',    # دلار: 266,200 تومان
            r'دلار[^\d]{0,20}(\d{3}[,،]\d{3})',         # دلار ... 266,200
        ]

        prices = []
        for pattern in patterns:
            for m in re.finditer(pattern, text):
                price_str = m.group(1).replace('،', '').replace(',', '')
                try:
                    price_toman = int(price_str)
                    if 200_000 < price_toman < 500_000:
                        prices.append(price_toman)
                except ValueError:
                    pass
            if prices:
                break

        if prices:
            # میانه قیمت‌های پیدا شده (برای دقت بیشتر)
            prices.sort()
            rate_toman = prices[len(prices) // 2]
            rate_irr = rate_toman * 10
            logger.info(f"USD rate from @DO_L4: {rate_toman:,} تومان = {rate_irr:,} IRR")
            return float(rate_irr)

        logger.debug("No USD price found in @DO_L4 channel")
        return None

    except Exception as e:
        logger.debug(f"@DO_L4 channel parse error: {e}")
        return None


def get_usd_to_irr() -> float:
    """نرخ دلار آزاد — زنجیره اولویت:
    ۰. GitHub Secret USD_IRR_RATE (همیشه دقیق)
    ۱. کانال تلگرام «دلار و طلا» (قیمت فردایی لحظه‌ای)
    ۲. bonbast.com
    ۳. bonbast API
    ۴. tgju.org API (فیلتر نرخ نیما)
    ۵. tgju.org HTML (فیلتر نرخ نیما)
    ۶. navasan.tech
    ۷. fallback ثابت: ۲۷۰,۰۰۰ تومان
    """
    import os

    # روش ۰: GitHub Secret (اولویت اول — همیشه دقیق)
    env_rate = os.environ.get("USD_IRR_RATE")
    if env_rate:
        try:
            rate = float(env_rate.replace(",", "").replace("_", ""))
            # اگر تومان وارد شده (۲۷۰۰۰۰) → تبدیل به ریال
            if rate < 500_000:
                rate = rate * 10
            if 1_000_000 < rate < 50_000_000:
                logger.info(f"USD rate from env/secret: {rate:,.0f} IRR ({rate/10:,.0f} تومان)")
                return rate
        except Exception:
            pass

    # روش ۱: کانال تلگرام «دلار و طلا» (قیمت لحظه‌ای بازار فردایی تهران)
    try:
        tg_rate = _get_usd_from_telegram_channel()
        if tg_rate:
            return tg_rate
    except Exception as e:
        logger.debug(f"Telegram channel USD error: {e}")

    # روش ۲: bonbast.com
    try:
        resp = _safe_get("https://bonbast.com/", timeout=15)
        if resp:
            match = re.search(r'"usd1":\s*"?(\d{4,8})"?', resp.text)
            if match:
                rate = int(match.group(1)) * 10  # تومان → ریال
                if 1_000_000 < rate < 50_000_000:   # بازه معقول (۱۰۰ت تا ۵م تومان)
                    logger.info(f"USD rate from bonbast: {rate:,} IRR")
                    return float(rate)
    except Exception as e:
        logger.error(f"bonbast error: {e}")

    # روش ۳: bonbast API
    try:
        resp2 = _safe_get("https://api.bonbast.com/latest", timeout=10,
                          headers={"Accept": "application/json"})
        if resp2:
            data = resp2.json()
            usd = data.get("usd", {})
            sell = usd.get("sell") or usd.get("1")
            if sell:
                rate = int(str(sell).replace(",", "")) * 10
                if 1_000_000 < rate < 50_000_000:
                    logger.info(f"USD rate from bonbast API: {rate:,} IRR")
                    return float(rate)
    except Exception as e:
        logger.debug(f"bonbast API error: {e}")

    # روش ۴: tgju.org API — نرخ دلار آزاد (price_dollar_rl)
    # بازار آزاد ~270,000 تومان = 2,700,000 ریال
    # نرخ نیما ~170,000 تومان = 1,700,000 ریال  ← باید رد شود
    # بازه معتبر: 2,000,000 تا 5,000,000 ریال (200,000 تا 500,000 تومان)
    IRR_MIN_FREE = 2_000_000   # 200,000 تومان — زیر این = نرخ نیما یا خطا
    IRR_MAX_FREE = 5_000_000   # 500,000 تومان — بالای این = خطا
    try:
        resp3 = _safe_get(
            "https://api.tgju.org/v1/market/indicator/summary-table-data/price_dollar_rl",
            timeout=10,
            headers={"Accept": "application/json", "Referer": "https://www.tgju.org/"}
        )
        if resp3:
            data = resp3.json()
            rows = data.get("data", [])
            if rows:
                # فیلدهای مختلف ممکن در پاسخ API
                price_str = (rows[0].get("p") or rows[0].get("price") or
                             rows[0].get("current") or rows[0].get("0"))
                if price_str:
                    rate = float(str(price_str).replace(",", ""))
                    if IRR_MIN_FREE < rate < IRR_MAX_FREE:
                        logger.info(f"USD rate from tgju (API): {rate:,.0f} IRR ({rate/10:,.0f} تومان)")
                        return rate
                    else:
                        logger.warning(
                            f"tgju API rate rejected: {rate:,.0f} IRR ({rate/10:,.0f} تومان) "
                            f"— خارج از بازه آزاد (نرخ نیما؟)"
                        )
    except Exception as e:
        logger.debug(f"tgju API error: {e}")

    # روش ۵: tgju.org — HTML scraping (fallback از API)
    # دلار آزاد باید بین 2,000,000 تا 5,000,000 ریال باشد
    try:
        resp4 = _safe_get(
            "https://www.tgju.org/profile/price_dollar_rl",
            timeout=12,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        )
        if resp4:
            # اول data-price (قابل اعتمادترین)
            match = re.search(r'data-price=["\'](\d{6,8})["\']', resp4.text)
            if not match:
                match = re.search(r'"p"\s*:\s*"(\d{6,8})"', resp4.text)
            if not match:
                # عدد 7 رقمی که با 2 یا 3 شروع می‌شود (2M-3.9M ریال = 200k-390k تومان)
                match = re.search(r'\b([23]\d{6})\b', resp4.text)
            if match:
                rate = float(match.group(1))
                if IRR_MIN_FREE < rate < IRR_MAX_FREE:
                    logger.info(f"USD rate from tgju (HTML): {rate:,.0f} IRR ({rate/10:,.0f} تومان)")
                    return rate
                else:
                    logger.warning(
                        f"tgju HTML rate rejected: {rate:,.0f} IRR ({rate/10:,.0f} تومان) "
                        f"— خارج از بازه آزاد"
                    )
    except Exception as e:
        logger.debug(f"tgju HTML error: {e}")

    # روش ۶: navasan.tech
    try:
        resp5 = _safe_get("https://api.navasan.tech/latest/?api_key=free&item=usd_buy",
                          timeout=10, headers={"Accept": "application/json"})
        if resp5:
            data = resp5.json()
            value = data.get("usd_buy", {}).get("value")
            if value:
                rate = float(str(value).replace(",", "")) * 10  # تومان → ریال
                if 1_000_000 < rate < 50_000_000:
                    logger.info(f"USD rate from navasan: {rate:,} IRR")
                    return float(rate)
    except Exception as e:
        logger.debug(f"navasan error: {e}")

    # Fallback ثابت — آبان ۱۴۰۳ → آذر ۱۴۰۵: ۲۷۰,۰۰۰ تومان
    logger.warning("Using fallback USD rate: 2,700,000 IRR (270,000 تومان)")
    return 2_700_000.0


# ═══════════════════════════════════════
# eBay — اصلی‌ترین منبع قیمت خارجی
# ═══════════════════════════════════════
def get_ebay_price(query_en: str, ebay_query: str = None) -> Optional[float]:
    """
    قیمت از eBay — بهترین گزینه از GitHub Actions
    استراتژی: جستجوی eBay با فیلتر "Buy It Now" و ارزان‌ترین قیمت
    خروجی: قیمت دلار (float) یا None
    """
    search_q = ebay_query or query_en
    encoded_q = requests.utils.quote(search_q)

    # روش ۱: eBay finding API (عمومی، بدون key)
    try:
        url = f"https://www.ebay.com/sch/i.html?_nkw={encoded_q}&_sop=15&LH_BIN=1&_ipg=24"
        headers = _get_headers({
            "Accept": "text/html,application/xhtml+xml",
            "Referer": "https://www.ebay.com/",
        })
        resp = requests.get(url, headers=headers, timeout=20)
        if resp.status_code == 200:
            text = resp.text
            # استخراج قیمت‌ها از HTML eBay
            prices = []
            # pattern 1: data-view="mi:1686" with price data
            for m in re.finditer(
                r'class="[^"]*s-item__price[^"]*"[^>]*>[\s\S]*?\$([\d,]+\.[\d]{2})',
                text
            ):
                try:
                    p = float(m.group(1).replace(",", ""))
                    if 1.0 <= p <= 1000:
                        prices.append(p)
                except (ValueError, TypeError):
                    pass

            # pattern 2: مقادیر JSON در صفحه
            for m in re.finditer(r'"price":\{"value":"([\d.]+)"', text):
                try:
                    p = float(m.group(1))
                    if 1.0 <= p <= 1000:
                        prices.append(p)
                except (ValueError, TypeError):
                    pass

            # pattern 3: ساده‌تر — هر قیمت دلاری
            if not prices:
                for m in re.finditer(r'\$\s*([\d]+\.[\d]{2})', text[:200000]):
                    try:
                        p = float(m.group(1))
                        if 1.0 <= p <= 500:
                            prices.append(p)
                    except (ValueError, TypeError):
                        pass

            if prices:
                prices.sort()
                # حذف قیمت‌های خیلی پایین (احتمالاً خطا) و خیلی بالا
                valid = [p for p in prices if p > prices[0] * 0.5]
                if valid:
                    # کوارتیل اول — نزدیک‌ترین به AliExpress
                    result = valid[len(valid) // 5] if len(valid) > 5 else valid[0]
                    logger.info(f"eBay [{search_q[:40]}]: ${result:.2f} (from {len(valid)} results)")
                    return result
    except Exception as e:
        logger.warning(f"eBay scrape error: {e}")

    logger.info(f"eBay: no price found for [{search_q[:40]}]")
    return None


# ═══════════════════════════════════════
# علی‌اکسپرس — تلاش مستقیم
# ═══════════════════════════════════════
def get_aliexpress_price(query_en: str) -> Optional[float]:
    """
    قیمت از علی‌اکسپرس — ممکن است از GitHub Actions block شود
    خروجی: قیمت دلار (float) یا None
    """
    # روش ۱: API موبایل علی‌اکسپرس
    try:
        url = (f"https://m.aliexpress.com/api/searchweb/product/search"
               f"?keywords={requests.utils.quote(query_en)}&sortType=default&page=1&pageSize=10")
        headers = {
            "User-Agent": "AliExpress/8.50.0 (Android 11; Mobile)",
            "Accept": "application/json",
            "bx-v": "2.5.14",
        }
        resp = requests.get(url, headers=headers, timeout=20)
        if resp.status_code == 200:
            data = resp.json()
            items = (data.get("result", {}).get("resultList") or
                     data.get("data", {}).get("products") or [])
            prices = []
            for item in items[:10]:
                price = (
                    item.get("price") or
                    item.get("salePrice") or
                    (item.get("skuPriceList") or [{}])[0].get("skuVal", {}).get(
                        "skuAmount", {}).get("value") or
                    item.get("itemInfo", {}).get("price")
                )
                if price:
                    try:
                        p = float(str(price).replace(",", "").replace("$", ""))
                        if 0.5 <= p <= 2000:
                            prices.append(p)
                    except (ValueError, TypeError):
                        pass
            if prices:
                result = sorted(prices)[len(prices) // 4]
                logger.info(f"AliExpress mobile API [{query_en[:30]}]: ${result:.2f}")
                return result
    except Exception as e:
        logger.debug(f"AliExpress mobile API failed: {e}")

    # روش ۲: Scrape HTML موبایل
    try:
        url2 = (f"https://www.aliexpress.com/wholesale"
                f"?SearchText={requests.utils.quote(query_en)}&SortType=total_tranpro_desc")
        headers2 = {
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept": "text/html,application/xhtml+xml",
        }
        resp2 = requests.get(url2, headers=headers2, timeout=20)
        if resp2.status_code == 200:
            text = resp2.text
            patterns = [
                r'"formatedPrice":\s*"US\s*\$\s*([\d]+\.[\d]{1,2})"',
                r'US\s*\$\s*([\d]+\.[\d]{1,2})',
                r'"price":\s*"([\d]+\.[\d]{1,2})"',
                r'"minAmount":\s*"([\d]+\.[\d]{1,2})"',
            ]
            prices = []
            for pat in patterns:
                for m in re.findall(pat, text):
                    try:
                        p = float(m)
                        if 0.5 <= p <= 2000:
                            prices.append(p)
                    except (ValueError, TypeError):
                        pass
                if len(prices) >= 3:
                    break
            if prices:
                result = sorted(prices)[len(prices) // 4]
                logger.info(f"AliExpress scrape [{query_en[:30]}]: ${result:.2f}")
                return result
    except Exception as e:
        logger.debug(f"AliExpress scrape failed: {e}")

    logger.warning(f"AliExpress: no price found for [{query_en[:30]}]")
    return None


# ═══════════════════════════════════════
# قیمت خارجی — با ترتیب اولویت
# ═══════════════════════════════════════
def get_foreign_price(product: dict) -> tuple[Optional[float], str]:
    """
    دریافت قیمت خارجی با fallback چندلایه
    خروجی: (قیمت دلار, منبع) یا (None, "")
    """
    ebay_query = product.get("ebay_query", product["query_en"])

    # ۱. eBay (بهترین گزینه از GitHub Actions)
    ebay_price = get_ebay_price(product["query_en"], ebay_query)
    if ebay_price:
        return ebay_price, "eBay"

    # ۲. AliExpress direct
    ali_price = get_aliexpress_price(product["query_en"])
    if ali_price:
        return ali_price, "AliExpress"

    # ۳. Fallback: قیمت دستی واقعی
    fallback = product.get("ali_price_usd_fallback")
    if fallback:
        logger.info(f"Using manual fallback price for [{product['name']}]: ${fallback}")
        return float(fallback), "قیمت پایه"

    return None, ""


# ═══════════════════════════════════════
# ترب ایران
# ═══════════════════════════════════════
def get_torob_price(query_fa: str) -> Optional[float]:
    """قیمت از ترب — قیمت‌یاب ایران | خروجی: تومان"""
    url = f"https://torob.com/api/v4/search/product/?query={requests.utils.quote(query_fa)}&page=0&sort=price_asc"
    try:
        resp = requests.get(url, headers={**_get_headers(), "Accept": "application/json"}, timeout=20)
        if resp.status_code == 200:
            data = resp.json()
            prices = []
            for item in data.get("results", [])[:10]:
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
    """قیمت از دیجی‌کالا | خروجی: تومان"""
    url = f"https://api.digikala.com/v1/search/?q={requests.utils.quote(query_fa)}&sort=1"
    try:
        resp = requests.get(url, headers={**_get_headers(), "Accept": "application/json"}, timeout=25)
        if resp.status_code == 200:
            data = resp.json()
            prices = []
            for p in data.get("data", {}).get("products", [])[:8]:
                sp = p.get("price", {}).get("selling_price")
                if sp and 10_000 < sp < 5_000_000_000:
                    prices.append(sp / 10)  # ریال → تومان
            if prices:
                price = min(prices)
                logger.info(f"Digikala [{query_fa}]: {price:,} Toman")
                return float(price)
    except Exception as e:
        logger.error(f"Digikala error: {e}")
    return None


# ═══════════════════════════════════════
# دیوار اصفهان
# ═══════════════════════════════════════
def get_divar_isfahan_price(query_fa: str) -> Optional[float]:
    """قیمت از دیوار اصفهان | خروجی: تومان"""
    url = f"https://api.divar.ir/v8/search/isfahan?q={requests.utils.quote(query_fa)}&sort=sort_date"
    try:
        resp = requests.get(url, headers={**_get_headers(), "Accept": "application/json"}, timeout=20)
        if resp.status_code == 200:
            data = resp.json()
            posts = data.get("widget_list", []) or data.get("list_widgets", [])
            prices = []
            for post in posts[:20]:
                desc = str(post)
                for m in re.finditer(r'(\d[\d,]{4,})', desc):
                    try:
                        val = int(m.group(1).replace(",", ""))
                        if 100_000 < val < 5_000_000_000:
                            prices.append(val)
                            break
                    except (ValueError, TypeError):
                        pass
            if prices:
                prices.sort()
                median = prices[len(prices) // 2]
                logger.info(f"Divar Isfahan [{query_fa}]: {median:,} Toman")
                return float(median)
    except Exception as e:
        logger.error(f"Divar error: {e}")
    return None


# ═══════════════════════════════════════
# قیمت نهایی هر کالا
# ═══════════════════════════════════════
def get_all_prices(product: dict) -> dict:
    """
    دریافت تمام قیمت‌ها برای یک کالا
    خروجی: دیکشنری قیمت‌ها با source مشخص
    استراتژی ایران: Torob → Digikala → iran_price_toman_fallback
    استراتژی خارجی: eBay → AliExpress → ali_price_usd_fallback
    """
    # قیمت خارجی (eBay → AliExpress → Fallback)
    time.sleep(random.uniform(1.0, 2.5))
    ali_usd, foreign_source = get_foreign_price(product)
    time.sleep(random.uniform(0.8, 1.8))

    # قیمت ایران (Torob → Digikala → iran_price_toman_fallback)
    iran_source = "آنلاین ایران"
    torob = get_torob_price(product["query_fa"])
    if not torob:
        time.sleep(random.uniform(0.5, 1.2))
        torob = get_digikala_price(product["query_fa"])

    # اگر scraping کار نکرد، از fallback استفاده می‌کنیم
    if not torob:
        fallback_iran = product.get("iran_price_toman_fallback")
        if fallback_iran:
            torob = float(fallback_iran)
            iran_source = "قیمت پایه ایران"
            logger.info(f"[{product['id']}] Iran price fallback: {torob:,.0f} تومان")
        else:
            iran_source = "نامشخص"
            logger.warning(f"[{product['id']}] No Iran price available (scraping failed, no fallback)")

    # دیوار اصفهان (جداگانه)
    time.sleep(random.uniform(0.8, 1.5))
    divar_isf = get_divar_isfahan_price(product["query_fa"])

    # اگر دیوار هم بلاک بود، از iran_price_toman_fallback با کسر ۱۵٪ استفاده می‌کنیم
    # (بازار دست دوم معمولاً ۱۰-۲۰٪ ارزان‌تر از آنلاین است)
    if not divar_isf and torob:
        divar_isf = torob * 0.85
        logger.info(f"[{product['id']}] Isfahan fallback (85% of Iran online): {divar_isf:,.0f} تومان")

    return {
        "aliexpress_usd": ali_usd,
        "foreign_source": foreign_source,
        "iran_online_toman": torob,
        "iran_source": iran_source,
        "isfahan_toman": divar_isf,
    }
