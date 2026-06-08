# Диаграммы

Три вида схемы — как в [dataroom-cms](https://github.com/sikuykus-lab/dataroom-cms):
**данные**, **взаимодействие пользователя**, **процессы администратора**.

Рендер: скопировать блок в [mermaid.live](https://mermaid.live).

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

## Процесс пользователя

```mermaid
flowchart LR
  A["Отправил мем"] --> B["В очереди"]
  B --> C{"Админ"}
  C -->|да| D["В канале"]
  C -->|нет| E["Тишина"]
```

## Процессы администратора

```mermaid
flowchart TD
  R1["BOT_TOKEN + ADMIN_USERNAME"] --> R2["Первый /start админа\n→ admin_chat_id.txt"]
  R2 --> R3["Очередь SUBMISSION"]
  R3 --> R4{"approve / reject"}
  R4 -->|approve| R5["Пост в канале"]
  R4 -->|reject| R6["Тишина для автора"]
```
