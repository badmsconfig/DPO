from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pathlib import Path

# Словарь селекторов
SELECTORS = {
    "main_title": (By.CSS_SELECTOR, "h1.page__content-title"),
    "intro_paragraphs": (By.CSS_SELECTOR, "div.page__content-desc > p"),
    "education_table": (By.CSS_SELECTOR, "div.page__content-desc > div.table:nth-of-type(1) > table > tbody > tr"),
    "post_table_paragraphs": (By.XPATH, "//div[contains(@class, 'page__content-desc')]/p[position() > 2 and position() <= 5]"),
    "research_title": (By.XPATH, "//div[contains(@class, 'page__content-desc')]/p[contains(., 'НАУЧНО-ИССЛЕДОВАТЕЛЬСКАЯ ДЕЯТЕЛЬНОСТЬ')]"),
    "research_table": (By.CSS_SELECTOR, "div.page__content-desc > div.table:nth-of-type(2) > table > tbody > tr"),
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

# Функция для парсинга таблицы
def parse_table(driver, table_locator, is_education_table=True):
    try:
        rows = WebDriverWait(driver, 15).until(
            EC.presence_of_all_elements_located(table_locator)
        )
        table_data = []
        for row in rows:
            cells = row.find_elements(By.CSS_SELECTOR, "td")
            row_data = []
            for i, cell in enumerate(cells):
                if is_education_table and i == 4:  # Колонка с ссылкой
                    try:
                        link = cell.find_element(By.CSS_SELECTOR, "p > a")
                        link_text = link.text.strip()
                        link_href = link.get_attribute("href")
                        row_data.append(f"{link_text} ({link_href})")
                    except:
                        row_data.append(cell.find_element(By.CSS_SELECTOR, "p").text.strip())
                else:
                    row_data.append(cell.find_element(By.CSS_SELECTOR, "p").text.strip())
            table_data.append(" | ".join(row_data))
        return table_data
    except Exception as e:
        print(f"Ошибка при парсинге таблицы: {str(e)}")
        return []

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

    # Извлечение вводных параграфов
    try:
        intro_paragraphs = WebDriverWait(driver, 15).until(
            EC.presence_of_all_elements_located(SELECTORS["intro_paragraphs"])
        )
        intro_texts = [p.text.strip() for p in intro_paragraphs[:2] if p.text.strip()]
        if intro_texts:
            result.append(("content", intro_texts))
            print(f"Вводные параграфы: {intro_texts}")
    except Exception as e:
        print(f"Ошибка при парсинге вводных параграфов: {str(e)}")

    # Извлечение таблицы образовательных программ
    try:
        education_table = parse_table(driver, SELECTORS["education_table"], is_education_table=True)
        if education_table:
            result.append(("table", {"title": "Образовательные программы", "content": education_table}))
            print(f"Таблица образовательных программ: {education_table}")
    except Exception as e:
        print(f"Ошибка при парсинге таблицы образовательных программ: {str(e)}")

    # Извлечение параграфов после таблицы
    try:
        post_table_paragraphs = WebDriverWait(driver, 15).until(
            EC.presence_of_all_elements_located(SELECTORS["post_table_paragraphs"])
        )
        post_table_texts = []
        for p in post_table_paragraphs:
            p_text = p.text.strip()
            if "Положение" in p_text:
                try:
                    link = p.find_element(By.CSS_SELECTOR, "a")
                    link_text = link.text.strip()
                    link_href = link.get_attribute("href")
                    p_text = p_text.replace(link_text, f"{link_text} ({link_href})")
                except:
                    pass
            post_table_texts.append(p_text)
        if post_table_texts:
            result.append(("content", post_table_texts))
            print(f"Параграфы после таблицы: {post_table_texts}")
    except Exception as e:
        print(f"Ошибка при парсинге параграфов после таблицы: {str(e)}")

    # Извлечение заголовка научной деятельности
    try:
        research_title = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located(SELECTORS["research_title"])
        ).text.strip()
        result.append(("section_title", research_title))
        print(f"Заголовок научной деятельности: {research_title}")
    except Exception as e:
        print(f"Ошибка при парсинге заголовка научной деятельности: {str(e)}")

    # Извлечение таблицы научной деятельности
    try:
        research_table = parse_table(driver, SELECTORS["research_table"], is_education_table=False)
        if research_table:
            result.append(("table", {"title": "Научно-исследовательская деятельность", "content": research_table}))
            print(f"Таблица научной деятельности: {research_table}")
    except Exception as e:
        print(f"Ошибка при парсинге таблицы научной деятельности: {str(e)}")

    return result, url

# Функция для сохранения данных в Markdown-файл
def save_to_markdown(data, url, filename="DPO_obrazovanie.md"):
    content = []
    for item in data:
        if item[0] == "title":
            content.append(f"# {item[1]}")
            content.append(f"[Перейти к странице]({url})")
        elif item[0] == "content":
            content.extend(item[1])
        elif item[0] == "section_title":
            content.append(f"## {item[1]}")
        elif item[0] == "table":
            content.append(f"## {item[1]['title']}")
            content.extend(item[1]["content"])

    final_content = "\n\n".join(line for line in content if line.strip())
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(final_content)
    print(f"Контент записан в файл: {filename}")
    return filename

# Основной блок программы
if __name__ == "__main__":
    TARGET_URL = "https://academydpo.org/obrazovanie"
    driver = get_driver()
    try:
        parsed_data, page_url = parse_page(driver, TARGET_URL)
        output_file = save_to_markdown(parsed_data, page_url)
        print(f"Файл {output_file} успешно сохранен!")
    except Exception as e:
        print(f"Ошибка при парсинге: {str(e)}")
    finally:
        driver.quit()