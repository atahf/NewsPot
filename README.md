# NewsPot

This is a Honeypot that aims to have following vulnerabilities:
- Insecure direct object references
- Failure to Restrict URL Access
- Unvalidated Redirects and Forwards

## Usage
- After downloading the source code an additional ```.env``` file is needed.
- This ```.env``` file should have following structure with your own credentials.
```
SECRET_KEY={YOUR_SECRET_KEY}
RECAPTCHA_SITE_KEY={YOUR_RECAPTCHA_SITE_KEY}
RECAPTCHA_SECRET_KEY={YOUR_RECAPTCHA_SECRET_KEY}
EMAIL_ADDRESS={YOUR_EMAIL_ADDRESS}
PASSWORD={YOUT_EMAIL_APP_PASSWORD}
APP_URL={YOUR_DEPLOY_IP_PORT}
```
- To run the application, you have to run [```main.py```](https://github.com/atahf/NewsPot/blob/main/main.py).
```
python main.py
```
- With current configuration, the application will run on ```YOUR_IP:8080```, but you can change it inside [```main.py```](https://github.com/atahf/NewsPot/blob/main/main.py).
