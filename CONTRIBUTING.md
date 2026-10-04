# Contributing to unraid-templates

This page is for anyone who wants to change a template or an icon. The general guidelines for cplieger repositories are in [cplieger/.github](https://github.com/cplieger/.github/blob/main/CONTRIBUTING.md).

## What is here

- `templates/<app>.xml` holds one template per app, in the `<Container version="2">` format Unraid's Docker manager reads.
- `ca_profile.xml` describes this repository to Community Applications, which shows it as the repository's description.
- `icon.png` is the repository icon, and `icons/<app>.png` is the icon each template points at.
- `scripts/validate.py` checks the templates and the profile.
- `scripts/icons.py` renders the icons.
- `scripts/release.sh` creates a release when the merged commit subjects call for a version bump.

## Checks

`scripts/validate.py` runs on every pull request. Run it locally with `python3 scripts/validate.py`. It prints one line per finding and exits 1 when it finds any.

It checks that each template:

- is well-formed XML with a `<Container version="2">` root
- has every required element, including `Support`, `Project`, `Overview` and `Icon`
- uses a `<Name>` no other template uses
- names a tagged `cplieger/*` image in `<Repository>`
- has a `<TemplateURL>` that names its own file on `main`
- points `<Icon>` at a file that exists in `icons/`
- has no `<Shell>`, because the images are distroless and have no shell
- uses only allowed `Type`, `Display`, `Mode`, `Required` and `Mask` values on each `Config`, with no duplicate target
- gives each optional `Config` the same `Default` as its value.

It also checks that `ca_profile.xml` mentions every app and points at an icon in this repository. Any other XML file outside `templates/` fails the check, because Community Applications reads every XML file in the repository as a template.

## Icons

Every generated icon follows one design. It is a square tile in a colour whose hue names the app's ecosystem, such as Plex, Sonarr and Radarr, or storage. One off-white glyph sits on the tile, in the same glyph box, stroke width and corner radius as every other icon.

`scripts/icons.py` holds every glyph as SVG paths. Run `uv run --with cairosvg scripts/icons.py` to render `icons/src/*.svg` and the PNGs the templates point at. Edit the script, not the generated images.

An app that ships its own mark keeps it. Its SVG is copied from the app's favicon into `icons/brand/`, and the script only rasterises and reshapes it, so those files are edited as art.

The same run writes the other shape and polarity combinations to `icons/variants/`. No template points at them, and Unraid never downloads them.

## Commits and pull requests

Write commit subjects as conventional commits, such as `fix: correct the seadex-scout config path`. When the merged subjects call for a version bump, `scripts/release.sh` cuts a GitHub release from the subjects since the last tag. Community Applications reads `main` directly, so the release is the changelog and carries no files. A merged change reaches the Apps tab at the next Community Applications feed build.

## Conduct and security

Follow the [code of conduct](https://github.com/cplieger/.github/blob/main/CODE_OF_CONDUCT.md). Report a security problem as the [security policy](https://github.com/cplieger/.github/blob/main/SECURITY.md) describes, not in a public issue.
