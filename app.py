import streamlit as st
import os
from openai import AzureOpenAI
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="안심이", page_icon="🛡️")

client = AzureOpenAI(
    api_key=os.getenv("AZURE_OAI_KEY"),
    api_version="2024-05-01-preview",
    azure_endpoint=os.getenv("AZURE_OAI_ENDPOINT")
)

# ==================== 시스템 프롬프트 (최신판 + 더 따뜻하게) ====================
SYSTEM_PROMPT = """
너는 '안심이'라는 이름의 스토킹·데이트폭력 전문 상담 보조 AI야.
모든 판단은 오직 아래 공식 자료만 근거로 해:

- 「스토킹범죄의 처벌 등에 관한 법률」(2023.10.19 시행)
- 여성가족부 공식 데이트폭력 피해판단 체크리스트
- 경찰청 스토킹사범 수사실무 매뉴얼(2024 개정)

말투는 끝까지 따뜻하고, 차분하고, 공감적이어야 해.
절대 “이건 아닙니다”라고 단정하지 말고, “해당할 가능성이 있어요”라고만 말해.
위험도는 저·중·고 3단계로만 나눠서 알려줘.

마지막엔 항상 아래 3가지를 안내해:
1. 여성긴급전화 1366 (24시간, 익명 가능)
2. 스토킹 피해 상담 1577-1366
3. 긴급 상황이면 지금 바로 112

첫인사: "안녕, 여기는 안심이야. 무슨 일이 있었는지 편하게 말해줄래? 내가 끝까지 들어줄게."
"""

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "assistant", "content": "안녕, 여기는 **안심이**야 🛡️\n무슨 일이 있었는지 편하게 말해줄래? 내가 끝까지 들어줄게."}
    ]

# ==================== UI (따뜻한 분위기) ====================
st.title("🛡️ 안심이")
st.caption("스토킹·데이트폭력 상황이 의심된다면, 바로 도와줄게요. 언제든 말해줘도 돼.")

# 과거 대화 표시
for msg in st.session_state.messages[1:]:
    if msg["role"] != "system":
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

# 입력창
if prompt := st.chat_input("지금 어떤 일이 있었는지 말해줄래? (자세할수록 더 정확히 도와줄게)"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("잠시만 기다려줘..."):
            response = client.chat.completions.create(
                model="gpt-4o-mini-032",  # 너가 쓰는 deployment 이름으로 변경
                messages=st.session_state.messages,
                temperature=0.2,    # 더 정확하고 일관성 있게
                max_tokens=1200
            )
            reply = response.choices[0].message.content
            st.markdown(reply)
            st.session_state.messages.append({"role": "assistant", "content": reply})

# 사이드바에 도움말
with st.sidebar:
    st.markdown("### ⚡ 언제든 전화해도 돼")
    st.markdown("• **1366** 여성긴급전화 (24시간)\n• **1577-1366** 스토킹 상담\n• **112** 긴급 상황")
    st.markdown("---")
    st.markdown("우리는 사용자의 개인정보와 상담 내용에 대한 익명성을 보장합니다. 💙")

