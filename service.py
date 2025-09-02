from database import pool, execute_update_query, execute_select_query
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import types


def generate_options_keyboard(answer_options, right_answer):
    builder = InlineKeyboardBuilder()

    for option in answer_options:
        builder.add(
            types.InlineKeyboardButton(
                text=option,
                callback_data=(
                    "right_answer" if option == right_answer else "wrong_answer"
                ),
            )
        )

    builder.adjust(1)
    return builder.as_markup()


async def get_question(message, user_id):

    id_question = await get_quiz_index(user_id)

    query = f"""
        DECLARE $id AS Uint64;
        
        SELECT * FROM `questions` WHERE `id` = $id
    """

    question = execute_select_query(pool, query, id=id_question)

    correct_index = question[0]["correct_option"]
    opts = question[0]["options"].split(";")
    kb = generate_options_keyboard(opts, opts[correct_index])
    await message.answer(
        f"{question[0]['question']}", reply_markup=kb
    )


async def get_quest(id_question):
    query = f"""
        DECLARE $id AS Uint64;
        
        SELECT * FROM `questions` WHERE `id` = $id
    """

    question = execute_select_query(pool, query, id=id_question)
    return question

async def new_quiz(message):
    user_id = message.from_user.id
    current_question_index = 0
    await reset_right_answer(user_id)
    await update_quiz_index(user_id, current_question_index)
    await get_question(message, user_id)


async def get_quiz_index(user_id):
    get_user_index = f"""
        DECLARE $user_id AS Uint64;

        SELECT question_index
        FROM `quiz_state`
        WHERE user_id == $user_id;
    """
    results = execute_select_query(pool, get_user_index, user_id=user_id)

    if len(results) == 0:
        return 0
    if results[0]["question_index"] is None:
        return 0
    return results[0]["question_index"]


async def update_quiz_index(user_id, question_index):
    set_quiz_state = f"""
        DECLARE $user_id AS Uint64;
        DECLARE $question_index AS Uint64;

        UPSERT INTO `quiz_state` (`user_id`, `question_index`)
        VALUES ($user_id, $question_index);
    """

    execute_update_query(
        pool,
        set_quiz_state,
        user_id=user_id,
        question_index=question_index,
    )


async def reset_right_answer(user_id):
    query = f"""
        DECLARE $user_id AS Uint64;
        
        UPSERT INTO `quiz_state` (`user_id`, `right_answer`)
        VALUES($user_id, 0) 
    """

    execute_update_query(
        pool,
        query,
        user_id=user_id,
    )


async def append_right_answer(user_id):
    query = f"""
        DECLARE $user_id AS Uint64;
        
        UPDATE `quiz_state` SET `right_answer` = `right_answer` + 1 WHERE `user_id` = $user_id
    """

    execute_update_query(
        pool,
        query,
        user_id=user_id,
    )

async def get_right_answers(user_id):
    query = f"""
        DECLARE $user_id AS Uint64;
        
        SELECT `right_answer` FROM `quiz_state` WHERE `user_id` = $user_id
    """

    results = execute_select_query(
        pool, 
        query, 
        user_id=user_id
    )

    if len(results) == 0:
        return 0
    if results[0]["right_answer"] is None:
        return 0
    return results[0]["right_answer"]


async def get_count_questions():
    query = f"""
        SELECT COUNT(*) FROM questions
    """

    result = execute_select_query(
        pool, 
        query
    )

    if len(result) == 0:
        return 0
    if result[0]["column0"] is None:
        return 0
    return result[0]["column0"]
