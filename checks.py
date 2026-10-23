from datetime import date, timedelta

from file_dop import normalize


def get_period_dates(period):
    start_text, end_text = period.split("_")

    start = date.fromisoformat(start_text)
    end = date.fromisoformat(end_text)

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