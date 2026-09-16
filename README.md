# unraid-templates

[![License](https://img.shields.io/github/license/cplieger/unraid-templates)](LICENSE)
[![OpenSSF Best Practices](https://www.bestpractices.dev/projects/PROJECT_ID/badge)](https://www.bestpractices.dev/projects/PROJECT_ID)
[![OpenSSF Scorecard](https://api.scorecard.dev/projects/github.com/cplieger/unraid-templates/badge)](https://scorecard.dev/viewer/?uri=github.com/cplieger/unraid-templates)

Unraid Community Applications templates for the container images published by cplieger.

## What this is

One XML template per app under `templates/`, in the format Unraid's Docker manager reads, plus the `ca_profile.xml` that describes this repository to Community Applications. Each template points at the app's Docker Hub image, its GitHub project and its issue tracker, and lists the app's configuration as fields Unraid shows in the Add Container form.

| App | What it does | Template | Project |
| --- | --- | --- | --- |
| plex-language-sync | Set preferred audio and subtitle languages per show; every new episode follows automatically | [`templates/plex-language-sync.xml`](templates/plex-language-sync.xml) | [cplieger/plex-language-sync](https://github.com/cplieger/plex-language-sync) |
| plex-exporter | Plex sessions, libraries, bandwidth and transcoding as Prometheus metrics, with a Grafana dashboard | [`templates/plex-exporter.xml`](templates/plex-exporter.xml) | [cplieger/plex-exporter](https://github.com/cplieger/plex-exporter) |
| fclones-scheduler | Find and deduplicate files on a schedule with fclones | [`templates/fclones-scheduler.xml`](templates/fclones-scheduler.xml) | [cplieger/docker-fclones-scheduler](https://github.com/cplieger/docker-fclones-scheduler) |

## Install on Unraid

Open the Apps tab on your Unraid server, search for the app by name and click Install. Unraid renders the template into the Add Container form; fill in the fields marked required and apply.

Before a template is listed in Community Applications, or to try a change from a branch, add this repository as a template source: Docker tab, Template Repositories, paste `https://github.com/cplieger/unraid-templates`, save. The templates then appear in the Template dropdown of Add Container.

## Support

A problem with an app (it starts but does the wrong thing, a log line you do not understand) goes to that app's issue tracker, linked from the Support field of its template and from the table above. A problem with a template itself (a wrong default, a missing field, a bad path) goes to [this repository's issues](https://github.com/cplieger/unraid-templates/issues).

## Contributing

Templates are checked by `scripts/validate.py` on every pull request: well-formed XML, the required fields, a `TemplateURL` that names its own file, a `cplieger/*` image reference and an icon that exists in `icons/`. Run it locally with `python3 scripts/validate.py`. Icons are one design: a square off-white tile, one glyph box, one stroke width, one corner radius, and a colour whose hue says which ecosystem the app belongs to (Plex, Sonarr/Radarr, storage). `scripts/icons.py` holds every glyph as SVG paths and renders `icons/src/*.svg` and the PNGs with `uv run --with cairosvg scripts/icons.py`; edit the script, not the images. Issues and pull requests are welcome; the general guidelines live in [cplieger/.github](https://github.com/cplieger/.github/blob/main/CONTRIBUTING.md).

## Disclaimer

This project is built with care and follows security best practices, but it is intended for personal / self-hosted use. No guarantees of fitness for production environments. Use at your own risk.

This project was built with AI-assisted tooling using [Claude](https://claude.com), [GPT](https://openai.com), and [Kiro](https://kiro.dev). The human maintainer defines architecture, supervises implementation, and makes all final decisions.

## License

Apache-2.0. See [LICENSE](LICENSE).
