"""Анализ обложек без платных сервисов.

Вход: папка с картинками обложек. Чтобы сравнить группы, разложи их в подпапки
win/ (залетевшие) и normal/ (обычные); можно и одной папкой.
Обложки можно скачать по ссылке https://i.ytimg.com/vi/<ID>/hqdefault.jpg
или пользователь загружает скриншоты.

Что делает:
1. Считает объективные метрики: яркость, контраст, насыщенность, «загруженность»
   (плотность деталей), доля тёплых цветов, 3 доминирующих цвета.
2. Сравнивает группы win / normal.
3. Собирает сетки превью: мобильный размер (168×94) — проверка читаемости,
   и средний (320×180) — для визуальной разметки по чек-листу.

Пример: python thumbnails.py ./thumbs --out ./thumb_report
"""
import argparse
import colorsys
import os
import pandas as pd
from PIL import Image, ImageDraw, ImageFilter, ImageStat
from _common import md

ap = argparse.ArgumentParser()
ap.add_argument("folder")
ap.add_argument("--out", default="thumb_report")
a = ap.parse_args()
os.makedirs(a.out, exist_ok=True)
EXT = (".jpg", ".jpeg", ".png", ".webp")

files = []
for root, _, names in os.walk(a.folder):
    grp = os.path.basename(root) if root != a.folder else "all"
    for n in sorted(names):
        if n.lower().endswith(EXT):
            files.append((grp, os.path.join(root, n)))
if not files:
    raise SystemExit("Картинок не найдено.")


def metrics(path):
    im = Image.open(path).convert("RGB").resize((320, 180))
    gray = im.convert("L")
    st = ImageStat.Stat(gray)
    hsv = im.convert("HSV")
    sat = ImageStat.Stat(hsv.getchannel("S")).mean[0] / 255 * 100
    edges = ImageStat.Stat(gray.filter(ImageFilter.FIND_EDGES)).mean[0]
    q = im.quantize(colors=6, method=Image.Quantize.MEDIANCUT)
    pal = q.getpalette()
    counts = sorted(q.getcolors(), reverse=True)
    dom, warm, total = [], 0, sum(c for c, _ in counts)
    for c, idx in counts:
        r, g, b = pal[idx * 3: idx * 3 + 3]
        h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
        if s > 0.25 and v > 0.2 and (h < 0.14 or h > 0.92):
            warm += c
        if len(dom) < 3:
            dom.append(f"#{r:02x}{g:02x}{b:02x}")
    return {
        "яркость": round(st.mean[0] / 255 * 100),
        "контраст": round(st.stddev[0] / 128 * 100),
        "насыщенность": round(sat),
        "загруженность": round(edges, 1),
        "тёплые цвета, %": round(warm / total * 100),
        "доминирующие цвета": " ".join(dom),
    }


rows = []
for grp, p in files:
    try:
        rows.append({"группа": grp, "файл": os.path.basename(p), **metrics(p)})
    except Exception as e:
        print("пропуск", p, e)
d = pd.DataFrame(rows)
print("## Метрики по каждой обложке")
print(md(d))

num = ["яркость", "контраст", "насыщенность", "загруженность", "тёплые цвета, %"]
if d["группа"].nunique() > 1:
    print("\n## Сравнение групп (медианы)")
    print(md(d.groupby("группа")[num].median().round(0).reset_index()))
    print("\nЗначимо, если разница заметная (≥15 пунктов по шкалам 0–100). Загруженность: выше = больше мелких деталей.")


def grid(size, name, cols=5):
    w, h = size
    label = 14
    rows_n = (len(files) + cols - 1) // cols
    canvas = Image.new("RGB", (cols * (w + 6), rows_n * (h + label + 6)), "white")
    dr = ImageDraw.Draw(canvas)
    for i, (grp, p) in enumerate(files):
        im = Image.open(p).convert("RGB").resize(size)
        x, y = (i % cols) * (w + 6), (i // cols) * (h + label + 6)
        canvas.paste(im, (x, y + label))
        dr.text((x + 2, y), f"{i + 1}. {grp}", fill="black")
    path = os.path.join(a.out, name)
    canvas.save(path)
    return path


print("\n## Сетки для просмотра")
print("Мобильный размер (читаемость):", grid((168, 94), "grid_mobile.png"))
print("Для разметки по чек-листу:", grid((320, 180), "grid_medium.png"))
print("Открой сетки инструментом просмотра изображений и разметь каждую обложку по чек-листу из references/thumbnails.md.")
