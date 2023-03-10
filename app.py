#!/usr/bin/python3
# SPDX-FileCopyrightText: 2023 FC Stegerman <flx@obfusk.net>
# SPDX-License-Identifier: AGPL-3.0-or-later

import os
import re

from typing import Any, Union

import requests

from flask import Flask, abort, make_response, redirect, request
from flask_limiter import Limiter

HOMEPAGE = "https://github.com/obfusk/fdroid-release-redirector"

CODEBERG = "codeberg.org"
GITLAB = "gitlab.com"
NOTABUG = "notabug.org"

# host, namespace, project, release_tag
GITEA_RELEASE = "https://{}/api/v1/repos/{}/{}/releases/tags/{}"

# host, namespace, project, release
GITLAB_RELEASE = "https://{}/api/v4/projects/{}%2F{}/releases/{}"
# host, namespace, project, upload
GITLAB_UPLOAD = "https://{}/{}/{}/uploads/{}"
# hash/filename
GITLAB_UPLOAD_RX = re.compile(r"\(/uploads/([0-9a-f]{32}/[^/)]+)\)")

# NB: HTML, not JSON
# host, namespace, project
NOTABUG_RELEASES = "https://{}/{}/{}/releases"
# namespace, project, release
NOTABUG_RELEASE_ZIP = 'href="/{}/{}/archive/{}.zip"'
# host, attachment
NOTABUG_ATTACHMENT = "https://{}/attachments/{}"
# uuid, filename
NOTABUG_ATTACHMENT_RX = re.compile(r'href="/attachments/([0-9a-f-]+)"[^>]*>([^<]+)<')
NOTABUG_DOWNLOADS_RX = re.compile(r'<div class="download">(.*?)</div>', re.S)

ENV_PREFIX = "FDROID_RELEASE_REDIRECTOR"
RATELIMIT = os.environ.get(f"{ENV_PREFIX}_RATELIMIT") in ("1", "yes", "true")
FORWARDED = os.environ.get(f"{ENV_PREFIX}_FORWARDED") in ("1", "yes", "true")

if FORWARDED:
    def get_remote_address() -> str:
        return request.access_route[-1]
else:
    from flask_limiter.util import get_remote_address


app = Flask(__name__)

# NB: in-memory storage may require WEB_CONCURRENCY=1
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["60/hour"],
    enabled=RATELIMIT,
    storage_uri="memory://",
    strategy="fixed-window",
)


# FIXME: too strict?
def validate(*args: str) -> bool:
    for arg in args:
        if not re.fullmatch(r"[a-zA-Z0-9._-]+", arg):
            return False
    return True


def gitea_release(host: str, namespace: str, project: str, release_tag: str,
                  asset: str) -> Union[int, str]:
    if not validate(namespace, project, release_tag, asset):
        return 400
    url = GITEA_RELEASE.format(host, namespace, project, release_tag)
    try:
        r = requests.get(url, timeout=3)
        if r.status_code == 404:
            return 404
        r.raise_for_status()
        data = r.json()
        for asset_data in data["assets"]:
            if asset_data["name"] == asset:
                asset_url: str = asset_data["browser_download_url"]
                return asset_url
        return 404
    except (IndexError, KeyError, requests.RequestException):
        return 400


def gitlab_release(host: str, namespace: str, project: str, release: str,
                   asset: str) -> Union[int, str]:
    if not validate(namespace, project, release, asset):
        return 400
    url = GITLAB_RELEASE.format(host, namespace, project, release)
    try:
        r = requests.get(url, timeout=3)
        if r.status_code == 404:
            return 404
        r.raise_for_status()
        data = r.json()
        asset_url: str
        for asset_url in (a["url"] for a in data["assets"]["links"]):
            if asset_url.endswith("/" + asset):
                return asset_url
        for upload in GITLAB_UPLOAD_RX.findall(data["description"]):
            if upload.endswith("/" + asset):
                asset_url = GITLAB_UPLOAD.format(host, namespace, project, upload)
                return asset_url
        return 404
    except (IndexError, KeyError, requests.RequestException):
        return 400


# FIXME: scraping HTML; no API, no pagination
def notabug_release(host: str, namespace: str, project: str, release: str,
                    asset: str) -> Union[int, str]:
    if not validate(namespace, project, release, asset):
        return 400
    url = NOTABUG_RELEASES.format(host, namespace, project)
    release_zip = NOTABUG_RELEASE_ZIP.format(namespace, project, release)
    try:
        r = requests.get(url, timeout=3)
        if r.status_code == 404:
            return 404
        r.raise_for_status()
        for dl_m in NOTABUG_DOWNLOADS_RX.finditer(r.text):
            if release_zip in dl_m[1]:
                for url_m in NOTABUG_ATTACHMENT_RX.finditer(dl_m[1]):
                    if url_m[2] == asset:
                        return NOTABUG_ATTACHMENT.format(host, url_m[1])
        return 404
    except (IndexError, KeyError, requests.RequestException):
        return 400


@app.route("/codeberg/<namespace>/<project>/<release>/<asset>")
def r_codeberg(namespace: str, project: str, release: str, asset: str) -> Any:
    result = gitea_release(CODEBERG, namespace, project, release, asset)
    if isinstance(result, int):
        abort(result)
    else:
        return redirect(result)


@app.route("/gitlab/<namespace>/<project>/<release>/<asset>")
@limiter.limit("120/hour")
def r_gitlab(namespace: str, project: str, release: str, asset: str) -> Any:
    result = gitlab_release(GITLAB, namespace, project, release, asset)
    if isinstance(result, int):
        abort(result)
    else:
        return redirect(result)


@app.route("/notabug/<namespace>/<project>/<release>/<asset>")
def r_notabug(namespace: str, project: str, release: str, asset: str) -> Any:
    result = notabug_release(NOTABUG, namespace, project, release, asset)
    if isinstance(result, int):
        abort(result)
    else:
        return redirect(result)


@app.route("/")
@limiter.exempt
def r_root() -> Any:
    return redirect(HOMEPAGE)


@app.route("/robots.txt")
@limiter.exempt
def r_robots() -> Any:
    resp = make_response("User-agent: *\nDisallow: /\n")
    resp.mimetype = "text/plain"
    return resp
