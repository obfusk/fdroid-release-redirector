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

`filename` must match the file name of one of the asset links or a file upload
in the release description.

## Forges planned to be supported

* NotABug

## Forges that will not be supported

* GitHub (no need, since release assets already have stable URLs)
