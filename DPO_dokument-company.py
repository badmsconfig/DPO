from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pathlib import Path

# Словарь селекторов
SELECTORS = {
    "main_title": (By.CSS_SELECTOR, "h1.page__content-title"),
    "document_list": (By.CSS_SELECTOR, "div.page__content-desc > ol > li > a")
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

    # Извлечение списка документов
    try:
        document_links = WebDriverWait(driver, 15).until(
            EC.presence_of_all_elements_located(SELECTORS["document_list"])
        )
        documents = []
        for link in document_links:
            doc_text = link.text.strip()
            doc_url = link.get_attribute("href")
            documents.append(f"[{doc_text}]({doc_url})")
        if documents:
            result.append(("content", documents))
            print(f"Документы: {documents}")
    except Exception as e:
        print(f"Ошибка при парсинге списка документов: {str(e)}")

    return result, url

# Функция для сохранения данных в Markdown-файл
def save_to_markdown(data, url, filename="DPO_documents.md"):
    content = []
    for item in data:
        if item[0] == "title":
            content.append(f"# {item[1]}")
            content.append(f"[Перейти к странице]({url})")
        elif item[0] == "content":
            content.append("\n## Список документов\n")
            content.extend([f"- {doc}" for doc in item[1]])

    final_content = "\n\n".join(line for line in content if line.strip())
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(final_content)
    print(f"Контент записан в файл: {filename}")
    return filename

# Основной блок программы
if __name__ == "__main__":
    TARGET_URL = "https://academydpo.org/dokument-company"
    driver = get_driver()
    try:
        parsed_data, page_url = parse_page(driver, TARGET_URL)
        output_file = save_to_markdown(parsed_data, page_url)
        print(f"Файл {output_file} успешно сохранен!")
    except Exception as e:
        print(f"Ошибка при парсинге: {str(e)}")
    finally:
        driver.quit()