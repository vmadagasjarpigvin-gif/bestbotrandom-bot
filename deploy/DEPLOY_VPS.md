# Деплой Telegram-бота на VPS

## Рекомендуемый сервер

Для 5000+ участников достаточно VPS:

- 2 vCPU
- 4 GB RAM
- 40+ GB NVMe
- Ubuntu 24.04 LTS

Больше всего нагрузку ограничивает не сервер, а Telegram Bot API: обычная массовая рассылка около 30 сообщений/сек суммарно. Поэтому 5000 сообщений технически уходят примерно за 3–10 минут с безопасной задержкой и обработкой 429.

## Вариант 1 — Docker Compose

```bash
apt update && apt upgrade -y
apt install -y docker.io docker-compose-plugin unzip
systemctl enable --now docker

mkdir -p /opt/giveaway_bot
cd /opt/giveaway_bot
# загрузить giveaway_bot.zip на сервер
unzip giveaway_bot.zip
cd giveaway_bot
mkdir -p data
touch bot.sqlite3

docker compose up -d --build
docker compose logs -f giveaway-bot
```

Обновление:

```bash
cd /opt/giveaway_bot/giveaway_bot
docker compose down
docker compose up -d --build
```

## Вариант 2 — systemd без Docker

```bash
apt update && apt upgrade -y
apt install -y python3.12 python3.12-venv python3-pip unzip
mkdir -p /opt/giveaway_bot
cd /opt/giveaway_bot
# загрузить файлы проекта сюда
python3.12 -m venv .venv
.venv/bin/pip install -r requirements.txt
cp deploy/giveaway-bot.service /etc/systemd/system/giveaway-bot.service
systemctl daemon-reload
systemctl enable --now giveaway-bot
journalctl -u giveaway-bot -f
```

## Проверки

```bash
systemctl status giveaway-bot
journalctl -u giveaway-bot -n 100 --no-pager
```

## Бэкап базы

```bash
cp /opt/giveaway_bot/bot.sqlite3 /opt/giveaway_bot/bot.sqlite3.backup.$(date +%F-%H%M)
```
