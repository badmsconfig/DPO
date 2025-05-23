from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from pathlib import Path

# Словарь селекторов
SELECTORS = {
    "main_title": (By.CSS_SELECTOR, "h1"),
    "intro_paragraph": (By.CSS_SELECTOR, "h1 + p"),
    "advantages_block": (By.CSS_SELECTOR, "div.preim_block > div.item"),
    "partnership_conditions": {
        "title": (By.XPATH, "//h2[contains(text(), 'Сотрудничество на выгодных для вас условиях')]"),
        "content": (By.CSS_SELECTOR, "div.item")
    },
    "partnership_steps": {
        "title": (By.XPATH, "//h2[contains(text(), 'Станьте нашим партнером за 3 простых шага')]"),
        "content": (By.CSS_SELECTOR, "div.name, div.desc")
    }
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
def parse_section(driver, title_locator, content_locator, section_name):
    content = []
    try:
        title = WebDriverWait(driver, 40).until(
            EC.visibility_of_element_located(title_locator)
        ).text.strip()
        print(f"Найден заголовок секции '{section_name}': {title}")
    except Exception as e:
        print(f"Не удалось найти заголовок секции '{section_name}' {title_locator}: {str(e)}")
        return None

    try:
        # Проверяем наличие элементов
        elements = WebDriverWait(driver, 40).until(
            EC.presence_of_all_elements_located(content_locator)
        )
        print(f"Найдено {len(elements)} элементов в секции '{section_name}'")
        seen_texts = set()
        for element in elements:
            if element.get_attribute('class') == 'item':  # Для секции условий
                try:
                    name = element.find_element(By.CSS_SELECTOR, "div.name").text.strip()
                    span = element.find_element(By.CSS_SELECTOR, "span").text.strip()
                    paragraph = element.find_element(By.CSS_SELECTOR, "p").text.strip()
                    bold = element.find_element(By.CSS_SELECTOR, "b").text.strip()
                    price = element.find_element(By.CSS_SELECTOR, "div.price").text.strip()
                    item_text = f"{name}\n{span}\n{paragraph}\n{bold} {price}"
                    print(f"Обработан элемент item: {item_text}")
                    if item_text not in seen_texts:
                        content.append(item_text)
                        seen_texts.add(item_text)
                except Exception as e:
                    print(f"Ошибка при парсинге элемента item в секции '{section_name}': {str(e)}")
                    try:
                        print(f"HTML элемента: {element.get_attribute('outerHTML')[:200]}...")
                    except:
                        pass
            else:  # Для секции шагов (name или desc)
                try:
                    element_text = element.get_attribute('innerText').strip()
                    if element.get_attribute('class') == 'desc' and 'связаться с нами' in element_text:
                        try:
                            link = element.find_element(By.CSS_SELECTOR, "a")
                            link_text = link.text.strip()
                            link_href = link.get_attribute("href")
                            element_text = element_text.replace(link_text, f"[{link_text}]({link_href})")
                        except Exception as e:
                            print(f"Ошибка при обработке ссылки в секции '{section_name}': {str(e)}")
                    if element_text and element_text not in seen_texts:
                        content.append(element_text)
                        seen_texts.add(element_text)
                        print(f"Обработан элемент name/desc: {element_text}")
                except Exception as e:
                    print(f"Ошибка при парсинге элемента name/desc в секции '{section_name}': {str(e)}")
                    try:
                        print(f"HTML элемента: {element.get_attribute('outerHTML')[:200]}...")
                    except:
                        pass
        print(f"Найден контент для секции '{section_name}': {content}")
    except Exception as e:
        print(f"Не удалось найти контент для секции '{section_name}' {content_locator}: {str(e)}")
        # Проверяем наличие div.item и div.name/desc на странице
        try:
            items = driver.find_elements(By.CSS_SELECTOR, "div.item")
            names_descs = driver.find_elements(By.CSS_SELECTOR, "div.name, div.desc")
            print(f"Найдено div.item на странице: {len(items)}")
            print(f"Найдено div.name/desc на странице: {len(names_descs)}")
            if items:
                print(f"HTML первого div.item: {items[0].get_attribute('outerHTML')[:200]}...")
            if names_descs:
                print(f"HTML первого div.name/desc: {names_descs[0].get_attribute('outerHTML')[:200]}...")
        except:
            pass
        # Выводим HTML страницы
        try:
            body = driver.find_element(By.TAG_NAME, "body").get_attribute('outerHTML')[:500]
            print(f"HTML страницы (первые 500 символов): {body}...")
        except:
            pass

    return {"title": title, "content": content}

# Функция для парсинга страницы
def parse_page(driver, url):
    driver.get(url)
    # Явная задержка для загрузки JavaScript
    time.sleep(5)
    try:
        WebDriverWait(driver, 40).until(
            EC.visibility_of_element_located(SELECTORS["main_title"])
        )
    except Exception as e:
        print(f"Ошибка загрузки страницы: {str(e)}")
        return [], url

    result = []

    # Извлечение основного заголовка
    try:
        main_title = WebDriverWait(driver, 40).until(
            EC.visibility_of_element_located(SELECTORS["main_title"])
        ).text.strip()
        result.append(("title", main_title))
        print(f"Основной заголовок: {main_title}")
    except Exception as e:
        print(f"Ошибка при парсинге заголовка: {str(e)}")

    # Извлечение вводного параграфа
    try:
        intro_text = WebDriverWait(driver, 40).until(
            EC.visibility_of_element_located(SELECTORS["intro_paragraph"])
        ).text.strip()
        if intro_text:
            result.append(("content", [intro_text]))
            print(f"Вводный параграф: {intro_text}")
    except Exception as e:
        print(f"Ошибка при парсинге вводного параграфа: {str(e)}")

    # Извлечение блока преимуществ
    try:
        advantages = WebDriverWait(driver, 40).until(
            EC.visibility_of_all_elements_located(SELECTORS["advantages_block"])
        )
        advantages_texts = []
        for item in advantages:
            name = item.find_element(By.CSS_SELECTOR, "div.name").text.strip().rstrip(',')
            desc = item.find_element(By.CSS_SELECTOR, "div.desc").text.strip()
            advantages_texts.append(f"{name}: {desc}")
        if advantages_texts:
            result.append(("section", {"title": "Преимущества сотрудничества", "content": advantages_texts}))
            print(f"Блок преимуществ: {advantages_texts}")
    except Exception as e:
        print(f"Ошибка при парсинге блока преимуществ: {str(e)}")

    # Парсинг секции условий сотрудничества
    conditions = parse_section(driver, SELECTORS["partnership_conditions"]["title"],
                            SELECTORS["partnership_conditions"]["content"],
                            "Сотрудничество на выгодных для вас условиях")
    if conditions:
        result.append(("section", conditions))

    # Парсинг секции шагов сотрудничества
    steps = parse_section(driver, SELECTORS["partnership_steps"]["title"],
                        SELECTORS["partnership_steps"]["content"],
                        "Станьте нашим партнером за 3 простых шага")
    if steps:
        result.append(("section", steps))

    return result, url

# Функция для сохранения данных в Markdown-файл
def save_to_markdown(data, url, filename="DPO_sotrudnichestvo.md"):
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
    TARGET_URL = "https://academydpo.org/sotrudnichestvo"
    driver = get_driver()
    try:
        parsed_data, page_url = parse_page(driver, TARGET_URL)
        output_file = save_to_markdown(parsed_data, page_url)
        print(f"Файл {output_file} успешно сохранен!")
    except Exception as e:
        print(f"Ошибка при парсинге: {str(e)}")
    finally:
        driver.quit()