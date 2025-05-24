# Импорт необходимых библиотек
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
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

# Словарь с CSS/XPath-селекторами для извлечения данных
SELECTORS = {
    "main_title": (By.CSS_SELECTOR, "h1.page__content-title"),  # Селектор основного заголовка
    "intro_paragraphs": (By.XPATH, "//div[contains(@class, 'page__content-desc')]//p[not(preceding-sibling::h2) and not(preceding-sibling::h3)]"),  # Селектор вводных параграфов
    "sub_titles": (By.CSS_SELECTOR, "div.page__content-desc h2, div.page__content-desc h3"),  # Селектор подзаголовков (h2, h3)
    "list_items": (By.XPATH, "./li"),  # Селектор элементов списка
}

# Функция для нормализации текста
def normalize_text(text):
    # Удаление лишних пробелов и нормализация пробелов перед запятыми
    text = re.sub(r'\s+', ' ', text).strip()
    text = re.sub(r'\s*,\s*', ', ', text)
    return text

# Функция для парсинга одной секции
def parse_section(driver, sub_title_element):
    content = []
    try:
        # Извлечение заголовка секции и его тега
        title = sub_title_element.text.strip()
        tag = sub_title_element.tag_name  # h2 или h3
        print(f"Найден подзаголовок ({tag}): {title}")

        # Извлечение контента секции (<p> или <ul>)
        try:
            # Находим все следующие элементы до следующего <h2> или <h3>
            next_elements = sub_title_element.find_elements(By.XPATH, "./following-sibling::*")
            for element in next_elements:
                # Если встретили следующий <h2> или <h3>, прерываем цикл
                if element.tag_name in ["h2", "h3"]:
                    break
                # Обрабатываем <p>
                if element.tag_name == "p":
                    element_text = element.get_attribute('innerText')
                    element_text = normalize_text(element_text)
                    if element_text:
                        content.append(element_text)
                # Обрабатываем <ul>
                elif element.tag_name == "ul":
                    list_items = element.find_elements(*SELECTORS["list_items"])
                    for item in list_items:
                        item_text = item.get_attribute('innerText')
                        item_text = normalize_text(item_text)
                        if item_text:
                            content.append(f"• {item_text}")  # Убрана табуляция для стандартного Markdown
            print(f"Найден контент для секции '{title}': {content}")
        except Exception as e:
            print(f"Не удалось найти контент для секции '{title}': {str(e)}")

        return {"title": title, "tag": tag, "content": content}
    except Exception as e:
        print(f"Общая ошибка в секции: {str(e)}")
        return None

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

    # Извлечение вводных параграфов
    try:
        intro_elements = WebDriverWait(driver, 15).until(
            EC.presence_of_all_elements_located(SELECTORS["intro_paragraphs"])
        )
        intro_text = [normalize_text(elem.text) for elem in intro_elements if elem.text.strip()]
        if intro_text:
            result.append(("content", intro_text))
            print(f"Вводные параграфы: {intro_text}")
        else:
            print("Вводные параграфы не найдены.")
    except Exception as e:
        print(f"Ошибка при парсинге вводных параграфов: {str(e)}")

    # Парсинг подзаголовков и их контента
    try:
        sub_title_elements = WebDriverWait(driver, 15).until(
            EC.presence_of_all_elements_located(SELECTORS["sub_titles"])
        )
        for sub_title_element in sub_title_elements:
            section = parse_section(driver, sub_title_element)
            if section:
                result.append(("section", section))
    except Exception as e:
        print(f"Ошибка при парсинге подзаголовков: {str(e)}")

    print(f"Итоговые данные: {result}")
    return result, url

# Функция для сохранения данных в Markdown-файл
def save_to_markdown(data, url, filename="DPO_vakantnye-mesta-dlya-priema-perevoda.md"):
    content = []
    # Обработка элементов для форматирования в Markdown
    for item in data:
        if item[0] == "title":
            # Добавление основного заголовка и ссылки на страницу
            content.append(f"# {item[1]}")
            content.append(f"[Перейти к странице]({url})")
        elif item[0] == "content":
            # Добавление вводных параграфов
            content.extend(item[1])
        elif item[0] == "section":
            section = item[1]
            # Форматирование заголовка в зависимости от тега (h2 или h3)
            if section["tag"] == "h2":
                content.append(f"## {section['title']}")
            else:
                content.append(f"### {section['title']}")
            content.extend(section["content"])

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
    TARGET_URL = "https://academydpo.org/vakantnye-mesta-dlya-priema-perevoda"

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