import csv

def normalize(text):
    text = text.lower()
    text = text.replace("ё", "е")
    words = text.split()
    return " ".join(words)

def is_empty(text):
    text = normalize(text)
    empty_values = ["", "-", "—", "нет", "н/д"]
    return text in empty_values

def read_csv(path):
    rows =[]

    with open(path, encoding="utf-8-sig", newline = "") as file:
        reader = csv.reader(file, delimiter=";")

        for row in reader:
            rows.append(row)

    return rows

def read_enterprises(path):
    enterprises = []

    with open(path, encoding="utf-8-sig") as file:
        for line in file:
            name = line.strip()

            if name:
                enterprises.append(name)

    return enterprises

def group_tasks(rows, enterprises):
    plans = {}
    names = {}
    marked_enterprises = set()

    for name in enterprises:
        names[normalize(name)] = name

    current_enterprise = None

    for row in rows:
        if len(row) < 2:
            current_enterprise = None
            continue

        name = normalize(row[0])
        task = row[1].strip()

        if name:
            if name not in names:
                current_enterprise = None
                continue

            current_enterprise = names[name]

            if current_enterprise not in plans:
                plans[current_enterprise] = []

        if current_enterprise is None:
            continue

        if normalize(task) in {"нет", "-", "—", "н/д"}:
            marked_enterprises.add(current_enterprise)

        elif not is_empty(task):
            plans[current_enterprise].append(task)

    empty_enterprises = []
    no_tasks_enterprises = []

    for name in enterprises:
        if plans.get(name):
            continue

        if name in marked_enterprises:
            no_tasks_enterprises.append(name)
        else:
            empty_enterprises.append(name)

    return plans, empty_enterprises, no_tasks_enterprises

def read_projects(path):
    projects = {}

    with open(path, encoding="utf-8-sig") as file:
        for line_number, line in enumerate(file, start=1):
            line = line.strip()

            if not line:
                continue

            if ";" not in line:
                raise ValueError(
                    f"Строка {line_number}: нужен формат "
                    "Название;вариант1|вариант2"
                )

            name, variants_text = line.split(";", 1)
            name = name.strip()

            variants = []

            for variant in variants_text.split("|"):
                variant = normalize(variant)

                if variant and variant not in variants:
                    variants.append(variant)

            if not name or not variants:
                raise ValueError(
                    f"Строка {line_number}: "
                    "не указано название проекта или варианты поиска."
                )

            if name in projects:
                raise ValueError(
                    f"Строка {line_number}: "
                    f"проект «{name}» указан повторно."
                )

            projects[name] = variants

    return projects
