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
    "section_titles": (By.CSS_SELECTOR, "h2"),  # Селектор заголовков секций (h2)
    "all_content": (By.CSS_SELECTOR, ".page__content-desc p"),  # Селектор всех параграфов контента
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

    # Парсинг контента
    try:
        content_elements = WebDriverWait(driver, 15).until(
            EC.presence_of_all_elements_located(SELECTORS["all_content"])
        )
        section_titles = driver.find_elements(*SELECTORS["section_titles"])
        section_titles_text = [elem.text.strip() for elem in section_titles]

        # Распределение параграфов по секциям
        content_index = 0
        for i, title in enumerate(section_titles_text):
            section_content = []
            if title == "Руководство":
                # Для "Руководство" добавляем первый и второй параграфы
                if content_index < len(content_elements):
                    section_content.append(content_elements[content_index].text.strip())
                    content_index += 1
                if content_index < len(content_elements):
                    section_content.append(content_elements[content_index].text.strip())
                    content_index += 1
            elif title == "Попечительский совет":
                # Для "Попечительский совет" добавляем два параграфа
                if content_index < len(content_elements):
                    section_content.append(content_elements[content_index].text.strip())
                    content_index += 1
                if content_index < len(content_elements):
                    section_content.append(content_elements[content_index].text.strip())
                    content_index += 1
            else:
                # Для остальных секций добавляем один параграф
                if content_index < len(content_elements):
                    section_content.append(content_elements[content_index].text.strip())
                    content_index += 1

            result.append(("section", {"title": title, "content": section_content}))
            print(f"Обработана секция: {title}, контент: {section_content}")

    except Exception as e:
        print(f"Ошибка при парсинге контента: {str(e)}")

    print(f"Итоговые данные: {result}")
    return result, url

# Функция для сохранения данных в Markdown-файл
def save_to_markdown(data, url, filename="DPO_rukovodstvo.md"):
    content = []
    # Обработка элементов для форматирования в Markdown
    for item in data:
        if item[0] == "title":
            # Добавление основного заголовка и ссылки на страницу
            content.append(f"# {item[1]}")
            content.append(f"[Перейти к странице]({url})")
        elif item[0] == "section":
            section = item[1]
            if section["title"] == "Руководство":
                # Для "Руководство": первый параграф перед заголовком, второй — после
                content.extend(section["content"][:1])  # Первый параграф
                content.append(f"## {section['title']}")  # Заголовок секции
                content.extend(section["content"][1:])  # Второй параграф
            else:
                # Для остальных секций: заголовок, затем контент
                content.append(f"## {section['title']}")
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
    TARGET_URL = "https://academydpo.org/rukovodstvo"

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