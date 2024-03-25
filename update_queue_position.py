import time
import user_consts

from twocaptcha import TwoCaptcha
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.support.select import Select
from locators import *


driver = webdriver.Chrome()
driver.implicitly_wait(15)

driver.get('https://q.midpass.ru/ru/Account/PrivatePersonLogOn?ReturnUrl=%2fru%2fAppointments%2fWaitingList')


def solve_captcha():
    time.sleep(1)

    img_captcha = driver.find_element(*CaptchaLocators.IMG_CAPTCHA)

    captcha_image_base64 = img_captcha.screenshot_as_base64
    solver = TwoCaptcha(user_consts.API_KEY)
    result = solver.normal(captcha_image_base64, hintText="x12345", minLen=6, maxLen = 6)

    print(result)
    return result["code"]


# login page
Select(driver.find_element(*LoginPageLocators.SELECT_COUNTRY)).select_by_visible_text("Грузия")
Select(driver.find_element(*LoginPageLocators.SELECT_SERVICE_PROVIDER)).select_by_visible_text(\
    "Тбилиси - Консульская служба Секции интересов РФ")

driver.find_element(*LoginPageLocators.INPUT_EMAIL).send_keys(user_consts.MAIL)
driver.find_element(*CaptchaLocators.INPUT_CAPTCHA).send_keys(solve_captcha())
driver.find_element(*LoginPageLocators.INPUT_PASSWORD).send_keys(user_consts.PASSWORD)

script = ActionChains(driver)
btn_login = driver.find_element(*LoginPageLocators.BTN_LOGIN)
script.scroll_to_element(btn_login).move_to_element(btn_login).click(btn_login).perform()


# main page
btn_waiting_list = driver.find_element(*MainPageLocators.BTN_WAITING_LIST)
script.move_to_element(btn_waiting_list).click(btn_waiting_list).perform()


# queue page
checkbox_waiting_list = driver.find_element(*QueuePageLocators.CHKBX_WAITING_LIST)
btn_confirm_appointment = driver.find_element(*QueuePageLocators.BTN_CONFIRM_APPOINTMENT)
script.move_to_element(checkbox_waiting_list).click(checkbox_waiting_list).perform()
script.scroll_to_element(btn_confirm_appointment).scroll_by_amount(0, 300).move_to_element(btn_confirm_appointment).perform()
script.click(btn_confirm_appointment).perform()


# confirm windows
driver.find_element(*CaptchaLocators.INPUT_CAPTCHA_OUTSTANDING).send_keys(solve_captcha())
driver.find_element(*CaptchaLocators.BTN_CONFIRM).click()
driver.find_element(*CaptchaLocators.BTN_OK).click()

time.sleep(3)
