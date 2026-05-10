from logging import getLogger

from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from ..aiogram_functions import IsAdmin, kb, Mailing, User
from ..rabbitmq import mailing_message_to_users
from ..service import UserService, AnalyticsService
from ..dto import QueryPaymentSinglePeriodStatsDto


router = Router()
router.message.filter(IsAdmin())
logger = getLogger(name=__name__)


@router.message(Command("admin_menu"))
async def admin_menu_message(message: Message) -> None:
    text = f"Добро пожаловать в меню, {message.from_user.first_name}"
    await message.answer(text=text, reply_markup=kb.admin_menu_kb())


@router.message(F.text == "📕 Бесплатно выдать баланс пользователю 📕")
async def get_id_user_for_top_up_balance(message: Message, state: FSMContext) -> None:
    await state.set_state(state=User.tg_id)
    text = (
        "📲 Введите сумму и телеграм id пользователя, которому хотите пополнить баланс 📲\n"
        "Отправка должна идти в формате tg_id:balance"
    )
    await message.answer(text=text, reply_markup=kb.cancel_top_up_balance())


@router.message(F.text == "❌ Отменить бесплатное пополнение ❌")
async def cancel_top_up_balance_user(message: Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    if current_state is None:
        text = "❌ Вы не запрашивали пополнение баланса пользователя! ❌"
        await message.answer(text=text, reply_markup=kb.admin_menu_kb())
        return
    await state.clear()
    text = "✅ Вы отменили пополнение баланса пользователя ✅"
    await message.answer(text=text, reply_markup=kb.admin_menu_kb())


@router.message(User.tg_id, F.text)
async def top_up_balance_user(
    message: Message,
    state: FSMContext,
    user_service: UserService,
) -> None:
    try:
        await state.update_data(user=message.text.split(sep=":"))
        data = await state.get_data()
        user: list[str] = data.get("user")
        if len(user) != 2:
            text = "❌ Вы отправили неправильный формат данных, попробуйте еще раз ❌"
            await message.answer(text=text)
            return
        tg_id = int(user[0])
        amount = float(user[1])
        current_user_in_db = await user_service.get_user_by_tg_id(tg_id=tg_id)
        if current_user_in_db is None:
            text = "❌ Пользователя не существует в нашем боте ❌"
            await message.answer(text=text)
            return
        if current_user_in_db.is_blocked:
            text = "❌ Пользователь заблокировал бота ❌"
            await message.answer(text=text)
            return
        await user_service.update_balance_user(
            tg_id=tg_id,
            amount=amount,
            type_update="plus",
        )
        text = f"📊 Вы успешно пополнили баланс юзера {tg_id} на сумму - {amount} 📊"
        await message.answer(text=text, reply_markup=kb.admin_menu_kb())
        await state.clear()
    except Exception as e:
        logger.error("Произошла непредвиденная ошибка - %s", str(e))
        text = "❌ Произошла непредвиденная ошибка, попробуйте еще раз ❌"
        await message.answer(text=text)
        return


@router.message(F.text == "📊 Стастистика бота 📊")
async def get_stats_bot_message(message: Message, analytics_service: AnalyticsService) -> None:
    analytics_users = await analytics_service.get_analytics_users()
    def fmt_payment(p: QueryPaymentSinglePeriodStatsDto) -> str:
        return f"{p.count} шт | {p.total_amount:.0f} ₽"
    text = (
        "📊 Статистика 📊\n\n"
        f"<b>Пользователей за вчера</b>: {analytics_users.users.yesterday} шт.\n"
        f"<b>Пользователей за сегодня</b>: {analytics_users.users.today} шт.\n"
        f"<b>Пользователей за эту неделю</b>: {analytics_users.users.week} шт.\n"
        f"<b>Пользователей за этот месяц</b>: {analytics_users.users.month} шт.\n"
        f"<b>Всего пользователей</b>: {analytics_users.users.total} шт.\n\n"
        "💳 Платежи 💳\n"
        f"<b>Платежей за вчера</b>: {fmt_payment(p=analytics_users.payments.yesterday)}\n"
        f"<b>Платежей за сегодня</b>: {fmt_payment(p=analytics_users.payments.today)}\n"
        f"<b>Платежей за эту неделю</b>: {fmt_payment(p=analytics_users.payments.week)}\n"
        f"<b>Платежей за этот месяц</b>: {fmt_payment(p=analytics_users.payments.month)}\n"
        f"<b>Всего платежей</b>: {fmt_payment(p=analytics_users.payments.total)}\n"
    )
    await message.answer(text=text)


@router.message(F.text == "💬 Рассылка 💬")
async def get_message_for_mailing(message: Message, state: FSMContext) -> None:
    await state.set_state(state=Mailing.mailing_message)
    text = "💬 Отправьте сообщение для рассылки (поддерживаются фотки и документы) 💬"
    await message.answer(text=text, reply_markup=kb.cancel_mailing())


@router.message(F.text == "❌ Отменить рассылку ❌")
async def cancel_send_mailing(message: Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    if current_state is None:
        text = "❌ Вы не запрашивали рассылку по пользователям! ❌"
        await message.answer(text=text, reply_markup=kb.admin_menu_kb())
        return
    await state.clear()
    text = "💼 Вы отменили рассылку 💼"
    await message.answer(text=text, reply_markup=kb.admin_menu_kb())


@router.message(Mailing.mailing_message)
async def send_mailing_message(
    message: Message,
    state: FSMContext,
    user_service: UserService,
) -> None:
    message_text = message.text if message.text or message.caption else None
    message_media = (
        message.photo[-1].file_id if message.photo else
        message.document.file_id if message.document else
        None
    )
    message_type = (
        "photo" if message.photo else
        "document" if message.document else
        "text"
    )
    await mailing_message_to_users(
        user_service=user_service,
        message_type=message_type,
        message_text=message_text,
        message_media=message_media,
    )
    text = "❗️ Рассылка запущена ❗️"
    await message.answer(text=text, reply_markup=kb.admin_menu_kb())
    await state.clear()
