import os
import re

UI_DIRS = [r"src\ui"]

KEYWORDS = [
    "Loi ", "loi ", "Chua ", "chua ",
    "Thanh cong", "thanh cong",
    "cap nhat", "Cap nhat",
    "Khong ", "khong ",
    "Nut ", "nut ",
    "Buoc ", "buoc ",
    "chi so", "Chi so",
    "tai lai", "Tai lai",
    "phan tich", "Phan tich",
    "dang ky", "Dang ky",
    "dang nhap", "Dang nhap",
    "tao moi", "Tao moi",
    "xoa ", "Xoa ",
    "kiem tra", "Kiem tra",
    "gui ", "Gui ",
    "tim ", "Tim ",
    "hien thi", "Hien thi",
    "xem truoc", "Xem truoc",
    "sao chep", "Sao chep",
]

results = []
for ui_dir in UI_DIRS:
    for root, dirs, files in os.walk(ui_dir):
        for fname in files:
            if fname.endswith(".py"):
                fpath = os.path.join(root, fname)
                with open(fpath, encoding="utf-8", errors="ignore") as fh:
                    for i, line in enumerate(fh, 1):
                        for kw in KEYWORDS:
                            if kw in line:
                                results.append((fpath, i, kw, line.rstrip()))
                                break

if results:
    for fpath, lineno, kw, line in results:
        print(f"[{kw}] {fpath}:{lineno}")
        print(f"  {line.strip()}")
        print()
else:
    print("OK - Khong phat hien chuoi tieng Viet khong dau.")

print(f"Tong: {len(results)} dong")
