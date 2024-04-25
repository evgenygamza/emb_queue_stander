from selenium.webdriver.common.by import By


class CaptchaLocators:
    IMG_CAPTCHA = (By.ID, "imgCaptcha")
    INPUT_CAPTCHA = (By.ID, "Captcha")
    INPUT_CAPTCHA_OUTSTANDING = (By.ID, "captchaValue")
    BTN_CONFIRM = (By.XPATH, "//span[text()='Подтвердить']")
    BTN_OK = (By.XPATH, "/html/body/div[9]/div/div[3]/a/span/span")
    # CAPTCHA_ERROR = (By.ID, "captchaError")


class LoginPageLocators:
    SELECT_COUNTRY = (By.CSS_SELECTOR, "select[data-bind*='selectedCountry']")
    SELECT_SERVICE_PROVIDER = (By.CSS_SELECTOR, "select[data-bind*='selectedServiceProvider']")
    INPUT_EMAIL = (By.ID, "Email")
    INPUT_PASSWORD = (By.ID, "Password")
    BTN_LOGIN = (By.XPATH, "//button[text()='Войти']")
    LOGIN_ERROR = (By.CSS_SELECTOR, "span.field-validation-error")


class MainPageLocators:
    BTN_WAITING_LIST = (By.XPATH, "//a[text()='Лист ожидания']")


class QueuePageLocators:
    CHKBX_WAITING_LIST = (By.CSS_SELECTOR, "div.datagrid-cell-check input")
    BTN_CONFIRM_APPOINTMENT = (By.CSS_SELECTOR, "#confirmAppointments")
    BTN_CONFIRM_APPOINTMENT_DISABLED = (By.CSS_SELECTOR, "#confirmAppointments.l-btn-disabled")
    CELL_QUANTITY_IN_QUEUE = (By.CSS_SELECTOR, "td[field='PlaceInQueueString'] div.datagrid-cell-c1-PlaceInQueueString")
