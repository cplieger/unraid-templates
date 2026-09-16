#!/usr/bin/env python3
"""Check every template and the repository profile before Community Apps reads them.

Exit 1 with one line per finding; exit 0 when clean.
"""

import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = 'https://raw.githubusercontent.com/cplieger/unraid-templates/main/'
IMAGE_OWNER = 'cplieger/'
REQUIRED = (
    'Name',
    'Repository',
    'Registry',
    'Network',
    'Support',
    'Project',
    'Overview',
    'Category',
    'Icon',
    'TemplateURL',
)
DISPLAY = {'always', 'advanced', 'always-hide', 'advanced-hide'}
TYPES = {'Variable', 'Path', 'Port', 'Label', 'Device'}
MODES = {'Path': {'rw', 'ro', 'rw,slave', 'ro,slave'}, 'Port': {'tcp', 'udp'}}
BOOL = {'true', 'false'}


def text(el, tag):
    child = el.find(tag)
    return (child.text or '').strip() if child is not None else ''


def parse(path):
    # The inputs are this repository's own files, so the stdlib parser's
    # entity handling is not a concern here.
    return ET.parse(path).getroot()  # noqa: S314


def check_template(path, names, findings):
    def bad(msg):
        findings.append(f'{path.relative_to(ROOT)}: {msg}')

    try:
        root = parse(path)
    except ET.ParseError as e:
        bad(f'not well-formed XML ({e})')
        return
    if root.tag != 'Container' or root.get('version') != '2':
        bad('root must be <Container version="2">')
    for tag in REQUIRED:
        if not text(root, tag):
            bad(f'<{tag}> missing or empty')
    name = text(root, 'Name')
    if name in names:
        bad(f'<Name>{name}</Name> is also used by {names[name]}')
    names[name] = path.name
    repo = text(root, 'Repository')
    if not repo.startswith(IMAGE_OWNER) or ':' not in repo:
        bad(f'<Repository> must be a tagged {IMAGE_OWNER}* image, got {repo!r}')
    want_url = f'{RAW}templates/{path.name}'
    if text(root, 'TemplateURL') != want_url:
        bad(f'<TemplateURL> must be {want_url}')
    icon = text(root, 'Icon')
    if not icon.startswith(f'{RAW}icons/'):
        bad(f"<Icon> must point into this repository's icons/, got {icon!r}")
    elif not (ROOT / icon[len(RAW) :]).is_file():
        bad(f'<Icon> names {icon[len(RAW) :]}, which does not exist')
    if root.find('Shell') is not None:
        bad('<Shell> set on a distroless image, which has no shell')
    seen = set()
    for cfg in root.findall('Config'):
        label = cfg.get('Name', '?')
        ctype = cfg.get('Type', '')
        if ctype not in TYPES:
            bad(f'Config {label!r}: Type {ctype!r} not in {sorted(TYPES)}')
        if not cfg.get('Target'):
            bad(f'Config {label!r}: Target is empty')
        if cfg.get('Display') not in DISPLAY:
            bad(f'Config {label!r}: Display {cfg.get("Display")!r} not in {sorted(DISPLAY)}')
        for attr in ('Required', 'Mask'):
            if cfg.get(attr) not in BOOL:
                bad(f'Config {label!r}: {attr} must be true or false')
        if ctype in MODES and cfg.get('Mode') not in MODES[ctype]:
            bad(f'Config {label!r}: Mode {cfg.get("Mode")!r} not valid for a {ctype}')
        key = (ctype, cfg.get('Target'))
        if key in seen:
            bad(f'Config {label!r}: duplicate {ctype} for {cfg.get("Target")}')
        seen.add(key)
        if cfg.get('Default', '') != (cfg.text or '').strip() and cfg.get('Required') == 'false':
            bad(
                f'Config {label!r}: Default {cfg.get("Default")!r} differs from the value {cfg.text!r}'
            )


def check_profile(findings):
    path = ROOT / 'ca_profile.xml'
    if not path.is_file():
        findings.append('ca_profile.xml missing at the repository root')
        return
    try:
        root = parse(path)
    except ET.ParseError as e:
        findings.append(f'ca_profile.xml: not well-formed XML ({e})')
        return
    if root.tag != 'CommunityApplications':
        findings.append('ca_profile.xml: root must be <CommunityApplications>')
    if not text(root, 'Profile'):
        findings.append('ca_profile.xml: <Profile> is empty')
    icon = text(root, 'Icon')
    if not icon.startswith(RAW) or not (ROOT / icon[len(RAW) :]).is_file():
        findings.append(f'ca_profile.xml: <Icon> must name a file in this repository, got {icon!r}')


def main():
    findings = []
    names = {}
    templates = sorted((ROOT / 'templates').glob('*.xml'))
    if not templates:
        findings.append('templates/ holds no XML file')
    for path in templates:
        check_template(path, names, findings)
    check_profile(findings)
    stray = [
        p
        for p in ROOT.rglob('*.xml')
        if p.parent != ROOT / 'templates' and p.name != 'ca_profile.xml' and '.git' not in p.parts
    ]
    for p in stray:
        findings.append(
            f'{p.relative_to(ROOT)}: XML outside templates/ is scanned by Community Apps as a template'
        )
    for f in findings:
        print(f, file=sys.stderr)
    print(f'{len(templates)} template(s) checked, {len(findings)} finding(s)')
    return 1 if findings else 0


if __name__ == '__main__':
    sys.exit(main())
