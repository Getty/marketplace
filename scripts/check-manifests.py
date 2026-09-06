#!/usr/bin/env python3
"""Check that the two marketplace manifests agree with each other and with the
repositories they point at.

    python3 scripts/check-manifests.py            # everything, needs `gh`
    python3 scripts/check-manifests.py --offline  # only what the files alone can tell

A catalog whose entries disagree, or point at repositories that moved, went
private or never became plugins, is worse than no catalog: it fails at install
time, on the user's machine. Everything here is a check the two harnesses'
own parsers do not make.
"""
import json
import re
import shutil
import subprocess
import sys

CLAUDE = ".claude-plugin/marketplace.json"
CODEX = ".agents/plugins/marketplace.json"

# What each harness expects to find in a plugin repository.
PLUGIN_MANIFEST = {CLAUDE: ".claude-plugin/plugin.json", CODEX: ".codex-plugin/plugin.json"}

# What Codex 0.153 accepts. One value outside these sets fails the whole
# manifest, not just its entry, for everyone who has the marketplace registered.
INSTALLATION = {"NOT_AVAILABLE", "AVAILABLE", "INSTALLED_BY_DEFAULT"}
AUTHENTICATION = {"ON_INSTALL", "ON_USE"}

errors = []


def err(msg):
    errors.append(msg)


def load(path):
    try:
        with open(path) as f:
            return json.load(f)
    except (OSError, ValueError) as e:
        err(f"{path}: {e}")
        return {"plugins": []}


def github_repo(entry, path):
    """The owner/repo an entry points at, or None with an error recorded."""
    src = entry.get("source")
    if isinstance(src, dict):
        if src.get("source") == "github" and src.get("repo"):
            return src["repo"]
        m = re.search(r"github\.com[/:]([^/]+/[^/]+?)(?:\.git)?/?$", src.get("url", ""))
        if m:
            return m.group(1)
    err(f"{path}: {entry.get('name', '?')}: cannot tell which GitHub repository this points at")
    return None


def gh(endpoint, raw=False):
    cmd = ["gh", "api", endpoint]
    if raw:
        cmd += ["-H", "Accept: application/vnd.github.raw"]
    r = subprocess.run(cmd, capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else None


def check_local(claude, codex):
    c_names = [p.get("name") for p in claude["plugins"]]
    x_names = [p.get("name") for p in codex["plugins"]]
    for path, names in ((CLAUDE, c_names), (CODEX, x_names)):
        dupes = sorted({n for n in names if names.count(n) > 1})
        if dupes:
            err(f"{path}: duplicate plugin names: {', '.join(dupes)}")
    only_c = sorted(set(c_names) - set(x_names))
    only_x = sorted(set(x_names) - set(c_names))
    if only_c:
        err(f"listed for Claude Code but not for Codex: {', '.join(only_c)}")
    if only_x:
        err(f"listed for Codex but not for Claude Code: {', '.join(only_x)}")

    for p in codex["plugins"]:
        n = p.get("name", "?")
        pol = p.get("policy") or {}
        if pol.get("installation") not in INSTALLATION:
            err(f"{CODEX}: {n}: policy.installation is {pol.get('installation')!r}, "
                f"Codex accepts {', '.join(sorted(INSTALLATION))}")
        if pol.get("authentication") not in AUTHENTICATION:
            err(f"{CODEX}: {n}: policy.authentication is {pol.get('authentication')!r}, "
                f"Codex accepts {', '.join(sorted(AUTHENTICATION))}")
        if not p.get("category"):
            err(f"{CODEX}: {n}: category is required")

    repos = {}
    for path, plugins in ((CLAUDE, claude["plugins"]), (CODEX, codex["plugins"])):
        for p in plugins:
            repo = github_repo(p, path)
            if repo and p.get("name"):
                repos.setdefault(p["name"], {})[path] = repo
    for name, by in sorted(repos.items()):
        if len(set(by.values())) > 1:
            err(f"{name}: the two manifests point at different repositories: "
                + ", ".join(f"{k} -> {v}" for k, v in by.items()))
    return repos


def check_remote(repos):
    if not shutil.which("gh"):
        err("`gh` is not installed; run with --offline to skip the GitHub checks")
        return
    for name, by in sorted(repos.items()):
        repo = next(iter(by.values()))
        if gh(f"repos/{repo}") is None:
            err(f"{name}: {repo} does not resolve on GitHub")
            continue
        for path, manifest in PLUGIN_MANIFEST.items():
            if path not in by:
                continue
            body = gh(f"repos/{repo}/contents/{manifest}", raw=True)
            if body is None:
                err(f"{name}: {path} lists it, but {repo} has no {manifest}")
                continue
            try:
                pj = json.loads(body)
            except ValueError as e:
                err(f"{name}: {repo}/{manifest} is not valid JSON: {e}")
                continue
            if pj.get("name") != name:
                err(f"{name}: {repo}/{manifest} calls itself {pj.get('name')!r}")
        print(f"ok  {name:<14} {repo}")


def main():
    offline = "--offline" in sys.argv[1:]
    repos = check_local(load(CLAUDE), load(CODEX))
    if not offline:
        check_remote(repos)
    if errors:
        print("\n".join(errors), file=sys.stderr)
        sys.exit(1)
    print(f"both manifests agree on {len(repos)} plugins")


if __name__ == "__main__":
    main()
