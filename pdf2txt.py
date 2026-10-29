"""
独立的预处理脚本：把 PDF 中的纯文字提取出来，保存为 txt 文件。
用法：python pdf_to_txt.py
运行前按需修改下面的 PDF_PATH 和 TXT_PATH。
"""

import re

from pypdf import PdfReader

PDF_PATH = "knowledge_base.pdf"
TXT_PATH = "knowledge_base.txt"


def pdf_to_text(pdf_path):
    reader = PdfReader(pdf_path)
    pages_text = []
    for i, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        pages_text.append(text)
        print(f"已提取第 {i + 1}/{len(reader.pages)} 页")
    return "\n\n".join(pages_text)


def collapse_repeated_chars(text, min_repeat=2):
    """部分 PDF 用重叠绘制同一字符来模拟加粗/阴影效果，解析时会被重复
    提取为“字符 空格 字符 空格 字符...”的形式，这里把这种模式压缩为 1 个字符。"""
    pattern = re.compile(r"(\S) (?:\1 ){" + str(min_repeat - 2) + r",}\1")
    return pattern.sub(r"\1", text)


def remove_space_between_cjk(text):
    """部分 PDF 会把中文字符间的字距处理成真实空格，导致“一句话”被拆成
    “单 字 隔 开”的样子。中文排版本身没有字间空格，这里把两个中文字符
    之间的空格去掉；英文单词间的空格不受影响，因为两侧必须都是中文字符才匹配。"""
    cjk = r"一-鿿　-〿＀-￯"
    pattern = re.compile(f"(?<=[{cjk}]) (?=[{cjk}])")
    return pattern.sub("", text)


def main():
    text = pdf_to_text(PDF_PATH)
    text = collapse_repeated_chars(text)
    text = remove_space_between_cjk(text)
    with open(TXT_PATH, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"转换完成，共 {len(text)} 字符，已保存到 {TXT_PATH}")


if __name__ == "__main__":
    main()
