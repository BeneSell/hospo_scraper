import requests
import urllib.parse
import pandas as pd
import json
from datetime import datetime, timedelta
import time
import re

# load from jsonfile to variable

bot_infos = None
with open("botinfos.json", "r") as file:
    file.seek(0)
    bot_infos = json.loads(file.read())


def set_updated_id(new_updated_id):
    with open("update_id_file.txt", "w") as file:
        file.write(str(new_updated_id))


def get_updated_id():
    with open("update_id_file.txt", "r") as file:
        file.seek(0)
        update_id = file.read()
        return int(update_id)


def send_message(chat_id, notification_text):
    notification_text = urllib.parse.quote(notification_text)
    bot_token = bot_infos["bot_token"]
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage?chat_id={chat_id}&text={notification_text}"
    return requests.get(url)


def clicked_on_subscried(link_to_text):
    url = f"https://t.me/test_21091998_bot?start={link_to_text}"
    # 10 mins
    time_period = 10
    # 10 seconds
    intervall = 10
    end_time = datetime.now() + timedelta(minutes=time_period)
    while datetime.now() < end_time:
        result = serach_for_new_user(link_to_text)
        print(result)
        if result != "no Message":
            return result
        time.sleep(intervall)
    return "no Message found"
    # serach ten mins for new user
    # send
    pass


umlautMap = {
    "\u00dc": "UE",
    "\u00c4": "AE",
    "\u00d6": "OE",
    "\u00fc": "ue",
    "\u00e4": "ae",
    "\u00f6": "oe",
    "\u00df": "ss",
}


def replaceUmlaute(to_replace: str):

    spcial_char_map = {ord("\u00e4"): "ae", ord("\u00fc"): "ue", ord("\u00f6"): "oe"}
    return to_replace.translate(spcial_char_map)


# ?offset=343126594
# use offset to only get one
def serach_for_new_user(link_to_text):
    bot_token = bot_infos["bot_token"]
    off_set_para = ""
    update_id = get_updated_id()
    if update_id != 0:
        off_set_para = f"?offset={update_id}"
        pass
    url = f"https://api.telegram.org/bot{bot_token}/getUpdates{off_set_para}"
    response = requests.get(url)

    message_dicts = json.loads(response.text)["result"]

    # link_to_text_for_telegram = replaceUmlaute(link_to_text)
    link_to_text_for_telegram = link_to_text
    link_to_text_for_telegram = re.sub(r"[\W_]+", "", link_to_text_for_telegram)

    try:
        print(
            [
                x
                for x in message_dicts
                if x["message"]["text"] == f"/start {link_to_text_for_telegram}"
            ]
        )
        new_user = [
            x
            for x in message_dicts
            if x["message"]["text"] == f"/start {link_to_text_for_telegram}"
        ][-1]
    except:
        return "no Message"
    # store for better pulling
    set_updated_id(new_user["update_id"] + 1)
    # i forgot why there is no / here but we need one
    # properly im deleting it in the process but i cant find it and im exhausted
    link_to_text = "/" + link_to_text
    return add_to_json(str(new_user["message"]["chat"]["id"]), link_to_text)

    return new_user
    pass


# json dict
# {"link_to_text": [all_chat_ids_which_want_infos]}


def change_json_file(new_dict):
    with open("subscriber.json", "w") as f:
        f.write(json.dumps(new_dict))


def get_subscriber_file():
    with open("subscriber.json", "r+") as file:
        return json.load(file)


def create_json(unique_link_to_texts: list, chat_list: list) -> dict:

    result_dict = {}
    for link_to_text in unique_link_to_texts:
        result_dict[link_to_text] = [
            y["chat_id"] for y in chat_list if y["link_to_text"] == link_to_text
        ]
    change_json_file(result_dict)

    return "created"


def add_to_json(new_chat_id, link_to_text):
    created_dict = get_subscriber_file()
    if len([x for x in created_dict[link_to_text] if new_chat_id == x]) != 0:
        send_message(new_chat_id, f"Du hast dich bereits zu {link_to_text} abonniert.")
        return "already_subscripted"

    # always at least empty list!
    created_dict[link_to_text].append(new_chat_id)

    change_json_file(created_dict)

    send_message(new_chat_id, f"Du hast {link_to_text} abboniert.")

    return "now_subscripted"


def remove_from_json(remove_chat_id, link_to_text, created_dict: dict):
    created_dict = get_subscriber_file()

    # always at least empty list!
    created_dict[link_to_text].remove(remove_chat_id)

    change_json_file(created_dict)
    return "unsuscripted"


def get_user_list_by_link_to_text(link_to_text):
    created_dict = get_subscriber_file()
    return created_dict[link_to_text]


def send_message_to_user_list(link_to_text):

    user_list = get_user_list_by_link_to_text(link_to_text)
    for x in user_list:
        # TODO den link ordentlich machen
        send_message(
            x,
            f"Hey es gibt neue Infos zu {link_to_text}. :) schau es dir hier an https://hosposcraper.pythonanywhere.com/index/{link_to_text} ",
        )
