# unraid-templates

[![License](https://img.shields.io/github/license/cplieger/unraid-templates)](LICENSE)

These are the Unraid templates for four open-source container apps by cplieger. Install any of them from your server's Apps tab. Unraid fills in the image, the folders and the defaults, and you add the one or two values each app needs. The templates are licensed under Apache-2.0, and each app keeps its own license.

## The apps

All four are listed in [Community Applications](https://docs.unraid.net/community-applications/), the catalog behind Unraid's Apps tab. Each image is published for `amd64` and `arm64`.

| App | What you get | What you fill in | Template |
| --- | --- | --- | --- |
| [plex-language-sync](https://github.com/cplieger/plex-language-sync) | Set the audio and subtitle language once per show, and every new episode follows | Plex URL and Plex token | [`plex-language-sync.xml`](templates/plex-language-sync.xml) |
| [plex-exporter](https://github.com/cplieger/plex-exporter) | See your Plex server's sessions, libraries, bandwidth and transcoding in Grafana | Plex URL and Plex token. You also need Prometheus or another metrics collector, and Grafana | [`plex-exporter.xml`](templates/plex-exporter.xml) |
| [fclones-scheduler](https://github.com/cplieger/docker-fclones-scheduler) | Find duplicate files on a share with [fclones](https://github.com/pkolaczk/fclones) on a schedule, and link or remove them if you choose | The share to scan. The default action only reports | [`fclones-scheduler.xml`](templates/fclones-scheduler.xml) |
| [seadex-scout](https://github.com/cplieger/seadex-scout) | Keep your Sonarr and Radarr anime library in sync with SeaDex's best releases | Sonarr URL and Sonarr API key. Radarr is optional | [`seadex-scout.xml`](templates/seadex-scout.xml) |

Without these templates, you would copy each image's settings from its README into Unraid's Add Container form by hand.

## Install on Unraid

1. Open the Apps tab on your Unraid server.
2. Search for the app by name and click Install.
3. Fill in the fields marked required in the Add Container form, then click Apply.

Each field's description says where to find a token or key, and each template's notes say what else the app needs. An app that keeps files stores them under `/mnt/user/appdata/<app>`, and its template lets it write there from the first start. Every template runs its app on the bridge network, without privileged mode. fclones-scheduler mounts the share you choose with write access, because linking and removing files need it.

Every template installs the image's `latest` tag, so the Docker tab offers each new release as an update. Your installed container keeps the settings you chose. When a template gains a new field later, only new installs show it.

## Support

A problem with an app goes to that app's issue tracker, which the Support link of its template opens. That includes an app that starts but does the wrong thing, or a log line you do not understand. A problem with a template itself goes to [this repository's issues](https://github.com/cplieger/unraid-templates/issues), for example a wrong default, a missing field or a bad path.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## Disclaimer

This project is built with care and follows security best practices, but it is intended for personal / self-hosted use. No guarantees of fitness for production environments. Use at your own risk.

This project was built with AI-assisted tooling using [Claude](https://claude.com), [GPT](https://openai.com), and [Kiro](https://kiro.dev). The human maintainer defines architecture, supervises implementation, and makes all final decisions.

## License

Apache-2.0. See [LICENSE](LICENSE).
