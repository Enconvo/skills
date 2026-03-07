#!/usr/bin/env python3
"""Discord Developer Portal CLI — manage Discord apps/bots via REST API + Playwright token extraction."""

import argparse
import base64
import json
import os
import sys
import urllib.request
import urllib.error

CONFIG_DIR = os.path.expanduser("~/.discord-dev")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")
API_BASE = "https://discord.com/api/v10"


def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE) as f:
            return json.load(f)
    return {}


def save_config(cfg):
    os.makedirs(CONFIG_DIR, exist_ok=True)
    with open(CONFIG_FILE, "w") as f:
        json.dump(cfg, f, indent=2)


def ensure_token():
    cfg = load_config()
    token = cfg.get("token")
    if not token:
        print("ERROR: No token configured. Run: discord-dev setup", file=sys.stderr)
        sys.exit(1)
    return token


def api_request(method, path, token, data=None):
    """Make a Discord API request."""
    url = f"{API_BASE}{path}"
    headers = {
        "Authorization": token,
        "Content-Type": "application/json",
        "User-Agent": "DiscordDevCLI/1.0",
    }

    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)

    try:
        with urllib.request.urlopen(req) as resp:
            if resp.status == 204:
                return None
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        error_body = e.read().decode()
        try:
            error_json = json.loads(error_body)
            print(f"ERROR {e.code}: {json.dumps(error_json, indent=2)}", file=sys.stderr)
        except json.JSONDecodeError:
            print(f"ERROR {e.code}: {error_body}", file=sys.stderr)
        sys.exit(1)


def fmt(data, as_json=False):
    """Format output."""
    if as_json:
        print(json.dumps(data, indent=2, ensure_ascii=False))
    else:
        if isinstance(data, list):
            for item in data:
                fmt_app(item)
                print("---")
        elif isinstance(data, dict):
            fmt_app(data)


def fmt_app(app):
    """Format a single application for display."""
    name = app.get("name", "?")
    app_id = app.get("id", "?")
    desc = app.get("description", "")
    bot = app.get("bot")
    print(f"  Name: {name}")
    print(f"  ID: {app_id}")
    if desc:
        print(f"  Description: {desc}")
    if bot:
        print(f"  Bot: {bot.get('username', '?')}#{bot.get('discriminator', '0')}")
        print(f"  Bot ID: {bot.get('id', '?')}")
        print(f"  Public: {bot.get('bot_public', '?')}")
    flags = app.get("flags", 0)
    intents = []
    if flags & (1 << 12):
        intents.append("PRESENCE")
    if flags & (1 << 13):
        intents.append("GUILD_MEMBERS")
    if flags & (1 << 14):
        intents.append("MESSAGE_CONTENT")
    if intents:
        print(f"  Intents: {', '.join(intents)}")


# ── Command handlers ──


def cmd_save_token(args):
    """Save Discord user token (from Playwright extraction)."""
    if not args.token:
        print("ERROR: --token is required", file=sys.stderr)
        sys.exit(1)
    cfg = load_config()
    cfg["token"] = args.token
    save_config(cfg)
    print(f"Token saved to {CONFIG_FILE}")


def cmd_status(args):
    """Check auth status by fetching current user info."""
    token = ensure_token()
    data = api_request("GET", "/users/@me", token)
    print(f"Authenticated: {data['username']}#{data.get('discriminator', '0')}")
    print(f"ID: {data['id']}")
    print(f"Email: {data.get('email', 'N/A')}")


def cmd_list(args):
    """List all applications."""
    token = ensure_token()
    apps = api_request("GET", "/applications", token)
    if args.json:
        print(json.dumps(apps, indent=2, ensure_ascii=False))
    else:
        if not apps:
            print("No applications found.")
            return
        for app in apps:
            fmt_app(app)
            print("---")


def cmd_create(args):
    """Create a new application."""
    token = ensure_token()
    data = {"name": args.name}
    app = api_request("POST", "/applications", token, data)

    if args.json:
        print(json.dumps(app, indent=2, ensure_ascii=False))
    else:
        print(f"Application created!")
        fmt_app(app)

    # Auto-create bot user if requested
    if args.bot:
        bot = api_request("POST", f"/applications/{app['id']}/bot", token)
        if args.json:
            print(json.dumps(bot, indent=2, ensure_ascii=False))
        else:
            print(f"\nBot user created!")
            print(f"  Bot Token: {bot.get('token', 'N/A')}")
            print(f"  Username: {bot.get('username', '?')}")
            print(f"\n  SAVE THIS TOKEN — it won't be shown again!")


def cmd_delete(args):
    """Delete an application."""
    token = ensure_token()
    app_id = resolve_app_id(token, args.app)
    api_request("DELETE", f"/applications/{app_id}", token)
    print(f"Application {app_id} deleted.")


def cmd_info(args):
    """Get detailed info about an application."""
    token = ensure_token()
    app_id = resolve_app_id(token, args.app)
    app = api_request("GET", f"/applications/{app_id}", token)
    if args.json:
        print(json.dumps(app, indent=2, ensure_ascii=False))
    else:
        fmt_app(app)


def cmd_update(args):
    """Update application settings."""
    token = ensure_token()
    app_id = resolve_app_id(token, args.app)

    data = {}
    if args.name:
        data["name"] = args.name
    if args.description is not None:
        data["description"] = args.description
    if args.icon:
        # Read image and convert to data URI
        with open(args.icon, "rb") as f:
            img_data = f.read()
        ext = args.icon.rsplit(".", 1)[-1].lower()
        mime = {"png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg", "gif": "image/gif", "webp": "image/webp"}.get(ext, "image/png")
        b64 = base64.b64encode(img_data).decode()
        data["icon"] = f"data:{mime};base64,{b64}"
    if args.public is not None:
        data["bot_public"] = args.public.lower() in ("true", "1", "yes")
    if args.require_code_grant is not None:
        data["bot_require_code_grant"] = args.require_code_grant.lower() in ("true", "1", "yes")

    if not data:
        print("ERROR: No changes specified. Use --name, --description, --icon, --public, or --require-code-grant", file=sys.stderr)
        sys.exit(1)

    app = api_request("PATCH", f"/applications/{app_id}", token, data)
    if args.json:
        print(json.dumps(app, indent=2, ensure_ascii=False))
    else:
        print("Application updated!")
        fmt_app(app)


def cmd_bot_add(args):
    """Add a bot user to an application."""
    token = ensure_token()
    app_id = resolve_app_id(token, args.app)
    bot = api_request("POST", f"/applications/{app_id}/bot", token)
    if args.json:
        print(json.dumps(bot, indent=2, ensure_ascii=False))
    else:
        print("Bot user created!")
        print(f"  Token: {bot.get('token', 'N/A')}")
        print(f"  Username: {bot.get('username', '?')}")
        print(f"\n  SAVE THIS TOKEN — it won't be shown again!")


def cmd_bot_reset(args):
    """Reset (regenerate) a bot token."""
    token = ensure_token()
    app_id = resolve_app_id(token, args.app)
    result = api_request("POST", f"/applications/{app_id}/bot/reset", token)
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(f"Bot token reset!")
        print(f"  New Token: {result.get('token', 'N/A')}")
        print(f"\n  SAVE THIS TOKEN — it won't be shown again!")


def cmd_commands_list(args):
    """List registered slash commands for an application."""
    token = ensure_token()
    app_id = resolve_app_id(token, args.app)
    commands = api_request("GET", f"/applications/{app_id}/commands", token)
    if args.json:
        print(json.dumps(commands, indent=2, ensure_ascii=False))
    else:
        if not commands:
            print("No commands registered.")
            return
        for cmd in commands:
            name = cmd.get("name", "?")
            desc = cmd.get("description", "")
            cmd_type = {1: "CHAT_INPUT", 2: "USER", 3: "MESSAGE"}.get(cmd.get("type", 1), "?")
            print(f"  /{name} — {desc} [{cmd_type}]")


def cmd_commands_set(args):
    """Bulk overwrite slash commands for an application."""
    token = ensure_token()
    app_id = resolve_app_id(token, args.app)

    # Parse commands from JSON string or file
    if args.commands.startswith("@"):
        with open(args.commands[1:]) as f:
            commands = json.load(f)
    else:
        commands = json.loads(args.commands)

    result = api_request("PUT", f"/applications/{app_id}/commands", token, commands)
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(f"Set {len(result)} commands.")
        for cmd in result:
            print(f"  /{cmd.get('name', '?')} — {cmd.get('description', '')}")


def cmd_oauth2_url(args):
    """Generate an OAuth2 invite URL."""
    token = ensure_token()
    app_id = resolve_app_id(token, args.app)

    permissions = args.permissions or "0"
    scopes = args.scopes or "bot applications.commands"

    url = f"https://discord.com/api/oauth2/authorize?client_id={app_id}&permissions={permissions}&scope={scopes.replace(' ', '%20')}"
    print(url)


def cmd_bot_id(args):
    """Get the bot user ID for an application."""
    token = ensure_token()
    app_id = resolve_app_id(token, args.app)
    app = api_request("GET", f"/applications/{app_id}", token)
    bot = app.get("bot")
    if not bot:
        print(f"ERROR: Application '{args.app}' has no bot user. Run: discord-dev bot-add {args.app}", file=sys.stderr)
        sys.exit(1)
    if args.json:
        print(json.dumps({"bot_id": bot["id"], "username": bot["username"], "app_id": app_id}, indent=2))
    else:
        print(f"Bot ID: {bot['id']}")
        print(f"Username: {bot['username']}#{bot.get('discriminator', '0')}")
        print(f"App ID: {app_id}")


def cmd_dm(args):
    """Send a DM to a bot (as the authenticated user) to trigger pairing."""
    token = ensure_token()

    # Resolve bot user ID
    bot_user_id = args.bot_id
    if not bot_user_id:
        # Try to resolve from app name
        if not args.app:
            print("ERROR: Provide --bot-id <id> or --app <name> to identify the bot.", file=sys.stderr)
            sys.exit(1)
        app_id = resolve_app_id(token, args.app)
        app = api_request("GET", f"/applications/{app_id}", token)
        bot = app.get("bot")
        if not bot:
            print(f"ERROR: Application '{args.app}' has no bot user.", file=sys.stderr)
            sys.exit(1)
        bot_user_id = bot["id"]

    # Create DM channel with the bot
    dm_channel = api_request("POST", "/users/@me/channels", token, {"recipient_id": bot_user_id})
    channel_id = dm_channel["id"]

    # Send message
    message = args.message or "/start"
    result = api_request("POST", f"/channels/{channel_id}/messages", token, {"content": message})

    if args.json:
        print(json.dumps({"channel_id": channel_id, "message_id": result["id"], "content": message, "bot_user_id": bot_user_id}, indent=2))
    else:
        print(f"DM channel: {channel_id}")
        print(f"Sent to bot {bot_user_id}: {message}")
        print(f"Message ID: {result['id']}")


def cmd_intents(args):
    """View or set privileged gateway intents."""
    token = ensure_token()
    app_id = resolve_app_id(token, args.app)
    app = api_request("GET", f"/applications/{app_id}", token)
    flags = app.get("flags", 0)

    INTENT_FLAGS = {
        "PRESENCE": 1 << 12,
        "GUILD_MEMBERS": 1 << 13,
        "MESSAGE_CONTENT": 1 << 14,
    }

    if not args.enable and not args.disable:
        # Just show current intents
        print("Privileged Gateway Intents:")
        for name, flag in INTENT_FLAGS.items():
            status = "ON" if flags & flag else "OFF"
            print(f"  {name}: {status}")
        return

    for intent_name in (args.enable or []):
        intent_name = intent_name.upper()
        if intent_name in INTENT_FLAGS:
            flags |= INTENT_FLAGS[intent_name]

    for intent_name in (args.disable or []):
        intent_name = intent_name.upper()
        if intent_name in INTENT_FLAGS:
            flags &= ~INTENT_FLAGS[intent_name]

    result = api_request("PATCH", f"/applications/{app_id}", token, {"flags": flags})
    new_flags = result.get("flags", 0)
    print("Updated Privileged Gateway Intents:")
    for name, flag in INTENT_FLAGS.items():
        status = "ON" if new_flags & flag else "OFF"
        print(f"  {name}: {status}")


# ── Helpers ──


def resolve_app_id(token, app_ref):
    """Resolve app name or ID to an application ID."""
    if app_ref.isdigit() and len(app_ref) > 10:
        return app_ref

    apps = api_request("GET", "/applications", token)
    for app in apps:
        if app["name"].lower() == app_ref.lower() or app["id"] == app_ref:
            return app["id"]

    print(f"ERROR: Application '{app_ref}' not found.", file=sys.stderr)
    print("Available apps:", file=sys.stderr)
    for app in apps:
        print(f"  {app['name']} ({app['id']})", file=sys.stderr)
    sys.exit(1)


def main():
    parser = argparse.ArgumentParser(prog="discord-dev", description="Manage Discord applications via Developer Portal API")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    sub = parser.add_subparsers(dest="cmd")

    # save-token
    p_save = sub.add_parser("save-token", help="Save Discord user token (from browser extraction)")
    p_save.add_argument("--token", required=True, help="Discord user token")

    # status
    sub.add_parser("status", help="Check auth status")

    # list
    sub.add_parser("list", help="List all applications")

    # create
    p_create = sub.add_parser("create", help="Create a new application")
    p_create.add_argument("name", help="Application name")
    p_create.add_argument("--bot", action="store_true", help="Also create a bot user immediately")

    # delete
    p_delete = sub.add_parser("delete", help="Delete an application")
    p_delete.add_argument("app", help="App name or ID")

    # info
    p_info = sub.add_parser("info", help="Get application details")
    p_info.add_argument("app", help="App name or ID")

    # update
    p_update = sub.add_parser("update", help="Update application settings")
    p_update.add_argument("app", help="App name or ID")
    p_update.add_argument("--name", help="New name")
    p_update.add_argument("--description", help="New description")
    p_update.add_argument("--icon", help="Path to icon image (PNG/JPG/GIF)")
    p_update.add_argument("--public", help="Bot public (true/false)")
    p_update.add_argument("--require-code-grant", help="Require OAuth2 code grant (true/false)")

    # bot-add
    p_bot_add = sub.add_parser("bot-add", help="Add bot user to an application")
    p_bot_add.add_argument("app", help="App name or ID")

    # bot-reset
    p_bot_reset = sub.add_parser("bot-reset", help="Reset (regenerate) bot token")
    p_bot_reset.add_argument("app", help="App name or ID")

    # commands-list
    p_cmd_list = sub.add_parser("commands-list", help="List slash commands")
    p_cmd_list.add_argument("app", help="App name or ID")

    # commands-set
    p_cmd_set = sub.add_parser("commands-set", help="Bulk set slash commands (JSON)")
    p_cmd_set.add_argument("app", help="App name or ID")
    p_cmd_set.add_argument("commands", help='JSON array of commands, or @filename.json')

    # oauth2-url
    p_oauth = sub.add_parser("oauth2-url", help="Generate OAuth2 invite URL")
    p_oauth.add_argument("app", help="App name or ID")
    p_oauth.add_argument("--permissions", help="Permission integer (default 0)")
    p_oauth.add_argument("--scopes", help='Space-separated scopes (default "bot applications.commands")')

    # intents
    p_intents = sub.add_parser("intents", help="View or set privileged gateway intents")
    p_intents.add_argument("app", help="App name or ID")
    p_intents.add_argument("--enable", nargs="+", help="Intents to enable: PRESENCE, GUILD_MEMBERS, MESSAGE_CONTENT")
    p_intents.add_argument("--disable", nargs="+", help="Intents to disable")

    # bot-id
    p_bot_id = sub.add_parser("bot-id", help="Get bot user ID for an application")
    p_bot_id.add_argument("app", help="App name or ID")

    # dm
    p_dm = sub.add_parser("dm", help="Send a DM to a bot (as user) to trigger pairing")
    p_dm.add_argument("--app", help="App name or ID (resolves bot user ID)")
    p_dm.add_argument("--bot-id", help="Bot user ID (if known)")
    p_dm.add_argument("--message", "-m", default="/start", help='Message to send (default: "/start")')

    args = parser.parse_args()

    if not args.cmd:
        parser.print_help()
        sys.exit(1)

    handler = {
        "save-token": cmd_save_token,
        "status": cmd_status,
        "list": cmd_list,
        "create": cmd_create,
        "delete": cmd_delete,
        "info": cmd_info,
        "update": cmd_update,
        "bot-add": cmd_bot_add,
        "bot-reset": cmd_bot_reset,
        "commands-list": cmd_commands_list,
        "commands-set": cmd_commands_set,
        "oauth2-url": cmd_oauth2_url,
        "intents": cmd_intents,
        "bot-id": cmd_bot_id,
        "dm": cmd_dm,
    }[args.cmd]

    handler(args)


if __name__ == "__main__":
    main()
