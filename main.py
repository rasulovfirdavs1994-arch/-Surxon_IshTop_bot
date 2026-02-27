import os
import logging
import time
import threading

from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from flask import Flask

# ================= CONFIG =================

TOKEN = os.getenv("TOKEN")
CHANNEL_ID = "@surxon_ishtop"

if not TOKEN:
    raise Exception("TOKEN topilmadi! Render Environment Variables tekshiring.")

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

# ================= FSM =================

class JobForm(StatesGroup):
    org = State()
    loc = State()
    pos = State()
    salary = State()
    phone = State()
    confirm = State()

# ================= KEYBOARD =================

def confirm_keyboard():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("✅ E'lon berish")
    kb.row("✏️ Tahrirlash", "❌ Bekor qilish")
    return kb

# ================= HANDLERS =================

@dp.message_handler(commands=["start"], state="*")
async def start(message: types.Message, state: FSMContext):
    await state.finish()

    await message.answer(
        "👋 Surxon IshTop botiga xush kelibsiz!\n\n"
        "📌 Ish e'lon berish uchun /add_job ni bosing."
    )

@dp.message_handler(commands=["add_job"])
async def add_job(message: types.Message):
    await message.answer("🏢 Tashkilot nomini kiriting:")
    await JobForm.org.set()

@dp.message_handler(state=JobForm.org)
async def org_step(message: types.Message, state: FSMContext):
    await state.update_data(org=message.text)

    await message.answer("📍 Manzilni kiriting:")
    await JobForm.loc.set()

@dp.message_handler(state=JobForm.loc)
async def loc_step(message: types.Message, state: FSMContext):
    await state.update_data(loc=message.text)

    await message.answer("💼 Lavozimni kiriting:")
    await JobForm.pos.set()

@dp.message_handler(state=JobForm.pos)
async def pos_step(message: types.Message, state: FSMContext):
    await state.update_data(pos=message.text)

    await message.answer("💰 Maoshni kiriting:")
    await JobForm.salary.set()

@dp.message_handler(state=JobForm.salary)
async def salary_step(message: types.Message, state: FSMContext):
    await state.update_data(salary=message.text)

    await message.answer("📞 Telefon raqamingiz:")
    await JobForm.phone.set()

@dp.message_handler(state=JobForm.phone)
async def phone_step(message: types.Message, state: FSMContext):
    await state.update_data(phone=message.text)

    data = await state.get_data()

    job_id = int(time.time() % 100000)
    await state.update_data(job_id=job_id)

    preview = f"""
📢 <b>ISH E'LONI (ID: {job_id})</b>

🏢 Tashkilot: {data['org']}
📍 Manzil: {data['loc']}
💼 Lavozim: {data['pos']}
💰 Maosh: {data['salary']}
📞 Aloqa: {data['phone']}

⚠️ Ma'lumotlar to'g'rimi?
"""

    await message.answer(preview, reply_markup=confirm_keyboard(), parse_mode="HTML")
    await JobForm.confirm.set()

@dp.message_handler(lambda m: m.text == "✅ E'lon berish", state=JobForm.confirm)
async def publish(message: types.Message, state: FSMContext):

    data = await state.get_data()

    post = f"""
📢 #ISH_ELONI (ID: {data['job_id']})

🏢 <b>Tashkilot:</b> {data['org']}
📍 <b>Manzil:</b> {data['loc']}
💼 <b>Lavozim:</b> {data['pos']}
💰 <b>Maosh:</b> {data['salary']}
📞 <b>Aloqa:</b> {data['phone']}
"""

    try:
        await bot.send_message(CHANNEL_ID, post, parse_mode="HTML")
        await message.answer("✅ E'lon kanalga joylandi!")
    except:
        await message.answer("❌ Bot kanal admini emas!")

    await state.finish()

@dp.message_handler(lambda m: m.text == "❌ Bekor qilish", state="*")
async def cancel(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer("❌ Bekor qilindi.")

# ================= FLASK HEALTH CHECK =================

app = Flask(__name__)

@app.route("/")
def home():
    return "Bot ishlayapti!"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

# ================= MAIN =================

if __name__ == "__main__":
    threading.Thread(target=run_web).start()
    executor.start_polling(dp, skip_updates=True)
