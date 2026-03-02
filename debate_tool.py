import argparse
import os
from dataclasses import dataclass


@dataclass
class DebateConfig:
    topic: str
    rounds: int
    gpt_model: str
    gemini_model: str
    max_tokens: int


class GPTClient:
    def __init__(self, api_key: str, model: str, max_tokens: int) -> None:
        from openai import OpenAI

        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.max_tokens = max_tokens

    def speak(self, prompt: str) -> str:
        response = self.client.responses.create(
            model=self.model,
            input=prompt,
            max_output_tokens=self.max_tokens,
        )
        return response.output_text.strip()


class GeminiClient:
    def __init__(self, api_key: str, model: str, max_tokens: int) -> None:
        import google.generativeai as genai

        self.genai = genai
        self.genai.configure(api_key=api_key)
        self.model = self.genai.GenerativeModel(model)
        self.max_tokens = max_tokens

    def speak(self, prompt: str) -> str:
        response = self.model.generate_content(
            prompt,
            generation_config=self.genai.types.GenerationConfig(
                max_output_tokens=self.max_tokens,
            ),
        )
        return (response.text or "").strip()


def build_prompt(topic: str, history: list[str], role_name: str, round_index: int) -> str:
    base = [
        f"你正在参加一场围绕以下主题的理性讨论：{topic}",
        f"当前发言角色：{role_name}，轮次：第 {round_index} 轮。",
        "请给出结构化回答：核心观点、理由、对对方观点的回应、建议。",
    ]
    if history:
        base.append("以下是已有讨论内容：")
        base.extend(history)
    return "\n".join(base)


def run_debate(config: DebateConfig) -> None:
    openai_key = os.getenv("OPENAI_API_KEY", "")
    gemini_key = os.getenv("GEMINI_API_KEY", "")

    if not openai_key:
        raise ValueError("缺少 OPENAI_API_KEY 环境变量。")
    if not gemini_key:
        raise ValueError("缺少 GEMINI_API_KEY 环境变量。")

    gpt = GPTClient(api_key=openai_key, model=config.gpt_model, max_tokens=config.max_tokens)
    gemini = GeminiClient(api_key=gemini_key, model=config.gemini_model, max_tokens=config.max_tokens)

    history: list[str] = []

    print(f"\n议题：{config.topic}")
    print(f"总轮数：{config.rounds}\n")

    for i in range(1, config.rounds + 1):
        gpt_prompt = build_prompt(config.topic, history, "GPT", i)
        gpt_reply = gpt.speak(gpt_prompt)
        history.append(f"[第{i}轮][GPT] {gpt_reply}")
        print(f"[第{i}轮][GPT]\n{gpt_reply}\n")

        gemini_prompt = build_prompt(config.topic, history, "Gemini", i)
        gemini_reply = gemini.speak(gemini_prompt)
        history.append(f"[第{i}轮][Gemini] {gemini_reply}")
        print(f"[第{i}轮][Gemini]\n{gemini_reply}\n")

    summary_prompt = (
        f"请作为主持人，基于以下关于“{config.topic}”的全部讨论，"
        "给出 1) 共识 2) 分歧 3) 可执行行动建议（3条）\n\n"
        + "\n".join(history)
    )
    summary = gpt.speak(summary_prompt)
    print("========== 主持人总结 ==========")
    print(summary)


def parse_args() -> DebateConfig:
    parser = argparse.ArgumentParser(description="让 GPT 与 Gemini 围绕一个问题进行多轮讨论。")
    parser.add_argument("topic", type=str, help="要讨论的问题")
    parser.add_argument("--rounds", type=int, default=3, help="讨论轮数，默认 3")
    parser.add_argument("--gpt-model", type=str, default="gpt-4o-mini", help="GPT 模型名")
    parser.add_argument("--gemini-model", type=str, default="gemini-1.5-flash", help="Gemini 模型名")
    parser.add_argument("--max-tokens", type=int, default=500, help="单次回复最大 token")
    args = parser.parse_args()

    return DebateConfig(
        topic=args.topic,
        rounds=args.rounds,
        gpt_model=args.gpt_model,
        gemini_model=args.gemini_model,
        max_tokens=args.max_tokens,
    )


if __name__ == "__main__":
    cfg = parse_args()
    run_debate(cfg)
