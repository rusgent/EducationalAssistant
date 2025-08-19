from datetime import datetime
from aiogram import Bot
from .db import async_engine, async_session
from sqlalchemy import select, insert, update
import os
import json
from .models import *


class Database:
    @staticmethod
    async def db_start():
        await Database.create_tables()
        await Database.db_succes()

    @staticmethod
    async def create_tables():
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    @staticmethod
    async def db_succes():
        async with async_session() as session:
            print("Подключение к БД прошло успешно!")

    @staticmethod
    async def get_all_users():
        async with async_session() as session:
            query = select(Users)
            result = await session.execute(query)
            list_users = result.scalars().all()
            return list_users
            # [ОбьектЮзер1.id]
            
    @staticmethod
    async def get_all_prem_users():
        async with async_session() as session:
            query = select(PremiumUsers)
            res = await session.execute(query)
            list_prem_users = res.scalars().all()
            return list_prem_users
    
    
    @staticmethod
    async def del_user(user_id: int):
        async with async_session() as session:
            query = select(Users).where(Users.user_id == user_id)
            res = await session.execute(query)
            user = res.scalar()
            
            if user:
                await session.delete(user)
                await session.commit()
                return True
            else:
                return False
            

    @staticmethod
    async def get_shedule_for_cls(cls: str):
        async with async_session() as session:
            query = select(SchoolSchedule.lessons).where(SchoolSchedule.cls_rus == cls)
            result = await session.execute(query)
            lessons = result.scalar()
            if lessons:
                return lessons
            return None

    @staticmethod
    async def add_user_and_check_new_username(user_id: int, username: str, fullname: str, bot: Bot):
        async with async_session() as session:
            query = select(Users.username).where(Users.user_id == user_id)
            res = await session.execute(query)
            old_username = res.scalar()

            if old_username is None:
                
                insert_new_user = insert(Users).values(
                    user_id=user_id,
                    username=username,
                    fullname=fullname
                )
                
                result = await session.execute(insert_new_user)
                new_user_id = result.inserted_primary_key[0]
                
                await bot.send_message(chat_id=os.getenv("RUS_ID"), text=(f'Новый пользователь зарегистрирован!\nID - {user_id}\nusername - @{username}\nfullname - {fullname}\n\nВсего уже {new_user_id} пользователей!'))

            else:
                if old_username != username:
                    update_user = (update(Users)
                                   .where(Users.user_id == user_id)
                                   .values(username=username,
                                           fullname=fullname))
                    await session.execute(update_user)
            await session.commit()
            
            
    @staticmethod
    async def check_and_update_username_prem_table(user_id: int, new_username: str, new_fullname: str):
        async with async_session() as session:
            query = select(PremiumUsers.username).where(PremiumUsers.tg_id == user_id)
            old_username = session.execute(query)
            if new_username != old_username:
                query = (update(PremiumUsers)
                         .where(PremiumUsers.tg_id == user_id)
                         .values(username=new_username,
                                 fullname=new_fullname))
            await session.commit()


    @staticmethod
    async def check_user(user_id: int):
        async with async_session() as session:
            query = select(Users).where(Users.user_id == user_id)
            res = await session.execute(query)
            user = res.scalar()
            return user



    @staticmethod
    async def set_favcls(user_id: int, favcls: str):
        async with async_session() as session:
            query = select(Users.favcls).where(Users.user_id == user_id)
            res = await session.execute(query)
            favcls_list = res.scalar()

            if favcls_list and favcls_list[0]:
                new_favcls_list = favcls_list
                if favcls not in new_favcls_list:
                    new_favcls_list.append(favcls)

            else:
                new_favcls_list = [favcls]

            favcls_list_json = new_favcls_list

            query = update(Users).where(Users.user_id == user_id).values(
                favcls=favcls_list_json
            )

            await session.execute(query)
            await session.commit()

    @staticmethod
    async def get_favcls_list(user_id: int):
        async with async_session() as session:
            query = select(Users.favcls).where(Users.user_id == user_id)
            res = await session.execute(query)
            res = res.scalar()

            if res:
                favcls_list = res
                return favcls_list
            else:
                return []

    @staticmethod
    async def del_favcls(user_id: int, cls: str):
        async with async_session() as session:
            favcls_list = await Database.get_favcls_list(user_id)

            if cls in favcls_list:
                favcls_list.remove(cls)

                query = update(Users).where(Users.user_id == user_id).values(
                    favcls=favcls_list
                )
                await session.execute(query)
                await session.commit()
                return True
            else:
                return False

    @staticmethod
    async def get_cls_list():
        async with async_session() as session:
            query = select(SchoolSchedule.cls_rus)
            res = await session.execute(query)
            res = res.scalars() # [9а, 9б]
            return res

    @staticmethod
    async def save_result(user_id: int, result: str):
        async with async_session() as session:
            query = insert(Results).values(
                user_id=user_id,
                result=result,
                timestamp=datetime.now()
            )
            await session.execute(query)
            await session.commit()

    @staticmethod
    async def check_result(user_id: int):
        async with async_session() as session:
            query = select(Results.result, Results.timestamp).where(Results.user_id == user_id)
            res = await session.execute(query)
            res = res.all()
            return res

    @staticmethod
    async def set_task(user_id: int, task_name: str, desc_task: str):
        async with async_session() as session:
            query = insert(Tasks).values(
                user_id=user_id,
                task_name=task_name,
                description=desc_task
            )

            await session.execute(query)
            await session.commit()
            
    @staticmethod
    async def get_tasks_list(user_id: int):
        async with async_session() as session:
            query = select(Tasks).where(Tasks.user_id == user_id)

            tasks = await session.execute(query)
            tasks = tasks.scalars().all()
            return tasks
        
    
    @staticmethod
    async def get_task(task_id: int):
        async with async_session() as session:
            query = select(Tasks).where(Tasks.id == task_id)

            task = await session.execute(query)
            task = task.scalar()
            return task
        
    @staticmethod
    async def edit_task_name(task_id: int, new_task_name: str):
        async with async_session() as session:
            query = update(Tasks).where(Tasks.id == task_id).values(
                task_name=new_task_name
            ).returning(Tasks)
            res = await session.execute(query)
            update_task = res.scalar()
            await session.commit()
            return update_task
            
    @staticmethod
    async def edit_task_desc(task_id: int, new_task_desc: str):
        async with async_session() as session:
            query = update(Tasks).where(Tasks.id == task_id).values(
                description=new_task_desc
            ).returning(Tasks)
            res = await session.execute(query)
            update_task = res.scalar()
            await session.commit()
            return update_task
        
    @staticmethod
    async def del_task(task_id: int):
        async with async_session() as session:
            query = select(Tasks).where(Tasks.id == task_id)
            res = await session.execute(query)
            task = res.scalar()
            
            if task:
                await session.delete(task)
                await session.commit()
                return True
            else:
                return False
        
    @staticmethod
    async def edit_school_menu_id(menu_id: int, date: str):
        async with async_session() as session:
            query = update(Menu).where(Menu.id == 1).values(
                menu_id=menu_id,
                date=date
            )
            res = await session.execute(query)
            await session.commit()
        
    @staticmethod
    async def get_school_menu_id():
        async with async_session() as session:
            query = select(Menu)
            res = await session.execute(query)
            menu = res.scalar()

            if menu:
                return menu
            else:
                return False
            
    @staticmethod
    async def check_school_notif_menu(user_id: int):
        async with async_session() as session:
            query = select(Users.is_notif).where(Users.user_id == user_id)
            res = await session.execute(query)
            is_notif = res.scalar()
            return str(is_notif)
        
    @staticmethod
    async def edit_vkl_school_notif_menu(user_id: int):
        async with async_session() as session:
            query = update(Users).where(Users.user_id == user_id).values(
                is_notif=1
            )
            res = await session.execute(query)
            await session.commit()
            
    @staticmethod
    async def edit_otkl_school_notif_menu(user_id: int):
        async with async_session() as session:
            query = update(Users).where(Users.user_id == user_id).values(
                is_notif=0
            )
            res = await session.execute(query)
            await session.commit()
            
    @staticmethod
    async def check_in_premium_users_table(user_id: int):
        async with async_session() as session:
            query = select(PremiumUsers).where(PremiumUsers.tg_id == user_id)
            res = await session.execute(query)
            user = res.scalar()
            
            return user

    @staticmethod
    async def check_premium(user_id: int):
        async with async_session() as session:
            query = select(PremiumUsers.premium_end_date).where(PremiumUsers.tg_id == user_id)
            res_date = (await session.execute(query)).scalar()
            
            # 2 - Подписка Активна
            # 1 - Сегодня полс день
            # 0 - Истекла
            today = datetime.now().date() 
            if res_date:
                if today < res_date:
                    return 2
                elif today == res_date:
                    return 1
            else:
                return 0
            
    @staticmethod
    async def add_new_prem_user(user_id, username, fullname, premium_end_date, bot: Bot, money, days):
        async with async_session() as session:
            insert_new_user = insert(PremiumUsers).values(
                    tg_id=user_id,
                    username=username,
                    fullname=fullname,
                    premium_end_date=premium_end_date
                    )
            
            result = await session.execute(insert_new_user)
            users = await Database.get_all_prem_users()
            count_prem_user = len(users) + 1
                
            await bot.send_message(chat_id=os.getenv("RUS_ID"), text=(f'Новый пользователь активировал подписку за {money} рублей на {days} дней!\n'
                                                                      f'ID - {user_id}\n@{username}\n'
                                                                      f'fullname - {fullname}\n\n'
                                                                      f'Всего уже {count_prem_user} премиум-пользователей!'))
            
            await session.commit()
            
            
    @staticmethod
    async def del_prem_user(user_id):
        async with async_session() as session:
            query = select(PremiumUsers).where(PremiumUsers.tg_id == user_id)
            res = await session.execute(query)
            user = res.scalar()
            
            if user:
                await session.delete(user)
                await session.commit()
                return True
            else:
                return False
    

    







