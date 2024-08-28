import streamlit as st
import openai
import io

# OpenAI API 키 입력 필드
st.title("한국어 ↔ 베트남어 번역 및 문법 검사 서비스")

api_key_input = st.text_input("OpenAI API 키를 입력하세요", type="password")

# st.session_state를 사용해 대화 기록 관리
if 'history' not in st.session_state:
    st.session_state['history'] = []

# 사용자가 API 키를 입력했는지 확인
if api_key_input:
    openai.api_key = api_key_input

    # 텍스트 입력 필드
    input_text = st.text_area("번역할 한국어 또는 베트남어 텍스트를 입력하세요", height=150)

    # 세 개의 버튼을 가로로 나란히 배치하기 위해 columns 사용
    col1, col2, col3 = st.columns([1, 1, 1])

    # 번역 버튼, 대화 기록 초기화 버튼을 가로로 나열
    with col1:
        translate_btn = st.button("번역하기")
    with col2:
        reset_btn = st.button("대화 기록 초기화")

    # 번역 버튼 기능
    if translate_btn:
        if input_text:
            try:
                # GPT-3.5-turbo 모델을 사용한 번역 요청 (베트남어 ↔ 한국어)
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "Translate the following text between Korean and Vietnamese."},
                        {"role": "user", "content": input_text}
                    ]
                )

                # 번역 결과 저장 및 표시
                translation = response.choices[0].message['content']
                st.session_state['history'].append({"input": input_text, "output": translation})

                # 번역 결과 출력 (박스 스타일 추가)
                st.write("### 번역된 결과:")
                st.markdown(f"<div style='background-color:#F0F0F0; padding:10px; border-radius:10px; font-size: 20px;'>{translation}</div>", unsafe_allow_html=True)

                # 주요 단어 설명 및 유사 문장 (한국어와 베트남어로 제공)
                st.write("### 추가 정보:")
                explanation_response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "For the following translated text, provide explanations for key terms in both Korean and Vietnamese, and offer similar example sentences in both languages."},
                        {"role": "user", "content": translation}
                    ]
                )
                explanation = explanation_response.choices[0].message['content']
                
                # 설명 박스화
                st.markdown(f"<div style='background-color:#E9F7EF; padding:10px; border-radius:10px;'>{explanation}</div>", unsafe_allow_html=True)

                # 문법 오류 검사 및 문장 다듬기 기능 추가
                st.write("### 문법 오류 검사 및 문장 다듬기:")
                grammar_check_response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "Check the following text for grammatical errors and suggest improvements."},
                        {"role": "user", "content": input_text}
                    ]
                )
                grammar_check = grammar_check_response.choices[0].message['content']
                
                # 문법 오류 결과 박스화
                st.markdown(f"<div style='background-color:#FFEFD5; padding:10px; border-radius:10px;'>{grammar_check}</div>", unsafe_allow_html=True)
                
                # 결과를 history에 저장
                st.session_state['history'][-1]['explanation'] = explanation
                st.session_state['history'][-1]['grammar_check'] = grammar_check

            except openai.error.AuthenticationError:
                st.error("API 키가 올바르지 않습니다. 다시 확인해 주세요.")
        else:
            st.warning("번역할 텍스트를 입력하세요.")

    # 대화 기록 초기화 버튼 기능
    if reset_btn:
        st.session_state['history'] = []

    # 대화 기록을 문서로 저장하고 다운로드 버튼 기능
    if st.session_state['history']:
        history_str = ""
        for idx, entry in enumerate(st.session_state['history']):
            history_str += f"대화 {idx+1}:\n입력: {entry['input']}\n번역: {entry['output']}\n"
            history_str += f"설명: {entry.get('explanation', '없음')}\n"
            history_str += f"문법 오류 검사 및 문장 다듬기: {entry.get('grammar_check', '없음')}\n"
            history_str += "\n" + ("-"*50) + "\n"
        
        # 대화 기록을 문서화하여 다운로드 버튼 생성
        with col3:
            st.download_button(
                label="대화 기록 다운로드",
                data=io.StringIO(history_str).getvalue(),
                file_name="translation_history.txt",
                mime="text/plain"
            )

    # 대화 기록 표시
    if st.session_state['history']:
        st.write("## 대화 기록")
        for idx, entry in enumerate(st.session_state['history']):
            st.write(f"**{idx+1}. 입력:** {entry['input']}")
            st.markdown(f"<div style='background-color:#F9F9F9; padding:10px; border-radius:10px;'>{entry['output']}</div>", unsafe_allow_html=True)
            st.write(f"**설명:** {entry.get('explanation', '없음')}")
            st.write(f"**문법 오류 검사 및 문장 다듬기:** {entry.get('grammar_check', '없음')}")
            st.write("---")

else:
    st.warning("API 키를 입력하세요.")
