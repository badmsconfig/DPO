from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pathlib import Path

# Словарь селекторов
SELECTORS = {
    "main_title": (By.CSS_SELECTOR, "h1.page__content-title"),
    "intro_paragraph": (By.CSS_SELECTOR, "div.page__content-desc > p:first-child"),
    "sections": {
        "terms": {
            "title": (By.XPATH, "//h2[contains(., '1. Определение терминов')]"),
            "content": (By.XPATH, "//h2[contains(., '1. Определение терминов')]/following-sibling::p[preceding-sibling::h2[1][contains(., '1. Определение терминов')]][following-sibling::h2[1][contains(., '2. Общие положения')]]")
        },
        "general_provisions": {
            "title": (By.XPATH, "//h2[contains(., '2. Общие положения')]"),
            "content": (By.XPATH, "//h2[contains(., '2. Общие положения')]/following-sibling::p[preceding-sibling::h2[1][contains(., '2. Общие положения')]][following-sibling::h2[1][contains(., '3. Предмет политики конфиденциальности')]]")
        },
        "subject": {
            "title": (By.XPATH, "//h2[contains(., '3. Предмет политики конфиденциальности')]"),
            "content": (By.XPATH, "//h2[contains(., '3. Предмет политики конфиденциальности')]/following-sibling::p[preceding-sibling::h2[1][contains(., '3. Предмет политики конфиденциальности')]][following-sibling::h2[1][contains(., '4. Цели сбора персональной информации пользователя')]]")
        },
        "purposes": {
            "title": (By.XPATH, "//h2[contains(., '4. Цели сбора персональной информации пользователя')]"),
            "content": (By.XPATH, "//h2[contains(., '4. Цели сбора персональной информации пользователя')]/following-sibling::p[preceding-sibling::h2[1][contains(., '4. Цели сбора персональной информации пользователя')]][following-sibling::h2[1][contains(., '5. Способы и сроки обработки персональной информации')]]")
        },
        "processing_methods": {
            "title": (By.XPATH, "//h2[contains(., '5. Способы и сроки обработки персональной информации')]"),
            "content": (By.XPATH, "//h2[contains(., '5. Способы и сроки обработки персональной информации')]/following-sibling::p[preceding-sibling::h2[1][contains(., '5. Способы и сроки обработки персональной информации')]][following-sibling::h2[1][contains(., '6. Права и обязанности сторон')]]")
        },
        "rights_obligations": {
            "title": (By.XPATH, "//h2[contains(., '6. Права и обязанности сторон')]"),
            "content": (By.XPATH, "//h2[contains(., '6. Права и обязанности сторон')]/following-sibling::p[preceding-sibling::h2[1][contains(., '6. Права и обязанности сторон')]][following-sibling::h2[1][contains(., '7. Ответственность сторон')]]")
        },
        "responsibility": {
            "title": (By.XPATH, "//h2[contains(., '7. Answerственность сторон')]"),
            "content": (By.XPATH, "//h2[contains(., '7. Ответственность сторон')]/following-sibling::p[preceding-sibling::h2[1][contains(., '7. Ответственность сторон')]][following-sibling::h2[1][contains(., '8. Разрешение споров')]]")
        },
        "dispute_resolution": {
            "title": (By.XPATH, "//h2[contains(., '8. Разрешение споров')]"),
            "content": (By.XPATH, "//h2[contains(., '8. Разрешение споров')]/following-sibling::p[preceding-sibling::h2[1][contains(., '8. Разрешение споров')]][following-sibling::h2[1][contains(., '9. Дополнительные условия')]]")
        },
        "additional_conditions": {
            "title": (By.XPATH, "//h2[contains(., '9. Дополнительные условия')]"),
            "content": (By.XPATH, "//h2[contains(., '9. Дополнительные условия')]/following-sibling::p[preceding-sibling::h2[1][contains(., '9. Дополнительные условия')]]")
        }
    },
    "footer_paragraphs": (By.XPATH, "//div[contains(@class, 'page__content-desc')]/p[position() > last()-3 and position() <= last()-1]")
}

# Функция для настройки и получения веб-драйвера Chrome
def get_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--window-size=1920,1080")
    driver = webdriver.Chrome(options=chrome_options)
    return driver

# Функция для парсинга секции
def parse_section(driver, title_locator, content_locator):
    content = []
    try:
        title = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located(title_locator)
        ).text.strip()
        print(f"Найден заголовок секции: {title}")
    except Exception as e:
        print(f"Не удалось найти заголовок секции {title_locator}: {str(e)}")
        return None

    try:
        elements = WebDriverWait(driver, 15).until(
            EC.presence_of_all_elements_located(content_locator)
        )
        seen_texts = set()
        for element in elements:
            element_text = element.get_attribute('innerText').strip()
            if element_text and element_text not in seen_texts:
                content.append(element_text)
                seen_texts.add(element_text)
        print(f"Найден контент для секции '{title}': {content}")
    except Exception as e:
        print(f"Не удалось найти контент для секции '{title}': {str(e)}")

    return {"title": title, "content": content}

# Функция для парсинга страницы
def parse_page(driver, url):
    driver.get(url)
    try:
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

    # Парсинг секций
    for section_key, section_data in SELECTORS["sections"].items():
        section = parse_section(driver, section_data["title"], section_data["content"])
        if section:
            result.append(("section", section))

    # Извлечение завершающих параграфов
    try:
        footer_paragraphs = WebDriverWait(driver, 15).until(
            EC.presence_of_all_elements_located(SELECTORS["footer_paragraphs"])
        )
        footer_texts = [p.text.strip() for p in footer_paragraphs if p.text.strip()]
        if footer_texts:
            result.append(("content", footer_texts))
            print(f"Завершающие параграфы: {footer_texts}")
    except Exception as e:
        print(f"Ошибка при парсинге завершающих параграфов: {str(e)}")

    return result, url

# Функция для сохранения данных в Markdown-файл
def save_to_markdown(data, url, filename="DPO_politika_konfidentsialnosti.md"):
    content = []
    for item in data:
        if item[0] == "title":
            content.append(f"# {item[1]}")
            content.append(f"[Перейти к странице]({url})")
        elif item[0] == "content":
            content.extend(item[1])
        elif item[0] == "section":
            section = item[1]
            content.append(f"## {section['title']}")
            content.extend(section['content'])

    final_content = "\n\n".join(line for line in content if line.strip())
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(final_content)
    print(f"Контент записан в файл: {filename}")
    return filename

# Основной блок программы
if __name__ == "__main__":
    TARGET_URL = "https://academydpo.org/politika-konfidentsialnosti-personalnyh-dannyh"
    driver = get_driver()
    try:
        parsed_data, page_url = parse_page(driver, TARGET_URL)
        output_file = save_to_markdown(parsed_data, page_url)
        print(f"Файл {output_file} успешно сохранен!")
    except Exception as e:
        print(f"Ошибка при парсинге: {str(e)}")
    finally:
        driver.quit()