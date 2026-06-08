# Telegram Meme Bot

Короче: **фото в ЛС → очередь → модератор → канал**, две кнопки, без веб-админки.

Задача: принимать мемы от подписчиков, не засоряя канал спамом. Админ видит одну карточку — опубликовать или отклонить.

---

## Что сделано

- **Очередь pending** в SQLite.
- **Approve / reject** — inline у админа.
- **Пост в канал** — с атрибуцией или анонимно.
- **Антиспам** по user_id.

---

## Фишки и удобство

| Фишка | Зачем |
|-------|-------|
| `/submit` или просто фото | Низкий порог для автора |
| «Принято в очередь» | Автор не видит модерацию |
| Две кнопки админу | Быстро, без лишних экранов |
| Очередь в БД | Перезапуск бота не теряет pending |

---

## Схема данных

```mermaid
flowchart TB
  subgraph author ["Автор"]
    PH["Фото в ЛС"]
  end

  subgraph bot ["Meme Bot"]
    Q["SUBMISSION pending"]
    ADM["Модератор"]
  end

  subgraph out ["Канал"]
    CH["Post"]
  end

  PH --> Q
  Q --> ADM
  ADM -->|approve| CH
  ADM -->|reject| Q
```

---

## Процесс пользователя

```mermaid
flowchart LR
  A["Отправил мем"] --> B["В очереди"]
  B --> C{"Админ"}
  C -->|да| D["В канале"]
  C -->|нет| E["Тишина"]
```

**Модератор / админ:**

```mermaid
flowchart TD
  R1["BOT_TOKEN + ADMIN_USERNAME"] --> R2["Первый /start админа\n→ admin_chat_id.txt"]
  R2 --> R3["Очередь SUBMISSION"]
  R3 --> R4{"approve / reject"}
  R4 -->|approve| R5["Пост в канале"]
  R4 -->|reject| R6["Тишина для автора"]
```

---

## Стек

| Слой | Технология |
|------|------------|
| Бот | python-telegram-bot |
| Очередь | SQLite |
| Секреты | BOT_TOKEN, ADMIN_USERNAME |

---

## Структура репозитория

```
README.md
LICENSE
.gitignore
bot/bot.py
docs/                     — DIAGRAMS.md (3× mermaid)
examples/.env.example
requirements.txt
```

---

## Быстрый старт

```bash
export BOT_TOKEN="..."
export ADMIN_USERNAME="..."
python3 bot.py
```

Бот должен быть **админом канала** с правом post.
