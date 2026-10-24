from pathlib import Path

from file_dop import (
    read_csv,
    read_enterprises,
    read_projects,
    group_tasks,
)
from checks import (
    find_repeats,
    get_period_dates,
    find_common_projects,
)

BASE_DIR = Path(__file__).resolve().parent

enterprises_path = BASE_DIR / "enterprises.txt"
projects_path = BASE_DIR / "projects.txt"
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

if not projects_path.is_file():
    print("Не найден справочник проектов:", projects_path)
    raise SystemExit(1)

try:
    projects = read_projects(projects_path)
except (OSError, UnicodeError, ValueError) as error:
    print("Ошибка чтения справочника проектов:", error)
    raise SystemExit(1)

if not projects:
    print("Справочник проектов пуст:", projects_path)
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
    plans, empty_enterprises, no_tasks_enterprises = group_tasks(
    rows, enterprises
    )

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
latest_period = sorted(history)[-1]
latest_plans = history[latest_period]

common_projects = find_common_projects(
    latest_plans, projects
)


latest_period = sorted(history)[-1]
latest_plans = history[latest_period]

common_projects = find_common_projects(
    latest_plans, projects
)

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
    "ОТЧЁТ ПО ПРОВЕРКЕ ПЛАНОВ",
    "Проверяемый период: " + latest_period,
    "",
    "1. ЗАПОЛНЕНИЕ",
    "",
    "Предприятия, не заполнившие ни одной задачи:",
]

if empty_enterprises:
    for name in empty_enterprises:
        report_lines.append("- " + name)
else:
    report_lines.append("Таких предприятий нет.")

report_lines.append("")
report_lines.append("Предприятия, которые написали «нет» или «-»:")

if no_tasks_enterprises:
    for name in no_tasks_enterprises:
        report_lines.append("- " + name)
else:
    report_lines.append("Таких предприятий нет.")

report_lines.extend([
    "",
    "2. ПОВТОРЫ ЗАДАЧ",
    "",
    "Задачи, повторяющиеся три последовательных периода и более.",
    "Повтор текста — повод для проверки, а не доказательство копирования.",
    "",
])

if not repeats:
    report_lines.append("Подтверждённые повторы не найдены.")

for item in repeats:
    report_lines.append("Предприятие: " + item["enterprise"])
    report_lines.append("Задача: " + item["task"])
    report_lines.append(
        "Периодов подряд: " + str(item["count"])
    )
    report_lines.append("")

report_lines.extend([
    "",
    "3. ОБЩИЕ ПРОЕКТЫ",
    "",
])

if not common_projects:
    report_lines.append(
        "Проекты с тремя и более упоминаниями не найдены."
    )

for item in common_projects:
    report_lines.append("Проект: " + item["project"])
    report_lines.append(
        "Количество упоминаний: " + str(item["count"])
    )
    report_lines.append(
        "Предприятия: " + ", ".join(item["enterprises"])
    )
    report_lines.append("")


report_folder.mkdir(exist_ok=True)

report_path = report_folder / "repeats.txt"

report_path.write_text(
    "\n".join(report_lines),
    encoding="utf-8",
)

print("Отчёт сохранён:", report_path)