from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pathlib import Path

# Словарь селекторов
SELECTORS = {
    "main_title": (By.CSS_SELECTOR, "h1.page__content-title"),
    "structure_table": (By.CSS_SELECTOR, "div.page__content-desc > div.table > table > tbody > tr")
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
def parse_table(driver, table_locator):
    try:
        rows = WebDriverWait(driver, 15).until(
            EC.presence_of_all_elements_located(table_locator)
        )
        table_data = []
        for row in rows:
            cells = row.find_elements(By.CSS_SELECTOR, "td")
            row_data = []
            for cell in cells:
                paragraphs = cell.find_elements(By.CSS_SELECTOR, "p")
                cell_text = "\n".join(p.text.strip() for p in paragraphs if p.text.strip())
                row_data.append(cell_text if cell_text else "—")
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

    # Извлечение таблицы структуры и органов управления
    try:
        structure_table = parse_table(driver, SELECTORS["structure_table"])
        if structure_table:
            result.append(("table", {"title": "Структура и органы управления", "content": structure_table}))
            print(f"Таблица структуры и органов управления: {structure_table}")
    except Exception as e:
        print(f"Ошибка при парсинге таблицы: {str(e)}")

    return result, url

# Функция для сохранения данных в Markdown-файл
def save_to_markdown(data, url, filename="DPO_struktura-i-organy-upravleniya.md"):
    content = []
    for item in data:
        if item[0] == "title":
            content.append(f"# {item[1]}")
            content.append(f"[Перейти к странице]({url})")
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
    TARGET_URL = "https://academydpo.org/struktura-i-organy-upravleniya"
    driver = get_driver()
    try:
        parsed_data, page_url = parse_page(driver, TARGET_URL)
        output_file = save_to_markdown(parsed_data, page_url)
        print(f"Файл {output_file} успешно сохранен!")
    except Exception as e:
        print(f"Ошибка при парсинге: {str(e)}")
    finally:
        driver.quit()