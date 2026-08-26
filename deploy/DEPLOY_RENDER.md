# Деплой Telegram-бота на Render

## Что создано
Файл `render.yaml` описывает Render Background Worker для polling-бота:

- сервис: `bestbotrandom-bot`
- запуск: `python -m app.main`
- хранение SQLite: `/var/data/bot.sqlite3`
- persistent disk: `bot-data`, 1 GB
- канал: `@irisha_starsik`
- бот username для рефок: `bestbotrandom_bot`
- админы: `1816081573,8134306958`, username `sexmakson`

## Важно
Для Telegram polling-бота нужен именно Render **Background Worker**, а не Web Service. Web Service должен слушать `$PORT`, а этот бот работает как постоянный фоновый процесс.

## Как поставить
1. Создай приватный GitHub/GitLab репозиторий.
2. Загрузи туда содержимое этой папки `giveaway_bot`.
3. В Render открой New → Blueprint.
4. Подключи репозиторий с этим `render.yaml`.
5. Render попросит secret env vars:
   - `BOT_TOKEN` — вставь текущий токен бота.
   - `ADMIN_PASSCODE` — придумай пароль для входа в админку, например `admin-XXXX`.
6. Нажми Apply / Deploy.

## После запуска
В Telegram напиши боту `/start`, затем админ — `/admin`.

## Если надо поменять токен
В Render → сервис `bestbotrandom-bot` → Environment → `BOT_TOKEN` → Save Changes → Manual Deploy / Restart.

## Если надо поменять канал/тексты/задержку
Пиши боту `/admin`; большинство настроек меняются там без перезаливки кода.
