from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardMarkup
from remnawave.models.hwid import HwidDeviceDto

from ..dto import TariffDto
from ..core import settings


def menu_kb() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.button(text="👤 Профиль 👤")
    builder.button(text="💼 Приобрести конфиг 💼")
    builder.button(text="❓ Поддержка ❓")
    builder.button(text="🧩 Моя подписка 🧩")
    return builder.adjust(2).as_markup(resize_keyboard=True)


def cancel_top_up() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.button(text="❌ Отменить пополнение ❌")
    return builder.as_markup(resize_keyboard=True)


def admin_menu_kb() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.button(text="📊 Стастистика бота 📊")
    builder.button(text="💬 Рассылка 💬")
    return builder.as_markup(resize_keyboard=True)


def cancel_mailing() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.button(text="❌ Отменить рассылку ❌")
    return builder.as_markup(resize_keyboard=True)


def profile_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="💵 Пополнить баланс 💵", callback_data="top_up_balance")
    builder.button(text="👥 Реферальная программа 👥", callback_data="referral_program")
    return builder.adjust(1).as_markup()


def check_invoice() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="❌ Отменить платеж ❌", callback_data="cancel_top_up")
    return builder.as_markup()


def get_payment_type() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Lolz ✅", callback_data="payment_lolz")
    builder.button(text="🦋 CryptoBot 🦋", callback_data="payment_cryptobot")
    builder.button(text="🧩 Crypto 🧩", callback_data="payment_heleket")
    return builder.as_markup()


def get_available_configs(tariffs: list[TariffDto]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for tariff in tariffs:
        builder.button(
            text=f"🚀 {tariff.name} | {tariff.price} RUB | {tariff.duration_days} дн.🚀",
            callback_data=f"tariff_{tariff.name}",
        )
    return builder.adjust(1).as_markup()


def buy_config(name: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="⚙️ Приобрести конфиг ⚙️", callback_data=f"buy_tariff_{name}")
    builder.button(text="Вернуться назад 🔙", callback_data="back_to_menu_configs")
    return builder.adjust(1).as_markup()


def manage_subscription(subscription_id: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text="📅 Как подключиться к подписке? 📅",
        url=settings.guide_vpn_connect.encoded_string(),
    )
    builder.button(
        text="📊 Продлить подписку 📊",
        callback_data=f"extend_subscription_{subscription_id}",
    )
    builder.button(
        text="📱 Управление устройствами 📱",
        callback_data=f"manage_hwid_users_{subscription_id}",
    )
    return builder.adjust(1).as_markup()


def manage_hwid_users(hwid_devices: list[HwidDeviceDto]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for device in hwid_devices:
        device_info = f"{device.platform} | {device.os_version}"
        builder.button(text=device_info, callback_data="ignore")
        builder.button(text="🗑", callback_data=f"hwid_delete_{str(device.hwid)}")
    builder.button(text="Вернуться к подписке 🔙", callback_data="subscription_start")
    return builder.adjust(2).as_markup()


def get_type_extending_subscribe(subscription_id: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    buttons = [
        {"text": "🌟 3 дн. | 50 RUB.", "callback_data": f"days_3_{subscription_id}_50"},
        {"text": "🌟 30 дн. | 350 RUB.", "callback_data": f"days_30_{subscription_id}_350"},
        {"text": "🌟 45 дн. | 500 RUB.", "callback_data": f"days_45_{subscription_id}_500"},
        {"text": "🌟 90 дн. | 1500 RUB.", "callback_data": f"days_90_{subscription_id}_1200"},
    ]
    for button in buttons:
        builder.button(text=button.get("text"), callback_data=button.get("callback_data"))
    builder.button(text="Вернуться к подписке 🔙", callback_data="subscription_start")
    return builder.adjust(1).as_markup()


def back_to_subscription_start() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="Вернуться к подписке 🔙", callback_data="subscription_start")
    return builder.as_markup()
