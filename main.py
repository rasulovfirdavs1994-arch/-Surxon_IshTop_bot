import os
import logging
import time

from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

# ========= CONFIG (Konfiguratsiya) =========
# Token Render panelida "Environment Variables" bo'limiga qo'shiladi
API_TOKEN = os.getenv("TOKEN")
CHANNEL_ID = "@surxon_ishtop"

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

# ========= FSM (Holatlar) =========
class JobForm(StatesGroup):
    org = State()      # Tashkilot nomi
    loc = State()      # Manzil
    pos = State()      # Lavozim
    salary = State()   # Maosh
    phone = State()    # Telefon raqami
    confirm = State()  # Tasdiqlash bosqichi

# ========= KEYBOARDS (Klaviaturalar) =========
def get_confirm_keyboard():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("✅ E'lon berish")
    kb.row("✏️ Tahrirlash", "❌ Bekor qilish")
    return kb

# ========= HANDLERS (Buyruqlar va Holatlar) =========

@dp.message_handler(commands=["start"], state="*")
async def start(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer(
        "👋 **Surxon IshTop** botiga xush kelibsiz!\n\n"
        "📌 Ish e'lonini joylash uchun: /add_job",
        parse_mode="Markdown"
    )

@dp.message_handler(commands=["add_job"], state="*")
async def add_job(message: types.Message):
    await message.answer("🏢 **Tashkilot nomini kiriting:**", parse_mode="Markdown")
    await JobForm.org.set()

@dp.message_handler(state=JobForm.org)
async def process_org(message: types.Message, state: FSMContext):
    await state.update_data(org=message.text)
    await message.answer("📍 **Manzilni kiriting:**", parse_mode="Markdown")
    await JobForm.loc.set()

@dp.message_handler(state=JobForm.loc)
async def process_loc(message: types.Message, state: FSMContext):
    await state.update_data(loc=message.text)
    await message.answer("💼 **Lavozimni kiriting:**", parse_mode="Markdown")
    await JobForm.pos.set()

@dp.message_handler(state=JobForm.pos)
async def process_pos(message: types.Message, state: FSMContext):
    await state.update_data(pos=message.text)
    await message.answer("💰 **Maoshni kiriting:**", parse_mode="Markdown")
    await JobForm.salary.set()

@dp.message_handler(state=JobForm.salary)
async def process_salary(message: types.Message, state: FSMContext):
    await state.update_data(salary=message.text)
    await message.answer("📞 **Telefon raqamingiz:**", parse_mode="Markdown")
    await JobForm.phone.set()

@dp.message_handler(state=JobForm.phone)
async def process_phone(message: types.Message, state: FSMContext):
    await state.update_data(phone=message.text)
    data = await state.get_data()
    job_id = int(time.time() % 100000)
    await state.update_data(job_id=job_id)

    preview = (
        f"📢 **ISH E'LONI (ID: {job_id})**\n\n"
        f"🏢 **Tashkilot:** {data['org']}\n"
        f"📍 **Manzil:** {data['loc']}\n"
        f"💼 **Lavozim:** {data['pos']}\n"
        f"💰 **Maosh:** {data['salary']}\n"
        f"📞 **Aloqa:** {message.text}\n\n"
        f"⚠️ *Ma'lumotlar to'g'rimi?*"
    )
    await message.answer(preview, reply_markup=get_confirm_keyboard(), parse_mode="Markdown")
    await JobForm.confirm.set()

@dp.message_handler(lambda m: m.text == "✅ E'lon berish", state=JobForm.confirm)
async def publish(message: types.Message, state: FSMContext):
    data = await state.get_data()
    post = (
        f"📢 #ISH_ELONI (ID: {data['job_id']})\n\n"
        f"🏢 **Tashkilot:** {data['org']}\n"
        f"📍 **Manzil:** {data['loc']}\n"
        f"💼 **Lavozim:** {data['pos']}\n"
        f"💰 **Maosh:** {data['salary']}\n"
        f"📞 **Aloqa:** {data['phone']}\n\n"
        f"🤖 @surxon_ishtop_bot"
    )
    try:
        await bot.send_message(CHANNEL_ID, post, parse_mode="Markdown")
        await message.answer("✅ **E'lon kanalga joylandi!**", reply_markup=types.ReplyKeyboardRemove())
    except Exception:
        await message.answer("❌ **Xatolik:** Bot kanal admini emas!")
    await state.finish()

@dp.message_handler(lambda m: m.text == "✏️ Tahrirlash", state=JobForm.confirm)
async def edit_job(message: types.Message):
    await message.answer("🔄 Tashkilot nomini qaytadan kiriting:", reply_markup=types.ReplyKeyboardRemove())
    await JobForm.org.set()

@dp.message_handler(lambda m: m.text == "❌ Bekor qilish", state="*")
async def cancel(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer("❌ E'lon berish bekor qilindi.", reply_markup=types.ReplyKeyboardRemove())

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
