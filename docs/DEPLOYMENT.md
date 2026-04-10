My note: Розгортання у Production середовищі (Deployment Guide)

Цей документ описує стандартизований процес розгортання Telegram-бота the-mix-bot на базі фреймворку Aiogram 3 та СУБД SQLite для виробничого середовища (Production).
1. Вимоги до апаратного та програмного забезпечення

Апаратні вимоги:
Для забезпечення стабільної роботи бота за допомогою Long Polling достатньо мінімальних ресурсів хмарного VPS-сервера :

    CPU: 1-2 vCPU (від 1.5 GHz).

    RAM: 1 - 2 GB оперативної пам'яті (щоб уникнути помилок OOM під час встановлення залежностей та роботи з БД).

    Disk: 10 - 20 GB SSD/NVMe дискового простору.

    Network: Від 10 Mbps.

Програмне забезпечення:

    Операційна система: Рекомендується Ubuntu 22.04 LTS або Debian 11/12.

    ПЗ: Python 3.10+ (фреймворк aiogram 3 вимагає сучасного синтаксису), Git, SQLite3, venv, systemd.

2. Налаштування мережі та безпеки

Бот працює через механізм Long Polling (ініціює вихідні запити до Telegram API), тому відкривати вхідні порти не потрібно. Налаштуйте брандмауер (UFW) для максимальної безпеки:
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw enable

Для дотримання принципу найменших привілеїв, бот не повинен працювати від імені користувача root. Створіть ізольованого системного користувача :

sudo useradd -r -s /bin/false telegram-bot
sudo mkdir -p /opt/the-mix-bot
sudo chown telegram-bot:telegram-bot /opt/the-mix-bot

3. Розгортання коду

Процес встановлення коду та залежностей має відбуватися від імені створеного користувача.

# Перехід у робочу директорію
cd /opt/the-mix-bot

# Клонування репозиторію
sudo -u telegram-bot git clone [https://github.com/liaamirt/the-mix-bot.git](https://github.com/liaamirt/the-mix-bot.git).

# Створення та активація ізольованого віртуального середовища
sudo -u telegram-bot python3 -m venv venv
sudo -u telegram-bot  -c "source venv/bin/activate && pip install --upgrade pip"

# Встановлення проектних залежностей
sudo -u telegram-bot  -c "source venv/bin/activate && pip install -r requirements.txt"

Створіть файл конфігурації .env з обмеженням доступу, щоб захистити ваш токен :

sudo -u telegram-bot nano.env

Внесіть наступні змінні (відповідно до config.py) :
Фрагмент коду

BOT_TOKEN=ваш_промисловий_токен
ADMIN_CHAT_ID=ідентифікатор_адміна
DB_PATH=themix.db

Обмежте права доступу до файлу з конфігурацією:

sudo chmod 600 /opt/the-mix-bot/.env

4. Налаштування СУБД (SQLite)

Оскільки проєкт використовує локальний файл бази даних themix.db (створюється автоматично скриптом database.py), окремого сервера бази даних піднімати не потрібно. Для забезпечення цілісності даних при паралельних запитах та підвищення швидкодії у production рекомендується активувати режим WAL (Write-Ahead Logging).
5. Конфігурація сервера (Systemd)

Для того, щоб бот автоматично запускався при завантаженні сервера та перезапускався у разі критичних помилок, необхідно створити сервіс для systemd.

Створіть конфігураційний файл:

sudo nano /etc/systemd/system/the-mix-bot.service

Додайте туди наступні інструкції :
Ini, TOML

[Unit]
Description=The Mix Restaurant Telegram Bot
After=network-online.target
Wants=network-online.target

Type=simple
User=telegram-bot
Group=telegram-bot
WorkingDirectory=/opt/the-mix-bot
EnvironmentFile=/opt/the-mix-bot/.env

# Запуск через інтерпретатор віртуального середовища
ExecStart=/opt/the-mix-bot/venv/bin/python main.py

# Політика перезапуску
Restart=always
RestartSec=10

# Базове посилення безпеки (Security Hardening)
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ReadWritePaths=/opt/the-mix-bot

[Install]
WantedBy=multi-user.target

Збережіть файл, оновіть конфігурацію демона та запустіть бота :

sudo systemctl daemon-reload
sudo systemctl enable the-mix-bot
sudo systemctl start the-mix-bot

6. Перевірка працездатності (Health Check)

Щоб переконатися, що розгортання виконано успішно, перевірте статус сервісу:

sudo systemctl status the-mix-bot

Вивід повинен містити маркер active (running).
Для моніторингу поведінки бота та перевірки наявності можливих помилок в режимі реального часу скористайтеся системним журналом :

sudo journalctl -u the-mix-bot -f

Фінальний тест: відкрийте Telegram та надішліть боту команду /start. Він має коректно та швидко відповісти.
