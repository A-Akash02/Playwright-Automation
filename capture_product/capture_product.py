import json
import asyncio
from playwright.async_api import async_playwright

# Constants for session file and URLs
SESSION_FILE = "session.json"
LOGIN_URL = "https://hiring.idenhq.com/"
INSTRUCTION_PAGE = "https://hiring.idenhq.com/instructions"
PRODUCT_PAGE = "https://hiring.idenhq.com/challenge"

async def save_session(context):
    """Saves browser session to a file."""
    cookies = await context.cookies()
    with open(SESSION_FILE, "w") as f:
        json.dump(cookies, f)

async def load_session(context):
    """Loads browser session from a file if available."""
    try:
        with open(SESSION_FILE, "r") as f:
            cookies = json.load(f)
            await context.add_cookies(cookies)
            return True
    except FileNotFoundError:
        return False

async def authenticate(page):
    """Logs into the application if no session exists."""
    await page.goto(LOGIN_URL)
    await page.wait_for_load_state("domcontentloaded")
    await page.fill("#email", "Enter email") 
    await page.fill("#password", "Enter Password") 
    await page.click("button[type='submit']")
    
    # Wait for the dashboard to load
    await page.wait_for_load_state("networkidle")
    print("Post-login URL:", page.url)

async def navigate_instruction(page):
    """Navigates to the instruction page and clicks 'Launch Challenge'."""
    await page.goto(INSTRUCTION_PAGE)
    await page.wait_for_selector("button:has-text('Launch Challenge')")
    launch_button = page.locator("button:has-text('Launch Challenge')")
    if await launch_button.is_visible():
        await launch_button.click()
        await page.wait_for_load_state("domcontentloaded")
        print("Navigated to challenge page.")
    else:
        print("'Launch Challenge' button not found or not visible.")

async def navigate_to_product_table(page):
    """Navigates to the product table."""
    await page.wait_for_timeout(2000)
    await page.get_by_role("button", name="Start Journey").click()
    await page.wait_for_timeout(2000)  # Wait for 2 seconds

    # Click 'Continue Search' button
    await page.get_by_role("button", name="Continue Search").click()
    await page.wait_for_timeout(2000)  # Wait for 2 seconds

    # Click 'Inventory Section' button
    await page.get_by_role("button", name="Inventory Section").click()
    await page.wait_for_timeout(2000)


##change
async def go_to_last_page(page):
    """Navigates to the last page of the product list."""
    while True:
        # Check if the 'Next' button exists and is visible
        next_button = page.locator("button:has-text('Next')")
        if await next_button.is_visible():
            await next_button.click()
            await page.wait_for_timeout(3000)  # Wait for next page to load
        else:
            break  # No more pages, exit loop

async def take_screenshot(page, filename="last_page.png"):
    """Takes a screenshot of the last page."""
    await page.screenshot(path=filename, full_page=True)
    print(f"Screenshot saved as {filename}")

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # Disable headless mode for debugging
        context = await browser.new_context()
        page = await context.new_page()

        session_loaded = await load_session(context)
        if not session_loaded:
            await authenticate(page)
            await save_session(context)
        
        await navigate_instruction(page)  # Navigate to instructions & launch challenge
        
        print("Current URL:", page.url)
        
        await page.goto(PRODUCT_PAGE)
        await navigate_to_product_table(page)
        
        # Go to the last page
        await go_to_last_page(page)

        # Take a screenshot of the last page
        await take_screenshot(page, filename="last_page.png")
        
        await browser.close()

# Run the main function
asyncio.run(main())
