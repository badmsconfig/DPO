from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pathlib import Path

# Словарь селекторов для страницы https://academydpo.org/dostupnaya-sreda-v-ooo-akademiya-dpo
SELECTORS = {
    "main_title": (By.CSS_SELECTOR, "h1.page__content-title"),
    "table_rows": (By.CSS_SELECTOR, "div.page__content-desc > div.table > table > tbody > tr")
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

    # Извлечение данных таблицы
    try:
        table_rows = WebDriverWait(driver, 15).until(
            EC.presence_of_all_elements_located(SELECTORS["table_rows"])
        )
        table_data = []
        for row in table_rows[1:]:  # Пропускаем заголовок таблицы
            cells = row.find_elements(By.CSS_SELECTOR, "td")
            if len(cells) == 2:
                condition = cells[0].text.strip()
                availability = cells[1].text.strip()
                # Разделение текста в ячейке на строки для пунктов (например, для "Специальные условия охраны здоровья")
                availability_lines = availability.split('\n')
                if len(availability_lines) > 1:
                    availability = '\n' + '\n'.join(f"- {line.strip()}" for line in availability_lines if line.strip())
                table_data.append((condition, availability))
        if table_data:
            result.append(("table", table_data))
            print(f"Данные таблицы: {table_data}")
    except Exception as e:
        print(f"Ошибка при парсинге таблицы: {str(e)}")

    return result, url

# Функция для сохранения данных в Markdown-файл
def save_to_markdown(data, url, filename="DPO_accessible_environment.md"):
    content = []

    # Формируем контент в логическом порядке
    for item in data:
        if item[0] == "title":
            content.append(f"# {item[1]}")
            content.append(f"[Перейти к странице]({url})")
        elif item[0] == "table":
            content.append("## Условия доступной среды")
            # Создаем таблицу в Markdown
            content.append("| Условия доступной среды | Наличие |")
            content.append("|------------------------|---------|")
            for condition, availability in item[1]:
                # Экранируем символы | в тексте, если они есть
                condition = condition.replace("|", "\\|")
                availability = availability.replace("|", "\\|")
                content.append(f"| {condition} | {availability} |")

    final_content = "\n\n".join(line for line in content if line.strip())
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(final_content)
    print(f"Контент записан в файл: {filename}")
    return filename

# Основной блок программы
if __name__ == "__main__":
    TARGET_URL = "https://academydpo.org/dostupnaya-sreda-v-ooo-akademiya-dpo"
    driver = get_driver()
    try:
        parsed_data, page_url = parse_page(driver, TARGET_URL)
        output_file = save_to_markdown(parsed_data, page_url)
        print(f"Файл {output_file} успешно сохранен!")
    except Exception as e:
        print(f"Ошибка при парсинге: {str(e)}")
    finally:
        driver.quit()