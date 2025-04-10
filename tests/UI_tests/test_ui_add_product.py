from conf_test import driver
import pytest, uuid
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def get_user():
    with open('user_data.txt', 'r') as f:
        line = f.readline().strip()  # Read the first line
        username, password = line.split(',')
        return username, password


def save_product_name(product_name):
    with open('user_data.txt', 'a') as f:
        f.write(product_name)


@pytest.mark.run(order=3)
def test_add_product(driver):
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

    # Find add product button
    add_product_button = driver.find_element(By.ID, 'add-product-btn')
    add_product_button.click()

    # Find product form
    form_name = driver.find_element(By.ID, 'name')
    form_price = driver.find_element(By.ID, 'price')
    form_description = driver.find_element(By.ID, 'description')

    # Create unique product
    unique_id = uuid.uuid4().hex[:6]  # Short unique ID
    product_name = f'Laptop Dell{unique_id}'
    # Save the name to use in other tests
    save_product_name(product_name)

    form_name.send_keys(product_name)
    form_price.send_keys(600)
    form_description.send_keys('I5 5600, nvidia gx 1080')

    # Click submit form
    submit_form_button = driver.find_element(By.CLASS_NAME, 'btn')
    submit_form_button.click()

    # Wait for the page to load / response (simplified)
    WebDriverWait(driver, 5).until(EC.alert_is_present())

    # Switch to alert and verify the message
    alert = driver.switch_to.alert
    alert_text = alert.text

    assert 'Product added successfully!' in alert_text

    # Accept (close) the alert
    alert.accept()
    # Wait until home page is loaded
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'product-card'))
    )

    # Verify if the last product added is displayed on the homepage
    product_cards = driver.find_elements(By.CLASS_NAME, 'product-card')
    last_product_card = product_cards[-1]

    # Check if the name in the last product card matches the product name added
    product_name_displayed = last_product_card.find_element(By.TAG_NAME,
                                                            'h3').text

    assert product_name == product_name_displayed, f"Product name mismatch. Expected: " \
                                                   f"{product_name}, Found: {product_name_displayed}"
