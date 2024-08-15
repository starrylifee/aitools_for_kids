import streamlit as st

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

# 홈 화면 제목
st.title("📚 AI 교육 도구 홈")

# 소개 문구
st.markdown("""
## 🎓 학생용 교육 도구 모음
이 페이지에서는 다양한 AI 기반 교육 도구를 사용할 수 있습니다. 각 도구는 교육 활동을 지원하며, 창의적이고 상호작용적인 학습 경험을 제공합니다.
""")

# 도구 소개
st.header("1. 학생용: 이미지 분석 교육 활동 도구")
st.markdown("""
이 도구를 사용하여 이미지를 분석하여 다양한 교육 활동을 수행할 수 있습니다. 활동 코드를 입력하고, 제공된 프롬프트와 이미지를 활용하여 AI와 함께 학습하세요.
""")

st.header("2. 학생용: 인공지능 글자기반 교육 활동 도구")
st.markdown("""
이 도구를 사용하여 다양한 글자기반 교육 활동을 수행할 수 있습니다. 코드를 입력하고, 프롬프트를 가져와 나의 입력을 넣으며 학습 내용을 확장하세요.
""")

st.header("3. 학생용: 이미지 생성 도구")
st.markdown("""
이 도구를 사용하여 교사가 제공한 프롬프트에 따라 이미지를 생성할 수 있습니다. 형용사를 선택하여 이미지의 스타일이나 느낌을 조정하고, 생성된 이미지를 학습에 활용하세요.
""")

# 사용자가 각 도구를 더 쉽게 이해하고 접근할 수 있도록 각 도구에 대한 간단한 설명과 그 기능을 소개하는 페이지입니다. 
# 각 도구에 대해 더 많은 정보를 얻으려면 사이드바의 각 도구 링크를 클릭하세요.
