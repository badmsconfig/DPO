# Импорт необходимых библиотек
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pathlib import Path

# Функция для настройки и получения веб-драйвера Chrome
def get_driver():
    # Настройка опций для браузера Chrome
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Запуск браузера в фоновом режиме (без GUI)
    chrome_options.add_argument("--disable-gpu")  # Отключение GPU для стабильности
    chrome_options.add_argument("--no-sandbox")  # Отключение песочницы для совместимости
    chrome_options.add_argument("--window-size=1920,1080")  # Установка размера окна браузера
    # Инициализация драйвера Chrome
    driver = webdriver.Chrome(options=chrome_options)
    return driver

# Словарь с CSS-селекторами для извлечения данных
SELECTORS = {
    "main_title": (By.CSS_SELECTOR, "h1.page__content-title"),  # Селектор основного заголовка
    "table_rows": (By.CSS_SELECTOR, "div.table table tbody tr"),  # Селектор строк таблицы
    "row_title": (By.CSS_SELECTOR, "td:nth-child(1) p"),  # Селектор заголовка строки
    "row_data": (By.CSS_SELECTOR, "td:nth-child(2) p")  # Селектор данных строки
}

# Функция для парсинга страницы
def parse_page(driver, url):
    # Загрузка страницы по указанному URL
    driver.get(url)
    try:
        # Ожидание загрузки основного заголовка (15 секунд)
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located(SELECTORS["main_title"])
        )
    except Exception as e:
        print(f"Ошибка загрузки страницы: {str(e)}")
        return [], url

    result = []

    # Извлечение основного заголовка
    try:
        main_title = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located(SELECTORS["main_title"])
        ).text.strip()
        result.append(("title", main_title))
        print(f"Основной заголовок: {main_title}")
    except Exception as e:
        print(f"Ошибка при парсинге основного заголовка: {str(e)}")

    # Парсинг таблицы
    try:
        rows = WebDriverWait(driver, 15).until(
            EC.presence_of_all_elements_located(SELECTORS["table_rows"])
        )
        table_content = []
        for row in rows:
            # Извлечение заголовка строки
            try:
                row_title = row.find_element(*SELECTORS["row_title"]).text.strip()
                print(f"Заголовок строки: {row_title}")
            except Exception as e:
                print(f"Ошибка при парсинге заголовка строки: {str(e)}")
                continue

            # Извлечение данных строки (все <p> в ячейке)
            try:
                data_elements = row.find_elements(*SELECTORS["row_data"])
                row_data = [elem.text.strip() for elem in data_elements if elem.text.strip()]
                row_data_text = "\n".join(row_data)
                print(f"Данные строки: {row_data_text}")
            except Exception as e:
                print(f"Ошибка при парсинге данных строки: {str(e)}")
                row_data_text = ""

            # Формирование строки в формате Markdown
            if row_title and row_data_text:
                table_content.append(f"### {row_title}\n{row_data_text}")

        if table_content:
            result.append(("content", table_content))
            print(f"Содержимое таблицы: {table_content}")
    except Exception as e:
        print(f"Ошибка при парсинге таблицы: {str(e)}")

    print(f"Итоговые данные: {result}")
    return result, url

# Функция для сохранения данных в Markdown-файл
def save_to_markdown(data, url, filename="DPO_osnovnye-svedeniya.md"):
    content = []
    # Обработка элементов для форматирования в Markdown
    for item in data:
        if item[0] == "title":
            # Добавление основного заголовка и ссылки на страницу
            content.append(f"# {item[1]}")
            content.append(f"[Перейти к странице]({url})")
        elif item[0] == "content":
            # Добавление содержимого таблицы
            content.extend(item[1])

    # Объединение контента с двумя пустыми строками между элементами
    final_content = "\n\n".join(line for line in content if line.strip())

    # Сохранение в файл с кодировкой UTF-8
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(final_content)

    print(f"Контент записан в файл: {filename}")
    return filename

# Основной блок программы
if __name__ == "__main__":
    # URL страницы для парсинга
    TARGET_URL = "https://academydpo.org/osnovnye-svedeniya"

    # Инициализация драйвера
    driver = get_driver()
    try:
        # Парсинг страницы и получение данных
        parsed_data, page_url = parse_page(driver, TARGET_URL)
        # Сохранение данных в Markdown-файл
        output_file = save_to_markdown(parsed_data, page_url)
        print(f"Файл {output_file} успешно сохранен!")
    except Exception as e:
        print(f"Ошибка при парсинге: {str(e)}")
    finally:
        # Закрытие драйвера для освобождения ресурсов
        driver.quit()