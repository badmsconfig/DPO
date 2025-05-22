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
    "intro_paragraph": (By.XPATH, "//div[contains(@class, 'page__content-desc')]/p[1]"),  # Селектор вводного параграфа
    "school_programs": (By.XPATH, "//div[contains(@class, 'wp-block-group-is-layout-flow')]//p[not(contains(text(), 'Академия также оказывает широкий спектр консалтинговых услуг'))]"),  # Селектор параграфов программ для школьников, исключая консалтинг
    "consulting": {
        "title": (By.XPATH, "//h2[contains(., 'Консалтинговые услуги')]"),  # Заголовок секции консалтинга
        "content": (By.XPATH, "//h2[contains(., 'Консалтинговые услуги')]/following-sibling::*[self::p or self::ul/li][preceding-sibling::h2[1][contains(., 'Консалтинговые услуги')]][not(following-sibling::h2)] | //h2[contains(., 'Консалтинговые услуги')]/following-sibling::*[self::p or self::ul/li][following-sibling::h2[1][contains(., 'Виды обучения')]]")  # Контент секции консалтинга
    },
    "education_types": {
        "title": (By.XPATH, "//h2[contains(., 'Виды обучения')]"),  # Заголовок секции видов обучения
        "content": (By.XPATH, "//h2[contains(., 'Виды обучения')]/following-sibling::*[self::p or self::ul/li][preceding-sibling::h2[1][contains(., 'Виды обучения')]][not(following-sibling::h2)] | //h2[contains(., 'Виды обучения')]/following-sibling::*[self::p or self::ul/li][following-sibling::h2[1][contains(., 'Курсы профессиональной переподготовки в Академии ДПО')]]")  # Контент секции видов обучения
    },
    "retraining": {
        "title": (By.XPATH, "//h2[contains(., 'Курсы профессиональной переподготовки в Академии ДПО')]"),  # Заголовок секции профпереподготовки
        "content": (By.XPATH, "//h2[contains(., 'Курсы профессиональной переподготовки в Академии ДПО')]/following-sibling::*[self::p or self::ul/li][preceding-sibling::h2[1][contains(., 'Курсы профессиональной переподготовки в Академии ДПО')]][not(following-sibling::h2)] | //h2[contains(., 'Курсы профессиональной переподготовки в Академии ДПО')]/following-sibling::*[self::p or self::ul/li][following-sibling::h2[1][contains(., 'Курсы повышения квалификации в Академии ДПО')]]")  # Контент секции профпереподготовки
    },
    "qualification": {
        "title": (By.XPATH, "//h2[contains(., 'Курсы повышения квалификации в Академии ДПО')]"),  # Заголовок секции повышения квалификации
        "content": (By.XPATH, "//h2[contains(., 'Курсы повышения квалификации в Академии ДПО')]/following-sibling::*[self::p or self::ul/li][preceding-sibling::h2[1][contains(., 'Курсы повышения квалификации в Академии ДПО')]][not(following-sibling::h2)] | //h2[contains(., 'Курсы повышения квалификации в Академии ДПО')]/following-sibling::*[self::p or self::ul/li][following-sibling::h2[1][contains(., 'Стоимость курсов')]]")  # Контент секции повышения квалификации
    },
    "pricing": {
        "title": (By.XPATH, "//h2[contains(., 'Стоимость курсов')]"),  # Заголовок секции стоимости
        "content": (By.XPATH, "//h2[contains(., 'Стоимость курсов')]/following-sibling::*[self::p or self::ul/li][preceding-sibling::h2[1][contains(., 'Стоимость курсов')]][not(following-sibling::h2)]")  # Контент секции стоимости
    }
}

# Функция для парсинга одной секции
def parse_section(driver, title_locator, content_locator):
    content = []
    try:
        # Извлечение заголовка секции
        try:
            title = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located(title_locator)
            ).text.strip()
            print(f"Найден заголовок секции: {title}")
        except Exception as e:
            print(f"Не удалось найти заголовок секции {title_locator}: {str(e)}")
            return None

        # Извлечение контента секции (параграфы и списки)
        try:
            elements = WebDriverWait(driver, 15).until(
                EC.presence_of_all_elements_located(content_locator)
            )
            seen_texts = set()  # Для предотвращения дублирования текста
            for element in elements:
                element_text = element.get_attribute('innerText').strip()
                if element_text and element_text not in seen_texts:
                    # Добавление символа • для элементов списка
                    if element.tag_name == "li":
                        content.append(f"• {element_text}")
                    else:
                        content.append(element_text)
                    seen_texts.add(element_text)
            print(f"Найден контент для секции '{title}': {content}")
        except Exception as e:
            print(f"Не удалось найти контент для секции '{title}': {str(e)}")

        return {"title": title, "content": content}
    except Exception as e:
        print(f"Общая ошибка в секции {title_locator}: {str(e)}")
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

    # Извлечение вводного параграфа
    try:
        intro_text = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located(SELECTORS["intro_paragraph"])
        ).text.strip()
        if intro_text:
            result.append(("content", [intro_text]))
            print(f"Вводный параграф: {intro_text}")
    except Exception as e:
        print(f"Ошибка при парсинге вводного параграфа: {str(e)}")

    # Извлечение программ для школьников
    try:
        school_elements = WebDriverWait(driver, 15).until(
            EC.presence_of_all_elements_located(SELECTORS["school_programs"])
        )
        school_text = [p.text.strip() for p in school_elements if p.text.strip()]
        if school_text:
            result.append(("content", school_text))
            print(f"Программы для школьников: {school_text}")
    except Exception as e:
        print(f"Ошибка при парсинге программ для школьников: {str(e)}")

    # Парсинг секции "Консалтинговые услуги"
    consulting = parse_section(driver, SELECTORS["consulting"]["title"], SELECTORS["consulting"]["content"])
    if consulting:
        result.append(("section", consulting))

    # Парсинг секции "Виды обучения"
    education_types = parse_section(driver, SELECTORS["education_types"]["title"], SELECTORS["education_types"]["content"])
    if education_types:
        result.append(("section", education_types))

    # Парсинг секции "Курсы профессиональной переподготовки"
    retraining = parse_section(driver, SELECTORS["retraining"]["title"], SELECTORS["retraining"]["content"])
    if retraining:
        result.append(("section", retraining))

    # Парсинг секции "Курсы повышения квалификации"
    qualification = parse_section(driver, SELECTORS["qualification"]["title"], SELECTORS["qualification"]["content"])
    if qualification:
        result.append(("section", qualification))

    # Парсинг секции "Стоимость курсов"
    pricing = parse_section(driver, SELECTORS["pricing"]["title"], SELECTORS["pricing"]["content"])
    if pricing:
        result.append(("section", pricing))

    print(f"Итоговые данные: {result}")
    return result, url

# Функция для сохранения данных в Markdown-файл
def save_to_markdown(data, url, filename="DPO_onas.md"):
    content = []
    # Обработка элементов для форматирования в Markdown
    for item in data:
        if item[0] == "title":
            # Добавление основного заголовка и ссылки на страницу
            content.append(f"# {item[1]}")
            content.append(f"[Перейти к странице]({url})")
        elif item[0] == "content":
            # Добавление параграфов (вводных или программ для школьников)
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
    TARGET_URL = "https://academydpo.org/o-nas"

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