import json


def log(path, text):
    with open(file=path, mode="a", encoding="utf-8") as f:
        line = json.dumps(text, ensure_ascii=False)
        f.write(line + "\n")
