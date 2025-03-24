import uuid, os
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from conf_test import driver


def save_user(username, password):
    with open('user_data.txt', 'w') as f:
        f.write(f"{username},{password}\n")


def test_register_user(driver):
    # Launch your Flask app (assuming it’s already running on localhost:5000)
    driver.get('http://127.0.0.1:5000/registerPage')

    # Find form fields and fill them
    username_input = driver.find_element(By.ID, 'username')
    email_input = driver.find_element(By.ID, 'email')
    password_input = driver.find_element(By.ID, 'password')

    unique_id = uuid.uuid4().hex[:6]  # Short unique ID
    username = f"testuser{unique_id}"
    email = f"{username}@example.com"

    username_input.send_keys(username)
    email_input.send_keys(email)
    password_input.send_keys('securepassword')

    # Save user and pw for login test
    save_user(username, 'securepassword')

    # Submit the form
    submit_button = driver.find_element(By.CLASS_NAME, 'btn')
    submit_button.click()

    # Wait for the page to load / response (simplified)
    WebDriverWait(driver, 5).until(EC.alert_is_present())

    # Switch to alert and verify the message
    alert = driver.switch_to.alert
    alert_text = alert.text
    assert 'Registration successful! Redirecting to login...' in alert_text

    # Accept (close) the alert
    alert.accept()
