"""Общие помощники: чтение таблиц и поиск колонок по-русски и по-английски."""
import re
import sys
import pandas as pd

ALIASES = {
    "title": ["title", "video title", "название", "название видео", "заголовок", "содержание", "content", "name"],
    "views": ["views", "view count", "просмотры", "просмотров", "viewcount"],
    "channel": ["channel", "channel name", "канал", "автор", "author"],
    "published": ["published", "publish date", "date", "video publish time", "время публикации видео", "дата публикации", "дата", "uploaded"],
    "subscribers": ["subscribers", "subs", "подписчики", "подписчиков"],
    "duration": ["duration", "длительность", "продолжительность"],
    "impressions": ["impressions", "показы", "показы значков"],
    "ctr": ["impressions click-through rate (%)", "ctr", "ctr для значков видео (%)", "ctr для значков (%)", "click-through rate"],
    "avg_view_pct": ["average percentage viewed (%)", "средний процент просмотра (%)", "средний процент просмотра", "avg % viewed"],
    "avg_view_dur": ["average view duration", "средняя продолжительность просмотра"],
    "watch_hours": ["watch time (hours)", "время просмотра (часы)"],
    "format": ["format", "формат", "type", "тип"],
    "url": ["url", "link", "ссылка"],
}


def read_table(path):
    if path.lower().endswith((".xlsx", ".xls")):
        return pd.read_excel(path)
    for enc in ("utf-8-sig", "utf-16", "cp1251"):
        try:
            return pd.read_csv(path, encoding=enc, sep=None, engine="python")
        except Exception:
            continue
    sys.exit(f"Не удалось прочитать файл: {path}")


def find_col(df, key):
    norm = {re.sub(r"\s+", " ", str(c)).strip().lower(): c for c in df.columns}
    for alias in ALIASES[key]:
        if alias in norm:
            return norm[alias]
    for alias in ALIASES[key]:  # частичное совпадение
        for n, c in norm.items():
            if alias in n:
                return c
    return None


def to_num(s):
    return pd.to_numeric(
        s.astype(str).str.replace("\u00a0", "").str.replace(" ", "").str.replace("%", "").str.replace(",", "."),
        errors="coerce",
    )


def to_seconds(v):
    """'12:34', '1:02:03', '754' -> секунды."""
    if pd.isna(v):
        return None
    s = str(v).strip()
    if ":" in s:
        parts = [float(p) for p in s.split(":")]
        sec = 0
        for p in parts:
            sec = sec * 60 + p
        return sec
    try:
        return float(s)
    except ValueError:
        return None


def md(df):
    """Таблица в markdown; если нет tabulate — простой текст."""
    try:
        return df.to_markdown(index=False)
    except ImportError:
        return df.to_string(index=False)
