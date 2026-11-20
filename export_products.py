"""
export_products.py — محصولات صادراتی ایران
این محصولات در ایران ارزان هستند و در بازارهای خارجی گران‌تر فروخته می‌شوند.

ساختار هر محصول:
  id, name, category
  iran_price_toman_fallback: قیمت عمده‌فروشی در ایران (تومان)
  target_markets: بازارهای هدف با قیمت تخمینی (USD)
  amazon_uk_query, amazon_de_query, noon_query: کوئری سرچ
  unit_weight_kg: وزن برای محاسبه حمل
  hs_code_hint: کد گمرکی تقریبی (برای اطلاع)
"""

# هزینه‌های صادرات به هر کشور/منطقه (USD per kg + % duty at destination)
EXPORT_COSTS = {
    "UAE": {
        "name": "امارات",
        "flag": "🇦🇪",
        "shipping_usd_per_kg": 3.5,   # حمل هوایی ایران→دبی
        "min_shipping_usd": 8.0,
        "import_duty_pct": 0.05,       # گمرک امارات ۵٪ (FTA با برخی کالاها ۰٪)
        "currency": "AED",
        "usd_rate": 3.67,
    },
    "Iraq": {
        "name": "عراق",
        "flag": "🇮🇶",
        "shipping_usd_per_kg": 2.0,    # زمینی/هوایی ایران→بغداد/اربیل
        "min_shipping_usd": 5.0,
        "import_duty_pct": 0.05,        # گمرک عراق متفاوت — ۵٪ تخمین
        "currency": "USD",
        "usd_rate": 1.0,
    },
    "Afghanistan": {
        "name": "افغانستان",
        "flag": "🇦🇫",
        "shipping_usd_per_kg": 2.5,
        "min_shipping_usd": 5.0,
        "import_duty_pct": 0.04,
        "currency": "USD",
        "usd_rate": 1.0,
    },
    "UK": {
        "name": "انگلیس",
        "flag": "🇬🇧",
        "shipping_usd_per_kg": 12.0,   # DHL/FedEx ایران→UK
        "min_shipping_usd": 25.0,
        "import_duty_pct": 0.12,        # UK import duty ~12% average
        "currency": "GBP",
        "usd_rate": 0.79,
    },
    "Germany": {
        "name": "آلمان",
        "flag": "🇩🇪",
        "shipping_usd_per_kg": 11.0,
        "min_shipping_usd": 22.0,
        "import_duty_pct": 0.10,        # EU customs ~10%
        "currency": "EUR",
        "usd_rate": 0.92,
    },
    "USA": {
        "name": "آمریکا",
        "flag": "🇺🇸",
        "shipping_usd_per_kg": 15.0,
        "min_shipping_usd": 30.0,
        "import_duty_pct": 0.0,         # محصولات ایرانی تحریم دارند — فقط برای آگاهی
        "currency": "USD",
        "usd_rate": 1.0,
        "note": "⚠️ تحریم — فقط برای مقایسه قیمت",
    },
}

EXPORT_PRODUCTS = [

    # ═══════════════════════════════════════
    # محصولات کشاورزی و غذایی ایران
    # ═══════════════════════════════════════

    {
        "id": "saffron_1g",
        "name": "زعفران ۱ گرمی",
        "category": "کشاورزی",
        "iran_price_toman_fallback": 180_000,     # ~۱۸۰ هزار تومان/گرم (عمده خراسان)
        "unit_weight_kg": 0.005,                   # ۵ گرم بسته‌بندی با جعبه
        "target_markets": {
            "UAE":        {"price_usd": 12.0,  "source": "noon.com"},
            "UK":         {"price_usd": 15.0,  "source": "amazon.co.uk"},
            "Germany":    {"price_usd": 14.0,  "source": "amazon.de"},
            "Iraq":       {"price_usd": 8.0,   "source": "market"},
            "USA":        {"price_usd": 18.0,  "source": "amazon.com"},
        },
        "amazon_uk_query": "saffron 1g persian premium",
        "amazon_de_query": "Safran 1g persisch premium",
        "noon_query": "saffron persian 1g",
        "hs_code_hint": "0910.20",
    },
    {
        "id": "saffron_5g",
        "name": "زعفران ۵ گرمی",
        "category": "کشاورزی",
        "iran_price_toman_fallback": 850_000,     # ~۸۵۰ هزار تومان/۵گرم عمده
        "unit_weight_kg": 0.02,
        "target_markets": {
            "UAE":        {"price_usd": 50.0,  "source": "noon.com"},
            "UK":         {"price_usd": 65.0,  "source": "amazon.co.uk"},
            "Germany":    {"price_usd": 60.0,  "source": "amazon.de"},
            "Iraq":       {"price_usd": 35.0,  "source": "market"},
        },
        "amazon_uk_query": "saffron 5g persian luxury gift",
        "amazon_de_query": "Safran 5g persisch",
        "noon_query": "saffron persian 5g gift box",
        "hs_code_hint": "0910.20",
    },
    {
        "id": "pistachio_kg",
        "name": "پسته ایرانی (۱ کیلو)",
        "category": "کشاورزی",
        "iran_price_toman_fallback": 1_200_000,   # ~۱.۲ میلیون تومان/کیلو عمده
        "unit_weight_kg": 1.1,
        "target_markets": {
            "UAE":        {"price_usd": 18.0,  "source": "noon.com"},
            "UK":         {"price_usd": 22.0,  "source": "amazon.co.uk"},
            "Germany":    {"price_usd": 20.0,  "source": "amazon.de"},
            "Iraq":       {"price_usd": 12.0,  "source": "market"},
            "Afghanistan":{"price_usd": 10.0,  "source": "market"},
        },
        "amazon_uk_query": "iranian pistachio 1kg raw roasted",
        "amazon_de_query": "Pistazien Iran 1kg",
        "noon_query": "pistachio iranian 1kg",
        "hs_code_hint": "0802.51",
    },
    {
        "id": "dates_kg",
        "name": "خرمای مضافتی (۱ کیلو)",
        "category": "کشاورزی",
        "iran_price_toman_fallback": 350_000,    # ~۳۵۰ هزار تومان/کیلو مضافتی عمده
        "unit_weight_kg": 1.1,
        "target_markets": {
            "UAE":        {"price_usd": 8.0,   "source": "noon.com"},
            "UK":         {"price_usd": 12.0,  "source": "amazon.co.uk"},
            "Germany":    {"price_usd": 10.0,  "source": "amazon.de"},
            "Iraq":       {"price_usd": 6.0,   "source": "market"},
            "Afghanistan":{"price_usd": 5.0,   "source": "market"},
        },
        "amazon_uk_query": "medjool dates 1kg iranian mazafati",
        "amazon_de_query": "Datteln 1kg Mazafati Iran",
        "noon_query": "mazafati dates iran 1kg",
        "hs_code_hint": "0804.10",
    },
    {
        "id": "dried_fig_500g",
        "name": "انجیر خشک (۵۰۰ گرم)",
        "category": "کشاورزی",
        "iran_price_toman_fallback": 180_000,    # ~۱۸۰ هزار تومان/۵۰۰گرم استهبان
        "unit_weight_kg": 0.6,
        "target_markets": {
            "UAE":        {"price_usd": 7.0,   "source": "noon.com"},
            "UK":         {"price_usd": 9.0,   "source": "amazon.co.uk"},
            "Germany":    {"price_usd": 8.0,   "source": "amazon.de"},
            "Iraq":       {"price_usd": 5.0,   "source": "market"},
        },
        "amazon_uk_query": "dried figs 500g turkish iranian",
        "amazon_de_query": "getrocknete Feigen 500g",
        "noon_query": "dried figs 500g",
        "hs_code_hint": "0804.20",
    },
    {
        "id": "rosewater_500ml",
        "name": "گلاب ۵۰۰ میلی",
        "category": "کشاورزی",
        "iran_price_toman_fallback": 80_000,     # ~۸۰ هزار تومان/۵۰۰ml گلاب قمصر
        "unit_weight_kg": 0.6,
        "target_markets": {
            "UAE":        {"price_usd": 6.0,   "source": "noon.com"},
            "UK":         {"price_usd": 8.0,   "source": "amazon.co.uk"},
            "Germany":    {"price_usd": 7.0,   "source": "amazon.de"},
            "Iraq":       {"price_usd": 4.0,   "source": "market"},
            "Afghanistan":{"price_usd": 3.5,   "source": "market"},
        },
        "amazon_uk_query": "rosewater 500ml persian cooking baking",
        "amazon_de_query": "Rosenwasser 500ml persisch",
        "noon_query": "rosewater persian 500ml",
        "hs_code_hint": "3301.29",
    },
    {
        "id": "barberry_200g",
        "name": "زرشک ۲۰۰ گرم",
        "category": "کشاورزی",
        "iran_price_toman_fallback": 120_000,    # ~۱۲۰ هزار تومان/۲۰۰g زرشک بیرجند
        "unit_weight_kg": 0.25,
        "target_markets": {
            "UAE":        {"price_usd": 5.0,   "source": "noon.com"},
            "UK":         {"price_usd": 7.0,   "source": "amazon.co.uk"},
            "Germany":    {"price_usd": 6.0,   "source": "amazon.de"},
            "Iraq":       {"price_usd": 4.0,   "source": "market"},
        },
        "amazon_uk_query": "barberry dried zereshk 200g persian",
        "amazon_de_query": "Berberitzen getrocknet 200g persisch",
        "noon_query": "zereshk barberry persian 200g",
        "hs_code_hint": "0813.40",
    },
    {
        "id": "dried_mulberry_500g",
        "name": "توت خشک (۵۰۰ گرم)",
        "category": "کشاورزی",
        "iran_price_toman_fallback": 150_000,    # ~۱۵۰ هزار تومان
        "unit_weight_kg": 0.6,
        "target_markets": {
            "UAE":        {"price_usd": 6.0,   "source": "noon.com"},
            "UK":         {"price_usd": 8.0,   "source": "amazon.co.uk"},
            "Germany":    {"price_usd": 7.5,   "source": "amazon.de"},
            "Iraq":       {"price_usd": 4.0,   "source": "market"},
        },
        "amazon_uk_query": "dried mulberry 500g white persian",
        "amazon_de_query": "getrocknete Maulbeeren 500g",
        "noon_query": "dried mulberry 500g",
        "hs_code_hint": "0813.40",
    },

    # ═══════════════════════════════════════
    # صنایع‌دستی و هدایا
    # ═══════════════════════════════════════

    {
        "id": "copper_bowl",
        "name": "کاسه مسی دست‌ساز",
        "category": "صنایع‌دستی",
        "iran_price_toman_fallback": 350_000,    # ~۳۵۰ هزار تومان اصفهان/کاشان
        "unit_weight_kg": 0.4,
        "target_markets": {
            "UAE":        {"price_usd": 25.0,  "source": "noon.com"},
            "UK":         {"price_usd": 35.0,  "source": "amazon.co.uk"},
            "Germany":    {"price_usd": 30.0,  "source": "amazon.de"},
        },
        "amazon_uk_query": "persian copper bowl handmade decorative",
        "amazon_de_query": "persische Kupferschale handgemacht",
        "noon_query": "copper bowl persian handmade",
        "hs_code_hint": "7418.19",
    },
    {
        "id": "persian_carpet_small",
        "name": "فرش دستبافت کوچک (۶۰×۹۰)",
        "category": "صنایع‌دستی",
        "iran_price_toman_fallback": 8_000_000,   # ~۸ میلیون تومان تبریز/اصفهان
        "unit_weight_kg": 2.5,
        "target_markets": {
            "UAE":        {"price_usd": 180.0, "source": "noon.com"},
            "UK":         {"price_usd": 250.0, "source": "amazon.co.uk"},
            "Germany":    {"price_usd": 220.0, "source": "amazon.de"},
        },
        "amazon_uk_query": "persian rug handmade 60x90 wool",
        "amazon_de_query": "persischer Teppich handgeknüpft 60x90",
        "noon_query": "persian carpet handmade small wool",
        "hs_code_hint": "5701.10",
    },

    # ═══════════════════════════════════════
    # غذای حیوانات خانگی
    # (ایران تولیدکننده بزرگ خوراک دام — قیمت پایین‌تر از اروپا)
    # ═══════════════════════════════════════

    {
        "id": "cat_food_dry_2kg",
        "name": "غذای خشک گربه ۲ کیلو",
        "category": "حیوانات‌خانگی",
        "iran_price_toman_fallback": 350_000,    # ~۳۵۰ هزار تومان (مارک‌های ایرانی مثل RC ایرانی)
        "unit_weight_kg": 2.2,
        "target_markets": {
            "UAE":        {"price_usd": 12.0,  "source": "noon.com"},
            "Iraq":       {"price_usd": 8.0,   "source": "market"},
            "Afghanistan":{"price_usd": 7.0,   "source": "market"},
            "UK":         {"price_usd": 18.0,  "source": "amazon.co.uk"},
            "Germany":    {"price_usd": 16.0,  "source": "amazon.de"},
        },
        "amazon_uk_query": "dry cat food 2kg adult chicken",
        "amazon_de_query": "Trockenfutter Katze 2kg adult",
        "noon_query": "dry cat food 2kg adult",
        "hs_code_hint": "2309.10",
    },
    {
        "id": "dog_food_dry_3kg",
        "name": "غذای خشک سگ ۳ کیلو",
        "category": "حیوانات‌خانگی",
        "iran_price_toman_fallback": 420_000,    # ~۴۲۰ هزار تومان
        "unit_weight_kg": 3.2,
        "target_markets": {
            "UAE":        {"price_usd": 15.0,  "source": "noon.com"},
            "Iraq":       {"price_usd": 10.0,  "source": "market"},
            "Afghanistan":{"price_usd": 8.0,   "source": "market"},
            "UK":         {"price_usd": 22.0,  "source": "amazon.co.uk"},
            "Germany":    {"price_usd": 20.0,  "source": "amazon.de"},
        },
        "amazon_uk_query": "dry dog food 3kg adult medium",
        "amazon_de_query": "Hundefutter trocken 3kg adult",
        "noon_query": "dry dog food 3kg adult",
        "hs_code_hint": "2309.10",
    },
    {
        "id": "cat_litter_5kg",
        "name": "خاک گربه (بنتونیت) ۵ کیلو",
        "category": "حیوانات‌خانگی",
        "iran_price_toman_fallback": 180_000,    # ~۱۸۰ هزار تومان (ایران تولیدکننده بنتونیت)
        "unit_weight_kg": 5.5,
        "target_markets": {
            "UAE":        {"price_usd": 8.0,   "source": "noon.com"},
            "Iraq":       {"price_usd": 6.0,   "source": "market"},
            "Afghanistan":{"price_usd": 5.0,   "source": "market"},
            "UK":         {"price_usd": 12.0,  "source": "amazon.co.uk"},
            "Germany":    {"price_usd": 11.0,  "source": "amazon.de"},
        },
        "amazon_uk_query": "clumping cat litter bentonite 5kg",
        "amazon_de_query": "Katzenstreu Klumpstreu Bentonit 5kg",
        "noon_query": "cat litter clumping 5kg bentonite",
        "hs_code_hint": "2508.10",
    },
    {
        "id": "cat_food_wet_pack",
        "name": "غذای مرطوب گربه (۱۲ عددی)",
        "category": "حیوانات‌خانگی",
        "iran_price_toman_fallback": 280_000,    # ~۲۸۰ هزار تومان (۱۲ پاکت ۸۵g)
        "unit_weight_kg": 1.3,
        "target_markets": {
            "UAE":        {"price_usd": 10.0,  "source": "noon.com"},
            "Iraq":       {"price_usd": 7.0,   "source": "market"},
            "UK":         {"price_usd": 15.0,  "source": "amazon.co.uk"},
            "Germany":    {"price_usd": 14.0,  "source": "amazon.de"},
        },
        "amazon_uk_query": "wet cat food pouches 12 pack adult",
        "amazon_de_query": "Nassfutter Katze 12 Stück",
        "noon_query": "wet cat food pouches 12 pack",
        "hs_code_hint": "2309.10",
    },
    {
        "id": "dog_treat_200g",
        "name": "تشویقی سگ (۲۰۰ گرم)",
        "category": "حیوانات‌خانگی",
        "iran_price_toman_fallback": 120_000,    # ~۱۲۰ هزار تومان
        "unit_weight_kg": 0.25,
        "target_markets": {
            "UAE":        {"price_usd": 6.0,   "source": "noon.com"},
            "Iraq":       {"price_usd": 4.0,   "source": "market"},
            "UK":         {"price_usd": 9.0,   "source": "amazon.co.uk"},
            "Germany":    {"price_usd": 8.0,   "source": "amazon.de"},
        },
        "amazon_uk_query": "dog treats training 200g chicken",
        "amazon_de_query": "Hundesnacks Training 200g",
        "noon_query": "dog treats training snacks 200g",
        "hs_code_hint": "2309.10",
    },

    # ═══════════════════════════════════════
    # مواد صنعتی / ساختمانی (ایران ارزان دارد)
    # ═══════════════════════════════════════

    {
        "id": "ceramic_tile_sqm",
        "name": "کاشی سرامیک (هر متر مربع)",
        "category": "ساختمانی",
        "iran_price_toman_fallback": 220_000,    # ~۲۲۰ هزار تومان/m² (کارخانه‌های ایران)
        "unit_weight_kg": 18.0,
        "target_markets": {
            "UAE":        {"price_usd": 12.0,  "source": "market"},
            "Iraq":       {"price_usd": 8.0,   "source": "market"},
            "Afghanistan":{"price_usd": 7.0,   "source": "market"},
        },
        "amazon_uk_query": "ceramic floor tile 60x60 box",
        "amazon_de_query": "Keramikfliesen 60x60 Karton",
        "noon_query": "ceramic floor tile 60x60",
        "hs_code_hint": "6908.90",
    },
    {
        "id": "piping_ppr_meter",
        "name": "لوله PPR (هر متر)",
        "category": "ساختمانی",
        "iran_price_toman_fallback": 45_000,    # ~۴۵ هزار تومان/m لوله ۲۵mm
        "unit_weight_kg": 0.3,
        "target_markets": {
            "UAE":        {"price_usd": 3.5,   "source": "market"},
            "Iraq":       {"price_usd": 2.5,   "source": "market"},
            "Afghanistan":{"price_usd": 2.0,   "source": "market"},
        },
        "amazon_uk_query": "ppr pipe 25mm per meter plumbing",
        "amazon_de_query": "PPR Rohr 25mm Sanitär",
        "noon_query": "ppr pipe 25mm",
        "hs_code_hint": "3917.32",
    },
]
