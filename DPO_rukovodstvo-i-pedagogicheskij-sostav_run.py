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
    "underline_text": (By.CSS_SELECTOR, "div.page__content-desc > u")
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
        print(f"Основ ſной заголовок: {main_title}")
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

    # Извлечение параграфов
    try:
        paragraphs = WebDriverWait(driver, 15).until(
            EC.presence_of_all_elements_located(SELECTORS["paragraphs"])
        )
        paragraph_texts = []
        current_person = None
        for p in paragraphs:
            p_text = p.text.strip()
            if p_text:
                # Проверяем, является ли параграф началом описания новой персоны
                if p_text.startswith("Генеральный директор:") or p_text.startswith("Заведующий учебной частью"):
                    if current_person:
                        paragraph_texts.append(current_person)
                    current_person = {"title": p_text}
                elif current_person:
                    # Добав,weляем информацию к текущей персоне
                    if "Уровень образования:" in p_text:
                        current_person["education"] = p_text
                    elif "Общий стаж работы:" in p_text:
                        current_person["total_experience"] = p_text
                    elif "Стаж работы в должности:" in p_text:
                        current_person["position_experience"] = p_text
                    elif "Окончил:" in p_text or "Окончил (а):" in p_text:
                        current_person["graduated"] = p_text
                    elif "Дополнительное профессиональное образование:" in p_text:
                        current_person["additional_education"] = p_text
                    elif "Контактный телефон:" in p_text:
                        current_person["phone"] = p_text
                    elif "Электронная почта:" in p_text:
                        current_person["email"] = p_text
        # Добавляем последнюю персону, если она есть
        if current_person:
            paragraph_texts.append(current_person)
        if paragraph_texts:
            result.append(("content", paragraph_texts))
            print(f"Параграфы: {paragraph_texts}")
    except Exception as e:
        print(f"Ошибка при парсинге параграфов: {str(e)}")

    return result, url

# Функция для сохранения данных в Markdown-файл
def save_to_markdown(data, url, filename="DPO_rukovodstvo-i-pedagogicheskij-sostav.md"):
    content = []
    for item in data:
        if item[0] == "title":
            content.append(f"# {item[1]}")
            content.append(f"[Перейти к странице]({url})")
        elif item[0] == "subtitle":
            content.append(f"## {item[1]}")
        elif item[0] == "content":
            for person in item[1]:
                if isinstance(person, dict):
                    content.append(f"## {person.get('title', '')}")
                    if "education" in person:
                        content.append(f"- {person['education']}")
                    if "total_experience" in person:
                        content.append(f"- {person['total_experience']}")
                    if "position_experience" in person:
                        content.append(f"- {person['position_experience']}")
                    if "graduated" in person:
                        content.append(f"- {person['graduated']}")
                    if "additional_education" in person:
                        content.append(f"- {person['additional_education']}")
                    if "phone" in person:
                        content.append(f"- {person['phone']}")
                    if "email" in person:
                        content.append(f"- {person['email']}")
                    content.append("")  # Пустая строка для разделения персон

    final_content = "\n".join(line for line in content if line.strip())
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(final_content)
    print(f"Контент записан в файл: {filename}")
    return filename

# Основная функция запуска
def run():
    TARGET_URL = "https://academydpo.org/rukovodstvo-i-pedagogicheskij-sostav"
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