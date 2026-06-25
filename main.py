import uuid
from datetime import datetime, timedelta
from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel

from database import engine, get_db, Base
from models import User, UserRole, Instrument, InstrumentStatus, Movement, Calibration
from auth import (
    hash_password, verify_password, create_access_token, create_refresh_token,
    get_current_user, require_role, jwt, SECRET_KEY, ALGORITHM
)

app = FastAPI(title="Сервис учёта измерительного инструмента БЕЛАЗ")


@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)


class ВходВСистему(BaseModel):
    табельный_номер: str
    пароль: str


class ОтветСТокеном(BaseModel):
    токен_доступа: str
    токен_обновления: str
    тип_токена: str = "bearer"


class ОбновитьТокен(BaseModel):
    токен_обновления: str


class СоздатьИнструмент(BaseModel):
    название: str
    модель: str
    серийный_номер: str
    цех: str


class ОбновитьИнструмент(BaseModel):
    название: str | None = None
    цех: str | None = None
    дата_следующей_поверки: str | None = None


class ВыдатьИнструмент(BaseModel):
    штрихкод: str
    табельный_номер_рабочего: str


class ВернутьИнструмент(BaseModel):
    штрихкод: str
    исправен: bool = True
    примечания: str | None = None


class ПровестиПоверку(BaseModel):
    id_инструмента: str
    дата_поверки: str
    дата_следующей_поверки: str
    номер_сертификата: str


def инструмент_в_словарь(inst):
    return {
        "id": str(inst.id),
        "штрихкод": inst.barcode,
        "название": inst.name,
        "модель": inst.model,
        "серийный_номер": inst.serial_number,
        "цех": inst.workshop,
        "статус": inst.status.value,
        "дата_последней_поверки": str(inst.last_verification_date) if inst.last_verification_date else None,
        "дата_следующей_поверки": str(inst.next_verification_date) if inst.next_verification_date else None,
        "номер_сертификата": inst.certificate_number,
    }


def движение_в_словарь(mov):
    return {
        "id": str(mov.id),
        "id_инструмента": str(mov.instrument_id),
        "id_пользователя": str(mov.user_id),
        "действие": mov.action,
        "дата_выдачи": str(mov.issued_at) if mov.issued_at else None,
        "дата_возврата": str(mov.returned_at) if mov.returned_at else None,
        "исправен": mov.condition_ok,
        "примечания": mov.notes,
    }


def поверка_в_словарь(cal):
    return {
        "id": str(cal.id),
        "id_инструмента": str(cal.instrument_id),
        "дата_поверки": str(cal.verification_date),
        "дата_следующей_поверки": str(cal.next_verification_date),
        "номер_сертификата": cal.certificate_number,
    }



@app.post("/api/v1/auth/вход")
def вход(data: ВходВСистему, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.badge_number == data.табельный_номер).first()
    if not user or not verify_password(data.пароль, user.hashed_password):
        raise HTTPException(status_code=401, detail="Неверный табельный номер или пароль")
    return {
        "токен_доступа": create_access_token(str(user.id), user.role.value),
        "токен_обновления": create_refresh_token(str(user.id)),
        "тип_токена": "bearer"
    }


@app.post("/api/v1/auth/обновить-токен")
def обновить_токен(data: ОбновитьТокен, db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(data.токен_обновления, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401)
        user = db.query(User).filter(User.id == payload.get("sub")).first()
        if not user:
            raise HTTPException(status_code=401)
        return {
            "токен_доступа": create_access_token(str(user.id), user.role.value),
            "токен_обновления": create_refresh_token(str(user.id)),
            "тип_токена": "bearer"
        }
    except Exception:
        raise HTTPException(status_code=401, detail="Неверный токен обновления")


@app.get("/api/v1/auth/профиль")
def профиль(user: User = Depends(get_current_user)):
    return {
        "id": str(user.id),
        "табельный_номер": user.badge_number,
        "фио": user.full_name,
        "цех": user.workshop,
        "роль": user.role.value
    }



@app.get("/api/v1/инструменты")
def список_инструментов(
    цех: str | None = Query(None),
    статус: str | None = Query(None),
    тип: str | None = Query(None),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    query = db.query(Instrument)
    if цех:
        query = query.filter(Instrument.workshop == цех)
    if статус:
        query = query.filter(Instrument.status == статус)
    if тип:
        query = query.filter(Instrument.model.ilike(f"%{тип}%"))
    return [инструмент_в_словарь(r) for r in query.all()]


@app.post("/api/v1/инструменты")
def добавить_инструмент(
    data: СоздатьИнструмент,
    db: Session = Depends(get_db),
    user: User = Depends(require_role(UserRole.АДМИНИСТРАТОР, UserRole.МЕТРОЛОГ))
):
    barcode = f"BELAZ-{uuid.uuid4().hex[:8].upper()}"
    inst = Instrument(
        barcode=barcode,
        name=data.название,
        model=data.модель,
        serial_number=data.серийный_номер,
        workshop=data.цех
    )
    db.add(inst)
    db.commit()
    db.refresh(inst)
    return инструмент_в_словарь(inst)


@app.get("/api/v1/инструменты/{inst_id}")
def карточка_инструмента(inst_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    inst = db.query(Instrument).filter(Instrument.id == inst_id).first()
    if not inst:
        raise HTTPException(status_code=404, detail="Инструмент не найден")
    return инструмент_в_словарь(inst)


@app.put("/api/v1/инструменты/{inst_id}")
def обновить_инструмент(
    inst_id: str,
    data: ОбновитьИнструмент,
    db: Session = Depends(get_db),
    user: User = Depends(require_role(UserRole.АДМИНИСТРАТОР, UserRole.МЕТРОЛОГ))
):
    inst = db.query(Instrument).filter(Instrument.id == inst_id).first()
    if not inst:
        raise HTTPException(status_code=404, detail="Инструмент не найден")
    if data.название is not None:
        inst.name = data.название
    if data.цех is not None:
        inst.workshop = data.цех
    if data.дата_следующей_поверки is not None:
        inst.next_verification_date = datetime.fromisoformat(data.дата_следующей_поверки)
    db.commit()
    db.refresh(inst)
    return инструмент_в_словарь(inst)


@app.delete("/api/v1/инструменты/{inst_id}")
def списать_инструмент(
    inst_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(require_role(UserRole.АДМИНИСТРАТОР))
):
    inst = db.query(Instrument).filter(Instrument.id == inst_id).first()
    if not inst:
        raise HTTPException(status_code=404, detail="Инструмент не найден")
    inst.status = InstrumentStatus.СПИСАН
    db.commit()
    return {"сообщение": "Инструмент списан", "статус": "списан"}


@app.post("/api/v1/движения/выдача")
def выдать_инструмент(
    data: ВыдатьИнструмент,
    db: Session = Depends(get_db),
    user: User = Depends(require_role(UserRole.АДМИНИСТРАТОР, UserRole.МЕТРОЛОГ))
):
    inst = db.query(Instrument).filter(Instrument.barcode == data.штрихкод).first()
    if not inst:
        raise HTTPException(status_code=404, detail="Инструмент с таким штрих-кодом не найден")
    if inst.status == InstrumentStatus.ПРОСРОЧЕН:
        raise HTTPException(status_code=400, detail="Поверка просрочена, выдача запрещена")
    if inst.status == InstrumentStatus.СПИСАН:
        raise HTTPException(status_code=400, detail="Инструмент списан")
    if inst.status != InstrumentStatus.ДОСТУПЕН:
        raise HTTPException(status_code=400, detail=f"Инструмент недоступен, статус: {inst.status.value}")
    if inst.next_verification_date and inst.next_verification_date <= datetime.utcnow():
        inst.status = InstrumentStatus.ПРОСРОЧЕН
        db.commit()
        raise HTTPException(status_code=400, detail="Срок поверки истёк")
    worker = db.query(User).filter(User.badge_number == data.табельный_номер_рабочего).first()
    if not worker:
        raise HTTPException(status_code=404, detail="Рабочий с таким табельным номером не найден")
    inst.status = InstrumentStatus.В_РАБОТЕ
    movement = Movement(instrument_id=inst.id, user_id=worker.id, action="выдача")
    db.add(movement)
    db.commit()
    db.refresh(movement)
    return движение_в_словарь(movement)


@app.post("/api/v1/движения/возврат")
def вернуть_инструмент(
    data: ВернутьИнструмент,
    db: Session = Depends(get_db),
    user: User = Depends(require_role(UserRole.АДМИНИСТРАТОР, UserRole.МЕТРОЛОГ))
):
    inst = db.query(Instrument).filter(Instrument.barcode == data.штрихкод).first()
    if not inst:
        raise HTTPException(status_code=404, detail="Инструмент не найден")
    if inst.status != InstrumentStatus.В_РАБОТЕ:
        raise HTTPException(status_code=400, detail="Инструмент не находится в использовании")
    movement = db.query(Movement).filter(
        Movement.instrument_id == inst.id,
        Movement.action == "выдача"
    ).order_by(Movement.issued_at.desc()).first()
    if not movement:
        raise HTTPException(status_code=400, detail="Запись о выдаче не найдена")
    if not data.исправен:
        inst.status = InstrumentStatus.ТРЕБУЕТСЯ_ПОВЕРКА
    elif inst.next_verification_date and inst.next_verification_date <= datetime.utcnow():
        inst.status = InstrumentStatus.ТРЕБУЕТСЯ_ПОВЕРКА
    else:
        inst.status = InstrumentStatus.ДОСТУПЕН
    movement.returned_at = datetime.utcnow()
    movement.condition_ok = data.исправен
    movement.notes = data.примечания
    movement.action = "возврат"
    db.commit()
    db.refresh(movement)
    return движение_в_словарь(movement)


@app.get("/api/v1/движения/история/{inst_id}")
def история_движений(inst_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    movements = db.query(Movement).filter(Movement.instrument_id == inst_id).order_by(Movement.issued_at.desc()).all()
    return [движение_в_словарь(m) for m in movements]



@app.get("/api/v1/поверка/просроченные")
def просроченные_инструменты(
    db: Session = Depends(get_db),
    user: User = Depends(require_role(UserRole.МЕТРОЛОГ, UserRole.АДМИНИСТРАТОР))
):
    cutoff = datetime.utcnow() + timedelta(days=7)
    instruments = db.query(Instrument).filter(
        Instrument.next_verification_date <= cutoff,
        Instrument.status.in_(["доступен", "в_работе", "просрочен"])
    ).all()
    return [инструмент_в_словарь(i) for i in instruments]


@app.post("/api/v1/поверка/провести")
def провести_поверку(
    data: ПровестиПоверку,
    db: Session = Depends(get_db),
    user: User = Depends(require_role(UserRole.МЕТРОЛОГ, UserRole.АДМИНИСТРАТОР))
):
    inst = db.query(Instrument).filter(Instrument.id == data.id_инструмента).first()
    if not inst:
        raise HTTPException(status_code=404, detail="Инструмент не найден")
    cal = Calibration(
        instrument_id=inst.id,
        verification_date=datetime.fromisoformat(data.дата_поверки),
        next_verification_date=datetime.fromisoformat(data.дата_следующей_поверки),
        certificate_number=data.номер_сертификата,
        performed_by=user.id
    )
    inst.status = InstrumentStatus.ДОСТУПЕН
    inst.last_verification_date = datetime.fromisoformat(data.дата_поверки)
    inst.next_verification_date = datetime.fromisoformat(data.дата_следующей_поверки)
    inst.certificate_number = data.номер_сертификата
    db.add(cal)
    db.commit()
    db.refresh(cal)
    return поверка_в_словарь(cal)


@app.post("/api/v1/обслуживание/ежедневная-проверка")
def ежедневная_проверка(db: Session = Depends(get_db)):
    now = datetime.utcnow()
    expired = db.query(Instrument).filter(
        Instrument.next_verification_date <= now,
        Instrument.status.in_([InstrumentStatus.ДОСТУПЕН, InstrumentStatus.В_РАБОТЕ])
    ).all()
    заблокировано = 0
    for inst in expired:
        inst.status = InstrumentStatus.ПРОСРОЧЕН
        заблокировано += 1
    db.commit()
    return {"статус": "ok", "заблокировано": заблокировано, "дата_проверки": now.isoformat()}


@app.get("/")
def главная():
    return {"сервис": "Сервис учёта измерительного инструмента БЕЛАЗ", "версия": "1.0"}