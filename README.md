# emb_queue_stander
lovely robot for dull work


# 1. Install python 
https://www.python.org/downloads/

# 2. Configure your options
you need to create user_consts.py in the root of the project which should contain your data:

``` python
MAIL = "yourmail@gmail.com"
PASSWORD = "password from your email box"
API_KEY = "123qwe456RTy789uiO0"
```

# 3. install requirements.txt

``` python
pip install -r requirements.txt
```

# 4. shedule task in cron
``` bash
57 11 * * * /path/to/python /path/to/file/update_queue_position.py
```
