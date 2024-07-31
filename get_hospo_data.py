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


headers = requests.utils.default_headers()

headers.update(
    {
        "User-Agent": "My User Agent 1.0",
    }
)


def render_template_for_each_row(row, length):
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


def pipe_tables(temp_soup_today):

    for a in temp_soup_today.find_all("a", href=True):
        if "node" not in a["href"]:
            a.string = a["href"]
        else:
            a["href"] = a.string

    uni_df = pd.read_html(temp_soup_today.decode_contents())[0]
    uni_df = uni_df.rename(
        columns={
            uni_df.columns[0]: "day",
            uni_df.columns[1]: "start_time",
            uni_df.columns[2]: "end_time",
            uni_df.columns[3]: "difficulty",
            uni_df.columns[4]: "location",
            uni_df.columns[5]: "extra_information_1",
            uni_df.columns[6]: "extra_information_2",
            uni_df.columns[7]: "extra_information_3",
            uni_df.columns[8]: "extra_information_4",
        }
    )
    uni_df = uni_df.fillna("NA - Keine Angabe")
    uni_df["counter"] = range(len(uni_df))

    new_html = []
    new_html_as_string = ""
    new_html = uni_df.apply(
        lambda row: render_template_for_each_row(row, uni_df["day"].count()), axis=1
    )
    for x in new_html:
        new_html_as_string = new_html_as_string + x
    return new_html_as_string


def start_piping(content_tag):

    piped_content = content_tag
    for ele in content_tag.findAll(attrs={"style": True}):
        del ele["style"]

    for_table_pipe = content_tag.select_one("table")
    if not pd.isna(for_table_pipe):
        new_html = pipe_tables(content_tag)
        piped_content.select_one("table").insert_after(
            BeautifulSoup(new_html, "html.parser")
        )
        piped_content.select_one("table").decompose()

    return piped_content


def comparing_homepage_data(row, curr_database):
    hash_yesterday = hashlib.md5(row["text"].encode("utf-8")).hexdigest()
    hash_today = hashlib.md5(row["text_today"].encode("utf-8")).hexdigest()
    has_changed = hash_yesterday != hash_today
    print(has_changed, hash_yesterday, hash_today, "Homepage")

    if True:
        temp_soup_today = row["text_today"]

        for ele in temp_soup_today.findAll(attrs={"style": True}):
            del ele["style"]
        temp_text = str(temp_soup_today)

        piped_text = start_piping(temp_soup_today)

        temp_dict = {
            "text": temp_text,
            "piped_text": piped_text,
            "link_to_text": row["link_to_text"],
            "sport_type": row["sport_type_x"],
            "last_changed": datetime.today(),
        }
        return pd.Series(temp_dict)
    else:
        # so it dosent overwrite last changed info
        temp_dict_from_old_base = (
            curr_database[curr_database["link_to_text"] == row["link_to_text"]]
            .iloc[0]
            .to_dict()
        )
        return pd.Series(temp_dict_from_old_base)


def get_info_from_homepage(
    session: CachedSession, session_today: CachedSession, curr_database
):
    # get all classes with cards
    # .class-header <- headline
    # and id frontpage-newsbox
    # add all to the list extra checkboxes

    content = session.get("https://hochschulsport-koeln.de/", headers=headers)
    content_today = session_today.get(
        "https://hochschulsport-koeln.de/", headers=headers
    )
    soup = BeautifulSoup(content.content, "html.parser")
    soup_today = BeautifulSoup(content_today.content, "html.parser")

    # ;text;piped_text;link_to_text;sport_type;last_changed
    headlines = ["/" + x.text.strip() for x in soup.select(".card .class-header")]
    headlines_today = [
        "/" + x.text.strip() for x in soup_today.select(".card .class-header")
    ]
    df_content = pd.DataFrame(
        {
            "text": soup.select(".card .card-body"),
            "link_to_text": headlines,
            "sport_type": "Startseite",
        }
    )
    df_content_today = pd.DataFrame(
        {
            "text_today": soup_today.select(".card .card-body"),
            "link_to_text": headlines_today,
            "sport_type": "Startseite",
        }
    )
    df_to_work_on = pd.merge(
        how="outer", on="link_to_text", left=df_content, right=df_content_today
    )
    return_df = df_to_work_on.apply(
        lambda row: comparing_homepage_data(row, curr_database), axis=1
    )
    return return_df


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


def get_source():
    session, session_today = cache_manipulation()
    url = "https://hochschulsport-koeln.de/"

    curr_database = pd.read_csv("./sports.csv", sep=";")
    response = session_today.get(url, headers=headers)

    soup = BeautifulSoup(response.content, "html.parser")

    # soup = BeautifulSoup(s, 'html.parser')
    menu_parents = soup.select("li")
    print(soup)
    row_list = []

    # for the homepage
    homepage_data = get_info_from_homepage(session, session_today, curr_database)
    sleep(1)

    # loop for the topics
    # exp: fitness, gesundheitssport etc
    for x in menu_parents:
        print(x.find(recursive=False).text)

        sport_type = x.find(recursive=False).text

        if len(x.select("ul>li")) > 0:
            # loop for the sports
            # football, volleyball etc
            for y in x.select("ul>li"):
                if not y.select_one("a"):
                    break

                endpoint = y.select_one("a").get("href")
                temp_response = session.get(url + endpoint, headers=headers)
                temp_today_response = session_today.get(url + endpoint, headers=headers)
                temp_soup = BeautifulSoup(temp_response.content, "html.parser")
                temp_soup_today = BeautifulSoup(
                    temp_today_response.content, "html.parser"
                )
                piped_text = ""

                hash_yesterday = hashlib.md5(
                    temp_soup.select_one("div.region.region-content")
                    .decode_contents()
                    .encode("utf-8")
                ).hexdigest()
                hash_today = hashlib.md5(
                    temp_soup_today.select_one("div.region.region-content")
                    .decode_contents()
                    .encode("utf-8")
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
                    for ele in temp_soup_today.findAll(attrs={"style": True}):
                        del ele["style"]
                    temp_text = temp_soup_today.select_one(
                        "div.region.region-content"
                    ).decode_contents()

                    piped_text = start_piping(
                        temp_soup_today.select_one("div.region.region-content")
                    ).decode_contents()

                    temp_dict = {
                        "text": temp_text,
                        "piped_text": piped_text,
                        "link_to_text": endpoint,
                        "sport_type": sport_type,
                        "last_changed": datetime.today(),
                    }
                    row_list.append(temp_dict)
                    if not has_endpoint_changed:
                        subscriber.send_message_to_user_list(endpoint)
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
                sleep(2)

    homepage_data.append(pd.DataFrame(row_list)).to_csv("sports.csv", sep=";")


get_source()
