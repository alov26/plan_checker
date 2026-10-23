from pathlib import Path

from file_dop import read_csv, read_enterprises, group_tasks
from checks import find_repeats


enterprises = read_enterprises("enterprises.txt")

files = sorted(Path("data").glob("*.csv"))

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

report_folder = Path("reports")
report_folder.mkdir(exist_ok=True)

report_path = report_folder / "repeats.txt"

report_path.write_text(
    "\n".join(report_lines),
    encoding="utf-8",
)

print("Отчёт сохранён:", report_path)