import streamlit as st
from openai import OpenAI
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# 페이지 설정 - 아이콘과 제목 설정
st.set_page_config(
    page_title="학생용 교육 도구 홈",  # 브라우저 탭에 표시될 제목
    page_icon="🤖",  # 브라우저 탭에 표시될 아이콘 (이모지 또는 이미지 파일 경로)
)

# Streamlit의 배경색 변경
background_color = "#E0F7FA"  # 파스텔 블루

# 배경색 변경을 위한 CSS
page_bg_css = f"""
<style>
    .stApp {{
        background-color: {background_color};
    }}
</style>
"""

# Streamlit의 기본 메뉴와 푸터 숨기기
hide_menu_style = """
    <style>
    #MainMenu {visibility: hidden; }
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    <script>
    document.addEventListener("DOMContentLoaded", function() {
        var mainMenu = document.getElementById('MainMenu');
        if (mainMenu) {
            mainMenu.style.display = 'none';
        }
        var footer = document.getElementsByTagName('footer')[0];
        if (footer) {
            footer.style.display = 'none';
        }
        var header = document.getElementsByTagName('header')[0];
        if (header) {
            header.style.display = 'none';
        }
    });
    </script>
"""

# Streamlit에서 HTML 및 CSS 적용
st.markdown(hide_menu_style, unsafe_allow_html=True)
st.markdown(page_bg_css, unsafe_allow_html=True)

# OpenAI API 클라이언트 초기화
client = OpenAI(api_key=st.secrets["api"]["keys"][0])  # 첫 번째 API 키 사용

# Google Sheets 인증 설정
credentials_dict = json.loads(st.secrets["gcp"]["credentials"])
credentials = ServiceAccountCredentials.from_json_keyfile_dict(credentials_dict, [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/spreadsheets"
])
gc = gspread.authorize(credentials)

# 스프레드시트 열기
spreadsheet = gc.open(st.secrets["google"]["spreadsheet_name"])
worksheet = spreadsheet.worksheet("시트2")  # 시트2에서 데이터를 가져옴

# 학생용 UI
st.header('🎓 학생용: 인공지능 대화 생성 도구')

# 사용 설명 추가
st.markdown("""
    **안내:** 이 도구를 사용하여 AI가 생성한 프롬프트에 따라 다양한 교육 활동을 수행할 수 있습니다.
    1. **코드 입력**: 수업과 관련된 코드를 입력하세요.
    2. **프롬프트 가져오기**: 코드를 입력한 후 '프롬프트 가져오기' 버튼을 클릭하면, 관련된 프롬프트를 불러옵니다.
    3. **활동 입력**: 제공된 프롬프트를 기반으로 자신의 활동을 작성하세요.
    4. **AI 대화 생성**: 작성한 활동을 바탕으로 AI가 관련된 대화를 생성합니다.
    5. **결과 확인**: AI가 생성한 대화를 확인하고 필요시 저장하세요.
""")

# 코드 입력
setting_name = st.text_input("🔑 코드 입력")

if st.button("📄 프롬프트 가져오기", key="get_prompt"):
    with st.spinner("🔍 프롬프트를 불러오는 중..."):
        # Google Sheets에서 코드에 해당하는 프롬프트 검색
        data = worksheet.get_all_records()
        st.session_state.prompt = None
        st.session_state.teacher_email = None  # 교사 이메일 초기화
        for row in data:
            if row.get('setting_name') == setting_name:
                st.session_state.prompt = row.get('prompt')
                st.session_state.teacher_email = row.get('Email')  # 교사 이메일 저장
                break

if "prompt" in st.session_state and st.session_state.prompt:
    st.success("✅ 프롬프트를 성공적으로 불러왔습니다.")
    st.write("**프롬프트:** " + st.session_state.prompt)

    # 학생 활동 입력
    student_answer = st.text_area("📝 활동 입력", value=st.session_state.get("student_answer", ""))

    if st.button("🤖 AI 대화 생성", key="generate_answer"):
        if student_answer:
            with st.spinner("💬 AI가 대화를 생성하는 중..."):
                st.session_state.student_answer = student_answer  # 학생 활동을 세션에 저장
                response = client.chat.completions.create(
                    model="gpt-4o-mini",  # 새로운 모델명 사용
                    messages=[
                        {"role": "system", "content": st.session_state.prompt},
                        {"role": "user", "content": student_answer}
                    ]
                )

                st.session_state.ai_answer = response.choices[0].message.content.strip()
                st.write("💡 **AI 생성 대화:** " + st.session_state.ai_answer)

                # AI 생성 후 이메일 발송
                teacher_email = st.session_state.teacher_email
                if teacher_email:
                    try:
                        msg = MIMEMultipart()
                        msg['From'] = st.secrets["email"]["address"]
                        msg['To'] = teacher_email
                        msg['Subject'] = f"학생의 활동 제출 - {setting_name}"

                        body = (
                            f"학생 활동 내용:\n{student_answer}\n\n"
                            f"AI 생성 대화:\n{st.session_state.ai_answer}"
                        )
                        msg.attach(MIMEText(body, 'plain'))

                        server = smtplib.SMTP('smtp.gmail.com', 587)
                        server.starttls()
                        server.login(st.secrets["email"]["address"], st.secrets["email"]["password"])
                        text = msg.as_string()
                        server.sendmail(st.secrets["email"]["address"], teacher_email, text)
                        server.quit()

                        st.success("✅ AI 생성 대화가 성공적으로 전송되었습니다!")
                    except Exception as e:
                        st.error(f"❌ 이메일 전송 중 오류가 발생했습니다: {str(e)}")
                else:
                    st.error("❌ 교사의 이메일 주소가 제공되지 않았습니다.")
        else:
            st.error("⚠️ 활동을 입력하세요.")
else:
    st.info("프롬프트를 업로드하세요.")
