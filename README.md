# TicTacToe Telegram Mini App

## Описание проекта

**TicTacToe Telegram Mini App** — production-ready мини-приложение для Telegram, в котором пользователь играет в «Крестики-нолики» против интеллектуального AI-соперника.

Проект спроектирован как полноценный коммерческий продукт: аккуратный UX, честная игровая логика, автоматическая выдача промокодов при победе, масштабируемая архитектура и развитая наблюдаемость.

Мини-приложение запускается напрямую внутри Telegram (Telegram Mini App) и не требует установки.

---

## Ключевые возможности

- 🎮 Игра «Крестики-нолики» 3×3 (игрок vs компьютер)
- 🤖 AI на базе **Minimax с alpha-beta pruning**
- 🎁 Генерация уникальных промокодов при победе
- 📩 Уведомления о результате партии в Telegram-бот
- 🎨 Уютный, «cozy / premium» интерфейс (ориентация на аудиторию 25–40)
- 📊 Полноценный мониторинг: Prometheus + Grafana (дашборды и алерты)
- 🔐 HTTPS-инфраструктура (обязательное требование Telegram Mini App)
- 🐳 Docker Compose для dev и prod окружений

---

## Технологический стек

| Слой           | Технологии                                         |
| -------------- | -------------------------------------------------- |
| Frontend       | Nuxt 3, TypeScript, Pinia, TailwindCSS, Vitest     |
| Backend        | FastAPI 0.115, Python 3.12, uv, Clean Architecture |
| AI             | Minimax + alpha-beta pruning                       |
| Хранилище      | Redis (промокоды), Postgres (данные Grafana)       |
| Мониторинг     | Prometheus, Grafana (дашборды + алерты)            |
| Инфраструктура | Nginx + Certbot, Docker Compose, cloudflared (dev) |

---

## Структура репозитория

```
apps/frontend         # Nuxt 3 фронтенд (Telegram Mini App)
apps/backend          # FastAPI backend (Clean Architecture)
monitoring/           # Prometheus, Grafana, дашборды и алерты
docker/               # Dockerfile'ы
docker-compose.dev.yml
docker-compose.prod.yml
```

---

## Переменные окружения

Для запуска проекта необходимо скопировать `.env.example` (dev) или `.env.prod.example` (prod) в `.env` и заполнить значения.

| Переменная              | Назначение                       |
| ----------------------- | -------------------------------- |
| ENV                     | `dev` или `prod`                 |
| FRONTEND_ORIGIN         | HTTPS-домен Mini App             |
| DOMAIN                  | Публичный домен продакшена       |
| LETSENCRYPT_EMAIL       | Email для ACME / Let's Encrypt   |
| TELEGRAM_BOT_TOKEN      | Токен Telegram-бота              |
| TELEGRAM_CHAT_ID        | Fallback chat_id (через запятую) |
| TELEGRAM_WEBHOOK_SECRET | Секрет webhook                   |
| REDIS_URL               | DSN Redis                        |
| POSTGRES_USER           | Пользователь Postgres (Grafana)  |
| POSTGRES_PASSWORD       | Пароль Postgres                  |
| POSTGRES_DB             | База Postgres                    |
| NUXT_PUBLIC_API_BASE    | Базовый URL backend              |
| PROMO_CODE_TTL_DAYS     | Время жизни промокода            |
| PROMO_CODE_LENGTH       | Длина промокода                  |
| GAME_DIFFICULTY_LEVEL   | Уровень сложности ИИ (1–3)       |

---

## Backend (FastAPI)

### Локальный запуск

```bash
cd apps/backend
uv sync
uv run ruff check .
uv run mypy src
uv run pytest --cov
uv run uvicorn tictactoe.main:app --reload
```

### Основные эндпоинты

- `POST /api/v1/game/move` — обработка хода игрока
- `POST /api/v1/game/reset` — сброс партии
- `GET /health` — health-check
- `GET /metrics` — метрики Prometheus
- `POST /api/v1/telegram/webhook/{secret}` — webhook Telegram-бота

---

## Frontend (Nuxt 3)

```bash
cd apps/frontend
pnpm install
pnpm lint
pnpm test
pnpm dev --host 0.0.0.0 --port 3000
```

### Особенности фронтенда

- Pinia store как единый источник состояния
- `useTelegramWebApp` — интеграция Telegram WebApp SDK
- Поддержка haptic feedback
- UI-состояния победы / поражения / ничьей
- Полная совместимость с мобильным Telegram

---

## Тестирование Mini App через cloudflared (dev)

```bash
docker compose -f docker-compose.dev.yml up --build
cloudflared tunnel --url http://localhost:3000
```

В BotFather:

```
/setdomain → URL туннеля
```

После настройки DNS и HTTPS вернуть:

```
https://<DOMAIN>/
```

---

## Подключение Telegram-бота

1. `/setdomain` → `https://<DOMAIN>/`
2. `/setmenubutton` → WebApp URL
3. Установить webhook:
   ```
   https://api.telegram.org/bot<TELEGRAM_BOT_TOKEN>/setWebhook?url=https://<DOMAIN>/api/v1/telegram/webhook/<TELEGRAM_WEBHOOK_SECRET>
   ```
4. Команда `/start` возвращает кнопку запуска Mini App

---

## Docker Compose

### Development

```bash
docker compose -f docker-compose.dev.yml up --build
```

Сервисы:

- frontend (Nuxt dev)
- backend (autoreload)
- Redis
- Postgres
- Prometheus
- Grafana (`http://localhost:3001`, admin/admin)

Postgres используется Grafana для хранения данных.

### Production

```bash
docker compose -f docker-compose.prod.yml --env-file .env up --build -d
```

В продакшене:

- Nginx как reverse-proxy
- Автоматический HTTPS через Let's Encrypt
- Certbot с автообновлением сертификатов
- Полный набор сервисов из dev-окружения

⚠️ Не забудьте открыть порты **80/443** и направить `DOMAIN` на IP сервера.

---

## Мониторинг и алерты

- Prometheus собирает метрики backend
- Grafana содержит готовые дашборды
- Алерты:
  - сбои Telegram-уведомлений
  - p95 latency `/move`
  - рост 5xx ошибок

Grafana использует Postgres для устойчивого хранения данных.

---

## Portainer (опционально)

```bash
docker volume create portainer_data
docker run -d \
  -p 8000:8000 -p 9443:9443 \
  --name portainer \
  --restart=unless-stopped \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v portainer_data:/data \
  portainer/portainer-ce:2.21.4
```

Открыть:

```
https://<host>:9443
```

---

## Чеклист деплоя

1. Настроить DNS (`DOMAIN` → IP сервера)
2. Открыть порты 80 и 443
3. Заполнить `.env`
4. Запустить prod-стек Docker Compose
5. Настроить BotFather (domain, menu button, webhook)
6. Проверить:
   - `/health`
   - `/metrics`
   - победа / поражение
   - дашборды Grafana

---

## Уровни сложности ИИ

| Уровень | Поведение                            |
| ------- | ------------------------------------ |
| 1       | Расслабленный AI (~80% побед игрока) |
| 2       | Сбалансированный режим (~40% побед)  |
| 3       | Почти безошибочный AI (~5% побед)    |

Изменение уровня сложности не требует перекомпиляции — достаточно перезапустить контейнеры с новым значением `GAME_DIFFICULTY_LEVEL`.

---
