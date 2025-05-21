# Импорт необходимых библиотек для работы с Selenium, управления ChromeDriver и работы с файлами
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
from pathlib import Path

# 🔧 Функция настройки веб-драйвера для работы в headless-режиме
def get_driver():
    # Создание объекта опций для браузера Chrome
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Запуск браузера без графического интерфейса
    chrome_options.add_argument("--disable-gpu")  # Отключение GPU для повышения стабильности
    chrome_options.add_argument("--no-sandbox")  # Отключение песочницы для совместимости
    chrome_options.add_argument("--window-size=1920,1080")  # Установка размера окна браузера
    # Автоматическая установка ChromeDriver с помощью webdriver-manager
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    return driver

# 📄 Словарь селекторов для извлечения данных со страницы
elements_to_parse = {
    # Селекторы для заголовков страницы
    "page_title": [
        {"type": "css", "value": "section.desc_page h2.desc_page-title"},
    ],
    # Селекторы для основного текста страницы
    "page_text": [
        {"type": "css", "value": "section.desc_page div.desc_page-text p"},
    ],
    # Селекторы для заголовков информационных блоков
    "info_block_title": [
        {"type": "css", "value": "h2.info_block__images-title span"},
    ],
    # Селекторы для текста информационных блоков
    "info_block_text": [
        {"type": "css", "value": "div.info_block-desc p"},
    ],
    # Селекторы для ссылок
    "info_links": [
        {"type": "css", "value": "a.info_block__list-link"},
    ],
    # Селекторы для секции описания на главной странице
    "home_desc_section": [
        {"type": "css", "value": "section.home_desc > *"},
    ],
    # Селектор для списка особенностей обучения
    "education_features": {
        "trigger_text": "Такое обучение имеет свои особенности:",
        "selector": {"type": "xpath", "value": "//p[contains(text(), 'Такое обучение имеет свои особенности:')]/following-sibling::ul[1]/li"},
    },
    # Селектор для списка форм обучения
    "learning_forms": {
        "trigger_text": "В нашей академии дистанционное обучение проводится в разных формах:",
        "selector": {"type": "xpath", "value": "//h3[contains(text(), 'В нашей академии дистанционное обучение проводится в разных формах:')]/following-sibling::ul[1]/li"},
    },
    # Селектор для списка медицинского образования
    "medical_education": {
        "trigger_text": "Дистанционное обучение для руководящего состава здравоохранительных организаций",
        "selector": {"type": "xpath", "value": "//p[contains(., 'Дистанционное обучение для руководящего состава')]/following-sibling::ul[1]/li/a"},
    },
    # Селектор для списка строительных курсов
    "construction_courses": {
        "trigger_text": "Курсы на базе средне-специального или высшего образования",
        "selector": {"type": "xpath", "value": "//p[contains(., 'Курсы на базе средне-специального или высшего образования')]/following-sibling::ul[1]/li/a"},
    },
    # Селектор для списка специальных курсов
    "special_courses": {
        "trigger_text": "Курсы специальной переподготовки на базе среднего и/или высшего образования",
        "selector": {"type": "xpath", "value": "//p[contains(., 'Курсы специальной переподготовки на базе среднего и/или высшего образования')]/following-sibling::ul[1]/li/a"},
    },
}

# 🧠 Функция парсинга одной веб-страницы
def parse_website(url, driver):
    # Создание словаря для хранения результатов парсинга
    results = {
        "url": url,
        "sections": [],  # Список для заголовков и текстов
        "links": [],  # Список для ссылок
        "education_features": [],  # Список особенностей обучения
        "learning_forms": [],  # Список форм обучения
        "medical_education": [],  # Список медицинского образования
        "construction_courses": [],  # Список строительных курсов
        "special_courses": [],  # Список специальных курсов
    }

    # Загрузка страницы
    driver.get(url)
    time.sleep(2)  # Ожидание загрузки страницы (2 секунды)

    # Парсинг заголовков страницы
    title_texts = []
    for selector in elements_to_parse["page_title"]:
        try:
            if selector["type"] == "css":
                elements = driver.find_elements(By.CSS_SELECTOR, selector["value"])
            elif selector["type"] == "xpath":
                elements = driver.find_elements(By.XPATH, selector["value"])
            # Сбор текста из элементов, отфильтрованных по наличию текста
            title_texts.extend([el.text.strip() for el in elements if el.text.strip()])
        except Exception as e:
            print(f"Ошибка при парсинге заголовков страницы: {str(e)}")
            continue

    # Парсинг основного текста страницы
    body_texts = []
    for selector in elements_to_parse["page_text"]:
        try:
            if selector["type"] == "css":
                elements = driver.find_elements(By.CSS_SELECTOR, selector["value"])
            elif selector["type"] == "xpath":
                elements = driver.find_elements(By.XPATH, selector["value"])
            # Сбор текста из элементов, отфильтрованных по наличию текста
            body_texts.extend([el.text.strip() for el in elements if el.text.strip()])
        except Exception as e:
            print(f"Ошибка при парсинге текста страницы: {str(e)}")
            continue

    # Объединение заголовков и текстов в секции
    if len(title_texts) == 1 and len(body_texts) > 1:
        for i, text in enumerate(body_texts):
            results["sections"].append({
                "title": title_texts[0] if i == 0 else "",  # Первый текст получает заголовок
                "text": text
            })
    else:
        for i in range(max(len(title_texts), len(body_texts))):
            title = title_texts[i] if i < len(title_texts) else ""
            text = body_texts[i] if i < len(body_texts) else ""
            results["sections"].append({"title": title, "text": text})

    # Парсинг заголовков информационных блоков
    info_titles = []
    for selector in elements_to_parse["info_block_title"]:
        try:
            if selector["type"] == "css":
                elements = driver.find_elements(By.CSS_SELECTOR, selector["value"])
            elif selector["type"] == "xpath":
                elements = driver.find_elements(By.XPATH, selector["value"])
            info_titles.extend([el.text.strip() for el in elements if el.text.strip()])
        except Exception as e:
            print(f"Ошибка при парсинге заголовков инфоблоков: {str(e)}")
            continue

    # Парсинг текстов информационных блоков
    info_texts = []
    for selector in elements_to_parse["info_block_text"]:
        try:
            if selector["type"] == "css":
                elements = driver.find_elements(By.CSS_SELECTOR, selector["value"])
            elif selector["type"] == "xpath":
                elements = driver.find_elements(By.XPATH, selector["value"])
            info_texts.extend([el.text.strip() for el in elements if el.text.strip()])
        except Exception as e:
            print(f"Ошибка при парсинге текстов инфоблоков: {str(e)}")
            continue

    # Объединение заголовков и текстов инфоблоков в секции
    if len(info_titles) == 1 and len(info_texts) > 0:
        for i, text in enumerate(info_texts):
            results["sections"].append({
                "title": info_titles[0] if i == 0 else "",  # Первый текст получает заголовок
                "text": text
            })
    else:
        for i in range(max(len(info_titles), len(info_texts))):
            title = info_titles[i] if i < len(info_titles) else ""
            text = info_texts[i] if i < len(info_texts) else ""
            results["sections"].append({"title": title, "text": text})

    # Парсинг ссылок
    for selector in elements_to_parse["info_links"]:
        try:
            if selector["type"] == "css":
                elements = driver.find_elements(By.CSS_SELECTOR, selector["value"])
            elif selector["type"] == "xpath":
                elements = driver.find_elements(By.XPATH, selector["value"])
            # Сбор текста и URL для каждой ссылки
            for el in elements:
                if el.text.strip():
                    results["links"].append({
                        "text": el.text.strip(),
                        "url": el.get_attribute("href")
                    })
        except Exception as e:
            print(f"Ошибка при парсинге ссылок: {str(e)}")
            continue

    # Парсинг секции home_desc
    for selector in elements_to_parse["home_desc_section"]:
        try:
            if selector["type"] == "css":
                elements = driver.find_elements(By.CSS_SELECTOR, selector["value"])
            # Обработка элементов в зависимости от их тега
            for el in elements:
                tag_name = el.tag_name.lower()
                text = el.text.strip()
                if not text:
                    continue
                if tag_name in ['h2', 'h3']:
                    results["sections"].append({"title": text, "text": ""})
                elif tag_name in ['p', 'li']:
                    if results["sections"] and not results["sections"][-1]["text"]:
                        results["sections"][-1]["text"] = text
                    else:
                        results["sections"].append({"title": "", "text": text})
        except Exception as e:
            print(f"Ошибка при парсинге home_desc: {str(e)}")
            continue

    # Парсинг списка особенностей обучения
    try:
        if elements_to_parse["education_features"]["selector"]["type"] == "xpath":
            elements = driver.find_elements(By.XPATH, elements_to_parse["education_features"]["selector"]["value"])
        for el in elements:
            text = el.text.strip()
            if text:
                results["education_features"].append(text)
    except Exception as e:
        print(f"Ошибка при парсинге особенностей обучения: {str(e)}")

    # Парсинг списка форм обучения
    try:
        if elements_to_parse["learning_forms"]["selector"]["type"] == "xpath":
            elements = driver.find_elements(By.XPATH, elements_to_parse["learning_forms"]["selector"]["value"])
        for el in elements:
            text = el.text.strip()
            if text:
                results["learning_forms"].append(text)
    except Exception as e:
        print(f"Ошибка при парсинге форм обучения: {str(e)}")

    # Парсинг списка медицинского образования
    try:
        if elements_to_parse["medical_education"]["selector"]["type"] == "xpath":
            elements = driver.find_elements(By.XPATH, elements_to_parse["medical_education"]["selector"]["value"])
        for el in elements:
            text = el.text.strip()
            url = el.get_attribute("href")
            if text:
                results["medical_education"].append({"text": text, "url": url})
    except Exception as e:
        print(f"Ошибка при парсинге медицинского образования: {str(e)}")

    # Парсинг списка строительных курсов
    try:
        if elements_to_parse["construction_courses"]["selector"]["type"] == "xpath":
            elements = driver.find_elements(By.XPATH, elements_to_parse["construction_courses"]["selector"]["value"])
        for el in elements:
            text = el.text.strip()
            url = el.get_attribute("href")
            if text:
                results["construction_courses"].append({"text": text, "url": url})
    except Exception as e:
        print(f"Ошибка при парсинге строительных курсов: {str(e)}")

    # Парсинг списка специальных курсов
    try:
        if elements_to_parse["special_courses"]["selector"]["type"] == "xpath":
            elements = driver.find_elements(By.XPATH, elements_to_parse["special_courses"]["selector"]["value"])
        for el in elements:
            text = el.text.strip()
            url = el.get_attribute("href")
            if text:
                results["special_courses"].append({"text": text, "url": url})
    except Exception as e:
        print(f"Ошибка при парсинге специальных курсов: {str(e)}")

    return results

# 💾 Функция сохранения результатов в Markdown-файл
def save_results_to_file(results, filename="DPO_glavnaya_results.md"):
    # Создание пути для сохранения файла в текущей директории
    save_path = Path.cwd() / filename

    with open(save_path, "w", encoding="utf-8") as f:
        for res in results:
            # Запись разделителя и URL страницы
            f.write(f"# Страница: {res['url']}\n\n")
            f.write(f"[Открыть страницу]({res['url']})\n\n")
            f.write(f"{'='*80}\n\n")

            # Запись секций с заголовками и текстами
            for section in res["sections"]:
                if section["title"]:
                    f.write(f"## {section['title']}\n\n")
                if section["text"]:
                    f.write(f"{section['text']}\n\n")

            # Запись ссылок
            if res["links"]:
                f.write("## Ссылки\n\n")
                for link in res["links"]:
                    f.write(f"- [{link['text']}]({link['url']})\n")
                f.write("\n")

            # Запись особенностей обучения
            if res["education_features"]:
                f.write("## Особенности обучения\n\n")
                for item in res["education_features"]:
                    f.write(f"- {item}\n")
                f.write("\n")

            # Запись форм обучения
            if res["learning_forms"]:
                f.write("## Формы обучения\n\n")
                for item in res["learning_forms"]:
                    f.write(f"- {item}\n")
                f.write("\n")

            # Запись медицинского образования
            if res["medical_education"]:
                f.write("## Медицинское образование\n\n")
                for item in res["medical_education"]:
                    f.write(f"- [{item['text']}]({item['url']})\n")
                f.write("\n")

            # Запись строительных курсов
            if res["construction_courses"]:
                f.write("## Строительные курсы\n\n")
                for item in res["construction_courses"]:
                    f.write(f"- [{item['text']}]({item['url']})\n")
                f.write("\n")

            # Запись специальных курсов
            if res["special_courses"]:
                f.write("## Специальные курсы\n\n")
                for item in res["special_courses"]:
                    f.write(f"- [{item['text']}]({item['url']})\n")
                f.write("\n")

    print(f"\n✅ Результаты сохранены в файл: {save_path}")
    return save_path

# 🔗 Список URL-адресов для парсинга
urls = [
    "https://academydpo.org/",
]

# 🚀 Основной блок выполнения программы
if __name__ == "__main__":
    # Инициализация веб-драйвера
    driver = get_driver()
    all_results = []

    # Цикл по всем URL для парсинга
    for url in urls:
        print(f"🔍 Парсинг: {url}")
        # Парсинг страницы и сохранение результатов
        data = parse_website(url, driver)
        all_results.append(data)

    # Закрытие веб-драйвера
    driver.quit()

    # Сохранение результатов в Markdown-файл
    save_results_to_file(all_results)