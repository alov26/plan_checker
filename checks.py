from datetime import date, timedelta

from file_dop import normalize


def get_period_dates(period):
    parts = period.split("_")

    if len(parts) != 2:
        raise ValueError(
            f"Неверное название периода: {period}. "
            "Нужен формат YYYY-MM-DD_YYYY-MM-DD."
        )

    start_text, end_text = parts

    try:
        start = date.fromisoformat(start_text)
        end = date.fromisoformat(end_text)
    except ValueError:
        raise ValueError(
            f"Неверные даты в периоде: {period}. "
            "Проверьте даты и формат YYYY-MM-DD_YYYY-MM-DD."
        ) from None

    if (
        start.isoformat() != start_text
        or end.isoformat() != end_text
    ):
        raise ValueError(
            f"Неверный формат периода: {period}. "
            "Нужен формат YYYY-MM-DD_YYYY-MM-DD."
        )

    if start > end:
        raise ValueError(
            f"В периоде {period} дата начала позже даты окончания."
        )

    return start, end


def normalized_tasks(tasks):
    result = set()

    for task in tasks:
        result.add(normalize(task))

    return result


def find_repeats(history):
    results = []

    if not history:
        return results

    periods = sorted(history)
    current_period = periods[-1]
    current_plans = history[current_period]

    for name, tasks in current_plans.items():
        checked = set()

        for task in tasks:
            text = normalize(task)

            if text in checked:
                continue

            checked.add(text)

            count = 1
            next_start, _ = get_period_dates(current_period)

            for period in reversed(periods[:-1]):
                start, end = get_period_dates(period)

                if end + timedelta(days=1) != next_start:
                    break

                previous_plans = history[period]

                if name not in previous_plans:
                    break

                previous_tasks = normalized_tasks(
                    previous_plans[name]
                )

                if text not in previous_tasks:
                    break

                count += 1
                next_start = start

            if count >= 3:
                results.append({
                    "enterprise": name,
                    "task": task,
                    "count": count,
                })

    return results

def find_common_projects(plans, projects):
    results = []

    for project_name, variants in projects.items():
        project_count = 0
        enterprises = []

        for enterprise, tasks in plans.items():
            for task in tasks:
                text = normalize(task)

                for symbol in '«»"“”„':
                    text = text.replace(symbol, "")

                found = False

                for variant in variants:
                    if variant in text:
                        found = True
                        break

                if found:
                    project_count += 1

                    if enterprise not in enterprises:
                        enterprises.append(enterprise)

        if project_count >= 3:
            results.append({
                "project": project_name,
                "count": project_count,
                "enterprises": enterprises,
            })

    return results

def find_common_projects(plans, projects):
    results = []

    for project_name, variants in projects.items():
        project_count = 0
        enterprises = []

        for enterprise, tasks in plans.items():
            for task in tasks:
                text = normalize(task)

                for symbol in '«»"“”„':
                    text = text.replace(symbol, "")

                text = normalize(text)

                found = False

                for variant in variants:
                    if variant in text:
                        found = True
                        break

                if found:
                    project_count += 1

                    if enterprise not in enterprises:
                        enterprises.append(enterprise)

        if project_count >= 3:
            results.append({
                "project": project_name,
                "count": project_count,
                "enterprises": enterprises,
            })

    return results