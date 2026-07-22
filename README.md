# Kassa Bot — o'rnatish yo'riqnomasi

## 1-qadam: Bot yaratish
1. Telegram'da **@BotFather** ga yozing.
2. `/newbot` buyrug'ini yuboring, botga ism va username bering (username `bot` bilan tugashi kerak).
3. BotFather sizga **token** beradi (masalan: `123456:ABC-DEF...`). Uni saqlab qo'ying.

## 2-qadam: Telegram ID'laringizni olish
1. Telegram'da **@userinfobot** ga yozing (yoki "start" bosing).
2. U sizga raqamli **ID** beradi.
3. Akangizga ham shu botga yozishni so'rang, uning ID'ini oling.

## 3-qadam: kassa_bot.py faylini to'ldirish
Faylni oching va quyidagilarni almashtiring:

```python
BOT_TOKEN = "BU_YERGA_BOTFATHERDAN_OLGAN_TOKENNI_QOYING"

ALLOWED_USERS = {
    111111111: "Siz",
    222222222: "Akam",
}
```
— token va ikkalangizning haqiqiy ID/ismlaringizni yozing.

## 4-qadam: Serverga joylashtirish

Bot doim ishlab turishi uchun uni **doim yonib turadigan server**da ishga tushirish kerak (o'z kompyuteringizda emas, chunki uni o'chirsangiz bot ham to'xtaydi). Eng oson bepul variantlar:

### Variant A — Railway.app (eng oson)
1. https://railway.app saytida ro'yxatdan o'ting.
2. "New Project" → "Deploy from GitHub repo" (avval shu 3 ta faylni — `kassa_bot.py`, `requirements.txt`, va o'zi yaratadigan `kassa.db` — GitHub repo'ga joylashtiring).
3. Railway avtomatik `requirements.txt`ni o'qib kutubxonalarni o'rnatadi.
4. "Variables" bo'limida xohlasangiz `BOT_TOKEN`ni environment variable sifatida ham qo'yishingiz mumkin (xavfsizroq).
5. Deploy qilgach, bot doim ishlab turadi.

### Variant B — PythonAnywhere
1. https://www.pythonanywhere.com saytida bepul akkaunt oching.
2. Fayllarni yuklang, "Bash console" ochib:
   ```
   pip install --user -r requirements.txt
   python3 kassa_bot.py
   ```
3. Bepul tarifda konsolni doim ochiq ushlab bo'lmaydi — "Always-on task" uchun pullik tarifga o'tish kerak bo'lishi mumkin.

### Variant C — o'z VPS serveringiz
Agar VPS (masalan DigitalOcean, Timeweb) bo'lsa:
```bash
pip install -r requirements.txt
python3 kassa_bot.py
```
Uni doim ishlab turishi uchun `screen`, `tmux` yoki `systemd` service sifatida ishga tushiring.

## Botdan foydalanish
- `/start` — botni ishga tushirish, asosiy menyu chiqadi
- **➕ Kirim** — pul kiritish (summa, keyin izoh so'raladi)
- **➖ Chiqim** — xarajat yozish
- **💰 Balans** — joriy kassa qoldig'i, jami kirim/chiqim
- **📜 Oxirgi yozuvlar** — so'nggi 10 ta yozuv

## Xavfsizlik haqida
Botga faqat `ALLOWED_USERS` ro'yxatidagi ikki Telegram akkaunt yoza oladi — boshqa hech kim, hatto botning username'ini bilsa ham, kira olmaydi. Bu parolga qaraganda ishonchliroq, chunki Telegram akkauntingizni o'zi tasdiqlaydi.

Ma'lumotlar `kassa.db` faylida saqlanadi — bu fayl serverda qoladi va bot qayta ishga tushirilsa ham yo'qolmaydi (faylni o'chirmasangiz).
