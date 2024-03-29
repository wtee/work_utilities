"""
This 'API' should be considered highly unstable and subject to change
without notice.
"""

import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options

base_url = "https://avian.lib.iastate.edu"
doc_view_url = "https://avian.lib.iastate.edu/documents/{}/view"
doc_edit_url = "https://avian.lib.iastate.edu/documents/{}/edit"
place_view_url = "https://avian.lib.iastate.edu/places/{}/view"
place_edit_url = "https://avian.lib.iastate.edu/places/{}/edit"

options = Options()
options.binary_location = "C:/Program Files/Mozilla Firefox/firefox.exe"


driver = webdriver.Firefox(options=options)

# To handle Okta logins, we need to wait for the login
# page's scripts to populate the HTML form elements
driver.implicitly_wait(10)

# ADD functions
def _add_access_point(field, ap):
    """
    The Selenium window must be in focus in the window manager for this function to work.
    Otherwise, the suggestion will not appear, and the tab key will not select the first item
    in the suggestions. Most of this function is a kludge to work around the hard-to-automate
    avIAn interface or the Selenium/Firefox driver's inablity to move to an item that isn't within
    the current viewport and Selenium's lack of a scroll function.

    It appears this function may not work properly unless it is the final edit made on a page.
    """
    return_elem_xpath = f'//input[@id="{field}"]'
    return_elem = driver.find_element(By.XPATH, return_elem_xpath)
    scroll_to(return_elem)
    ActionChains(driver).move_to_element(return_elem).click(return_elem).perform()
    # Send less than the full string to prompt suggestions
    return_elem.send_keys(ap[:-1])
    # Pause to give the Creator field time to auto-populate suggestions
    time.sleep(2)
    # Select the top option out of suggestions
    return_elem.send_keys(Keys.TAB)

    return return_elem


def add_genre(genre):
    field = "__wdzf-genres"
    return _add_access_point(field, genre)


def add_creator(creator):
    field = "__wdzf-creators"
    return _add_access_point(field, creator)


# CHANGE functions
def change_format_extent_number(new_number):
    format_extent_number_xpath = '//input[@name="extent"]'
    format_extent_number_field = driver.find_element(
        By.XPATH, format_extent_number_xpath
    )
    format_extent_number_field.clear()
    format_extent_number_field.send_keys(new_number)

    return format_extent_number_field


def change_description(func, *args):
    """
    Accepts a function to make changes to description text and assigns
    the string returned by that function to new_description. All such
    functions are passed the content of the description textbox. They
    may be passed additional arguments via *args.
    """
    return_elem_xpath = '//input[@id="__wdzf-title"]'
    return_elem = driver.find_element(By.XPATH, return_elem_xpath)
    description_xpath = '//textarea[@id="__wdzf-description"]'
    description_elem = driver.find_element(By.XPATH, description_xpath)
    new_description = func(description_elem.text, *args)
    description_elem.clear()
    description_elem.send_keys(new_description)

    return return_elem


# DELETE functions
def _delete_access_point(field, ap):
    field_row = field[:6] + "-row" + field[6:]
    return_elem_xpath = f'//input[@id="{field}"]'
    return_elem = driver.find_element(By.XPATH, return_elem_xpath)
    ap_delete_btn_xpath = (
        f'//div[@id="{field_row}"]//a[text()="{ap}"]/following-sibling::a'
    )
    ap_delete_btn = driver.find_element(By.XPATH, ap_delete_btn_xpath)
    scroll_to(ap_delete_btn)
    ActionChains(driver).move_to_element(ap_delete_btn).click(ap_delete_btn).perform()

    return return_elem


def delete_contributor(contrib):
    field = "__wdzf-contributors"
    return _delete_access_point(field, contrib)


def delete_people_org(ppl_org):
    field = "__wdzf-people"
    return _delete_access_point(field, ppl_org)


def delete_genre(genre):
    field = "__wdzf-genres"
    return _delete_access_point(field, genre)


def delete_topic(topic):
    field = "__wdzf-topics"
    return _delete_access_point(field, topic)


# READ functions
def read_geonames_id():
    field = "__wdzf-higherGeographyUri"
    return _read_edit_field(field)


def _read__edit_field(field):
    return _get_by_id(field).get_property("value")


# Utility functions
def login(username, password):
    login_btn_xpath = '//a[@href="/_webdev/auth/login"]'

    driver.get(base_url)
    driver.find_element(By.XPATH, login_btn_xpath).click()

    username_field = driver.find_element(By.ID, "okta-signin-username")
    password_field = driver.find_element(By.ID, "okta-signin-password")

    username_field.send_keys(username)
    password_field.send_keys(password)

    driver.find_element(By.ID, "okta-signin-submit").click()

    # If we don't pause here, the login fails. By pausing we keep
    # from short-circuiting Okta & Shibboleth.
    time.sleep(2)

    driver.get(base_url)


def load_page(view="view", doc_id=None, obj_type="document"):
    if doc_id is not None:
        driver.get(f"https://avian.lib.iastate.edu/{obj_type}/{doc_id}/{view}")
    else:
        driver.get(base_url)


def _get_by_xpath(xpath):
    return driver.find_element(By.XPATH, xpath)


def _get_by_id(id):
    return driver.find_element(By.ID, id)


def save(elem):
    """
    A quirk of the avIAn website is that sending the Enter key to most
    fields will submit the form. This is good since a quirk of Selenium, at
    least with geckodriver, is that scrolling up to the save button is
    unreliable.

    This function accepts an element as an argument and sends the Return key
    signal to it, saving any changes to the document to the database. Each
    function returns an element that will save the document when sent the
    Return signal. Generally, you will want to pass this function the last
    element returned."""

    elem.send_keys(Keys.RETURN)


def scroll_to(element):
    driver.execute_script(
        'arguments[0].scrollIntoView({behavior: "instant", block: "start", inline: "start"});',
        element,
    )
    # time.sleep(2)
    # return True
