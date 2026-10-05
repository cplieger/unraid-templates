# Contributing to unraid-templates

The [shared rules](https://github.com/cplieger/.github/blob/main/CONTRIBUTING.md) for commits, releases, synced files and checks apply here.

## Rules

- A new app touches four places: `templates/<app>.xml`, its icon, its name in the `<Profile>` text of `ca_profile.xml`, and the apps table and app count in `README.md`. `scripts/validate.py` reports a missing icon or profile mention, but never the README.
- `scripts/icons.py` generates `icon.png` and everything under `icons/` from the glyphs it holds as SVG paths. Change the script and run `uv run --with cairosvg scripts/icons.py`. Never edit an output by hand, because the next run overwrites it.
- The exception is `icons/brand/*.svg`, each a copy of an app's own favicon that the script only rasterises and reshapes. Update one by copying that favicon again.
- A template whose app writes to a mapped folder sets `--user 99:100`, Unraid's own user and group, in `<ExtraParams>`. The images take their user only from `--user` and read no `PUID` or `PGID` variable, so adding either one changes nothing.

## Checks

Run `python3 scripts/validate.py` before you push. It needs only Python 3. CI runs it only in the Publish workflow, so the local check in the shared rules does not cover it.

## Releases

Community Applications builds its feed from the templates on `main`, so a merged change reaches the Apps tab at the next build, whatever its commit type. The GitHub release is only the changelog.

Unlike the shared table, `scripts/release.sh` cuts no release for a type the table does not name, and cuts a major version for a `!` after any type or a `BREAKING CHANGE:` footer on any commit.
