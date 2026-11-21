# PBZ Bot

Discord community tools for PBZ, including opt-in roles, server statistics, moderation, and Roblox commands.

## Purpose and audience

PBZ Bot was built for a Discord community around Roblox games. Members can choose notification roles, play chat games and look up Roblox profiles. Moderators can manage messages and member timeouts in the same server.

## How it works

The slash-command groups live in `main.py`. A background task updates channel names with member and online counts every fifteen minutes. Roblox account lookup uses Bloxlink. The game kick command publishes a message to a configured Roblox universe where a separate game-side subscriber must handle it. The historical DevEx estimate uses the conversion factor embedded in the 2024 source.

## Quick start

From the repository root, use Python 3.12 in a virtual environment. The following commands use a POSIX shell. In PowerShell, activate the environment with `.venv\Scripts\Activate.ps1` and use `Copy-Item` in place of `cp`.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
cp settings.example.json settings.json
```

## Configuration

Set `DISCORD_TOKEN` in `.env`. The optional `API_LEAGUE_KEY` serves jokes, riddles and memes, `BLOXLINK_API_KEY` serves linked Roblox profiles, and `ROBLOX_OPEN_CLOUD_KEY` authorizes Messaging Service publishing for the selected universe. Set only the integrations you intend to run.

In `settings.json`, enter the Discord server ID, statistics channel IDs, opt-in role IDs and the universe ID. The game moderator role authorizes the game kick command. The large-purge role is an additional requirement for purges of 200 or more messages.

Enable the Server Members, Presence and Message Content intents. Grant the bot permissions for the features you use, including Manage Channels for counters and Manage Roles for opt-in roles. Discord moderation also requires the corresponding bot and caller permissions. Keep the bot's role above the roles it manages.

## Deployment and commands

Start the bot with `python main.py` after filling in its configuration. A deployment needs one running Python process with the same configuration as the local run. An existing process environment takes precedence over `.env`.

Try `/bot ping`, `/game flip`, `/random number` or `/toggle` in the configured server. The `/fetch` group serves images, jokes and riddles. The `/roblox` and `/mod` groups contain lookup and moderation commands.

## Testing and troubleshooting

Run `python -m py_compile main.py` for a syntax check. CI installs the dependencies and checks command registration offline. To check the Discord connection and provider responses, use the commands above in a test server.

For missing counters, check channel IDs, Manage Channels and the presence intent. For Roblox lookups or game messages, check the provider key and its scope. The game must subscribe to the expected topic for an in-game kick to take effect.

## Project history and release status

The original `main.py` was created August 7 and last modified August 30, 2024 (UTC filesystem timestamps). A comment in the original source dates the server rules to August 21, 2024. The first public release date is unknown.

This repository preserves the source as a historical project. No versioned release is recorded.

## Support and security

Open a repository issue for a reproducible bug. For credentials or vulnerabilities, use the private reporting route in [SECURITY.md](SECURITY.md). The [license notice](LICENSE) records the project's reuse terms.
