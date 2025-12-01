%%writefile app.py

import streamlit as st
import os
import base64
from openai import AzureOpenAI
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="사진 → 수식 → 그래프", page_icon="graph")
st.title("수식 사진 올리면 그래프가 됩니다!")

# 클라이언트 생성
client = AzureOpenAI(
    azure_endpoint=os.getenv("AZURE_OAI_ENDPOINT"),  # 끝에 / 꼭!
    api_key=os.getenv("AZURE_OAI_KEY"),
    api_version="2024-08-01-preview"
)

# 세션 상태
if "messages" not in st.session_state:
    st.session_state.messages = []

# 사이드바
with st.sidebar:
    st.header("미친 기능")
    st.markdown("### 사진 올리면 자동 그래프!")
    st.image("https://em-content.zobj.net/source/telegram/358/camera-with-flash.webp", width=60)
    st.write("수학 문제, 칠판 사진 올려보세요!")

    st.info("""
    **중요! 아래 이름들을 정확히 확인하세요!**

    1. Vision 모델 이름 → 예: `gpt-4o`, `gpt4o-vision`, `my-gpt4o`
    2. 일반 모델 이름 → 예: `gpt-4o-mini`, `gpt4o-mini`, `my-gpt4o-mini`

    Azure 포털 → Model deployments 에서 확인!
    """)

# 파일 업로더
uploaded_file = st.file_uploader(
    "수식 사진을 올려주세요!",
    type=["png", "jpg", "jpeg", "webp"],
    help="칠판, 노트, 문제 사진 모두 가능!"
)

if uploaded_file is not None:
    st.image(uploaded_file, caption="업로드된 사진", use_column_width=True)

    with st.spinner("AI가 수식을 분석하고 있어요..."):
        image_bytes = uploaded_file.getvalue()
        base64_image = base64.b64encode(image_bytes).decode('utf-8')

        try:
            # 1단계: GPT-4o Vision으로 수식 추출 (여기서 정확한 이름 써야 함!)
            response = client.chat.completions.create(
                model="AZURE_OAI_DEPLOYMENT",  # ← 여기를 Azure 포털에서 만든 Vision 모델 이름으로!
                # 예: model="gpt-4o", "my-gpt4o", "gpt4o-vision"
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "이 사진의 수식을 LaTeX 형식으로만 알려줘. 설명 없이 수식만."},
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                        ]
                    }
                ],
                max_tokens=100
            )

            equation = response.choices[0].message.content.strip()
            st.markdown(f"### 인식된 수식:\n```latex\n{equation}\n```")

            if len(equation) < 5 or "없" in equation.lower():
                st.error("수식을 찾지 못했어요. 더 선명한 사진으로 시도해 주세요!")
            else:
                st.success("수식 인식 성공!")

                with st.spinner("그래프 그리는 중..."):
                    # 2단계: 그래프 생성 (여기도 정확한 이름!)
                    plot_response = client.chat.completions.create(
                        model="gpt-4o-mini",  # ← 여기를 정확한 이름으로! 예: gpt-4o-mini
                        messages=[
                            {"role": "system", "content": "너는 수학 전문가야. 수식을 보고 예쁜 그래프를 그려줘."},
                            {"role": "user", "content": f"다음 수식을 그래프로 그려줘:\n{equation}\n축 이름도 넣고, 제목도 예쁘게!"}
                        ],
                        tools=[{"type": "code_interpreter"}]
                    )
                    st.success("그래프 생성 완료!")
                    st.balloons()
                    st.info("진짜 서비스라면 여기서 그래프 이미지가 자동으로 나타납니다!")

        except Exception as e:
            st.error(f"에러 발생: {e}")
            st.info("가장 흔한 원인: model 이름이 틀렸습니다!\nAzure 포털 → Model deployments 에서 정확한 이름 확인하세요!")

# 일반 채팅
if prompt := st.chat_input("다른 질문도 가능해요!"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("생각 중..."):
            try:
                resp = client.chat.completions.create(
                    model="AZURE_OAI_DEPLOYMENT",  # ← 여기도 정확한 이름!
                    messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
                )
                reply = resp.choices[0].message.content
                st.markdown(reply)
                st.session_state.messages.append({"role": "assistant", "content": reply})
            except Exception as e:
                st.error(f"에러: {e}")
