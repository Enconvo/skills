# OpenClaw CLI Commands (Condensed Reference)

Generated from `OpenClaw 2026.7.1-2 (0790d9f)` on 2026-08-03. Usage and first-level subcommands; see `cli-reference.md` for every option.

## Top-Level Commands

```text
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
```

## `acp`

```text
Usage: openclaw acp [options] [command]

  client                   Run an interactive ACP client against the local ACP
                           bridge
```

## `agent`

```text
Usage: openclaw agent [options]
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
  set         Replace exec approvals with a JSON file
```

## `attach`

```text
Usage: openclaw attach [options]
```

## `audit`

```text
Usage: openclaw audit [options]
```

## `backup`

```text
Usage: openclaw backup [options] [command]

  create      Write a backup archive for config, credentials, sessions, and
              workspaces
  help        Display help for command
  verify      Validate a backup archive and its embedded manifest
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
Usage: openclaw tui|terminal [options]
```

## `clawbot`

```text
Usage: openclaw clawbot [options] [command]

  help        Display help for command
  qr          Generate a mobile pairing QR code and setup code
```

## `commitments`

```text
Usage: openclaw commitments [options] [command]

  dismiss            Dismiss inferred follow-up commitments
  list               List inferred follow-up commitments
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

## `crestodian`

```text
Usage: openclaw crestodian [options]
```

## `cron`

```text
Usage: openclaw cron [options] [command]

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
```

## `daemon`

```text
Usage: openclaw daemon [options] [command]

  help        Display help for command
  install     Install the Gateway service (launchd/systemd/schtasks)
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

## `devices`

```text
Usage: openclaw devices [options] [command]

  approve     Approve a pending device pairing request
  clear       Clear paired devices from the gateway table
  list        List pending and paired devices
  reject      Reject a pending device pairing request
  remove      Remove a paired device entry
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

## `gateway`

```text
Usage: openclaw gateway [options] [command]

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
```

## `hooks`

```text
Usage: openclaw hooks [options] [command]

  check       Check hooks eligibility status
  disable     Disable a hook
  enable      Enable a hook
  info        Show detailed information about a hook
  install     Deprecated: install a hook pack via `openclaw plugins install`
  list        List all hooks
  update      Deprecated: update hook packs via `openclaw plugins update`
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

  aliases          Manage model aliases
  auth             Manage model auth profiles
  fallbacks        Manage model fallback list
  image-fallbacks  Manage image model fallback list
  list             List models (configured by default)
  scan             Scan OpenRouter free models for tools + images
  set              Set the default model
  set-image        Set the image model
  status           Show configured model state
```

## `node`

```text
Usage: openclaw node [options] [command]

  help        Display help for command
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
```

## `onboard`

```text
Usage: openclaw onboard [options]
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

  cleanup             Run session-store maintenance now
  compact             Compact a stored session transcript via the running
                      gateway
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
  curator       Inspect and manage skill lifecycle curation
  info          Show detailed information about a skill
  install       Install a skill from ClawHub, git, or a local directory
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
  flow              Inspect durable TaskFlow state under tasks
  list              List tracked background tasks
  maintenance       Preview or apply tasks and TaskFlow maintenance
  notify            Set task notify policy
  show              Show one background task by task id, run id, or session key
```

## `terminal`

```text
Usage: openclaw tui|terminal [options]
```

## `transcripts`

```text
Usage: openclaw transcripts [options] [command]

  help        Display help for command
  list        List stored transcript sessions
  path        Print a stored transcripts artifact path
  show        Print a transcript summary markdown file
```

## `tui`

```text
Usage: openclaw tui|terminal [options]
```

## `uninstall`

```text
Usage: openclaw uninstall [options]
```

## `update`

```text
Usage: openclaw update [options] [command]

  repair                                       Repair post-update doctor and plugin convergence
  status                                       Show update channel and version status
  wizard                                       Interactive update wizard
```

## `webhooks`

```text
Usage: openclaw webhooks [options] [command]

  gmail       Gmail Pub/Sub hooks (via gogcli)
  help        Display help for command
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
