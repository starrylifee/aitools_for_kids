import streamlit as st
import google.generativeai as genai
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json
import pathlib
import toml
from PIL import Image, UnidentifiedImageError
import io

# Streamlit의 기본 메뉴와 푸터 숨기기
hide_github_icon = """
    <style>
    .css-1jc7ptx, .e1ewe7hr3, .viewerBadge_container__1QSob,
    .styles_viewerBadge__1yB5_, .viewerBadge_link__1S137,
    .viewerBadge_text__1JaDK{ display: none; }
    #MainMenu{ visibility: hidden; }
    footer { visibility: hidden; }
    header { visibility: hidden; }
    </style>
"""
st.markdown(hide_github_icon, unsafe_allow_html=True)

# secrets.toml 파일 경로
secrets_path = pathlib.Path(__file__).parent.parent / ".streamlit/secrets.toml"

# secrets.toml 파일 읽기
with open(secrets_path, "r") as f:
    secrets = toml.load(f)

# Gemini API 키 설정
gemini_api_key1 = secrets["google"]["gemini_api_key1"]
genai.configure(api_key=gemini_api_key1)

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
worksheet = spreadsheet.sheet1

# 학생용 UI
st.header('🎓 학생용: AI 교육 활동 도구')

st.markdown("""
    **안내:** 이 도구를 사용하여 AI가 생성한 프롬프트에 따라 다양한 교육 활동을 수행할 수 있습니다.
    1. **활동 코드 입력**: 교사가 제공한 활동 코드를 입력하세요.
    2. **프롬프트 가져오기**: 활동 코드에 해당하는 프롬프트를 불러옵니다.
    3. **이미지 업로드**: 교육 활동에 사용할 이미지를 업로드하거나 카메라로 촬영하세요.
    4. **AI 활동 수행**: AI가 제공된 프롬프트와 이미지를 바탕으로 창의적인 교육 활동을 도와줍니다.
""")

# 활동 코드 입력
setting_name = st.text_input("🔑 활동 코드 입력")

if st.button("📄 프롬프트 가져오기", key="get_prompt"):
    with st.spinner('🔍 프롬프트를 불러오는 중입니다...'):
        # Google Sheets에서 활동 코드에 해당하는 프롬프트 검색
        data = worksheet.get_all_records()
        st.session_state.prompt = None
        for row in data:
            if row.get('setting_name') == setting_name:
                st.session_state.prompt = row.get('prompt')
                break

if "prompt" in st.session_state and st.session_state.prompt:
    st.success("✅ 프롬프트를 성공적으로 불러왔습니다.")
    st.write("**프롬프트:** " + st.session_state.prompt)

    # 이미지 업로드 또는 카메라 촬영
    st.write("📸 이미지를 업로드하거나 카메라로 촬영하여 프롬프트를 처리하세요.")
    image = st.file_uploader("이미지 업로드", type=["jpg", "jpeg", "png"])

    if image:
        st.image(image, caption='선택된 이미지', use_column_width=True)

        try:
            with st.spinner('🧠 AI가 이미지를 분석하여 창의적인 교육 활동을 도와줍니다...'):
                # 이미지 바이트 문자열로 변환
                img_bytes = image.read()

                # bytes 타입의 이미지 데이터를 PIL.Image.Image 객체로 변환
                img = Image.open(io.BytesIO(img_bytes))

                model = genai.GenerativeModel('gemini-1.5-flash')

                # Generate content
                response = model.generate_content([
                    st.session_state.prompt, img
                ])

                # Resolve the response
                response.resolve()

                # 결과 표시
                st.markdown(response.text)
        except UnidentifiedImageError:
            st.error("❌ 업로드된 파일이 유효한 이미지 파일이 아닙니다. 다른 파일을 업로드해 주세요.")
else:
    st.info("이미지를 업로드하세요.")
