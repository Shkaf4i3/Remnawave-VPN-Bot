from logging import getLogger
from datetime import datetime, timezone, timedelta

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.filters import CommandObject, CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.utils.deep_linking import create_start_link
from remnawave.exceptions import BadRequestError, ApiError, NetworkError, ServerError

from ..service import UserService, PaymentService, TariffService, SubscriptionService
from ..aiogram_functions import kb, Balance
from ..core import settings
from ..client import PaymentSystem, LolzTeam, CryptoBot, RemnawaveClient
from ..model import PaymentStatus
from ..utils import create_user, get_profile_subcription


router = Router()
payment_system = PaymentSystem(
    crypto_bot=CryptoBot(),
    lolz_client=LolzTeam(),
)
logger = getLogger(name=__name__)


@router.message(CommandStart(deep_link=True))
async def start_message_with_deep_link(
    message: Message,
    user_service: UserService,
    command: CommandObject,
) -> None:
    referrer_user_id = int(command.args)
    await create_user(
        message=message,
        user_service=user_service,
        referrer_user_id=referrer_user_id,
    )


@router.message(CommandStart())
async def start_message_without_deep_link(
    message: Message,
    user_service: UserService,
) -> None:
    await create_user(
        message=message,
        user_service=user_service,
    )


@router.message(Command("menu"))
async def open_menu_message(message: Message) -> None:
    text = "🌿 Вы открыли меню 🌿"
    await message.answer(text=text, reply_markup=kb.menu_kb())


@router.message(F.text == "❓ Поддержка ❓")
async def get_help_message(message: Message) -> None:
    text = (
        f"🆘 Возникли вопросы по поводу бота? ❓. Обращайтесь 🫱 {settings.support_username}"
    )
    await message.answer(text=text)


@router.message(F.text == "👤 Профиль 👤")
async def get_profile_message(message: Message, user_service: UserService) -> None:
    existing_user = await user_service.get_user_by_tg_id(tg_id=message.from_user.id)
    created_at = existing_user.created_at.strftime(format=r"%d/%m/%Y")
    text = (
        f"👤 Ваш профиль:\n"
        f"ID - <code>{existing_user.tg_id}</code>\n"
        f"Баланс - <code>{existing_user.balance}</code>\n"
        f"Дата регистрации в боте - <code>{created_at}</code>\n"
    )
    await message.answer(text=text, reply_markup=kb.profile_kb())


@router.message(F.text == "❌ Отменить пополнение ❌")
async def cancel_top_up(message: Message, state: FSMContext) -> None:
    state_data = await state.get_state()
    if state_data is None:
        text = "Вы не запрашивали пополнение баланса"
        await message.answer(text=text, reply_markup=kb.menu_kb())
        return
    text = "Вы отменили пополнение"
    await state.clear()
    await message.answer(text=text, reply_markup=kb.menu_kb())


@router.message(F.text == "💼 Приобрести конфиг 💼")
async def get_vless_config(message: Message, tariff_service: TariffService) -> None:
    text = "💿 Выберите любой из доступных конфигов 💿"
    tariffs = await tariff_service.get_list_tariffs()
    await message.answer(
        text=text,
        reply_markup=kb.get_available_configs(tariffs=tariffs),
    )


@router.message(F.text == "🧩 Моя подписка 🧩")
async def get_user_subscriptions(
    message: Message,
    user_service: UserService,
    subscription_service: SubscriptionService,
    tariff_service: TariffService,
    remnawave_client: RemnawaveClient,
) -> None:
    await get_profile_subcription(
        update=message,
        user_service=user_service,
        subscription_service=subscription_service,
        tariff_service=tariff_service,
        remnawave_client=remnawave_client,
        logger=logger,
        type="open",
    )


@router.callback_query(F.data.startswith("manage_"))
async def get_all_hwid_devices_user(
    callback: CallbackQuery,
    remnawave_client: RemnawaveClient,
    subscription_service: SubscriptionService,
) -> None:
    data = callback.data.split(sep="_")
    subscription_id = data[3]
    existing_subscription = await subscription_service.get_subscription_by_id(
        id=subscription_id,
    )
    hwid_devices = await remnawave_client.get_user_active_devices(
        uuid=str(existing_subscription.remnawave_user_uuid),
    )
    text = "✅ Здесь показаны все пользователи, которые активировали вашу подписку ✅"
    await callback.message.edit_text(
        text=text,
        reply_markup=kb.manage_hwid_users(hwid_devices=hwid_devices),
    )


@router.callback_query(F.data.startswith("hwid_"))
async def manage_hwid_device_by_user(
    callback: CallbackQuery,
    user_service: UserService,
    subscription_service: SubscriptionService,
    remnawave_client: RemnawaveClient,
) -> None:
    data = callback.data.split(sep="_")
    hwid_device = data[2]
    existing_user = await user_service.get_user_by_tg_id(tg_id=callback.from_user.id)
    existing_subscription = await subscription_service.get_subscription_by_user_id(
        user_id=existing_user.id,
    )
    hwid_devices = await remnawave_client.get_user_active_devices(
        uuid=str(existing_subscription.remnawave_user_uuid),
    )
    try:
        await remnawave_client.delete_hwid_device_user(
            user_uuid=existing_subscription.remnawave_user_uuid,
            hwid=hwid_device,
        )
        hwid_devices = [d for d in hwid_devices if str(d.hwid) != hwid_device]
        text = f"✅ Пользователь {hwid_device} успешно удален из подписки ✅"
        await callback.message.edit_text(
            text=text,
            reply_markup=kb.manage_hwid_users(hwid_devices=hwid_devices),
        )
    except ApiError as e:
        text = "🆘 Произошла ошибка сервиса, попробуйте еще раз 🆘"
        await callback.message.answer(text=text)
        logger.error("Произошла ошибка API - %s", str(e))
    except NetworkError as e:
        text = "🆘 Произошла ошибка сети, попробуйте еще раз 🆘"
        await callback.message.answer(text=text)
        logger.error("Произошла ошибка сети - %s", str(e))
    except BadRequestError as e:
        text = "🆘 Произошла ошибка клиента, попробуйте еще раз 🆘"
        await callback.message.answer(text=text)
        logger.error("Произошла ошибка клиента - %s", str(e))
    except ServerError as e:
        text = "🆘 Произошла ошибка сервера, попробуйте еще раз 🆘"
        await callback.message.answer(text=text)
        logger.error("Произошла ошибка сервера - %s", str(e))
    except Exception as e:
        text = "🆘 Произошла неожиданная ошибка, попробуйте еще раз 🆘"
        await callback.message.answer(text=text)
        logger.error("Произошла неожиданная ошибка - %s", str(e))


@router.callback_query(F.data.startswith("tariff_"))
async def get_subscription_info(
    callback: CallbackQuery,
    tariff_service: TariffService,
    state: FSMContext,
) -> None:
    data = callback.data.split(sep="_")
    tariff_name = data[1]
    exisiting_tariff = await tariff_service.get_tariff_by_name(name=tariff_name)
    text = (
        f"🏛 Тариф - {exisiting_tariff.name}🏛\n\n"
        f"💾 Описание тарифа - {exisiting_tariff.description} 💾\n"
        f"💴 Цена - {exisiting_tariff.price} RUB 💴\n"
        f"📅 Количество дней подписки - {exisiting_tariff.duration_days} 📅\n"
        f"📱 Сколько пользователей может подключиться по этому тарифу - {exisiting_tariff.device_limit} шт. 📱\n\n"
        "После покупки вы получите URL-ссылку на подписку и полный гайд по ее установке на различные прокси клиенты"
    )
    response_message = await callback.message.edit_text(
        text=text,
        reply_markup=kb.buy_config(name=exisiting_tariff.name),
    )
    await state.update_data(config_message_id=response_message.message_id)


@router.callback_query(F.data.startswith("buy_"))
async def buy_tariff(
    callback: CallbackQuery,
    tariff_service: TariffService,
    user_service: UserService,
    subscription_service: SubscriptionService,
    remnawave_client: RemnawaveClient,
    state: FSMContext,
) -> None:
    try:
        config_message_id = await state.get_value(key="config_message_id")
        data = callback.data.split(sep="_")
        tariff_name = data[2]
        existing_tariff = await tariff_service.get_tariff_by_name(name=tariff_name)
        existing_user = await user_service.get_user_by_tg_id(tg_id=callback.from_user.id)
        existing_subscription = await subscription_service.get_subscription_by_user_id(
            user_id=existing_user.id,
        )
        if existing_subscription:
            text = "❗️ Вы уже имеете активную подписку! ❗️"
            await callback.message.edit_text(text=text)
            return
        expires_at = datetime.now(tz=timezone.utc) + timedelta(days=existing_tariff.duration_days)
        if existing_user.balance < existing_tariff.price:
            text = "❌ Недостаточно средств на вашем счету, пополните баланс! ❌"
            await callback.message.edit_text(text=text)
            return
        created_remnawave_user = await remnawave_client.create_new_user(
            username=existing_user.first_name,
            expire_at=expires_at,
            telegram_id=existing_user.tg_id,
            hwid_device_limit=existing_tariff.device_limit,
        )
        config_url = await remnawave_client.get_subscription_url_by_user_uuid(
            user_uuid=created_remnawave_user.short_uuid,
        )
        created_subscription = await subscription_service.save_subscription(
            user_id=existing_user.id,
            tariff_id=existing_tariff.id,
            expires_at=expires_at,
            remnawave_user_uuid=created_remnawave_user.uuid,
            remnawave_short_uuid=created_remnawave_user.short_uuid,
            config_url=config_url,
        )
        await user_service.update_balance_user(
            tg_id=existing_user.tg_id,
            amount=existing_tariff.price,
            type_update="minus",
        )
        await callback.message.bot.delete_message(
            chat_id=existing_user.tg_id,
            message_id=config_message_id,
        )
        url = f"<a href='{settings.guide_vpn_connect.encoded_string()}'>тык</a>"
        text = (
            "✅ Ваша подписка успешно создана! ✅\n\n"
            f"🌐 Ссылка на конфиг - <code>{created_remnawave_user.subscription_url}</code> 🌐\n"
            f"🧩 Подписка активна до - {created_subscription.expires_at.strftime(format=r"%d/%m/%Y")} 🧩\n\n"
            f"Ссылка на гайд по установке прокси-клиента и подписки есть в этом мануале - {url}"
        )
        await callback.message.answer(text=text)
    except ApiError as e:
        text = "🆘 Произошла ошибка сервиса, попробуйте еще раз 🆘"
        await callback.message.answer(text=text)
        logger.error("Произошла ошибка API - %s", str(e))
    except NetworkError as e:
        text = "🆘 Произошла ошибка сети, попробуйте еще раз 🆘"
        await callback.message.answer(text=text)
        logger.error("Произошла ошибка сети - %s", str(e))
    except BadRequestError as e:
        text = "🆘 Произошла ошибка клиента, попробуйте еще раз 🆘"
        await callback.message.answer(text=text)
        logger.error("Произошла ошибка клиента - %s", str(e))
    except ServerError as e:
        text = "🆘 Произошла ошибка сервера, попробуйте еще раз 🆘"
        await callback.message.answer(text=text)
        logger.error("Произошла ошибка сервера - %s", str(e))
    except Exception as e:
        text = "🆘 Произошла неожиданная ошибка, попробуйте еще раз 🆘"
        await callback.message.answer(text=text)
        logger.error("Произошла неожиданная ошибка - %s", str(e))


@router.callback_query(F.data == "back_to_menu_configs")
async def back_to_menu_configs(callback: CallbackQuery, tariff_service: TariffService) -> None:
    tariffs = await tariff_service.get_list_tariffs()
    text = "🛠 Вы вернулись в меню 🛠"
    await callback.message.edit_text(
        text=text,
        reply_markup=kb.get_available_configs(tariffs=tariffs),
    )


@router.callback_query(F.data == "top_up_balance")
async def get_type_payment_system(callback: CallbackQuery) -> None:
    text = "💵 Выберите тип платежной системы 💵"
    await callback.message.edit_text(text=text, reply_markup=kb.get_payment_type())


@router.callback_query(F.data.startswith("payment_"))
async def get_amount_for_top_up_balance(callback: CallbackQuery, state: FSMContext) -> None:
    callback_data = callback.data.split(sep="_")
    text = "🌿 Введите сумму для пополнения (в рублях)🌿"
    await state.set_state(Balance.amount)
    await state.update_data(client=callback_data[1])
    await callback.message.answer(
        text=text,
        reply_markup=kb.cancel_top_up(),
    )


@router.message(Balance.amount, F.text)
async def proccess_top_up_balance(
    message: Message,
    state: FSMContext,
    payment_service: PaymentService,
) -> None:
    try:
        await state.update_data(amount=float(message.text))
        data = await state.get_data()
        amount = data.get("amount")
        type_client = data.get("client")
        created_invoice = await payment_system.create_invoice(
            type_client=type_client,
            amount=amount,
            required_telegram_id=message.from_user.id,
            required_telegram_username=message.from_user.first_name,
        )
        url = (
            f"{
                created_invoice.bot_invoice_url
                if type_client == "cryptobot" else created_invoice.url
            }"
        )
        await payment_service.save_payment(
            tg_id=message.from_user.id,
            invoice_id=str(created_invoice.invoice_id),
            amount=amount,
        )
        text = "✅ Ссылка на оплату успешно сгенерирована! ✅"
        await message.answer(text=text, reply_markup=ReplyKeyboardRemove())
        text = (
            f"👇 Перейдите по ссылке, чтобы произвести оплату 👇\n{url}"
        )
        await state.update_data(invoice_id=str(created_invoice.invoice_id))
        if type_client == "lolz":
            await state.update_data(payment_id=created_invoice.payment_id)
        response_message = await message.answer(text=text, reply_markup=kb.check_invoice())
        await state.update_data(message_delete_id=response_message.message_id)
    except ValueError:
        text = "❌ Вы ввели не число! ❌ Попробуйте еще раз"
        await message.answer(text=text)
        return
    except Exception as e:
        text = "❌ Ошибка при создании платежа ❌. Попробуйте снова"
        await message.answer(text=text, reply_markup=kb.menu_kb())
        logger.error("Произошла непредвиденная ошибка - %s", str(e))
        await state.clear()


@router.callback_query(F.data == "cancel_top_up")
async def cancel_top_up_balance(
    callback: CallbackQuery,
    state: FSMContext,
    payment_service: PaymentService,
) -> None:
    data = await state.get_data()
    invoice_id = data.get("invoice_id")
    type_client = data.get("client")
    message_delete_id = data.get("message_delete_id")
    if invoice_id is None:
        text = "🌐 Заявки на платеж не существует 🌐"
        await callback.message.answer(text=text)
        return
    try:
        if type_client == "cryptobot":
            await payment_system.delete_invoice(invoice_id=invoice_id)
            await payment_service.update_payment_by_invoice_id(
                invoice_id=invoice_id,
                status=PaymentStatus.CANCELLED,
            )
        await callback.message.bot.delete_message(
            chat_id=callback.message.chat.id,
            message_id=message_delete_id,
        )
        text = "✅ Вы успешно отменили платеж ✅"
        await callback.message.answer(text=text, reply_markup=kb.menu_kb())
        await state.clear()
    except Exception as e:
        text = "🚫 Не получилось удалить платеж, попробуйте еще раз 🚫"
        await callback.message.answer(text=text)
        logger.error("Произошла непредвиденная ошибка - %s", str(e))


@router.callback_query(F.data == "referral_program")
async def referral_program_message(callback: CallbackQuery, user_service: UserService) -> None:
    link = await create_start_link(bot=callback.message.bot, payload=callback.from_user.id)
    count_users = await user_service.get_count_users_by_tg_id(tg_id=callback.from_user.id)
    text = (
        f"🔗 Вот твоя реферальная ссылка:\n{link}\n"
        "💵 Приглашай знакомых и друзей и будешь получать 10 процентов от их пополнений 💵\n\n"
        f"💼 Общее количество приглашенных 💼: {count_users}"
    )
    await callback.message.edit_text(text=text)


@router.callback_query(F.data == "subscription_start")
async def get_subscription_profile_menu(
    callback: CallbackQuery,
    user_service: UserService,
    subscription_service: SubscriptionService,
    tariff_service: TariffService,
    remnawave_client: RemnawaveClient,
) -> None:
    await get_profile_subcription(
        update=callback,
        user_service=user_service,
        subscription_service=subscription_service,
        tariff_service=tariff_service,
        remnawave_client=remnawave_client,
        logger=logger,
        type="back",
    )


@router.callback_query(F.data.startswith("extend_"))
async def get_type_extending_subscribe(callback: CallbackQuery) -> None:
    data = callback.data.split(sep="_")
    subscription_id = data[2]
    text = "📆 Выберите подходящий тариф:"
    await callback.message.edit_text(
        text=text,
        reply_markup=kb.get_type_extending_subscribe(subscription_id=subscription_id),
    )


@router.callback_query(F.data.startswith("days_"))
async def update_subscription_days(
    callback: CallbackQuery,
    remnawave_client: RemnawaveClient,
    subscription_service: SubscriptionService,
    user_service: UserService,
) -> None:
    data = callback.data.split(sep="_")
    additional_days = int(data[1])
    subscription_id = data[2]
    price = float(data[3])
    existing_subscription = await subscription_service.get_subscription_by_id(
        id=subscription_id,
    )
    existing_user = await user_service.get_user_by_tg_id(
        tg_id=callback.from_user.id,
    )
    if existing_user.balance < price:
        text = "🆘 На вашем балансе недостаточно средств 🆘"
        await callback.message.edit_text(text=text, reply_markup=kb.back_to_subscription_start())
        return
    try:
        expires_at = existing_subscription.expires_at + timedelta(days=additional_days)
        updated_at = datetime.now(tz=timezone.utc)
        await remnawave_client.update_subscription_days(
            uuid=existing_subscription.remnawave_user_uuid,
            expires_at=expires_at,
        )
        await subscription_service.update_subscription(
            id=existing_subscription.id,
            expires_at=expires_at,
            updated_at=updated_at,
        )
        await user_service.update_balance_user(
            tg_id=existing_user.tg_id,
            amount=price,
            type_update="minus",
        )
        text = f"✅ Вы успешно продлили подписку на {additional_days} дн. ✅"
        await callback.message.edit_text(text=text, reply_markup=kb.back_to_subscription_start())
    except ApiError as e:
        text = "🆘 Произошла ошибка сервиса, попробуйте еще раз 🆘"
        await callback.message.edit_text(text=text, reply_markup=kb.back_to_subscription_start())
        logger.error("Произошла ошибка API - %s", str(e))
    except NetworkError as e:
        text = "🆘 Произошла ошибка сети, попробуйте еще раз 🆘"
        await callback.message.edit_text(text=text, reply_markup=kb.back_to_subscription_start())
        logger.error("Произошла ошибка сети - %s", str(e))
    except BadRequestError as e:
        text = "🆘 Произошла ошибка клиента, попробуйте еще раз 🆘"
        await callback.message.edit_text(text=text, reply_markup=kb.back_to_subscription_start())
        logger.error("Произошла ошибка клиента - %s", str(e))
    except ServerError as e:
        text = "🆘 Произошла ошибка сервера, попробуйте еще раз 🆘"
        await callback.message.edit_text(text=text, reply_markup=kb.back_to_subscription_start())
        logger.error("Произошла ошибка сервера - %s", str(e))
    except Exception as e:
        text = "🆘 Произошла неожиданная ошибка, попробуйте еще раз 🆘"
        await callback.message.edit_text(text=text, reply_markup=kb.back_to_subscription_start())
        logger.error("Произошла неожиданная ошибка - %s", str(e))
