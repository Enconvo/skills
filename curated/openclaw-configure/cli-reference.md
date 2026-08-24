# OpenClaw CLI Reference

Generated from `OpenClaw 2026.7.1-2 (0790d9f)` on 2026-08-03. Raw `--help` output for every top-level command.

## `openclaw`

```text
OpenClaw 2026.7.1-2 (0790d9f) — All your chats, one OpenClaw.

Usage: openclaw [options] [command]

Options:
  --container <name>   Run the CLI inside a running Podman/Docker container
                       named <name> (default: env OPENCLAW_CONTAINER)
  --dev                Dev profile: isolate state under ~/.openclaw-dev, default
                       gateway port 19001, and shift derived ports
                       (browser/canvas)
  -h, --help           Display help for command
  --log-level <level>  Global log level override for file + console
                       (silent|fatal|error|warn|info|debug|trace)
  --no-color           Disable ANSI colors
  --profile <name>     Use a named profile (isolates
                       OPENCLAW_STATE_DIR/OPENCLAW_CONFIG_PATH under
                       ~/.openclaw-<name>)
  -V, --version        output the version number

Commands:
  Hint: commands suffixed with * have subcommands. Run <command> --help for details.
  acp *                Run an ACP bridge backed by the Gateway
  agent                Run an agent turn via the Gateway (use --local for
                       embedded)
  agents *             Manage isolated agents (workspaces + auth + routing)
  approvals *          Manage exec approvals (gateway or node host)
  attach               Attach Claude Code to a gateway session with scoped MCP
                       tools
  audit                Inspect metadata-only agent run and tool action records
  backup *             Create and verify local backup archives for OpenClaw
                       state
  capability *         Run provider capability commands (fallback alias: infer)
  channels *           Manage connected chat channels and accounts
  chat                 Open a local terminal UI (alias for tui --local)
  clawbot *            Legacy clawbot command aliases
  commitments *        List and manage inferred follow-up commitments
  completion           Generate shell completion script
  config *             Non-interactive config helpers
                       (get/set/patch/unset/file/schema/validate). Run without
                       subcommand for guided setup.
  configure            Interactive configuration for credentials, channels,
                       gateway, and agent defaults
  crestodian           Open the ring-zero setup and repair helper
  cron *               Manage cron jobs (via Gateway)
  daemon *             Manage the Gateway service (launchd/systemd/schtasks)
  dashboard            Open the Control UI with your current token
  devices *            Device pairing and auth tokens
  directory *          Lookup contact and group IDs (self, peers, groups) for
                       supported chat channels
  dns *                DNS helpers for wide-area discovery (Tailscale + CoreDNS)
  docs                 Search the live OpenClaw docs
  doctor               Health checks + quick fixes for the gateway and channels
  exec-approvals *     Manage exec approvals (alias for approvals)
  exec-policy *        Show or synchronize requested exec policy with host
                       approvals
  gateway *            Run, inspect, and query the WebSocket Gateway
  health               Fetch health from the running gateway
  help                 Display help for command
  hooks *              Manage internal agent hooks
  infer *              Run provider-backed inference commands through a stable
                       CLI surface
  logs                 Tail gateway file logs via RPC
  mcp *                Manage OpenClaw mcp.servers config and channel bridge
  memory *             Search, inspect, and reindex memory files
  message *            Send, read, and manage messages and channel actions
  migrate *            Import state from another agent system
  models *             Model discovery, scanning, and configuration
  node *               Run and manage the headless node host service
  nodes *              Manage gateway-owned nodes (pairing, status, invoke, and
                       media)
  onboard              Guided setup for auth, models, Gateway, workspace,
                       channels, and skills
  pairing *            Secure DM pairing (approve inbound requests)
  plugins *            Manage OpenClaw plugins and extensions
  promos *             Discover and claim promotional model offers from ClawHub
  proxy *              Run the OpenClaw debug proxy and inspect captured traffic
  qr                   Generate a mobile pairing QR code and setup code
  reset                Reset local config/state (keeps the CLI installed)
  sandbox *            Manage sandbox containers (Docker-based agent isolation)
  secrets *            Secrets runtime controls
  security *           Audit local config and state for common security
                       foot-guns
  sessions *           List stored conversation sessions
  setup                Alias for openclaw onboard
  skills *             List and inspect available skills
  status               Show channel health and recent session recipients
  system *             System tools (events, heartbeat, presence)
  tasks *              Inspect durable background tasks and TaskFlow state
  terminal             Open a local terminal UI (alias for tui --local)
  transcripts *        Inspect stored transcripts
  tui                  Open a terminal UI connected to the Gateway
  uninstall            Uninstall the gateway service + local data (CLI remains)
  update *             Update OpenClaw and inspect update channel status
  webhooks *           Webhook helpers and integrations
  worktrees *          Create, inspect, restore, and clean up managed worktrees

Examples:
  openclaw onboard
    Run guided setup for a local Gateway, workspace, auth, and channels.
  openclaw setup
    Create the baseline config, workspace, and session folders.
  openclaw configure
    Change models, Gateway, channels, plugins, skills, and health checks.
  openclaw status
    Check Gateway, channel, model, and recent-session status.
  openclaw doctor --fix
    Repair common config, service, plugin, and channel problems.
  openclaw channels add
    Add or update a chat channel account with guided prompts.
  openclaw channels status
    See connected messaging accounts and login state.
  openclaw --dev gateway
    Run a dev Gateway (isolated state/config) on ws://127.0.0.1:19001.
  openclaw gateway run --force
    Start the Gateway and replace anything bound to its port.
  openclaw models status
    Show model/provider auth health before running agents.
  openclaw plugins list
    Inspect enabled, disabled, and installed plugins.
  openclaw agent --to +15555550123 --message "Run summary" --deliver
    Run one agent turn through the Gateway and optionally deliver the reply.
  openclaw message send --channel telegram --target @mychat --message "Hi"
    Send via your Telegram bot.

Docs: https://docs.openclaw.ai/cli
```

## `openclaw acp`

```text
OpenClaw 2026.7.1-2 (0790d9f) — All your chats, one OpenClaw.

Usage: openclaw acp [options] [command]

Run an ACP bridge backed by the Gateway

Options:
  -h, --help               Display help for command
  --no-prefix-cwd          Do not prefix prompts with the working directory
  --password <password>    Gateway password (if required)
  --password-file <path>   Read gateway password from file
  --provenance <mode>      ACP provenance mode: off, meta, or meta+receipt
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
  -v, --verbose            Verbose logging to stderr (default: false)

Commands:
  client                   Run an interactive ACP client against the local ACP
                           bridge

Docs: https://docs.openclaw.ai/cli/acp
```

## `openclaw agent`

```text
OpenClaw 2026.7.1-2 (0790d9f) — All your chats, one OpenClaw.

Usage: openclaw agent [options]

Run an agent turn via the Gateway (use --local for embedded)

Options:
  --agent <id>               Agent id (overrides routing bindings)
  --channel <channel>        Delivery channel:
                             last|telegram|whatsapp|discord|irc|googlechat|slack|signal|imessage|feishu|nostr|msteams|mattermost|nextcloud-talk|matrix|raft|line|zalo|clickclack|zalouser|sms|synology-chat|tlon|qa-channel|qqbot|twitch
                             (omit to use the main session channel)
  --deliver                  Send the agent's reply back to the selected channel
                             (default: false)
  -h, --help                 Display help for command
  --json                     Output result as JSON (default: false)
  --local                    Run the embedded agent locally (requires model
                             provider API keys in your shell) (default: false)
  -m, --message <text>       Message body for the agent
  --message-file <path>      Read the agent message body from a UTF-8 file
  --model <id>               Model override for this run (provider/model or
                             model id)
  --reply-account <id>       Delivery account id override
  --reply-channel <channel>  Delivery channel override (separate from routing)
  --reply-to <target>        Delivery target override (separate from session
                             routing)
  --session-id <id>          Use an explicit session id
  --session-key <key>        Explicit session key (agent:<id>:<key>, or scoped
                             to --agent)
  -t, --to <number>          Recipient number in E.164 used to derive the
                             session key
  --thinking <level>         Thinking level: off | minimal | low | medium | high
                             | xhigh | adaptive | max where supported
  --timeout <seconds>        Override agent command timeout (seconds, default
                             600 or config value)
  --verbose <on|off>         Persist agent verbose level for the session

Examples:
  openclaw agent --to +15555550123 --message "status update"
    Start a new session.
  openclaw agent --agent ops --message "Summarize logs"
    Use a specific agent.
  openclaw agent --agent ops --message-file ./task.md
    Read a multiline message file.
  openclaw agent --session-key agent:ops:incident-42 --message "Summarize status"
    Target an exact session key.
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

```text
OpenClaw 2026.7.1-2 (0790d9f) — All your chats, one OpenClaw.

Usage: openclaw agents [options] [command]

Manage isolated agents (workspaces + auth + routing)

Options:
  -h, --help    Display help for command

Commands:
  add           Add a new isolated agent
  bind          Add routing bindings for an agent
  bindings      List routing bindings
  delete        Delete an agent and prune workspace/state
  list          List configured agents
  set-identity  Update an agent identity (name/theme/emoji/avatar)
  unbind        Remove routing bindings for an agent

Docs: https://docs.openclaw.ai/cli/agents
```

## `openclaw approvals`

```text
OpenClaw 2026.7.1-2 (0790d9f) — All your chats, one OpenClaw.

Usage: openclaw approvals|exec-approvals [options] [command]

Manage exec approvals (gateway or node host)

Options:
  -h, --help  Display help for command

Commands:
  allowlist   Edit the per-agent allowlist
  get         Fetch exec approvals snapshot
  set         Replace exec approvals with a JSON file

Docs: https://docs.openclaw.ai/cli/approvals
```

## `openclaw attach`

```text
OpenClaw 2026.7.1-2 (0790d9f) — All your chats, one OpenClaw.

Usage: openclaw attach [options]

Attach Claude Code to a gateway session with scoped MCP tools

Options:
  --bin <path>     Claude Code binary to spawn (default: "claude")
  -h, --help       Display help for command
  --print-config   Mint the grant + write the .mcp.json, print how to launch it,
                   and exit without spawning (default: false)
  --session <key>  Gateway session key to bind (default: main session)
  --ttl <ms>       Grant TTL in milliseconds (default: gateway policy)

Examples:
  openclaw attach                       Attach Claude Code to the main session
  openclaw attach --session agent:main:telegram:123 --ttl 600000
  openclaw attach --print-config        Set up the grant + config and print how to launch it yourself
```

## `openclaw audit`

```text
OpenClaw 2026.7.1-2 (0790d9f) — All your chats, one OpenClaw.

Usage: openclaw audit [options]

Inspect metadata-only agent run and tool action records

Options:
  --after <timestamp>   Include records at/after ISO time or Unix milliseconds
  --agent <id>          Filter by agent id
  --before <timestamp>  Include records at/before ISO time or Unix milliseconds
  --cursor <sequence>   Continue from a previous result cursor
  -h, --help            Display help for command
  --json                Output a bounded JSON page (default: false)
  --kind <kind>         Filter by kind (agent_run or tool_action)
  --limit <count>       Maximum records (1-500) (default: "100")
  --run <id>            Filter by run id
  --session <key>       Filter by exact session key
  --status <status>     Filter by status (started, succeeded, failed, cancelled,
                        timed_out, blocked, unknown)

Docs: https://docs.openclaw.ai/cli/audit
```

## `openclaw backup`

```text
OpenClaw 2026.7.1-2 (0790d9f) — All your chats, one OpenClaw.

Usage: openclaw backup [options] [command]

Create and verify local backup archives for OpenClaw state

Options:
  -h, --help  Display help for command

Commands:
  create      Write a backup archive for config, credentials, sessions, and
              workspaces
  help        Display help for command
  verify      Validate a backup archive and its embedded manifest

Docs: https://docs.openclaw.ai/cli/backup
```

## `openclaw capability`

```text
OpenClaw 2026.7.1-2 (0790d9f) — All your chats, one OpenClaw.

Usage: openclaw infer|capability [options] [command]

Run provider-backed inference commands through a stable CLI surface

Options:
  -h, --help  Display help for command

Commands:
  audio       Audio transcription
  embedding   Embedding providers
  help        Display help for command
  image       Image generation and description
  inspect     Inspect one canonical capability id
  list        List canonical capability ids and supported transports
  model       Text inference and model catalog commands
  tts         Text to speech
  video       Video generation and description
  web         Web capabilities

Docs: https://docs.openclaw.ai/cli/infer
```

## `openclaw channels`

```text
OpenClaw 2026.7.1-2 (0790d9f) — All your chats, one OpenClaw.

Usage: openclaw channels [options] [command]

Manage connected chat channels and accounts

Options:
  -h, --help    Display help for command

Commands:
  add           Add or update a channel account
  capabilities  Show provider capabilities (intents/scopes + supported features)
  list          List chat channels (configured by default; pass --all for
                installable catalog)
  login         Link a channel account (if supported)
  logout        Log out of a channel session (if supported)
  logs          Show recent channel logs from the gateway log file
  remove        Disable or delete a channel account
  resolve       Resolve channel/user names to IDs
  status        Show gateway channel status (use status --deep for local)

Examples:
  openclaw channels list
    List configured channels.
  openclaw channels list --all
    Show configured, bundled, and installable channels.
  openclaw channels add
    Open guided channel setup.
  openclaw channels status --probe
    Run channel status checks and probes.
  openclaw channels add --channel telegram --token <token>
    Add or update a channel account non-interactively.
  openclaw channels login --channel whatsapp
    Link a WhatsApp Web account.

Docs: https://docs.openclaw.ai/cli/channels
```

## `openclaw chat`

```text
OpenClaw 2026.7.1-2 (0790d9f) — All your chats, one OpenClaw.

Usage: openclaw tui|terminal [options]

Open a terminal UI connected to the Gateway

Options:
  --deliver              Deliver assistant replies (default: false)
  -h, --help             Display help for command
  --history-limit <n>    History entries to load (default: "200")
  --local                Run against the local embedded agent runtime (default:
                         false)
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

## `openclaw clawbot`

```text
OpenClaw 2026.7.1-2 (0790d9f) — All your chats, one OpenClaw.

Usage: openclaw clawbot [options] [command]

Legacy clawbot command aliases

Options:
  -h, --help  Display help for command

Commands:
  help        Display help for command
  qr          Generate a mobile pairing QR code and setup code

Docs: https://docs.openclaw.ai/cli/clawbot
```

## `openclaw commitments`

```text
OpenClaw 2026.7.1-2 (0790d9f) — All your chats, one OpenClaw.

Usage: openclaw commitments [options] [command]

List and manage inferred follow-up commitments

Options:
  --agent <id>       Agent id to inspect
  --all              Show all statuses (default: false)
  -h, --help         Display help for command
  --json             Output JSON instead of text (default: false)
  --status <status>  Filter by status (pending, sent, dismissed, snoozed,
                     expired)

Commands:
  dismiss            Dismiss inferred follow-up commitments
  list               List inferred follow-up commitments

Examples:
  openclaw commitments
    List pending inferred follow-ups.
  openclaw commitments --all
    List all inferred follow-ups.
  openclaw commitments --agent work
    List one agent's inferred follow-ups.
  openclaw commitments dismiss cm_abc123
    Dismiss a follow-up.
```

## `openclaw completion`

```text
OpenClaw 2026.7.1-2 (0790d9f) — All your chats, one OpenClaw.

Usage: openclaw completion [options]

Generate shell completion script

Options:
  -h, --help           Display help for command
  -i, --install        Install completion script to shell profile
  -s, --shell <shell>  Shell to generate completion for (default: zsh) (choices:
                       "zsh", "bash", "powershell", "fish")
  --write-state        Write completion scripts to
                       $OPENCLAW_STATE_DIR/completions (no stdout)
  -y, --yes            Skip confirmation (non-interactive) (default: false)

Docs: https://docs.openclaw.ai/cli/completion
```

## `openclaw config`

```text
OpenClaw 2026.7.1-2 (0790d9f) — All your chats, one OpenClaw.

Usage: openclaw config [options] [command]

Non-interactive config helpers (get/set/patch/unset/file/schema/validate). Run
without subcommand for guided setup.

Options:
  -h, --help           Display help for command
  --section <section>  Configuration sections for guided setup (repeatable). Use
                       with no subcommand. (default: [])

Commands:
  file                 Print the active config file path
  get                  Get a config value by dot path
  patch                Patch config from a JSON5 object in one validated write.
                       Objects merge recursively, arrays/scalars replace, and
                       null deletes a path.
                       Examples:
                       openclaw config patch --file ./openclaw.patch.json5
                       --dry-run
                       openclaw config patch --stdin
  schema               Print the JSON schema for openclaw.json
  set                  Set config values by path (value mode, ref/provider
                       builder mode, or batch JSON mode).
                       Examples:
                       openclaw config set gateway.port 19001 --strict-json
                       openclaw config set channels.discord.token --ref-provider
                       default --ref-source env --ref-id DISCORD_BOT_TOKEN
                       openclaw config set secrets.providers.vault
                       --provider-source file --provider-path
                       /etc/openclaw/secrets.json --provider-mode json
                       openclaw config set --batch-file ./config-set.batch.json
                       --dry-run
  unset                Remove a config value by dot path
  validate             Validate the current config against the schema without
                       starting the gateway

Docs: https://docs.openclaw.ai/cli/config
```

## `openclaw configure`

```text
OpenClaw 2026.7.1-2 (0790d9f) — All your chats, one OpenClaw.

Usage: openclaw configure [options]

Interactive configuration for credentials, channels, gateway, and agent defaults

Options:
  -h, --help           Display help for command
  --section <section>  Configuration sections (repeatable). Options: workspace,
                       model, web, gateway, daemon, channels, plugins, skills,
                       health (default: [])

Docs: https://docs.openclaw.ai/cli/configure
```

## `openclaw crestodian`

```text
OpenClaw 2026.7.1-2 (0790d9f) — All your chats, one OpenClaw.

Usage: openclaw crestodian [options]

Open the ring-zero setup and repair helper

Options:
  -h, --help            Display help for command
  --json                Output startup overview as JSON (default: false)
  -m, --message <text>  Run one Crestodian request
  --yes                 Approve persistent config writes for this request
                        (default: false)

Examples:
  openclaw
    Start Crestodian.
  openclaw crestodian
    Start Crestodian explicitly.
  openclaw crestodian -m "status"
    Run one status request.
  openclaw crestodian -m "set default model openai/gpt-5.2" --yes
    Apply a typed config write.
```

## `openclaw cron`

```text
OpenClaw 2026.7.1-2 (0790d9f) — All your chats, one OpenClaw.

Usage: openclaw cron [options] [command]

Manage cron jobs (via Gateway)

Options:
  -h, --help  Display help for command

Commands:
  add         Add a cron job
  disable     Disable a cron job
  edit        Edit a cron job (patch fields)
  enable      Enable a cron job
  get         Get a cron job as JSON
  list        List cron jobs
  rm          Remove a cron job
  run         Run a cron job now (debug)
  runs        Show cron run history
  show        Show a cron job
  status      Show cron scheduler status

Docs: https://docs.openclaw.ai/cli/cron
Upgrade tip: run `openclaw doctor --fix` to normalize legacy cron job storage.
```

## `openclaw daemon`

```text
OpenClaw 2026.7.1-2 (0790d9f) — All your chats, one OpenClaw.

Usage: openclaw daemon [options] [command]

Manage the Gateway service (launchd/systemd/schtasks)

Options:
  -h, --help  Display help for command

Commands:
  help        Display help for command
  install     Install the Gateway service (launchd/systemd/schtasks)
  restart     Restart the Gateway service (launchd/systemd/schtasks)
  start       Start the Gateway service (launchd/systemd/schtasks)
  status      Show service install status + probe connectivity/capability
  stop        Stop the Gateway service (launchd/systemd/schtasks)
  uninstall   Uninstall the Gateway service (launchd/systemd/schtasks)

Docs: https://docs.openclaw.ai/cli/gateway
```

## `openclaw dashboard`

```text
OpenClaw 2026.7.1-2 (0790d9f) — All your chats, one OpenClaw.

Usage: openclaw dashboard [options]

Open the Control UI with your current token

Options:
  -h, --help  Display help for command
  --no-open   Print URL but do not launch a browser
  --yes       Start/install the gateway without prompting when needed (default:
              false)

Docs: https://docs.openclaw.ai/cli/dashboard
```

## `openclaw devices`

```text
OpenClaw 2026.7.1-2 (0790d9f) — All your chats, one OpenClaw.

Usage: openclaw devices [options] [command]

Device pairing and auth tokens

Options:
  -h, --help  Display help for command

Commands:
  approve     Approve a pending device pairing request
  clear       Clear paired devices from the gateway table
  list        List pending and paired devices
  reject      Reject a pending device pairing request
  remove      Remove a paired device entry
  revoke      Revoke a device token for a role
  rotate      Rotate a device token for a role
```

## `openclaw directory`

```text
OpenClaw 2026.7.1-2 (0790d9f) — All your chats, one OpenClaw.

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

```text
OpenClaw 2026.7.1-2 (0790d9f) — All your chats, one OpenClaw.

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

```text
OpenClaw 2026.7.1-2 (0790d9f) — All your chats, one OpenClaw.

Usage: openclaw docs [options] [query...]

Search the live OpenClaw docs

Arguments:
  query       Search query

Options:
  -h, --help  Display help for command

Docs: https://docs.openclaw.ai/cli/docs
```

## `openclaw doctor`

```text
OpenClaw 2026.7.1-2 (0790d9f) — All your chats, one OpenClaw.

Usage: openclaw doctor [options]

Health checks + quick fixes for the gateway and channels

Options:
  --all                       With --lint: run all registered checks, including
                              opt-in checks (default: false)
  --allow-exec                Allow doctor to execute exec SecretRefs while
                              verifying configured secrets (default: false)
  --deep                      Scan system services for extra gateway installs
                              (default: false)
  --fix                       Apply recommended repairs (alias for --repair)
                              (default: false)
  --force                     Apply aggressive repairs (overwrites custom
                              service config) (default: false)
  --generate-gateway-token    Generate and configure a gateway token (default:
                              false)
  -h, --help                  Display help for command
  --json                      With --lint or --post-upgrade: emit
                              machine-readable JSON output (default: false)
  --lint                      Run read-only health checks and report findings
                              (default: false)
  --no-workspace-suggestions  Disable workspace memory system suggestions
  --non-interactive           Run without prompts (safe migrations only)
                              (default: false)
  --only <id>                 With --lint: run only the specified check id
                              (repeatable) (default: [])
  --post-upgrade              Emit plugin-compat findings only (machine-readable
                              with --json) (default: false)
  --repair                    Apply recommended repairs without prompting
                              (default: false)
  --severity-min <level>      With --lint: drop findings below this severity
                              (info|warning|error)
  --skip <id>                 With --lint: skip a specific check id (repeatable)
                              (default: [])
  --yes                       Accept defaults without prompting (default: false)

Docs: https://docs.openclaw.ai/cli/doctor
```

## `openclaw exec-approvals`

```text
OpenClaw 2026.7.1-2 (0790d9f) — All your chats, one OpenClaw.

Usage: openclaw approvals|exec-approvals [options] [command]

Manage exec approvals (gateway or node host)

Options:
  -h, --help  Display help for command

Commands:
  allowlist   Edit the per-agent allowlist
  get         Fetch exec approvals snapshot
  set         Replace exec approvals with a JSON file

Docs: https://docs.openclaw.ai/cli/approvals
```

## `openclaw exec-policy`

```text
OpenClaw 2026.7.1-2 (0790d9f) — All your chats, one OpenClaw.

Usage: openclaw exec-policy [options] [command]

Show or synchronize requested exec policy with host approvals

Options:
  -h, --help  Display help for command

Commands:
  help        Display help for command
  preset      Apply a synchronized preset: "yolo", "cautious", or "deny-all"
  set         Synchronize local config and host approvals using explicit values
  show        Show the local config policy, host approvals, and effective merge

Docs: https://docs.openclaw.ai/cli/approvals
```

## `openclaw gateway`

```text
OpenClaw 2026.7.1-2 (0790d9f) — All your chats, one OpenClaw.

Usage: openclaw gateway [options] [command]

Run, inspect, and query the WebSocket Gateway

Options:
  --allow-unconfigured       Allow gateway start without enforcing
                             gateway.mode=local in config (does not repair
                             config) (default: false)
  --auth <mode>              Gateway auth mode
                             ("none"|"token"|"password"|"trusted-proxy")
  --bind <mode>              Bind mode
                             ("loopback"|"lan"|"tailnet"|"auto"|"custom").
                             Defaults to config gateway.bind (or loopback).
  --claude-cli-logs          Deprecated alias for --cli-backend-logs (default:
                             false)
  --cli-backend-logs         Only show CLI backend logs in the console (includes
                             stdout/stderr) (default: false)
  --compact                  Alias for "--ws-log compact" (default: false)
  --dev                      Create a dev config + workspace if missing (no
                             BOOTSTRAP.md) (default: false)
  --force                    Kill any existing listener on the target port
                             before starting (default: false)
  -h, --help                 Display help for command
  --password <password>      Password for auth mode=password
  --password-file <path>     Read gateway password from file
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
  diagnostics                Export local support diagnostics
  discover                   Discover gateways via Bonjour (local + wide-area if
                             configured)
  health                     Fetch Gateway health
  install                    Install the Gateway service
                             (launchd/systemd/schtasks)
  probe                      Show gateway reachability, auth capability, and
                             read-probe summary (local + remote)
  restart                    Restart the Gateway service
                             (launchd/systemd/schtasks)
  run                        Run the WebSocket Gateway (foreground)
  stability                  Fetch payload-free Gateway stability diagnostics
  start                      Start the Gateway service
                             (launchd/systemd/schtasks)
  status                     Show gateway service status + probe
                             connectivity/capability
  stop                       Stop the Gateway service (launchd/systemd/schtasks)
  uninstall                  Uninstall the Gateway service
                             (launchd/systemd/schtasks)
  usage-cost                 Fetch usage cost summary from session logs

Examples:
  openclaw gateway run
    Run the gateway in the foreground.
  openclaw gateway status
    Show service status plus connectivity/capability.
  openclaw gateway discover
    Find local and wide-area gateway beacons.
  openclaw gateway stability
    Show recent stability diagnostics.
  openclaw gateway call health
    Call a gateway RPC method directly.

Docs: https://docs.openclaw.ai/cli/gateway
```

## `openclaw health`

```text
OpenClaw 2026.7.1-2 (0790d9f) — All your chats, one OpenClaw.

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

## `openclaw help`

```text
OpenClaw 2026.7.1-2 (0790d9f) — All your chats, one OpenClaw.

Usage: openclaw [options] [command]

Options:
  --container <name>   Run the CLI inside a running Podman/Docker container
                       named <name> (default: env OPENCLAW_CONTAINER)
  --dev                Dev profile: isolate state under ~/.openclaw-dev, default
                       gateway port 19001, and shift derived ports
                       (browser/canvas)
  -h, --help           Display help for command
  --log-level <level>  Global log level override for file + console
                       (silent|fatal|error|warn|info|debug|trace)
  --no-color           Disable ANSI colors
  --profile <name>     Use a named profile (isolates
                       OPENCLAW_STATE_DIR/OPENCLAW_CONFIG_PATH under
                       ~/.openclaw-<name>)
  -V, --version        output the version number

Commands:
  Hint: commands suffixed with * have subcommands. Run <command> --help for details.
  acp *                Run an ACP bridge backed by the Gateway
  agent                Run an agent turn via the Gateway (use --local for
                       embedded)
  agents *             Manage isolated agents (workspaces + auth + routing)
  approvals *          Manage exec approvals (gateway or node host)
  attach               Attach Claude Code to a gateway session with scoped MCP
                       tools
  audit                Inspect metadata-only agent run and tool action records
  backup *             Create and verify local backup archives for OpenClaw
                       state
  capability *         Run provider capability commands (fallback alias: infer)
  channels *           Manage connected chat channels and accounts
  chat                 Open a local terminal UI (alias for tui --local)
  clawbot *            Legacy clawbot command aliases
  commitments *        List and manage inferred follow-up commitments
  completion           Generate shell completion script
  config *             Non-interactive config helpers
                       (get/set/patch/unset/file/schema/validate). Run without
                       subcommand for guided setup.
  configure            Interactive configuration for credentials, channels,
                       gateway, and agent defaults
  crestodian           Open the ring-zero setup and repair helper
  cron *               Manage cron jobs (via Gateway)
  daemon *             Manage the Gateway service (launchd/systemd/schtasks)
  dashboard            Open the Control UI with your current token
  devices *            Device pairing and auth tokens
  directory *          Lookup contact and group IDs (self, peers, groups) for
                       supported chat channels
  dns *                DNS helpers for wide-area discovery (Tailscale + CoreDNS)
  docs                 Search the live OpenClaw docs
  doctor               Health checks + quick fixes for the gateway and channels
  exec-approvals *     Manage exec approvals (alias for approvals)
  exec-policy *        Show or synchronize requested exec policy with host
                       approvals
  gateway *            Run, inspect, and query the WebSocket Gateway
  health               Fetch health from the running gateway
  help                 Display help for command
  hooks *              Manage internal agent hooks
  infer *              Run provider-backed inference commands through a stable
                       CLI surface
  logs                 Tail gateway file logs via RPC
  mcp *                Manage OpenClaw mcp.servers config and channel bridge
  memory *             Search, inspect, and reindex memory files
  message *            Send, read, and manage messages and channel actions
  migrate *            Import state from another agent system
  models *             Model discovery, scanning, and configuration
  node *               Run and manage the headless node host service
  nodes *              Manage gateway-owned nodes (pairing, status, invoke, and
                       media)
  onboard              Guided setup for auth, models, Gateway, workspace,
                       channels, and skills
  pairing *            Secure DM pairing (approve inbound requests)
  plugins *            Manage OpenClaw plugins and extensions
  promos *             Discover and claim promotional model offers from ClawHub
  proxy *              Run the OpenClaw debug proxy and inspect captured traffic
  qr                   Generate a mobile pairing QR code and setup code
  reset                Reset local config/state (keeps the CLI installed)
  sandbox *            Manage sandbox containers (Docker-based agent isolation)
  secrets *            Secrets runtime controls
  security *           Audit local config and state for common security
                       foot-guns
  sessions *           List stored conversation sessions
  setup                Alias for openclaw onboard
  skills *             List and inspect available skills
  status               Show channel health and recent session recipients
  system *             System tools (events, heartbeat, presence)
  tasks *              Inspect durable background tasks and TaskFlow state
  terminal             Open a local terminal UI (alias for tui --local)
  transcripts *        Inspect stored transcripts
  tui                  Open a terminal UI connected to the Gateway
  uninstall            Uninstall the gateway service + local data (CLI remains)
  update *             Update OpenClaw and inspect update channel status
  webhooks *           Webhook helpers and integrations
  worktrees *          Create, inspect, restore, and clean up managed worktrees

Examples:
  openclaw onboard
    Run guided setup for a local Gateway, workspace, auth, and channels.
  openclaw setup
    Create the baseline config, workspace, and session folders.
  openclaw configure
    Change models, Gateway, channels, plugins, skills, and health checks.
  openclaw status
    Check Gateway, channel, model, and recent-session status.
  openclaw doctor --fix
    Repair common config, service, plugin, and channel problems.
  openclaw channels add
    Add or update a chat channel account with guided prompts.
  openclaw channels status
    See connected messaging accounts and login state.
  openclaw --dev gateway
    Run a dev Gateway (isolated state/config) on ws://127.0.0.1:19001.
  openclaw gateway run --force
    Start the Gateway and replace anything bound to its port.
  openclaw models status
    Show model/provider auth health before running agents.
  openclaw plugins list
    Inspect enabled, disabled, and installed plugins.
  openclaw agent --to +15555550123 --message "Run summary" --deliver
    Run one agent turn through the Gateway and optionally deliver the reply.
  openclaw message send --channel telegram --target @mychat --message "Hi"
    Send via your Telegram bot.

Docs: https://docs.openclaw.ai/cli
```

## `openclaw hooks`

```text
OpenClaw 2026.7.1-2 (0790d9f) — All your chats, one OpenClaw.

Usage: openclaw hooks [options] [command]

Manage internal agent hooks

Options:
  -h, --help  Display help for command

Commands:
  check       Check hooks eligibility status
  disable     Disable a hook
  enable      Enable a hook
  info        Show detailed information about a hook
  install     Deprecated: install a hook pack via `openclaw plugins install`
  list        List all hooks
  update      Deprecated: update hook packs via `openclaw plugins update`

Docs: https://docs.openclaw.ai/cli/hooks
```

## `openclaw infer`

```text
OpenClaw 2026.7.1-2 (0790d9f) — All your chats, one OpenClaw.

Usage: openclaw infer|capability [options] [command]

Run provider-backed inference commands through a stable CLI surface

Options:
  -h, --help  Display help for command

Commands:
  audio       Audio transcription
  embedding   Embedding providers
  help        Display help for command
  image       Image generation and description
  inspect     Inspect one canonical capability id
  list        List canonical capability ids and supported transports
  model       Text inference and model catalog commands
  tts         Text to speech
  video       Video generation and description
  web         Web capabilities

Docs: https://docs.openclaw.ai/cli/infer
```

## `openclaw logs`

```text
OpenClaw 2026.7.1-2 (0790d9f) — All your chats, one OpenClaw.

Usage: openclaw logs [options]

Tail gateway file logs via RPC

Options:
  --expect-final   Wait for final response (agent) (default: false)
  --follow         Follow log output (default: false)
  -h, --help       Display help for command
  --interval <ms>  Polling interval in ms (default: "1000")
  --json           Emit JSON log lines (default: false)
  --limit <n>      Max lines to return (default: "200")
  --local-time     Display timestamps in local timezone (default) (default:
                   false)
  --max-bytes <n>  Max bytes to read (default: "250000")
  --no-color       Disable ANSI colors
  --plain          Plain text output (no ANSI styling) (default: false)
  --timeout <ms>   Timeout in ms (default: "30000")
  --token <token>  Gateway token (if required)
  --url <url>      Gateway WebSocket URL (defaults to gateway.remote.url when
                   configured)
  --utc            Display timestamps in UTC (default: false)

Docs: https://docs.openclaw.ai/cli/logs
```

## `openclaw mcp`

```text
OpenClaw 2026.7.1-2 (0790d9f) — All your chats, one OpenClaw.

Usage: openclaw mcp [options] [command]

Manage OpenClaw mcp.servers config and channel bridge

Options:
  -h, --help  Display help for command

Commands:
  add         Add one MCP server from flags and probe it before saving
  configure   Update MCP server operator controls without replacing the server
  doctor      Check configured MCP servers for static setup problems
  list        List OpenClaw-managed MCP servers from mcp.servers
  login       Authorize an OAuth MCP server
  logout      Clear stored OAuth credentials for an MCP server
  probe       Connect to configured MCP servers and list available capabilities
  reload      Dispose cached MCP runtimes so new config is used on the next turn
  serve       Expose OpenClaw channels over MCP stdio
  set         Set one OpenClaw-managed MCP server from a JSON object
  show        Show one OpenClaw-managed MCP server or the full mcp.servers
              config
  status      Show configured MCP server transport status without connecting
  tools       Update per-server MCP tool include/exclude filters
  unset       Remove one OpenClaw-managed MCP server
```

## `openclaw memory`

```text
OpenClaw 2026.7.1-2 (0790d9f) — All your chats, one OpenClaw.

Usage: openclaw memory [options] [command]

Search, inspect, and reindex memory files

Options:
  -h, --help       Display help for command

Commands:
  index            Reindex memory files
  promote          Rank short-term recalls and optionally append top entries to
                   MEMORY.md
  promote-explain  Explain a specific promotion candidate and its score
                   breakdown
  rem-backfill     Write grounded historical REM summaries into DREAMS.md for UI
                   review
  rem-harness      Preview REM reflections, candidate truths, and deep
                   promotions without writing
  search           Search memory files
  status           Show memory search index status

Examples:
  openclaw memory status
    Show index and provider status.
  openclaw memory status --fix
    Repair stale recall locks and normalize promotion metadata.
  openclaw memory status --deep
    Probe embedding provider readiness.
  openclaw memory index --force
    Force a full reindex.
  openclaw memory search "meeting notes"
    Quick search using positional query.
  openclaw memory search --query "deployment" --max-results 20
    Limit results for focused troubleshooting.
  openclaw memory promote --limit 10 --min-score 0.75
    Review weighted short-term candidates for long-term memory.
  openclaw memory promote --apply
    Append top-ranked short-term candidates into MEMORY.md.
  openclaw memory promote-explain "router vlan"
    Explain why a specific candidate would or would not promote.
  openclaw memory rem-harness --json
    Preview REM reflections, candidate truths, and deep promotion output.
  openclaw memory rem-backfill --path ./memory
    Write grounded historical REM entries into DREAMS.md for UI review.
  openclaw memory rem-backfill --path ./memory --stage-short-term
    Also seed durable grounded candidates into the live short-term promotion store.
  openclaw memory status --json
    Output machine-readable JSON (good for scripts).

Docs: https://docs.openclaw.ai/cli/memory
```

## `openclaw message`

```text
OpenClaw 2026.7.1-2 (0790d9f) — All your chats, one OpenClaw.

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

## `openclaw migrate`

```text
OpenClaw 2026.7.1-2 (0790d9f) — All your chats, one OpenClaw.

Usage: openclaw migrate [options] [command] [provider]

Import state from another agent system

Arguments:
  provider                Migration provider id, for example hermes

Options:
  --backup-output <path>  Pre-migration backup archive path or directory
  --dry-run               Preview only; do not apply changes (default: false)
  --force                 Allow dangerous options such as --no-backup (default:
                          false)
  --from <path>           Source directory to migrate from
  -h, --help              Display help for command
  --include-secrets       Import supported credentials and secrets
  --json                  Output JSON (default: false)
  --no-auth-credentials   Skip auth credential migration
  --no-backup             Skip the pre-migration OpenClaw backup
  --overwrite             Overwrite conflicting target files after item-level
                          backups (default: false)
  --plugin <name>         Select one Codex plugin to migrate by name or item id;
                          repeat for multiple plugins
  --skill <name>          Select one skill to migrate by name or item id; repeat
                          for multiple skills
  --verify-plugin-apps    Codex only: verify source plugin app accessibility
                          with app/list before planning native plugin activation
                          (default: false)
  --yes                   Apply without prompting after preview (default: false)

Commands:
  apply                   Apply a migration after a verified backup
  list                    List migration providers
  plan                    Preview a migration without changing OpenClaw state

Examples:
  openclaw migrate list
    Show available migration providers.
  openclaw migrate hermes
    Preview Hermes migration, then prompt before applying.
  openclaw migrate hermes --dry-run
    Preview Hermes migration only.
  openclaw migrate apply hermes --yes
    Apply Hermes migration non-interactively after writing a verified backup.
  openclaw migrate hermes --no-auth-credentials
    Preview and apply Hermes migration while skipping auth credential import.
```

## `openclaw models`

```text
OpenClaw 2026.7.1-2 (0790d9f) — All your chats, one OpenClaw.

Usage: openclaw models [options] [command]

Model discovery, scanning, and configuration

Options:
  --agent <id>     Agent id to inspect (overrides OPENCLAW_AGENT_DIR)
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

```text
OpenClaw 2026.7.1-2 (0790d9f) — All your chats, one OpenClaw.

Usage: openclaw node [options] [command]

Run and manage the headless node host service

Options:
  -h, --help  Display help for command

Commands:
  help        Display help for command
  install     Install the node host service (launchd/systemd/schtasks)
  restart     Restart the node host service (launchd/systemd/schtasks)
  run         Run the headless node host (foreground)
  start       Start the node host service (launchd/systemd/schtasks)
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
  openclaw node start
    Start the installed node host service.
  openclaw node restart
    Restart the installed node host service.

Docs: https://docs.openclaw.ai/cli/node
```

## `openclaw nodes`

```text
OpenClaw 2026.7.1-2 (0790d9f) — All your chats, one OpenClaw.

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
  remove      Remove a paired node entry
  rename      Rename a paired node (display name override)
  screen      Capture screen recordings from a paired node
  status      List known nodes with connection status and capabilities

Examples:
  openclaw nodes status
    List known nodes with live status.
  openclaw nodes pairing pending
    Show pending node pairing requests.
  openclaw nodes remove --node <id|name|ip>
    Remove a stale paired node entry.
  openclaw nodes invoke --node <id> --command system.which --params '{"name":"uname"}'
    Invoke a node command directly.
  openclaw nodes camera snap --node <id>
    Capture a photo from a node camera.

Docs: https://docs.openclaw.ai/cli/nodes
```

## `openclaw onboard`

```text
OpenClaw 2026.7.1-2 (0790d9f) — All your chats, one OpenClaw.

Usage: openclaw onboard [options]

Guided setup for auth, models, Gateway, workspace, channels, and skills

Options:
  --accept-risk                            Acknowledge that agents are powerful and full system access is risky (required for --non-interactive) (default: false)
  --ai-gateway-api-key <key>               Vercel AI Gateway API key
  --alibaba-model-studio-api-key <key>     Alibaba Model Studio API key
  --anthropic-api-key <key>                Anthropic API key
  --arceeai-api-key <key>                  Arcee AI API key
  --auth-choice <choice>                   Auth: custom-api-key|skip|claude-cli|apiKey|anthropic-cli|setup-token|arceeai-api-key|brave-api-key|byteplus-api-key|cerebras-api-key|openai-device-code|openai|chutes|chutes-api-key|clawrouter-api-key|cloudflare-ai-gateway-api-key|zai-cn|qwen-api-key-cn|qwen-api-key|zai-coding-cn|zai-coding-global|cohere-api-key|copilot-proxy|deepinfra-api-key|deepseek-api-key|featherless-api-key|fireworks-api-key|google-gemini-cli|github-copilot|zai-global|gmi-api-key|gemini-api-key|google-vertex-api-key|groq-api-key|huggingface-api-key|kilocode-api-key|kimi-code-api-key|litellm-api-key|lmstudio|longcat-api-key|meta-api-key|microsoft-foundry-apikey|microsoft-foundry-entra|minimax-cn-api|minimax-global-api|minimax-cn-oauth|minimax-global-oauth|mistral-api-key|moonshot-api-key|moonshot-api-key-cn|novita-api-key|nvidia-api-key|ollama|ollama-cloud|openai-api-key|opencode-go|opencode-zen|arceeai-openrouter|openrouter-api-key|openrouter-oauth|qianfan-api-key|qwen-oauth|sglang|qwen-standard-api-key-cn|qwen-standard-api-key|stepfun-standard-api-key-cn|stepfun-standard-api-key-intl|stepfun-plan-api-key-cn|stepfun-plan-api-key-intl|synthetic-api-key|tokenhub-api-key|tokenplan-api-key|together-api-key|venice-api-key|ai-gateway-api-key|vllm|volcengine-api-key|xai-api-key|xai-device-code|xai-oauth|xiaomi-api-key|xiaomi-token-plan-cn|xiaomi-token-plan-ams|xiaomi-token-plan-sgp|zai-api-key
  --byteplus-api-key <key>                 BytePlus API key
  --cerebras-api-key <key>                 Cerebras API key
  --chutes-api-key <key>                   Chutes API key
  --classic                                Use the classic multi-step setup wizard (default: false)
  --clawrouter-api-key <key>               ClawRouter proxy key
  --cloudflare-ai-gateway-account-id <id>  Cloudflare Account ID
  --cloudflare-ai-gateway-api-key <key>    Cloudflare AI Gateway API key
  --cloudflare-ai-gateway-gateway-id <id>  Cloudflare AI Gateway ID
  --cohere-api-key <key>                   Cohere API key
  --comfy-api-key <key>                    Comfy Cloud API key
  --custom-api-key <key>                   Custom provider API key (optional)
  --custom-base-url <url>                  Custom provider base URL
  --custom-compatibility <mode>            Custom provider API compatibility: openai|openai-responses|anthropic (default: openai)
  --custom-image-input                     Mark the custom provider model as image-capable
  --custom-model-id <id>                   Custom provider model ID
  --custom-provider-id <id>                Custom provider ID (optional; auto-derived by default)
  --custom-text-input                      Mark the custom provider model as text-only
  --daemon-runtime <runtime>               Daemon runtime: node
  --deepinfra-api-key <key>                DeepInfra API key
  --deepseek-api-key <key>                 DeepSeek API key
  --fal-api-key <key>                      fal API key
  --featherless-api-key <key>              Featherless AI API key
  --fireworks-api-key <key>                Fireworks API key
  --flow <flow>                            Onboard flow: quickstart|advanced|manual|import
  --gateway-auth <mode>                    Gateway auth: token|password
  --gateway-bind <mode>                    Gateway bind: loopback|tailnet|lan|auto|custom
  --gateway-password <password>            Gateway password (password auth)
  --gateway-port <port>                    Gateway port
  --gateway-token <token>                  Gateway token (token auth)
  --gateway-token-ref-env <name>           Gateway token SecretRef env var name (token auth; e.g. OPENCLAW_GATEWAY_TOKEN)
  --gemini-api-key <key>                   Gemini API key
  --github-copilot-token <token>           GitHub Copilot OAuth token
  --gmi-api-key <key>                      GMI Cloud API key
  --groq-api-key <key>                     Groq API key
  -h, --help                               Display help for command
  --huggingface-api-key <key>              Hugging Face API key (HF token)
  --import-from <provider>                 Migration provider to run during onboarding
  --import-secrets                         Import supported secrets during onboarding migration (default: false)
  --import-source <path>                   Source agent home for --import-from
  --install-daemon                         Install gateway service
  --json                                   Output JSON summary (default: false)
  --kilocode-api-key <key>                 Kilo Gateway API key
  --kimi-code-api-key <key>                Kimi Code API key (subscription)
  --litellm-api-key <key>                  LiteLLM API key
  --lmstudio-api-key <key>                 LM Studio API key
  --longcat-api-key <key>                  LongCat API key
  --meta-api-key <key>                     Meta API key
  --minimax-api-key <key>                  MiniMax API key
  --mistral-api-key <key>                  Mistral API key
  --mode <mode>                            Onboard mode: local|remote
  --modelstudio-api-key <key>              Qwen Cloud Coding Plan API key (Global/Intl)
  --modelstudio-api-key-cn <key>           Qwen Cloud Coding Plan API key (China)
  --modelstudio-standard-api-key <key>     Qwen Cloud standard API key (Global/Intl)
  --modelstudio-standard-api-key-cn <key>  Qwen Cloud standard API key (China)
  --modern                                 Alias for the default bootstrap onboarding (kept for compatibility) (default: false)
  --moonshot-api-key <key>                 Moonshot API key
  --no-install-daemon                      Skip gateway service install
  --node-manager <name>                    Node manager for skills: npm|pnpm|bun
  --non-interactive                        Run without prompts (default: false)
  --novita-api-key <key>                   NovitaAI API key
  --nvidia-api-key <key>                   NVIDIA API key
  --ollama-cloud-api-key <key>             Ollama Cloud API key
  --openai-api-key <key>                   OpenAI API Key
  --opencode-go-api-key <key>              OpenCode API key (Go catalog)
  --opencode-zen-api-key <key>             OpenCode API key (Zen catalog)
  --openrouter-api-key <key>               OpenRouter API key
  --pixverse-api-key <key>                 PixVerse API key
  --qianfan-api-key <key>                  QIANFAN API key
  --qwen-oauth-token <token>               Qwen OAuth token
  --remote-token <token>                   Remote Gateway token (optional)
  --remote-url <url>                       Remote Gateway WebSocket URL
  --reset                                  Reset config + credentials + sessions before running onboard (workspace only with --reset-scope full)
  --reset-scope <scope>                    Reset scope: config|config+creds+sessions|full
  --runway-api-key <key>                   Runway API key
  --secret-input-mode <mode>               API key persistence mode: plaintext|ref (default: plaintext)
  --skip-bootstrap                         Skip creating default agent workspace files
  --skip-channels                          Skip channel setup
  --skip-daemon                            Skip gateway service install
  --skip-health                            Skip health check
  --skip-hooks                             Skip hook setup
  --skip-search                            Skip search provider setup
  --skip-skills                            Skip skills setup
  --skip-ui                                Skip Control UI/TUI prompts
  --stepfun-api-key <key>                  StepFun API key
  --suppress-gateway-token-output          Suppress token-bearing Gateway/UI output
  --synthetic-api-key <key>                Synthetic API key
  --tailscale <mode>                       Tailscale: off|serve|funnel
  --tailscale-reset-on-exit                Reset tailscale serve/funnel on exit
  --together-api-key <key>                 Together AI API key
  --token <token>                          Token value (non-interactive; used with --auth-choice token)
  --token-expires-in <duration>            Optional token expiry duration (e.g. 365d, 12h)
  --token-profile-id <id>                  Auth profile id (non-interactive; default: <provider>:manual)
  --token-provider <id>                    Token provider id (non-interactive; used with --auth-choice token)
  --tokenhub-api-key <key>                 Tencent TokenHub API key
  --tokenplan-api-key <key>                Tencent TokenPlan API key
  --venice-api-key <key>                   Venice API key
  --volcengine-api-key <key>               Volcano Engine API key
  --vydra-api-key <key>                    Vydra API key
  --workspace <dir>                        Agent workspace directory (default: ~/.openclaw/workspace)
  --xai-api-key <key>                      xAI API key
  --xiaomi-api-key <key>                   Xiaomi MiMo pay-as-you-go API key
  --xiaomi-token-plan-api-key <key>        Xiaomi MiMo Token Plan API key
  --zai-api-key <key>                      Z.AI API key

Docs: https://docs.openclaw.ai/cli/onboard
```

## `openclaw pairing`

```text
OpenClaw 2026.7.1-2 (0790d9f) — All your chats, one OpenClaw.

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

```text
OpenClaw 2026.7.1-2 (0790d9f) — All your chats, one OpenClaw.

Usage: openclaw plugins [options] [command]

Manage OpenClaw plugins and extensions

Options:
  -h, --help   Display help for command

Commands:
  build        Generate simple tool plugin metadata
  disable      Disable a plugin in config
  doctor       Report plugin load issues
  enable       Enable a plugin in config
  init         Create a plugin project
  inspect      Inspect plugin details
  install      Install a plugin or hook pack (path, archive, npm spec, git repo,
               clawhub:package, or marketplace entry)
  list         List discovered plugins
  marketplace  Inspect Claude-compatible plugin marketplaces
  registry     Inspect or rebuild the persisted plugin registry
  search       Search ClawHub plugin packages
  uninstall    Uninstall a plugin
  update       Update installed plugins and tracked hook packs
  validate     Validate simple tool plugin metadata

Docs: https://docs.openclaw.ai/cli/plugins
```

## `openclaw promos`

```text
OpenClaw 2026.7.1-2 (0790d9f) — All your chats, one OpenClaw.

Usage: openclaw promos [options] [command]

Discover and claim promotional model offers from ClawHub

Options:
  -h, --help  Display help for command

Commands:
  claim       Claim a promotion: set up provider auth and register its models
  help        Display help for command
  list        List active promotions

Docs: https://docs.openclaw.ai/cli/promos
```

## `openclaw proxy`

```text
OpenClaw 2026.7.1-2 (0790d9f) — All your chats, one OpenClaw.

Usage: openclaw proxy [options] [command]

Run the OpenClaw debug proxy and inspect captured traffic

Options:
  -h, --help  Display help for command

Commands:
  blob        Read a captured payload blob by id
  coverage    Report current debug proxy transport coverage and remaining gaps
  help        Display help for command
  purge       Delete all captured traffic metadata and blobs
  query       Run a built-in query preset against captured traffic
  run         Run a child command with OpenClaw debug proxy capture enabled
  sessions    List recent capture sessions
  start       Start the local explicit debug proxy
  validate    Validate the operator-managed network proxy
```

## `openclaw qr`

```text
OpenClaw 2026.7.1-2 (0790d9f) — All your chats, one OpenClaw.

Usage: openclaw qr [options]

Generate a mobile pairing QR code and setup code

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

Docs: https://docs.openclaw.ai/cli/qr
```

## `openclaw reset`

```text
OpenClaw 2026.7.1-2 (0790d9f) — All your chats, one OpenClaw.

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

```text
OpenClaw 2026.7.1-2 (0790d9f) — All your chats, one OpenClaw.

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

## `openclaw secrets`

```text
OpenClaw 2026.7.1-2 (0790d9f) — All your chats, one OpenClaw.

Usage: openclaw secrets [options] [command]

Secrets runtime controls

Options:
  -h, --help  Display help for command

Commands:
  apply       Apply a previously generated secrets plan
  audit       Audit plaintext secrets, unresolved refs, and precedence drift
  configure   Interactive secrets helper (provider setup + SecretRef mapping +
              preflight)
  help        Display help for command
  reload      Re-resolve secret references and atomically swap runtime snapshot

Docs: https://docs.openclaw.ai/gateway/security
```

## `openclaw security`

```text
OpenClaw 2026.7.1-2 (0790d9f) — All your chats, one OpenClaw.

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
    Include best-effort live Gateway probes and plugin-owned security audit collectors.
  openclaw security audit --deep --token <token>
    Use explicit token for deep probe.
  openclaw security audit --deep --password <password>
    Use explicit password for deep probe.
  openclaw security audit --auth password --password <password>
    Audit a runtime-only password-mode Gateway secret.
  openclaw security audit --fix
    Apply safe remediations and file-permission fixes.
  openclaw security audit --json
    Output machine-readable JSON.

Docs: https://docs.openclaw.ai/cli/security
```

## `openclaw sessions`

```text
OpenClaw 2026.7.1-2 (0790d9f) — All your chats, one OpenClaw.

Usage: openclaw sessions [options] [command]

List stored conversation sessions

Options:
  --active <minutes>  Only show sessions updated within the past N minutes
  --agent <id>        Agent id to inspect (default: configured default agent)
  --all-agents        Aggregate sessions across all configured agents (default:
                      false)
  -h, --help          Display help for command
  --json              Output as JSON (default: false)
  --limit <count>     Max sessions to show (default: 100; use "all" for full
                      output)
  --store <path>      Path to session store (default: resolved from config)
  --verbose           Verbose logging (default: false)

Commands:
  cleanup             Run session-store maintenance now
  compact             Compact a stored session transcript via the running
                      gateway
  export-trajectory   Export a redacted trajectory bundle for a stored session
  list                List stored conversation sessions
  tail                Tail human-readable session trajectory progress

Examples:
  openclaw sessions
    List all sessions.
  openclaw sessions --agent work
    List sessions for one agent.
  openclaw sessions --all-agents
    Aggregate sessions across agents.
  openclaw sessions --active 120
    Only last 2 hours.
  openclaw sessions --limit 25
    Show the newest 25 sessions.
  openclaw sessions --json
    Machine-readable output.
  openclaw sessions --store ./tmp/sessions.json
    Use a specific session store.

Shows token usage per session when the agent reports it; set agents.defaults.contextTokens to cap the window and show %.

Docs: https://docs.openclaw.ai/cli/sessions
```

## `openclaw setup`

```text
OpenClaw 2026.7.1-2 (0790d9f) — All your chats, one OpenClaw.

Usage: openclaw setup [options]

Alias for openclaw onboard

Options:
  --accept-risk                            Acknowledge that agents are powerful and full system access is risky (required for --non-interactive) (default: false)
  --ai-gateway-api-key <key>               Vercel AI Gateway API key
  --alibaba-model-studio-api-key <key>     Alibaba Model Studio API key
  --anthropic-api-key <key>                Anthropic API key
  --arceeai-api-key <key>                  Arcee AI API key
  --auth-choice <choice>                   Auth: custom-api-key|skip|claude-cli|apiKey|anthropic-cli|setup-token|arceeai-api-key|brave-api-key|byteplus-api-key|cerebras-api-key|openai-device-code|openai|chutes|chutes-api-key|clawrouter-api-key|cloudflare-ai-gateway-api-key|zai-cn|qwen-api-key-cn|qwen-api-key|zai-coding-cn|zai-coding-global|cohere-api-key|copilot-proxy|deepinfra-api-key|deepseek-api-key|featherless-api-key|fireworks-api-key|google-gemini-cli|github-copilot|zai-global|gmi-api-key|gemini-api-key|google-vertex-api-key|groq-api-key|huggingface-api-key|kilocode-api-key|kimi-code-api-key|litellm-api-key|lmstudio|longcat-api-key|meta-api-key|microsoft-foundry-apikey|microsoft-foundry-entra|minimax-cn-api|minimax-global-api|minimax-cn-oauth|minimax-global-oauth|mistral-api-key|moonshot-api-key|moonshot-api-key-cn|novita-api-key|nvidia-api-key|ollama|ollama-cloud|openai-api-key|opencode-go|opencode-zen|arceeai-openrouter|openrouter-api-key|openrouter-oauth|qianfan-api-key|qwen-oauth|sglang|qwen-standard-api-key-cn|qwen-standard-api-key|stepfun-standard-api-key-cn|stepfun-standard-api-key-intl|stepfun-plan-api-key-cn|stepfun-plan-api-key-intl|synthetic-api-key|tokenhub-api-key|tokenplan-api-key|together-api-key|venice-api-key|ai-gateway-api-key|vllm|volcengine-api-key|xai-api-key|xai-device-code|xai-oauth|xiaomi-api-key|xiaomi-token-plan-cn|xiaomi-token-plan-ams|xiaomi-token-plan-sgp|zai-api-key
  --baseline                               Create baseline config/workspace/session folders without onboarding (default: false)
  --byteplus-api-key <key>                 BytePlus API key
  --cerebras-api-key <key>                 Cerebras API key
  --chutes-api-key <key>                   Chutes API key
  --classic                                Use the classic multi-step setup wizard (default: false)
  --clawrouter-api-key <key>               ClawRouter proxy key
  --cloudflare-ai-gateway-account-id <id>  Cloudflare Account ID
  --cloudflare-ai-gateway-api-key <key>    Cloudflare AI Gateway API key
  --cloudflare-ai-gateway-gateway-id <id>  Cloudflare AI Gateway ID
  --cohere-api-key <key>                   Cohere API key
  --comfy-api-key <key>                    Comfy Cloud API key
  --custom-api-key <key>                   Custom provider API key (optional)
  --custom-base-url <url>                  Custom provider base URL
  --custom-compatibility <mode>            Custom provider API compatibility: openai|openai-responses|anthropic (default: openai)
  --custom-image-input                     Mark the custom provider model as image-capable
  --custom-model-id <id>                   Custom provider model ID
  --custom-provider-id <id>                Custom provider ID (optional; auto-derived by default)
  --custom-text-input                      Mark the custom provider model as text-only
  --daemon-runtime <runtime>               Daemon runtime: node
  --deepinfra-api-key <key>                DeepInfra API key
  --deepseek-api-key <key>                 DeepSeek API key
  --fal-api-key <key>                      fal API key
  --featherless-api-key <key>              Featherless AI API key
  --fireworks-api-key <key>                Fireworks API key
  --flow <flow>                            Onboard flow: quickstart|advanced|manual|import
  --gateway-auth <mode>                    Gateway auth: token|password
  --gateway-bind <mode>                    Gateway bind: loopback|tailnet|lan|auto|custom
  --gateway-password <password>            Gateway password (password auth)
  --gateway-port <port>                    Gateway port
  --gateway-token <token>                  Gateway token (token auth)
  --gateway-token-ref-env <name>           Gateway token SecretRef env var name (token auth; e.g. OPENCLAW_GATEWAY_TOKEN)
  --gemini-api-key <key>                   Gemini API key
  --github-copilot-token <token>           GitHub Copilot OAuth token
  --gmi-api-key <key>                      GMI Cloud API key
  --groq-api-key <key>                     Groq API key
  -h, --help                               Display help for command
  --huggingface-api-key <key>              Hugging Face API key (HF token)
  --import-from <provider>                 Migration provider to run during onboarding
  --import-secrets                         Import supported secrets during onboarding migration (default: false)
  --import-source <path>                   Source agent home for --import-from
  --install-daemon                         Install gateway service
  --json                                   Output JSON summary (default: false)
  --kilocode-api-key <key>                 Kilo Gateway API key
  --kimi-code-api-key <key>                Kimi Code API key (subscription)
  --litellm-api-key <key>                  LiteLLM API key
  --lmstudio-api-key <key>                 LM Studio API key
  --longcat-api-key <key>                  LongCat API key
  --meta-api-key <key>                     Meta API key
  --minimax-api-key <key>                  MiniMax API key
  --mistral-api-key <key>                  Mistral API key
  --mode <mode>                            Onboard mode: local|remote
  --modelstudio-api-key <key>              Qwen Cloud Coding Plan API key (Global/Intl)
  --modelstudio-api-key-cn <key>           Qwen Cloud Coding Plan API key (China)
  --modelstudio-standard-api-key <key>     Qwen Cloud standard API key (Global/Intl)
  --modelstudio-standard-api-key-cn <key>  Qwen Cloud standard API key (China)
  --moonshot-api-key <key>                 Moonshot API key
  --no-install-daemon                      Skip gateway service install
  --node-manager <name>                    Node manager for skills: npm|pnpm|bun
  --non-interactive                        Run onboarding without prompts (default: false)
  --novita-api-key <key>                   NovitaAI API key
  --nvidia-api-key <key>                   NVIDIA API key
  --ollama-cloud-api-key <key>             Ollama Cloud API key
  --openai-api-key <key>                   OpenAI API Key
  --opencode-go-api-key <key>              OpenCode API key (Go catalog)
  --opencode-zen-api-key <key>             OpenCode API key (Zen catalog)
  --openrouter-api-key <key>               OpenRouter API key
  --pixverse-api-key <key>                 PixVerse API key
  --qianfan-api-key <key>                  QIANFAN API key
  --qwen-oauth-token <token>               Qwen OAuth token
  --remote-token <token>                   Remote Gateway token (optional)
  --remote-url <url>                       Remote Gateway WebSocket URL
  --reset                                  Reset config + credentials + sessions before running onboarding (workspace only with --reset-scope full)
  --reset-scope <scope>                    Reset scope: config|config+creds+sessions|full
  --runway-api-key <key>                   Runway API key
  --secret-input-mode <mode>               API key persistence mode: plaintext|ref (default: plaintext)
  --skip-bootstrap                         Skip creating default agent workspace files
  --skip-channels                          Skip channel setup
  --skip-daemon                            Skip gateway service install
  --skip-health                            Skip health check
  --skip-hooks                             Accepted for onboard compatibility; hooks setup is skipped
  --skip-search                            Skip search provider setup
  --skip-skills                            Skip skills setup
  --skip-ui                                Skip Control UI/TUI launch
  --stepfun-api-key <key>                  StepFun API key
  --suppress-gateway-token-output          Suppress token-bearing Gateway/UI output
  --synthetic-api-key <key>                Synthetic API key
  --tailscale <mode>                       Tailscale: off|serve|funnel
  --tailscale-reset-on-exit                Reset tailscale serve/funnel on exit
  --together-api-key <key>                 Together AI API key
  --token <token>                          Token value (non-interactive; used with --auth-choice token)
  --token-expires-in <duration>            Optional token expiry duration (e.g. 365d, 12h)
  --token-profile-id <id>                  Auth profile id (non-interactive; default: <provider>:manual)
  --token-provider <id>                    Token provider id (non-interactive; used with --auth-choice token)
  --tokenhub-api-key <key>                 Tencent TokenHub API key
  --tokenplan-api-key <key>                Tencent TokenPlan API key
  --venice-api-key <key>                   Venice API key
  --volcengine-api-key <key>               Volcano Engine API key
  --vydra-api-key <key>                    Vydra API key
  --wizard                                 Run interactive onboarding (default: false)
  --workspace <dir>                        Agent workspace directory (default: ~/.openclaw/workspace; stored as agents.defaults.workspace)
  --xai-api-key <key>                      xAI API key
  --xiaomi-api-key <key>                   Xiaomi MiMo pay-as-you-go API key
  --xiaomi-token-plan-api-key <key>        Xiaomi MiMo Token Plan API key
  --zai-api-key <key>                      Z.AI API key

Examples:
  openclaw setup
    Run full onboarding for auth, models, Gateway, and channels.

Docs: https://docs.openclaw.ai/cli/setup
```

## `openclaw skills`

```text
OpenClaw 2026.7.1-2 (0790d9f) — All your chats, one OpenClaw.

Usage: openclaw skills [options] [command]

List and inspect available skills

Options:
  --agent <id>  Target agent workspace (defaults to cwd-inferred, then default
                agent)
  -h, --help    Display help for command

Commands:
  check         Check which skills are ready, visible, or missing requirements
  curator       Inspect and manage skill lifecycle curation
  info          Show detailed information about a skill
  install       Install a skill from ClawHub, git, or a local directory
  list          List all available skills
  search        Search ClawHub skills
  update        Update ClawHub-installed skills in the active or shared managed
                directory
  verify        Verify a ClawHub skill with ClawHub
  workshop      Manage pending skill proposals

Docs: https://docs.openclaw.ai/cli/skills
```

## `openclaw status`

```text
OpenClaw 2026.7.1-2 (0790d9f) — All your chats, one OpenClaw.

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

```text
OpenClaw 2026.7.1-2 (0790d9f) — All your chats, one OpenClaw.

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

## `openclaw tasks`

```text
OpenClaw 2026.7.1-2 (0790d9f) — All your chats, one OpenClaw.

Usage: openclaw tasks [options] [command]

Inspect durable background tasks and TaskFlow state

Options:
  -h, --help        Display help for command
  --json            Output as JSON (default: false)
  --runtime <name>  Filter by kind (subagent, acp, cron, cli)
  --status <name>   Filter by status (queued, running, succeeded, failed,
                    timed_out, cancelled, lost)

Commands:
  audit             Show stale or broken background tasks and TaskFlows
  cancel            Cancel a running background task
  flow              Inspect durable TaskFlow state under tasks
  list              List tracked background tasks
  maintenance       Preview or apply tasks and TaskFlow maintenance
  notify            Set task notify policy
  show              Show one background task by task id, run id, or session key
```

## `openclaw terminal`

```text
OpenClaw 2026.7.1-2 (0790d9f) — All your chats, one OpenClaw.

Usage: openclaw tui|terminal [options]

Open a terminal UI connected to the Gateway

Options:
  --deliver              Deliver assistant replies (default: false)
  -h, --help             Display help for command
  --history-limit <n>    History entries to load (default: "200")
  --local                Run against the local embedded agent runtime (default:
                         false)
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

## `openclaw transcripts`

```text
OpenClaw 2026.7.1-2 (0790d9f) — All your chats, one OpenClaw.

Usage: openclaw transcripts [options] [command]

Inspect stored transcripts

Options:
  -h, --help  Display help for command

Commands:
  help        Display help for command
  list        List stored transcript sessions
  path        Print a stored transcripts artifact path
  show        Print a transcript summary markdown file
```

## `openclaw tui`

```text
OpenClaw 2026.7.1-2 (0790d9f) — All your chats, one OpenClaw.

Usage: openclaw tui|terminal [options]

Open a terminal UI connected to the Gateway

Options:
  --deliver              Deliver assistant replies (default: false)
  -h, --help             Display help for command
  --history-limit <n>    History entries to load (default: "200")
  --local                Run against the local embedded agent runtime (default:
                         false)
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

```text
OpenClaw 2026.7.1-2 (0790d9f) — All your chats, one OpenClaw.

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

```text
OpenClaw 2026.7.1-2 (0790d9f) — All your chats, one OpenClaw.

Usage: openclaw update [options] [command]

Update OpenClaw and inspect update channel status

Options:
  --acknowledge-clawhub-risk                   Acknowledge ClawHub release trust warnings during post-update plugin sync (default: false)
  --channel <stable|extended-stable|beta|dev>  Persist update channel (git + npm)
  --dry-run                                    Preview update actions without making changes (default: false)
  -h, --help                                   Display help for command
  --json                                       Output result as JSON (default: false)
  --no-restart                                 Skip restarting the gateway service after a successful update
  --tag <dist-tag|version|spec>                Override the package target for this update (dist-tag, version, or package spec)
  --timeout <seconds>                          Timeout for each update step in seconds (default: 1800)
  --yes                                        Skip confirmation prompts (non-interactive) (default: false)

Commands:
  repair                                       Repair post-update doctor and plugin convergence
  status                                       Show update channel and version status
  wizard                                       Interactive update wizard

What this does:
  - Git checkouts: fetches, rebases, installs deps, builds, and runs doctor
  - npm installs: updates via detected package manager

Switch channels:
  - Use --channel stable|extended-stable|beta|dev to persist the update channel in config
  - Run openclaw update status to see the active channel and source
  - Use --tag <dist-tag|version|spec> for a one-off package update without persisting
  - Use --tag main for a one-off package update from GitHub main

Non-interactive:
  - Use --yes to accept downgrade prompts
  - Use --acknowledge-clawhub-risk only after reviewing ClawHub plugin trust warnings
  - Combine with --channel/--tag/--no-restart/--json/--timeout as needed
  - Use --dry-run to preview actions without writing config/installing/restarting

Examples:
  openclaw update # Update a source checkout (git)
  openclaw update --channel extended-stable # Switch to the monthly supported npm channel
  openclaw update --channel beta # Switch to beta channel (git + npm)
  openclaw update --channel dev # Switch to dev channel (git + npm)
  openclaw update --tag beta # One-off update to a dist-tag or version
  openclaw update --tag main # One-off package update from GitHub main
  openclaw update --dry-run # Preview actions without changing anything
  openclaw update --no-restart # Update without restarting the service
  openclaw update --json # Output result as JSON
  openclaw update --yes # Non-interactive (accept downgrade prompts)
  openclaw update repair # Repair stranded post-update plugin state
  openclaw update --acknowledge-clawhub-risk # Acknowledge ClawHub plugin trust warnings
  openclaw update wizard # Interactive update wizard
  openclaw --update # Shorthand for openclaw update

Notes:
  - Switch channels with --channel stable|extended-stable|beta|dev
  - For global installs: auto-updates via detected package manager when possible (see docs/install/updating.md)
  - Downgrades require confirmation (can break configuration)
  - Skips update if the working directory has uncommitted changes

Docs: https://docs.openclaw.ai/cli/update
```

## `openclaw webhooks`

```text
OpenClaw 2026.7.1-2 (0790d9f) — All your chats, one OpenClaw.

Usage: openclaw webhooks [options] [command]

Webhook helpers and integrations

Options:
  -h, --help  Display help for command

Commands:
  gmail       Gmail Pub/Sub hooks (via gogcli)
  help        Display help for command

Docs: https://docs.openclaw.ai/cli/webhooks
```

## `openclaw worktrees`

```text
OpenClaw 2026.7.1-2 (0790d9f) — All your chats, one OpenClaw.

Usage: openclaw worktrees [options] [command]

Create, inspect, restore, and clean up managed worktrees

Options:
  -h, --help  Display help for command

Commands:
  create      Create a managed worktree
  gc          Run managed worktree cleanup now
  list        List active and restorable managed worktrees
  remove      Snapshot and remove a managed worktree
  restore     Restore a managed worktree from its snapshot
```
