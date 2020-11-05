from telegram.ext import (
    Filters,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler)

from ..utils.consts import TEXT
from ..tamplates.messages import (
    reply,
    ask_a_boolean_question)
from ..database.manipulation import (
    add_category as add_category_in_db,
    add_photo)


(END                         ,
ASK_FOR_CATEGORY_DESCRIPTION ,
ASK_FOR_CATEGORY_TAGS        ,
ASK_FOR_CATEGORY_PHOTO       ,
ASK_IF_ITS_ALL_OK            ) = range(-1, 4)


pattern_to_save_everything = "boolean_response"


def ask_for_category_name(update, context):
    text = TEXT["ask_for_category_name"]
    update.message.reply_text(text)
    return ASK_FOR_CATEGORY_DESCRIPTION


def ask_for_category_description(update, context):
    category_name = update.message.text
    context.user_data["category_name"] = category_name
    text = TEXT["ask_for_category_description"]
    update.message.reply_text(text)
    return ASK_FOR_CATEGORY_TAGS


def ask_for_category_tags(update, context):
    category_description = update.message.text
    context.user_data["category_description"] = category_description
    text = TEXT["ask_for_category_tags"]
    update.message.reply_text(text)
    return ASK_FOR_CATEGORY_PHOTO


def ask_for_category_photo(update, context):
    category_tags = update.message.text
    context.user_data["category_tags"] = category_tags
    text = TEXT["ask_for_category_photo"]
    update.message.reply_text(text)
    return ASK_IF_ITS_ALL_OK


def save_photo_in_user_data(update, context):
    photo = update.message.photo[0]
    photo = photo.get_file()
    context.user_data["photo"] = photo


def save_category_info_in_db(update, context):
    photo = context.user_data["photo"]
    add_photo(
        photo.file_id,
        photo.download_as_bytearray())
    add_category_in_db(
        context.user_data["category_name"],
        context.user_data["category_description"],
        context.user_data["category_tags"],
        photo.file_id)


def ask_if_its_all_ok(update, context):
    save_photo_in_user_data(update, context)
    ask_a_boolean_question(update, context, pattern_to_save_everything)


def catch_response(update, context):
    query = update.callback_query
    if query.data == pattern_to_save_everything + "OK":
        save_category_info_in_db(update, context)
        text = TEXT["information_stored"]
    else:
        text = TEXT["canceled_operation"]
    query.edit_message_text(text)
    return END


def cancel_add_category(update, context):
    text = TEXT["canceled_operation"]
    update.message.reply_text(text)
    return END


add_category_command = (
    CommandHandler("add_category", ask_for_category_name))


add_category = ConversationHandler(
    entry_points = [add_category_command],
    states = {
        ASK_FOR_CATEGORY_DESCRIPTION : [
            MessageHandler(
                Filters.text, 
                ask_for_category_description)
            ],
        ASK_FOR_CATEGORY_TAGS : [
            MessageHandler(
                Filters.text, 
                ask_for_category_tags)
            ],
        ASK_FOR_CATEGORY_PHOTO : [
            MessageHandler(
                Filters.text, 
                ask_for_category_photo)
            ],
        ASK_IF_ITS_ALL_OK : [
            MessageHandler(
                Filters.photo,
                ask_if_its_all_ok),
            CallbackQueryHandler(
                catch_response,
                pattern=pattern_to_save_everything
                )
            ]
        },
    fallbacks = [MessageHandler(Filters.all, cancel_add_category)]

    )


