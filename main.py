from pathlib import Path

from file_dop import read_csv, read_enterprises, group_tasks
from checks import find_repeats, get_period_dates


BASE_DIR = Path(__file__).resolve().parent

enterprises_path = BASE_DIR / "enterprises.txt"
data_folder = BASE_DIR / "data"
report_folder = BASE_DIR / "reports"


if not enterprises_path.is_file():
    print("Не найден список предприятий:", enterprises_path)
    raise SystemExit(1)


enterprises = read_enterprises(enterprises_path)

if not enterprises:
    print("Список предприятий пуст:", enterprises_path)
    raise SystemExit(1)


if not data_folder.is_dir():
    print("Не найдена папка с планами:", data_folder)
    raise SystemExit(1)


files = sorted(data_folder.glob("*.csv"))

if not files:
    print("В папке нет CSV-файлов с планами:", data_folder)
    raise SystemExit(1)

for path in files:
    try:
        get_period_dates(path.stem)
    except ValueError as error:
        print(f"Ошибка в имени файла {path.name}: {error}")
        raise SystemExit(1)

history = {}

print("Найдено файлов:", len(files))

for path in files:
    rows = read_csv(path)
    plans = group_tasks(rows, enterprises)

    history[path.stem] = plans

    filled = 0
    empty = 0
    missing = 0

    for name in enterprises:
        if name not in plans:
            missing += 1

        elif not plans[name]:
            empty += 1

        else:
            filled += 1

    print()
    print("Период:", path.stem)
    print("Есть записи:", filled)
    print("Без записей:", empty)
    print("Отсутствуют в таблице:", missing)


repeats = find_repeats(history)

print()
print("ЗАДАЧИ С ПОВТОРОМ ОТ ТРЁХ ПЕРИОДОВ ПОДРЯД")
print()

if not repeats:
    print("Подтверждённые повторы не найдены.")

for item in repeats:
    print("Предприятие:", item["enterprise"])
    print("Задача:", item["task"])
    print("Периодов подряд:", item["count"])
    print()

report_lines = [
    "ПОВТОРЯЮЩИЕСЯ ЗАДАЧИ",
    "Проверка последнего периода: " + sorted(history)[-1],
    "",
    "Повтор текста — повод для проверки, а не доказательство копирования.",
    "",
]

if not repeats:
    report_lines.append("Подтверждённые повторы не найдены.")

for item in repeats:
    report_lines.append("Предприятие: " + item["enterprise"])
    report_lines.append("Задача: " + item["task"])
    report_lines.append(
        "Периодов подряд: " + str(item["count"])
    )
    report_lines.append("")

report_folder.mkdir(exist_ok=True)


report_path = report_folder / "repeats.txt"

report_path.write_text(
    "\n".join(report_lines),
    encoding="utf-8",
)

print("Отчёт сохранён:", report_path)