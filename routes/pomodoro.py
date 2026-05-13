from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database.session import get_async_session
from models.pomodoro import Pomodoro
from schemas.pomodoro import (
    PomodoroActiveResponse,
    PomodoroControl,
    PomodoroResponse,
    PomodoroStop,
)
from services.auth_user import get_current_user

router = APIRouter(prefix="/pomodoro", tags=["pomodoro"])


@router.post("/start", response_model=PomodoroResponse)
async def start_pomodoro(
    payload: PomodoroControl,
    db: AsyncSession = Depends(get_async_session),
):
    current_user = await get_current_user(payload.name, payload.password, db)

    result = await db.execute(
        select(Pomodoro).where(
            Pomodoro.user_id == current_user.id,
            Pomodoro.active == True,
        )
    )
    existing = result.scalars().first()
    if existing:
        raise HTTPException(status_code=400, detail="Já existe um pomodoro ativo para este usuário")

    pomodoro = Pomodoro(
        user_id=current_user.id,
        status="working",
        active=True,
        duration=payload.duration,
        started_at=datetime.utcnow(),
    )
    db.add(pomodoro)
    await db.commit()
    await db.refresh(pomodoro)
    return pomodoro


@router.post("/stop", response_model=PomodoroResponse)
async def stop_pomodoro(
    payload: PomodoroStop,
    db: AsyncSession = Depends(get_async_session),
):
    current_user = await get_current_user(payload.name, payload.password, db)

    result = await db.execute(
        select(Pomodoro).where(
            Pomodoro.user_id == current_user.id,
            Pomodoro.active == True,
        )
    )
    pomodoro = result.scalars().first()
    if not pomodoro:
        raise HTTPException(status_code=404, detail="Nenhum pomodoro ativo encontrado")

    pomodoro.active = False
    pomodoro.status = "stopped"
    pomodoro.ended_at = datetime.utcnow()
    await db.commit()
    await db.refresh(pomodoro)
    return pomodoro


@router.get("/active", response_model=list[PomodoroActiveResponse])
async def get_active_pomodoros(db: AsyncSession = Depends(get_async_session)):
    result = await db.execute(
        select(Pomodoro).options(selectinload(Pomodoro.user)).where(Pomodoro.active == True)
    )
    active_sessions = result.scalars().all()
    return [
        PomodoroActiveResponse(
            id=session.id,
            user_id=session.user_id,
            status=session.status,
            duration=session.duration,
            started_at=session.started_at,
            user_name=session.user.name if session.user else "",
        )
        for session in active_sessions
    ]
