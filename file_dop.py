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

        if current_enterprise is not None and not is_empty(task):
            plans[current_enterprise].append(task)

    return plans