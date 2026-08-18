# Getty's plugins

One marketplace for every plugin I publish — for **Claude Code** and **Codex**.
Register it once and install what you need; no separate marketplace per plugin.

```
/plugin marketplace add Getty/marketplace          # Claude Code
codex plugin marketplace add Getty/marketplace     # Codex
```

## Plugins

| Plugin | What it does | Claude Code | Codex |
|---|---|:--:|:--:|
| [`briefing`](https://github.com/Getty/briefing) | Subagents declare the skills they need; a hook loads those skill bodies into the agent's context *before* its first turn. No "MANDATORY: read X first" pleading, no silent skips. | ✅ | ✅ |
| [`manage-skills`](https://github.com/Getty/manage-skills) | One source of truth per skill, hardlinks everywhere else. Ships the `manage-skills` CLI plus the skills that explain how to drive it. | ✅ | ✅ |

```
/plugin install briefing@getty
/plugin install manage-skills@getty

codex plugin add briefing@getty
codex plugin add manage-skills@getty
```

A Codex plugin manifest cannot put a command on `PATH`, so `manage-skills` is reached by
path there: the script ships in the plugin root, and the skill that documents it says
where. Codex gives the model the absolute path of every `SKILL.md`, so a relative
reference resolves without anything else. If you want the command in your own shell too —
worth doing in either harness, since a plugin only reaches the agent's shell — install it
directly (below).

## Every plugin also runs on its own track

This catalog is the convenient way in, never the only one. Each plugin lives in and is
released from its own repository, keeps its own version, and stays installable without
this repo:

```
/plugin marketplace add Getty/briefing        # briefing is its own one-plugin marketplace
codex plugin marketplace add Getty/briefing

curl -fsSL https://raw.githubusercontent.com/Getty/manage-skills/main/install.sh | sh
```

`manage-skills` is a standalone CLI first and a plugin second: a single self-contained
bash script with no dependencies, versioned on its own release cycle. It needs neither
this catalog nor any particular agent harness — that is rather the point of it.

## What this repo is

Only a catalog. Adding a plugin here means one entry, not a copy of anything. Two
manifests sit side by side because the two ecosystems disagree on the format:

| | Claude Code | Codex |
|---|---|---|
| Manifest | `.claude-plugin/marketplace.json` | `.agents/plugins/marketplace.json` |
| Source type | `github` + `repo` | `url` / `git-subdir` |
| Per entry | tags, category | `policy.installation`, `policy.authentication`, `category` |

Codex does read `.claude-plugin/marketplace.json` as a legacy location, but it does not
accept Claude Code's schema there, so one file cannot serve both.

## License

The catalog is MIT. Each plugin carries its own license — see the table above.
