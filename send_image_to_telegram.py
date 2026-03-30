import asyncio
import os
from telegram import Bot

async def send_photo():
    token = "8328278713:AAFXTVblPtep5dQBFBVcuMdsaSmrsoGr5QE"
    # User's chat id defaults to what we typically use or we can ask for updates. We will use a typical broadcast or known admin ID if available, else we fetch from updates.
    
    bot = Bot(token=token)
    
    chat_id = "6735404856"
    print(f"Sending to chat_id: {chat_id}")
    
    photo_path = r"C:\Users\sunjo\.gemini\antigravity\brain\8008be59-c485-4610-bbbc-0ee44e613c7b\luca_anime_portrait_1772454185826.png"
    
    with open(photo_path, 'rb') as photo:
        await bot.send_photo(
            chat_id=chat_id, 
            photo=photo, 
            caption="충성! 🫡 대표님, 저 Luca 부장의 새로운 공식 프로필(Anime Ver.)입니다! \n\n앞으로 완벽한 일처리는 물론, 중간중간 재밌는 표정으로 업무의 지루함도 싹 날려드리겠습니다! 🚀"
        )
    print("Photo sent successfully!")

if __name__ == "__main__":
    asyncio.run(send_photo())
