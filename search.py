"""Инструменты поиска подстрок на основе алгоритма Кнута-Морриса-Пратта."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Tuple, Union
import argparse
import time


MAX_OUTPUT_LINES = 10
_RESET = "\033[0m"
_COLORS = (
    "\033[31m",
    "\033[32m",
    "\033[33m",
    "\033[34m",
    "\033[35m",
    "\033[36m",
    "\033[91m",
    "\033[92m",
    "\033[93m",
    "\033[94m",
)


def log_execution_time(function):
    """Декоратор логирования времени выполнения функции."""

    def wrapper(*args, **kwargs):
        started_at = time.perf_counter()
        result = function(*args, **kwargs)
        elapsed = (time.perf_counter() - started_at) * 1000
        print(f"[timing] {function.__name__}: {elapsed:.3f} ms")
        return result

    return wrapper


def _build_prefix_table(pattern: str) -> List[int]:
    """Строит префикс-функцию для КМП."""
    prefix = [0] * len(pattern)
    matched = 0
    for index in range(1, len(pattern)):
        while matched > 0 and pattern[index] != pattern[matched]:
            matched = prefix[matched - 1]
        if pattern[index] == pattern[matched]:
            matched += 1
            prefix[index] = matched
    return prefix


def _kmp_find_all(haystack: str, needle: str) -> List[int]:
    """Ищет все вхождения needle в haystack алгоритмом КМП."""
    if needle == "":
        return []
    prefix = _build_prefix_table(needle)
    result: List[int] = []
    matched = 0
    for index, symbol in enumerate(haystack):
        while matched > 0 and symbol != needle[matched]:
            matched = prefix[matched - 1]
        if symbol == needle[matched]:
            matched += 1
            if matched == len(needle):
                result.append(index - len(needle) + 1)
                matched = prefix[matched - 1]
    return result


def _ordered(
    matches: List[int],
    method: str,
    limit: Optional[int],
) -> Optional[Tuple[int, ...]]:
    if not matches:
        return None
    ordered = matches if method == "first" else list(reversed(matches))
    if limit is not None:
        ordered = ordered[:limit]
    return tuple(ordered) if ordered else None


def _normalize_substrings(sub_string: Union[str, Sequence[str]]) -> List[str]:
    if isinstance(sub_string, str):
        return [sub_string]
    return list(sub_string)


def search(
    string: str,
    sub_string: Union[str, Sequence[str]],
    case_sensitivity: bool = False,
    method: str = "first",
    count: Optional[int] = None,
) -> Optional[Union[Tuple[int, ...], Dict[str, Optional[Tuple[int, ...]]]]]:
    """Ищет подстроки в строке.

    Для одной подстроки возвращает кортеж индексов или None.
    Для нескольких подстрок возвращает словарь {подстрока: кортеж|None} или None,
    если не найдено ни одного вхождения для всех подстрок.
    """
    if method not in {"first", "last"}:
        raise ValueError("method must be 'first' or 'last'")
    if count is not None and count < 0:
        raise ValueError("count must be non-negative or None")

    source = string if case_sensitivity else string.lower()
    needles_original = _normalize_substrings(sub_string)
    needles = needles_original if case_sensitivity else [item.lower() for item in needles_original]

    if isinstance(sub_string, str):
        return _ordered(_kmp_find_all(source, needles[0]), method, count)

    if count is None:
        result = {
            original: _ordered(_kmp_find_all(source, prepared), method, None)
            for original, prepared in zip(needles_original, needles)
        }
    else:
        merged: List[Tuple[int, str]] = []
        for original, prepared in zip(needles_original, needles):
            for start in _kmp_find_all(source, prepared):
                merged.append((start, original))

        merged.sort(key=lambda item: item[0], reverse=(method == "last"))
        selected = merged[:count]

        grouped: Dict[str, List[int]] = {item: [] for item in needles_original}
        for position, needle_name in selected:
            grouped[needle_name].append(position)

        result = {key: (tuple(value) if value else None) for key, value in grouped.items()}

    if all(item is None for item in result.values()):
        return None
    return result


def search_in_file(
    file_path: str,
    sub_string: Union[str, Sequence[str]],
    case_sensitivity: bool = False,
    method: str = "first",
    count: Optional[int] = None,
    encoding: str = "utf-8",
) -> Optional[Union[Tuple[int, ...], Dict[str, Optional[Tuple[int, ...]]]]]:
    """Ищет подстроки в содержимом файла."""
    with open(file_path, "r", encoding=encoding) as source_file:
        content = source_file.read()
    return search(content, sub_string, case_sensitivity, method, count)


@dataclass(frozen=True)
class _Span:
    start: int
    end: int
    color: str


def _build_spans(
    text: str,
    substrings: Sequence[str],
    case_sensitivity: bool,
) -> List[_Span]:
    source = text if case_sensitivity else text.lower()
    spans: List[_Span] = []
    for index, substring in enumerate(substrings):
        prepared = substring if case_sensitivity else substring.lower()
        color = _COLORS[index % len(_COLORS)]
        for start in _kmp_find_all(source, prepared):
            spans.append(_Span(start=start, end=start + len(substring), color=color))
    spans.sort(key=lambda item: (item.start, -(item.end - item.start)))
    return spans


def highlight_matches(
    text: str,
    substrings: Sequence[str],
    case_sensitivity: bool = False,
    max_lines: int = MAX_OUTPUT_LINES,
) -> str:
    """Возвращает текст с ANSI-подсветкой найденных подстрок."""
    if not text:
        return ""

    pos = 0
    line_count = 0
    while line_count < max_lines and pos < len(text):
        next_nl = text.find("\n", pos)
        if next_nl == -1:
            pos = len(text)
            break
        pos = next_nl + 1
        line_count += 1

    text = text[:pos]
    spans = _build_spans(text, substrings, case_sensitivity)
    if not spans:
        return text

    result_parts: List[str] = []
    cursor = 0
    for span in spans:
        if span.start < cursor:
            continue
        result_parts.append(text[cursor:span.start])
        result_parts.append(span.color)
        result_parts.append(text[span.start:span.end])
        result_parts.append(_RESET)
        cursor = span.end
    result_parts.append(text[cursor:])
    return "".join(result_parts)


def _parse_substrings(raw_substrings: Sequence[str]) -> List[str]:
    parsed: List[str] = []
    for item in raw_substrings:
        if item == "":
            parsed.append("")
        else:
            parsed.extend(part for part in item.split(",") if part != "")
    if not parsed:
        raise ValueError("At least one substring must be provided")
    return parsed


def _make_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Поиск подстрок в строке/файле (КМП).")
    parser.add_argument("-s", "--string", help="Целевая строка для поиска.")
    parser.add_argument("-f", "--file", help="Путь к файлу для поиска.")
    parser.add_argument(
        "-u",
        "--substring",
        action="append",
        required=True,
        help="Подстрока(и) для поиска. Можно указывать несколько раз или через запятую.",
    )
    parser.add_argument(
        "-c",
        "--case-sensitive",
        action="store_true",
        help="Включить чувствительность к регистру.",
    )
    parser.add_argument(
        "-m",
        "--method",
        choices=("first", "last"),
        default="first",
        help="Направление поиска.",
    )
    parser.add_argument(
        "-k",
        "--count",
        type=int,
        default=None,
        help="Ограничение количества найденных вхождений.",
    )
    parser.add_argument(
        "--color",
        action="store_true",
        help=f"Вывести текст с подсветкой (не более {MAX_OUTPUT_LINES} строк).",
    )
    parser.add_argument("--encoding", default="utf-8", help="Кодировка файла.")
    return parser


@log_execution_time
def _run_cli(arguments: Optional[Sequence[str]] = None) -> int:
    parser = _make_parser()
    args = parser.parse_args(arguments)

    if (args.string is not None) == (args.file is not None):
        parser.error("Specify exactly one source: --string or --file")

    substrings = _parse_substrings(args.substring)
    payload = args.string
    if args.file:
        with open(args.file, "r", encoding=args.encoding) as source_file:
            payload = source_file.read()

    result = search(
        string=payload,
        sub_string=substrings if len(substrings) > 1 else substrings[0],
        case_sensitivity=args.case_sensitive,
        method=args.method,
        count=args.count,
    )
    print(result)

    if args.color:
        preview = highlight_matches(
            payload,
            substrings=substrings,
            case_sensitivity=args.case_sensitive,
            max_lines=MAX_OUTPUT_LINES,
        )
        print(preview)

    return 0


def main() -> int:
    """Точка входа консольной утилиты."""
    return _run_cli()


if __name__ == "__main__":
    raise SystemExit(main())