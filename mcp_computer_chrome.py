import sys
import json
import base64
import os
import asyncio
import mss
import mss.tools
import pyautogui
import pyperclip
from mcp.server.fastmcp import FastMCP
from playwright.async_api import async_playwright

mcp = FastMCP(
    "Luca Beast Automator V3",
    dependencies=["mss", "pyautogui", "playwright", "mcp", "opencv-python", "pyperclip"]
)

# ═══════════════════════════════════════════════
#  COMPUTER CONTROL (OS Level)
# ═══════════════════════════════════════════════

@mcp.tool()
def computer_screenshot() -> str:
    """Take a screenshot of the main monitor and return as base64 png data uri."""
    with mss.mss() as sct:
        monitor = sct.monitors[1]
        sct_img = sct.grab(monitor)
        png_bytes = mss.tools.to_png(sct_img.rgb, sct_img.size)
        return "data:image/png;base64," + base64.b64encode(png_bytes).decode("utf-8")

@mcp.tool()
def computer_mouse_move(x: int, y: int) -> str:
    """Move the mouse to an absolute (x, y) screen coordinate."""
    pyautogui.moveTo(x, y, duration=0.2, tween=pyautogui.easeInOutQuad)
    return f"Moved mouse to ({x}, {y})"

@mcp.tool()
def computer_click(x: int = None, y: int = None, button: str = "left", clicks: int = 1) -> str:
    """Click the mouse. If x,y provided, moves there first. Button: 'left','right','middle'."""
    if x is not None and y is not None:
        pyautogui.moveTo(x, y, duration=0.15)
    pyautogui.click(button=button, clicks=clicks)
    pos = f" at ({x},{y})" if x is not None else ""
    return f"Clicked {button} {clicks} time(s){pos}."

@mcp.tool()
def computer_double_click(x: int, y: int) -> str:
    """Double-click at (x, y)."""
    pyautogui.doubleClick(x, y)
    return f"Double-clicked at ({x}, {y})"

@mcp.tool()
def computer_right_click(x: int, y: int) -> str:
    """Right-click at (x, y) to open context menu."""
    pyautogui.rightClick(x, y)
    return f"Right-clicked at ({x}, {y})"

@mcp.tool()
def computer_mouse_drag(start_x: int, start_y: int, end_x: int, end_y: int, duration: float = 0.5) -> str:
    """Click and drag from start to end coordinates."""
    pyautogui.moveTo(start_x, start_y)
    pyautogui.dragTo(end_x, end_y, duration=duration, button='left')
    return f"Dragged from ({start_x},{start_y}) to ({end_x},{end_y})"

@mcp.tool()
def computer_type_text(text: str, interval: float = 0.02) -> str:
    """Type a string of text on the keyboard."""
    pyautogui.typewrite(text, interval=interval)
    return f"Typed: {text}"

@mcp.tool()
def computer_press_key(key: str) -> str:
    """Press a specific key. Examples: 'enter', 'tab', 'esc', 'backspace', 'f5', 'delete'."""
    pyautogui.press(key)
    return f"Pressed key: {key}"

@mcp.tool()
def computer_hotkey(*keys: str) -> str:
    """Press a keyboard shortcut (hotkey combo). Examples: ('ctrl','c'), ('alt','tab'), ('ctrl','shift','t').
    Pass keys as separate arguments e.g. keys=['ctrl','c']"""
    pyautogui.hotkey(*keys)
    return f"Hotkey pressed: {'+'.join(keys)}"

@mcp.tool()
def computer_hotkey_combo(combo: str) -> str:
    """Press a keyboard shortcut by combo string. Examples: 'ctrl+c', 'alt+tab', 'ctrl+shift+t', 'win+d'."""
    parts = [k.strip() for k in combo.split('+')]
    pyautogui.hotkey(*parts)
    return f"Hotkey pressed: {combo}"

@mcp.tool()
def computer_clipboard_get() -> str:
    """Get the current content of the system clipboard."""
    try:
        return pyperclip.paste()
    except Exception as e:
        return f"Error reading clipboard: {e}"

@mcp.tool()
def computer_clipboard_set(text: str) -> str:
    """Set the system clipboard to the given text."""
    try:
        pyperclip.copy(text)
        return f"Clipboard set to: {text[:80]}{'...' if len(text) > 80 else ''}"
    except Exception as e:
        return f"Error setting clipboard: {e}"

@mcp.tool()
def computer_click_image(image_path: str, confidence: float = 0.8) -> str:
    """Locate an image on the screen using OpenCV fuzzy matching and click its center."""
    try:
        location = pyautogui.locateCenterOnScreen(image_path, confidence=confidence)
        if location:
            pyautogui.click(location)
            return f"Found image at {location} and clicked it."
        else:
            return f"Image {image_path} not found on screen (confidence={confidence})."
    except Exception as e:
        return f"Error finding/clicking image: {e}"

@mcp.tool()
def computer_scroll(x: int, y: int, clicks: int = 3, direction: str = "down") -> str:
    """Scroll at screen position (x,y). direction: 'up' or 'down'."""
    amount = -clicks if direction == "down" else clicks
    pyautogui.scroll(amount, x=x, y=y)
    return f"Scrolled {direction} {abs(clicks)} clicks at ({x},{y})"

@mcp.tool()
def computer_get_screen_size() -> str:
    """Get the screen resolution."""
    w, h = pyautogui.size()
    return f"Screen size: {w}x{h}"

@mcp.tool()
def computer_get_mouse_position() -> str:
    """Get the current mouse cursor position."""
    x, y = pyautogui.position()
    return f"Mouse at ({x}, {y})"

# ═══════════════════════════════════════════════
#  CHROME BROWSER CONTROL (Playwright V3)
# ═══════════════════════════════════════════════

_playwright_instance = None
_browser = None
_context = None
_lock = asyncio.Lock()

STATE_FILE = os.path.join(os.path.dirname(__file__), "browser_state.json")

CHROME_UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36"

async def get_browser_context():
    global _playwright_instance, _browser, _context
    async with _lock:
        if _context is None:
            if _playwright_instance is None:
                _playwright_instance = await async_playwright().start()
            if _browser is None or not _browser.is_connected():
                _browser = await _playwright_instance.chromium.launch(
                    headless=False,
                    channel="chrome",
                    args=[
                        "--disable-blink-features=AutomationControlled",
                        "--start-maximized",
                        "--no-first-run",
                        "--disable-infobars",
                    ]
                )
            ctx_kwargs = dict(
                viewport={'width': 1920, 'height': 1080},
                user_agent=CHROME_UA,
                locale="ko-KR",
                timezone_id="Asia/Seoul",
            )
            if os.path.exists(STATE_FILE):
                ctx_kwargs["storage_state"] = STATE_FILE
            _context = await _browser.new_context(**ctx_kwargs)
            await _context.add_init_script(
                "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
            )
            if len(_context.pages) == 0:
                await _context.new_page()
    return _context

async def get_active_page():
    context = await get_browser_context()
    if len(context.pages) > 0:
        return context.pages[-1]
    return await context.new_page()

async def save_browser_state():
    global _context
    if _context:
        try:
            await _context.storage_state(path=STATE_FILE)
        except Exception:
            pass

# ── Navigation ──

@mcp.tool()
async def browser_navigate(url: str, wait_until: str = "domcontentloaded") -> str:
    """Open Chrome and navigate to the given URL.
    wait_until options: 'load', 'domcontentloaded', 'networkidle'"""
    page = await get_active_page()
    await page.goto(url, wait_until=wait_until, timeout=30000)
    await save_browser_state()
    return f"Navigated to {url}\nTitle: {await page.title()}\nURL: {page.url}"

@mcp.tool()
async def browser_go_back() -> str:
    """Navigate browser back."""
    page = await get_active_page()
    await page.go_back()
    return f"Went back. Now at: {page.url}"

@mcp.tool()
async def browser_go_forward() -> str:
    """Navigate browser forward."""
    page = await get_active_page()
    await page.go_forward()
    return f"Went forward. Now at: {page.url}"

@mcp.tool()
async def browser_reload() -> str:
    """Reload the current page."""
    page = await get_active_page()
    await page.reload(wait_until="domcontentloaded")
    return f"Page reloaded. Title: {await page.title()}"

@mcp.tool()
async def browser_get_current_url() -> str:
    """Get the current page URL and title."""
    page = await get_active_page()
    return f"URL: {page.url}\nTitle: {await page.title()}"

# ── Tab Management ──

@mcp.tool()
async def browser_new_tab(url: str = "about:blank") -> str:
    """Open a new browser tab, optionally navigating to a URL."""
    context = await get_browser_context()
    page = await context.new_page()
    if url != "about:blank":
        await page.goto(url, wait_until="domcontentloaded")
    return f"New tab opened. Title: {await page.title()}, URL: {page.url}"

@mcp.tool()
async def browser_close_tab(index: int = -1) -> str:
    """Close a browser tab by index. -1 closes the active (last) tab."""
    context = await get_browser_context()
    if not context.pages:
        return "No tabs to close."
    idx = index if index >= 0 else len(context.pages) - 1
    if idx >= len(context.pages):
        return f"Invalid index {idx}"
    await context.pages[idx].close()
    return f"Closed tab at index {idx}. Remaining tabs: {len(context.pages)}"

@mcp.tool()
async def browser_list_tabs() -> str:
    """List all currently open browser tabs with index, URL, and title."""
    context = await get_browser_context()
    if not context.pages:
        return "No tabs are open."
    result = []
    for idx, p in enumerate(context.pages):
        try:
            title = await p.title()
            active_marker = " ← ACTIVE" if idx == len(context.pages) - 1 else ""
            result.append(f"[{idx}] {title[:60]} | {p.url}{active_marker}")
        except Exception:
            result.append(f"[{idx}] (unavailable)")
    return "Open Tabs:\n" + "\n".join(result)

@mcp.tool()
async def browser_switch_tab(index: int) -> str:
    """Switch active tab to the specified index (from browser_list_tabs)."""
    context = await get_browser_context()
    if index < 0 or index >= len(context.pages):
        return f"Error: Invalid tab index {index}. Total: {len(context.pages)}"
    page = context.pages[index]
    await page.bring_to_front()
    # Move to end to maintain "last = active" logic
    pages = context.pages
    pages.append(pages.pop(index))
    return f"Switched to tab [{index}]: {await page.title()}"

# ── Element Interaction (Vimium Badge System) ──

_BADGE_JS = """
() => {
    document.querySelectorAll('.luca-tag').forEach(e => e.remove());
    let idCounter = 1;
    let interactables = [];

    const selectors = [
        'a[href]', 'button', 'input:not([type="hidden"])', 'select', 'textarea',
        '[role="button"]', '[role="link"]', '[role="menuitem"]', '[role="tab"]',
        '[role="checkbox"]', '[role="radio"]', '[role="combobox"]', '[role="option"]',
        '[contenteditable="true"]', '[tabindex]:not([tabindex="-1"])'
    ].join(', ');

    const vw = window.innerWidth || document.documentElement.clientWidth;
    const vh = window.innerHeight || document.documentElement.clientHeight;

    document.querySelectorAll(selectors).forEach(el => {
        const rect = el.getBoundingClientRect();
        if (rect.width < 2 || rect.height < 2) return;
        if (rect.top < 0 || rect.bottom > vh || rect.left < 0 || rect.right > vw) return;

        const style = window.getComputedStyle(el);
        if (style.display === 'none' || style.visibility === 'hidden' || style.opacity === '0') return;

        const id = idCounter++;
        el.setAttribute('data-luca-id', id);

        const text = (el.innerText || el.value || el.placeholder ||
            el.getAttribute('aria-label') || el.getAttribute('title') ||
            el.getAttribute('alt') || '').trim().substring(0, 50);

        interactables.push({ id, tag: el.tagName.toLowerCase(), type: el.type || '', text });

        const badge = document.createElement('div');
        badge.className = 'luca-tag';
        badge.innerText = id;
        Object.assign(badge.style, {
            position: 'absolute',
            left: (rect.left + window.scrollX) + 'px',
            top: (rect.top + window.scrollY) + 'px',
            backgroundColor: '#E53935',
            color: '#FFFFFF',
            padding: '1px 4px',
            fontSize: '11px',
            fontWeight: 'bold',
            zIndex: '9999999',
            pointerEvents: 'none',
            borderRadius: '3px',
            boxShadow: '0 1px 3px rgba(0,0,0,0.5)',
            fontFamily: 'monospace',
            lineHeight: '1.4',
        });
        document.body.appendChild(badge);
    });
    return interactables;
}
"""

@mcp.tool()
async def browser_mark_elements() -> str:
    """[VIMIUM-STYLE] Inject numbered red badges over all interactive elements.
    Returns JSON with base64 screenshot and element list."""
    page = await get_active_page()
    await page.wait_for_timeout(500)
    elements_info = await page.evaluate(_BADGE_JS)
    png_bytes = await page.screenshot()
    img_b64 = "data:image/png;base64," + base64.b64encode(png_bytes).decode("utf-8")
    await save_browser_state()
    return json.dumps({
        "image_data_uri": img_b64,
        "interactable_elements": elements_info,
        "total": len(elements_info)
    }, ensure_ascii=False)

@mcp.tool()
async def browser_click_badge(luca_id: int) -> str:
    """Click an element by its badge ID from browser_mark_elements()."""
    page = await get_active_page()
    el = await page.query_selector(f'[data-luca-id="{luca_id}"]')
    if el:
        await el.scroll_into_view_if_needed()
        await el.hover()
        await page.wait_for_timeout(80)
        await el.click()
        await save_browser_state()
        return f"Clicked element ID {luca_id}"
    return f"Error: Element ID {luca_id} not found."

@mcp.tool()
async def browser_hover_badge(luca_id: int) -> str:
    """Hover over an element by badge ID (useful for dropdowns/tooltips)."""
    page = await get_active_page()
    el = await page.query_selector(f'[data-luca-id="{luca_id}"]')
    if el:
        await el.scroll_into_view_if_needed()
        await el.hover()
        return f"Hovered over element ID {luca_id}"
    return f"Error: Element ID {luca_id} not found."

@mcp.tool()
async def browser_fill_badge(luca_id: int, text: str, clear_first: bool = True) -> str:
    """Fill a text input/textarea by badge ID."""
    page = await get_active_page()
    el = await page.query_selector(f'[data-luca-id="{luca_id}"]')
    if el:
        await el.scroll_into_view_if_needed()
        if clear_first:
            await el.fill("")
        await el.fill(text)
        await save_browser_state()
        return f"Filled element ID {luca_id}"
    return f"Error: Element ID {luca_id} not found."

@mcp.tool()
async def browser_select_option(luca_id: int, value: str = None, label: str = None) -> str:
    """Select a dropdown option by badge ID. Provide value OR label."""
    page = await get_active_page()
    el = await page.query_selector(f'[data-luca-id="{luca_id}"]')
    if el:
        if value:
            await el.select_option(value=value)
        elif label:
            await el.select_option(label=label)
        await save_browser_state()
        return f"Selected option in element ID {luca_id}"
    return f"Error: Element ID {luca_id} not found."

@mcp.tool()
async def browser_upload_file(luca_id: int, file_path: str) -> str:
    """Upload a file to an <input type='file'> element by badge ID."""
    page = await get_active_page()
    el = await page.query_selector(f'[data-luca-id="{luca_id}"]')
    if el:
        await el.set_input_files(file_path)
        return f"File '{file_path}' uploaded to element ID {luca_id}"
    return f"Error: Element ID {luca_id} not found."

# ── Waiting ──

@mcp.tool()
async def browser_wait_for_selector(selector: str, timeout_ms: int = 10000, state: str = "visible") -> str:
    """Wait for a CSS selector to appear. state: 'visible','hidden','attached','detached'."""
    page = await get_active_page()
    try:
        await page.wait_for_selector(selector, timeout=timeout_ms, state=state)
        return f"Selector '{selector}' is now {state}."
    except Exception as e:
        return f"Timeout waiting for '{selector}': {e}"

@mcp.tool()
async def browser_wait_for_navigation(timeout_ms: int = 10000) -> str:
    """Wait for the page to finish navigating."""
    page = await get_active_page()
    try:
        await page.wait_for_load_state("domcontentloaded", timeout=timeout_ms)
        return f"Navigation complete. URL: {page.url}"
    except Exception as e:
        return f"Navigation wait error: {e}"

@mcp.tool()
async def browser_sleep(ms: int = 1000) -> str:
    """Wait for specified milliseconds (for pages that need time to render)."""
    await asyncio.sleep(ms / 1000)
    return f"Waited {ms}ms."

# ── Reading Page Content ──

@mcp.tool()
async def browser_screenshot() -> str:
    """Take a clean screenshot of the current browser page (no badges)."""
    page = await get_active_page()
    # Remove any existing badges first
    await page.evaluate("() => document.querySelectorAll('.luca-tag').forEach(e => e.remove())")
    png_bytes = await page.screenshot(full_page=False)
    return "data:image/png;base64," + base64.b64encode(png_bytes).decode("utf-8")

@mcp.tool()
async def browser_screenshot_full() -> str:
    """Take a full-page screenshot (scrolls to capture entire page)."""
    page = await get_active_page()
    await page.evaluate("() => document.querySelectorAll('.luca-tag').forEach(e => e.remove())")
    png_bytes = await page.screenshot(full_page=True)
    return "data:image/png;base64," + base64.b64encode(png_bytes).decode("utf-8")

@mcp.tool()
async def browser_get_markdown() -> str:
    """Extract the page content as clean text (token-efficient)."""
    page = await get_active_page()
    text = await page.evaluate("() => document.body.innerText")
    return text[:20000]  # Cap at 20k chars

@mcp.tool()
async def browser_get_page_source() -> str:
    """Get the raw HTML source of the current page."""
    page = await get_active_page()
    content = await page.content()
    return content[:50000]  # Cap at 50k chars

@mcp.tool()
async def browser_get_element_text(selector: str) -> str:
    """Get the text content of the first element matching a CSS selector."""
    page = await get_active_page()
    try:
        el = await page.query_selector(selector)
        if el:
            return await el.inner_text()
        return f"No element found for selector: {selector}"
    except Exception as e:
        return f"Error: {e}"

@mcp.tool()
async def browser_find_text(text: str) -> str:
    """Check if specific text exists on the current page. Returns location info."""
    page = await get_active_page()
    try:
        els = await page.get_by_text(text, exact=False).all()
        if els:
            return f"Found '{text}' in {len(els)} element(s) on the page."
        return f"Text '{text}' not found on page."
    except Exception as e:
        return f"Error: {e}"

# ── Keyboard & Interaction ──

@mcp.tool()
async def browser_press_key(key: str) -> str:
    """Press a key in the active browser tab. Examples: 'Enter','Tab','Escape','ArrowDown','F5'."""
    page = await get_active_page()
    await page.keyboard.press(key)
    return f"Pressed '{key}' in browser."

@mcp.tool()
async def browser_type_text(text: str) -> str:
    """Type text character by character in the browser (for focused input fields)."""
    page = await get_active_page()
    await page.keyboard.type(text, delay=30)
    return f"Typed text in browser."

@mcp.tool()
async def browser_scroll(direction: str = "down", amount_pixels: int = 800) -> str:
    """Scroll the active page up or down by pixels."""
    page = await get_active_page()
    delta = amount_pixels if direction == "down" else -amount_pixels
    await page.evaluate(f"window.scrollBy(0, {delta})")
    return f"Scrolled {direction} by {amount_pixels}px."

@mcp.tool()
async def browser_scroll_to_bottom() -> str:
    """Scroll to the very bottom of the page."""
    page = await get_active_page()
    await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
    return "Scrolled to bottom of page."

@mcp.tool()
async def browser_scroll_to_top() -> str:
    """Scroll to the very top of the page."""
    page = await get_active_page()
    await page.evaluate("window.scrollTo(0, 0)")
    return "Scrolled to top of page."

# ── JavaScript Execution ──

@mcp.tool()
async def browser_evaluate_js(script: str) -> str:
    """Evaluate raw JavaScript on the current page and return the result."""
    page = await get_active_page()
    try:
        res = await page.evaluate(script)
        await save_browser_state()
        return str(res)
    except Exception as e:
        return f"JS Error: {e}"

@mcp.tool()
async def browser_click_by_selector(selector: str) -> str:
    """Click an element using a CSS selector directly (advanced use)."""
    page = await get_active_page()
    try:
        await page.click(selector, timeout=5000)
        await save_browser_state()
        return f"Clicked selector: {selector}"
    except Exception as e:
        return f"Error clicking selector '{selector}': {e}"

@mcp.tool()
async def browser_fill_by_selector(selector: str, text: str) -> str:
    """Fill an input element using a CSS selector directly (advanced use)."""
    page = await get_active_page()
    try:
        await page.fill(selector, text, timeout=5000)
        await save_browser_state()
        return f"Filled selector: {selector}"
    except Exception as e:
        return f"Error filling selector '{selector}': {e}"

# ── Session Management ──

@mcp.tool()
async def browser_save_session() -> str:
    """Manually save the browser session (cookies, localStorage) to disk."""
    await save_browser_state()
    return f"Session saved to {STATE_FILE}"

@mcp.tool()
async def browser_clear_session() -> str:
    """Clear the saved browser session file (logout all sites)."""
    global _context
    if os.path.exists(STATE_FILE):
        os.remove(STATE_FILE)
    _context = None
    return "Session cleared. Next browser action will start a fresh session."

@mcp.tool()
async def browser_get_cookies() -> str:
    """Get all cookies for the current page."""
    context = await get_browser_context()
    page = await get_active_page()
    cookies = await context.cookies([page.url])
    return json.dumps(cookies, ensure_ascii=False, indent=2)

# ── Dialog Handling ──

@mcp.tool()
async def browser_dismiss_dialog() -> str:
    """Setup auto-dismissal for next alert/confirm/prompt dialog."""
    page = await get_active_page()
    page.once("dialog", lambda dialog: asyncio.ensure_future(dialog.dismiss()))
    return "Dialog auto-dismiss armed."

@mcp.tool()
async def browser_accept_dialog(prompt_text: str = "") -> str:
    """Setup auto-accept for next alert/confirm/prompt dialog. Optionally provide prompt text."""
    page = await get_active_page()
    async def handle(dialog):
        await dialog.accept(prompt_text)
    page.once("dialog", handle)
    return "Dialog auto-accept armed."


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Luca Beast Automator MCP V3")
    parser.add_argument("--test", action="store_true", help="Run a quick internal test")
    args = parser.parse_args()

    if args.test:
        print("V3 Beast Automator loaded successfully.")
        sys.exit(0)

    mcp.run()
