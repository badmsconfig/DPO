import os
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from pdf2image import convert_from_path
import pytesseract
import re
import time
import logging

# Настройка логирования удаленных строк
logging.basicConfig(
    filename='removed_stamps.log',
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    encoding='utf-8'
)

# Настройка пути к Tesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Users\Admin\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'  # Укажите ваш путь

# Настройка TESSDATA_PREFIX
os.environ['TESSDATA_PREFIX'] = r'C:\Program Files\Tesseract-OCR\tessdata'  # Укажите путь к tessdata

# Проверка Tesseract
try:
    tesseract_version = pytesseract.get_tesseract_version()
    print(f"Tesseract версия: {tesseract_version}")
except Exception as e:
    print(f"Ошибка Tesseract: {str(e)}")
    print(f"Проверьте, что Tesseract установлен по пути {pytesseract.pytesseract.tesseract_cmd}")
    exit(1)

# Проверка языков Tesseract
try:
    available_langs = pytesseract.get_languages()
    if 'rus' not in available_langs:
        print(
            f"Ошибка: Русский язык (rus) не установлен. Скачайте rus.traineddata и поместите в {os.environ['TESSDATA_PREFIX']}")
        exit(1)
    print(f"Доступные языки Tesseract: {available_langs}")
except Exception as e:
    print(f"Ошибка проверки языков Tesseract: {str(e)}")
    exit(1)

# Путь для сохранения Markdown-файлов
output_dir = r'D:\python_work\DPO\Doc_MD'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Путь к итоговому файлу
final_output_path = os.path.join(output_dir, 'Ustavdok.md')

# Путь к Poppler
poppler_path = r'D:\python_work\DPO\Release-24.08.0-0\poppler-24.08.0\Library\bin'  # Укажите ваш путь к папке bin Poppler

# Проверка Poppler
try:
    from pdf2image import pdfinfo_from_path
    print("Poppler работает (проверка pdf2image прошла)")
except Exception as e:
    print(f"Ошибка проверки Poppler: {str(e)}")
    print(f"Проверьте, что Poppler установлен и путь {poppler_path} содержит pdftoppm.exe")
    exit(1)

# URL страницы
url = 'https://academydpo.org/dokument-company'

# URL для исключения
excluded_url = 'https://academydpo.org/wp-content/uploads/2024/12/Litsenziya-AKADEMIYA-DPO.pdf'

# Настройка Selenium
chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-gpu')  # Для устранения ошибок GPU

# Запуск ChromeDriver
try:
    driver = webdriver.Chrome(options=chrome_options)
except Exception as e:
    print(f"Ошибка инициализации ChromeDriver: {str(e)}")
    exit(1)

# Функция для очистки текста от печатей, пустых строк и одинарных символов
def clean_stamp_text(text):
    # Список паттернов для печатей и похожих элементов
    stamp_patterns = [
        r"[Кк][оа]?[нв]?тур\s*Крипт[о|опро|а]",  # Вариации: "Контур", "Ковтур", "Ко тур", "Крипто", "Криптопро"
        r"владелец\s*(ООО|000|ооо|Ч00)?\s*\"?АКАДЕМИЯ\s*ДПО\"?",  # Название организации с ошибками
        r"МАНДАЖИ\s*ИВАН\s*АНАТОЛЬЕВИЧ|АКИ\s*ИВАН\s*АНАТОЛЬЕВИЧ",  # Имя владельца и его искажения
        r"Документ\s*подписан\s*квалифицированн[ой|ая|ой\s*электронной\s*подписью].*",  # Подпись с вариациями
        r"серийный\s*номер\s*[A-Z0-9\s/]*",  # Серийный номер с пробелами, слэшами и ошибками
        r"\d{2}\.\d{2}\.\d{4}\s*-\s*\d{2}\.\d{2}\.\d{4}.*",  # Диапазон дат с возможными ошибками
        r"[A-Z0-9\s/]{10,}",  # Длинные строки из букв, цифр, слэшей (серийные номера)
        r"удостоверяющий\s*центр",  # Элементы сертификатов
        r"электронная\s*подпись",  # Упоминания подписи
        r"сертификат",  # Упоминания сертификатов
        r"подпис[ь|ано|ать]",  # Вариации слова "подпись"
        r"срок\s*действия\s*(ООО|000|ооо|Ч00)?\s*\"?АКАДЕМИЯ\s*ДПО\"?",  # Срок действия и организация
        r"ННОЙ\s*Е",  # Фрагмент с ошибкой OCR
        r"владелецсерийный\s*номер",  # Слитный текст
        r"Блеелеч\s*оО\s*АКАД.*",  # Искажённая строка с именем и организацией
        r"й\s*йный\s*номе",  # Искажённый "серийный номер"
        r"Крипто\s*[внелен|ЕЕЛД\s*СЫ].*",  # Искажения "владелец"
        r"[оа]?нтур\s*Кри",  # Фрагменты "Контур Кри"
        r"В39А372321\s*ВААОРЕРОВАЕ",  # Частичный серийный номер
        r"ю\s*-\s*\d{2}\.\d{2}\.\d{4}",  # Искажённая дата
        r"владелец",  # Само слово "владелец"
        r"ннннннннн[Нн]+.*ОИВЕРЖДЕ",  # Искажённое "ПОДТВЕРЖДЕНО"
    ]

    # Разделяем текст на строки и фильтруем
    lines = text.split('\n')
    cleaned_lines = []
    for line in lines:
        # Удаляем пустые строки и строки, содержащие только пробелы
        if not line.strip():
            logging.info(f"Удалена пустая строка: {line}")
            continue
        # Удаляем строки, содержащие только один символ (буква, цифра, знак)
        if re.match(r'^\s*.\s*$', line):
            logging.info(f"Удалена строка с одним символом: {line}")
            continue
        # Проверяем, содержит ли строка элементы печати
        is_stamp = False
        for pattern in stamp_patterns:
            if re.search(pattern, line, re.IGNORECASE):
                is_stamp = True
                logging.info(f"Удалена строка (печать): {line}")
                break
        if not is_stamp:
            cleaned_lines.append(line)

    # Объединяем строки обратно
    return '\n'.join(cleaned_lines)

try:
    # Загрузка страницы
    driver.get(url)
    time.sleep(3)  # Ожидание загрузки страницы

    # Поиск всех ссылок в списке <ol>
    links = driver.find_elements(By.CSS_SELECTOR, 'ol li a')

    # Список для хранения содержимого всех Markdown-файлов
    all_markdown_content = []

    for link in links:
        pdf_url = link.get_attribute('href')
        document_name = link.text.strip()

        # Пропускаем указанный URL
        if pdf_url == excluded_url:
            print(f"Пропущен документ: {document_name} ({pdf_url})")
            continue

        # Очистка имени файла
        safe_filename = re.sub(r'[^\w\s-]', '', document_name).replace(' ', '_') + '.md'
        output_path = os.path.join(output_dir, safe_filename)

        print(f"Обработка документа: {document_name}")

        # Скачивание PDF
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        try:
            pdf_response = requests.get(pdf_url, headers=headers)
            pdf_response.raise_for_status()
        except Exception as e:
            print(f"Ошибка скачивания PDF {document_name}: {str(e)}")
            continue

        # Сохранение PDF во временный файл
        temp_pdf_path = 'temp.pdf'
        with open(temp_pdf_path, 'wb') as f:
            f.write(pdf_response.content)

        # Конвертация PDF в изображения
        try:
            images = convert_from_path(temp_pdf_path, poppler_path=poppler_path, dpi=300)
        except Exception as e:
            print(f"Ошибка при конвертации PDF {document_name}: {str(e)}")
            os.remove(temp_pdf_path)
            continue

        # Извлечение текста с помощью OCR
        full_text = []
        for i, image in enumerate(images):
            try:
                text = pytesseract.image_to_string(image, lang='rus')
                if not text.strip():
                    text = "Текст не распознан (пустая страница или низкое качество)"
                # Очистка текста от печатей, пустых строк и одинарных символов
                cleaned_text = clean_stamp_text(text)
                if cleaned_text.strip():  # Добавляем только непустой очищенный текст
                    full_text.append(cleaned_text)
            except Exception as e:
                full_text.append(f"Ошибка OCR: {str(e)}")

        # Пропускаем, если текст пустой
        if not full_text:
            print(f"Пропущен документ {document_name}: нет распознанного текста")
            os.remove(temp_pdf_path)
            continue

        # Объединяем текст всех страниц без заголовков
        markdown_content = f"# {document_name}\n\n" + '\n\n'.join(full_text)

        # Сохранение в индивидуальный Markdown-файл
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)

        print(f"Сохранено: {output_path}")

        # Добавляем содержимое в общий список
        all_markdown_content.append(markdown_content)

        # Удаление временного PDF
        os.remove(temp_pdf_path)

    # Сохранение всех Markdown-файлов в итоговый Ustavdok.md
    if all_markdown_content:
        with open(final_output_path, 'w', encoding='utf-8') as f:
            f.write('\n\n\n'.join(all_markdown_content))
        print(f"Итоговый файл сохранён: {final_output_path}")
    else:
        print("Нет содержимого для сохранения в Ustavdok.md")

finally:
    # Закрытие браузера
    driver.quit()

print("Обработка завершена!")