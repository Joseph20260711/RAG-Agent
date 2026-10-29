# RAG-Agent

一个基于检索增强生成（RAG）的本地智能体项目。

## 功能概览

- 读取 PDF 文档并提取文本
- 文本切分、向量化与相似度检索
- 基于检索结果构造提示词，调用本地大模型生成回答

## 项目结构

```
RAG-Agent/
├── main.py            # 程序入口
├── chunking.py        # 文本切分
├── config.py          # 读取配置
├── embedding.py       # 文本向量化
├── logging_utils.py   # 日志工具
├── preprocess.py      # 文本预处理
├── prompting.py       # 提示词构造
├── retrieving.py      # 检索
├── config.toml        # 配置文件
├── requirements.txt   # Python 依赖
└── data               # 知识库文件夹
```

## 环境要求

- Python 3.12（在 3.12.15 上测试通过）
- [Ollama](https://ollama.com)：本地模型运行服务，需要先安装并保持在后台运行

## 快速开始

### 1. 获取代码

```bash
git clone https://github.com/Joseph20260711/RAG-Agent.git
cd RAG-Agent
```

### 2. 创建虚拟环境并安装依赖

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. 准备模型

确保 Ollama 服务已启动，然后拉取所需模型：

```bash
ollama pull qwen3.5:9b        # 对话模型
ollama pull nomic-embed-text  # 向量化模型
```

### 4. 准备知识库

将知识库文件放入 `data` 文件夹。

> 注意：目前仅支持单个知识库文件。

### 5. 运行

```bash
python main.py
```

## 配置

目前配置项直接写在源码中，修改后重新运行即可生效：

| 配置项 | 当前值 | 名称 |
| --- | --- | --- |
| 对话模型 | `qwen3.5:9b` | `chat` |
| 向量化模型 | `nomic-embed-text` | `embedding` |
| 切分长度 | 500 字符 | `chunk_size` |
| 重叠长度 | 100 字符 | `chunk_overlap` |
| 检索条数 | 10 | `top_k` |

## 工作流程

1. **文档读取**：PDF 由 `pdf2txt.py` 调用 pypdf 提取文本；TXT 文件直接读取。
2. **文本切分**：
   - 按字符数切分，每个片段约 500 个字符
   - 相邻片段重叠 100 个字符，避免语义在片段边界处断裂
   - 切分后向两端延伸至自然断点，保证片段语义完整
3. **向量化**：用 Ollama 的 `nomic-embed-text` 模型把片段转为向量。
4. **检索**：用 numpy 计算查询与片段的相似度，取前 10 条。
5. **生成**：将检索到的片段与问题拼成提示词，交给 `qwen3.5:9b` 生成回答。

## 已知限制

- 使用 9B 规模的本地模型，复杂推理与长上下文能力有限
- 检索流程由代码固定执行，而不是由模型自主决定是否检索

## 后续计划

- [ ] 将检索改为模型可调用的工具，由模型自主决定是否检索

## 常见问题

**运行时报连接错误？**

先确认 Ollama 服务正在运行，并且模型已用 `ollama pull` 拉取。

**提示找不到模块？**

确认已激活虚拟环境（命令行前应有 `(.venv)`），并执行过 `pip install -r requirements.txt`。