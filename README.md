# ASearch

Консольная утилита и Python-модуль для поиска подстрок в строке или файле с использованием алгоритма Кнута-Морриса-Пратта (КМП).

## Возможности

- Поиск одной или нескольких подстрок.
- Поиск в строке (`--string`) или в файле (`--file`).
- Режимы поиска:
  - `first` — в прямом порядке;
  - `last` — в обратном порядке.
- Ограничение количества найденных вхождений (`--count`).
- Чувствительность к регистру (`--case-sensitive`).
- Цветная подсветка найденных фрагментов в консоли (`--color`, до 10 строк вывода).
- Логирование времени выполнения CLI через декоратор.

## Структура проекта

- `search.py` — основная реализация поиска и CLI.
- `test_search.py` — юнит-тесты.
- `.pylintrc` — конфигурация `pylint`.

## Требования

- Python 3.9+

## Запуск CLI

Общая форма:

```bash
python search.py [-s STRING | -f FILE] -u SUBSTRING [-u SUBSTRING ...] [-c] [-m {first,last}] [-k COUNT] [--color] [--encoding ENCODING]
```

### Аргументы

- `-s, --string` — исходная строка для поиска.
- `-f, --file` — путь к файлу для поиска.
- `-u, --substring` — подстрока для поиска. Можно передавать несколько раз или перечислять через запятую.
- `-c, --case-sensitive` — включить чувствительность к регистру.
- `-m, --method` — порядок выдачи: `first` или `last`.
- `-k, --count` — ограничить количество результатов.
- `--color` — вывести фрагмент исходного текста с подсветкой совпадений.
- `--encoding` — кодировка файла (по умолчанию `utf-8`).

> Нужно указать ровно один источник: либо `--string`, либо `--file`.

## Примеры

Поиск одной подстроки в строке:

```bash
python search.py -s "ababbababa" -u "aba"
```

Результат:

```text
(0, 5, 7)
```

Поиск нескольких подстрок:

```bash
python search.py -s "ababbababa" -u "aba,bba"
```

Результат:

```text
{'aba': (0, 5, 7), 'bba': (3,)}
```

Поиск в файле с ограничением и обратным порядком:

```bash
python search.py -f input.txt -u "error" -m last -k 3 --encoding utf-8
```

Вывод с подсветкой:

```bash
python search.py -s "Hello hello HELLO" -u "hello" --color
```

## Использование как модуля

```python
from search import search

result = search(
    string="ababbababa",
    sub_string=("aba", "bba"),
    case_sensitivity=False,
    method="first",
    count=None,
)
print(result)  # {'aba': (0, 5, 7), 'bba': (3,)}
```

Сигнатура функции:

```python
search(
    string: str,
    sub_string: str | list[str] | tuple[str, ...],
    case_sensitivity: bool = False,
    method: str = "first",
    count: int | None = None,
) -> tuple[int, ...] | dict[str, tuple[int, ...] | None] | None
```

## Тесты

Запуск тестов:

```bash
python -m unittest -v
```

## Линтинг

```bash
pylint search.py test_search.py --rcfile=.pylintrc
```
