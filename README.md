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

## Currently supported forges

### Codeberg

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

## Forges that will not be supported

* GitHub (no need, since release assets already have stable URLs)
