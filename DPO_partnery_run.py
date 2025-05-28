from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pathlib import Path

# Словарь селекторов
SELECTORS = {
    "main_title": (By.CSS_SELECTOR, "h1.page__content-title"),
    "underline_text": (By.CSS_SELECTOR, "div.page__content-desc > u"),
    "partner_blocks": (By.CSS_SELECTOR, "div.partners__block"),
    "partner_images": (By.CSS_SELECTOR, "img.partners__block-img")
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

    # Извлечение подзаголовка (underline)
    try:
        underline_text = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located(SELECTORS["underline_text"])
        ).text.strip()
        result.append(("subtitle", underline_text))
        print(f"Подзаголовок: {underline_text}")
    except Exception as e:
        print(f"Ошибка при парсинге подзаголовка: {str(e)}")

    # Извлечение данных о партнёрах
    try:
        partner_blocks = WebDriverWait(driver, 15).until(
            EC.presence_of_all_elements_located(SELECTORS["partner_blocks"])
        )
        partner_data = []
        for block in partner_blocks:
            partner = {}
            # Проверяем, есть ли ссылка (тег <a>)
            try:
                link = block.find_element(By.XPATH, "./self::a | ./a")
                partner["href"] = link.get_attribute("href")
            except:
                partner["href"] = None
            # Извлекаем изображение
            try:
                img = block.find_element(*SELECTORS["partner_images"])
                partner["name"] = img.get_attribute("alt").strip()
                partner["img_src"] = img.get_attribute("src").strip()
            except Exception as e:
                print(f"Ошибка при парсинге изображения партнёра: {str(e)}")
                continue
            if partner.get("name"):
                partner_data.append(partner)
        if partner_data:
            result.append(("partners", partner_data))
            print(f"Партнёры: {partner_data}")
    except Exception as e:
        print(f"Ошибка при парсинге партнёров: {str(e)}")

    return result, url

# Функция для сохранения данных в Markdown-файл
def save_to_markdown(data, url, filename="DPO_partnery.md"):
    content = []
    for item in data:
        if item[0] == "title":
            content.append(f"# {item[1]}")
            content.append(f"[Перейти к странице]({url})")
        elif item[0] == "subtitle":
            content.append(f"## {item[1]}")
        elif item[0] == "partners":
            content.append("## Партнёры")
            for partner in item[1]:
                name = partner.get("name", "Неизвестный партнёр")
                href = partner.get("href")
                img_src = partner.get("img_src")
                if href:
                    content.append(f"- [{name}]({href})")
                else:
                    content.append(f"- {name}")
                if img_src:
                    content.append(f"  - Логотип: [Логотип]({img_src})")
                content.append("")  # Пустая строка для разделения партнёров

    final_content = "\n".join(line for line in content if line.strip())
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(final_content)
    print(f"Контент записан в файл: {filename}")
    return filename

# Основная функция запуска
def run():
    TARGET_URL = "https://academydpo.org/partnery"
    driver = get_driver()
    try:
        parsed_data, page_url = parse_page(driver, TARGET_URL)
        output_file = save_to_markdown(parsed_data, page_url)
        print(f"Файл {output_file} успешно сохранен!")
    except Exception as e:
        print(f"Ошибка при парсинге: {str(e)}")
    finally:
        driver.quit()

# Основной блок программы
if __name__ == "__main__":
    run()