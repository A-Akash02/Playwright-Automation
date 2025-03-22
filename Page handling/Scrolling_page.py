import json, os
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
    await page.fill("#email", "Enter Email ID")  
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
    await page.wait_for_timeout(2000)

    # Click 'Continue Search' button
    await page.get_by_role("button", name="Continue Search").click()
    await page.wait_for_timeout(2000)

    # Click 'Inventory Section' button
    await page.get_by_role("button", name="Inventory Section").click()
    await page.wait_for_timeout(2000)

async def load_all_products(page):
    """Scrolls through the page to load all products."""
    last_height = await page.evaluate("document.body.scrollHeight")
    
    while True:
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await page.wait_for_timeout(2000)  # Wait for new products to load

        new_height = await page.evaluate("document.body.scrollHeight")
        if new_height == last_height:
            break  # Stop when no new products load
        last_height = new_height

async def scrape_product_data(page):
    """Scrapes product details from the page and takes screenshots of each product."""


    product_cards = await page.locator(".product-card").all()  # Modify selector if needed
    products = []

    for index, card in enumerate(product_cards):
        # Scroll to the product card to ensure visibility
        await card.scroll_into_view_if_needed()
        await page.wait_for_timeout(500)  # Add a small delay to ensure smooth scrolling
        
        # Take a screenshot of the product


        # Extract product details (modify as per actual selectors)
        title = await card.locator(".product-title").text_content()
        price = await card.locator(".product-price").text_content()

        products.append({
            "title": title.strip() if title else "N/A",
            "price": price.strip() if price else "N/A",
        })
    
    return products
async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # Set headless=True if you don't want UI
        context = await browser.new_context()
        page = await context.new_page()

        session_loaded = await load_session(context)
        if not session_loaded:
            await authenticate(page)
            await save_session(context)

        await navigate_instruction(page)
        await navigate_to_product_table(page)
        await load_all_products(page)

        products = await scrape_product_data(page)
        print(products)

        await browser.close()

asyncio.run(main())
