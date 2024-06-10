start = (""
         "Список команд:\n"
         "- /queue - Подтвердить заявку\n"
         "- /position - Узнать своё текущее место в очереди\n"
         "- /email - ввести свою почту\n"
         "- /password - обновить пароль\n"
         "- /cancel - отменить ввод пароля или почты\n"
         "- /delete - удалить свои данные\n"
         "- /start или /help - повторить эту инструкцию\n"
         "")

enter = "Захожу в кабинет"
login_status = "Результат авторизации: $value"
failed = "Авторизация по каким-то причинам не удалась. Давайте попробуем ещё"
position = "Текущее место в очереди: $value"
last_hundred = ("Внимание! \n"
                "Осталось меньше ста человек")

get_position = "С последнего обновления ваш номер был $value"
enter_password = "Введите в следующем сообщении пароль:"
new_password = "Новый пароль: $value"

enter_email = "Введите в следующем сообщении адрес электронной почты:"
new_email = "Новая почта: $value"

cancel = "Действие отменено"

delete_failed = "Что-то пошло не так. Попробуйте еще раз: /delete"
deleted = "Удалено"

reminder = ("Пора подтвердить место в очереди. \n"
            "Пожалуйста, отправь мне команду /queue")

captcha_fail = ("Я не справился с капчой. Давайте попробеум еще раз:\n"
                "/queue")
login_success = "Авторизация прошла успешно"
banned = ("Система решила, что я бот. На почту пришел новый пароль. \n"
          "Пришлите его мне с помощью команды /password \n"
          "и мы попробуем через час ещё разок")
login_fail = "Авторизация не удалась при невыясненных обстоятельствах"
inactive = "Кнопка подтверждения неактивна. Сегодня уже подтверждено"
update_success = "Заявка подтверждена. До завтра можно не переживать"
update_fail = "Что-то пошло не так. Заявка не подтверждена"

echo = "При чем тут $value"
