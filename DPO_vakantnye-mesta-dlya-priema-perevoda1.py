from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pathlib import Path

# Словарь селекторов для страницы https://academydpo.org/vakantnye-mesta-dlya-priema-perevoda
SELECTORS = {
    "main_title": (By.CSS_SELECTOR, "h1.page__content-title"),
    "sub_title_h3": (By.CSS_SELECTOR, "div.page__content-desc > h3"),
    "sub_title_h2": (By.CSS_SELECTOR, "div.page__content-desc > h2"),
    "paragraphs": (By.CSS_SELECTOR, "div.page__content-desc > p"),
    "list_items": (By.CSS_SELECTOR, "div.page__content-desc > ul > li")
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

    # Извлечение подзаголовка h3
    try:
        sub_title_h3 = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located(SELECTORS["sub_title_h3"])
        ).text.strip()
        result.append(("sub_title_h3", sub_title_h3))
        print(f"Подзаголовок h3: {sub_title_h3}")
    except Exception as e:
        print(f"Ошибка при парсинге подзаголовка h3: {str(e)}")

    # Извлечение подзаголовков h2
    try:
        sub_titles_h2 = WebDriverWait(driver, 15).until(
            EC.presence_of_all_elements_located(SELECTORS["sub_title_h2"])
        )
        sub_titles_h2_texts = [h2.text.strip() for h2 in sub_titles_h2 if h2.text.strip()]
        if sub_titles_h2_texts:
            result.append(("sub_titles_h2", sub_titles_h2_texts))
            print(f"Подзаголовки h2: {sub_titles_h2_texts}")
    except Exception as e:
        print(f"Ошибка при парсинге подзаголовков h2: {str(e)}")

    # Извлечение параграфов и списка
    try:
        paragraphs = WebDriverWait(driver, 15).until(
            EC.presence_of_all_elements_located(SELECTORS["paragraphs"])
        )
        paragraph_texts = []
        list_processed = False
        for i, p in enumerate(paragraphs):
            p_text = p.text.strip()
            # Обработка параграфа перед списком направлений
            if not list_processed and "таких сфер деятельности, как" in p_text:
                try:
                    ul = p.find_element(By.XPATH, "./following-sibling::ul")
                    li_elements = ul.find_elements(By.CSS_SELECTOR, "li")
                    measures = []
                    for li in li_elements:
                        li_text = li.text.strip().rstrip(";")  # Удаление точек с запятой
                        try:
                            a = li.find_element(By.CSS_SELECTOR, "a")
                            href = a.get_attribute("href")
                            measures.append(f"- [{li_text}]({href})")
                        except:
                            measures.append(f"- {li_text}")
                    p_text = f"{p_text}\n" + "\n".join(measures)
                    list_processed = True
                except:
                    print("Не удалось найти список направлений")
            paragraph_texts.append(p_text)
        if paragraph_texts:
            result.append(("content", paragraph_texts))
            print(f"Параграфы: {paragraph_texts}")
    except Exception as e:
        print(f"Ошибка при парсинге параграфов: {str(e)}")

    return result, url

# Функция для сохранения данных в Markdown-файл
def save_to_markdown(data, url, filename="PDO_vakantnye-mesta-dlya-priema-perevoda.md"):
    content = []
    content_parts = {
        "title": None,
        "sub_title_h3": None,
        "sub_titles_h2": [],
        "content": []
    }

    # Собираем данные в словарь для упрощения обработки
    for item in data:
        if item[0] in content_parts:
            content_parts[item[0]] = item[1]

    # Формируем контент в логическом порядке
    if content_parts["title"]:
        content.append(f"# {content_parts['title']}")
        content.append(f"[Перейти к странице]({url})")

    if content_parts["sub_title_h3"]:
        content.append(f"## {content_parts['sub_title_h3']}")

    # Добавляем первый параграф (с списком) и следующий параграф
    if content_parts["content"] and len(content_parts["content"]) > 0:
        content.append(content_parts["content"][0])  # Параграф со списком
        if len(content_parts["content"]) > 1:
            content.append(content_parts["content"][1])  # Параграф после списка

    # Добавляем первый подзаголовок h2 и связанные параграфы
    if content_parts["sub_titles_h2"] and len(content_parts["sub_titles_h2"]) > 0:
        content.append(f"## {content_parts['sub_titles_h2'][0]}")
        # Добавляем параграфы 2, 3, 4 (индексы 2, 3, 4 в списке content)
        for i in range(2, 5):
            if i < len(content_parts["content"]):
                content.append(content_parts["content"][i])

    # Добавляем второй подзаголовок h2 и оставшиеся параграфы
    if content_parts["sub_titles_h2"] and len(content_parts["sub_titles_h2"]) > 1:
        content.append(f"## {content_parts['sub_titles_h2'][1]}")
        for i in range(5, len(content_parts["content"])):
            content.append(content_parts["content"][i])

    final_content = "\n\n".join(line for line in content if line.strip())
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(final_content)
    print(f"Контент записан в файл: {filename}")
    return filename

# Основной блок программы
if __name__ == "__main__":
    TARGET_URL = "https://academydpo.org/vakantnye-mesta-dlya-priema-perevoda"
    driver = get_driver()
    try:
        parsed_data, page_url = parse_page(driver, TARGET_URL)
        output_file = save_to_markdown(parsed_data, page_url)
        print(f"Файл {output_file} успешно сохранен!")
    except Exception as e:
        print(f"Ошибка при парсинге: {str(e)}")
    finally:
        driver.quit()