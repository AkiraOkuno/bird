import os
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager

# ──────────────────────────────────────────────────────────────────────────────
# CONFIGURATION
# ──────────────────────────────────────────────────────────────────────────────

RANDOM_SITE_URL = "http://random.whatsmyip.org/"
TIMEOUT = 15  # how many seconds to wait for the <a id="random_link"> href to appear

# ──────────────────────────────────────────────────────────────────────────────
# FIRST FALLBACK: Pure-requests + BeautifulSoup
#
# If Selenium + headless Chrome fails altogether, we can try a fallback that
# fetches the RANDOM_SITE_URL HTML via requests, parses out the JS‐injected link,
# and returns it. In practice, random.whatsmyip.org relies on inline JS, so the
# <a id="random_link"> won't exist in the raw HTML. However, some users have
# reported that occasionally the page will have a <noscript> fallback or a
# simple redirect. This fallback is your “last resort.”
# ──────────────────────────────────────────────────────────────────────────────

def fetch_random_site_with_requests() -> str | None:
    """
    Attempt to fetch RANDOM_SITE_URL via plain requests and pull out
    any <a id="random_link"> href via BeautifulSoup. In many cases,
    this will NOT work because the page is entirely populated by JS,
    but it may help in certain cache/redirect scenarios.
    """
    try:
        from bs4 import BeautifulSoup
    except ImportError:
        return None

    try:
        resp = requests.get(RANDOM_SITE_URL, timeout=10)
        if resp.status_code != 200:
            return None

        soup = BeautifulSoup(resp.text, "lxml")
        a = soup.find("a", {"id": "random_link"})
        if a and a.get("href"):
            return a["href"]
        return None
    except Exception:
        return None

# ──────────────────────────────────────────────────────────────────────────────
# MAIN: Selenium + headless Chromium approach
# ──────────────────────────────────────────────────────────────────────────────

def fetch_random_site_with_selenium(timeout: int = TIMEOUT) -> str | None:
    """
    Uses Selenium + headless Chromium to load RANDOM_SITE_URL, waits for
    <a id="random_link"> href to be populated, and returns that link.
    Returns None if any step fails (timeout, driver errors, etc.).
    """
    try:
        # 1) Download the correct ChromeDriver
        driver_path = ChromeDriverManager().install()
        service = ChromeService(driver_path)

        # 2) Configure headless Chromium with additional flags
        options = webdriver.ChromeOptions()
        # On most Linux distros (including GitHub Actions), 'chromium-browser' is installed here:
        options.binary_location = "/usr/bin/chromium-browser"
        # For some machines, the binary might be at '/usr/bin/chromium' instead.
        if not os.path.exists(options.binary_location):
            alt_path = "/usr/bin/chromium"
            if os.path.exists(alt_path):
                options.binary_location = alt_path

        options.add_argument("--headless=new")          # use the new headless mode
        options.add_argument("--disable-gpu")            # recommended for headless
        options.add_argument("--no-sandbox")             # bypass OS security model
        options.add_argument("--disable-dev-shm-usage")  # avoid shared memory issues
        options.add_argument("--remote-debugging-port=0")# necessary in many CI environments

        driver = webdriver.Chrome(service=service, options=options)

        try:
            driver.get(RANDOM_SITE_URL)

            # Wait until <a id="random_link"> has a non-empty href
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
        # Log or print the exception if you want to debug
        print(f"[SELENIUM] Error: {e}", flush=True)
        return None


# ──────────────────────────────────────────────────────────────────────────────
# PUBLIC FUNCTION: generate()
# ──────────────────────────────────────────────────────────────────────────────

def generate() -> str:
    """
    Returns exactly one string:
      🌐 *Website aleatório do dia: *
      https://some-random-site.example

    If Selenium fails, it tries a fallback via pure requests. If that also fails,
    returns an error message in Portuguese.
    """
    # 1) First attempt: Selenium + headless Chromium
    site = fetch_random_site_with_selenium(timeout=TIMEOUT)
    if site:
        return f"🌐 *Website aleatório do dia: *\n{site}"

    # 2) Fallback: requests + BeautifulSoup
    site = fetch_random_site_with_requests()
    if site:
        return f"🌐 *Website aleatório do dia (fallback): *\n{site}"

    # 3) If all else fails:
    return "⚠️ Não consegui obter o site aleatório hoje."


# ──────────────────────────────────────────────────────────────────────────────
# If you want to debug/test locally, uncomment below:
# if __name__ == "__main__":
#     print(generate())
# ──────────────────────────────────────────────────────────────────────────────

