#!/usr/bin/python3
# SPDX-FileCopyrightText: 2023 FC Stegerman <flx@obfusk.net>
# SPDX-License-Identifier: AGPL-3.0-or-later

import re

from typing import Any, Union

import requests

from flask import Flask, abort, make_response, redirect

# namespace, project, tag
CODEBERG_RELEASE = "https://codeberg.org/api/v1/repos/{}/{}/releases/tags/{}"

# namespace, project, release
GITLAB_RELEASE = "https://gitlab.com/api/v4/projects/{}%2F{}/releases/{}"
# namespace, project, upload
GITLAB_UPLOAD = "https://gitlab.com/{}/{}/uploads/{}"

app = Flask(__name__)


# FIXME: too strict?
def validate(*args: str) -> bool:
    for arg in args:
        if not re.fullmatch(r"[a-zA-Z0-9._-]+", arg):
            return False
    return True


def codeberg_release(namespace: str, project: str, release: str,
                     asset: str) -> Union[int, str]:
    if not validate(namespace, project, release, asset):
        return 400
    url = CODEBERG_RELEASE.format(namespace, project, release)
    try:
        req = requests.get(url, timeout=3)
        if req.status_code == 404:
            return 404
        req.raise_for_status()
        data = req.json()
        for asset_data in data["assets"]:
            if asset_data["name"] == asset:
                asset_url: str = asset_data["browser_download_url"]
                return asset_url
        return 404
    except (IndexError, KeyError, requests.RequestException):
        return 400


def gitlab_release(namespace: str, project: str, release: str,
                   asset: str) -> Union[int, str]:
    if not validate(namespace, project, release, asset):
        return 400
    url = GITLAB_RELEASE.format(namespace, project, release)
    try:
        req = requests.get(url, timeout=3)
        if req.status_code == 404:
            return 404
        req.raise_for_status()
        data = req.json()
        asset_url: str
        for asset_url in (a["url"] for a in data["assets"]["links"]):
            if asset_url.endswith("/" + asset):
                return asset_url
        for upload in re.findall(r"\(/uploads/([0-9a-f]{32}/[^/)]+)\)", data["description"]):
            if upload.endswith("/" + asset):
                asset_url = GITLAB_UPLOAD.format(namespace, project, upload)
                return asset_url
        return 404
    except (IndexError, KeyError, requests.RequestException):
        return 400


@app.route("/codeberg/<namespace>/<project>/<release>/<asset>")
def r_codeberg(namespace: str, project: str, release: str, asset: str) -> Any:
    result = codeberg_release(namespace, project, release, asset)
    if isinstance(result, int):
        abort(result)
    else:
        return redirect(result)


@app.route("/gitlab/<namespace>/<project>/<release>/<asset>")
def r_gitlab(namespace: str, project: str, release: str, asset: str) -> Any:
    result = gitlab_release(namespace, project, release, asset)
    if isinstance(result, int):
        abort(result)
    else:
        return redirect(result)


@app.route("/robots.txt")
def r_robots() -> Any:
    resp = make_response("User-agent: *\nDisallow: /\n")
    resp.mimetype = "text/plain"
    return resp
