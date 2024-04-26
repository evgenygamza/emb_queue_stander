import asyncio
import user_consts

from time import sleep
from datetime import datetime
from twocaptcha import TwoCaptcha
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.select import Select
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from locators import *
# from reminder_bot_ import send_message

class Midpass:
    def __init__(self) -> None:
        self.driver = webdriver.Chrome()
        self.driver.implicitly_wait(15)
        self.script = ActionChains(self.driver)

    def find(self, how, what):
        try:
            self.driver.find_element(how, what)
        except NoSuchElementException:
            return False
        return self.driver.find_element(how, what)

    def solve_captcha(self) -> str:
        sleep(1)

        img_captcha = self.find(*CaptchaLocators.IMG_CAPTCHA)

        captcha_image_base64 = img_captcha.screenshot_as_base64
        solver = TwoCaptcha(user_consts.API_KEY)
        result = solver.normal(captcha_image_base64, hintText="x12345", minLen=6, maxLen = 6)

        return result["code"]

    def login_private_person(self, mail: str, password: str) -> tuple:
        self.driver.get("https://q.midpass.ru/ru/Account/PrivatePersonLogOn")

        # login page
        Select(self.find(*LoginPageLocators.SELECT_COUNTRY)).select_by_visible_text("Грузия")
        Select(self.find(*LoginPageLocators.SELECT_SERVICE_PROVIDER)).select_by_visible_text(\
            "Тбилиси - Консульская служба Секции интересов РФ")

        self.find(*LoginPageLocators.INPUT_EMAIL).send_keys(mail)
        self.find(*CaptchaLocators.INPUT_CAPTCHA).send_keys(self.solve_captcha())
        self.find(*LoginPageLocators.INPUT_PASSWORD).send_keys(password)

        btn_login = self.find(*LoginPageLocators.BTN_LOGIN)
        self.script.scroll_to_element(btn_login).move_to_element(btn_login).click(btn_login).perform()

        EC.invisibility_of_element(LoginPageLocators.LOGIN_ERROR)

        try:
            WebDriverWait(self.driver, 10).until(EC.url_to_be("https://q.midpass.ru/ru/Home/Index"))
            return True, "Login succeed"
        except TimeoutException:
            try:
                error_element = WebDriverWait(self.driver, 3).until(
                    EC.presence_of_element_located(LoginPageLocators.LOGIN_ERROR))
                return False, error_element.text
            except:
                return False, "Login failed"

    def go_to_waiting_list_and_check_position(self) -> str:
        # main page
        btn_waiting_list = self.find(*MainPageLocators.BTN_WAITING_LIST)
        self.script.move_to_element(btn_waiting_list).click(btn_waiting_list).perform()

        # queue page
        position = int(self.find(*QueuePageLocators.CELL_QUANTITY_IN_QUEUE).text.split()[1])
        return position
    
    def update_queue_position(self) -> str:
        checkbox_waiting_list = self.find(*QueuePageLocators.CHKBX_WAITING_LIST)
        btn_confirm_appointment = self.find(*QueuePageLocators.BTN_CONFIRM_APPOINTMENT)
        self.script.move_to_element(checkbox_waiting_list).click(checkbox_waiting_list).perform()
        self.script.scroll_to_element(btn_confirm_appointment).scroll_by_amount(0, 600).move_to_element(btn_confirm_appointment).perform()
        btn_class = btn_confirm_appointment.get_attribute("class")
        if "l-btn-disabled" in btn_class:
            return "Кнопка подтверждения неактивна. На сегодня уже подтверждено"
        try:
            self.script.click(btn_confirm_appointment).perform()
            # confirmation window
            self.find(*CaptchaLocators.INPUT_CAPTCHA_OUTSTANDING).send_keys(self.solve_captcha())
            self.find(*CaptchaLocators.BTN_CONFIRM).click()
            sleep(3)
            self.find(*CaptchaLocators.BTN_OK).click()  # fixme
            return "Заявка подтверждена. До завтра можно не переживать"
        except:
            return "Что-то пошло не так. Заявка не подтверждена"
        finally:
            sleep(3)


if __name__ == "__main__":
    script = Midpass()
    print(script.login_private_person(mail=user_consts.MAIL, password=user_consts.PASSWORD))
    print(script.go_to_waiting_list_and_check_position())
    print(script.update_queue_position())
