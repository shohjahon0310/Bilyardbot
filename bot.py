
import logging
from aiogram import Bot, Dispatcher, types, executor
from datetime import datetime, timedelta

API_TOKEN = '7637817344:AAEoiYHF6gnsERKmlCwjOyI9cV_QBiJUN2E'
ADMIN_ID = 1549017358

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Har daqiqa narxi
PRICE_PER_MIN = 35000 / 60

# Stol va mahsulotlar ma’lumotlari
tables = {
    "1": {"time": None, "products": []},
    "2": {"time": None, "products": []},
    "3": {"time": None, "products": []},
    "4": {"time": None, "products": []},
}
products = {}  # nom: narx

# Kunlik/haftalik hisob
turnover = []

def calc_price(start, end):
    duration = end - start
    minutes = int(duration.total_seconds() // 60)
    return minutes, round(minutes * PRICE_PER_MIN)

@dp.message_handler(commands=['start'])
async def start_cmd(message: types.Message):
    await message.reply("🎱 Бильярд ҳисоблаш бот
/stol1 13:00 14:02
/plus1 cola
/hisob1")

@dp.message_handler(commands=['addproduct'])
async def add_product(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return await message.reply("⛔️ Бу функция фақат админ учун.")
    try:
        _, nom, narx = message.text.split()
        products[nom.lower()] = int(narx)
        await message.reply(f"✅ {nom.capitalize()} ({narx} сўм) қўшилди.")
    except:
        await message.reply("❗️ Формат: /addproduct nom narx")

@dp.message_handler(commands=['plus1', 'plus2', 'plus3', 'plus4'])
async def add_to_table(message: types.Message):
    stol = message.text[5]
    try:
        nom = message.text.split()[1].lower()
        narx = products.get(nom)
        if not narx:
            return await message.reply("❗️ Бу номда маҳсулот топилмади.")
        tables[stol]["products"].append((nom, narx))
        await message.reply(f"➕ {stol}-столга {nom.capitalize()} ({narx} сўм) қўшилди.")
    except:
        await message.reply("❗️ Формат: /plus1 cola")

@dp.message_handler(commands=['stol1', 'stol2', 'stol3', 'stol4'])
async def set_time(message: types.Message):
    stol = message.text[5]
    try:
        _, t1, t2 = message.text.split()
        start = datetime.strptime(t1, "%H:%M")
        end = datetime.strptime(t2, "%H:%M")
        tables[stol]["time"] = (start, end)
        await message.reply(f"⏱ {stol}-стол учун вақт сақланди: {t1} → {t2}")
    except:
        await message.reply("❗️ Формат: /stol1 13:00 14:12")

@dp.message_handler(commands=['hisob1', 'hisob2', 'hisob3', 'hisob4'])
async def show_total(message: types.Message):
    stol = message.text[-1]
    table = tables[stol]
    if not table["time"]:
        return await message.reply("❗️ Вақт киритилмаган.")
    start, end = table["time"]
    minutes, price_time = calc_price(start, end)
    price_products = sum(p[1] for p in table["products"])
    total = price_time + price_products
    turnover.append(total)
    msg = f"📋 {stol}-стол ҳисоботи:
"
    msg += f"⏱ Вақт: {minutes} дақиқа = {price_time:,} сўм
"
    if table["products"]:
        msg += "🥤 Маҳсулотлар:
"
        for p in table["products"]:
            msg += f"- {p[0].capitalize()}: {p[1]:,} сўм
"
    msg += f"💵 Жами: {total:,} сўм"
    await message.reply(msg)

@dp.message_handler(commands=['kunlik'])
async def daily_turnover(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return await message.reply("⛔️ Админгина кўра олади.")
    await message.reply(f"📊 Бугунги оборот: {sum(turnover):,} сўм")

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    executor.start_polling(dp, skip_updates=True)
