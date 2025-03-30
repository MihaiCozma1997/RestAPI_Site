import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

DRIVER_PATH = r'C:\Users\mihai\PycharmProjects\RESTApi\chromedriver-win64\chromedriver.exe'


@pytest.fixture(scope="module")
def driver():
    options = Options()
    #options.add_argument('--headless')  # Headless mode for faster tests
    options.add_argument('--disable-gpu')
    service = Service(executable_path=DRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=options)
    yield driver
    driver.quit()
