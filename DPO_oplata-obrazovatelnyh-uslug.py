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

# Словарь с CSS/XPath-селекторами для извлечения данных
SELECTORS = {
    "main_title": (By.CSS_SELECTOR, "h1.page__content-title"),  # Селектор основного заголовка
    "section_titles": (By.CSS_SELECTOR, "h2"),  # Селектор заголовков секций (h2)
    # Селектор для контента секции: <p> и <h3> между текущим <h2> и следующим <h2> (или до конца)
    "section_content": (By.XPATH, "./following-sibling::*[self::p or self::h3][preceding-sibling::h2[1][contains(., '{current_title}')]][following-sibling::h2[1][contains(., '{next_title}')]] | ./following-sibling::*[self::p or self::h3][preceding-sibling::h2[1][contains(., '{current_title}')]][not(following-sibling::h2)]")
}

# Функция для парсинга одной секции
def parse_section(driver, section_element, current_title, next_title=None):
    content = []
    try:
        # Извлечение заголовка секции
        title = section_element.text.strip()
        print(f"Найден заголовок секции: {title}")

        # Формирование селектора для контента секции
        if next_title:
            content_selector = (By.XPATH, SELECTORS["section_content"][1].format(current_title=title, next_title=next_title))
        else:
            content_selector = (By.XPATH, SELECTORS["section_content"][1].format(current_title=title, next_title=""))

        # Извлечение контента секции (<p> и <h3> в порядке появления)
        content_elements = section_element.find_elements(*content_selector)
        for element in content_elements:
            element_text = element.get_attribute('innerText').strip()
            if element_text:
                # Если элемент — <h3>, добавляем как подзаголовок
                if element.tag_name == "h3":
                    content.append(f"### {element_text}")
                else:
                    # Разбиваем текст <p> на строки, учитывая <br> и списки с •
                    lines = element_text.replace("\n", " ").split("  ")  # Учитываем двойные пробелы после <br>
                    for line in lines:
                        line = line.strip()
                        if not line:
                            continue
                        if "•" in line:
                            # Разбиваем по • для обработки элементов списка
                            sub_lines = line.split("•")
                            for sub_line in sub_lines:
                                sub_line = sub_line.strip()
                                if sub_line:
                                    # Удаляем точку с запятой в конце, если есть
                                    sub_line = sub_line.rstrip(";")
                                    content.append(f"• {sub_line}")
                        else:
                            content.append(line)
        print(f"Найден контент для секции '{title}': {content}")
        return {"title": title, "content": content}
    except Exception as e:
        print(f"Общая ошибка в секции {title}: {str(e)}")
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

    # Парсинг секций
    try:
        section_elements = WebDriverWait(driver, 15).until(
            EC.presence_of_all_elements_located(SELECTORS["section_titles"])
        )
        section_titles = [elem.text.strip() for elem in section_elements]

        for i, section_element in enumerate(section_elements):
            # Определение следующего заголовка (если есть)
            next_title = section_titles[i + 1] if i + 1 < len(section_titles) else None
            section = parse_section(driver, section_element, section_titles[i], next_title)
            if section:
                result.append(("section", section))
    except Exception as e:
        print(f"Ошибка при парсинге секций: {str(e)}")

    print(f"Итоговые данные: {result}")
    return result, url

# Функция для сохранения данных в Markdown-файл
def save_to_markdown(data, url, filename="DPO_oplata-obrazovatelnyh-uslug.md"):
    content = []
    # Обработка элементов для форматирования в Markdown
    for item in data:
        if item[0] == "title":
            # Добавление основного заголовка и ссылки на страницу
            content.append(f"# {item[1]}")
            content.append(f"[Перейти к странице]({url})")
        elif item[0] == "content":
            # Добавление параграфов
            content.extend(item[1])
        elif item[0] == "section":
            # Добавление заголовка секции и ее контента
            section = item[1]
            content.append(f"## {section['title']}")
            content.extend(section['content'])

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
    TARGET_URL = "https://academydpo.org/oplata-obrazovatelnyh-uslug"

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