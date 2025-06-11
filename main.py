import asyncio
import os
import sys
import subprocess
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.filters import Command
from aiogram.types import Message, FSInputFile

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram import F

from recognize import download_audio_snippet, recognize_with_shazam
from spotify import search_tracks, add_track_to_playlist, check_track_in_playlist
        
# Пароль и токен
ACCESS_PASSWORD = "1234"
TOKEN_API = "7692359451:AAEicTS7yoAtoY0KifOB-nJ8jqnuD9UbOZo"

# Бот
bot = Bot(token=TOKEN_API, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# Хранилище авторизованных пользователей
authorized_users = set()

pending_choices = {}

@dp.message(Command("start"))
async def start_handler(message: Message):
    user_id = message.from_user.id

    if user_id not in authorized_users:
        await message.answer("🔒 Введите пароль для доступа:")
    else:
        await message.answer("✅ Вы уже авторизованы. Отправьте ссылку на видео 🎧")

@dp.message(Command("restart"))
async def restart_handler(message: Message):
    await message.answer("♻️ Перезапускаю бота...")
    python = sys.executable
    os.execl(python, python, *sys.argv)



@dp.message()
async def link_or_password_handler(message: Message):
    user_id = message.from_user.id
    text = message.text.strip()

    # Проверка пароля
    if user_id not in authorized_users:
        if text == ACCESS_PASSWORD:
            authorized_users.add(user_id)
            await message.answer("✅ Пароль верный. Отправьте ссылку на видео 🎧")
        else:
            await message.answer("❌ Неверный пароль. Попробуйте снова.")
        return

    # Проверка ссылки
    if not text.startswith("http"):
        await message.answer("❌ Это не похоже на ссылку. Попробуй ещё раз.")
        return

    await message.answer("🎧 Извлекаю аудио и распознаю трек…")

    try:
        snippet_path = download_audio_snippet(text)

        # Распознавание
        result = await recognize_with_shazam(snippet_path)
        track = result.get("track", {})
        title = track.get("title", "Без названия")
        subtitle = track.get("subtitle", "")
        artist = subtitle if isinstance(subtitle, str) else ", ".join(a['name'] for a in subtitle)



        # spotify_track_id = search_track(title, artist)
        # if spotify_track_id:
        #     added = add_track_to_playlist(spotify_track_id)
        #     if added:
        #         in_playlist = check_track_in_playlist(spotify_track_id)
        #         if in_playlist:
        #             await message.answer("✅ Трек успешно добавлен в Spotify плейлист!")
        #         else:
        #             await message.answer("⚠️ Добавлен, но не найден в плейлисте.")
        #     else:
        #         await message.answer("❌ Не удалось добавить в плейлист.")
        # else:
        #     await message.answer("❌ Трек не найден в Spotify.")
            
        #     from spotify import search_tracks, add_track_to_playlist

        spotify_tracks = search_tracks(title, artist)

        if not spotify_tracks:
            await message.answer("❌ Трек не найден в Spotify.")
        else:
            # Сохраняем в память
            pending_choices[user_id] = spotify_tracks

            track_buttons = [
                [InlineKeyboardButton(
                    text=f"{t['name']} — {t['artist']}", callback_data=f"choose_{i}"
                )]
                for i, t in enumerate(spotify_tracks)
            ]

            # Добавляем кнопку "Попробовать заново"
            track_buttons.append([
                InlineKeyboardButton(
                    text="🔁 Отправить новую ссылку", callback_data="back"
                )
            ])

            kb = InlineKeyboardMarkup(inline_keyboard=track_buttons)


            await message.answer("🔎 Вот, что нашёл в Spotify. Выбери правильный трек:", reply_markup=kb)

        # Ссылка на трек
        song_link = track.get("url", "") or track.get("share", {}).get("href", "")
        text = f"<b>{title}</b> — {artist}"
        if song_link:
            text += f"\n<a href='{song_link}'>Слушать</a>"
        await message.answer(text)

        # Удаляем сниппет
        os.remove(snippet_path)

    except Exception as e:
        await message.answer(f"⚠️ Произошла ошибка: <code>{str(e)}</code>")

@dp.callback_query(F.data == "back")
async def handle_back(callback: CallbackQuery):
    user_id = callback.from_user.id
    pending_choices.pop(user_id, None)
    await callback.message.edit_text("🔄 Можешь отправить новую ссылку для распознавания.")


@dp.callback_query(F.data.startswith("choose_"))
async def handle_track_choice(callback: CallbackQuery):
    user_id = callback.from_user.id
    index = int(callback.data.split("_")[1])

    if user_id not in pending_choices or index >= len(pending_choices[user_id]):
        await callback.answer("⚠️ Неверный выбор.", show_alert=True)
        return

    selected = pending_choices[user_id][index]
    added = add_track_to_playlist(selected["id"])

    if added:
        await callback.message.edit_text(
            f"✅ Добавлено в плейлист:\n<b>{selected['name']}</b> — {selected['artist']}\n"
            f"<a href='{selected['url']}'>Слушать в Spotify</a>"
        )
    else:
        await callback.message.edit_text("❌ Не удалось добавить трек в плейлист.")

    del pending_choices[user_id]

async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
