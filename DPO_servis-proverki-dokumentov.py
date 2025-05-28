from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pathlib import Path

# Словарь селекторов для страницы https://academydpo.org/servis-proverki-dokumentov
SELECTORS = {
    "main_title": (By.CSS_SELECTOR, "h1.valid_doc__title"),
    "desc_paragraphs": (By.CSS_SELECTOR, "div.valid_doc__desc > p:not(.wp-block-heading ~ p)"),
    "sub_title": (By.CSS_SELECTOR, "h1.wp-block-heading"),
    "registry_paragraphs": (By.CSS_SELECTOR, "div.valid_doc__desc > h1.wp-block-heading ~ p"),
    "list_items": (By.CSS_SELECTOR, "div.valid_doc__desc > ul > li")
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

    # Извлечение параграфов описания (до подзаголовка)
    try:
        desc_paragraphs = WebDriverWait(driver, 15).until(
            EC.presence_of_all_elements_located(SELECTORS["desc_paragraphs"])
        )
        desc_texts = [p.text.strip() for p in desc_paragraphs if p.text.strip()]
        if desc_texts:
            result.append(("desc_content", desc_texts))
            print(f"Параграфы описания: {desc_texts}")
    except Exception as e:
        print(f"Ошибка при парсинге параграфов описания: {str(e)}")

    # Извлечение подзаголовка
    try:
        sub_title = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located(SELECTORS["sub_title"])
        ).text.strip()
        result.append(("sub_title", sub_title))
        print(f"Подзаголовок: {sub_title}")
    except Exception as e:
        print(f"Ошибка при парсинге подзаголовка: {str(e)}")

    # Извлечение параграфов реестра (после подзаголовка) и списка целей
    try:
        registry_paragraphs = WebDriverWait(driver, 15).until(
            EC.presence_of_all_elements_located(SELECTORS["registry_paragraphs"])
        )
        registry_texts = []
        for i, p in enumerate(registry_paragraphs):
            p_text = p.text.strip()
            # Обработка параграфа с целями реестра
            if "Целями создания Федерального реестра являются" in p_text:
                try:
                    ul = p.find_element(By.XPATH, "./following-sibling::ul")
                    li_elements = ul.find_elements(By.CSS_SELECTOR, "li")
                    measures = [li.text.strip() for li in li_elements if li.text.strip()]
                    p_text = f"{p_text}\n" + "\n".join(f"- {m}" for m in measures)
                except:
                    print("Не удалось найти список целей реестра")
            registry_texts.append(p_text)
        if registry_texts:
            result.append(("registry_content", registry_texts))
            print(f"Параграфы реестра: {registry_texts}")
    except Exception as e:
        print(f"Ошибка при парсинге параграфов реестра: {str(e)}")

    return result, url

# Функция для сохранения данных в Markdown-файл
def save_to_markdown(data, url, filename="PDO_servis-proverki-dokumentov.md"):
    content = []
    for item in data:
        if item[0] == "title":
            content.append(f"# {item[1]}")
            content.append(f"[Перейти к странице]({url})")
        elif item[0] == "desc_content":
            content.extend(item[1])
        elif item[0] == "sub_title":
            content.append(f"## {item[1]}")
        elif item[0] == "registry_content":
            content.extend(item[1])

    final_content = "\n\n".join(line for line in content if line.strip())
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(final_content)
    print(f"Контент записан в файл: {filename}")
    return filename

# Основной блок программы
if __name__ == "__main__":
    TARGET_URL = "https://academydpo.org/servis-proverki-dokumentov"
    driver = get_driver()
    try:
        parsed_data, page_url = parse_page(driver, TARGET_URL)
        output_file = save_to_markdown(parsed_data, page_url)
        print(f"Файл {output_file} успешно сохранен!")
    except Exception as e:
        print(f"Ошибка при парсинге: {str(e)}")
    finally:
        driver.quit()