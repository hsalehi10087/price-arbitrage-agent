"""
تست API های جایگزین برای قیمت‌گیری — اجرا روی GitHub Actions
"""
import requests
import json
import re
import time

def test_amazon():
    """Amazon.com - scraping بدون key"""
    try:
        url = "https://www.amazon.com/s?k=bluetooth+earphone&ref=sr_pg_1"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept": "text/html,application/xhtml+xml",
        }
        r = requests.get(url, headers=headers, timeout=15)
        print(f"Amazon HTTP: {r.status_code} | size: {len(r.text)}")
        if r.status_code == 200:
            prices = re.findall(r'\$(\d+\.\d{2})', r.text[:50000])
            prices = [float(p) for p in prices if 1 <= float(p) <= 500]
            print(f"Amazon prices found: {sorted(prices)[:5]}")
            return True
    except Exception as e:
        print(f"Amazon FAIL: {e}")
    return False

def test_ebay():
    """eBay - رایگان بدون key"""
    try:
        url = "https://www.ebay.com/sch/i.html?_nkw=bluetooth+earphone&_sop=15&_ipg=10"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "Accept": "text/html",
        }
        r = requests.get(url, headers=headers, timeout=15)
        print(f"eBay HTTP: {r.status_code} | size: {len(r.text)}")
        if r.status_code == 200:
            prices = re.findall(r'[\$£](\d+\.\d{2})', r.text[:100000])
            prices = [float(p) for p in prices if 1 <= float(p) <= 500]
            print(f"eBay prices found: {sorted(prices)[:5]}")
            return True
    except Exception as e:
        print(f"eBay FAIL: {e}")
    return False

def test_torob():
    """Torob ایران"""
    try:
        url = "https://torob.com/api/v4/search/product/?query=هندزفری+بلوتوث&page=0&sort=price_asc"
        r = requests.get(url, headers={"Accept": "application/json"}, timeout=15)
        print(f"Torob HTTP: {r.status_code}")
        if r.status_code == 200:
            data = r.json()
            prices = [item.get("price1") for item in data.get("results", [])[:5] if item.get("price1")]
            print(f"Torob prices: {prices}")
            return True
    except Exception as e:
        print(f"Torob FAIL: {e}")
    return False

def test_digikala():
    """Digikala"""
    try:
        url = "https://api.digikala.com/v1/search/?q=هندزفری+بلوتوث&sort=1"
        r = requests.get(url, headers={"Accept": "application/json"}, timeout=15)
        print(f"Digikala HTTP: {r.status_code}")
        if r.status_code == 200:
            data = r.json()
            products = data.get("data", {}).get("products", [])[:3]
            prices = [p.get("price", {}).get("selling_price") for p in products if p.get("price")]
            print(f"Digikala prices: {prices}")
            return True
    except Exception as e:
        print(f"Digikala FAIL: {e}")
    return False

def test_divar():
    """Divar اصفهان"""
    try:
        url = "https://api.divar.ir/v8/search/isfahan?q=هندزفری+بلوتوث&sort=sort_date"
        r = requests.get(url, headers={"Accept": "application/json"}, timeout=15)
        print(f"Divar HTTP: {r.status_code} | size: {len(r.text)}")
        if r.status_code == 200:
            data = r.json()
            print(f"Divar keys: {list(data.keys())[:5]}")
            return True
    except Exception as e:
        print(f"Divar FAIL: {e}")
    return False

def test_aliexpress_api():
    """AliExpress از طریق API رسمی (DS API)"""
    try:
        url = "https://api.aliexpress.com/recommend/query"
        r = requests.get(url, timeout=10)
        print(f"AliExpress API: {r.status_code}")
    except Exception as e:
        print(f"AliExpress API FAIL: {e}")

    # روش ۲: از طریق aliexpress CDN
    try:
        url2 = "https://ae-goods.aliexpress.com/item_detail.htm?id=1005001234"
        r2 = requests.get(url2, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        print(f"AliExpress CDN: {r2.status_code}")
    except Exception as e:
        print(f"AliExpress CDN FAIL: {e}")

def test_bonbast():
    """نرخ دلار از bonbast"""
    try:
        r = requests.get("https://bonbast.com/", timeout=15, headers={"User-Agent": "Mozilla/5.0"})
        print(f"Bonbast HTTP: {r.status_code} | size: {len(r.text)}")
        if r.status_code == 200:
            m = re.search(r'"usd1":\s*"?(\d+)"?', r.text)
            print(f"USD rate: {m.group(1) if m else 'NOT FOUND'}")
        return r.status_code == 200
    except Exception as e:
        print(f"Bonbast FAIL: {e}")
    return False

if __name__ == "__main__":
    print("=" * 50)
    print("TEST: Amazon")
    test_amazon()
    time.sleep(2)

    print("\nTEST: eBay")
    test_ebay()
    time.sleep(2)

    print("\nTEST: Torob")
    test_torob()
    time.sleep(2)

    print("\nTEST: Digikala")
    test_digikala()
    time.sleep(2)

    print("\nTEST: Divar Isfahan")
    test_divar()
    time.sleep(2)

    print("\nTEST: AliExpress")
    test_aliexpress_api()
    time.sleep(2)

    print("\nTEST: Bonbast")
    test_bonbast()
    print("=" * 50)
