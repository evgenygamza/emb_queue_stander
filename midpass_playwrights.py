from playwright.async_api import async_playwright
from twocaptcha import TwoCaptcha

import urls
import base64
import user_consts


class Midpass:
    def __init__(self) -> None:
        self.browser = None
        self.page = None

    async def __aenter__(self):
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=True)
        self.page = await self.browser.new_page()
        await self.page.set_viewport_size({"width": 1024, "height": 868})
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.browser.close()
        await self.playwright.stop()

    async def solve_captcha(self) -> str:
        await self.page.wait_for_timeout(1000)
        img_captcha = await self.page.locator("#imgCaptcha").screenshot()
        await self.page.locator("#imgCaptcha").screenshot(path="ss.png")
        captcha_image_base64 = base64.b64encode(img_captcha).decode()
        solver = TwoCaptcha(user_consts.API_KEY)
        result = solver.normal(captcha_image_base64, hintText="x12345", minLen=6, maxLen=6)
        return result["code"]

    async def login_private_person(self, mail: str, password: str) -> tuple:
        await self.page.goto(urls.LOGON_PAGE)

        # login page
        await self.page.select_option("select[data-bind*='selectedCountry']", label="Грузия")
        await self.page.select_option("select[data-bind*='selectedServiceProvider']",
                                label="Тбилиси - Консульская служба Секции интересов РФ")

        await self.page.fill("#Email", mail)
        try:
            await self.page.locator("#Captcha").click()
            captcha_resolution = await self.solve_captcha()
            await self.page.locator("#Captcha").fill(captcha_resolution)
        except:
            return False, ("Я не справился с капчой. Давайте попробеум еще раз:\n"
                           "/queue")
        await self.page.locator("#Password").fill(password)

        await self.page.get_by_text("Войти").click()

        if self.page.url == urls.INDEX_PAGE:
            return True, "Авторизация прошла успешно"

        error_elements = await self.page.query_selector_all("span.field-validation-error")
        if error_elements:
            return False, await error_elements[0].inner_text()

        if self.page.url == urls.BAN_PAGE:
            return "banned", ("Система решила, что я бот. На почту пришел новый пароль. \n"
                              "Пришлите его мне с помощью команды /password \n"
                              "и мы попробуем через час еще разок")

        return False, "Авторизация не удалась при невыясненных обстоятельствах"

    async def go_to_waiting_list_and_check_position(self) -> int:
        # main page
        await self.page.get_by_text("Лист ожидания").click()
        # queue page
        position_text = await self.page.inner_text("td[field='PlaceInQueueString'] div.datagrid-cell-c1-PlaceInQueueString")
        position = int(position_text.split()[1])
        return position

    async def update_queue_position(self) -> str:
        await self.page.locator("div.datagrid-cell-check input").check()
        btn_confirm_appointment = self.page.get_by_text("Подтвердить заявку")
        btn_class = await btn_confirm_appointment.get_attribute("class")
        if "l-btn-disabled" in btn_class:
            return "Кнопка подтверждения неактивна. Сегодня уже подтверждено"
        try:
            await btn_confirm_appointment.click()
            # confirmation window
            captcha_resolution2 = await self.solve_captcha()
            await self.page.locator("#captchaValue").fill(captcha_resolution2)
            await self.page.get_by_role("link", name="Подтвердить", exact=True).click()
            await self.page.wait_for_timeout(6000)
            await self.page.get_by_role("link", name="Ок", exact=True).click()
            return "Заявка подтверждена. До завтра можно не переживать"
        except:
            return "Что-то пошло не так. Заявка не подтверждена"
        finally:
            await self.page.wait_for_timeout(3000)


async def main():
    async with Midpass() as script:
        try:
            login = await script.login_private_person(mail=user_consts.MAIL, password=user_consts.PASSWORD)
            if not login[0]:
                print(login[1])
                return
            print(await script.go_to_waiting_list_and_check_position())
            print(await script.update_queue_position())
        finally:
            pass

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
