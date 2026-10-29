"""
知识库预处理：自动识别文件类型，并统一转换为纯文本。

支持 .pdf 和 .txt。PDF 的转换结果缓存在 .cache/ 目录，PDF 未改动时直接复用。
也可以单独运行做检查：python preprocess.py [知识库路径]
"""

import re
from pathlib import Path

from pypdf import PdfReader

PROJECT_ROOT = Path(__file__).parent
CACHE_DIR = PROJECT_ROOT / ".cache"
SUPPORTED_SUFFIXES = {".pdf", ".txt"}


# ---------- 文本清洗 ----------


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


# ---------- 文件定位 ----------


def find_source_files(path):
    """根据配置的路径找到所有知识库文件。

    path 可以是文件，也可以是目录（只扫描该目录本层，不递归）；
    相对路径以项目根目录为基准。
    """
    path = Path(path)
    if not path.is_absolute():
        path = PROJECT_ROOT / path

    if path.is_file():
        if path.suffix.lower() not in SUPPORTED_SUFFIXES:
            raise ValueError(
                f"不支持的文件类型：{path.name}（目前支持：{', '.join(sorted(SUPPORTED_SUFFIXES))}）"
            )
        return [path]

    if path.is_dir():
        files = sorted(
            p
            for p in path.iterdir()
            if p.is_file() and p.suffix.lower() in SUPPORTED_SUFFIXES
        )
        if not files:
            raise FileNotFoundError(
                f"目录 {path} 中没有找到知识库文件（支持：{', '.join(sorted(SUPPORTED_SUFFIXES))}）"
            )
        return files

    raise FileNotFoundError(f"知识库路径不存在：{path}")


# ---------- 读取 ----------


def read_text_file(path):
    """读取 TXT 文件，兼容 UTF-8（含 BOM）和 GBK 系列编码。"""
    raw = path.read_bytes()
    for encoding in ("utf-8-sig", "gb18030"):
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            continue
    raise ValueError(f"无法识别 {path.name} 的编码，请先转换为 UTF-8")


def extract_pdf_text(pdf_path):
    """从 PDF 提取纯文字并清洗。"""
    reader = PdfReader(pdf_path)
    if reader.is_encrypted and reader.decrypt("") == 0:
        raise ValueError(f"{pdf_path.name} 已加密，请先解除密码保护")

    pages_text = []
    for i, page in enumerate(reader.pages, start=1):
        pages_text.append(page.extract_text() or "")

    text = "\n\n".join(pages_text)
    text = collapse_repeated_chars(text)
    text = remove_space_between_cjk(text)

    if not text.strip():
        raise ValueError(
            f"没有从 {pdf_path.name} 中提取到文字，可能是扫描版 PDF（图片），目前不支持 OCR"
        )
    return text


# ---------- 缓存 ----------


def _cache_path(pdf_path):
    return CACHE_DIR / f"{pdf_path.stem}.txt"


def _cache_is_fresh(pdf_path, cache_path):
    return (
        cache_path.exists() and cache_path.stat().st_mtime >= pdf_path.stat().st_mtime
    )


# ---------- 对外接口 ----------


def _load_one(source, force=False):
    """读取单个知识库文件，返回纯文本（逻辑与原 load_knowledge_base 相同）。"""
    suffix = source.suffix.lower()

    if suffix == ".txt":
        print(f"读取知识库：{source.name}")
        return read_text_file(source)

    cache_path = _cache_path(source)
    if not force and _cache_is_fresh(source, cache_path):
        return cache_path.read_text(encoding="utf-8")

    text = extract_pdf_text(source)
    CACHE_DIR.mkdir(exist_ok=True)
    cache_path.write_text(text, encoding="utf-8")
    return text


def load_knowledge_base(path, force=False):
    """读取知识库，返回 [(文件名, 文本), ...]。"""
    return [(f.name, _load_one(f, force)) for f in find_source_files(path)]
