"""
لیست کالاهای رصد روزانه — ۴۰ کالا در ۸ دسته
هر کالا دارای: نام فارسی، کوئری انگلیسی برای سایت‌های خارجی، کوئری فارسی برای سایت‌های ایرانی
ali_price_usd_fallback: قیمت واقعی AliExpress (به‌روز شده آذر ۱۴۰۵ / نوامبر ۲۰۲۶) — fallback وقتی scraping کار نمی‌کند
iran_price_toman_fallback: قیمت بازار ایران به تومان (آذر ۱۴۰۵ — دلار ۲۷۰ هزار تومان) — fallback وقتی Torob/Digikala بلاک است
ebay_query: کوئری بهینه‌شده برای جستجو در eBay
"""

PRODUCTS = [
    # ───── الکترونیک و گجت ─────
    {
        "id": "bt_earphone",
        "name": "هندزفری بلوتوث",
        "query_en": "bluetooth earphone wireless",
        "ebay_query": "bluetooth earphone wireless earbud TWS",
        "query_fa": "هندزفری بلوتوث",
        "category": "الکترونیک",
        "ali_price_usd_fallback": 4.5,          # TWS earbuds basic on AliExpress
        "iran_price_toman_fallback": 850_000,    # هندزفری بلوتوث معمولی در ایران ~۸۵۰ هزار تومان
    },
    {
        "id": "smartwatch",
        "name": "ساعت هوشمند",
        "query_en": "smartwatch fitness band",
        "ebay_query": "smartwatch fitness tracker heart rate",
        "query_fa": "ساعت هوشمند",
        "category": "الکترونیک",
        "ali_price_usd_fallback": 12.0,          # basic smartwatch / fitness band
        "iran_price_toman_fallback": 2_800_000,  # ساعت هوشمند ارزان در ایران ~۲.۸ میلیون تومان
    },
    {
        "id": "powerbank",
        "name": "پاوربانک ۱۰۰۰۰",
        "query_en": "power bank 10000mah",
        "ebay_query": "power bank 10000mah portable charger",
        "query_fa": "پاوربانک ۱۰۰۰۰",
        "category": "الکترونیک",
        "ali_price_usd_fallback": 8.0,           # 10000mAh powerbank
        "iran_price_toman_fallback": 1_800_000,  # پاوربانک ۱۰۰۰۰ در ایران ~۱.۸ میلیون تومان
    },
    {
        "id": "usb_hub",
        "name": "هاب USB-C",
        "query_en": "usb c hub 7 in 1",
        "ebay_query": "usb c hub 7 in 1 multiport adapter",
        "query_fa": "هاب USB",
        "category": "الکترونیک",
        "ali_price_usd_fallback": 9.5,           # 7-in-1 USB-C hub
        "iran_price_toman_fallback": 2_200_000,  # هاب USB-C در ایران ~۲.۲ میلیون تومان
    },
    {
        "id": "webcam",
        "name": "وب‌کم ۱۰۸۰p",
        "query_en": "webcam 1080p hd",
        "ebay_query": "webcam 1080p hd computer camera",
        "query_fa": "وب کم",
        "category": "الکترونیک",
        "ali_price_usd_fallback": 11.0,          # 1080p webcam with microphone
        "iran_price_toman_fallback": 2_500_000,  # وب‌کم ۱۰۸۰p در ایران ~۲.۵ میلیون تومان
    },
    {
        "id": "rgb_mouse",
        "name": "ماوس گیمینگ RGB",
        "query_en": "rgb gaming mouse",
        "ebay_query": "rgb gaming mouse wired optical",
        "query_fa": "ماوس گیمینگ",
        "category": "الکترونیک",
        "ali_price_usd_fallback": 7.0,           # RGB gaming mouse wired
        "iran_price_toman_fallback": 1_600_000,  # ماوس گیمینگ ارزان در ایران ~۱.۶ میلیون تومان
    },
    {
        "id": "mechanical_kb",
        "name": "کیبورد مکانیکال",
        "query_en": "mechanical keyboard gaming",
        "ebay_query": "mechanical keyboard gaming rgb tenkeyless",
        "query_fa": "کیبورد مکانیکال",
        "category": "الکترونیک",
        "ali_price_usd_fallback": 25.0,          # mechanical keyboard basic
        "iran_price_toman_fallback": 7_500_000,  # کیبورد مکانیکال ارزان در ایران ~۷.۵ میلیون تومان
    },
    {
        "id": "phone_holder",
        "name": "هولدر موبایل ماشین",
        "query_en": "car phone holder magnetic",
        "ebay_query": "car phone mount magnetic dashboard",
        "query_fa": "هولدر موبایل ماشین",
        "category": "الکترونیک",
        "ali_price_usd_fallback": 2.5,           # magnetic car phone holder
        "iran_price_toman_fallback": 350_000,    # هولدر موبایل ماشینی در ایران ~۳۵۰ هزار تومان
    },

    # ───── لوازم خانگی و آشپزخانه ─────
    {
        "id": "air_purifier",
        "name": "دستگاه تصفیه هوا",
        "query_en": "air purifier hepa filter small",
        "ebay_query": "air purifier hepa filter desktop room",
        "query_fa": "تصفیه هوا",
        "category": "خانگی",
        "ali_price_usd_fallback": 28.0,          # desktop HEPA air purifier
        "iran_price_toman_fallback": 9_500_000,  # تصفیه هوا رومیزی در ایران ~۹.۵ میلیون تومان
    },
    {
        "id": "electric_kettle",
        "name": "کتری برقی",
        "query_en": "electric kettle 1.7l stainless",
        "ebay_query": "electric kettle 1.7l stainless steel",
        "query_fa": "کتری برقی",
        "category": "خانگی",
        "ali_price_usd_fallback": 14.0,          # 1.7L stainless kettle
        "iran_price_toman_fallback": 2_800_000,  # کتری برقی استیل در ایران ~۲.۸ میلیون تومان
    },
    {
        "id": "food_scale",
        "name": "ترازوی آشپزخانه",
        "query_en": "digital kitchen scale 5kg",
        "ebay_query": "digital kitchen food scale 5kg lcd",
        "query_fa": "ترازوی آشپزخانه",
        "category": "خانگی",
        "ali_price_usd_fallback": 5.5,           # digital kitchen scale
        "iran_price_toman_fallback": 850_000,    # ترازوی آشپزخانه دیجیتال در ایران ~۸۵۰ هزار تومان
    },
    {
        "id": "vacuum_mini",
        "name": "جاروبرقی کوچک",
        "query_en": "mini vacuum cleaner handheld",
        "ebay_query": "handheld mini vacuum cleaner cordless",
        "query_fa": "جاروبرقی کوچک",
        "category": "خانگی",
        "ali_price_usd_fallback": 18.0,          # cordless handheld vacuum
        "iran_price_toman_fallback": 4_500_000,  # جاروبرقی دستی شارژی در ایران ~۴.۵ میلیون تومان
    },
    {
        "id": "led_strip",
        "name": "نوار LED هوشمند ۵متر",
        "query_en": "smart led strip light 5m rgb",
        "ebay_query": "smart led strip light 5m rgb wifi app",
        "query_fa": "نوار ال ای دی",
        "category": "خانگی",
        "ali_price_usd_fallback": 8.0,           # 5m smart RGB LED strip
        "iran_price_toman_fallback": 1_500_000,  # نوار LED هوشمند ۵ متری در ایران ~۱.۵ میلیون تومان
    },
    {
        "id": "towel_warmer",
        "name": "گرمکن حوله",
        "query_en": "towel warmer electric",
        "ebay_query": "electric towel warmer rack bathroom",
        "query_fa": "گرمکن حوله",
        "category": "خانگی",
        "ali_price_usd_fallback": 35.0,           # electric towel warmer rack
        "iran_price_toman_fallback": 12_000_000,  # گرمکن حوله برقی در ایران ~۱۲ میلیون تومان
    },

    # ───── ابزار و DIY ─────
    {
        "id": "drill_set",
        "name": "دریل و پیچ‌گوشتی برقی",
        "query_en": "cordless drill screwdriver set",
        "ebay_query": "cordless drill screwdriver set rechargeable",
        "query_fa": "دریل شارژی",
        "category": "ابزار",
        "ali_price_usd_fallback": 22.0,          # cordless drill set with bits
        "iran_price_toman_fallback": 6_500_000,  # دریل شارژی در ایران ~۶.۵ میلیون تومان
    },
    {
        "id": "multimeter",
        "name": "مولتی‌متر دیجیتال",
        "query_en": "digital multimeter professional",
        "ebay_query": "digital multimeter professional auto range",
        "query_fa": "مولتی متر",
        "category": "ابزار",
        "ali_price_usd_fallback": 12.0,          # digital multimeter
        "iran_price_toman_fallback": 1_800_000,  # مولتی‌متر دیجیتال در ایران ~۱.۸ میلیون تومان
    },
    {
        "id": "tool_set",
        "name": "جعبه‌ابزار کامل",
        "query_en": "tool kit set home repair",
        "ebay_query": "tool kit set home repair 46 piece",
        "query_fa": "جعبه ابزار",
        "category": "ابزار",
        "ali_price_usd_fallback": 20.0,          # complete home tool kit
        "iran_price_toman_fallback": 5_500_000,  # جعبه‌ابزار کامل در ایران ~۵.۵ میلیون تومان
    },
    {
        "id": "laser_level",
        "name": "تراز لیزری",
        "query_en": "laser level self leveling",
        "ebay_query": "laser level self leveling cross line",
        "query_fa": "تراز لیزری",
        "category": "ابزار",
        "ali_price_usd_fallback": 15.0,          # self-leveling laser level
        "iran_price_toman_fallback": 4_200_000,  # تراز لیزری در ایران ~۴.۲ میلیون تومان
    },

    # ───── پوشاک و کفش ─────
    {
        "id": "sneakers",
        "name": "کتانی ورزشی",
        "query_en": "running sneakers sport shoes",
        "ebay_query": "running sneakers men sport shoes lightweight",
        "query_fa": "کتانی ورزشی",
        "category": "پوشاک",
        "ali_price_usd_fallback": 18.0,          # running shoes basic
        "iran_price_toman_fallback": 4_500_000,  # کتانی ورزشی در ایران ~۴.۵ میلیون تومان
    },
    {
        "id": "leather_wallet",
        "name": "کیف پول چرمی",
        "query_en": "genuine leather wallet slim",
        "ebay_query": "genuine leather wallet slim men bifold",
        "query_fa": "کیف پول چرمی",
        "category": "پوشاک",
        "ali_price_usd_fallback": 6.0,           # slim leather wallet
        "iran_price_toman_fallback": 850_000,    # کیف پول چرمی در ایران ~۸۵۰ هزار تومان
    },
    {
        "id": "winter_jacket",
        "name": "کاپشن زمستانه",
        "query_en": "men winter jacket waterproof",
        "ebay_query": "men winter jacket waterproof quilted puffer",
        "query_fa": "کاپشن مردانه",
        "category": "پوشاک",
        "ali_price_usd_fallback": 30.0,           # winter puffer jacket
        "iran_price_toman_fallback": 12_000_000,  # کاپشن زمستانه در ایران ~۱۲ میلیون تومان
    },
    {
        "id": "sunglasses",
        "name": "عینک آفتابی",
        "query_en": "polarized sunglasses men",
        "ebay_query": "polarized sunglasses men uv400 driving",
        "query_fa": "عینک آفتابی",
        "category": "پوشاک",
        "ali_price_usd_fallback": 5.0,           # polarized sunglasses
        "iran_price_toman_fallback": 950_000,    # عینک آفتابی پلاریزه در ایران ~۹۵۰ هزار تومان
    },

    # ───── سلامت و زیبایی ─────
    {
        "id": "hair_dryer",
        "name": "سشوار حرفه‌ای",
        "query_en": "professional hair dryer 2000w",
        "ebay_query": "professional hair dryer 2000w ionic salon",
        "query_fa": "سشوار",
        "category": "زیبایی",
        "ali_price_usd_fallback": 16.0,          # 2000W hair dryer
        "iran_price_toman_fallback": 3_500_000,  # سشوار حرفه‌ای در ایران ~۳.۵ میلیون تومان
    },
    {
        "id": "electric_razor",
        "name": "ریش‌تراش برقی",
        "query_en": "electric shaver razor men",
        "ebay_query": "electric shaver razor men rechargeable rotary",
        "query_fa": "ریش تراش برقی",
        "category": "زیبایی",
        "ali_price_usd_fallback": 14.0,          # rotary electric shaver
        "iran_price_toman_fallback": 3_200_000,  # ریش‌تراش برقی در ایران ~۳.۲ میلیون تومان
    },
    {
        "id": "massage_gun",
        "name": "ماساژ گان عضلانی",
        "query_en": "massage gun deep tissue",
        "ebay_query": "massage gun deep tissue percussion muscle",
        "query_fa": "ماساژ گان",
        "category": "زیبایی",
        "ali_price_usd_fallback": 22.0,          # percussion massage gun
        "iran_price_toman_fallback": 7_500_000,  # ماساژ گان در ایران ~۷.۵ میلیون تومان
    },
    {
        "id": "blood_pressure",
        "name": "فشارسنج دیجیتال",
        "query_en": "digital blood pressure monitor",
        "ebay_query": "digital blood pressure monitor upper arm automatic",
        "query_fa": "فشارسنج دیجیتال",
        "category": "سلامت",
        "ali_price_usd_fallback": 16.0,          # upper arm BP monitor
        "iran_price_toman_fallback": 3_800_000,  # فشارسنج بازویی در ایران ~۳.۸ میلیون تومان
    },
    {
        "id": "oximeter",
        "name": "اکسیمتر",
        "query_en": "pulse oximeter fingertip",
        "ebay_query": "pulse oximeter fingertip blood oxygen spo2",
        "query_fa": "اکسیمتر",
        "category": "سلامت",
        "ali_price_usd_fallback": 5.0,           # fingertip pulse oximeter
        "iran_price_toman_fallback": 650_000,    # اکسیمتر انگشتی در ایران ~۶۵۰ هزار تومان
    },

    # ───── ورزش و فیتنس ─────
    {
        "id": "resistance_band",
        "name": "باند مقاومتی",
        "query_en": "resistance band set fitness",
        "ebay_query": "resistance band set fitness exercise loop",
        "query_fa": "باند مقاومتی ورزشی",
        "category": "ورزش",
        "ali_price_usd_fallback": 5.0,           # resistance band set 5 levels
        "iran_price_toman_fallback": 650_000,    # ست باند مقاومتی در ایران ~۶۵۰ هزار تومان
    },
    {
        "id": "yoga_mat",
        "name": "مت یوگا",
        "query_en": "yoga mat non slip 6mm",
        "ebay_query": "yoga mat non slip 6mm thick exercise fitness",
        "query_fa": "مت یوگا",
        "category": "ورزش",
        "ali_price_usd_fallback": 8.0,           # 6mm non-slip yoga mat
        "iran_price_toman_fallback": 1_200_000,  # مت یوگا ۶ میلی در ایران ~۱.۲ میلیون تومان
    },
    {
        "id": "jump_rope",
        "name": "طناب ورزشی دیجیتال",
        "query_en": "digital jump rope counter",
        "ebay_query": "digital jump rope counter timer skipping",
        "query_fa": "طناب ورزشی",
        "category": "ورزش",
        "ali_price_usd_fallback": 4.0,           # digital counter jump rope
        "iran_price_toman_fallback": 450_000,    # طناب ورزشی دیجیتال در ایران ~۴۵۰ هزار تومان
    },
    {
        "id": "water_bottle",
        "name": "بطری آب ورزشی",
        "query_en": "insulated stainless water bottle",
        "ebay_query": "insulated stainless steel water bottle 500ml",
        "query_fa": "بطری آب ورزشی",
        "category": "ورزش",
        "ali_price_usd_fallback": 6.0,           # insulated stainless bottle
        "iran_price_toman_fallback": 850_000,    # بطری آب استیل در ایران ~۸۵۰ هزار تومان
    },

    # ───── کودک و آموزشی ─────
    {
        "id": "lego_clone",
        "name": "لگو و بلوک ساختنی",
        "query_en": "building blocks lego compatible",
        "ebay_query": "building blocks lego compatible set children",
        "query_fa": "لگو",
        "category": "کودک",
        "ali_price_usd_fallback": 10.0,          # Lego-compatible block set large
        "iran_price_toman_fallback": 1_800_000,  # ست لگو بزرگ در ایران ~۱.۸ میلیون تومان
    },
    {
        "id": "slime_kit",
        "name": "کیت اسلایم",
        "query_en": "slime kit diy children",
        "ebay_query": "slime kit diy children making set",
        "query_fa": "کیت اسلایم",
        "category": "کودک",
        "ali_price_usd_fallback": 5.0,           # DIY slime kit with supplies
        "iran_price_toman_fallback": 650_000,    # کیت اسلایم در ایران ~۶۵۰ هزار تومان
    },
    {
        "id": "science_kit",
        "name": "کیت آزمایشگاهی کودک",
        "query_en": "science experiment kit children",
        "ebay_query": "science experiment kit children educational stem",
        "query_fa": "کیت آزمایشگاهی",
        "category": "کودک",
        "ali_price_usd_fallback": 12.0,          # children science experiment kit
        "iran_price_toman_fallback": 2_500_000,  # کیت آزمایشگاهی در ایران ~۲.۵ میلیون تومان
    },

    # ───── خودرو ─────
    {
        "id": "dash_cam",
        "name": "دوربین داشبورد",
        "query_en": "dash cam car 1080p",
        "ebay_query": "dash cam car 1080p front rear wifi",
        "query_fa": "دوربین خودرو داشبورد",
        "category": "خودرو",
        "ali_price_usd_fallback": 20.0,          # 1080p dashcam front+rear
        "iran_price_toman_fallback": 5_500_000,  # دوربین داشبورد در ایران ~۵.۵ میلیون تومان
    },
    {
        "id": "obd2_scanner",
        "name": "دیاگ OBD2",
        "query_en": "obd2 scanner bluetooth",
        "ebay_query": "obd2 scanner bluetooth car diagnostic elm327",
        "query_fa": "دیاگ خودرو",
        "category": "خودرو",
        "ali_price_usd_fallback": 5.0,           # ELM327 OBD2 bluetooth scanner
        "iran_price_toman_fallback": 850_000,    # دیاگ OBD2 بلوتوث در ایران ~۸۵۰ هزار تومان
    },
    {
        "id": "tire_inflator",
        "name": "تورم‌انداز تایر",
        "query_en": "portable tire inflator air pump",
        "ebay_query": "portable tire inflator air pump 12v car",
        "query_fa": "کمپرسور تایر خودرو",
        "category": "خودرو",
        "ali_price_usd_fallback": 18.0,          # portable 12V tire inflator
        "iran_price_toman_fallback": 4_500_000,  # کمپرسور تایر خودرو در ایران ~۴.۵ میلیون تومان
    },
    {
        "id": "car_polish",
        "name": "واکس و پولیش خودرو",
        "query_en": "car wax polish ceramic coating",
        "ebay_query": "car wax polish ceramic coating liquid spray",
        "query_fa": "واکس خودرو",
        "category": "خودرو",
        "ali_price_usd_fallback": 8.0,           # ceramic coating spray wax
        "iran_price_toman_fallback": 1_200_000,  # واکس سرامیک خودرو در ایران ~۱.۲ میلیون تومان
    },
    {
        "id": "seat_cover",
        "name": "روکش صندلی خودرو",
        "query_en": "car seat cover leather full set",
        "ebay_query": "car seat cover leather universal full set 5 seats",
        "query_fa": "روکش صندلی خودرو",
        "category": "خودرو",
        "ali_price_usd_fallback": 35.0,           # full set leather-look seat covers
        "iran_price_toman_fallback": 11_000_000,  # روکش کامل صندلی در ایران ~۱۱ میلیون تومان
    },
]
