# OpenClaw CLI Commands (Condensed Reference)

Generated from `OpenClaw 2026.9.4 (3a9d69d)` on 2026-09-13. Usage and first-level subcommands; see `cli-reference.md` for entry-point options.

## Top-Level Commands

```text
  Hint: commands suffixed with * have subcommands. Run <command> --help for details.
  acp *                Run an ACP bridge backed by the Gateway
  agent *              Run an agent turn via the Gateway (use --local for
                       embedded)
  agents *             Manage isolated agents (workspaces + auth + routing)
  approvals *          Manage approval policy and pending requests
  attach               Attach Claude Code to a gateway session with scoped MCP
                       tools
  audit                Inspect activity records and exact-run identity context
  automations *        Manage automations (alias for cron)
  backup *             Create, verify, and restore backup archives and SQLite
                       snapshots
  browser *            Manage OpenClaw's dedicated browser (Chrome/Chromium)
  capability *         Run provider capability commands (fallback alias: infer)
  channels *           Manage connected chat channels and accounts
  chat                 Open a local terminal UI (alias for tui --local)
  clawbot *            Legacy clawbot command aliases
  codex *              Inspect and branch from Codex sessions through the
                       Gateway
  completion           Generate shell completion script
  config *             Non-interactive config helpers
                       (get/set/patch/unset/file/schema/validate). Run without
                       subcommand for guided setup.
  configure            Interactive configuration for credentials, channels,
                       gateway, and agent defaults
  connect              Connect this machine to an OpenClaw Gateway as a node
  cron *               Manage automations (via Gateway)
  daemon *             Manage the Gateway service (launchd/systemd/schtasks)
  dashboard            Open the Control UI with your current token
  database *           Inspect database schema compatibility and shared-state
                       write ownership
  devices *            Device pairing and auth tokens (for mobile app setup
                       codes, use `openclaw qr` instead)
  directory *          Lookup contact and group IDs (self, peers, groups) for
                       supported chat channels
  dns *                DNS helpers for wide-area discovery (Tailscale + CoreDNS)
  docs                 Search the live OpenClaw docs
  doctor               Health checks + quick fixes for the gateway and channels
  exec-approvals *     Manage exec approvals (alias for approvals)
  exec-policy *        Show or synchronize requested exec policy with host
                       approvals
  file-transfer *      Review file-transfer standing approvals
  fleet *              Provision and manage isolated tenant cells (experimental)
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
  onboard *            Guided setup for auth, models, Gateway, workspace,
                       channels, and skills
  openclam *           Pair and inspect the OpenClam channel
  pairing *            Secure DM pairing (approve inbound requests)
  plugins *            Manage OpenClaw plugins and extensions
  promos *             Discover and claim promotional model offers from ClawHub
  proxy *              Run the OpenClaw debug proxy and inspect captured traffic
  qr                   Generate a mobile pairing QR code and setup code
  reset                Reset local config/state (keeps the CLI installed)
  resume               Resume a recent Gateway session in the TUI
  sandbox *            Manage sandbox containers (Docker-based agent isolation)
  secrets *            Secrets runtime controls
  security *           Audit local config and state for common security
                       foot-guns
  sessions *           List stored conversation sessions
  setup                Chat with OpenClaw; onboard when setup is incomplete
  skills *             List and inspect available skills
  status               Show channel health and recent session recipients
  system *             System tools (events, heartbeat, presence)
  tasks *              Inspect durable background tasks and TaskFlow state
  telemetry *          Inspect and manage anonymous usage telemetry
  terminal             Open a local terminal UI (alias for tui --local)
  transcripts *        Inspect stored transcripts
  triage               Collect sanitized diagnostics and open a local coding
                       agent for repair
  tui                  Open a terminal UI connected to the Gateway
  uninstall            Uninstall the gateway service + local data
  update *             Update OpenClaw and inspect update channel status
  users *              Manage durable user profiles and email aliases
  webhooks *           Webhook helpers and integrations
  worker               Run the restricted cloud worker runtime
  worktrees *          Create, inspect, restore, and clean up managed worktrees
```

## `acp`

```text
Usage: openclaw acp [options] [command]

  client                   Run an interactive ACP client against the local ACP
                           bridge
```

## `agent`

```text
Usage: openclaw agent [options] [command]

  exec                       Run one isolated headless embedded agent turn
```

## `agents`

```text
Usage: openclaw agents [options] [command]

  add           Add a new isolated agent
  bind          Add routing bindings for an agent
  bindings      List routing bindings
  delete        Delete an agent and prune workspace/state
  list          List configured agents
  set-identity  Update an agent identity (name/theme/emoji/avatar)
  unbind        Remove routing bindings for an agent
```

## `approvals`

```text
Usage: openclaw approvals|exec-approvals [options] [command]

  allowlist   Edit the per-agent allowlist
  get         Fetch exec approvals snapshot
  grants      Standing grants minted by allow-always on automation approvals
  pending     List pending exec, plugin, and system-agent approvals
  resolve     Resolve a pending approval
  set         Replace exec approvals with a JSON file
```

## `attach`

```text
Usage: openclaw attach [options] [target]
```

## `audit`

```text
Usage: openclaw audit [options]
```

## `automations`

```text
Usage: openclaw cron|automations [options] [command]

  add                    Add an automation
  disable                Disable an automation
  edit                   Edit an automation (patch fields)
  enable                 Enable an automation
  get                    Get an automation as JSON
  list                   List automations
  rm                     Remove an automation
  run                    Run an automation now (debug)
  runs                   Show automation run history
  scratch                Read or replace an automation's private scratch
  show                   Show an automation
  status                 Show automations scheduler status
```

## `backup`

```text
Usage: openclaw backup [options] [command]

  create      Write a backup archive for config, credentials, sessions, and
              workspaces
  disable     Remove the scheduled Git backup automation
  enable      Provision a Gateway automation for scheduled Git backups
  git         Create and restore deterministic versioned SQLite dumps in Git
  help        Display help for command
  restore     Restore a verified backup archive to a fresh staging directory
  sqlite      Create, list, verify, and restore SQLite snapshots
  verify      Validate a backup archive and its embedded manifest
```

## `browser`

```text
Usage: openclaw browser [options] [command]

  batch                     Run a batch of browser actions in one call
  click                     Click an element by ref from snapshot
  click-coords              Click viewport coordinates
  close                     Close a tab (tab reference optional)
  console                   Get recent console messages
  cookie-sync               Sync allowlisted macOS browser cookies to a managed
                            profile
  cookies                   Read/write cookies
  create-profile            Create a new browser profile
  delete-profile            Delete a browser profile
  dialog                    Arm the next modal dialog (alert/confirm/prompt)
  doctor                    Check browser plugin readiness
  download                  Click a ref and save the resulting download
  drag                      Drag from one ref to another
  errors                    Get recent page errors
  evaluate                  Evaluate a function against the page or a ref
  extension                 Chrome extension install, status, and pairing
  fill                      Fill a form with JSON field descriptors
  focus                     Focus a tab by tab reference
  highlight                 Highlight an element by ref
  hover                     Hover an element by ai ref
  import-profile            Import cookies from a macOS Chrome-family profile
  navigate                  Navigate the current tab to a URL
  open                      Open a URL in a new tab
  pdf                       Save page as PDF
  press                     Press a key
  profiles                  List all browser profiles
  requests                  Get recent network requests (best-effort)
  reset-profile             Reset browser profile (moves it to Trash)
  resize                    Resize the viewport
  responsebody              Wait for a network response and return its body
  screenshot                Capture a screenshot (prints the saved path)
  scrollintoview            Scroll an element into view by ref from snapshot
  select                    Select option(s) in a select element
  set                       Browser environment settings
  snapshot                  Capture a snapshot (default: ai; aria is the
                            accessibility tree)
  start                     Start the browser (no-op if already running)
  status                    Show browser status
  stop                      Stop the browser (best-effort)
  storage                   Read/write localStorage/sessionStorage
  system-profiles           List Chrome-family profiles available for cookie
                            import
  tab                       Tab shortcuts (index-based)
  tabs                      List open tabs
  trace                     Record a Playwright trace
  type                      Type into an element by ref from snapshot
  upload                    Arm file upload for the next file chooser
  wait                      Wait for time, selector, URL, load state, or JS
                            conditions
  waitfordownload           Wait for the next download (and save it)
```

## `capability`

```text
Usage: openclaw infer|capability [options] [command]

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
```

## `channels`

```text
Usage: openclaw channels [options] [command]

  add           Add or update a channel account
  capabilities  Show provider capabilities (intents/scopes + supported features)
  dead-letters  Inspect and resubmit failed inbound channel events
  list          List chat channels (configured by default; pass --all for
                installable catalog)
  login         Link a channel account (if supported)
  logout        Log out of a channel session (if supported)
  logs          Show recent channel logs from the gateway log file
  remove        Disable or delete a channel account
  resolve       Resolve channel/user names to IDs
  status        Show gateway channel status (use status --deep for local)
```

## `chat`

```text
Usage: openclaw tui|terminal [options] [target]
```

## `clawbot`

```text
Usage: openclaw clawbot [options] [command]

  help        Display help for command
  qr          Generate a mobile pairing QR code and setup code
```

## `codex`

```text
Usage: openclaw codex [options] [command]

  archive     Archive a stored or idle Gateway-local Codex thread
  continue    Continue a Gateway-local Codex thread as an OpenClaw branch
  help        Display help for command
  sessions    List non-archived Codex app-server sessions across connected hosts
```

## `completion`

```text
Usage: openclaw completion [options]
```

## `config`

```text
Usage: openclaw config [options] [command]

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
```

## `configure`

```text
Usage: openclaw configure [options]
```

## `connect`

```text
Usage: openclaw connect [options] [target]
```

## `cron`

```text
Usage: openclaw cron|automations [options] [command]

  add                    Add an automation
  disable                Disable an automation
  edit                   Edit an automation (patch fields)
  enable                 Enable an automation
  get                    Get an automation as JSON
  list                   List automations
  rm                     Remove an automation
  run                    Run an automation now (debug)
  runs                   Show automation run history
  scratch                Read or replace an automation's private scratch
  show                   Show an automation
  status                 Show automations scheduler status
```

## `daemon`

```text
Usage: openclaw daemon [options] [command]

  help        Display help for command
  install     Install and start the Gateway service (launchd/systemd/schtasks)
  restart     Restart the Gateway service (launchd/systemd/schtasks)
  start       Start the Gateway service (launchd/systemd/schtasks)
  status      Show service install status + probe connectivity/capability
  stop        Stop the Gateway service (launchd/systemd/schtasks)
  uninstall   Uninstall the Gateway service (launchd/systemd/schtasks)
```

## `dashboard`

```text
Usage: openclaw dashboard [options]
```

## `database`

```text
Usage: openclaw database [options] [command]

  ownership        Inspect or claim write ownership
  preflight        Compare one copied SQLite file with this release's state
                   schema
  preflight-agent  Compare one copied agent SQLite file with this release's
                   agent schema and owner
```

## `devices`

```text
Usage: openclaw devices [options] [command]

  approve     Approve a pending device pairing request
  clear       Clear paired devices from the gateway table
  join-code   Mint a single-use node onboarding URL (not a mobile app setup
              code; use `openclaw qr` for that)
  list        List pending and paired devices
  reject      Reject a pending device pairing request
  remove      Remove a paired device entry
  rename      Assign an operator label to a paired device
  revoke      Revoke a device token for a role
  rotate      Rotate a device token for a role
```

## `directory`

```text
Usage: openclaw directory [options] [command]

  groups      Group directory
  peers       Peer directory (contacts/users)
  self        Show the current account user
```

## `dns`

```text
Usage: openclaw dns [options] [command]

  help        Display help for command
  setup       Set up CoreDNS to serve your discovery domain for unicast DNS-SD
              (Wide-Area Bonjour)
```

## `docs`

```text
Usage: openclaw docs [options] [query...]
```

## `doctor`

```text
Usage: openclaw doctor [options]
```

## `exec-approvals`

```text
Usage: openclaw approvals|exec-approvals [options] [command]

  allowlist   Edit the per-agent allowlist
  get         Fetch exec approvals snapshot
  grants      Standing grants minted by allow-always on automation approvals
  pending     List pending exec, plugin, and system-agent approvals
  resolve     Resolve a pending approval
  set         Replace exec approvals with a JSON file
```

## `exec-policy`

```text
Usage: openclaw exec-policy [options] [command]

  help        Display help for command
  preset      Apply a synchronized preset: "yolo", "cautious", or "deny-all"
  set         Synchronize local config and host approvals using explicit values
  show        Show the local config policy, host approvals, and effective merge
```

## `file-transfer`

```text
Usage: openclaw file-transfer [options] [command]

  approvals   Manage standing approvals
  help        Display help for command
```

## `fleet`

```text
Usage: openclaw fleet [options] [command]

  backup      Back up one tenant cell as a host operator (archive contains
              secrets)
  create      Create an isolated tenant cell
  doctor      Audit fleet cells without changing them
  help        Display help for command
  list        List tenant cells
  logs        Stream tenant cell container logs
  restart     Restart a tenant cell
  restore     Restore one tenant cell as a host operator (archive contains
              secrets)
  rm          Remove a tenant cell
  start       Start a tenant cell
  status      Show tenant cell status
  stop        Stop a tenant cell
  upgrade     Replace a tenant cell with a freshly pulled image
```

## `gateway`

```text
Usage: openclaw gateway [options] [command]

  auth-token                Reveal the configured shared Gateway token
  call                      Call a Gateway method
  diagnostics               Export local support diagnostics
  discover                  Discover gateways via Bonjour (local + wide-area if
                            configured)
  health                    Fetch Gateway health
  install                   Install and start the Gateway service
                            (launchd/systemd/schtasks)
  probe                     Show gateway reachability, auth capability, and
                            read-probe summary (local + remote)
  restart                   Restart the Gateway service
                            (launchd/systemd/schtasks)
  resume                    Release a cooperative Gateway suspension
  run                       Run the WebSocket Gateway (foreground)
  stability                 Fetch payload-free Gateway stability diagnostics
  start                     Start the Gateway service (launchd/systemd/schtasks)
  status                    Show gateway service status + probe
                            connectivity/capability
  stop                      Stop the Gateway service (launchd/systemd/schtasks)
  suspend                   Prepare the Gateway for cooperative host suspension
  uninstall                 Uninstall the Gateway service
                            (launchd/systemd/schtasks)
  usage-cost                Fetch usage cost summary from session logs
```

## `health`

```text
Usage: openclaw health [options]
```

## `help`

```text
Usage: openclaw [options] [command]

  Hint: commands suffixed with * have subcommands. Run <command> --help for details.
  acp *                Run an ACP bridge backed by the Gateway
  agent *              Run an agent turn via the Gateway (use --local for
                       embedded)
  agents *             Manage isolated agents (workspaces + auth + routing)
  approvals *          Manage approval policy and pending requests
  attach               Attach Claude Code to a gateway session with scoped MCP
                       tools
  audit                Inspect activity records and exact-run identity context
  automations *        Manage automations (alias for cron)
  backup *             Create, verify, and restore backup archives and SQLite
                       snapshots
  browser *            Manage OpenClaw's dedicated browser (Chrome/Chromium)
  capability *         Run provider capability commands (fallback alias: infer)
  channels *           Manage connected chat channels and accounts
  chat                 Open a local terminal UI (alias for tui --local)
  clawbot *            Legacy clawbot command aliases
  codex *              Inspect and branch from Codex sessions through the
                       Gateway
  completion           Generate shell completion script
  config *             Non-interactive config helpers
                       (get/set/patch/unset/file/schema/validate). Run without
                       subcommand for guided setup.
  configure            Interactive configuration for credentials, channels,
                       gateway, and agent defaults
  connect              Connect this machine to an OpenClaw Gateway as a node
  cron *               Manage automations (via Gateway)
  daemon *             Manage the Gateway service (launchd/systemd/schtasks)
  dashboard            Open the Control UI with your current token
  database *           Inspect database schema compatibility and shared-state
                       write ownership
  devices *            Device pairing and auth tokens (for mobile app setup
                       codes, use `openclaw qr` instead)
  directory *          Lookup contact and group IDs (self, peers, groups) for
                       supported chat channels
  dns *                DNS helpers for wide-area discovery (Tailscale + CoreDNS)
  docs                 Search the live OpenClaw docs
  doctor               Health checks + quick fixes for the gateway and channels
  exec-approvals *     Manage exec approvals (alias for approvals)
  exec-policy *        Show or synchronize requested exec policy with host
                       approvals
  file-transfer *      Review file-transfer standing approvals
  fleet *              Provision and manage isolated tenant cells (experimental)
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
  onboard *            Guided setup for auth, models, Gateway, workspace,
                       channels, and skills
  openclam *           Pair and inspect the OpenClam channel
  pairing *            Secure DM pairing (approve inbound requests)
  plugins *            Manage OpenClaw plugins and extensions
  promos *             Discover and claim promotional model offers from ClawHub
  proxy *              Run the OpenClaw debug proxy and inspect captured traffic
  qr                   Generate a mobile pairing QR code and setup code
  reset                Reset local config/state (keeps the CLI installed)
  resume               Resume a recent Gateway session in the TUI
  sandbox *            Manage sandbox containers (Docker-based agent isolation)
  secrets *            Secrets runtime controls
  security *           Audit local config and state for common security
                       foot-guns
  sessions *           List stored conversation sessions
  setup                Chat with OpenClaw; onboard when setup is incomplete
  skills *             List and inspect available skills
  status               Show channel health and recent session recipients
  system *             System tools (events, heartbeat, presence)
  tasks *              Inspect durable background tasks and TaskFlow state
  telemetry *          Inspect and manage anonymous usage telemetry
  terminal             Open a local terminal UI (alias for tui --local)
  transcripts *        Inspect stored transcripts
  triage               Collect sanitized diagnostics and open a local coding
                       agent for repair
  tui                  Open a terminal UI connected to the Gateway
  uninstall            Uninstall the gateway service + local data
  update *             Update OpenClaw and inspect update channel status
  users *              Manage durable user profiles and email aliases
  webhooks *           Webhook helpers and integrations
  worker               Run the restricted cloud worker runtime
  worktrees *          Create, inspect, restore, and clean up managed worktrees
```

## `hooks`

```text
Usage: openclaw hooks [options] [command]

  check         Check hooks eligibility status
  disable       Disable a hook
  enable        Enable a hook
  info          Show detailed information about a hook
  install       Deprecated: install a hook pack via `openclaw plugins install`
  list          List all hooks
  update        Deprecated: update hook packs via `openclaw plugins update`
```

## `infer`

```text
Usage: openclaw infer|capability [options] [command]

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
```

## `logs`

```text
Usage: openclaw logs [options]
```

## `mcp`

```text
Usage: openclaw mcp [options] [command]

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

## `memory`

```text
Usage: openclaw memory [options] [command]

  forget            Delete memories and derived artifacts from selected sessions
  index             Reindex memory files
  promote           Rank short-term recalls and optionally append top entries to
                    MEMORY.md
  promote-explain   Explain a specific promotion candidate and its score
                    breakdown
  rem-backfill      Write grounded historical REM summaries into DREAMS.md for
                    UI review
  rem-harness       Preview REM reflections, candidate truths, and deep
                    promotions without writing
  reset             Clear the derived memory index and embedding cache without
                    deleting sessions
  search            Search memory files
  session-backfill  Distill retained session history into staged memory
                    candidates
  status            Show memory search index status
```

## `message`

```text
Usage: openclaw message [options] [command]

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
```

## `migrate`

```text
Usage: openclaw migrate [options] [command] [provider]

  apply                   Apply a migration after a verified backup
  list                    List migration providers
  plan                    Preview a migration without changing OpenClaw state
```

## `models`

```text
Usage: openclaw models [options] [command]

  accounts         Manage your personal model accounts on the Gateway
  aliases          Manage model aliases
  auth             Manage system/agent credentials on this machine
  fallbacks        Manage model fallback list
  image-fallbacks  Manage image model fallback list
  list             List models (configured by default)
  refresh          Refresh the hosted model catalog
  scan             Scan OpenRouter free models for tools + images
  set              Set the default model
  set-image        Set the image model
  status           Show configured model state
```

## `node`

```text
Usage: openclaw node [options] [command]

  help        Display help for command
  identity    Print the node host device identity (device id + public key)
  install     Install the node host service (launchd/systemd/schtasks)
  restart     Restart the node host service (launchd/systemd/schtasks)
  run         Run the headless node host (foreground)
  start       Start the node host service (launchd/systemd/schtasks)
  status      Show node host status
  stop        Stop the node host service (launchd/systemd/schtasks)
  uninstall   Uninstall the node host service (launchd/systemd/schtasks)
```

## `nodes`

```text
Usage: openclaw nodes [options] [command]

  approve     Approve a pending pairing request
  camera      Capture camera media from a paired node
  canvas      Present widget documents on a paired macOS panel
  describe    Describe a node (capabilities + supported invoke commands)
  help        Display help for command
  invoke      Invoke a command on a paired node
  list        List pending and paired nodes
  location    Fetch location from a paired node
  notify      Send a local notification on a node
  pending     List pending pairing requests
  push        Send an APNs test push to an iOS node
  reject      Reject a pending pairing request
  remove      Remove a paired node entry
  rename      Rename a paired node (display name override)
  screen      Capture screen recordings from a paired node
  status      List known nodes with connection status and capabilities
```

## `onboard`

```text
Usage: openclaw onboard [options] [command]

  recommendations                          Read the app recommendations stored during onboarding
```

## `openclam`

```text
Usage: openclaw openclam [options] [command]

  help         Display help for command
  pair         Create a one-time pairing code for OpenClam iOS
  pair-device  Create a fresh iPhone code from the existing OpenClam connection
  status       Show OpenClam pairing state without secrets
```

## `pairing`

```text
Usage: openclaw pairing [options] [command]

  approve     Approve a pairing code and allow that sender
  help        Display help for command
  list        List pending pairing requests
```

## `plugins`

```text
Usage: openclaw plugins [options] [command]

  build        Build plugin metadata and native Control UI assets
  disable      Disable a plugin in config
  doctor       Report plugin load issues
  enable       Enable a plugin in config
  init         Create a plugin project
  inspect      Inspect plugin details
  install      Install a plugin or hook pack (path, archive, npm spec, git repo,
               clawhub:package, or marketplace entry)
  list         List discovered plugins
  marketplace  Inspect Claude-compatible plugin marketplaces
  pack         Bundle a built plugin into an exact artifact for activation
               approval
  registry     Inspect or rebuild the persisted plugin registry
  search       Search ClawHub plugin packages
  uninstall    Uninstall a plugin
  update       Update installed plugins and tracked hook packs
  validate     Validate plugin metadata and native Control UI assets
```

## `promos`

```text
Usage: openclaw promos [options] [command]

  claim       Claim a promotion: set up provider auth and register its models
  help        Display help for command
  list        List active promotions
```

## `proxy`

```text
Usage: openclaw proxy [options] [command]

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

## `qr`

```text
Usage: openclaw qr [options]
```

## `reset`

```text
Usage: openclaw reset [options]
```

## `resume`

```text
Usage: openclaw resume [options] [query]
```

## `sandbox`

```text
Usage: openclaw sandbox [options] [command]

  explain     Explain effective sandbox/tool policy for a session/agent
  list        List sandbox containers and their status
  recreate    Remove containers to force recreation with updated config
```

## `secrets`

```text
Usage: openclaw secrets [options] [command]

  apply       Apply a previously generated secrets plan
  audit       Audit plaintext secrets, unresolved refs, and precedence drift
  configure   Interactive secrets helper (provider setup + SecretRef mapping +
              preflight)
  help        Display help for command
  reload      Re-resolve secret references and atomically swap runtime snapshot
  store       Manage the team-scoped SQLite secret and environment store
```

## `security`

```text
Usage: openclaw security [options] [command]

  audit       Audit config + local state for common security foot-guns
  help        Display help for command
```

## `sessions`

```text
Usage: openclaw sessions [options] [command]

  archive             Archive stored sessions via the running gateway
  cleanup             Run session-store maintenance now
  compact             Compact a stored session transcript via the running
                      gateway
  delete              Delete stored sessions and their live artifacts via the
                      running gateway. Retained archives can remain searchable.
  export-trajectory   Export a redacted trajectory bundle for a stored session
  list                List stored conversation sessions
  tail                Tail human-readable session trajectory progress
```

## `setup`

```text
Usage: openclaw setup [options]
```

## `skills`

```text
Usage: openclaw skills [options] [command]

  check         Check which skills are ready, visible, or missing requirements
  curator       Inspect skill usage and collection review outcomes
  info          Show detailed information about a skill
  install       Install a skill from ClawHub, git, or a local directory
  library       Manage authenticated personal and team skill libraries
  list          List all available skills
  search        Search ClawHub skills
  update        Update ClawHub-installed skills in the active or shared managed
                directory
  verify        Verify a ClawHub skill with ClawHub
  workshop      Manage pending skill proposals
```

## `status`

```text
Usage: openclaw status [options]
```

## `system`

```text
Usage: openclaw system [options] [command]

  event       Enqueue a system event and optionally trigger a heartbeat
  heartbeat   Heartbeat controls
  help        Display help for command
  presence    List system presence entries
```

## `tasks`

```text
Usage: openclaw tasks [options] [command]

  audit             Show stale or broken background tasks and TaskFlows
  cancel            Cancel a running background task
  dismiss           Dismiss delivery for up to 10 blocked subagent completions
  flow              Inspect durable TaskFlow state under tasks
  list              List tracked background tasks
  maintenance       Preview or apply tasks and TaskFlow maintenance
  notify            Set task notify policy
  retry             Retry delivery for up to 10 blocked subagent completions
  show              Show one background task by task id, run id, or session key
```

## `telemetry`

```text
Usage: openclaw telemetry [options] [command]

  help        Display help for command
  off         Disable anonymous feature statistics
  on          Enable anonymous feature statistics
  show        Preview the daily update request from this CLI process
```

## `terminal`

```text
Usage: openclaw tui|terminal [options] [target]
```

## `transcripts`

```text
Usage: openclaw transcripts [options] [command]

  help        Display help for command
  list        List stored transcript sessions
  path        Materialize and print a stored transcripts artifact path
  show        Print and materialize a transcript summary
```

## `triage`

```text
Usage: openclaw triage [options]
```

## `tui`

```text
Usage: openclaw tui|terminal [options] [target]
```

## `uninstall`

```text
Usage: openclaw uninstall [options]
```

## `update`

```text
Usage: openclaw update [options] [command]

  cleanup                                      Retire verified update recovery originals after acknowledging rollback loss
  repair                                       Reconcile abandoned updates or repair post-update doctor and plugin convergence
  status                                       Show update channel and version status
  wizard                                       Interactive update wizard
```

## `users`

```text
Usage: openclaw users [options] [command]

  link-email  Link an email alias to a user profile
  list        List durable user profiles
```

## `webhooks`

```text
Usage: openclaw webhooks [options] [command]

  gmail       Gmail Pub/Sub hooks (via gogcli)
  help        Display help for command
```

## `worker`

```text
Usage: openclaw worker [options]
```

## `worktrees`

```text
Usage: openclaw worktrees [options] [command]

  create      Create a managed worktree
  gc          Run managed worktree cleanup now
  list        List active and restorable managed worktrees
  remove      Snapshot and remove a managed worktree
  restore     Restore a managed worktree from its snapshot
```
