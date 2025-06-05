import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager

RANDOM_SITE_URL = "http://random.whatsmyip.org/"
TIMEOUT = 15  # seconds to wait for the JS-injected link

def fetch_random_site(timeout: int = TIMEOUT) -> str | None:
    try:
        # 1) Download the correct ChromeDriver version for the installed Chromium
        driver_path = ChromeDriverManager().install()
        service = ChromeService(driver_path)

        # 2) Configure headless Chromium with the required flags
        options = webdriver.ChromeOptions()

        # Point to the binary installed by `sudo apt-get install chromium-browser`
        options.binary_location = "/usr/bin/chromium-browser"
        if not os.path.exists(options.binary_location):
            # On some images it may appear at /usr/bin/chromium
            alt_path = "/usr/bin/chromium"
            if os.path.exists(alt_path):
                options.binary_location = alt_path

        # Essential flags for headless on Ubuntu CI
        options.add_argument("--headless=new")          # use new headless if version >=109
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
    link = fetch_random_site(timeout=TIMEOUT)
    if link:
        return f"🌐 *Website aleatório do dia: *\n{link}"
    else:
        return "⚠️ Não consegui obter o site aleatório hoje."

