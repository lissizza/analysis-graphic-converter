# Телеграм-бот для обработки PDF-файлов c результатами анализов на органические кислоты в моче и аминокислоты в крови.

Этот телеграм-бот умеет делать из цифровых результатов анализов наглядные графические результаты. Благодаря этому можно сразу увидеть, где значения приближаются к критическим или выходят за пределы референсного интервала.
Он принимает PDF файлы с результатами анализов, обрабатывает их, и предоставляет пользователю возможность скачать результаты в формате PNG или PDF. 
На данный момент поддерживаются только файлы результатов на органические кислоты в моче и аминокислоты в крови для лаборатории Helix.

## Требования

- Python 3.10+
- Основные библиотеки:
  - `python-telegram-bot`
  - `pdfplumber`
  - `pandas`
  - `matplotlib`
  - `nest_asyncio`
  - `python-dotenv`

## Установка

1. Клонируйте репозиторий:

    ```bash
    git clone <URL_вашего_репозитория>
    cd <название_репозитория>
    ```

2. Создайте виртуальное окружение и активируйте его:

    ```bash
    python -m venv venv
    source venv/bin/activate  # Для Windows используйте `venv\Scripts\activate`
    ```

3. Установите зависимости:

    ```bash
    pip install -r requirements.txt
    ```

4. Создайте файл `.env` в корневой директории проекта и добавьте в него ваш токен Telegram-бота:

    ```dotenv
    BOT_TOKEN=ваш_телеграм_токен
    ```

## Использование

1. Запустите бота:

    ```bash
    python bot.py
    ```

2. В Telegram начните чат с вашим ботом, отправьте команду `/start` и следуйте инструкциям.

## Структура проекта

- `bot.py`: Основной файл для запуска бота.
- `handlers.py`: Функции-обработчики команд и сообщений бота.
- `pdf_processing.py`: Логика извлечения данных из PDF файлов.
- `plotting.py`: Логика построения графиков на основе данных.

## Безопасность

Для обеспечения безопасности бота:

- Используйте контейнеры (например, Docker) для изоляции среды выполнения.
- Регулярно обновляйте зависимости.
- Включите полное логирование и мониторинг.

## Лицензия

Этот проект лицензирован под MIT License. Подробности смотрите в файле LICENSE.

## Вклад

Если вы хотите внести свой вклад в проект, пожалуйста, создайте новый pull request. Мы приветствуем все предложения и улучшения.
