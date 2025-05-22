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
    "section_titles": (By.CSS_SELECTOR, "h2"),  # Селектор подзаголовков
    "content_paragraphs": (By.CSS_SELECTOR, ".page__content-desc > *"),  # Селектор всех дочерних элементов контента
}

# Функция для парсинга страницы
def parse_page(driver, url):
    # Загрузка страницы по указанному URL
    driver.get(url)
    try:
        # Ожидание загрузки основного заголовка (10 секунд)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(SELECTORS["main_title"])
        )
    except Exception as e:
        print(f"Ошибка загрузки страницы: {str(e)}")
        return [], url

    content = []

    # Извлечение основного заголовка
    try:
        main_title = driver.find_element(*SELECTORS["main_title"]).text.strip()
        content.append(("title", main_title))
        print(f"Основной заголовок: {main_title}")
    except Exception as e:
        print(f"Ошибка при парсинге заголовка: {str(e)}")

    # Извлечение всего контента (подзаголовки, параграобы, списки)
    try:
        elements = driver.find_elements(*SELECTORS["content_paragraphs"])
        for el in elements:
            tag = el.tag_name
            text = el.text.strip()
            if not text:
                continue

            if tag == "h2":
                # Форматирование подзаголовка для Markdown
                content.append(("section_title", text))
            elif tag == "ul":
                # Извлечение элементов списка
                items = el.find_elements(By.TAG_NAME, "li")
                for li in items:
                    li_text = li.text.strip().rstrip(";")
                    if li_text:
                        content.append(("list_item", f"• {li_text}"))
            else:
                # Добавление параграфов или других элементов
                content.append(("paragraph", text))

        print(f"Итоговый контент: {content}")
    except Exception as e:
        print(f"Ошибка при парсинге контента: {str(e)}")

    return content, url

# Функция для сохранения данных в Markdown-файл
def save_to_markdown(data, url, filename="DPO_matertehnichobespechenieiosnashhennost.md"):
    content = []
    # Добавление основного заголовка и ссылки на страницу
    for item in data:
        if item[0] == "title":
            content.append(f"# {item[1]}")
            content.append(f"[Перейти к странице]({url})")
        elif item[0] == "section_title":
            # Форматирование подзаголовка
            content.append(f"## {item[1]}")
        elif item[0] == "list_item":
            # Добавление элемента списка
            content.append(item[1])
        elif item[0] == "paragraph":
            # Добавление параграфа
            content.append(item[1])

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
    TARGET_URL = "https://academydpo.org/materialno-tehnicheskoe-obespechenie-i-osnashhennost"

    # Инициализация драйвера
    driver = get_driver()
    try:
        # Парсинг страницы и получение данных
        parsed_content, page_url = parse_page(driver, TARGET_URL)
        # Сохранение данных в Markdown-файл
        output_file = save_to_markdown(parsed_content, page_url)
        print(f"Файл {output_file} успешно сохранен!")
    except Exception as e:
        print(f"Ошибка при парсинге: {str(e)}")
    finally:
        # Закрытие драйвера для освобождения ресурсов
        driver.quit()