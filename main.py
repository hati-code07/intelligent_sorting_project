import random
import time
import sys
from enum import Enum
from dataclasses import dataclass


# ============================================================
# 1. Алгоритмы сортировки
# ============================================================

def insertion_sort(arr):
    """Сортировка вставками: O(n^2), O(n) на почти отсортированных данных."""
    a = arr.copy()
    for i in range(1, len(a)):
        key = a[i]
        j = i - 1
        while j >= 0 and a[j] > key:
            a[j + 1] = a[j]
            j -= 1
        a[j + 1] = key
    return a


def quick_sort(arr):
    """Быстрая сортировка с медианой из трёх: O(n log n) в среднем."""
    a = arr.copy()

    def _quick(lo, hi):
        # Рекурсивно обрабатываем меньшую часть, большую — циклом,
        # чтобы ограничить глубину рекурсии.
        while lo < hi:
            mid = (lo + hi) // 2
            if a[mid] < a[lo]:
                a[mid], a[lo] = a[lo], a[mid]
            if a[hi] < a[lo]:
                a[hi], a[lo] = a[lo], a[hi]
            if a[hi] < a[mid]:
                a[hi], a[mid] = a[mid], a[hi]
            pivot = a[mid]

            i, j = lo, hi
            while i <= j:
                while i <= hi and a[i] < pivot:
                    i += 1
                while j >= lo and a[j] > pivot:
                    j -= 1
                if i <= j:
                    a[i], a[j] = a[j], a[i]
                    i += 1
                    j -= 1

            if j - lo < hi - i:
                if lo < j:
                    _quick(lo, j)
                lo = i
            else:
                if i < hi:
                    _quick(i, hi)
                hi = j

    _quick(0, len(a) - 1)
    return a


def merge_sort(arr):
    """Стабильная сортировка слиянием: O(n log n)."""
    if len(arr) <= 1:
        return arr.copy()

    mid = len(arr) // 2
    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])
    result = []
    i = j = 0

    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1

    result.extend(left[i:])
    result.extend(right[j:])
    return result


def heap_sort(arr):
    """Пирамидальная сортировка: O(n log n)."""
    a = arr.copy()
    n = len(a)

    def sift_down(start, end):
        root = start
        while 2 * root + 1 <= end:
            child = 2 * root + 1
            if child + 1 <= end and a[child] < a[child + 1]:
                child += 1
            if a[root] < a[child]:
                a[root], a[child] = a[child], a[root]
                root = child
            else:
                return

    for start in range((n - 2) // 2, -1, -1):
        sift_down(start, n - 1)
    for end in range(n - 1, 0, -1):
        a[0], a[end] = a[end], a[0]
        sift_down(0, end - 1)
    return a


def counting_sort(arr):
    """Сортировка подсчётом: O(n + k) для целых чисел с небольшим диапазоном."""
    if not arr:
        return []
    mn, mx = min(arr), max(arr)
    # Защита от выделения чрезмерно большого массива счётчиков.
    if mx - mn > 10_000_000:
        return sorted(arr)

    counts = [0] * (mx - mn + 1)
    for value in arr:
        counts[value - mn] += 1

    result = []
    for offset, count in enumerate(counts):
        result.extend([offset + mn] * count)
    return result


ALGORITHMS = {
    "insertion": insertion_sort,
    "quick": quick_sort,
    "merge": merge_sort,
    "heap": heap_sort,
    "counting": counting_sort,
}

ALG_NAMES = {
    "insertion": "Сортировка вставками",
    "quick": "Быстрая сортировка",
    "merge": "Сортировка слиянием",
    "heap": "Пирамидальная сортировка",
    "counting": "Сортировка подсчётом",
}


# ============================================================
# 2. Профилирование данных
# ============================================================

class DataType(Enum):
    EMPTY = "пустой"
    SINGLE = "один элемент"
    SORTED = "отсортирован"
    REVERSED = "обратно отсортирован"
    NEARLY_SORTED = "почти отсортирован"
    FEW_UNIQUE = "мало уникальных"
    MANY_DUPLICATES = "много дубликатов"
    NARROW_RANGE = "узкий диапазон целых"
    RANDOM = "случайный"


@dataclass
class DataProfile:
    size: int
    data_type: DataType
    unique_ratio: float
    is_integer: bool
    value_range: int
    sorted_ratio: float


def analyze(arr):
    """Определяет размер и характер входного массива."""
    n = len(arr)
    if n == 0:
        return DataProfile(0, DataType.EMPTY, 0.0, True, 0, 0.0)
    if n == 1:
        is_int = isinstance(arr[0], int)
        return DataProfile(1, DataType.SINGLE, 1.0, is_int, 0, 1.0)

    unique_ratio = len(set(arr)) / n
    is_int = all(isinstance(x, int) and not isinstance(x, bool) for x in arr)
    value_range = max(arr) - min(arr) if is_int else 0

    sorted_pairs = sum(arr[i] <= arr[i + 1] for i in range(n - 1))
    sorted_ratio = sorted_pairs / (n - 1)
    reversed_pairs = sum(arr[i] >= arr[i + 1] for i in range(n - 1))
    reversed_ratio = reversed_pairs / (n - 1)

    if sorted_ratio == 1.0:
        data_type = DataType.SORTED
    elif reversed_ratio == 1.0:
        data_type = DataType.REVERSED
    elif sorted_ratio >= 0.95:
        data_type = DataType.NEARLY_SORTED
    elif unique_ratio <= 0.05:
        data_type = DataType.FEW_UNIQUE
    elif unique_ratio <= 0.30:
        data_type = DataType.MANY_DUPLICATES
    elif is_int and value_range <= n * 2:
        data_type = DataType.NARROW_RANGE
    else:
        data_type = DataType.RANDOM

    return DataProfile(n, data_type, unique_ratio, is_int, value_range, sorted_ratio)


# ============================================================
# 3. Измерительный выбор алгоритма
# ============================================================

@dataclass
class Decision:
    algorithm: str
    reason: str
    timings: dict


def _time_func(func, data, repeats=3):
    """Возвращает лучшее время из нескольких прогонов."""
    best = float("inf")
    for _ in range(repeats):
        start = time.perf_counter()
        func(data)
        elapsed = time.perf_counter() - start
        best = min(best, elapsed)
    return best


def choose_algorithm(arr, profile):
    """
    Отбирает подходящие алгоритмы, тестирует их на выборке
    и выбирает алгоритм с минимальным измеренным временем.
    """
    n = profile.size
    if n <= 1:
        return Decision("insertion", "0–1 элемент — сортировать практически нечего", {})

    candidates = set(ALGORITHMS)
    if n > 5000:
        candidates.discard("insertion")

    # Counting sort подходит только целым числам с умеренным диапазоном.
    if not (profile.is_integer and profile.value_range <= max(10_000, n * 2)):
        candidates.discard("counting")

    sample_size = 2000
    if n <= sample_size:
        sample = arr.copy()
    else:
        step = n / sample_size
        sample = [arr[int(i * step)] for i in range(sample_size)]

    # Не запускаем counting sort на выборке, если фактический диапазон
    # выборки оказался слишком большим.
    sample_is_int = all(isinstance(x, int) and not isinstance(x, bool) for x in sample)
    if "counting" in candidates and (
        not sample_is_int or max(sample) - min(sample) > 10_000_000
    ):
        candidates.discard("counting")

    timings = {
        name: _time_func(ALGORITHMS[name], sample, repeats=3)
        for name in sorted(candidates)
    }
    winner = min(timings, key=timings.get)

    if winner == "counting":
        reason = f"узкий диапазон целых чисел (range={profile.value_range}); сортировка подсчётом"
    elif winner == "insertion":
        if profile.data_type in (DataType.SORTED, DataType.NEARLY_SORTED):
            reason = "почти упорядоченные данные; сортировка вставками требует мало перемещений"
        else:
            reason = f"малый размер n={n}; низкие накладные расходы сортировки вставками"
    elif winner == "quick":
        reason = "быстрая сортировка показала лучшее время на тестовой выборке"
    elif winner == "merge":
        reason = "сортировка слиянием показала лучшее время; сложность O(n log n)"
    else:
        reason = "пирамидальная сортировка показала лучшее время; сложность O(n log n)"

    reason += f" (замер на {len(sample)} элементах)"
    return Decision(winner, reason, timings)


def smart_sort(arr):
    """Основная функция: анализ данных → выбор → сортировка."""
    profile = analyze(arr)
    decision = choose_algorithm(arr, profile)
    return ALGORITHMS[decision.algorithm](arr), decision, profile


# ============================================================
# 4. Генераторы тестовых данных
# ============================================================

def make_random(n):
    return [random.randint(0, 10**6) for _ in range(n)]


def make_sorted(n):
    return list(range(n))


def make_reversed(n):
    return list(range(n, 0, -1))


def make_nearly_sorted(n, swaps=None):
    arr = list(range(n))
    if n < 2:
        return arr
    swaps = swaps if swaps is not None else max(1, n // 100)
    for _ in range(swaps):
        i, j = random.sample(range(n), 2)
        arr[i], arr[j] = arr[j], arr[i]
    return arr


def make_few_unique(n):
    return [random.choice([1, 2, 3]) for _ in range(n)]


def make_many_duplicates(n):
    return [random.randint(0, max(1, n // 10)) for _ in range(n)]


def make_narrow_range(n):
    return [random.randint(0, 100) for _ in range(n)]


# ============================================================
# 5. Ввод данных
# ============================================================

def parse_user_input(text):
    """Разбирает числа, разделённые пробелами, запятыми или точкой с запятой."""
    text = text.replace(",", " ").replace(";", " ")
    result = []
    for part in text.split():
        try:
            result.append(int(part))
        except ValueError:
            try:
                result.append(float(part))
            except ValueError as exc:
                raise ValueError(f"Не удалось распознать число: '{part}'") from exc
    return result


def input_array_interactive():
    print("\nВВОД МАССИВА")
    print("Введите числа через пробел, запятую или точку с запятой.")
    print("Пример: 5 3 8 1 9 2 7")
    while True:
        raw = input("Массив: ").strip()
        if not raw:
            print("Пустая строка — будет обработан пустой массив.")
            return []
        try:
            return parse_user_input(raw)
        except ValueError as exc:
            print(f"Ошибка: {exc}. Попробуйте ещё раз.")


def input_from_file(path):
    with open(path, "r", encoding="utf-8") as file:
        return parse_user_input(file.read())


def menu_input():
    print("\nСПОСОБ ВВОДА ДАННЫХ")
    print("1 — ввести массив вручную")
    print("2 — загрузить массив из файла")
    print("3 — сгенерировать случайный массив")
    print("0 — выход")

    while True:
        choice = input("Выбор: ").strip()
        if choice == "1":
            return input_array_interactive(), "ручной ввод"
        if choice == "2":
            path = input("Путь к файлу: ").strip()
            try:
                arr = input_from_file(path)
                print(f"Загружено элементов: {len(arr)}")
                return arr, f"файл {path}"
            except (OSError, ValueError) as exc:
                print(f"Не удалось прочитать файл: {exc}")
                continue
        if choice == "3":
            try:
                n = int(input("Размер массива: ").strip())
                lo = int(input("Минимум (Enter = 0): ").strip() or "0")
                hi = int(input("Максимум (Enter = 1000000): ").strip() or "1000000")
                if n < 0:
                    print("Размер не может быть отрицательным.")
                    continue
                if lo > hi:
                    lo, hi = hi, lo
                arr = [random.randint(lo, hi) for _ in range(n)]
                return arr, f"генерация (n={n}, диапазон [{lo}; {hi}])"
            except ValueError:
                print("Размер и границы должны быть целыми числами.")
                continue
        if choice == "0":
            return None, None
        print("Введите 0, 1, 2 или 3.")


# ============================================================
# 6. Отчёт по одному массиву
# ============================================================

def run_user_case(arr, source, verbose=False):
    profile = analyze(arr)
    decision = choose_algorithm(arr, profile)

    print("\n" + "=" * 64)
    print(f"Исходный массив (источник: {source}, n={len(arr)})")
    if len(arr) <= 100:
        print(arr)
    else:
        print(f"{arr[:30]} ... {arr[-10:]}")

    if verbose:
        print(
            f"\nТип: {profile.data_type.value} | уникальных: {profile.unique_ratio:.1%} "
            f"| отсортированных соседних пар: {profile.sorted_ratio:.1%}"
        )
        if profile.is_integer and profile.value_range:
            print(f"Диапазон значений: {profile.value_range}")
        print(f"Выбран алгоритм: {ALG_NAMES[decision.algorithm]}")
        print(f"Причина: {decision.reason}")
        print(f"\n{'Алгоритм':<28} {'Время, мс':>12} {'Корректно':>12}")
        print("-" * 54)
        expected = sorted(arr)
        for name, func in ALGORITHMS.items():
            if len(arr) > 20_000 and name == "insertion":
                print(f"{ALG_NAMES[name]:<28} {'—':>12} {'пропущен':>12}")
                continue
            try:
                start = time.perf_counter()
                result = func(arr)
                elapsed = (time.perf_counter() - start) * 1000
                print(f"{ALG_NAMES[name]:<28} {elapsed:>12.3f} {str(result == expected):>12}")
            except Exception as exc:
                print(f"{ALG_NAMES[name]:<28} {'—':>12} {'ошибка':>12}: {exc}")

    sorted_arr = ALGORITHMS[decision.algorithm](arr)
    print(f"\nРезультат ({ALG_NAMES[decision.algorithm]}):")
    print(sorted_arr if len(sorted_arr) <= 100 else f"{sorted_arr[:30]} ... {sorted_arr[-10:]}")
    print(f"Проверка корректности: {'OK' if sorted_arr == sorted(arr) else 'FAIL'}")


# ============================================================
# 7. Тестирование
# ============================================================

def benchmark_case(name, data):
    profile = analyze(data)
    print("\n" + "=" * 74)
    print(f"Тест: {name} (n={len(data)})")
    print(
        f"Тип: {profile.data_type.value} | уникальных: {profile.unique_ratio:.1%} "
        f"| отсортированных соседних пар: {profile.sorted_ratio:.1%}"
    )
    if profile.is_integer and profile.value_range:
        print(f"Диапазон значений: {profile.value_range}")

    decision = choose_algorithm(data, profile)
    print(f"Выбран алгоритм: {ALG_NAMES[decision.algorithm]}")
    print(f"Причина: {decision.reason}")
    print(f"\n{'Алгоритм':<28} {'Время, мс':>12} {'Корректно':>12}")
    print("-" * 54)

    results = []
    expected = sorted(data)
    for name_key, func in ALGORITHMS.items():
        if len(data) > 20_000 and name_key == "insertion":
            results.append((name_key, None, "пропущен"))
            continue
        try:
            start = time.perf_counter()
            result = func(data)
            elapsed = time.perf_counter() - start
            results.append((name_key, elapsed, result == expected))
        except Exception as exc:
            results.append((name_key, None, f"ошибка: {exc}"))

    chosen_time = None
    valid = []
    for name_key, elapsed, status in results:
        if elapsed is None:
            print(f"{ALG_NAMES[name_key]:<28} {'—':>12} {str(status):>12}")
            continue
        print(f"{ALG_NAMES[name_key]:<28} {elapsed * 1000:>12.3f} {str(status):>12}")
        if status is True:
            valid.append((name_key, elapsed))
        if name_key == decision.algorithm:
            chosen_time = elapsed

    if valid and chosen_time is not None:
        best_name, best_time = min(valid, key=lambda item: item[1])
        ratio = chosen_time / best_time if best_time else 1.0
        print(
            f"Быстрейший в этом запуске: {ALG_NAMES[best_name]} "
            f"({best_time * 1000:.3f} мс); выбранный алгоритм — {ratio:.2f}x от лучшего."
        )


def run_all_tests():
    random.seed(42)
    cases = [
        ("Пустой массив", []),
        ("Один элемент", [42]),
        ("Малый случайный (n=50)", make_random(50)),
        ("Средний случайный (n=5000)", make_random(5000)),
        ("Большой случайный (n=50000)", make_random(50000)),
        ("Отсортированный (n=20000)", make_sorted(20000)),
        ("Обратно отсортированный (n=20000)", make_reversed(20000)),
        ("Почти отсортированный (n=20000)", make_nearly_sorted(20000)),
        ("Мало уникальных (n=10000)", make_few_unique(10000)),
        ("Много дубликатов (n=20000)", make_many_duplicates(20000)),
        ("Узкий диапазон (n=20000)", make_narrow_range(20000)),
    ]

    for name, data in cases:
        benchmark_case(name, data)

    print("\nИтоговая проверка функции smart_sort:")
    all_ok = True
    for name, data in cases:
        result, decision, _ = smart_sort(data)
        ok = result == sorted(data)
        all_ok = all_ok and ok
        print(f"{name:<38} {ALG_NAMES[decision.algorithm]:<28} {'OK' if ok else 'FAIL'}")
    print(f"\nВсе проверки пройдены: {'ДА' if all_ok else 'НЕТ'}")


# ============================================================
# 8. Точка входа
# ============================================================

def main():
    args = sys.argv[1:]

    if args and args[0] == "demo":
        data = [5, 3, 8, 1, 9, 2, 7]
        result, decision, profile = smart_sort(data)
        print(f"Вход:    {data}")
        print(f"Выход:   {result}")
        print(f"Профиль: {profile.data_type.value}, n={profile.size}")
        print(f"Выбран:  {ALG_NAMES[decision.algorithm]}")
        print(f"Причина: {decision.reason}")
        return

    if args and args[0] == "file" and len(args) >= 2:
        try:
            arr = input_from_file(args[1])
            run_user_case(arr, f"файл {args[1]}", verbose=True)
        except (OSError, ValueError) as exc:
            print(f"Ошибка: {exc}")
        return

    if args and args[0] == "tests":
        run_all_tests()
        return

    print("ИНТЕЛЛЕКТУАЛЬНЫЙ ВЫБОР АЛГОРИТМА СОРТИРОВКИ")
    while True:
        arr, source = menu_input()
        if arr is None:
            print("Выход. До свидания!")
            break
        details = input("Показать подробности выбора? (д/н): ").strip().lower() in (
            "y", "yes", "д", "да"
        )
        run_user_case(arr, source, verbose=details)
        again = input("Сортировать ещё один массив? (д/н): ").strip().lower()
        if again not in ("y", "yes", "д", "да", "+"):
            print("Выход. До свидания!")
            break


if __name__ == "__main__":
    main()
