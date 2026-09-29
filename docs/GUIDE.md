# راهنمای README چرخشی

هر شب ساعت ۰۰:۰۵ به وقت تهران، GitHub Actions یکی از تم‌ها را انتخاب می‌کند و `README.md` را با آمار تازه‌ی گیت‌هاب از نو می‌سازد.

ترتیب تم‌ها: `terminal` ← `cinematic` ← `wow` ← `space-shooter` ← `cap-tip` ← `snake` ← دوباره از اول.

## عوض کردن اطلاعات

فقط فایل `profile.yml` را ویرایش کن و commit و push کن. چند دقیقه بعد README دوباره ساخته می‌شود.

- **پروژه‌های منتخب:** همان ریپوهای Pin‌شده‌ی پروفایلت هستند. در صفحه‌ی پروفایل گیت‌هاب روی «Customize your pins» بزن.
- **عکس:** اگر `photo` را خالی بگذاری، عکس پروفایل گیت‌هابت استفاده می‌شود. برای عکس دیگر، فایل را کنار `profile.yml` بگذار (مثلاً `photo.jpg`) و در `profile.yml` بنویس `photo: photo.jpg`.
- **`README.md`، `assets/`، `previews/` و `data/` را دستی ویرایش نکن**؛ هر شب بازنویسی می‌شوند.

## دیدن همه‌ی تم‌ها

پوشه‌ی `previews/` روی گیت‌هاب را باز کن. برای هر تم یک فایل هست که همیشه با آمار روز به‌روز است.

## فعال کردن یک تم خاص همین الان

1. در ریپو به تب **Actions** برو.
2. از سمت چپ **Daily README theme** را انتخاب کن.
3. روی **Run workflow** بزن، تم را انتخاب کن و دوباره **Run workflow** را بزن.

این تم تا اجرای شبانه‌ی بعدی می‌ماند.

## اگر عوض شدن روزانه متوقف شد

گیت‌هاب اجرای زمان‌بندی‌شده را در ریپوهایی که ۶۰ روز هیچ فعالیتی نداشته‌اند خاموش می‌کند. در تب **Actions**، workflow را باز کن و روی **Enable workflow** بزن.

## کامیت‌های ریپوهای خصوصی

برای اینکه کامیت‌های ریپوهای خصوصی هم در گراف و آمار شمرده شوند، در گیت‌هاب به **Settings ← Public profile** برو و گزینه‌ی **Include private contributions on my profile** را روشن کن.

اگر روزی API گیت‌هاب با توکن پیش‌فرض خطا داد، یک توکن شخصی با دسترسی `read:user` بساز و در **Settings ← Secrets and variables ← Actions** با نام `PROFILE_TOKEN` ذخیره کن.

## اجرا روی کامپیوتر خودت

```bash
pip install -r requirements-dev.txt
python -m pytest -q
python -m generator list
python -m generator build --offline --theme snake
```

`--offline` از آمار ذخیره‌شده در `data/github.json` استفاده می‌کند. برای گرفتن آمار تازه، یک توکن گیت‌هاب را در متغیر `GITHUB_TOKEN` بگذار و `--offline` را حذف کن.
