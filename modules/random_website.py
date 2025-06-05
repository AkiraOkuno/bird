# random_site_bot.py

import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException, WebDriverException

RANDOM_SITE_URL = "http://random.whatsmyip.org/"
TIMEOUT = 15  # seconds to wait for the JS-injected link

def fetch_random_site(timeout: int = TIMEOUT) -> str | None:
    """
    Uses Selenium + headless Chromium to navigate to RANDOM_SITE_URL,
    waits for <a id="random_link"> to get a non-empty href, and returns it.
    Returns None on failure.
    """
    try:
        # 1) Tell Selenium exactly where chromedriver is on Ubuntu:
        driver_path = "/usr/lib/chromium-browser/chromedriver"
        service = ChromeService(driver_path)

        # 2) Configure headless Chromium with required flags:
        options = webdriver.ChromeOptions()
        options.binary_location = "/usr/bin/chromium-browser"
        # Fallback to /usr/bin/chromium if needed:
        if not os.path.exists(options.binary_location):
            alt = "/usr/bin/chromium"
            if os.path.exists(alt):
                options.binary_location = alt

        # Essential headless flags:
        options.add_argument("--headless")            # use legacy headless mode
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--remote-debugging-port=0")

        driver = webdriver.Chrome(service=service, options=options)

        try:
            driver.get(RANDOM_SITE_URL)
            locator = (By.ID, "random_link")
            WebDriverWait(driver, timeout).until(
                lambda d: (
                    d.find_element(*locator).get_attribute("href")
                    and d.find_element(*locator).get_attribute("href").strip() != ""
                )
            )
            return driver.find_element(*locator).get_attribute("href")
        finally:
            driver.quit()

    except (TimeoutException, WebDriverException) as e:
        print(f"[SELENIUM] Error: {e}", flush=True)
        return None

def generate() -> str:
    """
    Returns a string like:
      🌐 *Website aleatório do dia: *
      https://some-random-site.example

    Falls back to an error message if Selenium fails.
    """
    link = fetch_random_site(timeout=TIMEOUT)
    if link:
        return f"🌐 *Website aleatório do dia: *\n{link}"
    else:
        return "⚠️ Não consegui obter o site aleatório hoje."
