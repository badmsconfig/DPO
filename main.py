import os
import subprocess
import glob
import datetime

BASE_DIR = r"D:\python_work\DPO\DPO"
SCRIPTS = [
    "DPO_aktsii.py",
    "DPO_dokument-company.py",
    "DPO_dokumenty.py",
    "DPO_FAQ.py",
    "DPO_finhozdeyat.py",
    "DPO_glavnaya.py",
    "DPO_master-of-business-administration-mba.py",
    "DPO_matertehnichobespechenieiosnashhennost.py",
    "DPO_napravleniya-main.py",
    "DPO_onas.py",
    "DPO_oplata-obrazovatelnyh-uslug.py",
    "DPO_osnovnye-svedeniya.py",
    "DPO_partnery.py",
    "DPO_pedagogicheskij-sostav.py",
    "DPO_platnye-obrazovatelnye-uslugi.py",
    "DPO_rukovodstvo.py",
    "DPO_rukovodstvo-i-pedagogicheskij-sostav.py",
    "DPO_stipendii-i-inye-vidy-materialnoj-podderzhki.py",
    "DPO_vakantnye-mesta-dlya-priema-perevoda.py",
    "PDO_dostupnaya-sreda-v-ooo-akademiya-dpo.py",
    "PDO_kontakty.py",
    "PDO_materialno-tehnicheskoe-obespechenie-i-osnashhennost-obrazovatelnogo-protsessa.py",
    "PDO_materialno-tehnicheskoe-obespechenie-i-osnashhennost-obrazovatelnogo-protsessa-dostupnaya-sreda.py",
    "PDO_mezhdunarodnoe-sotrudnichestvo.py",
    "PDO_obrazovanie.py",
    "PDO_organizatsiya-pitaniya.py",
    "PDO_politika-konfidentsialnosti-personalnyh-dannyh.py",
    "PDO_servis-proverki-dokumentov.py",
    "PDO_sotrudnichestvo.py",
    "PDO_stipendii.py",
    "PDO_struktura-i-organy-upravleniya.py",
    "PDO_vakantnye-mesta-dlya-priema-perevoda.py"
]
TIMESTAMP = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
OUTPUT_FILE = os.path.join(BASE_DIR, f"Раздел_1_{TIMESTAMP}.md")


def run_scripts():
    """Запускает все скрипты из списка и проверяет создание Markdown-файлов."""
    os.chdir(BASE_DIR)
    python_exe = os.path.join(BASE_DIR, r"..\venv\Scripts\python.exe")
    successful_scripts = []
    missing_files = []

    for script in SCRIPTS:
        expected_md = os.path.join(BASE_DIR, script.replace(".py", ".md"))
        try:
            print(f"Запуск скрипта: {script}")
            result = subprocess.run([python_exe, script], capture_output=True, text=True, timeout=300)
            if result.returncode == 0:
                print(f"Скрипт {script} успешно выполнен")
                successful_scripts.append(script)
                if os.path.exists(expected_md):
                    print(f"Создан файл: {expected_md}")
                else:
                    print(f"Ошибка: файл {expected_md} не создан")
                    missing_files.append(expected_md)
            else:
                print(f"Ошибка при выполнении {script}: {result.stderr}")
                missing_files.append(expected_md)
        except subprocess.TimeoutExpired:
            print(f"Скрипт {script} превысил время выполнения (5 минут)")
            missing_files.append(expected_md)
        except Exception as e:
            print(f"Исключение при выполнении {script}: {str(e)}")
            missing_files.append(expected_md)

    return successful_scripts, missing_files


def combine_markdown_files(missing_files):
    """Объединяет все Markdown-файлы в один и записывает информацию о пропущенных файлах."""
    markdown_files = glob.glob(os.path.join(BASE_DIR, "*.md"))
    print(f"Найдено Markdown-файлов: {len(markdown_files)}")
    print(f"Список файлов: {markdown_files}")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as outfile:
        outfile.write("# Раздел 1\n\n")
        outfile.write(f"Дата создания: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

        if not markdown_files:
            outfile.write("Ошибка: Markdown-файлы не найдены.\n")
            print("Ошибка: Markdown-файлы не найдены.")
            return

        added_files = []
        for md_file in sorted(markdown_files):
            if md_file == OUTPUT_FILE:
                continue
            try:
                with open(md_file, "r", encoding="utf-8") as infile:
                    outfile.write(f"## Данные из файла: {os.path.basename(md_file)}\n\n")
                    outfile.write(infile.read())
                    outfile.write("\n\n---\n\n")
                print(f"Файл {md_file} добавлен в итоговый отчет")
                added_files.append(md_file)
            except Exception as e:
                print(f"Ошибка при обработке {md_file}: {str(e)}")
                outfile.write(f"## Ошибка: файл {os.path.basename(md_file)} не добавлен\n\n")
                outfile.write(f"Причина: {str(e)}\n\n---\n\n")

        if missing_files:
            outfile.write("## Пропущенные или не созданные файлы\n\n")
            for missing_file in missing_files:
                if missing_file not in added_files:
                    outfile.write(f"- {os.path.basename(missing_file)}: не создан или не добавлен\n")
                    print(f"Файл {missing_file} не был создан или добавлен")
            for md_file in markdown_files:
                expected_mds = [script.replace(".py", ".md") for script in SCRIPTS]
                if os.path.basename(md_file) not in expected_mds and md_file != OUTPUT_FILE:
                    outfile.write(f"- {os.path.basename(md_file)}: найден, но не ожидался\n")
                    print(f"Файл {md_file} найден, но не ожидался")


def main():
    print("Запуск обработки скриптов...")
    successful_scripts, missing_files = run_scripts()
    print(f"\nУспешно выполнено скриптов: {len(successful_scripts)} из {len(SCRIPTS)}")
    print(f"Пропущенные файлы: {len(missing_files)}")
    print("\nОбъединение Markdown-файлов...")
    combine_markdown_files(missing_files)
    print(f"\nИтоговый файл создан: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()