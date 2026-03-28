import asyncio
import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton, WebAppInfo
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

load_dotenv()

API_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

class AdminState(StatesGroup):
    waiting_for_ad = State()

ads = []

def main_menu_keyboard():
    keyboard = [
        [KeyboardButton(text="📥 Yuklab olish")],
        [KeyboardButton(text="❓ Qanday ishlaydi?")],
        [KeyboardButton(text="🚗 Haydovchi bo'lmoqchiman")],
        [KeyboardButton(text="📞 Admin bilan bog'lanish")]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

def admin_keyboard():
    keyboard = [
        [InlineKeyboardButton(text="📢 Reklama qo'shish", callback_data="add_ad")],
        [InlineKeyboardButton(text="📋 Reklama ro'yxati", callback_data="list_ads")],
        [InlineKeyboardButton(text="◀️ Orqaga", callback_data="back_to_menu")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def ads_keyboard():
    keyboard = [[InlineKeyboardButton(text="◀️ Orqaga", callback_data="admin_panel")]]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        await message.answer("Admin panelga xush kelibsiz!", reply_markup=admin_keyboard())
    else:
        await message.answer(
            "🚕 ElTaxi - Yo'lovchi va Haydovchilar uchun bot!\n\nQuyidagi bo'limlardan birini tanlang:",
            reply_markup=main_menu_keyboard()
        )

@dp.callback_query(F.data == "admin_panel")
async def admin_panel(callback: types.CallbackQuery):
    if callback.from_user.id == ADMIN_ID:
        await callback.message.edit_text("Admin panel:", reply_markup=admin_keyboard())
    await callback.answer()

@dp.callback_query(F.data == "add_ad")
async def add_ad(callback: types.CallbackQuery, state: FSMContext):
    if callback.from_user.id == ADMIN_ID:
        await callback.message.edit_text("Reklama matnini yuboring:")
        await state.set_state(AdminState.waiting_for_ad)
    await callback.answer()

@dp.message(AdminState.waiting_for_ad)
async def save_ad(message: types.Message, state: FSMContext):
    if message.from_user.id == ADMIN_ID:
        ads.append(message.text)
        await message.answer("✅ Reklama qo'shildi!", reply_markup=admin_keyboard())
        await state.clear()

@dp.callback_query(F.data == "list_ads")
async def list_ads(callback: types.CallbackQuery):
    if callback.from_user.id == ADMIN_ID:
        if ads:
            text = "📋 Reklama ro'yxati:\n\n" + "\n\n".join(f"{i+1}. {ad}" for i, ad in enumerate(ads))
        else:
            text = "Reklamalar yo'q"
        await callback.message.edit_text(text, reply_markup=ads_keyboard())
    await callback.answer()

@dp.message(F.text == "📥 Yuklab olish")
async def yuklab_olish(message: types.Message):
    await message.answer("https://eltaxi-production.up.railway.app")

@dp.message(F.text == "◀️ Orqaga")
async def orqaga(message: types.Message):
    await message.answer(
        "🚕 ElTaxi - Yo'lovchi va Haydovchilar uchun bot!\n\nQuyidagi bo'limlardan birini tanlang:",
        reply_markup=main_menu_keyboard()
    )

CHANNEL_CHAT_ID = -1003897886406
VIDEO_MESSAGE_ID = 139

@dp.message(F.text == "❓ Qanday ishlaydi?")
async def how_it_works_msg(message: types.Message):
    reply_keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="◀️ Orqaga")]],
        resize_keyboard=True
    )
    try:
        await bot.copy_message(
            chat_id=message.from_user.id,
            from_chat_id=CHANNEL_CHAT_ID,
            message_id=VIDEO_MESSAGE_ID
        )
        await message.answer(
            "📹 <b>Video yuqorida:</b>\n\n"
            "ElTaxi orqali yo'lovchilar haydovchilarni tez va oson chaqirishadi.",
            reply_markup=reply_keyboard
        )
    except Exception as e:
        await message.answer(
            "❌ Video topilmadi. Iltimos, qayta urinib ko'ring.",
            reply_markup=reply_keyboard
        )

@dp.message(F.text == "🚗 Haydovchi bo'lmoqchiman")
async def driver_register(message: types.Message):
    reply_keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="◀️ Orqaga")]],
        resize_keyboard=True
    )
    await message.answer(
        "🚗 <b>Haydovchi bo'lish uchun:</b>\n\n"
        "ElTaxi'da haydovchi bo'lish uchun @sharqtech_admin ga yozing.\n\n"
        "Biz sizga barcha kerakli ma'lumotlarni beramiz va ro'yxatdan o'tkazamiz.",
        reply_markup=reply_keyboard
    )

@dp.message(F.text == "📞 Admin bilan bog'lanish")
async def contact_admin(message: types.Message):
    reply_keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="◀️ Orqaga")]],
        resize_keyboard=True
    )
    await message.answer(
        "📞 <b>Admin bilan bog'lanish:</b>\n\n"
        "Savollar yoki muammolar bo'lsa, @sharqtech_admin ga yozing.\n\n"
        "Biz tez orada javob beramiz!",
        reply_markup=reply_keyboard
    )

@dp.callback_query(F.data == "how_it_works")
async def how_it_works(callback: types.CallbackQuery):
    text = """❓ <b>Qanday ishlaydi?</b>

1. <b>Yuklab olish</b> - Ilovani yuklab oling
2. <b>Ro'yxatdan o'ting</b> - Telefon raqamingizni kiriting
3. <b>Buyurtma bering</b> - Qayerdan qayerga borishni belgilang
4. <b>Haydovchi kutish</b> - Eng yaqin haydovchini kuting

🚀 Oddiy va tez!"""
    await callback.message.edit_text(text, reply_markup=main_menu_keyboard())
    await callback.answer()

@dp.callback_query(F.data == "driver")
async def driver_info(callback: types.CallbackQuery):
    text = """🚗 <b>Haydovchi uchun</b>

ElTaxi haydovchisi bo'lish uchun:
1. Ilovani yuklab oling
2. "Haydovchi" bo'limini tanlang
3. Ma'lumotlaringizni kiriting
4. Buyurtmalarni qabul qiling

💰 Endi ishni boshlashingiz mumkin!"""
    await callback.message.edit_text(text, reply_markup=main_menu_keyboard())
    await callback.answer()

@dp.callback_query(F.data == "stats")
async def stats(callback: types.CallbackQuery):
    text = """📊 <b>Statistika</b>

👥 Jami foydalanuvchilar: 1+

(Bot hozir ishga tushirildi)"""
    await callback.message.edit_text(text, reply_markup=main_menu_keyboard())
    await callback.answer()

@dp.callback_query(F.data == "back_to_menu")
async def back_to_menu(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "🚕 ElTaxi - Yo'lovchi va Haydovchilar uchun bot!\n\nQuyidagi bo'limlardan birini tanlang:",
        reply_markup=main_menu_keyboard()
    )
    await callback.answer()

VIDEO_FILE_ID = "BAACAgIAAxkBAA..."

@dp.message(F.video)
async def get_video_id(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        global VIDEO_FILE_ID
        VIDEO_FILE_ID = message.video.file_id
        with open("video_id.txt", "w") as f:
            f.write(VIDEO_FILE_ID)
        await message.answer(f"Video olindi!")

async def main():
    await dp.start_polling(bot)

async def start_webhook():
    webhook_url = os.getenv("WEBHOOK_URL")
    if webhook_url:
        await bot.set_webhook(webhook_url)
        from aiogram.types import Update
        from aiohttp import web
        app = web.Application()
        router = Router()
        
        @router.post("/webhook")
        async def webhook(request):
            update = Update(**await request.json())
            await dp.feed_update(bot, update)
            return web.Response()
        
        app.router.include_router(router)
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, "0.0.0.0", 8000)
        await site.start()
    else:
        await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(start_webhook())