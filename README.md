# GPT + Gemini 讨论工具（MVP）

这是一个命令行工具：给定一个问题后，让 **GPT** 和 **Gemini** 轮流讨论若干轮，并在最后输出“主持人总结”。

## 功能

- 同时调用 OpenAI 与 Gemini。
- 支持指定讨论轮数。
- 每一轮会把上一轮双方观点作为上下文。
- 最后由 GPT 做一段综合总结（可按需改成 Gemini）。

## 准备

1. Python 3.10+
2. 安装依赖：

```bash
pip install -r requirements.txt
```

3. 设置环境变量：

```bash
export OPENAI_API_KEY="你的_openai_key"
export GEMINI_API_KEY="你的_gemini_key"
```

## 使用

```bash
python debate_tool.py "AI 是否应该完全自动化客服系统？" --rounds 3
```

可选参数：

- `--gpt-model`（默认：`gpt-4o-mini`）
- `--gemini-model`（默认：`gemini-1.5-flash`）
- `--max-tokens`（默认：500）

## 设计思路（简版）

- 把“问题 + 历史发言”拼成 prompt。
- GPT 与 Gemini 交替发言，避免信息孤岛。
- 每轮输出后立刻打印，便于实时观察。
- 结束后做汇总，得到可执行结论。

## 后续可以扩展

- Web UI（Streamlit / Next.js）
- 多角色（支持 Claude、Qwen 等）
- 评分器（自动打分论证质量）
- 会话持久化（保存讨论历史）
