# ایجنت قیمت‌یاب آربیتراژ 📦

## چه می‌کند؟
هر روز ساعت ۸ صبح تهران، ۴۰ کالا را اسکن می‌کند و دو جدول به تلگرام می‌فرستد:

1. **آربیتراژ بین‌المللی** — قیمت علی‌اکسپرس (با احتساب گمرک) در مقابل قیمت بازار ایران
2. **آربیتراژ داخلی** — قیمت آنلاین ایران در مقابل قیمت دیوار اصفهان

## ساختار فایل‌ها
```
price-arbitrage-agent/
├── main.py               # نقطه ورود
├── products.py           # لیست ۴۰ کالا در ۸ دسته
├── scrapers.py           # scraping از AliExpress، ترب، دیجی‌کالا، دیوار
├── arbitrage_engine.py   # محاسبه حاشیه سود
├── telegram_reporter.py  # فرمت‌بندی و ارسال گزارش
├── requirements.txt
└── .github/workflows/price-arbitrage.yml
```

## نصب و راه‌اندازی

### 1. ساخت Repository در GitHub
```
repo جدید: hsalehi10087/price-arbitrage-agent (private)
```

### 2. اضافه کردن Secrets
در `Settings > Secrets > Actions`:
```
TELEGRAM_BOT_TOKEN = [همان توکن بات Hossein_scanner_bot]
TELEGRAM_CHAT_ID   = [همان Chat ID قبلی]
```

### 3. Push کردن فایل‌ها
```bash
git init
git add .
git commit -m "Initial: Price Arbitrage Agent"
git remote add origin https://github.com/hsalehi10087/price-arbitrage-agent.git
git push -u origin main
```

### 4. اجرای دستی برای تست
در GitHub: `Actions > Price Arbitrage Daily Agent > Run workflow`

## دسته‌بندی کالاها
- 🔌 الکترونیک (۸ کالا)
- 🏠 خانگی (۶ کالا)
- 🔧 ابزار (۴ کالا)
- 👕 پوشاک (۴ کالا)
- 💊 سلامت و زیبایی (۵ کالا)
- 🏃 ورزش (۴ کالا)
- 🧒 کودک (۳ کالا)
- 🚗 خودرو (۵ کالا)

## نکته مهم
هزینه گمرک ۳۰٪ + ارسال ۵$ در محاسبه لحاظ شده.
قیمت دلار از bonbast.com (بازار آزاد) دریافت می‌شود.
