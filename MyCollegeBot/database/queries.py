from sqlalchemy import select, update
from database.db import async_session
from database.models import User, Ticket

async def add_user(tg_id: int, name: str, group: str, phone: str = None):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.telegram_id == tg_id))
        if not user:
            session.add(User(telegram_id=tg_id, name=name, group_name=group, phone=phone))
            await session.commit()

async def get_user(tg_id: int):
    async with async_session() as session:
        return await session.scalar(select(User).where(User.telegram_id == tg_id))

async def get_all_users():
    async with async_session() as session:
        result = await session.execute(select(User))
        return result.scalars().all()

async def create_ticket(tg_id: int, text: str, photo: str = None):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.telegram_id == tg_id))
        if user:
            new_ticket = Ticket(user_id=user.id, text=text, photo=photo)
            session.add(new_ticket)
            await session.commit()
            return new_ticket.id

async def get_user_tickets(tg_id: int):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.telegram_id == tg_id))
        if user:
            result = await session.execute(select(Ticket).where(Ticket.user_id == user.id).order_by(Ticket.created_at.desc()))
            return result.scalars().all()
    return []

async def get_all_tickets(status_filter=None):
    async with async_session() as session:
        query = select(Ticket, User).join(User) 
        if status_filter:
            query = query.where(Ticket.status == status_filter)
        result = await session.execute(query.order_by(Ticket.created_at.desc()))
        return result.all() 

async def update_ticket_status(ticket_id: int, new_status: str):
    async with async_session() as session:
        await session.execute(update(Ticket).where(Ticket.id == ticket_id).values(status=new_status))
        await session.commit()
        
async def get_ticket_by_id(ticket_id: int):
     async with async_session() as session:

        query = select(Ticket, User).join(User).where(Ticket.id == ticket_id)
        result = await session.execute(query)
        return result.first()