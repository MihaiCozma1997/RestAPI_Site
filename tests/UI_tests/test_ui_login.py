from conf_test import driver
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def get_user():
    with open('user_data.txt', 'r') as f:
        line = f.readline().strip()  # Read the first line
        username, password = line.split(',')
        return username, password


@pytest.mark.run(order=2)
def test_login_user(driver):
    # Launch your Flask app (assuming it’s already running on localhost:5000)
    driver.get('http://127.0.0.1:5000/loginPage')

    # Access user detail from registration process
    username, password = get_user()

    # Find form fields and fill them
    username_input = driver.find_element(By.ID, 'username')
    password_input = driver.find_element(By.ID, 'password')

    username_input.send_keys(username)
    password_input.send_keys(password)

    # Submit the form
    submit_button = driver.find_element(By.CLASS_NAME, 'btn')
    submit_button.click()

    # Wait for the page to load / response (simplified)
    WebDriverWait(driver, 5).until(EC.alert_is_present())

    # Switch to alert and verify the message
    alert = driver.switch_to.alert
    alert_text = alert.text
    assert 'Login successful!' in alert_text

    # Accept (close) the alert
    alert.accept()