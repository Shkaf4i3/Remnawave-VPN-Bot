from typing import Annotated, Dict, Any

from fastapi import APIRouter, Depends, Header

from ..service import WebhookService
from ..deps import service_deps


router = APIRouter(prefix="/webhook", tags=["Webhooks Router"])


@router.post(
    path="/tg",
    summary="Handle tg webhook",
    description="Handle tg webhook",
)
async def handle_tg_webhook_update(
    update: Dict[str, Any],
    webhook_service: Annotated[WebhookService, Depends(service_deps.get_webhook_service)],
    x_telegram_bot_api_secret_token: str = Header(),
) -> None:
    await webhook_service.handle_tg_webhook_update(
        update=update,
        x_telegram_bot_api_secret_token=x_telegram_bot_api_secret_token,
    )


@router.post(
    path="/cryptobot",
    summary="Handle cryptobot webhook",
    description="Handle cryptobot webhook",
)
async def handle_cryptobot_webhook_update(
    update: Dict[str, Any],
    webhook_service: Annotated[WebhookService, Depends(service_deps.get_webhook_service)],
) -> None:
    await webhook_service.handle_cryptobot_webhook_update(update=update)


@router.post(
    path="/lolzteam",
    summary="Handle lolzteam webhook",
    description="Handle lolzteam webhook",
)
async def handle_lolzteam_webhook_update(
    update: Dict[str, Any],
    webhook_service: Annotated[WebhookService, Depends(service_deps.get_webhook_service)],
) -> None:
    await webhook_service.handle_lolzteam_webhook_update(update=update)
