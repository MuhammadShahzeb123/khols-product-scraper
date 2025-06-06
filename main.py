import asyncio
import random
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

async def run():
    async with async_playwright() as p:
        # Configure browser with stealth settings
        browser = await p.chromium.launch(
            headless=False,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-infobars',
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-web-security',
                f'--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{random.randint(100,115)}.0.0.0 Safari/537.36'
            ]
        )
        
        context = await browser.new_context(
            viewport={'width': 1366, 'height': 768},
            locale='en-US',
            timezone_id='America/New_York',
            color_scheme='light'
        )
        
        # Block unnecessary resources
        await context.route("**/*.{png,jpg,jpeg,gif,svg,woff,woff2,eot,ttf,otf}", lambda route: route.abort())
        
        page = await context.new_page()
        
        try:
            # Human-like navigation pattern
            await page.goto('https://www.kohls.com/', wait_until='domcontentloaded')
            await human_delay()
            
            # Simulate mouse movements
            await page.mouse.move(100, 100)
            for _ in range(5):
                await page.mouse.move(
                    random.randint(100, 300),
                    random.randint(100, 300),
                    steps=5
                )
                await asyncio.sleep(0.2)
            
            # Go to target page
            await page.goto(
                'https://www.kohls.com/catalog/small-appliances-kitchen-dining.jsp?CN=Category:Small%20Appliances+Department:Kitchen%20%26%20Dining&cc=for_thehome-TN3.0-S-KitchenAppliances&kls_sbp=51315730140270284583322764306131642956',
                wait_until='networkidle',
                timeout=60000
            )
            
            # Human-like scrolling
            scroll_distance = random.randint(200, 500)
            for _ in range(5):
                await page.mouse.wheel(0, scroll_distance)
                await human_delay(0.5, 1.5)
                scroll_distance = random.randint(100, 300)
            
            # Wait for products container
            await page.wait_for_selector('#productsContainer', state='attached', timeout=30000)
            await human_delay()
            
            print("Products found, extracting data...")
            container = await page.query_selector('#productsContainer')
            html = await container.inner_html()
            
            # Parse with BeautifulSoup
            soup = BeautifulSoup(html, 'html.parser')
            products = soup.find_all('li', class_='products_grid')
            
            # Extract product data
            for product in products:
                data_id = product.get('data-id', 'N/A')
                
                # Name extraction
                name_block = product.find('div', class_='prod_nameBlock')
                name = name_block.get_text(strip=True) if name_block else 'N/A'
                
                # Price extraction
                sale_price = 'N/A'
                original_price = 'N/A'
                price_block = product.find('span', class_='prod_price_amount')
                if price_block:
                    sale_price = price_block.get_text(strip=True)
                    orig_block = product.find('div', class_='prod_price_original')
                    if orig_block:
                        original_price = orig_block.get_text(strip=True).replace('Reg.', '').strip()
                
                # Rating extraction
                rating = 'N/A'
                rating_block = product.find('a', class_='stars')
                if rating_block:
                    class_list = rating_block.get('class', [])
                    rating_class = next((c for c in class_list if c.startswith('stars-')), None)
                    if rating_class:
                        rating = rating_class.replace('stars-', '').replace('-', '.')
                
                # Review count
                review_count = 'N/A'
                reviews_block = product.find('span', class_='prod_ratingCount')
                if reviews_block:
                    review_count = reviews_block.get_text(strip=True).strip('()')
                
                print(f"\nProduct ID: {data_id}")
                print(f"Name: {name}")
                print(f"Sale Price: {sale_price}")
                print(f"Original Price: {original_price}")
                print(f"Rating: {rating}")
                print(f"Reviews: {review_count}")
                print("-" * 50)
            
        finally:
            await browser.close()

async def human_delay(min_sec=0.3, max_sec=2.0):
    await asyncio.sleep(random.uniform(min_sec, max_sec))

if __name__ == '__main__':
    asyncio.run(run())