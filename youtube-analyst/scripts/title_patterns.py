"""Паттерны заголовков: сравнение залетевших и обычных роликов.

Вход: CSV с колонками title и views (+ channel опц.). Группы определяются по ×медианы
(как в outliers.py): залетевшие ≥ --min, обычные 0.6–1.4×.
Если колонки views нет — нужна колонка group со значениями win / normal.

Пример: python title_patterns.py videos.csv
"""
import argparse
import warnings
warnings.filterwarnings("ignore")
import re
import pandas as pd
from _common import read_table, find_col, to_num, md

ap = argparse.ArgumentParser()
ap.add_argument("file")
ap.add_argument("--min", type=float, default=3.0)
a = ap.parse_args()

df = read_table(a.file)
tc, vc, cc = find_col(df, "title"), find_col(df, "views"), find_col(df, "channel")
d = pd.DataFrame({"title": df[tc].astype(str)})
if vc:
    d["views"] = to_num(df[vc])
    d["channel"] = df[cc].astype(str) if cc else "канал"
    d["x"] = d["views"] / d.groupby("channel")["views"].transform("median")
    d["group"] = None
    d.loc[d["x"] >= a.min, "group"] = "win"
    d.loc[(d["x"] >= 0.6) & (d["x"] <= 1.4), "group"] = "normal"
elif "group" in df.columns:
    d["group"] = df["group"]
else:
    raise SystemExit("Нужна колонка просмотров или group (win/normal).")
d = d.dropna(subset=["group"])

FEATURES = {
    "есть число": r"\d",
    "вопрос (?)": r"\?",
    "восклицание (!)": r"!",
    "КАПС-слово": r"\b[A-ZА-ЯЁ]{3,}\b",
    "я / мой / личный опыт": r"(?i)\b(я|мой|моя|моё|мне|меня|i|my|me|i'm|i've)\b",
    "ты / вы (обращение)": r"(?i)\b(ты|вы|твой|ваш|тебе|вам|you|your)\b",
    "отрицание / запрет": r"(?i)\b(не|нельзя|никогда|никто|ничего|стоп|перестань|don't|never|stop|no one|nobody)\b",
    "крайность": r"(?i)(сам(ый|ая|ое|ые)|худш|лучш|невероятн|безумн|most|worst|best|insane|craziest)",
    "почему / как / что": r"(?i)^(почему|как|что|зачем|why|how|what)\b",
    "сравнение (vs / против)": r"(?i)(\bvs\b|против|или|versus)",
    "деньги / цифры результата": r"(?i)(\$|₽|руб|доллар|миллион|тысяч|million|\bk\b)",
    "время / срок": r"(?i)(\d+\s*(дн|час|мин|лет|год|недел|days?|hours?|years?|weeks?))",
    "тайна / правда / секрет": r"(?i)(правд|секрет|тайн|скрыва|real|truth|secret|hidden)",
    "эмодзи": r"[\U0001F300-\U0001FAFF]",
    "двоеточие / тире": r"[:—|-]",
}
for name, rx in FEATURES.items():
    d[name] = d["title"].str.contains(rx, regex=True)
d["длина, симв."] = d["title"].str.len()
d["слов"] = d["title"].str.split().str.len()

g = d.groupby("group")
n = g.size()
rows = []
for name in FEATURES:
    w = d.loc[d.group == "win", name].mean() * 100 if n.get("win", 0) else float("nan")
    o = d.loc[d.group == "normal", name].mean() * 100 if n.get("normal", 0) else float("nan")
    rows.append({"признак": name, "у залетевших, %": round(w), "у обычных, %": round(o), "разница": round(w - o)})
res = pd.DataFrame(rows).sort_values("разница", ascending=False)

print(f"Залетевших: {n.get('win', 0)}, обычных: {n.get('normal', 0)}")
if n.get("win", 0) < 5 or n.get("normal", 0) < 5:
    print("⚠ Меньше 5 роликов в группе — выводы предварительные.")
print("\n## Признаки заголовков")
print(md(res))
print("\n## Длина")
print(md(g[["длина, симв.", "слов"]].median().round(0).reset_index()))
print("\nПаттерн = разница ≥ 25 п.п. Остальное — норма ниши или шум.")
print("\n## Заголовки залетевших (для ручного разбора шаблонов)")
for t in d.loc[d.group == "win", "title"]:
    print("-", t)
