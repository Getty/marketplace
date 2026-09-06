<p align="center">
  <img src="banner.png" width="800"
       alt="A llama in dungarees tending a market stall at sunset, under a sign reading Gettys Marketplace, with small robots and glowing plugin icons on the counter">
</p>

# Getty's plugins

One marketplace for every plugin I publish — for **Claude Code** and **Codex**.
Register it once and install what you need; no separate marketplace per plugin.

```
/plugin marketplace add Getty/marketplace          # Claude Code
codex plugin marketplace add Getty/marketplace     # Codex
```

## Plugins

| Plugin | What it does | License | Claude Code | Codex |
|---|---|:--:|:--:|:--:|
| [`agent-irc`](https://github.com/Getty/agent-irc) | Mirrors a session into IRC as it happens: each prompt, each tool call with its duration, subagents starting and finishing with what they consumed, the turn's total in tokens when it ends. One nick per session, so a channel of running agents reads like a team room. Python 3.9+, standard library only. Tool outputs never leave the machine. | Artistic-2.0 | ✅ | ✅ |
| [`briefing`](https://github.com/Getty/briefing) | Subagents declare the skills they need; a hook loads those skill bodies into the agent's context *before* its first turn. No "MANDATORY: read X first" pleading, no silent skips. | Artistic-2.0 | ✅ | ✅ |
| [`manage-skills`](https://github.com/Getty/manage-skills) | One source of truth per skill, hardlinks everywhere else. Ships the `manage-skills` CLI plus the skills that explain how to drive it. | MIT | ✅ | ✅ |
| [`skills`](https://github.com/Getty/skills) | The skills that belong to no single project: Perl house style and release tooling, git conventions, Kubernetes and containers, driving Claude Code and Codex headless, and the craft of writing skills themselves. A skill lives there only as long as nothing else claims it. | Artistic-2.0 | ✅ | ✅ |

```
/plugin install agent-irc@getty
/plugin install briefing@getty
/plugin install manage-skills@getty
/plugin install skills@getty

codex plugin add agent-irc@getty
codex plugin add briefing@getty
codex plugin add manage-skills@getty
codex plugin add skills@getty
```

### agent-irc, in one glance

A channel with one session in it:

```
<agent-irc-1> ▶ session e873ddde · claude claude-fable-5-1 · ~/dev/agent-irc
<agent-irc-1> » ok ich würde gern ein codex und claude plugin machen…
<agent-irc-1> ⚙ Bash 1.2s: ls -la && find . -maxdepth 3
<agent-irc-1> ⇢ subagent Explore: find hook payloads
<agent-irc-1> ⇠ subagent Explore done · 42s · 18 tools · 31k in / 2k out · claude-sonnet-5
<agent-irc-1> ⚠ permission: Bash: rm -rf build
<agent-irc-1> ✔ turn · 3m12s · 24 tools · 210k in (190k cached) / 6k out · claude-fable-5-1
```

The plugin bundles one MCP server; every hook hands its event to that server,
which formats a line and keeps the IRC connections open for the life of the
session. Configuration lives in the harness's own settings under the key
`agent-irc`: a list of `ircs://` URLs and a `level` — `activity` for the lines
above, `subactivity` to add the tool calls inside subagents, `full` to add the
complete prompt and answer texts. Passwords come from the environment via
`${VAR}`, so a committed project file never has to contain one. Codex asks once
to trust the plugin's hooks; until you do, nothing is sent. The exact line
format, the sending-rate knobs, and what each level discloses are in the
[plugin's README](https://github.com/Getty/agent-irc#readme) and its
[privacy note](https://github.com/Getty/agent-irc/blob/main/PRIVACY.md).

### manage-skills on Codex

A Codex plugin manifest cannot put a command on `PATH`, so `manage-skills` is reached by
path there: the script ships in the plugin root, and the skill that documents it says
where. Codex gives the model the absolute path of every `SKILL.md`, so a relative
reference resolves without anything else. If you want the command in your own shell too —
worth doing in either harness, since a plugin only reaches the agent's shell — install it
directly (below).

## manage-skills also runs on its own track

This catalog is the convenient way in. For `manage-skills` it is not the only one:

```
curl -fsSL https://raw.githubusercontent.com/Getty/manage-skills/main/install.sh | sh
```

It is a standalone CLI first and a plugin second — a single self-contained bash script
with no dependencies, versioned on its own release cycle. It needs neither this catalog
nor any particular agent harness, which is rather the point of it.

## What this repo is

Only a catalog. Adding a plugin here means one entry, not a copy of anything. Nothing is
pinned: every entry tracks its repository's `main`, and refreshing the marketplace brings
whatever is there. Two manifests sit side by side because the two ecosystems disagree on
the format:

| | Claude Code | Codex |
|---|---|---|
| Manifest | `.claude-plugin/marketplace.json` | `.agents/plugins/marketplace.json` |
| Source type | `github` + `repo` | `url` / `git-subdir` |
| Per entry | tags, category | `policy.installation`, `policy.authentication`, `category` |

Codex does read `.claude-plugin/marketplace.json` as a legacy location, but it does not
accept Claude Code's schema there, so one file cannot serve both.

CI keeps the two honest: both manifests must list the same plugins and point at the same
repositories, every repository must answer and carry a plugin manifest for each harness
it is listed for, and the current Claude Code and Codex CLIs must accept the catalog as
they would on your machine. `scripts/check-manifests.py` runs the first part by hand.

## License

The catalog is MIT. Each plugin carries its own license; the table above lists them.
