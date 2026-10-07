"""Разбор выгрузки из YouTube Студии (свой канал, бесплатно).

Как выгрузить: YouTube Студия → Аналитика → «Расширенный режим» → период
(лучше «Всё время» или 365 дней) → метрики: Показы, CTR для значков, Просмотры,
Средняя продолжительность просмотра, Средний процент просмотра, Подписчики →
кнопка экспорта → CSV. В архиве нужен файл «Table data.csv» (Данные таблицы).

Что делает: делит Shorts и длинные, считает медианы, находит свои залетевшие
ролики и ставит каждому ролику диагноз по связке CTR × удержание:
  хит / слабая упаковка (CTR) / не держит (удержание) / слабый по всем.

Пример: python studio_report.py "Table data.csv"
"""
import argparse
import pandas as pd
from _common import read_table, find_col, to_num, to_seconds, md

ap = argparse.ArgumentParser()
ap.add_argument("file")
ap.add_argument("--shorts-max", type=int, default=180, help="макс. длительность Shorts, сек")
a = ap.parse_args()

df = read_table(a.file)
c = {k: find_col(df, k) for k in ["title", "views", "published", "duration", "impressions", "ctr", "avg_view_pct", "avg_view_dur", "subscribers"]}
if not c["title"] or not c["views"]:
    raise SystemExit(f"Не нашёл колонки названия/просмотров. Колонки файла: {list(df.columns)}")

# убрать строку «Итого/Total» (в выгрузке Студии она первая, без названия)
first = df.columns[0]
df = df[df[c["title"]].notna() & ~df[first].astype("string").str.strip().str.lower().isin(["total", "итого"])]
d = pd.DataFrame({"title": df[c["title"]].astype(str), "views": to_num(df[c["views"]])})
for k in ["impressions", "ctr", "avg_view_pct", "subscribers"]:
    if c[k]:
        d[k] = to_num(df[c[k]])
if c["duration"]:
    d["dur_s"] = df[c["duration"]].map(to_seconds)
if c["published"]:
    d["published"] = pd.to_datetime(df[c["published"]], errors="coerce")
d = d[~d["title"].str.lower().isin(["nan", "итого", "total", ""])].dropna(subset=["views"])

d["формат"] = "длинное"
if "dur_s" in d:
    d.loc[d["dur_s"] <= a.shorts_max, "формат"] = "shorts"

missing = [k for k in ["impressions", "ctr", "avg_view_pct"] if k not in d]
if missing:
    print("⚠ В выгрузке нет метрик:", ", ".join(missing), "— добавь их в таблицу Студии перед экспортом для полного диагноза.\n")

tot_imp = d["impressions"].sum() if "impressions" in d else None
if len(d) < 10 or (tot_imp is not None and tot_imp < 1000):
    print(f"⚠ МАЛО ДАННЫХ: роликов {len(d)}, показов всего {tot_imp:.0f}. CTR и сравнения роликов — шум. "
          "Главный вывод для такого канала: алгоритм ещё не раздаёт ролики; анализируй нишу и конкурентов, а не эту таблицу.\n")

for fmt, g in d.groupby("формат"):
    g = g.copy()
    med = g["views"].median()
    g["×медианы"] = (g["views"] / med).round(1)
    print(f"# {fmt.upper()}: {len(g)} роликов, медиана просмотров {med:,.0f}".replace(",", " "))

    if "ctr" in g and "avg_view_pct" in g:
        mc, mr = g["ctr"].median(), g["avg_view_pct"].median()
        print(f"Медиана CTR: {mc:.1f}% · медиана среднего % просмотра: {mr:.0f}%")

        def diag(r):
            hc, hr = r["ctr"] >= mc, r["avg_view_pct"] >= mr
            if hc and hr:
                return "хит: тема+упаковка+контент"
            if not hc and hr:
                return "слабая упаковка → менять обложку/название"
            if hc and not hr:
                return "не держит → хук/обещание не совпадает"
            return "слабый по всем"
        g["диагноз"] = g.apply(diag, axis=1)
        print("\n## Распределение диагнозов")
        print(md(g["диагноз"].value_counts().rename_axis("диагноз").reset_index(name="роликов")))
    if "impressions" in g:
        low = g[g["impressions"] < g["impressions"].median() * 0.3]
        if len(low):
            print(f"\nАлгоритм почти не показывал {len(low)} роликов (показы < 30% медианы) — проблема темы/первых часов, а не упаковки.")

    cols = [x for x in ["title", "views", "×медианы", "impressions", "ctr", "avg_view_pct", "диагноз"] if x in g]
    print("\n## Топ-10 по ×медианы")
    print(md(g.sort_values("×медианы", ascending=False)[cols].head(10)))
    if "диагноз" in g:
        fix = g[g["диагноз"].str.startswith("слабая упаковка")].sort_values("avg_view_pct", ascending=False)
        if len(fix):
            print("\n## Кандидаты на замену обложки/названия (контент держит, клика нет)")
            print(md(fix[cols].head(10)))
    print()
