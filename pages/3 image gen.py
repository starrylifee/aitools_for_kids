import streamlit as st
from openai import OpenAI
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json

# 페이지 설정 - 아이콘과 제목 설정
st.set_page_config(
    page_title="학생용 교육 도구 홈",  # 브라우저 탭에 표시될 제목
    page_icon="🤖",  # 브라우저 탭에 표시될 아이콘 (이모지 또는 이미지 파일 경로)
)

# Streamlit의 배경색 변경
background_color = "#C5E1A5"  # 파스텔 그린

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
worksheet = spreadsheet.worksheet("시트3")  # 시트3에서 데이터를 가져옴

# 학생용 UI
st.header('🎨 학생용: 이미지 생성 도구')

# 사용 설명 추가
st.markdown("""
    **안내:** 이 도구를 사용하여 교사가 제공한 프롬프트에 따라 이미지를 생성할 수 있습니다.
    1. **이름 입력**: 학생의 이름을 입력하세요.
    2. **코드 입력**: 수업과 관련된 코드를 입력하세요.
    3. **프롬프트 가져오기**: 코드를 입력한 후 '프롬프트 가져오기' 버튼을 클릭하면, 교사가 설정한 프롬프트를 불러옵니다.
    4. **주제 및 형용사 선택**: 이미지의 스타일이나 느낌을 나타내는 주제와 형용사를 선택하세요.
    5. **이미지 생성**: 교사 프롬프트와 선택한 형용사를 바탕으로 이미지를 생성합니다.
    6. **결과 확인**: 생성된 이미지를 확인하고 필요시 다운로드하세요.
""")

# 이름 입력
student_name = st.text_input("👤 이름 입력 (필수)", key="student_name")

# 코드 입력
setting_name = st.text_input("🔑 코드 입력")

if st.button("📄 프롬프트 가져오기", key="get_prompt"):
    if not student_name:
        st.error("이름을 입력해야 합니다.")
    else:
        with st.spinner("🔍 프롬프트를 불러오는 중..."):
            # Google Sheets에서 코드에 해당하는 프롬프트 검색
            data = worksheet.get_all_records()
            st.session_state.prompt = None
            for row in data:
                if row.get('setting_name') == setting_name:
                    st.session_state.prompt = row.get('prompt')
                    break

if "prompt" in st.session_state and st.session_state.prompt:
    st.success("✅ 프롬프트를 성공적으로 불러왔습니다.")
    st.write("**프롬프트:** " + st.session_state.prompt)

    # 주제 및 형용사 선택 옵션 제공
    with st.expander("주제 및 형용사 선택"):

        col1, col2 = st.columns(2)

        with col1:
            selected_color = st.radio("🎨 색감 선택", ["선택하지 않음"] + [
                "밝은", "어두운", "선명한", "부드러운", "따뜻한", 
                "차가운", "다채로운", "흑백의", "파스텔톤의", "무채색의"
            ])
            selected_mood = st.radio("🌅 분위기 선택", ["선택하지 않음"] + [
                "몽환적인", "현실적인", "우아한", "고요한", "활기찬", 
                "긴장감 있는", "로맨틱한", "공포스러운", "신비로운", "평화로운"
            ])

        with col2:
            selected_style = st.radio("🖌️ 스타일 선택", ["선택하지 않음"] + [
                "미니멀한", "복잡한", "빈티지한", "모던한", "고전적인", 
                "미래적인", "자연주의적인", "기하학적인", "추상적인", "대담한"
            ])
            selected_texture = st.radio("🧶 텍스처 선택", ["선택하지 않음"] + [
                "매끄러운", "거친", "부드러운", "뾰족한", "질감이 느껴지는", 
                "광택 있는", "매트한", "무광의", "광택이 있는", "플러시한"
            ])
            selected_emotion = st.radio("😊 감정 표현 선택", ["선택하지 않음"] + [
                "즐거운", "슬픈", "분노한", "평온한", "감동적인", 
                "따뜻한", "외로운", "흥미로운", "짜릿한", "사려 깊은"
            ])

    # 선택된 "선택하지 않음"을 제외한 주제 및 형용사 결합
    combined_concept = " ".join([option for option in [selected_color, selected_mood, selected_style, selected_texture, selected_emotion] if option != "선택하지 않음"])

    if st.button("🖼️ 이미지 생성", key="generate_image"):
        if combined_concept:
            with st.spinner("🖼️ 이미지를 생성하는 중..."):
                combined_prompt = f"{st.session_state.prompt} {combined_concept}"
                response = client.images.generate(
                    model="dall-e-3",
                    prompt=combined_prompt,
                    size="1024x1024",
                    quality="standard",
                    n=1,
                )

                image_url = response.data[0].url
                st.session_state.image_url = image_url
                st.image(image_url, caption="Generated Image", use_column_width=True)
                st.success("✅ 이미지가 성공적으로 생성되었습니다!")
                st.download_button(label="💾 이미지 다운로드", data=image_url, file_name="generated_image.png")
                
                # AI 생성 후 이메일 발송
                teacher_email = st.secrets["email"]["teacher_email"]
                if teacher_email:
                    try:
                        import smtplib
                        from email.mime.multipart import MIMEMultipart
                        from email.mime.text import MIMEText

                        msg = MIMEMultipart()
                        msg['From'] = st.secrets["email"]["address"]
                        msg['To'] = teacher_email
                        msg['Subject'] = f"학생의 이미지 생성 결과 제출 - {setting_name}"

                        body = (
                            f"학생 이름: {student_name}\n\n"  # 이름을 이메일에 포함
                            f"프롬프트:\n{st.session_state.prompt}\n\n"
                            f"선택된 형용사:\n{combined_concept}\n\n"
                            f"이미지 URL:\n{image_url}\n"
                        )
                        msg.attach(MIMEText(body, 'plain'))

                        server = smtplib.SMTP('smtp.gmail.com', 587)
                        server.starttls()
                        server.login(st.secrets["email"]["address"], st.secrets["email"]["password"])
                        text = msg.as_string()
                        server.sendmail(st.secrets["email"]["address"], teacher_email, text)
                        server.quit()

                        st.success("✅ 생성된 이미지 결과가 성공적으로 전송되었습니다!")
                    except Exception as e:
                        st.error(f"❌ 이메일 전송 중 오류가 발생했습니다: {str(e)}")
                else:
                    st.error("❌ 교사의 이메일 주소가 제공되지 않았습니다.")
        else:
            st.error("⚠️ 최소한 하나의 형용사를 선택하세요.")
else:
    st.info("프롬프트를 업로드하세요.")
