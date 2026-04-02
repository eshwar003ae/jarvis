import os
import subprocess
import sys
import logging
import asyncio
from fuzzywuzzy import process
from langchain.tools import tool

# Reconfigure encoding for console output
sys.stdout.reconfigure(encoding='utf-8')

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- LINUX COMPATIBLE WINDOW FOCUS ---
async def focus_window(title_keyword: str) -> bool:
    """Focuses a window based on a keyword in its title (Cross-Platform)."""
    await asyncio.sleep(1.5)
    title_keyword = title_keyword.lower().strip()

    # LINUX LOGIC
    if sys.platform.startswith('linux'):
        try:
            # Using 'wmctrl' which is common on Linux for window management
            # To install: sudo apt-get install wmctrl
            subprocess.run(['wmctrl', '-a', title_keyword], check=True)
            logger.info(f"🪟 Linux window focus attempted for: {title_keyword}")
            return True
        except Exception as e:
            logger.warning(f"⚠ Linux focus failed (is wmctrl installed?): {e}")
            return False

    # WINDOWS LOGIC (Fallback)
    else:
        try:
            import pygetwindow as gw
            for window in gw.getAllWindows():
                if title_keyword in window.title.lower():
                    if window.isMinimized:
                        window.restore()
                    window.activate()
                    logger.info(f"🪟 Windows focus: {window.title}")
                    return True
        except ImportError:
            logger.warning("⚠ pygetwindow not found for Windows focus.")
        except Exception as e:
            logger.warning(f"⚠ Windows focus error: {e}")
    
    return False

# --- FILE INDEXING & SEARCH ---
async def index_files(base_dirs):
    file_index = []
    # Change "D:/" to "/" or your Home directory for Linux testing
    actual_dirs = [d for d in base_dirs if os.path.exists(d)]
    
    for base_dir in actual_dirs:
        for root, _, files in os.walk(base_dir):
            for f in files:
                file_index.append({
                    "name": f,
                    "path": os.path.join(root, f),
                    "type": "file"
                })
    logger.info(f"✅ Indexed {len(file_index)} files from {actual_dirs}.")
    return file_index

async def search_file(query, index):
    choices = [item["name"] for item in index]
    if not choices:
        return None
    
    best_match, score = process.extractOne(query, choices)
    if score > 70:
        for item in index:
            if item["name"] == best_match:
                return item
    return None

async def open_file(item):
    try:
        logger.info(f"📂 Opening: {item['path']}")
        if os.name == 'nt':
            os.startfile(item["path"])
        else:
            # Use 'xdg-open' for Linux/Ubuntu
            subprocess.call(['xdg-open', item["path"]])
        
        await focus_window(item["name"])
        return f"✅ File open: {item['name']}"
    except Exception as e:
        return f"❌ Failed to open file: {e}"

# --- TOOL DEFINITION ---
@tool
async def Play_file(name: str) -> str:
    """Searches for and opens a file by name. Works on Windows and Linux."""
    # Note: On Linux, you usually don't have a "D:/" drive. 
    # I recommend adding your Linux home folder to this list.
    folders_to_index = ["D:/", os.path.expanduser("~/Documents")]
    
    index = await index_files(folders_to_index)
    item = await search_file(name.strip(), index)
    
    if item:
        return await open_file(item)
    return "❌ File not found."
