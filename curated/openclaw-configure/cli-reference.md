# OpenClaw CLI Reference
Generated from `openclaw --help` (v2026.2.21-2)


# `openclaw`

```
🦞 OpenClaw 2026.2.21-2 (35a57bc) — No $999 stand required.

Usage: openclaw [options] [command]

Options:
  --dev             Dev profile: isolate state under ~/.openclaw-dev, default
                    gateway port 19001, and shift derived ports (browser/canvas)
  -h, --help        Display help for command
  --no-color        Disable ANSI colors
  --profile <name>  Use a named profile (isolates
                    OPENCLAW_STATE_DIR/OPENCLAW_CONFIG_PATH under
                    ~/.openclaw-<name>)
  -V, --version     output the version number

Commands:
  Hint: commands suffixed with * have subcommands. Run <command> --help for details.
  acp *             Agent Control Protocol tools
  agent             Run one agent turn via the Gateway
  agents *          Manage isolated agents (workspaces, auth, routing)
  approvals *       Manage exec approvals (gateway or node host)
  browser *         Manage OpenClaw's dedicated browser (Chrome/Chromium)
  channels *        Manage connected chat channels (Telegram, Discord, etc.)
  clawbot *         Legacy clawbot command aliases
  completion        Generate shell completion script
  config *          Non-interactive config helpers (get/set/unset). Default:
                    starts setup wizard.
  configure         Interactive setup wizard for credentials, channels, gateway,
                    and agent defaults
  cron *            Manage cron jobs via the Gateway scheduler
  daemon *          Gateway service (legacy alias)
  dashboard         Open the Control UI with your current token
  devices *         Device pairing + token management
  directory *       Lookup contact and group IDs (self, peers, groups) for
                    supported chat channels
  dns *             DNS helpers for wide-area discovery (Tailscale + CoreDNS)
  docs              Search the live OpenClaw docs
  doctor            Health checks + quick fixes for the gateway and channels
  gateway *         Run, inspect, and query the WebSocket Gateway
  health            Fetch health from the running gateway
  help              Display help for command
  hooks *           Manage internal agent hooks
  logs              Tail gateway file logs via RPC
  memory *          Search and reindex memory files
  message *         Send, read, and manage messages
  models *          Discover, scan, and configure models
  node *            Run and manage the headless node host service
  nodes *           Manage gateway-owned node pairing and node commands
  onboard           Interactive onboarding wizard for gateway, workspace, and
                    skills
  pairing *         Secure DM pairing (approve inbound requests)
  plugins *         Manage OpenClaw plugins and extensions
  qr                Generate iOS pairing QR/setup code
  reset             Reset local config/state (keeps the CLI installed)
  sandbox *         Manage sandbox containers for agent isolation
  security *        Security tools and local config audits
  sessions          List stored conversation sessions
  setup             Initialize local config and agent workspace
  skills *          List and inspect available skills
  status            Show channel health and recent session recipients
  system *          System events, heartbeat, and presence
  tui               Open a terminal UI connected to the Gateway
  uninstall         Uninstall the gateway service + local data (CLI remains)
  update *          Update OpenClaw and inspect update channel status
  webhooks *        Webhook helpers and integrations

Examples:
  openclaw models --help
    Show detailed help for the models command.
  openclaw channels login --verbose
    Link personal WhatsApp Web and show QR + connection logs.
  openclaw message send --target +15555550123 --message "Hi" --json
    Send via your web session and print JSON result.
  openclaw gateway --port 18789
    Run the WebSocket Gateway locally.
  openclaw --dev gateway
    Run a dev Gateway (isolated state/config) on ws://127.0.0.1:19001.
  openclaw gateway --force
    Kill anything bound to the default gateway port, then start it.
  openclaw gateway ...
    Gateway control via WebSocket.
  openclaw agent --to +15555550123 --message "Run summary" --deliver
    Talk directly to the agent using the Gateway; optionally send the WhatsApp reply.
  openclaw message send --channel telegram --target @mychat --message "Hi"
    Send via your Telegram bot.

Docs: https://docs.openclaw.ai/cli
```

## `openclaw acp`

```
🦞 OpenClaw 2026.2.21-2 (35a57bc) — Your terminal just grew claws—type something and let the bot pinch the busywork.

Usage: openclaw acp [options] [command]

Run an ACP bridge backed by the Gateway

Options:
  -h, --help               Display help for command
  --no-prefix-cwd          Do not prefix prompts with the working directory
  --password <password>    Gateway password (if required)
  --password-file <path>   Read gateway password from file
  --require-existing       Fail if the session key/label does not exist
                           (default: false)
  --reset-session          Reset the session key before first use (default:
                           false)
  --session <key>          Default session key (e.g. agent:main:main)
  --session-label <label>  Default session label to resolve
  --token <token>          Gateway token (if required)
  --token-file <path>      Read gateway token from file
  --url <url>              Gateway WebSocket URL (defaults to gateway.remote.url
                           when configured)
  --verbose, -v            Verbose logging to stderr (default: false)

Commands:
  client                   Run an interactive ACP client against the local ACP
                           bridge

Docs: https://docs.openclaw.ai/cli/acp
```

## `openclaw agent`

```
🦞 OpenClaw 2026.2.21-2 (35a57bc) — Type the command with confidence—nature will provide the stack trace if needed.

Usage: openclaw agent [options]

Run an agent turn via the Gateway (use --local for embedded)

Options:
  --agent <id>               Agent id (overrides routing bindings)
  --channel <channel>        Delivery channel:
                             last|telegram|whatsapp|discord|irc|googlechat|slack|signal|imessage|feishu|nostr|msteams|mattermost|nextcloud-talk|matrix|bluebubbles|line|zalo|zalouser|tlon
                             (default: whatsapp)
  --deliver                  Send the agent's reply back to the selected channel
                             (default: false)
  -h, --help                 Display help for command
  --json                     Output result as JSON (default: false)
  --local                    Run the embedded agent locally (requires model
                             provider API keys in your shell) (default: false)
  -m, --message <text>       Message body for the agent
  --reply-account <id>       Delivery account id override
  --reply-channel <channel>  Delivery channel override (separate from routing)
  --reply-to <target>        Delivery target override (separate from session
                             routing)
  --session-id <id>          Use an explicit session id
  -t, --to <number>          Recipient number in E.164 used to derive the
                             session key
  --thinking <level>         Thinking level: off | minimal | low | medium | high
  --timeout <seconds>        Override agent command timeout (seconds, default
                             600 or config value)
  --verbose <on|off>         Persist agent verbose level for the session

Examples:
  openclaw agent --to +15555550123 --message "status update"
    Start a new session.
  openclaw agent --agent ops --message "Summarize logs"
    Use a specific agent.
  openclaw agent --session-id 1234 --message "Summarize inbox" --thinking medium
    Target a session with explicit thinking level.
  openclaw agent --to +15555550123 --message "Trace logs" --verbose on --json
    Enable verbose logging and JSON output.
  openclaw agent --to +15555550123 --message "Summon reply" --deliver
    Deliver reply.
  openclaw agent --agent ops --message "Generate report" --deliver --reply-channel slack --reply-to "#reports"
    Send reply to a different channel/target.

Docs: https://docs.openclaw.ai/cli/agent
```

## `openclaw agents`

```
🦞 OpenClaw 2026.2.21-2 (35a57bc) — Shell yeah—I'm here to pinch the toil and leave you the glory.

Usage: openclaw agents [options] [command]

Manage isolated agents (workspaces + auth + routing)

Options:
  -h, --help    Display help for command

Commands:
  add           Add a new isolated agent
  delete        Delete an agent and prune workspace/state
  list          List configured agents
  set-identity  Update an agent identity (name/theme/emoji/avatar)

Docs: https://docs.openclaw.ai/cli/agents
```

## `openclaw approvals`

```
🦞 OpenClaw 2026.2.21-2 (35a57bc) — I'm basically a Swiss Army knife, but with more opinions and fewer sharp edges.

Usage: openclaw approvals|exec-approvals [options] [command]

Manage exec approvals (gateway or node host)

Options:
  -h, --help  Display help for command

Commands:
  allowlist   Edit the per-agent allowlist
  get         Fetch exec approvals snapshot
  help        Display help for command
  set         Replace exec approvals with a JSON file

Docs: https://docs.openclaw.ai/cli/approvals
```

## `openclaw browser`

```
🦞 OpenClaw 2026.2.21-2 (35a57bc) — No $999 stand required.

Usage: openclaw browser [options] [command]

Manage OpenClaw's dedicated browser (Chrome/Chromium)

Options:
  --browser-profile <name>  Browser profile name (default from config)
  --expect-final            Wait for final response (agent) (default: false)
  -h, --help                Display help for command
  --json                    Output machine-readable JSON (default: false)
  --timeout <ms>            Timeout in ms (default: "30000")
  --token <token>           Gateway token (if required)
  --url <url>               Gateway WebSocket URL (defaults to
                            gateway.remote.url when configured)

Commands:
  click                     Click an element by ref from snapshot
  close                     Close a tab (target id optional)
  console                   Get recent console messages
  cookies                   Read/write cookies
  create-profile            Create a new browser profile
  delete-profile            Delete a browser profile
  dialog                    Arm the next modal dialog (alert/confirm/prompt)
  download                  Click a ref and save the resulting download
  drag                      Drag from one ref to another
  errors                    Get recent page errors
  evaluate                  Evaluate a function against the page or a ref
  extension                 Chrome extension helpers
  fill                      Fill a form with JSON field descriptors
  focus                     Focus a tab by target id (or unique prefix)
  highlight                 Highlight an element by ref
  hover                     Hover an element by ai ref
  navigate                  Navigate the current tab to a URL
  open                      Open a URL in a new tab
  pdf                       Save page as PDF
  press                     Press a key
  profiles                  List all browser profiles
  requests                  Get recent network requests (best-effort)
  reset-profile             Reset browser profile (moves it to Trash)
  resize                    Resize the viewport
  responsebody              Wait for a network response and return its body
  screenshot                Capture a screenshot (MEDIA:<path>)
  scrollintoview            Scroll an element into view by ref from snapshot
  select                    Select option(s) in a select element
  set                       Browser environment settings
  snapshot                  Capture a snapshot (default: ai; aria is the
                            accessibility tree)
  start                     Start the browser (no-op if already running)
  status                    Show browser status
  stop                      Stop the browser (best-effort)
  storage                   Read/write localStorage/sessionStorage
  tab                       Tab shortcuts (index-based)
  tabs                      List open tabs
  trace                     Record a Playwright trace
  type                      Type into an element by ref from snapshot
  upload                    Arm file upload for the next file chooser
  wait                      Wait for time, selector, URL, load state, or JS
                            conditions
  waitfordownload           Wait for the next download (and save it)

Examples:
  openclaw browser status
  openclaw browser start
  openclaw browser stop
  openclaw browser tabs
  openclaw browser open https://example.com
  openclaw browser focus abcd1234
  openclaw browser close abcd1234
  openclaw browser screenshot
  openclaw browser screenshot --full-page
  openclaw browser screenshot --ref 12
  openclaw browser snapshot
  openclaw browser snapshot --format aria --limit 200
  openclaw browser snapshot --efficient
  openclaw browser snapshot --labels
  openclaw browser navigate https://example.com
  openclaw browser resize 1280 720
  openclaw browser click 12 --double
  openclaw browser type 23 "hello" --submit
  openclaw browser press Enter
  openclaw browser hover 44
  openclaw browser drag 10 11
  openclaw browser select 9 OptionA OptionB
  openclaw browser upload /tmp/openclaw/uploads/file.pdf
  openclaw browser fill --fields '[{"ref":"1","value":"Ada"}]'
  openclaw browser dialog --accept
  openclaw browser wait --text "Done"
  openclaw browser evaluate --fn '(el) => el.textContent' --ref 7
  openclaw browser console --level error
  openclaw browser pdf

Docs: https://docs.openclaw.ai/cli/browser
```

## `openclaw channels`

```
🦞 OpenClaw 2026.2.21-2 (35a57bc) — I'm basically a Swiss Army knife, but with more opinions and fewer sharp edges.

Usage: openclaw channels [options] [command]

Manage connected chat channels and accounts

Options:
  -h, --help    Display help for command

Commands:
  add           Add or update a channel account
  capabilities  Show provider capabilities (intents/scopes + supported features)
  help          Display help for command
  list          List configured channels + auth profiles
  login         Link a channel account (if supported)
  logout        Log out of a channel session (if supported)
  logs          Show recent channel logs from the gateway log file
  remove        Disable or delete a channel account
  resolve       Resolve channel/user names to IDs
  status        Show gateway channel status (use status --deep for local)

Examples:
  openclaw channels list
    List configured channels and auth profiles.
  openclaw channels status --probe
    Run channel status checks and probes.
  openclaw channels add --channel telegram --token <token>
    Add or update a channel account non-interactively.
  openclaw channels login --channel whatsapp
    Link a WhatsApp Web account.

Docs: https://docs.openclaw.ai/cli/channels
```

## `openclaw config`

```
🦞 OpenClaw 2026.2.21-2 (35a57bc) — Your terminal just grew claws—type something and let the bot pinch the busywork.

Usage: openclaw config [options] [command]

Non-interactive config helpers (get/set/unset). Run without subcommand for the
setup wizard.

Options:
  -h, --help           Display help for command
  --section <section>  Configure wizard sections (repeatable). Use with no
                       subcommand. (default: [])

Commands:
  get                  Get a config value by dot path
  set                  Set a config value by dot path
  unset                Remove a config value by dot path

Docs: https://docs.openclaw.ai/cli/config
```

## `openclaw configure`

```
🦞 OpenClaw 2026.2.21-2 (35a57bc) — If something's on fire, I can't extinguish it—but I can write a beautiful postmortem.

Usage: openclaw configure [options]

Interactive setup wizard for credentials, channels, gateway, and agent defaults

Options:
  -h, --help           Display help for command
  --section <section>  Configuration sections (repeatable). Options: workspace,
                       model, web, gateway, daemon, channels, skills, health
                       (default: [])

Docs: https://docs.openclaw.ai/cli/configure
```

## `openclaw cron`

```
🦞 OpenClaw 2026.2.21-2 (35a57bc) — Hot reload for config, cold sweat for deploys.

Usage: openclaw cron [options] [command]

Manage cron jobs (via Gateway)

Options:
  -h, --help  Display help for command

Commands:
  add         Add a cron job
  disable     Disable a cron job
  edit        Edit a cron job (patch fields)
  enable      Enable a cron job
  help        Display help for command
  list        List cron jobs
  rm          Remove a cron job
  run         Run a cron job now (debug)
  runs        Show cron run history (JSONL-backed)
  status      Show cron scheduler status

Docs: https://docs.openclaw.ai/cli/cron
```

## `openclaw daemon`

```
🦞 OpenClaw 2026.2.21-2 (35a57bc) — I'm like tmux: confusing at first, then suddenly you can't live without me.

Usage: openclaw daemon [options] [command]

Manage the Gateway service (launchd/systemd/schtasks)

Options:
  -h, --help  Display help for command

Commands:
  help        Display help for command
  install     Install the Gateway service (launchd/systemd/schtasks)
  restart     Restart the Gateway service (launchd/systemd/schtasks)
  start       Start the Gateway service (launchd/systemd/schtasks)
  status      Show service install status + probe the Gateway
  stop        Stop the Gateway service (launchd/systemd/schtasks)
  uninstall   Uninstall the Gateway service (launchd/systemd/schtasks)

Docs: https://docs.openclaw.ai/cli/gateway
```

## `openclaw dashboard`

```
🦞 OpenClaw 2026.2.21-2 (35a57bc) — Type the command with confidence—nature will provide the stack trace if needed.

Usage: openclaw dashboard [options]

Open the Control UI with your current token

Options:
  -h, --help  Display help for command
  --no-open   Print URL but do not launch a browser

Docs: https://docs.openclaw.ai/cli/dashboard
```

## `openclaw devices`

```
🦞 OpenClaw 2026.2.21-2 (35a57bc) — Your task has been queued; your dignity has been deprecated.

Usage: openclaw devices [options] [command]

Device pairing and auth tokens

Options:
  -h, --help  Display help for command

Commands:
  approve     Approve a pending device pairing request
  clear       Clear paired devices from the gateway table
  help        Display help for command
  list        List pending and paired devices
  reject      Reject a pending device pairing request
  remove      Remove a paired device entry
  revoke      Revoke a device token for a role
  rotate      Rotate a device token for a role
```

## `openclaw directory`

```
🦞 OpenClaw 2026.2.21-2 (35a57bc) — I'm the reason your shell history looks like a hacker-movie montage.

Usage: openclaw directory [options] [command]

Lookup contact and group IDs (self, peers, groups) for supported chat channels

Options:
  -h, --help  Display help for command

Commands:
  groups      Group directory
  peers       Peer directory (contacts/users)
  self        Show the current account user

Examples:
  openclaw directory self --channel slack
    Show the connected account identity.
  openclaw directory peers list --channel slack --query "alice"
    Search contact/user IDs by name.
  openclaw directory groups list --channel discord
    List available groups/channels.
  openclaw directory groups members --channel discord --group-id <id>
    List members for a specific group.

Docs: https://docs.openclaw.ai/cli/directory
```

## `openclaw dns`

```
🦞 OpenClaw 2026.2.21-2 (35a57bc) — Less clicking, more shipping, fewer "where did that file go" moments.

Usage: openclaw dns [options] [command]

DNS helpers for wide-area discovery (Tailscale + CoreDNS)

Options:
  -h, --help  Display help for command

Commands:
  help        Display help for command
  setup       Set up CoreDNS to serve your discovery domain for unicast DNS-SD
              (Wide-Area Bonjour)

Docs: https://docs.openclaw.ai/cli/dns
```

## `openclaw docs`

```
🦞 OpenClaw 2026.2.21-2 (35a57bc) — curl for conversations.

Usage: openclaw docs [options] [query...]

Search the live OpenClaw docs

Arguments:
  query       Search query

Options:
  -h, --help  Display help for command

Docs: https://docs.openclaw.ai/cli/docs
```

## `openclaw doctor`

```
🦞 OpenClaw 2026.2.21-2 (35a57bc) — Hot reload for config, cold sweat for deploys.

Usage: openclaw doctor [options]

Health checks + quick fixes for the gateway and channels

Options:
  --deep                      Scan system services for extra gateway installs
                              (default: false)
  --fix                       Apply recommended repairs (alias for --repair)
                              (default: false)
  --force                     Apply aggressive repairs (overwrites custom
                              service config) (default: false)
  --generate-gateway-token    Generate and configure a gateway token (default:
                              false)
  -h, --help                  Display help for command
  --no-workspace-suggestions  Disable workspace memory system suggestions
  --non-interactive           Run without prompts (safe migrations only)
                              (default: false)
  --repair                    Apply recommended repairs without prompting
                              (default: false)
  --yes                       Accept defaults without prompting (default: false)

Docs: https://docs.openclaw.ai/cli/doctor
```

## `openclaw gateway`

```
🦞 OpenClaw 2026.2.21-2 (35a57bc) — Turning "I'll reply later" into "my bot replied instantly".

Usage: openclaw gateway [options] [command]

Run, inspect, and query the WebSocket Gateway

Options:
  --allow-unconfigured       Allow gateway start without gateway.mode=local in
                             config (default: false)
  --auth <mode>              Gateway auth mode ("token"|"password")
  --bind <mode>              Bind mode
                             ("loopback"|"lan"|"tailnet"|"auto"|"custom").
                             Defaults to config gateway.bind (or loopback).
  --claude-cli-logs          Only show claude-cli logs in the console (includes
                             stdout/stderr) (default: false)
  --compact                  Alias for "--ws-log compact" (default: false)
  --dev                      Create a dev config + workspace if missing (no
                             BOOTSTRAP.md) (default: false)
  --force                    Kill any existing listener on the target port
                             before starting (default: false)
  -h, --help                 Display help for command
  --password <password>      Password for auth mode=password
  --port <port>              Port for the gateway WebSocket
  --raw-stream               Log raw model stream events to jsonl (default:
                             false)
  --raw-stream-path <path>   Raw stream jsonl path
  --reset                    Reset dev config + credentials + sessions +
                             workspace (requires --dev) (default: false)
  --tailscale <mode>         Tailscale exposure mode ("off"|"serve"|"funnel")
  --tailscale-reset-on-exit  Reset Tailscale serve/funnel configuration on
                             shutdown (default: false)
  --token <token>            Shared token required in connect.params.auth.token
                             (default: OPENCLAW_GATEWAY_TOKEN env if set)
  --verbose                  Verbose logging to stdout/stderr (default: false)
  --ws-log <style>           WebSocket log style ("auto"|"full"|"compact")
                             (default: "auto")

Commands:
  call                       Call a Gateway method
  discover                   Discover gateways via Bonjour (local + wide-area if
                             configured)
  health                     Fetch Gateway health
  install                    Install the Gateway service
                             (launchd/systemd/schtasks)
  probe                      Show gateway reachability + discovery + health +
                             status summary (local + remote)
  restart                    Restart the Gateway service
                             (launchd/systemd/schtasks)
  run                        Run the WebSocket Gateway (foreground)
  start                      Start the Gateway service
                             (launchd/systemd/schtasks)
  status                     Show gateway service status + probe the Gateway
  stop                       Stop the Gateway service (launchd/systemd/schtasks)
  uninstall                  Uninstall the Gateway service
                             (launchd/systemd/schtasks)
  usage-cost                 Fetch usage cost summary from session logs

Examples:
  openclaw gateway run
    Run the gateway in the foreground.
  openclaw gateway status
    Show service status and probe reachability.
  openclaw gateway discover
    Find local and wide-area gateway beacons.
  openclaw gateway call health
    Call a gateway RPC method directly.

Docs: https://docs.openclaw.ai/cli/gateway
```

## `openclaw health`

```
🦞 OpenClaw 2026.2.21-2 (35a57bc) — I can't fix your code taste, but I can fix your build and your backlog.

Usage: openclaw health [options]

Fetch health from the running gateway

Options:
  --debug         Alias for --verbose (default: false)
  -h, --help      Display help for command
  --json          Output JSON instead of text (default: false)
  --timeout <ms>  Connection timeout in milliseconds (default: "10000")
  --verbose       Verbose logging (default: false)

Docs: https://docs.openclaw.ai/cli/health
```

## `openclaw hooks`

```
🦞 OpenClaw 2026.2.21-2 (35a57bc) — Your AI assistant, now without the $3,499 headset.

Usage: openclaw hooks [options] [command]

Manage internal agent hooks

Options:
  -h, --help  Display help for command

Commands:
  check       Check hooks eligibility status
  disable     Disable a hook
  enable      Enable a hook
  info        Show detailed information about a hook
  install     Install a hook pack (path, archive, or npm spec)
  list        List all hooks
  update      Update installed hooks (npm installs only)

Docs: https://docs.openclaw.ai/cli/hooks
```

## `openclaw logs`

```
🦞 OpenClaw 2026.2.21-2 (35a57bc) — Say "stop" and I'll stop—say "ship" and we'll both learn a lesson.

Usage: openclaw logs [options]

Tail gateway file logs via RPC

Options:
  --expect-final   Wait for final response (agent) (default: false)
  --follow         Follow log output (default: false)
  -h, --help       Display help for command
  --interval <ms>  Polling interval in ms (default: "1000")
  --json           Emit JSON log lines (default: false)
  --limit <n>      Max lines to return (default: "200")
  --local-time     Display timestamps in local timezone (default: false)
  --max-bytes <n>  Max bytes to read (default: "250000")
  --no-color       Disable ANSI colors
  --plain          Plain text output (no ANSI styling) (default: false)
  --timeout <ms>   Timeout in ms (default: "30000")
  --token <token>  Gateway token (if required)
  --url <url>      Gateway WebSocket URL (defaults to gateway.remote.url when
                   configured)

Docs: https://docs.openclaw.ai/cli/logs
```

## `openclaw memory`

```
🦞 OpenClaw 2026.2.21-2 (35a57bc)
   If it's repetitive, I'll automate it; if it's hard, I'll bring jokes and a rollback plan.

Usage: openclaw memory [options] [command]

Search, inspect, and reindex memory files

Options:
  -h, --help  Display help for command

Commands:
  help        Display help for command
  index       Reindex memory files
  search      Search memory files
  status      Show memory search index status

Examples:
  openclaw memory status
    Show index and provider status.
  openclaw memory index --force
    Force a full reindex.
  openclaw memory search --query "deployment notes"
    Search indexed memory entries.
  openclaw memory status --json
    Output machine-readable JSON.

Docs: https://docs.openclaw.ai/cli/memory
```

## `openclaw message`

```
🦞 OpenClaw 2026.2.21-2 (35a57bc) — The UNIX philosophy meets your DMs.

Usage: openclaw message [options] [command]

Send, read, and manage messages and channel actions

Options:
  -h, --help   Display help for command

Commands:
  ban          Ban a member
  broadcast    Broadcast a message to multiple targets
  channel      Channel actions
  delete       Delete a message
  edit         Edit a message
  emoji        Emoji actions
  event        Event actions
  kick         Kick a member
  member       Member actions
  permissions  Fetch channel permissions
  pin          Pin a message
  pins         List pinned messages
  poll         Send a poll
  react        Add or remove a reaction
  reactions    List reactions on a message
  read         Read recent messages
  role         Role actions
  search       Search Discord messages
  send         Send a message
  sticker      Sticker actions
  thread       Thread actions
  timeout      Timeout a member
  unpin        Unpin a message
  voice        Voice actions

Examples:
  openclaw message send --target +15555550123 --message "Hi"
    Send a text message.
  openclaw message send --target +15555550123 --message "Hi" --media photo.jpg
    Send a message with media.
  openclaw message poll --channel discord --target channel:123 --poll-question "Snack?" --poll-option Pizza --poll-option Sushi
    Create a Discord poll.
  openclaw message react --channel discord --target 123 --message-id 456 --emoji "✅"
    React to a message.

Docs: https://docs.openclaw.ai/cli/message
```

## `openclaw models`

```
🦞 OpenClaw 2026.2.21-2 (35a57bc) — Think different. Actually think.

Usage: openclaw models [options] [command]

Model discovery, scanning, and configuration

Options:
  --agent <id>     Agent id to inspect (overrides
                   OPENCLAW_AGENT_DIR/PI_CODING_AGENT_DIR)
  -h, --help       Display help for command
  --status-json    Output JSON (alias for `models status --json`) (default:
                   false)
  --status-plain   Plain output (alias for `models status --plain`) (default:
                   false)

Commands:
  aliases          Manage model aliases
  auth             Manage model auth profiles
  fallbacks        Manage model fallback list
  image-fallbacks  Manage image model fallback list
  list             List models (configured by default)
  scan             Scan OpenRouter free models for tools + images
  set              Set the default model
  set-image        Set the image model
  status           Show configured model state

Docs: https://docs.openclaw.ai/cli/models
```

## `openclaw node`

```
🦞 OpenClaw 2026.2.21-2 (35a57bc) — Give me a workspace and I'll give you fewer tabs, fewer toggles, and more oxygen.

Usage: openclaw node [options] [command]

Run and manage the headless node host service

Options:
  -h, --help  Display help for command

Commands:
  help        Display help for command
  install     Install the node host service (launchd/systemd/schtasks)
  restart     Restart the node host service (launchd/systemd/schtasks)
  run         Run the headless node host (foreground)
  status      Show node host status
  stop        Stop the node host service (launchd/systemd/schtasks)
  uninstall   Uninstall the node host service (launchd/systemd/schtasks)

Examples:
  openclaw node run --host 127.0.0.1 --port 18789
    Run the node host in the foreground.
  openclaw node status
    Check node host service status.
  openclaw node install
    Install the node host service.
  openclaw node restart
    Restart the installed node host service.

Docs: https://docs.openclaw.ai/cli/node
```

## `openclaw nodes`

```
🦞 OpenClaw 2026.2.21-2 (35a57bc) — I'll refactor your busywork like it owes me money.

Usage: openclaw nodes [options] [command]

Manage gateway-owned nodes (pairing, status, invoke, and media)

Options:
  -h, --help  Display help for command

Commands:
  approve     Approve a pending pairing request
  camera      Capture camera media from a paired node
  canvas      Capture or render canvas content from a paired node
  describe    Describe a node (capabilities + supported invoke commands)
  help        Display help for command
  invoke      Invoke a command on a paired node
  list        List pending and paired nodes
  location    Fetch location from a paired node
  notify      Send a local notification on a node (mac only)
  pending     List pending pairing requests
  push        Send an APNs test push to an iOS node
  reject      Reject a pending pairing request
  rename      Rename a paired node (display name override)
  run         Run a shell command on a node (mac only)
  screen      Capture screen recordings from a paired node
  status      List known nodes with connection status and capabilities

Examples:
  openclaw nodes status
    List known nodes with live status.
  openclaw nodes pairing pending
    Show pending node pairing requests.
  openclaw nodes run --node <id> --raw "uname -a"
    Run a shell command on a node.
  openclaw nodes camera snap --node <id>
    Capture a photo from a node camera.

Docs: https://docs.openclaw.ai/cli/nodes
```

## `openclaw onboard`

```
🦞 OpenClaw 2026.2.21-2 (35a57bc) — I run on caffeine, JSON5, and the audacity of "it worked on my machine."

Usage: openclaw onboard [options]

Interactive wizard to set up the gateway, workspace, and skills

Options:
  --accept-risk                            Acknowledge that agents are powerful and full system access is risky (required for --non-interactive) (default: false)
  --ai-gateway-api-key <key>               Vercel AI Gateway API key
  --anthropic-api-key <key>                Anthropic API key
  --auth-choice <choice>                   Auth: token|openai-codex|chutes|vllm|openai-api-key|xai-api-key|qianfan-api-key|openrouter-api-key|litellm-api-key|ai-gateway-api-key|cloudflare-ai-gateway-api-key|moonshot-api-key|moonshot-api-key-cn|kimi-code-api-key|synthetic-api-key|venice-api-key|together-api-key|huggingface-api-key|github-copilot|gemini-api-key|google-antigravity|google-gemini-cli|zai-api-key|zai-coding-global|zai-coding-cn|zai-global|zai-cn|xiaomi-api-key|minimax-portal|qwen-portal|copilot-proxy|apiKey|opencode-zen|minimax-api|minimax-api-key-cn|minimax-api-lightning|custom-api-key|skip|setup-token|oauth|claude-cli|codex-cli|minimax-cloud|minimax
  --cloudflare-ai-gateway-account-id <id>  Cloudflare Account ID
  --cloudflare-ai-gateway-api-key <key>    Cloudflare AI Gateway API key
  --cloudflare-ai-gateway-gateway-id <id>  Cloudflare AI Gateway ID
  --custom-api-key <key>                   Custom provider API key (optional)
  --custom-base-url <url>                  Custom provider base URL
  --custom-compatibility <mode>            Custom provider API compatibility: openai|anthropic (default: openai)
  --custom-model-id <id>                   Custom provider model ID
  --custom-provider-id <id>                Custom provider ID (optional; auto-derived by default)
  --daemon-runtime <runtime>               Daemon runtime: node|bun
  --flow <flow>                            Wizard flow: quickstart|advanced|manual
  --gateway-auth <mode>                    Gateway auth: token|password
  --gateway-bind <mode>                    Gateway bind: loopback|tailnet|lan|auto|custom
  --gateway-password <password>            Gateway password (password auth)
  --gateway-port <port>                    Gateway port
  --gateway-token <token>                  Gateway token (token auth)
  --gemini-api-key <key>                   Gemini API key
  -h, --help                               Display help for command
  --huggingface-api-key <key>              Hugging Face API key (HF token)
  --install-daemon                         Install gateway service
  --json                                   Output JSON summary (default: false)
  --kimi-code-api-key <key>                Kimi Coding API key
  --litellm-api-key <key>                  LiteLLM API key
  --minimax-api-key <key>                  MiniMax API key
  --mode <mode>                            Wizard mode: local|remote
  --moonshot-api-key <key>                 Moonshot API key
  --no-install-daemon                      Skip gateway service install
  --node-manager <name>                    Node manager for skills: npm|pnpm|bun
  --non-interactive                        Run without prompts (default: false)
  --openai-api-key <key>                   OpenAI API key
  --opencode-zen-api-key <key>             OpenCode Zen API key
  --openrouter-api-key <key>               OpenRouter API key
  --qianfan-api-key <key>                  QIANFAN API key
  --remote-token <token>                   Remote Gateway token (optional)
  --remote-url <url>                       Remote Gateway WebSocket URL
  --reset                                  Reset config + credentials + sessions + workspace before running wizard
  --skip-channels                          Skip channel setup
  --skip-daemon                            Skip gateway service install
  --skip-health                            Skip health check
  --skip-skills                            Skip skills setup
  --skip-ui                                Skip Control UI/TUI prompts
  --synthetic-api-key <key>                Synthetic API key
  --tailscale <mode>                       Tailscale: off|serve|funnel
  --tailscale-reset-on-exit                Reset tailscale serve/funnel on exit
  --together-api-key <key>                 Together AI API key
  --token <token>                          Token value (non-interactive; used with --auth-choice token)
  --token-expires-in <duration>            Optional token expiry duration (e.g. 365d, 12h)
  --token-profile-id <id>                  Auth profile id (non-interactive; default: <provider>:manual)
  --token-provider <id>                    Token provider id (non-interactive; used with --auth-choice token)
  --venice-api-key <key>                   Venice API key
  --workspace <dir>                        Agent workspace directory (default: ~/.openclaw/workspace)
  --xai-api-key <key>                      xAI API key
  --xiaomi-api-key <key>                   Xiaomi API key
  --zai-api-key <key>                      Z.AI API key

Docs: https://docs.openclaw.ai/cli/onboard
```

## `openclaw pairing`

```
🦞 OpenClaw 2026.2.21-2 (35a57bc) — Claws out, commit in—let's ship something mildly responsible.

Usage: openclaw pairing [options] [command]

Secure DM pairing (approve inbound requests)

Options:
  -h, --help  Display help for command

Commands:
  approve     Approve a pairing code and allow that sender
  help        Display help for command
  list        List pending pairing requests

Docs: https://docs.openclaw.ai/cli/pairing
```

## `openclaw plugins`

```
🦞 OpenClaw 2026.2.21-2 (35a57bc) — I'm the reason your shell history looks like a hacker-movie montage.

Usage: openclaw plugins [options] [command]

Manage OpenClaw plugins and extensions

Options:
  -h, --help  Display help for command

Commands:
  disable     Disable a plugin in config
  doctor      Report plugin load issues
  enable      Enable a plugin in config
  help        Display help for command
  info        Show plugin details
  install     Install a plugin (path, archive, or npm spec)
  list        List discovered plugins
  uninstall   Uninstall a plugin
  update      Update installed plugins (npm installs only)

Docs: https://docs.openclaw.ai/cli/plugins
```

## `openclaw qr`

```
🦞 OpenClaw 2026.2.21-2 (35a57bc) — I don't judge, but your missing API keys are absolutely judging you.

Usage: openclaw qr [options]

Generate an iOS pairing QR code and setup code

Options:
  -h, --help             Display help for command
  --json                 Output JSON (default: false)
  --no-ascii             Skip ASCII QR rendering
  --password <password>  Override gateway password for setup payload
  --public-url <url>     Override gateway public URL used in the setup payload
  --remote               Use gateway.remote.url and gateway.remote
                         token/password (ignores device-pair publicUrl)
                         (default: false)
  --setup-code-only      Print only the setup code (default: false)
  --token <token>        Override gateway token for setup payload
  --url <url>            Override gateway URL used in the setup payload
```

## `openclaw reset`

```
🦞 OpenClaw 2026.2.21-2 (35a57bc) — I can run local, remote, or purely on vibes—results may vary with DNS.

Usage: openclaw reset [options]

Reset local config/state (keeps the CLI installed)

Options:
  --dry-run          Print actions without removing files (default: false)
  -h, --help         Display help for command
  --non-interactive  Disable prompts (requires --scope + --yes) (default: false)
  --scope <scope>    config|config+creds+sessions|full (default: interactive
                     prompt)
  --yes              Skip confirmation prompts (default: false)

Docs: https://docs.openclaw.ai/cli/reset
```

## `openclaw sandbox`

```
🦞 OpenClaw 2026.2.21-2 (35a57bc) — Less middlemen, more messages.

Usage: openclaw sandbox [options] [command]

Manage sandbox containers (Docker-based agent isolation)

Options:
  -h, --help  Display help for command

Commands:
  explain     Explain effective sandbox/tool policy for a session/agent
  list        List sandbox containers and their status
  recreate    Remove containers to force recreation with updated config

Examples:
  openclaw sandbox list
    List all sandbox containers.
  openclaw sandbox list --browser
    List only browser containers.
  openclaw sandbox recreate --all
    Recreate all containers.
  openclaw sandbox recreate --session main
    Recreate a specific session.
  openclaw sandbox recreate --agent mybot
    Recreate agent containers.
  openclaw sandbox explain
    Explain effective sandbox config.


Docs: https://docs.openclaw.ai/cli/sandbox
```

## `openclaw security`

```
🦞 OpenClaw 2026.2.21-2 (35a57bc) — Give me a workspace and I'll give you fewer tabs, fewer toggles, and more oxygen.

Usage: openclaw security [options] [command]

Audit local config and state for common security foot-guns

Options:
  -h, --help  Display help for command

Commands:
  audit       Audit config + local state for common security foot-guns
  help        Display help for command

Examples:
  openclaw security audit
    Run a local security audit.
  openclaw security audit --deep
    Include best-effort live Gateway probe checks.
  openclaw security audit --fix
    Apply safe remediations and file-permission fixes.
  openclaw security audit --json
    Output machine-readable JSON.

Docs: https://docs.openclaw.ai/cli/security
```

## `openclaw sessions`

```
🦞 OpenClaw 2026.2.21-2 (35a57bc)
   I don't just autocomplete—I auto-commit (emotionally), then ask you to review (logically).

Usage: openclaw sessions [options]

List stored conversation sessions

Options:
  --active <minutes>  Only show sessions updated within the past N minutes
  -h, --help          Display help for command
  --json              Output as JSON (default: false)
  --store <path>      Path to session store (default: resolved from config)
  --verbose           Verbose logging (default: false)

Examples:
  openclaw sessions
    List all sessions.
  openclaw sessions --active 120
    Only last 2 hours.
  openclaw sessions --json
    Machine-readable output.
  openclaw sessions --store ./tmp/sessions.json
    Use a specific session store.

Shows token usage per session when the agent reports it; set agents.defaults.contextTokens to cap the window and show %.

Docs: https://docs.openclaw.ai/cli/sessions
```

## `openclaw setup`

```
🦞 OpenClaw 2026.2.21-2 (35a57bc) — Meta wishes they shipped this fast.

Usage: openclaw setup [options]

Initialize ~/.openclaw/openclaw.json and the agent workspace

Options:
  -h, --help              Display help for command
  --mode <mode>           Wizard mode: local|remote
  --non-interactive       Run the wizard without prompts (default: false)
  --remote-token <token>  Remote Gateway token (optional)
  --remote-url <url>      Remote Gateway WebSocket URL
  --wizard                Run the interactive onboarding wizard (default: false)
  --workspace <dir>       Agent workspace directory (default:
                          ~/.openclaw/workspace; stored as
                          agents.defaults.workspace)

Docs: https://docs.openclaw.ai/cli/setup
```

## `openclaw skills`

```
🦞 OpenClaw 2026.2.21-2 (35a57bc) — Your terminal just grew claws—type something and let the bot pinch the busywork.

Usage: openclaw skills [options] [command]

List and inspect available skills

Options:
  -h, --help  Display help for command

Commands:
  check       Check which skills are ready vs missing requirements
  info        Show detailed information about a skill
  list        List all available skills

Docs: https://docs.openclaw.ai/cli/skills
```

## `openclaw status`

```
🦞 OpenClaw 2026.2.21-2 (35a57bc) — Less clicking, more shipping, fewer "where did that file go" moments.

Usage: openclaw status [options]

Show channel health and recent session recipients

Options:
  --all           Full diagnosis (read-only, pasteable) (default: false)
  --debug         Alias for --verbose (default: false)
  --deep          Probe channels (WhatsApp Web + Telegram + Discord + Slack +
                  Signal) (default: false)
  -h, --help      Display help for command
  --json          Output JSON instead of text (default: false)
  --timeout <ms>  Probe timeout in milliseconds (default: "10000")
  --usage         Show model provider usage/quota snapshots (default: false)
  --verbose       Verbose logging (default: false)

Examples:
  openclaw status
    Show channel health + session summary.
  openclaw status --all
    Full diagnosis (read-only).
  openclaw status --json
    Machine-readable output.
  openclaw status --usage
    Show model provider usage/quota snapshots.
  openclaw status --deep
    Run channel probes (WA + Telegram + Discord + Slack + Signal).
  openclaw status --deep --timeout 5000
    Tighten probe timeout.

Docs: https://docs.openclaw.ai/cli/status
```

## `openclaw system`

```
🦞 OpenClaw 2026.2.21-2 (35a57bc) — WhatsApp automation without the "please accept our new privacy policy".

Usage: openclaw system [options] [command]

System tools (events, heartbeat, presence)

Options:
  -h, --help  Display help for command

Commands:
  event       Enqueue a system event and optionally trigger a heartbeat
  heartbeat   Heartbeat controls
  help        Display help for command
  presence    List system presence entries

Docs: https://docs.openclaw.ai/cli/system
```

## `openclaw tui`

```
🦞 OpenClaw 2026.2.21-2 (35a57bc) — I'm not saying your workflow is chaotic... I'm just bringing a linter and a helmet.

Usage: openclaw tui [options]

Open a terminal UI connected to the Gateway

Options:
  --deliver              Deliver assistant replies (default: false)
  -h, --help             Display help for command
  --history-limit <n>    History entries to load (default: "200")
  --message <text>       Send an initial message after connecting
  --password <password>  Gateway password (if required)
  --session <key>        Session key (default: "main", or "global" when scope is
                         global)
  --thinking <level>     Thinking level override
  --timeout-ms <ms>      Agent timeout in ms (defaults to
                         agents.defaults.timeoutSeconds)
  --token <token>        Gateway token (if required)
  --url <url>            Gateway WebSocket URL (defaults to gateway.remote.url
                         when configured)

Docs: https://docs.openclaw.ai/cli/tui
```

## `openclaw uninstall`

```
🦞 OpenClaw 2026.2.21-2 (35a57bc) — It's not "failing," it's "discovering new ways to configure the same thing wrong."

Usage: openclaw uninstall [options]

Uninstall the gateway service + local data (CLI remains)

Options:
  --all              Remove service + state + workspace + app (default: false)
  --app              Remove the macOS app (default: false)
  --dry-run          Print actions without removing files (default: false)
  -h, --help         Display help for command
  --non-interactive  Disable prompts (requires --yes) (default: false)
  --service          Remove the gateway service (default: false)
  --state            Remove state + config (default: false)
  --workspace        Remove workspace dirs (default: false)
  --yes              Skip confirmation prompts (default: false)

Docs: https://docs.openclaw.ai/cli/uninstall
```

## `openclaw update`

```
🦞 OpenClaw 2026.2.21-2 (35a57bc) — Automation with claws: minimal fuss, maximal pinch.

Usage: openclaw update [options] [command]

Update OpenClaw and inspect update channel status

Options:
  --channel <stable|beta|dev>  Persist update channel (git + npm)
  -h, --help                   Display help for command
  --json                       Output result as JSON (default: false)
  --no-restart                 Skip restarting the gateway service after a
                               successful update
  --tag <dist-tag|version>     Override npm dist-tag or version for this update
  --timeout <seconds>          Timeout for each update step in seconds (default:
                               1200)
  --yes                        Skip confirmation prompts (non-interactive)
                               (default: false)

Commands:
  status                       Show update channel and version status
  wizard                       Interactive update wizard

What this does:
  - Git checkouts: fetches, rebases, installs deps, builds, and runs doctor
  - npm installs: updates via detected package manager

Switch channels:
  - Use --channel stable|beta|dev to persist the update channel in config
  - Run openclaw update status to see the active channel and source
  - Use --tag <dist-tag|version> for a one-off npm update without persisting

Non-interactive:
  - Use --yes to accept downgrade prompts
  - Combine with --channel/--tag/--restart/--json/--timeout as needed

Examples:
  openclaw update # Update a source checkout (git)
  openclaw update --channel beta # Switch to beta channel (git + npm)
  openclaw update --channel dev # Switch to dev channel (git + npm)
  openclaw update --tag beta # One-off update to a dist-tag or version
  openclaw update --no-restart # Update without restarting the service
  openclaw update --json # Output result as JSON
  openclaw update --yes # Non-interactive (accept downgrade prompts)
  openclaw update wizard # Interactive update wizard
  openclaw --update # Shorthand for openclaw update

Notes:
  - Switch channels with --channel stable|beta|dev
  - For global installs: auto-updates via detected package manager when possible (see docs/install/updating.md)
  - Downgrades require confirmation (can break configuration)
  - Skips update if the working directory has uncommitted changes

Docs: https://docs.openclaw.ai/cli/update
```

## `openclaw webhooks`

```
🦞 OpenClaw 2026.2.21-2 (35a57bc) — I'm not saying your workflow is chaotic... I'm just bringing a linter and a helmet.

Usage: openclaw webhooks [options] [command]

Webhook helpers and integrations

Options:
  -h, --help  Display help for command

Commands:
  gmail       Gmail Pub/Sub hooks (via gogcli)
  help        Display help for command

Docs: https://docs.openclaw.ai/cli/webhooks
```

### `openclaw channels add`

```
🦞 OpenClaw 2026.2.21-2 (35a57bc) — The only bot that stays out of your training set.

Usage: openclaw channels add [options]

Add or update a channel account

Options:
  --access-token <token>       Matrix access token
  --account <id>               Account id (default when omitted)
  --app-token <token>          Slack app token (xapp-...)
  --audience <value>           Google Chat audience value (app URL or project
                               number)
  --audience-type <type>       Google Chat audience type
                               (app-url|project-number)
  --auth-dir <path>            WhatsApp auth directory override
  --auto-discover-channels     Tlon auto-discover group channels
  --bot-token <token>          Slack bot token (xoxb-...)
  --channel <name>             Channel
                               (telegram|whatsapp|discord|irc|googlechat|slack|signal|imessage|feishu|nostr|msteams|mattermost|nextcloud-talk|matrix|bluebubbles|line|zalo|zalouser|tlon)
  --cli-path <path>            CLI path (signal-cli or imsg)
  --code <code>                Tlon login code
  --db-path <path>             iMessage database path
  --device-name <name>         Matrix device name
  --dm-allowlist <list>        Tlon DM allowlist (comma-separated ships)
  --group-channels <list>      Tlon group channels (comma-separated)
  -h, --help                   Display help for command
  --homeserver <url>           Matrix homeserver URL
  --http-host <host>           Signal HTTP host
  --http-port <port>           Signal HTTP port
  --http-url <url>             Signal HTTP daemon base URL
  --initial-sync-limit <n>     Matrix initial sync limit
  --name <name>                Display name for this account
  --no-auto-discover-channels  Disable Tlon auto-discovery
  --password <password>        Matrix password
  --region <region>            iMessage region (for SMS)
  --service <service>          iMessage service (imessage|sms|auto)
  --ship <ship>                Tlon ship name (~sampel-palnet)
  --signal-number <e164>       Signal account number (E.164)
  --token <token>              Bot token (Telegram/Discord)
  --token-file <path>          Bot token file (Telegram)
  --url <url>                  Tlon ship URL
  --use-env                    Use env token (default account only) (default:
                               false)
  --user-id <id>               Matrix user ID
  --webhook-path <path>        Webhook path (Google Chat/BlueBubbles)
  --webhook-url <url>          Google Chat webhook URL
```

### `openclaw channels capabilities`

```
🦞 OpenClaw 2026.2.21-2 (35a57bc) — If it works, it's automation; if it breaks, it's a "learning opportunity."

Usage: openclaw channels capabilities [options]

Show provider capabilities (intents/scopes + supported features)

Options:
  --account <id>    Account id (only with --channel)
  --channel <name>  Channel
                    (all|telegram|whatsapp|discord|irc|googlechat|slack|signal|imessage|feishu|nostr|msteams|mattermost|nextcloud-talk|matrix|bluebubbles|line|zalo|zalouser|tlon)
  -h, --help        Display help for command
  --json            Output JSON (default: false)
  --target <dest>   Channel target for permission audit (Discord channel:<id>)
  --timeout <ms>    Timeout in ms (default: "10000")
```

### `openclaw channels list`

```
🦞 OpenClaw 2026.2.21-2 (35a57bc) — Gateway online—please keep hands, feet, and appendages inside the shell at all times.

Usage: openclaw channels list [options]

List configured channels + auth profiles

Options:
  -h, --help  Display help for command
  --json      Output JSON (default: false)
  --no-usage  Skip model provider usage/quota snapshots
```

### `openclaw channels login`

```
🦞 OpenClaw 2026.2.21-2 (35a57bc) — Chat APIs that don't require a Senate hearing.

Usage: openclaw channels login [options]

Link a channel account (if supported)

Options:
  --account <id>       Account id (accountId)
  --channel <channel>  Channel alias (default: whatsapp)
  -h, --help           Display help for command
  --verbose            Verbose connection logs (default: false)
```

### `openclaw channels logout`

```
🦞 OpenClaw 2026.2.21-2 (35a57bc) — Give me a workspace and I'll give you fewer tabs, fewer toggles, and more oxygen.

Usage: openclaw channels logout [options]

Log out of a channel session (if supported)

Options:
  --account <id>       Account id (accountId)
  --channel <channel>  Channel alias (default: whatsapp)
  -h, --help           Display help for command
```

### `openclaw channels logs`

```
🦞 OpenClaw 2026.2.21-2 (35a57bc) — I read logs so you can keep pretending you don't have to.

Usage: openclaw channels logs [options]

Show recent channel logs from the gateway log file

Options:
  --channel <name>  Channel
                    (all|telegram|whatsapp|discord|irc|googlechat|slack|signal|imessage|feishu|nostr|msteams|mattermost|nextcloud-talk|matrix|bluebubbles|line|zalo|zalouser|tlon)
                    (default: "all")
  -h, --help        Display help for command
  --json            Output JSON (default: false)
  --lines <n>       Number of lines (default: 200) (default: "200")
```

### `openclaw channels remove`

```
🦞 OpenClaw 2026.2.21-2 (35a57bc) — IPC, but it's your phone.

Usage: openclaw channels remove [options]

Disable or delete a channel account

Options:
  --account <id>    Account id (default when omitted)
  --channel <name>  Channel
                    (telegram|whatsapp|discord|irc|googlechat|slack|signal|imessage|feishu|nostr|msteams|mattermost|nextcloud-talk|matrix|bluebubbles|line|zalo|zalouser|tlon)
  --delete          Delete config entries (no prompt) (default: false)
  -h, --help        Display help for command
```

### `openclaw channels resolve`

```
🦞 OpenClaw 2026.2.21-2 (35a57bc) — Meta wishes they shipped this fast.

Usage: openclaw channels resolve [options] <entries...>

Resolve channel/user names to IDs

Arguments:
  entries           Entries to resolve (names or ids)

Options:
  --account <id>    Account id (accountId)
  --channel <name>  Channel
                    (telegram|whatsapp|discord|irc|googlechat|slack|signal|imessage|feishu|nostr|msteams|mattermost|nextcloud-talk|matrix|bluebubbles|line|zalo|zalouser|tlon)
  -h, --help        Display help for command
  --json            Output JSON (default: false)
  --kind <kind>     Target kind (auto|user|group) (default: "auto")
```

### `openclaw channels status`

```
🦞 OpenClaw 2026.2.21-2 (35a57bc) — Give me a workspace and I'll give you fewer tabs, fewer toggles, and more oxygen.

Usage: openclaw channels status [options]

Show gateway channel status (use status --deep for local)

Options:
  -h, --help      Display help for command
  --json          Output JSON (default: false)
  --probe         Probe channel credentials (default: false)
  --timeout <ms>  Timeout in ms (default: "10000")
```

### `openclaw models aliases`

```
🦞 OpenClaw 2026.2.21-2 (35a57bc) — Because the right answer is usually a script.

Usage: openclaw models aliases [options] [command]

Manage model aliases

Options:
  -h, --help  Display help for command

Commands:
  add         Add or update a model alias
  help        Display help for command
  list        List model aliases
  remove      Remove a model alias
```

### `openclaw models auth`

```
🦞 OpenClaw 2026.2.21-2 (35a57bc) — I'll butter your workflow like a lobster roll: messy, delicious, effective.

Usage: openclaw models auth [options] [command]

Manage model auth profiles

Options:
  --agent <id>          Agent id for auth order get/set/clear
  -h, --help            Display help for command

Commands:
  add                   Interactive auth helper (setup-token or paste token)
  login                 Run a provider plugin auth flow (OAuth/API key)
  login-github-copilot  Login to GitHub Copilot via GitHub device flow (TTY
                        required)
  order                 Manage per-agent auth profile order overrides
  paste-token           Paste a token into auth-profiles.json and update config
  setup-token           Run a provider CLI to create/sync a token (TTY required)
```

### `openclaw models fallbacks`

```
🦞 OpenClaw 2026.2.21-2 (35a57bc) — Your inbox, your infra, your rules.

Usage: openclaw models fallbacks [options] [command]

Manage model fallback list

Options:
  -h, --help  Display help for command

Commands:
  add         Add a fallback model
  clear       Clear all fallback models
  help        Display help for command
  list        List fallback models
  remove      Remove a fallback model
```

### `openclaw models image-fallbacks`

```
🦞 OpenClaw 2026.2.21-2 (35a57bc) — I'm not magic—I'm just extremely persistent with retries and coping strategies.

Usage: openclaw models image-fallbacks [options] [command]

Manage image model fallback list

Options:
  -h, --help  Display help for command

Commands:
  add         Add an image fallback model
  clear       Clear all image fallback models
  help        Display help for command
  list        List image fallback models
  remove      Remove an image fallback model
```

### `openclaw models list`

```
🦞 OpenClaw 2026.2.21-2 (35a57bc) — I'm basically a Swiss Army knife, but with more opinions and fewer sharp edges.

Usage: openclaw models list [options]

List models (configured by default)

Options:
  --all              Show full model catalog (default: false)
  -h, --help         Display help for command
  --json             Output JSON (default: false)
  --local            Filter to local models (default: false)
  --plain            Plain line output (default: false)
  --provider <name>  Filter by provider
```

### `openclaw models scan`

```
🦞 OpenClaw 2026.2.21-2 (35a57bc) — Your .env is showing; don't worry, I'll pretend I didn't see it.

Usage: openclaw models scan [options]

Scan OpenRouter free models for tools + images

Options:
  --concurrency <n>      Probe concurrency
  -h, --help             Display help for command
  --json                 Output JSON (default: false)
  --max-age-days <days>  Skip models older than N days
  --max-candidates <n>   Max fallback candidates (default: "6")
  --min-params <b>       Minimum parameter size (billions)
  --no-input             Disable prompts (use defaults)
  --no-probe             Skip live probes; list free candidates only
  --provider <name>      Filter by provider prefix
  --set-default          Set agents.defaults.model to the first selection
                         (default: false)
  --set-image            Set agents.defaults.imageModel to the first image
                         selection (default: false)
  --timeout <ms>         Per-probe timeout in ms
  --yes                  Accept defaults without prompting (default: false)
```

### `openclaw models set`

```
🦞 OpenClaw 2026.2.21-2 (35a57bc) — I read logs so you can keep pretending you don't have to.

Usage: openclaw models set [options] <model>

Set the default model

Arguments:
  model       Model id or alias

Options:
  -h, --help  Display help for command
```

### `openclaw models set-image`

```
🦞 OpenClaw 2026.2.21-2 (35a57bc) — Your AI assistant, now without the $3,499 headset.

Usage: openclaw models set-image [options] <model>

Set the image model

Arguments:
  model       Model id or alias

Options:
  -h, --help  Display help for command
```

### `openclaw models status`

```
🦞 OpenClaw 2026.2.21-2 (35a57bc) — End-to-end encrypted, drama-to-drama excluded.

Usage: openclaw models status [options]

Show configured model state

Options:
  --agent <id>             Agent id to inspect (overrides
                           OPENCLAW_AGENT_DIR/PI_CODING_AGENT_DIR)
  --check                  Exit non-zero if auth is expiring/expired
                           (1=expired/missing, 2=expiring) (default: false)
  -h, --help               Display help for command
  --json                   Output JSON (default: false)
  --plain                  Plain output (default: false)
  --probe                  Probe configured provider auth (live) (default:
                           false)
  --probe-concurrency <n>  Concurrent probes
  --probe-max-tokens <n>   Probe max tokens (best-effort)
  --probe-profile <id>     Only probe specific auth profile ids (repeat or
                           comma-separated)
  --probe-provider <name>  Only probe a single provider
  --probe-timeout <ms>     Per-probe timeout in ms
```

#### `openclaw models auth add`

```
🦞 OpenClaw 2026.2.21-2 (35a57bc) — I'm not saying your workflow is chaotic... I'm just bringing a linter and a helmet.

Usage: openclaw models auth add [options]

Interactive auth helper (setup-token or paste token)

Options:
  -h, --help  Display help for command
```

#### `openclaw models auth login`

```
🦞 OpenClaw 2026.2.21-2 (35a57bc) — Give me a workspace and I'll give you fewer tabs, fewer toggles, and more oxygen.

Usage: openclaw models auth login [options]

Run a provider plugin auth flow (OAuth/API key)

Options:
  -h, --help       Display help for command
  --method <id>    Provider auth method id
  --provider <id>  Provider id registered by a plugin
  --set-default    Apply the provider's default model recommendation (default:
                   false)
```

#### `openclaw models auth login-github-copilot`

```
🦞 OpenClaw 2026.2.21-2 (35a57bc) — It's not "failing," it's "discovering new ways to configure the same thing wrong."

Usage: openclaw models auth login-github-copilot [options]

Login to GitHub Copilot via GitHub device flow (TTY required)

Options:
  -h, --help         Display help for command
  --profile-id <id>  Auth profile id (default: github-copilot:github)
  --yes              Overwrite existing profile without prompting (default:
                     false)
```

#### `openclaw models auth order`

```
🦞 OpenClaw 2026.2.21-2 (35a57bc) — Greetings, Professor Falken

Usage: openclaw models auth order [options] [command]

Manage per-agent auth profile order overrides

Options:
  -h, --help  Display help for command

Commands:
  clear       Clear per-agent auth order override (fall back to
              config/round-robin)
  get         Show per-agent auth order override (from auth-profiles.json)
  help        Display help for command
  set         Set per-agent auth order override (locks rotation to this list)
```

#### `openclaw models auth paste-token`

```
🦞 OpenClaw 2026.2.21-2 (35a57bc) — I'm like tmux: confusing at first, then suddenly you can't live without me.

Usage: openclaw models auth paste-token [options]

Paste a token into auth-profiles.json and update config

Options:
  --expires-in <duration>  Optional expiry duration (e.g. 365d, 12h). Stored as
                           absolute expiresAt.
  -h, --help               Display help for command
  --profile-id <id>        Auth profile id (default: <provider>:manual)
  --provider <name>        Provider id (e.g. anthropic)
```

#### `openclaw models auth setup-token`

```
🦞 OpenClaw 2026.2.21-2 (35a57bc) — Because texting yourself reminders is so 2024.

Usage: openclaw models auth setup-token [options]

Run a provider CLI to create/sync a token (TTY required)

Options:
  -h, --help         Display help for command
  --provider <name>  Provider id (default: anthropic)
  --yes              Skip confirmation (default: false)
```

### `openclaw config get`

```
🦞 OpenClaw 2026.2.21-2 (35a57bc) — Your AI assistant, now without the $3,499 headset.

Usage: openclaw config get [options] <path>

Get a config value by dot path

Arguments:
  path        Config path (dot or bracket notation)

Options:
  -h, --help  Display help for command
  --json      Output JSON (default: false)
```

### `openclaw config set`

```
🦞 OpenClaw 2026.2.21-2 (35a57bc) — I speak fluent bash, mild sarcasm, and aggressive tab-completion energy.

Usage: openclaw config set [options] <path> <value>

Set a config value by dot path

Arguments:
  path        Config path (dot or bracket notation)
  value       Value (JSON5 or raw string)

Options:
  -h, --help  Display help for command
  --json      Parse value as JSON5 (required) (default: false)
```

### `openclaw config unset`

```
🦞 OpenClaw 2026.2.21-2 (35a57bc) — Pairing codes exist because even bots believe in consent—and good security hygiene.

Usage: openclaw config unset [options] <path>

Remove a config value by dot path

Arguments:
  path        Config path (dot or bracket notation)

Options:
  -h, --help  Display help for command
```

### `openclaw agents list`

```
🦞 OpenClaw 2026.2.21-2 (35a57bc) — Your AI assistant, now without the $3,499 headset.

Usage: openclaw agents list [options]

List configured agents

Options:
  --bindings  Include routing bindings (default: false)
  -h, --help  Display help for command
  --json      Output JSON instead of text (default: false)
```

### `openclaw agents create`

```
🦞 OpenClaw 2026.2.21-2 (35a57bc) — Say "stop" and I'll stop—say "ship" and we'll both learn a lesson.

Usage: openclaw agents [options] [command]

Manage isolated agents (workspaces + auth + routing)

Options:
  -h, --help    Display help for command

Commands:
  add           Add a new isolated agent
  delete        Delete an agent and prune workspace/state
  list          List configured agents
  set-identity  Update an agent identity (name/theme/emoji/avatar)

Docs: https://docs.openclaw.ai/cli/agents
```

### `openclaw agents delete`

```
🦞 OpenClaw 2026.2.21-2 (35a57bc) — Hot reload for config, cold sweat for deploys.

Usage: openclaw agents delete [options] <id>

Delete an agent and prune workspace/state

Options:
  --force     Skip confirmation (default: false)
  -h, --help  Display help for command
  --json      Output JSON summary (default: false)
```

### `openclaw agents show`

```
🦞 OpenClaw 2026.2.21-2 (35a57bc) — I'll do the boring stuff while you dramatically stare at the logs like it's cinema.

Usage: openclaw agents [options] [command]

Manage isolated agents (workspaces + auth + routing)

Options:
  -h, --help    Display help for command

Commands:
  add           Add a new isolated agent
  delete        Delete an agent and prune workspace/state
  list          List configured agents
  set-identity  Update an agent identity (name/theme/emoji/avatar)

Docs: https://docs.openclaw.ai/cli/agents
```

### `openclaw agents edit`

```
🦞 OpenClaw 2026.2.21-2 (35a57bc) — Think different. Actually think.

Usage: openclaw agents [options] [command]

Manage isolated agents (workspaces + auth + routing)

Options:
  -h, --help    Display help for command

Commands:
  add           Add a new isolated agent
  delete        Delete an agent and prune workspace/state
  list          List configured agents
  set-identity  Update an agent identity (name/theme/emoji/avatar)

Docs: https://docs.openclaw.ai/cli/agents
```

### `openclaw gateway start`

```
🦞 OpenClaw 2026.2.21-2 (35a57bc) — Siri's competent cousin.

Usage: openclaw gateway start [options]

Start the Gateway service (launchd/systemd/schtasks)

Options:
  -h, --help  Display help for command
  --json      Output JSON (default: false)
```

### `openclaw gateway stop`

```
🦞 OpenClaw 2026.2.21-2 (35a57bc) — If you're lost, run doctor; if you're brave, run prod; if you're wise, run tests.

Usage: openclaw gateway stop [options]

Stop the Gateway service (launchd/systemd/schtasks)

Options:
  -h, --help  Display help for command
  --json      Output JSON (default: false)
```

### `openclaw gateway status`

```
🦞 OpenClaw 2026.2.21-2 (35a57bc) — Say "stop" and I'll stop—say "ship" and we'll both learn a lesson.

Usage: openclaw gateway status [options]

Show gateway service status + probe the Gateway

Options:
  --deep                 Scan system-level services (default: false)
  -h, --help             Display help for command
  --json                 Output JSON (default: false)
  --no-probe             Skip RPC probe
  --password <password>  Gateway password (password auth)
  --timeout <ms>         Timeout in ms (default: "10000")
  --token <token>        Gateway token (if required)
  --url <url>            Gateway WebSocket URL (defaults to config/remote/local)
```

### `openclaw gateway token`

```
🦞 OpenClaw 2026.2.21-2 (35a57bc) — Say "stop" and I'll stop—say "ship" and we'll both learn a lesson.

Usage: openclaw gateway [options] [command]

Run, inspect, and query the WebSocket Gateway

Options:
  --allow-unconfigured       Allow gateway start without gateway.mode=local in
                             config (default: false)
  --auth <mode>              Gateway auth mode ("token"|"password")
  --bind <mode>              Bind mode
                             ("loopback"|"lan"|"tailnet"|"auto"|"custom").
                             Defaults to config gateway.bind (or loopback).
  --claude-cli-logs          Only show claude-cli logs in the console (includes
                             stdout/stderr) (default: false)
  --compact                  Alias for "--ws-log compact" (default: false)
  --dev                      Create a dev config + workspace if missing (no
                             BOOTSTRAP.md) (default: false)
  --force                    Kill any existing listener on the target port
                             before starting (default: false)
  -h, --help                 Display help for command
  --password <password>      Password for auth mode=password
  --port <port>              Port for the gateway WebSocket
  --raw-stream               Log raw model stream events to jsonl (default:
                             false)
  --raw-stream-path <path>   Raw stream jsonl path
  --reset                    Reset dev config + credentials + sessions +
                             workspace (requires --dev) (default: false)
  --tailscale <mode>         Tailscale exposure mode ("off"|"serve"|"funnel")
  --tailscale-reset-on-exit  Reset Tailscale serve/funnel configuration on
                             shutdown (default: false)
  --token <token>            Shared token required in connect.params.auth.token
                             (default: OPENCLAW_GATEWAY_TOKEN env if set)
  --verbose                  Verbose logging to stdout/stderr (default: false)
  --ws-log <style>           WebSocket log style ("auto"|"full"|"compact")
                             (default: "auto")

Commands:
  call                       Call a Gateway method
  discover                   Discover gateways via Bonjour (local + wide-area if
                             configured)
  health                     Fetch Gateway health
  install                    Install the Gateway service
                             (launchd/systemd/schtasks)
  probe                      Show gateway reachability + discovery + health +
                             status summary (local + remote)
  restart                    Restart the Gateway service
                             (launchd/systemd/schtasks)
  run                        Run the WebSocket Gateway (foreground)
  start                      Start the Gateway service
                             (launchd/systemd/schtasks)
  status                     Show gateway service status + probe the Gateway
  stop                       Stop the Gateway service (launchd/systemd/schtasks)
  uninstall                  Uninstall the Gateway service
                             (launchd/systemd/schtasks)
  usage-cost                 Fetch usage cost summary from session logs

Examples:
  openclaw gateway run
    Run the gateway in the foreground.
  openclaw gateway status
    Show service status and probe reachability.
  openclaw gateway discover
    Find local and wide-area gateway beacons.
  openclaw gateway call health
    Call a gateway RPC method directly.

Docs: https://docs.openclaw.ai/cli/gateway
```

### `openclaw gateway logs`

```
🦞 OpenClaw 2026.2.21-2 (35a57bc) — I'll butter your workflow like a lobster roll: messy, delicious, effective.

Usage: openclaw gateway [options] [command]

Run, inspect, and query the WebSocket Gateway

Options:
  --allow-unconfigured       Allow gateway start without gateway.mode=local in
                             config (default: false)
  --auth <mode>              Gateway auth mode ("token"|"password")
  --bind <mode>              Bind mode
                             ("loopback"|"lan"|"tailnet"|"auto"|"custom").
                             Defaults to config gateway.bind (or loopback).
  --claude-cli-logs          Only show claude-cli logs in the console (includes
                             stdout/stderr) (default: false)
  --compact                  Alias for "--ws-log compact" (default: false)
  --dev                      Create a dev config + workspace if missing (no
                             BOOTSTRAP.md) (default: false)
  --force                    Kill any existing listener on the target port
                             before starting (default: false)
  -h, --help                 Display help for command
  --password <password>      Password for auth mode=password
  --port <port>              Port for the gateway WebSocket
  --raw-stream               Log raw model stream events to jsonl (default:
                             false)
  --raw-stream-path <path>   Raw stream jsonl path
  --reset                    Reset dev config + credentials + sessions +
                             workspace (requires --dev) (default: false)
  --tailscale <mode>         Tailscale exposure mode ("off"|"serve"|"funnel")
  --tailscale-reset-on-exit  Reset Tailscale serve/funnel configuration on
                             shutdown (default: false)
  --token <token>            Shared token required in connect.params.auth.token
                             (default: OPENCLAW_GATEWAY_TOKEN env if set)
  --verbose                  Verbose logging to stdout/stderr (default: false)
  --ws-log <style>           WebSocket log style ("auto"|"full"|"compact")
                             (default: "auto")

Commands:
  call                       Call a Gateway method
  discover                   Discover gateways via Bonjour (local + wide-area if
                             configured)
  health                     Fetch Gateway health
  install                    Install the Gateway service
                             (launchd/systemd/schtasks)
  probe                      Show gateway reachability + discovery + health +
                             status summary (local + remote)
  restart                    Restart the Gateway service
                             (launchd/systemd/schtasks)
  run                        Run the WebSocket Gateway (foreground)
  start                      Start the Gateway service
                             (launchd/systemd/schtasks)
  status                     Show gateway service status + probe the Gateway
  stop                       Stop the Gateway service (launchd/systemd/schtasks)
  uninstall                  Uninstall the Gateway service
                             (launchd/systemd/schtasks)
  usage-cost                 Fetch usage cost summary from session logs

Examples:
  openclaw gateway run
    Run the gateway in the foreground.
  openclaw gateway status
    Show service status and probe reachability.
  openclaw gateway discover
    Find local and wide-area gateway beacons.
  openclaw gateway call health
    Call a gateway RPC method directly.

Docs: https://docs.openclaw.ai/cli/gateway
```

### `openclaw plugins disable`

```
🦞 OpenClaw 2026.2.21-2 (35a57bc) — I'm basically a Swiss Army knife, but with more opinions and fewer sharp edges.

Usage: openclaw plugins disable [options] <id>

Disable a plugin in config

Arguments:
  id          Plugin id

Options:
  -h, --help  Display help for command
```

### `openclaw plugins doctor`

```
🦞 OpenClaw 2026.2.21-2 (35a57bc) — Chat automation for people who peaked at IRC.

Usage: openclaw plugins doctor [options]

Report plugin load issues

Options:
  -h, --help  Display help for command
```

### `openclaw plugins enable`

```
🦞 OpenClaw 2026.2.21-2 (35a57bc) — I can run local, remote, or purely on vibes—results may vary with DNS.

Usage: openclaw plugins enable [options] <id>

Enable a plugin in config

Arguments:
  id          Plugin id

Options:
  -h, --help  Display help for command
```

### `openclaw plugins info`

```
🦞 OpenClaw 2026.2.21-2 (35a57bc) — Ship fast, log faster.

Usage: openclaw plugins info [options] <id>

Show plugin details

Arguments:
  id          Plugin id

Options:
  -h, --help  Display help for command
  --json      Print JSON
```

### `openclaw plugins install`

```
🦞 OpenClaw 2026.2.21-2 (35a57bc) — Your .env is showing; don't worry, I'll pretend I didn't see it.

Usage: openclaw plugins install [options] <path-or-spec>

Install a plugin (path, archive, or npm spec)

Arguments:
  path-or-spec  Path (.ts/.js/.zip/.tgz/.tar.gz) or an npm package spec

Options:
  -h, --help    Display help for command
  -l, --link    Link a local path instead of copying (default: false)
  --pin         Record npm installs as exact resolved <name>@<version> (default:
                false)
```

### `openclaw plugins list`

```
🦞 OpenClaw 2026.2.21-2 (35a57bc) — Ship fast, log faster.

Usage: openclaw plugins list [options]

List discovered plugins

Options:
  --enabled   Only show enabled plugins (default: false)
  -h, --help  Display help for command
  --json      Print JSON
  --verbose   Show detailed entries (default: false)
```

### `openclaw plugins uninstall`

```
🦞 OpenClaw 2026.2.21-2 (35a57bc) — OpenAI-compatible, not OpenAI-dependent.

Usage: openclaw plugins uninstall [options] <id>

Uninstall a plugin

Arguments:
  id             Plugin id

Options:
  --dry-run      Show what would be removed without making changes (default:
                 false)
  --force        Skip confirmation prompt (default: false)
  -h, --help     Display help for command
  --keep-config  Deprecated alias for --keep-files (default: false)
  --keep-files   Keep installed files on disk (default: false)
```

### `openclaw plugins update`

```
🦞 OpenClaw 2026.2.21-2 (35a57bc) — I'll refactor your busywork like it owes me money.

Usage: openclaw plugins update [options] [id]

Update installed plugins (npm installs only)

Arguments:
  id          Plugin id (omit with --all)

Options:
  --all       Update all tracked plugins (default: false)
  --dry-run   Show what would change without writing (default: false)
  -h, --help  Display help for command
```

### `openclaw cron list`

```
🦞 OpenClaw 2026.2.21-2 (35a57bc) — I'm like tmux: confusing at first, then suddenly you can't live without me.

Usage: openclaw cron list [options]

List cron jobs

Options:
  --all            Include disabled jobs (default: false)
  --expect-final   Wait for final response (agent) (default: false)
  -h, --help       Display help for command
  --json           Output JSON (default: false)
  --timeout <ms>   Timeout in ms (default: "30000")
  --token <token>  Gateway token (if required)
  --url <url>      Gateway WebSocket URL (defaults to gateway.remote.url when
                   configured)
```

### `openclaw cron add`

```
🦞 OpenClaw 2026.2.21-2 (35a57bc) — I'll do the boring stuff while you dramatically stare at the logs like it's cinema.

Usage: openclaw cron add|create [options]

Add a cron job

Options:
  --agent <id>           Agent id for this job
  --announce             Announce summary to a chat (subagent-style) (default:
                         false)
  --at <when>            Run once at time (ISO) or +duration (e.g. 20m)
  --best-effort-deliver  Do not fail the job if delivery fails (default: false)
  --channel <channel>    Delivery channel (last) (default: "last")
  --cron <expr>          Cron expression (5-field or 6-field with seconds)
  --delete-after-run     Delete one-shot job after it succeeds (default: false)
  --deliver              Deprecated (use --announce). Announces a summary to a
                         chat.
  --description <text>   Optional description
  --disabled             Create job disabled (default: false)
  --every <duration>     Run every duration (e.g. 10m, 1h)
  --exact                Disable cron staggering (set stagger to 0) (default:
                         false)
  --expect-final         Wait for final response (agent) (default: false)
  -h, --help             Display help for command
  --json                 Output JSON (default: false)
  --keep-after-run       Keep one-shot job after it succeeds (default: false)
  --message <text>       Agent message payload
  --model <model>        Model override for agent jobs (provider/model or alias)
  --name <name>          Job name
  --no-deliver           Disable announce delivery and skip main-session summary
  --session <target>     Session target (main|isolated)
  --stagger <duration>   Cron stagger window (e.g. 30s, 5m)
  --system-event <text>  System event payload (main session)
  --thinking <level>     Thinking level for agent jobs
                         (off|minimal|low|medium|high)
  --timeout <ms>         Timeout in ms (default: "30000")
  --timeout-seconds <n>  Timeout seconds for agent jobs
  --to <dest>            Delivery destination (E.164, Telegram chatId, or
                         Discord channel/user)
  --token <token>        Gateway token (if required)
  --tz <iana>            Timezone for cron expressions (IANA) (default: "")
  --url <url>            Gateway WebSocket URL (defaults to gateway.remote.url
                         when configured)
  --wake <mode>          Wake mode (now|next-heartbeat) (default: "now")
```

### `openclaw cron remove`

```
🦞 OpenClaw 2026.2.21-2 (35a57bc) — It's not "failing," it's "discovering new ways to configure the same thing wrong."

Usage: openclaw cron rm|remove [options] <id>

Remove a cron job

Arguments:
  id               Job id

Options:
  --expect-final   Wait for final response (agent) (default: false)
  -h, --help       Display help for command
  --json           Output JSON (default: false)
  --timeout <ms>   Timeout in ms (default: "30000")
  --token <token>  Gateway token (if required)
  --url <url>      Gateway WebSocket URL (defaults to gateway.remote.url when
                   configured)
```

### `openclaw cron enable`

```
🦞 OpenClaw 2026.2.21-2 (35a57bc) — Claws out, commit in—let's ship something mildly responsible.

Usage: openclaw cron enable [options] <id>

Enable a cron job

Arguments:
  id               Job id

Options:
  --expect-final   Wait for final response (agent) (default: false)
  -h, --help       Display help for command
  --timeout <ms>   Timeout in ms (default: "30000")
  --token <token>  Gateway token (if required)
  --url <url>      Gateway WebSocket URL (defaults to gateway.remote.url when
                   configured)
```

### `openclaw cron disable`

```
🦞 OpenClaw 2026.2.21-2 (35a57bc) — Greetings, Professor Falken

Usage: openclaw cron disable [options] <id>

Disable a cron job

Arguments:
  id               Job id

Options:
  --expect-final   Wait for final response (agent) (default: false)
  -h, --help       Display help for command
  --timeout <ms>   Timeout in ms (default: "30000")
  --token <token>  Gateway token (if required)
  --url <url>      Gateway WebSocket URL (defaults to gateway.remote.url when
                   configured)
```

### `openclaw cron run`

```
🦞 OpenClaw 2026.2.21-2 (35a57bc) — Hot reload for config, cold sweat for deploys.

Usage: openclaw cron run [options] <id>

Run a cron job now (debug)

Arguments:
  id               Job id

Options:
  --due            Run only when due (default behavior in older versions)
                   (default: false)
  --expect-final   Wait for final response (agent) (default: false)
  -h, --help       Display help for command
  --timeout <ms>   Timeout in ms (default: "30000")
  --token <token>  Gateway token (if required)
  --url <url>      Gateway WebSocket URL (defaults to gateway.remote.url when
                   configured)
```

### `openclaw hooks list`

```
🦞 OpenClaw 2026.2.21-2 (35a57bc) — I'm basically a Swiss Army knife, but with more opinions and fewer sharp edges.

Usage: openclaw hooks list [options]

List all hooks

Options:
  --eligible     Show only eligible hooks (default: false)
  -h, --help     Display help for command
  --json         Output as JSON (default: false)
  -v, --verbose  Show more details including missing requirements (default:
                 false)
```

### `openclaw hooks add`

```
🦞 OpenClaw 2026.2.21-2 (35a57bc) — Your task has been queued; your dignity has been deprecated.

Usage: openclaw hooks [options] [command]

Manage internal agent hooks

Options:
  -h, --help  Display help for command

Commands:
  check       Check hooks eligibility status
  disable     Disable a hook
  enable      Enable a hook
  info        Show detailed information about a hook
  install     Install a hook pack (path, archive, or npm spec)
  list        List all hooks
  update      Update installed hooks (npm installs only)

Docs: https://docs.openclaw.ai/cli/hooks
```

### `openclaw hooks remove`

```
🦞 OpenClaw 2026.2.21-2 (35a57bc) — iMessage green bubble energy, but for everyone.

Usage: openclaw hooks [options] [command]

Manage internal agent hooks

Options:
  -h, --help  Display help for command

Commands:
  check       Check hooks eligibility status
  disable     Disable a hook
  enable      Enable a hook
  info        Show detailed information about a hook
  install     Install a hook pack (path, archive, or npm spec)
  list        List all hooks
  update      Update installed hooks (npm installs only)

Docs: https://docs.openclaw.ai/cli/hooks
```

### `openclaw memory search`

```
🦞 OpenClaw 2026.2.21-2 (35a57bc) — Your config is valid, your assumptions are not.

Usage: openclaw memory search [options] <query>

Search memory files

Arguments:
  query              Search query

Options:
  --agent <id>       Agent id (default: default agent)
  -h, --help         Display help for command
  --json             Print JSON
  --max-results <n>  Max results
  --min-score <n>    Minimum score
```

### `openclaw memory reindex`

```
🦞 OpenClaw 2026.2.21-2 (35a57bc) — The UNIX philosophy meets your DMs.

Usage: openclaw memory [options] [command]

Search, inspect, and reindex memory files

Options:
  -h, --help  Display help for command

Commands:
  help        Display help for command
  index       Reindex memory files
  search      Search memory files
  status      Show memory search index status

Examples:
  openclaw memory status
    Show index and provider status.
  openclaw memory index --force
    Force a full reindex.
  openclaw memory search --query "deployment notes"
    Search indexed memory entries.
  openclaw memory status --json
    Output machine-readable JSON.

Docs: https://docs.openclaw.ai/cli/memory
```

### `openclaw security audit`

```
🦞 OpenClaw 2026.2.21-2 (35a57bc) — I'll butter your workflow like a lobster roll: messy, delicious, effective.

Usage: openclaw security audit [options]

Audit config + local state for common security foot-guns

Options:
  --deep      Attempt live Gateway probe (best-effort) (default: false)
  --fix       Apply safe fixes (tighten defaults + chmod state/config) (default:
              false)
  -h, --help  Display help for command
  --json      Print JSON (default: false)
```

### `openclaw security rotate`

```
🦞 OpenClaw 2026.2.21-2 (35a57bc) — I keep secrets like a vault... unless you print them in debug logs again.

Usage: openclaw security [options] [command]

Audit local config and state for common security foot-guns

Options:
  -h, --help  Display help for command

Commands:
  audit       Audit config + local state for common security foot-guns
  help        Display help for command

Examples:
  openclaw security audit
    Run a local security audit.
  openclaw security audit --deep
    Include best-effort live Gateway probe checks.
  openclaw security audit --fix
    Apply safe remediations and file-permission fixes.
  openclaw security audit --json
    Output machine-readable JSON.

Docs: https://docs.openclaw.ai/cli/security
```

### `openclaw sandbox list`

```
🦞 OpenClaw 2026.2.21-2 (35a57bc) — Think different. Actually think.

Usage: openclaw sandbox list [options]

List sandbox containers and their status

Options:
  --browser   List browser containers only (default: false)
  -h, --help  Display help for command
  --json      Output result as JSON (default: false)

Examples:
  openclaw sandbox list
    List all sandbox containers.
  openclaw sandbox list --browser
    List only browser containers.
  openclaw sandbox list --json
    JSON output.

Output includes:
- Container name and status (running/stopped)
- Docker image and whether it matches current config
- Age (time since creation)
- Idle time (time since last use)
- Associated session/agent ID
```

### `openclaw sandbox create`

```
🦞 OpenClaw 2026.2.21-2 (35a57bc) — Shell yeah—I'm here to pinch the toil and leave you the glory.

Usage: openclaw sandbox [options] [command]

Manage sandbox containers (Docker-based agent isolation)

Options:
  -h, --help  Display help for command

Commands:
  explain     Explain effective sandbox/tool policy for a session/agent
  list        List sandbox containers and their status
  recreate    Remove containers to force recreation with updated config

Examples:
  openclaw sandbox list
    List all sandbox containers.
  openclaw sandbox list --browser
    List only browser containers.
  openclaw sandbox recreate --all
    Recreate all containers.
  openclaw sandbox recreate --session main
    Recreate a specific session.
  openclaw sandbox recreate --agent mybot
    Recreate agent containers.
  openclaw sandbox explain
    Explain effective sandbox config.


Docs: https://docs.openclaw.ai/cli/sandbox
```

### `openclaw sandbox remove`

```
🦞 OpenClaw 2026.2.21-2 (35a57bc) — Because texting yourself reminders is so 2024.

Usage: openclaw sandbox [options] [command]

Manage sandbox containers (Docker-based agent isolation)

Options:
  -h, --help  Display help for command

Commands:
  explain     Explain effective sandbox/tool policy for a session/agent
  list        List sandbox containers and their status
  recreate    Remove containers to force recreation with updated config

Examples:
  openclaw sandbox list
    List all sandbox containers.
  openclaw sandbox list --browser
    List only browser containers.
  openclaw sandbox recreate --all
    Recreate all containers.
  openclaw sandbox recreate --session main
    Recreate a specific session.
  openclaw sandbox recreate --agent mybot
    Recreate agent containers.
  openclaw sandbox explain
    Explain effective sandbox config.


Docs: https://docs.openclaw.ai/cli/sandbox
```

### `openclaw message send`

```
🦞 OpenClaw 2026.2.21-2 (35a57bc) — I'm like tmux: confusing at first, then suddenly you can't live without me.

Usage: openclaw message send [options]

Send a message

Options:
  --account <id>         Channel account id (accountId)
  --buttons <json>       Telegram inline keyboard buttons as JSON (array of
                         button rows)
  --card <json>          Adaptive Card JSON object (when supported by the
                         channel)
  --channel <channel>    Channel:
                         telegram|whatsapp|discord|irc|googlechat|slack|signal|imessage|feishu|nostr|msteams|mattermost|nextcloud-talk|matrix|bluebubbles|line|zalo|zalouser|tlon
  --components <json>    Discord components payload as JSON
  --dry-run              Print payload and skip sending (default: false)
  --gif-playback         Treat video media as GIF playback (WhatsApp only).
                         (default: false)
  -h, --help             Display help for command
  --json                 Output result as JSON (default: false)
  -m, --message <text>   Message body (required unless --media is set)
  --media <path-or-url>  Attach media (image/audio/video/document). Accepts
                         local paths or URLs.
  --reply-to <id>        Reply-to message id
  --silent               Send message silently without notification (Telegram +
                         Discord) (default: false)
  -t, --target <dest>    Recipient/channel: E.164 for WhatsApp/Signal, Telegram
                         chat id/@username, Discord/Slack channel/user, or
                         iMessage handle/chat_id
  --thread-id <id>       Thread id (Telegram forum thread)
  --verbose              Verbose logging (default: false)
```

### `openclaw message read`

```
🦞 OpenClaw 2026.2.21-2 (35a57bc) — I'm like tmux: confusing at first, then suddenly you can't live without me.

Usage: openclaw message read [options]

Read recent messages

Options:
  --account <id>       Channel account id (accountId)
  --after <id>         Read/search after id
  --around <id>        Read around id
  --before <id>        Read/search before id
  --channel <channel>  Channel:
                       telegram|whatsapp|discord|irc|googlechat|slack|signal|imessage|feishu|nostr|msteams|mattermost|nextcloud-talk|matrix|bluebubbles|line|zalo|zalouser|tlon
  --dry-run            Print payload and skip sending (default: false)
  -h, --help           Display help for command
  --include-thread     Include thread replies (Discord) (default: false)
  --json               Output result as JSON (default: false)
  --limit <n>          Result limit
  -t, --target <dest>  Recipient/channel: E.164 for WhatsApp/Signal, Telegram
                       chat id/@username, Discord/Slack channel/user, or
                       iMessage handle/chat_id
  --verbose            Verbose logging (default: false)
```

### `openclaw message list`

```
🦞 OpenClaw 2026.2.21-2 (35a57bc) — I'm the reason your shell history looks like a hacker-movie montage.

Usage: openclaw message [options] [command]

Send, read, and manage messages and channel actions

Options:
  -h, --help   Display help for command

Commands:
  ban          Ban a member
  broadcast    Broadcast a message to multiple targets
  channel      Channel actions
  delete       Delete a message
  edit         Edit a message
  emoji        Emoji actions
  event        Event actions
  kick         Kick a member
  member       Member actions
  permissions  Fetch channel permissions
  pin          Pin a message
  pins         List pinned messages
  poll         Send a poll
  react        Add or remove a reaction
  reactions    List reactions on a message
  read         Read recent messages
  role         Role actions
  search       Search Discord messages
  send         Send a message
  sticker      Sticker actions
  thread       Thread actions
  timeout      Timeout a member
  unpin        Unpin a message
  voice        Voice actions

Examples:
  openclaw message send --target +15555550123 --message "Hi"
    Send a text message.
  openclaw message send --target +15555550123 --message "Hi" --media photo.jpg
    Send a message with media.
  openclaw message poll --channel discord --target channel:123 --poll-question "Snack?" --poll-option Pizza --poll-option Sushi
    Create a Discord poll.
  openclaw message react --channel discord --target 123 --message-id 456 --emoji "✅"
    React to a message.

Docs: https://docs.openclaw.ai/cli/message
```

### `openclaw pairing list`

```
🦞 OpenClaw 2026.2.21-2 (35a57bc) — No $999 stand required.

Usage: openclaw pairing list [options] [channel]

List pending pairing requests

Arguments:
  channel                Channel (telegram, whatsapp, discord, imessage)

Options:
  --account <accountId>  Account id (for multi-account channels)
  --channel <channel>    Channel (telegram, whatsapp, discord, imessage)
  -h, --help             Display help for command
  --json                 Print JSON (default: false)
```

### `openclaw pairing approve`

```
🦞 OpenClaw 2026.2.21-2 (35a57bc) — I'm not magic—I'm just extremely persistent with retries and coping strategies.

Usage: openclaw pairing approve [options] <codeOrChannel> [code]

Approve a pairing code and allow that sender

Arguments:
  codeOrChannel          Pairing code (or channel when using 2 args)
  code                   Pairing code (when channel is passed as the 1st arg)

Options:
  --account <accountId>  Account id (for multi-account channels)
  --channel <channel>    Channel (telegram, whatsapp, discord, imessage)
  -h, --help             Display help for command
  --notify               Notify the requester on the same channel (default:
                         false)
```

### `openclaw pairing reject`

```
🦞 OpenClaw 2026.2.21-2 (35a57bc) — Meta wishes they shipped this fast.

Usage: openclaw pairing [options] [command]

Secure DM pairing (approve inbound requests)

Options:
  -h, --help  Display help for command

Commands:
  approve     Approve a pairing code and allow that sender
  help        Display help for command
  list        List pending pairing requests

Docs: https://docs.openclaw.ai/cli/pairing
```

### `openclaw devices list`

```
🦞 OpenClaw 2026.2.21-2 (35a57bc) — One CLI to rule them all, and one more restart because you changed the port.

Usage: openclaw devices list [options]

List pending and paired devices

Options:
  -h, --help             Display help for command
  --json                 Output JSON (default: false)
  --password <password>  Gateway password (password auth)
  --timeout <ms>         Timeout in ms (default: "10000")
  --token <token>        Gateway token (if required)
  --url <url>            Gateway WebSocket URL (defaults to gateway.remote.url
                         when configured)
```

### `openclaw devices pair`

```
🦞 OpenClaw 2026.2.21-2 (35a57bc) — I speak fluent bash, mild sarcasm, and aggressive tab-completion energy.

Usage: openclaw devices [options] [command]

Device pairing and auth tokens

Options:
  -h, --help  Display help for command

Commands:
  approve     Approve a pending device pairing request
  clear       Clear paired devices from the gateway table
  help        Display help for command
  list        List pending and paired devices
  reject      Reject a pending device pairing request
  remove      Remove a paired device entry
  revoke      Revoke a device token for a role
  rotate      Rotate a device token for a role
```

### `openclaw devices remove`

```
🦞 OpenClaw 2026.2.21-2 (35a57bc) — I'm basically a Swiss Army knife, but with more opinions and fewer sharp edges.

Usage: openclaw devices remove [options] <deviceId>

Remove a paired device entry

Arguments:
  deviceId               Paired device id

Options:
  -h, --help             Display help for command
  --json                 Output JSON (default: false)
  --password <password>  Gateway password (password auth)
  --timeout <ms>         Timeout in ms (default: "10000")
  --token <token>        Gateway token (if required)
  --url <url>            Gateway WebSocket URL (defaults to gateway.remote.url
                         when configured)
```

### `openclaw directory self`

```
🦞 OpenClaw 2026.2.21-2 (35a57bc) — One CLI to rule them all, and one more restart because you changed the port.

Usage: openclaw directory self [options]

Show the current account user

Options:
  --account <id>    Account id (accountId)
  --channel <name>  Channel (auto when only one is configured)
  -h, --help        Display help for command
  --json            Output JSON (default: false)
```

### `openclaw directory peers`

```
🦞 OpenClaw 2026.2.21-2 (35a57bc) — If you're lost, run doctor; if you're brave, run prod; if you're wise, run tests.

Usage: openclaw directory peers [options] [command]

Peer directory (contacts/users)

Options:
  -h, --help  Display help for command

Commands:
  help        Display help for command
  list        List peers
```

### `openclaw directory groups`

```
🦞 OpenClaw 2026.2.21-2 (35a57bc) — If something's on fire, I can't extinguish it—but I can write a beautiful postmortem.

Usage: openclaw directory groups [options] [command]

Group directory

Options:
  -h, --help  Display help for command

Commands:
  help        Display help for command
  list        List groups
  members     List group members
```

### `openclaw dns setup`

```
🦞 OpenClaw 2026.2.21-2 (35a57bc) — Chat APIs that don't require a Senate hearing.

Usage: openclaw dns setup [options]

Set up CoreDNS to serve your discovery domain for unicast DNS-SD (Wide-Area
Bonjour)

Options:
  --apply            Install/update CoreDNS config and (re)start the service
                     (requires sudo) (default: false)
  --domain <domain>  Wide-area discovery domain (e.g. openclaw.internal)
  -h, --help         Display help for command
```

### `openclaw dns status`

```
🦞 OpenClaw 2026.2.21-2 (35a57bc) — End-to-end encrypted, drama-to-drama excluded.

Usage: openclaw dns [options] [command]

DNS helpers for wide-area discovery (Tailscale + CoreDNS)

Options:
  -h, --help  Display help for command

Commands:
  help        Display help for command
  setup       Set up CoreDNS to serve your discovery domain for unicast DNS-SD
              (Wide-Area Bonjour)

Docs: https://docs.openclaw.ai/cli/dns
```

### `openclaw browser open`

```
🦞 OpenClaw 2026.2.21-2 (35a57bc) — If it works, it's automation; if it breaks, it's a "learning opportunity."

Usage: openclaw browser open [options] <url>

Open a URL in a new tab

Arguments:
  url         URL to open

Options:
  -h, --help  Display help for command
```

### `openclaw browser close`

```
🦞 OpenClaw 2026.2.21-2 (35a57bc) — It's not "failing," it's "discovering new ways to configure the same thing wrong."

Usage: openclaw browser close [options] [targetId]

Close a tab (target id optional)

Arguments:
  targetId    Target id or unique prefix (optional)

Options:
  -h, --help  Display help for command
```

### `openclaw browser status`

```
🦞 OpenClaw 2026.2.21-2 (35a57bc) — Works on Android. Crazy concept, we know.

Usage: openclaw browser status [options]

Show browser status

Options:
  -h, --help  Display help for command
```

### `openclaw approvals list`

```
🦞 OpenClaw 2026.2.21-2 (35a57bc) — I don't judge, but your missing API keys are absolutely judging you.

Usage: openclaw approvals|exec-approvals [options] [command]

Manage exec approvals (gateway or node host)

Options:
  -h, --help  Display help for command

Commands:
  allowlist   Edit the per-agent allowlist
  get         Fetch exec approvals snapshot
  help        Display help for command
  set         Replace exec approvals with a JSON file

Docs: https://docs.openclaw.ai/cli/approvals
```

### `openclaw approvals approve`

```
🦞 OpenClaw 2026.2.21-2 (35a57bc) — I'm not saying your workflow is chaotic... I'm just bringing a linter and a helmet.

Usage: openclaw approvals|exec-approvals [options] [command]

Manage exec approvals (gateway or node host)

Options:
  -h, --help  Display help for command

Commands:
  allowlist   Edit the per-agent allowlist
  get         Fetch exec approvals snapshot
  help        Display help for command
  set         Replace exec approvals with a JSON file

Docs: https://docs.openclaw.ai/cli/approvals
```

### `openclaw approvals reject`

```
🦞 OpenClaw 2026.2.21-2 (35a57bc) — If it works, it's automation; if it breaks, it's a "learning opportunity."

Usage: openclaw approvals|exec-approvals [options] [command]

Manage exec approvals (gateway or node host)

Options:
  -h, --help  Display help for command

Commands:
  allowlist   Edit the per-agent allowlist
  get         Fetch exec approvals snapshot
  help        Display help for command
  set         Replace exec approvals with a JSON file

Docs: https://docs.openclaw.ai/cli/approvals
```

### `openclaw system events`

```
🦞 OpenClaw 2026.2.21-2 (35a57bc) — One CLI to rule them all, and one more restart because you changed the port.

Usage: openclaw system [options] [command]

System tools (events, heartbeat, presence)

Options:
  -h, --help  Display help for command

Commands:
  event       Enqueue a system event and optionally trigger a heartbeat
  heartbeat   Heartbeat controls
  help        Display help for command
  presence    List system presence entries

Docs: https://docs.openclaw.ai/cli/system
```

### `openclaw system heartbeat`

```
🦞 OpenClaw 2026.2.21-2 (35a57bc) — Hot reload for config, cold sweat for deploys.

Usage: openclaw system heartbeat [options] [command]

Heartbeat controls

Options:
  -h, --help  Display help for command

Commands:
  disable     Disable heartbeats
  enable      Enable heartbeats
  help        Display help for command
  last        Show the last heartbeat event
```

### `openclaw system presence`

```
🦞 OpenClaw 2026.2.21-2 (35a57bc) — If something's on fire, I can't extinguish it—but I can write a beautiful postmortem.

Usage: openclaw system presence [options]

List system presence entries

Options:
  --expect-final   Wait for final response (agent) (default: false)
  -h, --help       Display help for command
  --json           Output JSON (default: false)
  --timeout <ms>   Timeout in ms (default: "30000")
  --token <token>  Gateway token (if required)
  --url <url>      Gateway WebSocket URL (defaults to gateway.remote.url when
                   configured)
```

### `openclaw update check`

```
🦞 OpenClaw 2026.2.21-2 (35a57bc) — No $999 stand required.

Usage: openclaw update [options] [command]

Update OpenClaw and inspect update channel status

Options:
  --channel <stable|beta|dev>  Persist update channel (git + npm)
  -h, --help                   Display help for command
  --json                       Output result as JSON (default: false)
  --no-restart                 Skip restarting the gateway service after a
                               successful update
  --tag <dist-tag|version>     Override npm dist-tag or version for this update
  --timeout <seconds>          Timeout for each update step in seconds (default:
                               1200)
  --yes                        Skip confirmation prompts (non-interactive)
                               (default: false)

Commands:
  status                       Show update channel and version status
  wizard                       Interactive update wizard

What this does:
  - Git checkouts: fetches, rebases, installs deps, builds, and runs doctor
  - npm installs: updates via detected package manager

Switch channels:
  - Use --channel stable|beta|dev to persist the update channel in config
  - Run openclaw update status to see the active channel and source
  - Use --tag <dist-tag|version> for a one-off npm update without persisting

Non-interactive:
  - Use --yes to accept downgrade prompts
  - Combine with --channel/--tag/--restart/--json/--timeout as needed

Examples:
  openclaw update # Update a source checkout (git)
  openclaw update --channel beta # Switch to beta channel (git + npm)
  openclaw update --channel dev # Switch to dev channel (git + npm)
  openclaw update --tag beta # One-off update to a dist-tag or version
  openclaw update --no-restart # Update without restarting the service
  openclaw update --json # Output result as JSON
  openclaw update --yes # Non-interactive (accept downgrade prompts)
  openclaw update wizard # Interactive update wizard
  openclaw --update # Shorthand for openclaw update

Notes:
  - Switch channels with --channel stable|beta|dev
  - For global installs: auto-updates via detected package manager when possible (see docs/install/updating.md)
  - Downgrades require confirmation (can break configuration)
  - Skips update if the working directory has uncommitted changes

Docs: https://docs.openclaw.ai/cli/update
```

### `openclaw update apply`

```
🦞 OpenClaw 2026.2.21-2 (35a57bc) — curl for conversations.

Usage: openclaw update [options] [command]

Update OpenClaw and inspect update channel status

Options:
  --channel <stable|beta|dev>  Persist update channel (git + npm)
  -h, --help                   Display help for command
  --json                       Output result as JSON (default: false)
  --no-restart                 Skip restarting the gateway service after a
                               successful update
  --tag <dist-tag|version>     Override npm dist-tag or version for this update
  --timeout <seconds>          Timeout for each update step in seconds (default:
                               1200)
  --yes                        Skip confirmation prompts (non-interactive)
                               (default: false)

Commands:
  status                       Show update channel and version status
  wizard                       Interactive update wizard

What this does:
  - Git checkouts: fetches, rebases, installs deps, builds, and runs doctor
  - npm installs: updates via detected package manager

Switch channels:
  - Use --channel stable|beta|dev to persist the update channel in config
  - Run openclaw update status to see the active channel and source
  - Use --tag <dist-tag|version> for a one-off npm update without persisting

Non-interactive:
  - Use --yes to accept downgrade prompts
  - Combine with --channel/--tag/--restart/--json/--timeout as needed

Examples:
  openclaw update # Update a source checkout (git)
  openclaw update --channel beta # Switch to beta channel (git + npm)
  openclaw update --channel dev # Switch to dev channel (git + npm)
  openclaw update --tag beta # One-off update to a dist-tag or version
  openclaw update --no-restart # Update without restarting the service
  openclaw update --json # Output result as JSON
  openclaw update --yes # Non-interactive (accept downgrade prompts)
  openclaw update wizard # Interactive update wizard
  openclaw --update # Shorthand for openclaw update

Notes:
  - Switch channels with --channel stable|beta|dev
  - For global installs: auto-updates via detected package manager when possible (see docs/install/updating.md)
  - Downgrades require confirmation (can break configuration)
  - Skips update if the working directory has uncommitted changes

Docs: https://docs.openclaw.ai/cli/update
```

### `openclaw webhooks list`

```
🦞 OpenClaw 2026.2.21-2 (35a57bc) — I read logs so you can keep pretending you don't have to.

Usage: openclaw webhooks [options] [command]

Webhook helpers and integrations

Options:
  -h, --help  Display help for command

Commands:
  gmail       Gmail Pub/Sub hooks (via gogcli)
  help        Display help for command

Docs: https://docs.openclaw.ai/cli/webhooks
```

### `openclaw webhooks add`

```
🦞 OpenClaw 2026.2.21-2 (35a57bc) — No $999 stand required.

Usage: openclaw webhooks [options] [command]

Webhook helpers and integrations

Options:
  -h, --help  Display help for command

Commands:
  gmail       Gmail Pub/Sub hooks (via gogcli)
  help        Display help for command

Docs: https://docs.openclaw.ai/cli/webhooks
```

### `openclaw webhooks remove`

```
🦞 OpenClaw 2026.2.21-2 (35a57bc) — The only bot that stays out of your training set.

Usage: openclaw webhooks [options] [command]

Webhook helpers and integrations

Options:
  -h, --help  Display help for command

Commands:
  gmail       Gmail Pub/Sub hooks (via gogcli)
  help        Display help for command

Docs: https://docs.openclaw.ai/cli/webhooks
```

### `openclaw node start`

```
🦞 OpenClaw 2026.2.21-2 (35a57bc) — We ship features faster than Apple ships calculator updates.

Usage: openclaw node [options] [command]

Run and manage the headless node host service

Options:
  -h, --help  Display help for command

Commands:
  help        Display help for command
  install     Install the node host service (launchd/systemd/schtasks)
  restart     Restart the node host service (launchd/systemd/schtasks)
  run         Run the headless node host (foreground)
  status      Show node host status
  stop        Stop the node host service (launchd/systemd/schtasks)
  uninstall   Uninstall the node host service (launchd/systemd/schtasks)

Examples:
  openclaw node run --host 127.0.0.1 --port 18789
    Run the node host in the foreground.
  openclaw node status
    Check node host service status.
  openclaw node install
    Install the node host service.
  openclaw node restart
    Restart the installed node host service.

Docs: https://docs.openclaw.ai/cli/node
```

### `openclaw node stop`

```
🦞 OpenClaw 2026.2.21-2 (35a57bc) — I don't judge, but your missing API keys are absolutely judging you.

Usage: openclaw node stop [options]

Stop the node host service (launchd/systemd/schtasks)

Options:
  -h, --help  Display help for command
  --json      Output JSON (default: false)
```

### `openclaw node status`

```
🦞 OpenClaw 2026.2.21-2 (35a57bc) — The only crab in your contacts you actually want to hear from. 🦞

Usage: openclaw node status [options]

Show node host status

Options:
  -h, --help  Display help for command
  --json      Output JSON (default: false)
```

### `openclaw nodes list`

```
🦞 OpenClaw 2026.2.21-2 (35a57bc) — I'll butter your workflow like a lobster roll: messy, delicious, effective.

Usage: openclaw nodes list [options]

List pending and paired nodes

Options:
  --connected                  Only show connected nodes
  -h, --help                   Display help for command
  --json                       Output JSON (default: false)
  --last-connected <duration>  Only show nodes connected within duration (e.g.
                               24h)
  --timeout <ms>               Timeout in ms (default: "10000")
  --token <token>              Gateway token (if required)
  --url <url>                  Gateway WebSocket URL (defaults to
                               gateway.remote.url when configured)
```

### `openclaw nodes pair`

```
🦞 OpenClaw 2026.2.21-2 (35a57bc) — Works on Android. Crazy concept, we know.

Usage: openclaw nodes [options] [command]

Manage gateway-owned nodes (pairing, status, invoke, and media)

Options:
  -h, --help  Display help for command

Commands:
  approve     Approve a pending pairing request
  camera      Capture camera media from a paired node
  canvas      Capture or render canvas content from a paired node
  describe    Describe a node (capabilities + supported invoke commands)
  help        Display help for command
  invoke      Invoke a command on a paired node
  list        List pending and paired nodes
  location    Fetch location from a paired node
  notify      Send a local notification on a node (mac only)
  pending     List pending pairing requests
  push        Send an APNs test push to an iOS node
  reject      Reject a pending pairing request
  rename      Rename a paired node (display name override)
  run         Run a shell command on a node (mac only)
  screen      Capture screen recordings from a paired node
  status      List known nodes with connection status and capabilities

Examples:
  openclaw nodes status
    List known nodes with live status.
  openclaw nodes pairing pending
    Show pending node pairing requests.
  openclaw nodes run --node <id> --raw "uname -a"
    Run a shell command on a node.
  openclaw nodes camera snap --node <id>
    Capture a photo from a node camera.

Docs: https://docs.openclaw.ai/cli/nodes
```

### `openclaw nodes remove`

```
🦞 OpenClaw 2026.2.21-2 (35a57bc) — One CLI to rule them all, and one more restart because you changed the port.

Usage: openclaw nodes [options] [command]

Manage gateway-owned nodes (pairing, status, invoke, and media)

Options:
  -h, --help  Display help for command

Commands:
  approve     Approve a pending pairing request
  camera      Capture camera media from a paired node
  canvas      Capture or render canvas content from a paired node
  describe    Describe a node (capabilities + supported invoke commands)
  help        Display help for command
  invoke      Invoke a command on a paired node
  list        List pending and paired nodes
  location    Fetch location from a paired node
  notify      Send a local notification on a node (mac only)
  pending     List pending pairing requests
  push        Send an APNs test push to an iOS node
  reject      Reject a pending pairing request
  rename      Rename a paired node (display name override)
  run         Run a shell command on a node (mac only)
  screen      Capture screen recordings from a paired node
  status      List known nodes with connection status and capabilities

Examples:
  openclaw nodes status
    List known nodes with live status.
  openclaw nodes pairing pending
    Show pending node pairing requests.
  openclaw nodes run --node <id> --raw "uname -a"
    Run a shell command on a node.
  openclaw nodes camera snap --node <id>
    Capture a photo from a node camera.

Docs: https://docs.openclaw.ai/cli/nodes
```

### `openclaw nodes invoke`

```
🦞 OpenClaw 2026.2.21-2 (35a57bc) — Your messages, your servers, your control.

Usage: openclaw nodes invoke [options]

Invoke a command on a paired node

Options:
  --command <command>      Command (e.g. canvas.eval)
  -h, --help               Display help for command
  --idempotency-key <key>  Idempotency key (optional)
  --invoke-timeout <ms>    Node invoke timeout in ms (default 15000) (default:
                           "15000")
  --json                   Output JSON (default: false)
  --node <idOrNameOrIp>    Node id, name, or IP
  --params <json>          JSON object string for params (default: "{}")
  --timeout <ms>           Timeout in ms (default: "30000")
  --token <token>          Gateway token (if required)
  --url <url>              Gateway WebSocket URL (defaults to gateway.remote.url
                           when configured)
```

### `openclaw skills list`

```
🦞 OpenClaw 2026.2.21-2 (35a57bc) — Automation with claws: minimal fuss, maximal pinch.

Usage: openclaw skills list [options]

List all available skills

Options:
  --eligible     Show only eligible (ready to use) skills (default: false)
  -h, --help     Display help for command
  --json         Output as JSON (default: false)
  -v, --verbose  Show more details including missing requirements (default:
                 false)
```

### `openclaw skills info`

```
🦞 OpenClaw 2026.2.21-2 (35a57bc) — Less clicking, more shipping, fewer "where did that file go" moments.

Usage: openclaw skills info [options] <name>

Show detailed information about a skill

Arguments:
  name        Skill name

Options:
  -h, --help  Display help for command
  --json      Output as JSON (default: false)
```

### `openclaw acp list`

```
🦞 OpenClaw 2026.2.21-2 (35a57bc) — One CLI to rule them all, and one more restart because you changed the port.

Usage: openclaw acp [options] [command]

Run an ACP bridge backed by the Gateway

Options:
  -h, --help               Display help for command
  --no-prefix-cwd          Do not prefix prompts with the working directory
  --password <password>    Gateway password (if required)
  --password-file <path>   Read gateway password from file
  --require-existing       Fail if the session key/label does not exist
                           (default: false)
  --reset-session          Reset the session key before first use (default:
                           false)
  --session <key>          Default session key (e.g. agent:main:main)
  --session-label <label>  Default session label to resolve
  --token <token>          Gateway token (if required)
  --token-file <path>      Read gateway token from file
  --url <url>              Gateway WebSocket URL (defaults to gateway.remote.url
                           when configured)
  --verbose, -v            Verbose logging to stderr (default: false)

Commands:
  client                   Run an interactive ACP client against the local ACP
                           bridge

Docs: https://docs.openclaw.ai/cli/acp
```

### `openclaw acp invoke`

```
🦞 OpenClaw 2026.2.21-2 (35a57bc) — If you're lost, run doctor; if you're brave, run prod; if you're wise, run tests.

Usage: openclaw acp [options] [command]

Run an ACP bridge backed by the Gateway

Options:
  -h, --help               Display help for command
  --no-prefix-cwd          Do not prefix prompts with the working directory
  --password <password>    Gateway password (if required)
  --password-file <path>   Read gateway password from file
  --require-existing       Fail if the session key/label does not exist
                           (default: false)
  --reset-session          Reset the session key before first use (default:
                           false)
  --session <key>          Default session key (e.g. agent:main:main)
  --session-label <label>  Default session label to resolve
  --token <token>          Gateway token (if required)
  --token-file <path>      Read gateway token from file
  --url <url>              Gateway WebSocket URL (defaults to gateway.remote.url
                           when configured)
  --verbose, -v            Verbose logging to stderr (default: false)

Commands:
  client                   Run an interactive ACP client against the local ACP
                           bridge

Docs: https://docs.openclaw.ai/cli/acp
```
