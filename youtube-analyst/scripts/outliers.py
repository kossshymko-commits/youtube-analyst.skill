"""Поиск залетевших роликов без платных сервисов.

Вход: CSV/XLSX с колонками (названия гибкие, RU/EN): title, views, channel (опц.),
published (опц.), subscribers (опц.), format (опц.: shorts/long), url (опц.).
Считает медиану просмотров по каждому каналу (и формату) и множитель ×медианы.

Пример: python outliers.py videos.csv --min 3
"""
import argparse
import pandas as pd
from _common import read_table, find_col, to_num, md

ap = argparse.ArgumentParser()
ap.add_argument("file")
ap.add_argument("--min", type=float, default=3.0, help="порог ×медианы (по умолчанию 3)")
ap.add_argument("--top", type=int, default=20)
a = ap.parse_args()

df = read_table(a.file)
c = {k: find_col(df, k) for k in ["title", "views", "channel", "published", "subscribers", "format", "url"]}
if not c["title"] or not c["views"]:
    raise SystemExit(f"Нужны колонки с названием и просмотрами. Найдены: {list(df.columns)}")

d = pd.DataFrame({"title": df[c["title"]].astype(str), "views": to_num(df[c["views"]])})
d["channel"] = df[c["channel"]].astype(str) if c["channel"] else "канал"
d["format"] = df[c["format"]].astype(str).str.lower() if c["format"] else "all"
if c["subscribers"]:
    d["subs"] = to_num(df[c["subscribers"]])
if c["url"]:
    d["url"] = df[c["url"]].astype(str)
if c["published"]:
    d["published"] = pd.to_datetime(df[c["published"]], errors="coerce", dayfirst=True)
    days = (pd.Timestamp.now() - d["published"]).dt.days.clip(lower=1)
    d["views_per_day"] = (d["views"] / days).round(0)
d = d[df[c["title"]].notna().values].dropna(subset=["views"])

grp = d.groupby(["channel", "format"])["views"]
d["median"] = grp.transform("median")
d["n_in_channel"] = grp.transform("count")
d["x_median"] = (d["views"] / d["median"]).round(1)
if "subs" in d:
    d["views_per_sub"] = (d["views"] / d["subs"]).round(2)

print("## Медианы по каналам")
summary = d.groupby(["channel", "format"]).agg(роликов=("views", "count"), медиана=("views", "median")).reset_index()
print(md(summary))
small = summary[summary["роликов"] < 10]
if len(small):
    print("\n⚠ Меньше 10 роликов у:", ", ".join(small["channel"]), "— медиана ненадёжна.")

out = d[d["x_median"] >= a.min].sort_values("x_median", ascending=False).head(a.top)
cols = [x for x in ["title", "channel", "views", "x_median", "views_per_sub", "views_per_day", "url"] if x in out]
print(f"\n## Залетевшие ролики (≥ {a.min}× медианы): {len(out)}")
print(md(out[cols]) if len(out) else "Нет роликов выше порога — попробуй --min 2.")

# Обычные ролики для сравнения паттернов (около медианы)
normal = d[(d["x_median"] >= 0.6) & (d["x_median"] <= 1.4)].sort_values("x_median")
print(f"\n## Обычные ролики для сравнения (0.6–1.4× медианы): {len(normal)}")
print(normal[[x for x in ["title", "channel", "views", "x_median"] if x in normal]].head(15).pipe(md))
