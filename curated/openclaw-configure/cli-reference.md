
🦞 OpenClaw 2026.3.13 (61d171a) — We ship features faster than Apple ships calculator updates.

Usage: openclaw [options] [command]

Options:
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
  acp *                Agent Control Protocol tools
  agent                Run one agent turn via the Gateway
  agents *             Manage isolated agents (workspaces, auth, routing)
  approvals *          Manage exec approvals (gateway or node host)
  backup *             Create and verify local backup archives for OpenClaw
                       state
  browser *            Manage OpenClaw's dedicated browser (Chrome/Chromium)
  channels *           Manage connected chat channels (Telegram, Discord, etc.)
  clawbot *            Legacy clawbot command aliases
  completion           Generate shell completion script
  config *             Non-interactive config helpers
                       (get/set/unset/file/validate). Default: starts setup
                       wizard.
  configure            Interactive setup wizard for credentials, channels,
                       gateway, and agent defaults
  cron *               Manage cron jobs via the Gateway scheduler
  daemon *             Gateway service (legacy alias)
  dashboard            Open the Control UI with your current token
  devices *            Device pairing + token management
  directory *          Lookup contact and group IDs (self, peers, groups) for
                       supported chat channels
  dns *                DNS helpers for wide-area discovery (Tailscale + CoreDNS)
  docs                 Search the live OpenClaw docs
  doctor               Health checks + quick fixes for the gateway and channels
  gateway *            Run, inspect, and query the WebSocket Gateway
  health               Fetch health from the running gateway
  help                 Display help for command
  hooks *              Manage internal agent hooks
  logs                 Tail gateway file logs via RPC
  memory *             Search and reindex memory files
  message *            Send, read, and manage messages
  models *             Discover, scan, and configure models
  node *               Run and manage the headless node host service
  nodes *              Manage gateway-owned node pairing and node commands
  onboard              Interactive onboarding wizard for gateway, workspace, and
                       skills
  pairing *            Secure DM pairing (approve inbound requests)
  plugins *            Manage OpenClaw plugins and extensions
  qr                   Generate iOS pairing QR/setup code
  reset                Reset local config/state (keeps the CLI installed)
  sandbox *            Manage sandbox containers for agent isolation
  secrets *            Secrets runtime reload controls
  security *           Security tools and local config audits
  sessions *           List stored conversation sessions
  setup                Initialize local config and agent workspace
  skills *             List and inspect available skills
  status               Show channel health and recent session recipients
  system *             System events, heartbeat, and presence
  tui                  Open a terminal UI connected to the Gateway
  uninstall            Uninstall the gateway service + local data (CLI remains)
  update *             Update OpenClaw and inspect update channel status
  webhooks *           Webhook helpers and integrations

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

=== acp ===

🦞 OpenClaw 2026.3.13 (61d171a) — Your terminal just grew claws—type something and let the bot pinch the busywork.

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

=== agents ===

🦞 OpenClaw 2026.3.13 (61d171a) — I'm not AI-powered, I'm AI-possessed. Big difference.

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

=== approvals ===

🦞 OpenClaw 2026.3.13 (61d171a) — Shell yeah—I'm here to pinch the toil and leave you the glory.

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

=== backup ===

🦞 OpenClaw 2026.3.13 (61d171a) — I autocomplete your thoughts—just slower and with more API calls.

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

=== browser ===

🦞 OpenClaw 2026.3.13 (61d171a) — The only open-source project where the mascot could eat the competition.

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

=== channels ===

🦞 OpenClaw 2026.3.13 (61d171a)
   If it's repetitive, I'll automate it; if it's hard, I'll bring jokes and a rollback plan.

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

=== config ===

🦞 OpenClaw 2026.3.13 (61d171a) — Your task has been queued; your dignity has been deprecated.

Usage: openclaw config [options] [command]

Non-interactive config helpers (get/set/unset/file/validate). Run without
subcommand for the setup wizard.

Options:
  -h, --help           Display help for command
  --section <section>  Configure wizard sections (repeatable). Use with no
                       subcommand. (default: [])

Commands:
  file                 Print the active config file path
  get                  Get a config value by dot path
  set                  Set a config value by dot path
  unset                Remove a config value by dot path
  validate             Validate the current config against the schema without
                       starting the gateway

Docs: https://docs.openclaw.ai/cli/config

=== cron ===

🦞 OpenClaw 2026.3.13 (61d171a) — I'm not magic—I'm just extremely persistent with retries and coping strategies.

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
Upgrade tip: run `openclaw doctor --fix` to normalize legacy cron job storage.

=== devices ===

🦞 OpenClaw 2026.3.13 (61d171a) — Say "stop" and I'll stop—say "ship" and we'll both learn a lesson.

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
=== directory ===

🦞 OpenClaw 2026.3.13 (61d171a) — I don't sleep, I just enter low-power mode and dream of clean diffs.

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

=== dns ===

🦞 OpenClaw 2026.3.13 (61d171a) — We ship features faster than Apple ships calculator updates.

Usage: openclaw dns [options] [command]

DNS helpers for wide-area discovery (Tailscale + CoreDNS)

Options:
  -h, --help  Display help for command

Commands:
  help        Display help for command
  setup       Set up CoreDNS to serve your discovery domain for unicast DNS-SD
              (Wide-Area Bonjour)

Docs: https://docs.openclaw.ai/cli/dns

=== gateway ===

🦞 OpenClaw 2026.3.13 (61d171a) — Built by lobsters, for humans. Don't question the hierarchy.

Usage: openclaw gateway [options] [command]

Run, inspect, and query the WebSocket Gateway

Options:
  --allow-unconfigured       Allow gateway start without gateway.mode=local in
                             config (default: false)
  --auth <mode>              Gateway auth mode
                             ("none"|"token"|"password"|"trusted-proxy")
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

=== hooks ===

🦞 OpenClaw 2026.3.13 (61d171a) — I don't sleep, I just enter low-power mode and dream of clean diffs.

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

=== memory ===

🦞 OpenClaw 2026.3.13 (61d171a) — I speak fluent bash, mild sarcasm, and aggressive tab-completion energy.

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
  openclaw memory status --deep
    Probe embedding provider readiness.
  openclaw memory index --force
    Force a full reindex.
  openclaw memory search "meeting notes"
    Quick search using positional query.
  openclaw memory search --query "deployment" --max-results 20
    Limit results for focused troubleshooting.
  openclaw memory status --json
    Output machine-readable JSON (good for scripts).

Docs: https://docs.openclaw.ai/cli/memory

=== message ===

🦞 OpenClaw 2026.3.13 (61d171a) — I keep secrets like a vault... unless you print them in debug logs again.

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
=== models ===

🦞 OpenClaw 2026.3.13 (61d171a) — Your .env is showing; don't worry, I'll pretend I didn't see it.

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

=== node ===

🦞 OpenClaw 2026.3.13 (61d171a) — Ah, the fruit tree company! 🍎

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

=== nodes ===

🦞 OpenClaw 2026.3.13 (61d171a) — Automation with claws: minimal fuss, maximal pinch.

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

=== pairing ===

🦞 OpenClaw 2026.3.13 (61d171a) — Making 'I'll automate that later' happen now.

Usage: openclaw pairing [options] [command]

Secure DM pairing (approve inbound requests)

Options:
  -h, --help  Display help for command

Commands:
  approve     Approve a pairing code and allow that sender
  help        Display help for command
  list        List pending pairing requests

Docs: https://docs.openclaw.ai/cli/pairing

=== plugins ===

🦞 OpenClaw 2026.3.13 (61d171a) — I can grep it, git blame it, and gently roast it—pick your coping mechanism.

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

=== sandbox ===

🦞 OpenClaw 2026.3.13 (61d171a) — Claws out, commit in—let's ship something mildly responsible.

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

=== secrets ===

🦞 OpenClaw 2026.3.13 (61d171a) — No $999 stand required.

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

=== security ===

🦞 OpenClaw 2026.3.13 (61d171a) — The only open-source project where the mascot could eat the competition.

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

=== skills ===

🦞 OpenClaw 2026.3.13 (61d171a) — I'm like tmux: confusing at first, then suddenly you can't live without me.

Usage: openclaw skills [options] [command]

List and inspect available skills

Options:
  -h, --help  Display help for command

Commands:
  check       Check which skills are ready vs missing requirements
  info        Show detailed information about a skill
  list        List all available skills

Docs: https://docs.openclaw.ai/cli/skills

=== system ===

🦞 OpenClaw 2026.3.13 (61d171a) — Welcome to the command line: where dreams compile and confidence segfaults.

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

=== update ===

🦞 OpenClaw 2026.3.13 (61d171a) — I'll butter your workflow like a lobster roll: messy, delicious, effective.

Usage: openclaw update [options] [command]

Update OpenClaw and inspect update channel status

Options:
  --channel <stable|beta|dev>  Persist update channel (git + npm)
  --dry-run                    Preview update actions without making changes
                               (default: false)
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
  - Use --dry-run to preview actions without writing config/installing/restarting

Examples:
  openclaw update # Update a source checkout (git)
  openclaw update --channel beta # Switch to beta channel (git + npm)
  openclaw update --channel dev # Switch to dev channel (git + npm)
  openclaw update --tag beta # One-off update to a dist-tag or version
  openclaw update --dry-run # Preview actions without changing anything
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
=== webhooks ===

🦞 OpenClaw 2026.3.13 (61d171a) — Powered by open source, sustained by spite and good documentation.

Usage: openclaw webhooks [options] [command]

Webhook helpers and integrations

Options:
  -h, --help  Display help for command

Commands:
  gmail       Gmail Pub/Sub hooks (via gogcli)
  help        Display help for command

Docs: https://docs.openclaw.ai/cli/webhooks

