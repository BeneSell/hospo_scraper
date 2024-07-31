# -*- coding: UTF-8 -*-

from asyncio import constants
from cgitb import text
from datetime import datetime
from inspect import getsource
from opcode import hascompare
from os import sep
from sqlite3 import Date
import string
from tabnanny import check
from unicodedata import category, name
from xmlrpc.client import DateTime
from bs4 import BeautifulSoup
from numpy import sort, true_divide
import requests
import requests_cache
from requests_cache import CachedSession
import pandas as pd
from time import sleep
from num2words import num2words

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
import urllib.parse
import subscriber


headers = requests.utils.default_headers()

headers.update(
    {
        "User-Agent": "My User Agent 1.0",
    }
)


app = Flask(__name__)
# api = Api(app)
cors = CORS(app, resources={r"/*": {"origins": "*"}})
app.config["SERVER_NAME"] = "127.0.0.1:5000"


with app.app_context():
    # from get_hospo_data import get_source
    # get_hospo_data.get_source()
    pass


@app.route("/favicon.ico")
def favicon():
    return send_from_directory(
        os.path.join(app.root_path, "static"),
        "favicon.ico",
        mimetype="image/vnd.microsoft.icon",
    )


def create_data_based_description(return_df: pd.DataFrame, search_term):
    new_description = ""
    if return_df.count().iloc[0] > 1:
        new_description = f"""
        Hochschulsport hat { num2words(return_df.count().iloc[0])} Angebote für {search_term}.
        Das Angebot mit den neusten Änderungen ist {return_df.sort_values(by="last_changed", ascending=False).iloc[0]["link_to_text"]}
        """
    elif return_df.count().iloc[0] == 1:
        new_description = f"""
        {search_term} bei Hochschulsport, letzte Änderung am {return_df.iloc[0]["last_changed"]}
        """
    elif return_df.count().iloc[0] == 0:
        new_description = """
        Leider keine Ergebnisse gefunden.
        """
    return new_description

    #     if(length(list)) > 1
    # hochschulsport hat {{count numtoword}} Angebote f�r {{Sportname}}.
    # Der mit den neusten �nderungen ist {{list.first}}
    # else:
    # {{Sportname}} bei Hochschulsport, letzte �nderung am {{last changed}}

    # /Volleyball
    # geändert am 02.05.2022 und hat zehn wöchentliche Termine.

    # /aqua
    # geändert am 02.05.2022 hat keine gelistetete Termine

    pass


def compute_query(
    sport_name: string, checked_sports_categorie: list, sort_value: string
):
    data = pd.read_csv("sports.csv", sep=";", parse_dates=["last_changed"])  # read CSV

    # serach after the given sport_name (serach value)
    # data = data[data["link_to_text"].str.contains(sport_name, flags=re.IGNORECASE, regex=True)]
    print(sport_name)
    print(data[["title"]].iloc[0])
    if sport_name != "":
        data = data[
            data[["title"]]
            .map(lambda x: sport_name.lower() in x.lower())
            .any(axis=1)
        ]

    # categorie filter
    if checked_sports_categorie:
        print(checked_sports_categorie)
        data = data[
            data["sport_type"].str.contains(
                "|".join(checked_sports_categorie), flags=re.IGNORECASE, regex=True
            )
        ]
    data = data.fillna(999)

    # sorting
    if sort_value == "by_link_asc":
        data["link_to_text"] = data["link_to_text"].apply(lambda x: x.strip())
        data = data.sort_values(by="link_to_text", ascending=True)
        print(data.iloc[0:5]["link_to_text"])
        pass
    elif sort_value == "by_link_desc":
        data = data.sort_values(by="link_to_text", ascending=False)
        pass
    elif sort_value == "by_date_asc":
        data = data.sort_values(by="last_changed", ascending=False)
        pass
    elif sort_value == "by_date_desc":
        data = data.sort_values(by="last_changed", ascending=True)
        pass

    data["last_changed"] = data["last_changed"].apply(
        lambda x: x.strftime(format="%d.%m.%Y")
    )

    new_description = "Schaue dir alle Kurse von Hochschulsport Köln an!"
    if sport_name != "":
        categories_can_used = data.groupby(by="sport_type").count().index.to_list()
        new_description = create_data_based_description(data, sport_name)
    else:
        # empty means all
        categories_can_used = []
    data = data.to_dict("records")  # convert dataframe to dictionary
    return {
        "data": data,
        "categorie_can_used": json.dumps(categories_can_used),
        "new_description": json.dumps(new_description.strip()),
    }


@app.route("/sports/")
@app.route("/sports/<sport_name>")
def sports(sport_name=""):
    checked_sports_categorie = request.args.getlist("sports_categories")
    sort_value = request.args.get("sort_value")

    if pd.isna(checked_sports_categorie).any():
        checked_sports_categorie = []
    if pd.isna(sort_value):
        sort_value = ""

    # encode
    sort_value = urllib.parse.unquote(sort_value)
    checked_sports_categorie = [
        urllib.parse.unquote(x) for x in checked_sports_categorie
    ]
    print(checked_sports_categorie)
    description = f"Information gecrawlt von der Hoschulsport Köln Seite."

    direct_query = {"data": [], "new_description": description}
    if sport_name != "" or sort_value != "" or len(checked_sports_categorie) != 0:
        direct_query = compute_query(sport_name, checked_sports_categorie, sort_value)

    return {
        "data": render_template(
            "index.html",
            sport_name=sport_name,
            sports_categories=json.dumps(checked_sports_categorie),
            sort_value=sort_value,
            description=direct_query["new_description"],
            data=direct_query["data"],
            load_serach=False,
        ),
        "categorie_can_used": direct_query["categorie_can_used"],
        "new_description": json.dumps(direct_query["new_description"]),
    }, 200


@app.route("/sports_categorie/")
def sports_categorie():
    data = pd.read_csv("sports.csv", sep=";")  # read CSV
    data = data["sport_type"].unique()
    data = list(data)
    return {"data": data}, 200


@app.route("/index/")
@app.route("/index/<sport_name>")
def index(sport_name=""):
    checked_sports_categorie = request.args.getlist("sports_categories")
    sort_value = request.args.get("sort_value")

    if pd.isna(checked_sports_categorie):
        checked_sports_categorie = []
    if pd.isna(sort_value):
        sort_value = ""

    # encode
    sort_value = urllib.parse.unquote(sort_value)
    checked_sports_categorie = [
        urllib.parse.unquote(x) for x in checked_sports_categorie
    ]

    description = f"Information gecrawlt von der Hoschulsport Köln Seite."

    direct_query = {"data": [], "new_description": description}
    if sport_name != "" or sort_value != "" or len(checked_sports_categorie) != 0:
        direct_query = compute_query(sport_name, checked_sports_categorie, sort_value)

    if sport_name != "":
        sport_name = "/" + sport_name

    print(direct_query["new_description"])

    return render_template(
        "index.html",
        sport_name=sport_name,
        sports_categories=json.dumps(checked_sports_categorie),
        sort_value=sort_value,
        description=direct_query["new_description"],
        data=direct_query["data"],
        load_serach=True,
    )


@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template("404.html"), 404


@app.route("/subscribe/")
@app.route("/subscribe/<link_to_text>")
@app.route("/subscribe/index.php/<link_to_text>")
def subscribe(link_to_text):
    # len not over or equal 70

    link_to_text = urllib.parse.unquote(link_to_text)
    print(len(link_to_text))
    # properply way to long!
    return_value = subscriber.clicked_on_subscried(link_to_text)
    return return_value
    pass


# to compare
# with session.cache_disabled():
#
#    session.get('http://httpbin.org/get')
if __name__ == "__main__":
    # app.run(debug=True, use_reloader=False,host="0.0.0.0",port=5000, ssl_context="adhoc")
    app.run(debug=True, use_reloader=False, port=5000)
