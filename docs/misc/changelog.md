# Changelog

Our releases are accompanied by changelogs based on the
[Keep a Changelog](https://keepachangelog.com/en/1.0.0/) format. We are using
the [towncrier](https://github.com/twisted/towncrier) utility to generate them
at the time a new version is released. There are currently four such changelogs
for different parts of the repository:

* **[`core/CHANGELOG.md`](https://github.com/trezor/trezor-firmware/blob/master/core/CHANGELOG.md)** for Trezor T firmware
* **[`legacy/firmware/CHANGELOG.md`](https://github.com/trezor/trezor-firmware/blob/master/legacy/firmware/CHANGELOG.md)** for Trezor 1 firmware
* **[`legacy/bootloader/CHANGELOG.md`](https://github.com/trezor/trezor-firmware/blob/master/legacy/bootloader/CHANGELOG.md)** for Trezor 1 bootloader
* **[`python/CHANGELOG.md`](https://github.com/trezor/trezor-firmware/blob/master/python/CHANGELOG.md)** for Python client library

## Adding changelog entry

`towncrier` aims to create changelogs that are convenient to read, at the
expense of being somewhat inconvenient to create. Furthermore, every changelog
entry has to be linked to a GitHub issue or pull request number. If you don't
want to create an issue just to satisfy this rule you can use self-reference to
your change's pull request number by first creating the PR and then adding the
entry.

There are a few types of changelog entries, as described by the [Keep a
Changelog](https://keepachangelog.com/en/1.0.0/) format:

* `added`
* `changed`
* `deprecated`
* `removed`
* `fixed`
* `security`
* `incompatible`, used only by `python`

As an example, an entry describing bug fix for issue 1234 in Trezor T firmware
is added by creating file `core/.changelog.d/1234.fixed`. This file typically
contains single line describing the change, and can be formatted with markdown.

XXX rewrite^

## Generating changelog at the time of release

XXX script
XXX specifying date
