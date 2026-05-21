"""
평가자-최적화자 — 이메일 제목 줄 다듬기
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


# --- 조각 1: 생성자 — 이메일 제목을 쓴다 ---
def generate(brief, feedback=""):
    """
    brief    : 어떤 이메일인지 설명
    feedback : 평가자가 준 지적 (처음엔 없음)
    """
    prompt = f"다음 이메일의 제목 줄을 1개만 써 줘. 제목 줄만 출력하고 다른 말은 하지 마.\n\n[이메일 설명]\n{brief}"

    # 피드백이 있으면 프롬프트에 덧붙인다
    if feedback:
        prompt += f"\n\n[이전 제목에 대한 피드백 — 반드시 반영할 것]\n{feedback}"

    message = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=200,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text.strip()


# --- 조각 2: 평가자 — 제목을 검사한다 ---
def evaluate(brief, subject):
    """
    제목을 검사해서 합격(PASS) / 불합격(FAIL) + 이유를 돌려준다.
    """
    prompt = f"""너는 까다로운 이메일 마케팅 전문가야.
다음 이메일 제목 줄을 아래 3가지 기준으로 평가해.

평가 기준:
1. 길이 — 모바일에서 안 잘리게 40자 이내인가
2. 후킹 — 진부하지 않고 열어보고 싶게 만드는가
3. 명확성 — 핵심 혜택이 앞쪽에 잘 드러나는가

3가지를 모두 만족할 때만 PASS. 하나라도 부족하면 FAIL.

응답은 반드시 다음 형식으로만:
판정: PASS 또는 FAIL
이유: (부족한 점을 구체적으로. 어떻게 고치면 좋을지까지)

[이메일 설명]
{brief}

[검사할 제목]
{subject}"""

    message = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=400,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text.strip()


# --- 조각 3: 루프 — 합격(PASS)할 때까지 생성↔평가 반복 ---
def run(brief, max_rounds=4):
    feedback = ""  # 처음엔 피드백 없음

    for round_num in range(1, max_rounds + 1):
        print(f"\n{'=' * 50}")
        print(f"  라운드 {round_num}")
        print(f"{'=' * 50}")

        # 1) 생성 — 피드백이 있으면 반영해서 쓴다
        subject = generate(brief, feedback)
        print(f"[생성된 제목] {subject}")

        # 2) 평가
        review = evaluate(brief, subject)
        print(f"[평가]\n{review}")

        # 3) 판정 확인 — PASS면 루프 종료
        if "PASS" in review:
            print(f"\n✅ 라운드 {round_num}에서 합격! 최종 제목: {subject}")
            return subject

        # FAIL이면 → 이번 평가를 다음 라운드의 피드백으로 넘긴다
        feedback = review

    # max_rounds 다 돌아도 PASS 안 나옴
    print(f"\n⚠️ {max_rounds}라운드 안에 합격 못 함. 마지막 제목: {subject}")
    return subject


# --- 실행 ---
brief = "신규 가입자에게 보내는 환영 이메일. 첫 구매 시 20% 할인 쿠폰을 준다."
run(brief)