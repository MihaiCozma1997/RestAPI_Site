import time

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


@pytest.mark.run(order=5)
def test_rating_product(driver):
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

    # Wait until home page is loaded
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'product-card'))
    )

    # Find rate product button
    last_product_card = driver.find_elements(By.CLASS_NAME, 'product-card')[-1]
    rate_button = last_product_card.find_element(By.CLASS_NAME, 'review-button')
    rate_button.click()

    # Find the 5th star
    star_button = driver.find_element(By.XPATH, '//i[@class="fa-regular fa-star" and @data-value="5"]')
    star_button.click()

    # fill review description
    review_description = driver.find_element(By.ID, 'review-comment')
    review_description.send_keys('Test review comment')

    # Find submit review button
    submit_review_button = driver.find_element(By.ID, 'submit-review')
    submit_review_button.click()

    # Wait for the page to load / response (simplified)
    WebDriverWait(driver, 5).until(EC.alert_is_present())

    # Switch to alert and verify the message
    alert = driver.switch_to.alert
    alert_text = alert.text
    assert 'Review added successfully!' in alert_text

    # Accept (close) the alert
    alert.accept()

    # Wait until home page is loaded
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'product-card'))
    )

    # find see review button
    last_product_card = driver.find_elements(By.CLASS_NAME, 'product-card')[-1]
    reviews = last_product_card.find_element(By.CLASS_NAME, 'clickable')
    reviews.click()

    # Wait until home page is loaded
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, 'reviews-list'))
    )
    reviews_list = driver.find_elements(By.ID, 'reviews-list')[-1]
    paragraphs = reviews_list.find_elements(By.TAG_NAME, 'p')

    # Find the review
    review_user_display = paragraphs[0].text
    review_rating_display = paragraphs[0].text
    review_description_display = paragraphs[0].text

    # Format review output
    review_user_display = review_user_display.split(' ')[1]
    review_rating_display = review_rating_display.split(' ')[1]

    registered_user = get_user()[0]

    assert registered_user == review_user_display, f"User Mismatch. Expected: " \
                                                 f"{registered_user}, Found: {review_user_display}"
    assert 5 == review_rating_display, f"Price mismatch. Expected: " \
                                       f"5, Found: {review_rating_display}"
    assert 'Test review comment' == review_description_display, f"Description mismatch. Expected: " \
                                                                f"Test review comment, Found: {review_description_display}"
