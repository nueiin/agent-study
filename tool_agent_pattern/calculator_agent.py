"""
도구 1개짜리 에이전트 — 계산기
"""
import os
import sys

try:
    from anthropic import Anthropic
except ImportError:
    sys.exit("터미널에서 'pip install anthropic' 를 먼저 실행하세요.")

if not os.environ.get("ANTHROPIC_API_KEY"):
    sys.exit("ANTHROPIC_API_KEY 환경변수가 없습니다.")

client = Anthropic()


# --- 도구 정의: AI에게 "이런 도구가 있다"고 알려주는 메뉴판 ---
tools = [
    {
        "name": "multiply",
        "description": "두 수의 곱셈을 정확하게 계산한다. 큰 수 곱하기에 사용할 것.",
        "input_schema": {
            "type": "object",
            "properties": {
                "a": {"type": "number", "description": "첫 번째 수"},
                "b": {"type": "number", "description": "두 번째 수"},
            },
            "required": ["a", "b"],
        },
    },
    {
        "name": "add",
        "description": "두 수의 덧셈을 정확하게 계산한다. 큰 수 더하기에 사용할 것.",
        "input_schema": {
            "type": "object",
            "properties": {
                "a": {"type": "number", "description": "첫 번째 수"},
                "b": {"type": "number", "description": "두 번째 수"},
            },
            "required": ["a", "b"],
        },
    },
]

def multiply(a, b):
    """두 수를 곱한다."""
    result = a * b
    print(f"  [도구 실행] {a} × {b} = {result}")
    return result


def add(a, b):
    """두 수를 더한다."""
    result = a + b
    print(f"  [도구 실행] {a} + {b} = {result}")
    return result


# --- 에이전트 루프 ---
def run_agent(question):
    # 대화 기록. AI에게 매번 '전체 대화'를 보내야 한다 (LLM은 기억이 없으니까)
    messages = [{"role": "user", "content": question}]

    while True:  # 도구가 필요 없어질 때까지 반복
        response = client.messages.create(
            model="claude-haiku-4-5",
            max_tokens=1024,
            tools=tools,                 # 조각 2에서 만든 메뉴판
            messages=messages,
        )

        # AI의 응답을 대화 기록에 추가
        messages.append({"role": "assistant", "content": response.content})

        # AI가 도구를 원하는가? stop_reason으로 판단
        if response.stop_reason != "tool_use":
            # 도구 안 씀 = 최종 답변. 루프 종료.
            for block in response.content:
                if block.type == "text":
                    return block.text

        # 여기 왔다 = AI가 도구를 쓰겠다는 것. 요청을 처리한다.
        tool_results = []
        for block in response.content:
            if block.type == "tool_use":
                print(f"  [AI 요청] {block.name}({block.input})")

                # AI가 부른 도구 이름(block.name)을 보고 맞는 함수 선택
                if block.name == "multiply":
                    output = multiply(block.input["a"], block.input["b"])
                elif block.name == "add":
                    output = add(block.input["a"], block.input["b"])
                else:
                    output = f"알 수 없는 도구: {block.name}"

                # 결과를 AI에게 돌려줄 형식으로 포장
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": str(output),
                })

        # 도구 결과들을 대화에 추가 → 다음 루프에서 AI가 이걸 보고 이어감
        messages.append({"role": "user", "content": tool_results})


# 실행
answer = run_agent("73856 × 91423 을 계산하고, 거기에 500000 을 더하면?")
print("\n최종 답변:", answer)