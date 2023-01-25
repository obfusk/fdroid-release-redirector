<!-- SPDX-FileCopyrightText: 2023 FC Stegerman <flx@obfusk.net> -->
<!-- SPDX-License-Identifier: AGPL-3.0-or-later -->

[![CI](https://github.com/obfusk/fdroid-release-redirector/workflows/CI/badge.svg)](https://github.com/obfusk/fdroid-release-redirector/actions?query=workflow%3ACI)
[![AGPLv3+](https://img.shields.io/badge/license-AGPLv3+-blue.svg)](https://www.gnu.org/licenses/agpl-3.0.html)

# fdroid-release-redirector

Redirector for code forges that don't have stable URLs for release
assets (by default).

## Example

```sh
$ SERVER=https://fdroid-release-redirector.herokuapp.com
$ NAMESPACE=some-user PROJECT=some-project RELEASE=v1.0
$ curl -sI $SERVER/gitlab/$NAMESPACE/$PROJECT/$RELEASE/release.apk | grep ^Location:
Location: https://example.com/some.apk
```

## F-Droid reproducible builds

When using `Binaries:` for F-Droid reproducible builds, you can use something
like this in the `metadata/your.app.id.yml`:

```yaml
Binaries: https://fdroid-release-redirector.herokuapp.com/gitlab/yourusername/yourapp/v%v/app-release.apk
```

NB: replace forge (`gitlab`), username (`yourusername`), repository (`yourapp`),
tag format, and filename (`app-release.apk`) with appropriate values.

## Supported forges

### Codeberg

NB: it turns out that Codeberg already has stable URLs, even though the download
page uses non-stable ones:
`https://codeberg.org/<namespace>/<project>/releases/download/<tag>/<filename>`.

API: `/codeberg/<namespace>/<project>/<release-tag>/<filename>`

`filename` must match the `name` of one of the assets.

### GitLab

API: `/gitlab/<namespace>/<project>/<release>/<filename>`

`filename` must match the filename of one of the asset links or a file upload in
the release description.

### NotABug

API: `/notabug/<namespace>/<project>/<release>/<filename>`

`filename` must match the filename of one of the downloads.

NB: there does not seem to be a JSON API for releases like for the other forges,
so the project's releases HTML page is scraped (which could break if the HTML
changes); pagination is currently not supported (so the release is only found if
it is on the first page).

## Unsupported forges

* GitHub (no need, since release assets already have stable URLs)

## License

[![AGPLv3+](https://www.gnu.org/graphics/agplv3-155x51.png)](https://www.gnu.org/licenses/agpl-3.0.html)

<!-- vim: set tw=70 sw=2 sts=2 et fdm=marker : -->
