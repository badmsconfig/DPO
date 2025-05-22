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
    "content_paragraphs": (By.CSS_SELECTOR, "div.page__content-desc p"),  # Селектор параграфов
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
        print(f"Ошибка при парсинге заголовка: {str(e)}")

    # Извлечение параграфов контента
    try:
        content_elements = WebDriverWait(driver, 15).until(
            EC.presence_of_all_elements_located(SELECTORS["content_paragraphs"])
        )
        content_text = [elem.text.strip() for elem in content_elements if elem.text.strip()]
        if content_text:
            result.append(("content", content_text))
            print(f"Параграфы контента: {content_text}")
    except Exception as e:
        print(f"Ошибка при парсинге контента: {str(e)}")

    print(f"Итоговые данные: {result}")
    return result, url

# Функция для сохранения данных в Markdown-файл
def save_to_markdown(data, url, filename="DPO_finhozdeyat.md"):
    content = []
    for item in data:
        if item[0] == "title":
            # Добавление заголовка в формате Markdown и ссылки на страницу
            content.append(f"# {item[1]}")
            content.append(f"[Перейти к странице]({url})")
        elif item[0] == "content":
            # Добавление параграфов контента
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
    TARGET_URL = "https://academydpo.org/finansovo-hozyajstvennaya-deyatelnost"

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