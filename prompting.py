import ollama

from config import CHAT_MODEL


def build_prompt(question, relevant_chunks):
    context = "\n\n---\n\n".join(relevant_chunks)
    prompt = f"""请你根据下面提供的参考资料回答问题，回答时务必引用参考资料中的内容（只需要截取出与问题相关的部分，不需要完整引用）作为依据；如果问题超出了参考资料的范围，那么请你如实回答不知道，而不是编造。
    \n\n参考资料如下（不同片段间通过“---”隔开）：\n\n
    {context}
    \n\n问题如下：
    {question}
    """
    return prompt


def generate_answer(prompt):
    output = ollama.generate(model=CHAT_MODEL, prompt=prompt, stream=True, think=False)
    return output
