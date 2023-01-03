#!/usr/bin/python3
# SPDX-FileCopyrightText: 2023 FC Stegerman <flx@obfusk.net>
# SPDX-License-Identifier: AGPL-3.0-or-later

import re

import requests

from flask import Flask, abort, make_response, redirect

# namespace, project, release
GITLAB_RELEASE = "https://gitlab.com/api/v4/projects/{}%2F{}/releases/{}"
# namespace, project, upload
GITLAB_UPLOAD = "https://gitlab.com/{}/{}/uploads/{}"

app = Flask(__name__)


def validate(*args):
    for arg in args:
        if not re.fullmatch(r"[a-zA-Z0-9._-]+", arg):
            raise ValueError(f"invalid: {arg!r}")


@app.route("/gitlab/<namespace>/<project>/<release>/<asset>")
def gitlab_release(namespace, project, release, asset):
    try:
        validate(namespace, project, release, asset)
    except ValueError:
        abort(400)
    url = GITLAB_RELEASE.format(namespace, project, release)
    try:
        req = requests.get(url, timeout=3)
        req.raise_for_status()
        data = req.json()
        for asset_url in (a["url"] for a in data["assets"]["links"]):
            if asset_url.endswith("/" + asset):
                return redirect(asset_url)
        for upload in re.findall(r"\(/uploads/([0-9a-f]{32}/[^/)]+)\)", data["description"]):
            if upload.endswith("/" + asset):
                asset_url = GITLAB_UPLOAD.format(namespace, project, upload)
                return redirect(asset_url)
        abort(404)
    except (IndexError, KeyError, requests.RequestException):
        abort(400)


@app.route("/robots.txt")
def robots():
    resp = make_response("User-agent: *\nDisallow: /\n")
    resp.mimetype = "text/plain"
    return resp
