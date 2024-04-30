import user_consts
import urls

from time import sleep
from twocaptcha import TwoCaptcha
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from locators import *


class Midpass:
    def __init__(self) -> None:
        self.chrome_options = Options()
        self.chrome_options.add_argument("--headless")
        self.chrome_options.add_argument("disable-infobars")
        self.chrome_options.add_argument("--disable-extensions")
        self.chrome_options.add_argument("--disable-gpu")
        self.chrome_options.add_argument("--disable-dev-shm-usage")
        self.chrome_options.add_argument("--no-sandbox")

        self.driver = webdriver.Chrome(self.chrome_options)
        self.driver.set_window_size(1024, 868)
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
        # img_captcha.screenshot("ss.png")
        solver = TwoCaptcha(user_consts.API_KEY)
        result = solver.normal(captcha_image_base64, hintText="x12345", minLen=6, maxLen = 6)
        # print("result: ", result["code"])
        return result["code"]

    def login_private_person(self, mail: str, password: str) -> tuple:
        self.driver.get(urls.LOGON_PAGE)

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

        if self.driver.current_url == urls.INDEX_PAGE:
            return True, "Авторизация прошла успешно"
        
        error_elements = self.driver.find_elements(*LoginPageLocators.LOGIN_ERROR)
        
        if error_elements:
            return False, error_elements[0].text

        if self.driver.current_url == urls.BAN_PAGE:
            return False, "Система решила, что я бот. На почту пришел новый пароль. \n"\
                            "Пришлите его мне с помощью команды /password \n"\
                            "и я попытаюсь снова через пару часов"

        return False, "Авторизация не удалась при невыясненных обстоятельствах"

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
            return "Кнопка подтверждения неактивна. Сегодня уже подтверждено"
        try:
            self.script.click(btn_confirm_appointment).perform()
            # confirmation window
            self.find(*CaptchaLocators.INPUT_CAPTCHA_OUTSTANDING).send_keys(self.solve_captcha())
            self.find(*CaptchaLocators.BTN_CONFIRM).click()
            sleep(6)
            self.find(*CaptchaLocators.BTN_OK).click()  # fixme
            return "Заявка подтверждена. До завтра можно не переживать"
        except:
            return "Что-то пошло не так. Заявка не подтверждена"
        finally:
            sleep(3)


if __name__ == "__main__":
    script = Midpass()

    login = script.login_private_person(mail=user_consts.MAIL, password=user_consts.PASSWORD)
    if not login[0]:
        print(login[1])
        exit()
    print(script.go_to_waiting_list_and_check_position())
    print(script.update_queue_position())
