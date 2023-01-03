# fdroid-release-redirector

Redirector for release assets; currently supports: GitLab.

```sh
$ SERVER=https://fdroid-release-redirector.herokuapp.com/
$ curl -sI $SERVER/gitlab/namespace/project/v1.0/release-v1.0.apk | grep ^Location:
Location: https://example.com/release.apk
```
