# OpenClaw CLI Commands (Condensed Reference)

Generated from openclaw v2026.2.21-2. One line per command, key flags only.

---

## 1. Channels

```
channels add          Add/update a channel account. --channel <name> --token <token> --account <id>
channels remove       Disable or delete a channel account. --channel <name> --account <id> --delete
channels login        Link a channel account (QR/auth flow). --channel <channel> --account <id> --verbose
channels logout       Log out of a channel session. --channel <channel> --account <id>
channels list         List configured channels + auth profiles. --json --no-usage
channels status       Show gateway channel status. --probe --json --timeout <ms>
channels capabilities Show provider capabilities (intents/scopes/features). --channel <name> --json --target <dest>
channels resolve      Resolve channel/user names to IDs. --channel <name> --kind <auto|user|group> --json
channels logs         Show recent channel logs from gateway log file. --channel <name> --lines <n> --json
```

## 2. Models

```
models set            Set the default model. <model> (model id or alias)
models set-image      Set the image model. <model>
models list           List models (configured by default). --all --json --local --provider <name>
models scan           Scan OpenRouter free models for tools + images. --set-default --set-image --json --yes
models status         Show configured model state. --agent <id> --probe --json --check --plain
models aliases        Manage model aliases. Sub: add, list, remove
models auth           Manage model auth profiles. Sub: add, login, login-github-copilot, order, paste-token, setup-token
models fallbacks      Manage model fallback list. Sub: add, list, remove, clear
models image-fallbacks Manage image model fallback list. Sub: add, list, remove, clear
```

## 3. Plugins

```
plugins enable        Enable a plugin in config. <id>
plugins disable       Disable a plugin in config. <id>
plugins install       Install a plugin (path, archive, or npm spec). <path-or-spec> --link --pin
plugins uninstall     Uninstall a plugin. <id> --dry-run --force --keep-files
plugins list          List discovered plugins. --enabled --json --verbose
plugins info          Show plugin details. <id> --json
plugins doctor        Report plugin load issues.
plugins update        Update installed plugins (npm installs only). [id] --all --dry-run
```

## 4. Gateway

```
gateway run           Run the WebSocket Gateway (foreground). --port <port> --bind <mode> --token <token> --force --verbose
gateway start         Start the Gateway service (launchd/systemd/schtasks). --json
gateway stop          Stop the Gateway service. --json
gateway status        Show gateway service status + probe. --deep --json --no-probe --token <token> --url <url>
gateway install       Install the Gateway service.
gateway uninstall     Uninstall the Gateway service.
gateway restart       Restart the Gateway service.
gateway health        Fetch Gateway health.
gateway call          Call a Gateway RPC method directly.
gateway discover      Discover gateways via Bonjour (local + wide-area).
gateway probe         Show gateway reachability + discovery + health + status summary.
gateway usage-cost    Fetch usage cost summary from session logs.
```

## 5. Config

```
config get            Get a config value by dot path. <path> --json
config set            Set a config value by dot path. <path> <value> --json --strict-json
config unset          Remove a config value by dot path. <path>
configure             Interactive setup wizard. --section <workspace|model|web|gateway|daemon|channels|skills|health>
```

## 6. Agents

```
agents list           List configured agents. --bindings --json
agents add            Add a new isolated agent. (interactive)
agents delete         Delete an agent and prune workspace/state. <id> --force --json
agents set-identity   Update an agent identity (name/theme/emoji/avatar).
```

## 7. Cron

```
cron list             List cron jobs. --all --json --token <token> --url <url>
cron add              Add a cron job. --name <name> --cron <expr> --every <duration> --at <when> --message <text> --agent <id> --announce --deliver --tz <iana>
cron rm               Remove a cron job. <id> --json
cron enable           Enable a cron job. <id>
cron disable          Disable a cron job. <id>
cron run              Run a cron job now (debug). <id> --due
cron edit             Edit a cron job (patch fields).
cron runs             Show cron run history (JSONL-backed).
cron status           Show cron scheduler status.
```

## 8. Hooks

```
hooks list            List all hooks. --eligible --json --verbose
hooks enable          Enable a hook.
hooks disable         Disable a hook.
hooks info            Show detailed information about a hook.
hooks install         Install a hook pack (path, archive, or npm spec).
hooks check           Check hooks eligibility status.
hooks update          Update installed hooks (npm installs only).
```

## 9. Security

```
security audit        Audit config + local state for security foot-guns. --deep --fix --json
```

## 10. Sandbox

```
sandbox list          List sandbox containers and their status. --browser --json
sandbox recreate      Remove containers to force recreation with updated config. --all --session <id> --agent <id>
sandbox explain       Explain effective sandbox/tool policy for a session/agent.
```

## 11. Memory

```
memory search         Search memory files. <query> --agent <id> --json --max-results <n> --min-score <n>
memory index          Reindex memory files. --force
memory status         Show memory search index status. --json
```

## 12. Message

```
message send          Send a message. --channel <ch> --target <dest> --message <text> --media <path-or-url> --reply-to <id> --silent --buttons <json> --json
message read          Read recent messages. --channel <ch> --target <dest> --limit <n> --before <id> --after <id> --json
message edit          Edit a message.
message delete        Delete a message.
message broadcast     Broadcast a message to multiple targets.
message search        Search Discord messages.
message react         Add or remove a reaction. --emoji <emoji> --message-id <id>
message reactions     List reactions on a message.
message pin           Pin a message.
message unpin         Unpin a message.
message pins          List pinned messages.
message poll          Send a poll. --poll-question <text> --poll-option <opt>
message ban           Ban a member.
message kick          Kick a member.
message timeout       Timeout a member.
message permissions   Fetch channel permissions.
message thread        Thread actions.
message channel       Channel actions.
message member        Member actions.
message role          Role actions.
message emoji         Emoji actions.
message sticker       Sticker actions.
message event         Event actions.
message voice         Voice actions.
```

## 13. Pairing

```
pairing list          List pending pairing requests. [channel] --account <id> --json
pairing approve       Approve a pairing code and allow that sender. <codeOrChannel> [code] --channel <ch> --notify
```

## 14. Devices

```
devices list          List pending and paired devices. --json --token <token> --url <url>
devices approve       Approve a pending device pairing request.
devices reject        Reject a pending device pairing request.
devices remove        Remove a paired device entry. <deviceId> --json
devices revoke        Revoke a device token for a role.
devices rotate        Rotate a device token for a role.
devices clear         Clear paired devices from the gateway table.
```

## 15. Directory

```
directory self        Show the current account user. --channel <name> --account <id> --json
directory peers list  List peers (contacts/users). --channel <name> --query <text>
directory groups list List available groups/channels. --channel <name>
directory groups members List members for a specific group. --channel <name> --group-id <id>
```

## 16. Browser

```
browser start         Start the browser (no-op if already running).
browser stop          Stop the browser (best-effort).
browser status        Show browser status.
browser open          Open a URL in a new tab. <url>
browser close         Close a tab. [targetId]
browser tabs          List open tabs.
browser focus         Focus a tab by target id.
browser navigate      Navigate the current tab to a URL. <url>
browser screenshot    Capture a screenshot. --full-page --ref <n>
browser snapshot      Capture a snapshot (AI or accessibility tree). --format <ai|aria> --efficient --labels --limit <n>
browser click         Click an element by ref. <ref> --double
browser type          Type into an element by ref. <ref> <text> --submit
browser press         Press a key. <key>
browser hover         Hover an element by ref. <ref>
browser drag          Drag from one ref to another. <from> <to>
browser select        Select option(s) in a select element. <ref> <options...>
browser fill          Fill a form with JSON field descriptors. --fields <json>
browser upload        Arm file upload for the next file chooser. <path>
browser dialog        Arm the next modal dialog. --accept
browser wait          Wait for time, selector, URL, load state, or JS. --text <text>
browser evaluate      Evaluate a function against the page or ref. --fn <js> --ref <n>
browser console       Get recent console messages. --level <level>
browser errors        Get recent page errors.
browser requests      Get recent network requests.
browser cookies       Read/write cookies.
browser storage       Read/write localStorage/sessionStorage.
browser resize        Resize the viewport. <width> <height>
browser pdf           Save page as PDF.
browser download      Click a ref and save the resulting download.
browser highlight     Highlight an element by ref.
browser scrollintoview Scroll an element into view by ref.
browser tab           Tab shortcuts (index-based).
browser trace         Record a Playwright trace.
browser set           Browser environment settings.
browser profiles      List all browser profiles.
browser create-profile Create a new browser profile.
browser delete-profile Delete a browser profile.
browser reset-profile  Reset browser profile (moves to Trash).
browser extension     Chrome extension helpers.
browser responsebody  Wait for a network response and return its body.
browser waitfordownload Wait for the next download (and save it).
```

## 17. Nodes

```
node run              Run the headless node host (foreground). --host <ip> --port <port>
node install          Install the node host service (launchd/systemd/schtasks).
node uninstall        Uninstall the node host service.
node restart          Restart the node host service.
node stop             Stop the node host service. --json
node status           Show node host status. --json
nodes list            List pending and paired nodes. --connected --json --last-connected <duration>
nodes status          List known nodes with connection status and capabilities.
nodes pending         List pending pairing requests.
nodes approve         Approve a pending pairing request.
nodes reject          Reject a pending pairing request.
nodes rename          Rename a paired node (display name override).
nodes describe        Describe a node (capabilities + supported invoke commands).
nodes invoke          Invoke a command on a paired node. --node <id> --command <cmd> --params <json>
nodes run             Run a shell command on a node (mac only). --node <id> --raw <cmd>
nodes camera          Capture camera media from a paired node. --node <id>
nodes canvas          Capture or render canvas content from a paired node.
nodes screen          Capture screen recordings from a paired node.
nodes location        Fetch location from a paired node.
nodes notify          Send a local notification on a node (mac only).
nodes push            Send an APNs test push to an iOS node.
```

## 18. DNS

```
dns setup             Set up CoreDNS for unicast DNS-SD (Wide-Area Bonjour). --domain <domain> --apply
```

## 19. Approvals

```
approvals get         Fetch exec approvals snapshot.
approvals set         Replace exec approvals with a JSON file.
approvals allowlist   Edit the per-agent allowlist.
```

## 20. System

```
system event          Enqueue a system event and optionally trigger a heartbeat.
system heartbeat      Heartbeat controls. Sub: enable, disable, last
system presence       List system presence entries. --json --token <token> --url <url>
```

## 21. Update

```
update                Update OpenClaw (git or npm). --channel <stable|beta|dev> --tag <dist-tag|version> --yes --no-restart --json --timeout <s>
update status         Show update channel and version status.
update wizard         Interactive update wizard.
```

## 22. Webhooks

```
webhooks gmail        Gmail Pub/Sub hooks (via gogcli).
```

## 23. ACP

```
acp                   Run an ACP bridge backed by the Gateway. --url <url> --token <token> --session <key> --verbose
acp client            Run an interactive ACP client against the local ACP bridge.
```

## 24. Skills

```
skills list           List all available skills. --eligible --json --verbose
skills info           Show detailed information about a skill. <name> --json
skills check          Check which skills are ready vs missing requirements.
```

## 25. Other Top-Level

```
doctor                Health checks + quick fixes for gateway and channels. --fix --repair --deep --force --non-interactive --yes
health                Fetch health from the running gateway. --json --verbose --timeout <ms>
status                Show channel health + recent session recipients. --all --deep --json --usage --timeout <ms>
logs                  Tail gateway file logs via RPC. --follow --limit <n> --json --local-time --token <token> --url <url>
dashboard             Open the Control UI with your current token. --no-open
tui                   Open a terminal UI connected to the Gateway. --session <key> --deliver --thinking <level> --token <token> --url <url>
sessions              List stored conversation sessions. --active <minutes> --json --verbose
agent                 Run one agent turn via the Gateway. --to <number> --message <text> --agent <id> --deliver --channel <ch> --thinking <level> --local --json --timeout <s> --verbose
onboard               Interactive onboarding wizard. --flow <quickstart|advanced|manual> --mode <local|remote> --non-interactive (many provider key flags)
setup                 Initialize config and agent workspace. --mode <local|remote> --workspace <dir> --wizard --non-interactive
reset                 Reset local config/state (keeps CLI). --scope <config|config+creds+sessions|full> --dry-run --yes
uninstall             Uninstall gateway service + local data. --all --service --state --workspace --app --dry-run --yes
qr                    Generate iOS pairing QR code and setup code. --json --setup-code-only --remote --token <token> --url <url>
completion            Generate shell completion script.
docs                  Search the live OpenClaw docs. <query>
daemon install        Install the Gateway service (legacy alias). Also: start, stop, restart, status, uninstall
```
