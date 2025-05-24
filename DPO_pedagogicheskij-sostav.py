import requests
import pdfplumber
import re
import os
from urllib.parse import urljoin
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options


def is_text_valid(text):
    """Проверяет текст на наличие бессмысленных символов или 'белиберды'."""
    garbage_pattern = r'[^a-zA-Zа-яА-Я0-9\s.,;:!?-]'
    garbage_count = len(re.findall(garbage_pattern, text))
    total_length = len(text)

    if total_length == 0 or (garbage_count / total_length > 0.3):
        return False

    word_pattern = r'[а-яА-Я]{3,}'
    words = re.findall(word_pattern, text)
    return len(words) > 2


def clean_text(text):
    """Очищает текст от лишних пробелов и переносов строк."""
    text = re.sub(r'\s+', ' ', text.strip())
    return text


def parse_page(url):
    """Парсит страницу с помощью Selenium и извлекает заголовок и ссылку на PDF."""
    try:
        # Настройка Selenium
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Запуск в фоновом режиме
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--enable-unsafe-swiftshader")  # Добавляем флаг для подавления предупреждений WebGL

        # Укажите путь к chromedriver.exe, если он не в PATH
        # service = Service('D:/path/to/chromedriver.exe')
        service = Service()  # Если chromedriver в PATH
        driver = webdriver.Chrome(service=service, options=chrome_options)

        # Загружаем страницу
        driver.get(url)

        # Извлекаем заголовок
        title_element = driver.find_element(By.CSS_SELECTOR, 'article.page__content h1.page__content-title')
        title_text = clean_text(title_element.text) if title_element else "Без заголовка"

        # Извлекаем ссылку на PDF
        pdf_link = driver.find_element(By.CSS_SELECTOR, 'article.page__content div.page__content-desc a')
        pdf_url = urljoin(url, pdf_link.get_attribute('href')) if pdf_link else None

        driver.quit()
        return title_text, pdf_url
    except Exception as e:
        print(f"Ошибка при парсинге страницы: {e}")
        return None, None


def parse_pdf(pdf_url):
    """Парсит PDF и извлекает текст, исключая страницы с невалидным текстом."""
    try:
        # Добавляем User-Agent, чтобы обойти возможные ограничения
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'
        }
        response = requests.get(pdf_url, headers=headers)
        response.raise_for_status()

        with open('temp.pdf', 'wb') as f:
            f.write(response.content)

        text_content = []
        with pdfplumber.open('temp.pdf') as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text and is_text_valid(page_text):
                    cleaned_text = clean_text(page_text)
                    text_content.append(cleaned_text)

        os.remove('temp.pdf')
        return '\n\n'.join(text_content)
    except requests.exceptions.HTTPError as e:
        print(f"Ошибка HTTP при загрузке PDF: {e}")
        return ""
    except Exception as e:
        print(f"Ошибка при парсинге PDF: {e}")
        return ""


def save_to_markdown(title, page_url, pdf_text):
    """Сохраняет текст в формате Markdown."""
    markdown_content = f"# {title}\n\n[Ссылка на страницу]({page_url})\n\n{pdf_text}"

    with open('output.md', 'w', encoding='utf-8') as f:
        f.write(markdown_content)
    print("Результат сохранен в output.md")


def main():
    url = "https://academydpo.org/pedagogicheskij-sostav"

    title, pdf_url = parse_page(url)
    if not title or not pdf_url:
        print("Не удалось извлечь заголовок или ссылку на PDF")
        return

    pdf_text = parse_pdf(pdf_url)
    if not pdf_text:
        print("Не удалось извлечь текст из PDF. Проверьте доступ к файлу или защиту от ботов.")
        return

    save_to_markdown(title, url, pdf_text)


if __name__ == "__main__":
    main()