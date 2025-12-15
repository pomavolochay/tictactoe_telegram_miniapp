from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from ...config import Settings, get_settings
from ...presentation.dependencies import get_telegram_webhook_use_case
from ...application.use_cases import TelegramWebhookUseCase

router = APIRouter(prefix="/api/v1/telegram", tags=["telegram"])


@router.post("/webhook/{secret}")
async def telegram_webhook(
    secret: str,
    payload: dict,
    settings: Settings = Depends(get_settings),
    use_case: TelegramWebhookUseCase = Depends(get_telegram_webhook_use_case),
) -> dict[str, str]:
    expected = settings.telegram_webhook_secret
    if not expected or secret != expected:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="invalid_secret")
    await use_case.handle_update(payload)
    return {"status": "ok"}
