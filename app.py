#!/usr/bin/python3
# SPDX-FileCopyrightText: 2023 FC Stegerman <flx@obfusk.net>
# SPDX-License-Identifier: AGPL-3.0-or-later

import requests

from flask import Flask, abort, redirect

GITLAB_RELEASE = "https://gitlab.com/api/v4/projects/{}%2F{}/releases/{}"

app = Flask(__name__)


@app.route("/gitlab/<namespace>/<project>/<release>/<asset>")
def gitlab_release(namespace, project, release, asset):
    url = GITLAB_RELEASE.format(namespace, project, release)
    try:
        req = requests.get(url, timeout=3)
        req.raise_for_status()
        for asset_url in (a["url"] for a in req.json()["assets"]["links"]):
            if asset_url.endswith(asset):
                return redirect(asset_url)
    except (IndexError, KeyError, requests.RequestException):
        pass
    abort(500)


@app.route("/robots.txt")
def robots():
    return "User-agent: *\nDisallow: /\n"
