import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager

# ──────────────────────────────────────────────────────────────────────────────
# This script fetches a random website from http://random.whatsmyip.org/
# using headless Chromium + Selenium. At the end, it exposes a function
# `generate()` that returns a string in the format:
#
#    🌐 *Website aleatório do dia: *
#    https://some-random-site.example
#
# If anything goes wrong, it will return an error message instead.
# ──────────────────────────────────────────────────────────────────────────────

RANDOM_SITE_URL = "http://random.whatsmyip.org/"

def fetch_random_website(timeout: int = 5) -> str | None:
    """
    Launches headless Chromium, points it at RANDOM_SITE_URL, waits until
    the <a id="random_link"> element receives a non-empty href, and returns
    that href string. If there is a timeout or WebDriver error, returns None.
    """
    try:
        # 1) Let webdriver-manager download the matching ChromeDriver
        driver_path = ChromeDriverManager().install()
        service = ChromeService(driver_path)

        # 2) Configure headless Chromium
        options = webdriver.ChromeOptions()
        # On most Linux CI runners or local Linux, chromium-browser is at this path.
        options.binary_location = "/usr/bin/chromium-browser"
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        driver = webdriver.Chrome(service=service, options=options)

        try:
            # 3) Open the Random Website Machine page
            driver.get(RANDOM_SITE_URL)

            # 4) Wait until <a id="random_link"> has a non-empty href attribute
            locator = (By.ID, "random_link")
            WebDriverWait(driver, timeout).until(
                lambda d: d.find_element(*locator).get_attribute("href")
                         and d.find_element(*locator).get_attribute("href").strip() != ""
            )

            # 5) Return the href value
            return driver.find_element(*locator).get_attribute("href")
        finally:
            driver.quit()

    except (TimeoutException, WebDriverException) as e:
        # Log to stdout/stderr if you want, or just return None
        print(f"[RANDOM_SITE] Error fetching random website: {e}", flush=True)
        return None

def generate() -> str:
    """
    Fetches a random website using fetch_random_website(). If successful,
    returns a string like:

      🌐 *Website aleatório do dia: *
      https://some-random-site.example

    If unsuccessful, returns an error message in Portuguese.
    """
    url = fetch_random_website(timeout=15)
    if url:
        return f"🌐 *Website aleatório do dia: *\n{url}"
    else:
        return "⚠️ Não consegui obter o site aleatório hoje."
