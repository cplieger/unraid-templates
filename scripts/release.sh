#!/usr/bin/env bash
# Cut a semver release when a file Community Apps reads changed since the last
# tag. Runs after validate in publish.yaml; DRY_RUN=1 prints the decision and
# creates nothing. Community Apps reads main directly, so a release carries no
# assets: it is the changelog of the template set.
set -euo pipefail

REPO="${GITHUB_REPOSITORY:-cplieger/unraid-templates}"
# What CA and an install read: the templates, the profile and the icon PNGs
# their URLs name. A CI, script, doc or icon-source change ships nothing.
SHIPPED=(templates ca_profile.xml icon.png ':(glob)icons/*.png')

last="$(git describe --tags --abbrev=0 --match 'v*' 2>/dev/null || true)"
range="${last:+${last}..HEAD}"
range="${range:-HEAD}"

subjects="$(git log --format='%s' "$range" -- "${SHIPPED[@]}")"
bodies="$(git log --format='%b' "$range" -- "${SHIPPED[@]}")"

# The tree compare catches a change reverted inside the range, which still
# leaves subjects behind.
if [ -z "$subjects" ] || { [ -n "$last" ] && git diff --quiet "$last" HEAD -- "${SHIPPED[@]}"; }; then
  echo "release: no shipped file changed since ${last:-the beginning}; nothing to cut"
  exit 0
fi

# A shipped change always releases, so patch is the floor and commits only raise it.
bump="patch"
if grep -qE '^[a-z]+(\([^)]*\))?!:' <<<"$subjects" || grep -q '^BREAKING CHANGE:' <<<"$bodies"; then
  bump="major"
elif grep -qE '^feat(\([^)]*\))?:' <<<"$subjects"; then
  bump="minor"
fi

if [ -z "$last" ]; then
  next="v1.0.0"
else
  IFS=. read -r major minor patch <<<"${last#v}"
  case "$bump" in
    major) next="v$((major + 1)).0.0" ;;
    minor) next="v${major}.$((minor + 1)).0" ;;
    patch) next="v${major}.${minor}.$((patch + 1))" ;;
  esac
fi

notes="$(printf '## %s\n\n%s\n' "$next" "$(sed 's/^/- /' <<<"$subjects")")"
echo "release: ${last:-<none>} -> $next ($bump)"

if [ "${DRY_RUN:-0}" = "1" ]; then
  printf '%s\n' "$notes"
  exit 0
fi

if gh release view "$next" --repo "$REPO" >/dev/null 2>&1; then
  echo "release: $next already exists; nothing to do"
  exit 0
fi

sha="$(git rev-parse HEAD)"
gh api --method POST "repos/${REPO}/git/refs" --raw-field ref="refs/tags/${next}" --raw-field sha="$sha" >/dev/null
gh release create "$next" --repo "$REPO" --title "$next" --notes "$notes" --latest
echo "release: created $next"
