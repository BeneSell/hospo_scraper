from asyncio import constants
from cgitb import text
from datetime import datetime
from opcode import hascompare
from os import sep
from sqlite3 import Date
import string
from unicodedata import category, name
from xmlrpc.client import DateTime
from bs4 import BeautifulSoup
from numpy import sort, true_divide
import requests
import requests_cache
from requests_cache import CachedSession
import pandas as pd
from time import sleep

from flask import Flask, request, render_template, send_from_directory
from flask_restful import Resource, Api, reqparse
from flask_cors import CORS
from flask_restful import reqparse
import re
import os
import hashlib
import json
import pathlib
import ast
import numpy as np
import subscriber

app = Flask(__name__)
app.config["SERVER_NAME"] = "localhost"

# headers = requests.utils.default_headers()

headers = {"User-Agent": "My User Agent 1.0", "From": "youremail@domain.example"}


def render_template_for_each_row(row, length):
    row_as_tag = ""
    with app.app_context():
        row_as_tag = render_template(
            "template_list.html",
            day=row["day"],
            start_time=row["start_time"],
            end_time=row["end_time"],
            location=row["location"],
            difficulty=row["difficulty"],
            extra_information_1=row["extra_information_1"],
            extra_information_2=row["extra_information_2"],
            extra_information_3=row["extra_information_3"],
            extra_information_4=row["extra_information_4"],
            count=row["counter"] + 1,
            length=length,
        )

    return row_as_tag


def pipe_tables(uni_df):

    # for a in temp_soup_today.find_all('a', href=True):
    #     if("node" not in a["href"]):
    #         a.string = a['href']
    #     else:
    #         a['href'] = a.string

    # uni_df = pd.read_html(temp_soup_today.decode_contents())[0]
    # uni_df = uni_df.rename(columns={uni_df.columns[0]:"day", uni_df.columns[1]:"start_time", uni_df.columns[2]:"end_time", uni_df.columns[3]:"difficulty", uni_df.columns[4]:"location", uni_df.columns[5]:"extra_information_1", uni_df.columns[6]:"extra_information_2", uni_df.columns[7]:"extra_information_3", uni_df.columns[8]:"extra_information_4"})
    # uni_df = uni_df.fillna("NA - Keine Angabe")

    uni_df["counter"] = range(len(uni_df))

    new_html = []
    new_html_as_string = ""
    new_html = uni_df.apply(
        lambda row: render_template_for_each_row(row, uni_df["day"].count()), axis=1
    )
    for x in new_html:
        new_html_as_string = new_html_as_string + x
    return new_html_as_string


# def comparing_homepage_data(row, curr_database):
#     hash_yesterday = hashlib.md5(row["text"].encode("utf-8")).hexdigest()
#     hash_today = hashlib.md5(row["text_today"].encode("utf-8")).hexdigest()
#     has_changed = hash_yesterday != hash_today
#     print(has_changed, hash_yesterday, hash_today, "Homepage")

#     if True:
#         temp_soup_today = row["text_today"]

#         for ele in temp_soup_today.findAll(attrs={"style": True}):
#             del ele["style"]
#         temp_text = str(temp_soup_today)

#         piped_text = start_piping(temp_soup_today)

#         temp_dict = {
#             "text": temp_text,
#             "piped_text": piped_text,
#             "link_to_text": row["link_to_text"],
#             "sport_type": row["sport_type_x"],
#             "last_changed": datetime.today(),
#         }
#         return pd.Series(temp_dict)
#     else:
#         # so it dosent overwrite last changed info
#         temp_dict_from_old_base = (
#             curr_database[curr_database["link_to_text"] == row["link_to_text"]]
#             .iloc[0]
#             .to_dict()
#         )
#         return pd.Series(temp_dict_from_old_base)


def cache_manipulation():
    cache_list = []
    german_today = datetime.today().strftime(format="%d.%m.%Y")
    # print(pathlib.Path.cwd())
    for f in pathlib.Path.cwd().iterdir():
        if (
            re.match(".*cache.*sqlite", str(f))
            and not f.is_dir()
            and not german_today in str(f)
        ):
            cache_list.append({"file": f, "last_modified": f.lstat().st_mtime})
    df_cache_sqlite = pd.DataFrame(cache_list)
    last_modified_file = df_cache_sqlite.sort_values(
        by="last_modified", ascending=False
    ).iloc[0]

    # requests_cache.install_cache('demo_cache')

    # Connection to web page
    # the function "install_cache" wants the session name without the .sqlite
    session_file_name = (
        str(last_modified_file["file"]).split("\\")[-1].replace(".sqlite", "")
    )
    requests_cache.install_cache(session_file_name)
    session = CachedSession(session_file_name)
    print(session_file_name)

    session_today = CachedSession(cache_name="./cache" + german_today + ".sqlite")
    requests_cache.install_cache(cache_name="./cache" + german_today + ".sqlite")
    print("cache" + german_today)

    return session, session_today


def get_table(node_id, session):
    sleep(1)
    api_url = "https://api.hochschulsport-koeln.de/json/v2/course/" + node_id + "/dates"
    response = session.get(api_url, headers=headers)

    # if repsonse is not empty
    if response.json():
        # json to dataframe
        uni_df = pd.DataFrame(response.json())

        uni_df["adress"] = (
            uni_df["field_postleitzahl"]
            + " "
            + uni_df["field_stadt"]
            + " "
            + uni_df["field_strasse"]
        )

        uni_df = uni_df.rename(
            columns={
                "level": "difficulty",
                "start": "start_time",
                "end": "end_time",
                "day": "day",
                "place": "location",
                "notes": "extra_information_1",
                "registration": "registration",
                "cancellation": "cancellation",
                "terminlos": "extra_information_1",
                "period": "extra_information_2",
                "placeid": "placeid",
                "registration_at_place": "extra_information_3",
                "field_wochentag_1": "field_weekday_1",
                "field_kurzname": "extra_information_4",
            }
        )
        new_table = pipe_tables(uni_df=uni_df)

        return new_table


def get_source():
    session, session_today = cache_manipulation()
    url = "https://api.hochschulsport-koeln.de/entity/menu/main/tree"
    url_api = "https://api.hochschulsport-koeln.de/json/v2/course/"

    curr_database = pd.read_csv("./sports.csv", sep=";")
    response = session_today.get(url, headers=headers)

    # soup = BeautifulSoup(s, 'html.parser')
    menu_parents = [x for x in response.json()]
    row_list = []

    # for the homepage
    sleep(1)

    # loop for the topics
    # exp: fitness, gesundheitssport etc
    for x in menu_parents:

        sport_type = x["link"]["title"]

        if len(x["subtree"]) > 0:
            # loop for the sports
            # football, volleyball etc
            for y in x["subtree"]:

                # if route_parameters is empty
                if not y["link"]["route_parameters"]:
                    continue

                endpoint = y["link"]["route_parameters"]["node"]
                title = y["link"]["title"]

                temp_response = session.get(url_api + endpoint, headers=headers)
                temp_today_response = session_today.get(
                    url_api + endpoint, headers=headers
                )

                if temp_response.json() == []:
                    continue

                temp_soup = BeautifulSoup(
                    temp_response.json()[0]["body"], "html.parser"
                )
                temp_soup_today = BeautifulSoup(
                    temp_today_response.json()[0]["body"], "html.parser"
                )
                piped_text = ""

                hash_yesterday = hashlib.md5(
                    temp_soup.decode_contents().encode("utf-8")
                ).hexdigest()
                hash_today = hashlib.md5(
                    temp_soup_today.decode_contents().encode("utf-8")
                ).hexdigest()
                has_changed = hash_yesterday != hash_today

                # if true it has changed
                has_endpoint_changed = (
                    curr_database[curr_database["link_to_text"] == endpoint][
                        "link_to_text"
                    ].count()
                    == 0
                )

                print(has_changed, has_endpoint_changed, hash_yesterday, hash_today)

                if has_changed or has_endpoint_changed:

                    temp_text = temp_soup_today.decode_contents()

                    sleep(1)
                    piped_text = (
                        str(temp_text) + "\n" + str(get_table(endpoint, session))
                    )

                    temp_dict = {
                        "text": temp_text,
                        "piped_text": piped_text,
                        "title": title,
                        "link_to_text": endpoint,
                        "sport_type": sport_type,
                        "last_changed": datetime.today(),
                    }

                    row_list.append(temp_dict)
                    if not has_endpoint_changed:
                        pass
                        # subscriber.send_message_to_user_list(endpoint)
                else:
                    # so it dosent overwrite last changed info
                    # print(curr_database[curr_database["link_to_text"] == endpoint]["link_to_text"])

                    if (
                        curr_database[curr_database["link_to_text"] == endpoint][
                            "link_to_text"
                        ].count()
                        == 0
                    ):
                        # endpoint changed
                        pass
                    temp_dict_from_old_base = (
                        curr_database[(curr_database["link_to_text"] == endpoint)]
                        .iloc[0]
                        .to_dict()
                    )
                    row_list.append(temp_dict_from_old_base)
                    pass
                # to be nice
                sleep(1)

    pd.DataFrame(row_list).to_csv("sports.csv", sep=";")
    print("finished")


get_source()
