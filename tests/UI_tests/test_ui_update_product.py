from conf_test import driver
import uuid, pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def get_user():
    with open('user_data.txt', 'r') as f:
        line = f.readline().strip()  # Read the first line
        username, password = line.split(',')
        return username, password


def get_product_name():
    with open('user_data.txt', 'r') as f:
        line = f.readlines()  # Read the first line
        return line[1]


@pytest.mark.run(order=4)
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

    # Find update product button
    update_product_button = driver.find_element(By.ID, 'update-product-btn')
    update_product_button.click()

    # Wait until page is loaded
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, 'update-product-form'))
    )
    # Update last product in list
    update_product_card = driver.find_elements(By.ID, 'user-products-container')[-1]

    # Find edit button
    edit_button = update_product_card.find_element(By.XPATH, "//button[text()='Edit']")
    edit_button.click()

    # Find the update form
    form_name = driver.find_element(By.ID, 'update-name')
    form_price = driver.find_element(By.ID, 'update-price')
    form_description = driver.find_element(By.ID, 'update-description')

    # Create unique product
    unique_id = uuid.uuid4().hex[:6]  # Short unique ID
    product_name = f'Laptop Dell{unique_id}'
    price = 1000
    description = 'I9 5600, nvidia gx 3080'

    # Clear prefilled data form
    form_name.clear()
    form_price.clear()
    form_description.clear()

    # Update the product information
    form_name.send_keys(product_name)
    form_price.send_keys(price)
    form_description.send_keys(description)

    # Click submit form
    submit_form_button = driver.find_element(By.XPATH, "//button[text()='Update Product']")
    submit_form_button.click()

    # Wait for the page to load / response (simplified)
    WebDriverWait(driver, 5).until(EC.alert_is_present())

    # Switch to alert and verify the message
    alert = driver.switch_to.alert
    alert_text = alert.text

    assert 'Product updated successfully!' in alert_text

    # Accept (close) the alert
    alert.accept()

    # Launch your Flask app (assuming it’s already running on localhost:5000)
    driver.get('http://127.0.0.1:5000/')

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
    price_displayed = last_product_card.find_element(By.XPATH,
                                                     ".//p[strong[text()='Price:']]").text
    description_displayed = last_product_card.find_element(By.ID,
                                                           "description").text
    # Transform price in a number
    price_displayed = int(price_displayed.split('$')[1])

    assert product_name == product_name_displayed, f"Product name mismatch. Expected: " \
                                                   f"{product_name}, Found: {product_name_displayed}"
    assert price == price_displayed, f"Price mismatch. Expected: " \
                                     f"{price}, Found: {price_displayed}"
    assert description == description_displayed, f"Description mismatch. Expected: " \
                                                 f"{description}, Found: {description_displayed}"
