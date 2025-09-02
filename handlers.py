from aiogram import types, F, Router
from aiogram.filters import Command
from aiogram.filters.command import Command
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from service import (
    get_question,
    new_quiz,
    get_quiz_index,
    update_quiz_index,
    append_right_answer,
    get_right_answers,
    get_count_questions,
    get_quest,
)
import os

router = Router()

PHOTO_URL = os.getenv("PHOTO_URL")
[]


@router.callback_query(F.data == "right_answer")
async def right_answer(callback: types.CallbackQuery):

    await callback.bot.edit_message_reply_markup(
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
        reply_markup=None,
    )

    await append_right_answer(callback.from_user.id)
    await callback.message.answer("Верно!")
    current_question_index = await get_quiz_index(callback.from_user.id)
    # Обновление номера текущего вопроса в базе данных
    current_question_index += 1
    await update_quiz_index(callback.from_user.id, current_question_index)

    if current_question_index < (await get_count_questions()):
        await get_question(callback.message, callback.from_user.id)
    else:
        count_right_answers = await get_right_answers(callback.from_user.id)
        await callback.message.answer(
            f"Это был последний вопрос. Квиз завершен!  Вы правильно ответили на {count_right_answers} вопросов"
        )


@router.callback_query(F.data == "wrong_answer")
async def wrong_answer(callback: types.CallbackQuery):
    await callback.bot.edit_message_reply_markup(
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
        reply_markup=None,
    )

    # Получение текущего вопроса из БД состояний пользователя
    current_question_index = await get_quiz_index(callback.from_user.id)
    question = await get_quest(current_question_index)
    correct_option = question[0]["correct_option"]

    await callback.message.answer(
        f"Неправильно. Правильный ответ: {question[0]['options'].split(";")[correct_option]}"
    )

    # Обновление номера текущего вопроса в БД
    current_question_index += 1
    await update_quiz_index(callback.from_user.id, current_question_index)

    if current_question_index < (await get_count_questions()):
        await get_question(callback.message, callback.from_user.id)
    else:
        count_right_answers = await get_right_answers(callback.from_user.id)
        await callback.message.answer(
            f"Это был последний вопрос. Квиз завершен! Вы правильно ответили на {count_right_answers} вопросов"
        )


# Хэндлер на команду /start
@router.message(Command("start"))
async def cmd_start(message: types.Message):
    builder = ReplyKeyboardBuilder()
    builder.add(types.KeyboardButton(text="Начать игру"))
    await message.answer(
        "Добро пожаловать в квиз!", reply_markup=builder.as_markup(resize_keyboard=True)
    )


# Хэндлер на команду /quiz
@router.message(F.text == "Начать игру")
@router.message(Command("quiz"))
async def cmd_quiz(message: types.Message):
    await message.answer_photo(photo=PHOTO_URL, caption="Давайте начнем квиз!")
    await new_quiz(message)
