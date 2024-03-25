from selenium.webdriver.common.by import By


class CaptchaLocators:
    IMG_CAPTCHA = (By.CSS_SELECTOR, "#imgCaptcha")
    INPUT_CAPTCHA = (By.ID, "Captcha")
    INPUT_CAPTCHA_OUTSTANDING = (By.ID, "captchaValue")
    BTN_CONFIRM = (By.XPATH, "//span[text()='Подтвердить']")
    BTN_OK = (By.XPATH, "//span[text()='Ок']")


class LoginPageLocators:
    SELECT_COUNTRY = (By.CSS_SELECTOR, "select[data-bind*='selectedCountry']")
    SELECT_SERVICE_PROVIDER = (By.CSS_SELECTOR, "select[data-bind*='selectedServiceProvider']")
    INPUT_EMAIL = (By.CSS_SELECTOR, "#Email")
    INPUT_PASSWORD = (By.CSS_SELECTOR, "#Password")
    BTN_LOGIN = (By.XPATH, "//button[text()='Войти']")


class MainPageLocators:
    BTN_WAITING_LIST = (By.XPATH, "//a[text()='Лист ожидания']")


class QueuePageLocators:
    CHKBX_WAITING_LIST = (By.CSS_SELECTOR, "div.datagrid-cell-check input")
    BTN_CONFIRM_APPOINTMENT = (By.CSS_SELECTOR, "#confirmAppointments")
