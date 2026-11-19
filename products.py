"""
لیست کالاهای رصد روزانه — ۴۰ کالا در ۸ دسته
هر کالا دارای: نام فارسی، کوئری انگلیسی برای سایت‌های خارجی، کوئری فارسی برای سایت‌های ایرانی
"""

PRODUCTS = [
    # ───── الکترونیک و گجت ─────
    {"id": "bt_earphone",   "name": "هندزفری بلوتوث",        "query_en": "bluetooth earphone wireless",    "query_fa": "هندزفری بلوتوث",        "category": "الکترونیک"},
    {"id": "smartwatch",    "name": "ساعت هوشمند",           "query_en": "smartwatch fitness band",        "query_fa": "ساعت هوشمند",            "category": "الکترونیک"},
    {"id": "powerbank",     "name": "پاوربانک ۱۰۰۰۰",        "query_en": "power bank 10000mah",           "query_fa": "پاوربانک ۱۰۰۰۰",         "category": "الکترونیک"},
    {"id": "usb_hub",       "name": "هاب USB-C",             "query_en": "usb c hub 7 in 1",              "query_fa": "هاب USB",                "category": "الکترونیک"},
    {"id": "webcam",        "name": "وب‌کم ۱۰۸۰p",           "query_en": "webcam 1080p hd",               "query_fa": "وب کم",                  "category": "الکترونیک"},
    {"id": "rgb_mouse",     "name": "ماوس گیمینگ RGB",        "query_en": "rgb gaming mouse",              "query_fa": "ماوس گیمینگ",            "category": "الکترونیک"},
    {"id": "mechanical_kb", "name": "کیبورد مکانیکال",        "query_en": "mechanical keyboard gaming",    "query_fa": "کیبورد مکانیکال",         "category": "الکترونیک"},
    {"id": "phone_holder",  "name": "هولدر موبایل ماشین",     "query_en": "car phone holder magnetic",     "query_fa": "هولدر موبایل ماشین",      "category": "الکترونیک"},

    # ───── لوازم خانگی و آشپزخانه ─────
    {"id": "air_purifier",  "name": "دستگاه تصفیه هوا",      "query_en": "air purifier hepa filter small", "query_fa": "تصفیه هوا",              "category": "خانگی"},
    {"id": "electric_kettle","name": "کتری برقی",             "query_en": "electric kettle 1.7l stainless", "query_fa": "کتری برقی",              "category": "خانگی"},
    {"id": "food_scale",    "name": "ترازوی آشپزخانه",        "query_en": "digital kitchen scale 5kg",     "query_fa": "ترازوی آشپزخانه",         "category": "خانگی"},
    {"id": "vacuum_mini",   "name": "جاروبرقی کوچک",          "query_en": "mini vacuum cleaner handheld",  "query_fa": "جاروبرقی کوچک",           "category": "خانگی"},
    {"id": "led_strip",     "name": "نوار LED هوشمند ۵متر",   "query_en": "smart led strip light 5m rgb",  "query_fa": "نوار ال ای دی",           "category": "خانگی"},
    {"id": "towel_warmer",  "name": "گرمکن حوله",             "query_en": "towel warmer electric",         "query_fa": "گرمکن حوله",              "category": "خانگی"},

    # ───── ابزار و DIY ─────
    {"id": "drill_set",     "name": "دریل و پیچ‌گوشتی برقی", "query_en": "cordless drill screwdriver set", "query_fa": "دریل شارژی",             "category": "ابزار"},
    {"id": "multimeter",    "name": "مولتی‌متر دیجیتال",      "query_en": "digital multimeter professional","query_fa": "مولتی متر",               "category": "ابزار"},
    {"id": "tool_set",      "name": "جعبه‌ابزار کامل",        "query_en": "tool kit set home repair",      "query_fa": "جعبه ابزار",              "category": "ابزار"},
    {"id": "laser_level",   "name": "تراز لیزری",             "query_en": "laser level self leveling",     "query_fa": "تراز لیزری",              "category": "ابزار"},

    # ───── پوشاک و کفش ─────
    {"id": "sneakers",      "name": "کتانی ورزشی",           "query_en": "running sneakers sport shoes",  "query_fa": "کتانی ورزشی",            "category": "پوشاک"},
    {"id": "leather_wallet","name": "کیف پول چرمی",           "query_en": "genuine leather wallet slim",   "query_fa": "کیف پول چرمی",            "category": "پوشاک"},
    {"id": "winter_jacket", "name": "کاپشن زمستانه",          "query_en": "men winter jacket waterproof",  "query_fa": "کاپشن مردانه",            "category": "پوشاک"},
    {"id": "sunglasses",    "name": "عینک آفتابی",            "query_en": "polarized sunglasses men",      "query_fa": "عینک آفتابی",             "category": "پوشاک"},

    # ───── سلامت و زیبایی ─────
    {"id": "hair_dryer",    "name": "سشوار حرفه‌ای",          "query_en": "professional hair dryer 2000w", "query_fa": "سشوار",                  "category": "زیبایی"},
    {"id": "electric_razor","name": "ریش‌تراش برقی",          "query_en": "electric shaver razor men",     "query_fa": "ریش تراش برقی",           "category": "زیبایی"},
    {"id": "massage_gun",   "name": "ماساژ گان عضلانی",       "query_en": "massage gun deep tissue",       "query_fa": "ماساژ گان",               "category": "زیبایی"},
    {"id": "blood_pressure","name": "فشارسنج دیجیتال",         "query_en": "digital blood pressure monitor","query_fa": "فشارسنج دیجیتال",          "category": "سلامت"},
    {"id": "oximeter",      "name": "اکسیمتر",                "query_en": "pulse oximeter fingertip",      "query_fa": "اکسیمتر",                "category": "سلامت"},

    # ───── ورزش و فیتنس ─────
    {"id": "resistance_band","name": "باند مقاومتی",           "query_en": "resistance band set fitness",   "query_fa": "باند مقاومتی ورزشی",      "category": "ورزش"},
    {"id": "yoga_mat",      "name": "مت یوگا",                "query_en": "yoga mat non slip 6mm",         "query_fa": "مت یوگا",                "category": "ورزش"},
    {"id": "jump_rope",     "name": "طناب ورزشی دیجیتال",     "query_en": "digital jump rope counter",     "query_fa": "طناب ورزشی",              "category": "ورزش"},
    {"id": "water_bottle",  "name": "بطری آب ورزشی",          "query_en": "insulated stainless water bottle","query_fa": "بطری آب ورزشی",           "category": "ورزش"},

    # ───── کودک و آموزشی ─────
    {"id": "lego_clone",    "name": "لگو و بلوک ساختنی",      "query_en": "building blocks lego compatible","query_fa": "لگو",                    "category": "کودک"},
    {"id": "slime_kit",     "name": "کیت اسلایم",             "query_en": "slime kit diy children",        "query_fa": "کیت اسلایم",              "category": "کودک"},
    {"id": "science_kit",   "name": "کیت آزمایشگاهی کودک",    "query_en": "science experiment kit children","query_fa": "کیت آزمایشگاهی",          "category": "کودک"},

    # ───── خودرو ─────
    {"id": "dash_cam",      "name": "دوربین داشبورد",         "query_en": "dash cam car 1080p",            "query_fa": "دوربین خودرو داشبورد",    "category": "خودرو"},
    {"id": "obd2_scanner",  "name": "دیاگ OBD2",              "query_en": "obd2 scanner bluetooth",        "query_fa": "دیاگ خودرو",              "category": "خودرو"},
    {"id": "tire_inflator", "name": "تورم‌انداز تایر",         "query_en": "portable tire inflator air pump","query_fa": "کمپرسور تایر خودرو",      "category": "خودرو"},
    {"id": "car_polish",    "name": "واکس و پولیش خودرو",     "query_en": "car wax polish ceramic coating","query_fa": "واکس خودرو",              "category": "خودرو"},
    {"id": "seat_cover",    "name": "روکش صندلی خودرو",       "query_en": "car seat cover leather full set","query_fa": "روکش صندلی خودرو",        "category": "خودرو"},
]
