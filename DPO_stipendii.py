from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pathlib import Path

# Словарь селекторов
SELECTORS = {
    "main_title": (By.CSS_SELECTOR, "h1.page__content-title"),
    "paragraphs": (By.CSS_SELECTOR, "div.page__content-desc > p"),
    "support_measures": (By.CSS_SELECTOR, "div.page__content-desc > ul > li")
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

    # Извлечение параграфов
    try:
        paragraphs = WebDriverWait(driver, 15).until(
            EC.presence_of_all_elements_located(SELECTORS["paragraphs"])
        )
        paragraph_texts = []
        for p in paragraphs:
            p_text = p.text.strip()
            # Обработка параграфа с мерами поддержки
            if "Меры социальной поддержки" in p_text:
                try:
                    ul = p.find_element(By.XPATH, "./following-sibling::ul")
                    li_elements = ul.find_elements(By.CSS_SELECTOR, "li")
                    measures = [li.text.strip() for li in li_elements if li.text.strip()]
                    p_text = f"{p_text}\n" + "\n".join(f"- {m}" for m in measures)
                except:
                    print("Не удалось найти список мер поддержки")
            paragraph_texts.append(p_text)
        if paragraph_texts:
            result.append(("content", paragraph_texts))
            print(f"Параграфы: {paragraph_texts}")
    except Exception as e:
        print(f"Ошибка при парсинге параграфов: {str(e)}")

    return result, url

# Функция для сохранения данных в Markdown-файл
def save_to_markdown(data, url, filename="DPO_stipendii.md"):
    content = []
    for item in data:
        if item[0] == "title":
            content.append(f"# {item[1]}")
            content.append(f"[Перейти к странице]({url})")
        elif item[0] == "content":
            content.extend(item[1])

    final_content = "\n\n".join(line for line in content if line.strip())
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(final_content)
    print(f"Контент записан в файл: {filename}")
    return filename

# Основной блок программы
if __name__ == "__main__":
    TARGET_URL = "https://academydpo.org/stipendii"
    driver = get_driver()
    try:
        parsed_data, page_url = parse_page(driver, TARGET_URL)
        output_file = save_to_markdown(parsed_data, page_url)
        print(f"Файл {output_file} успешно сохранен!")
    except Exception as e:
        print(f"Ошибка при парсинге: {str(e)}")
    finally:
        driver.quit()
