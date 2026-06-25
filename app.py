import streamlit as st

from src.pipelines.pipelines import step_search, step_read, step_write, step_critic

# ──────────────────────────────────────────────────────────────────────────────
# Page config
# ──────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Multi-Agent Research Studio",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ──────────────────────────────────────────────────────────────────────────────
# Light, airy theme
# ──────────────────────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(135deg, #f5f7ff 0%, #eef9ff 45%, #fff5fb 100%);
    }
    #MainMenu, footer {visibility: hidden;}

    .hero {
        background: linear-gradient(120deg, #6366f1 0%, #38bdf8 55%, #22d3ee 100%);
        border-radius: 22px;
        padding: 34px 40px;
        color: white;
        box-shadow: 0 12px 35px rgba(99,102,241,0.28);
        margin-bottom: 6px;
    }
    .hero h1 {margin: 0; font-size: 2.1rem; font-weight: 800; letter-spacing: -0.5px;}
    .hero p {margin: 8px 0 0; font-size: 1.02rem; opacity: 0.95;}

    .agent-card {
        background: white;
        border-radius: 16px;
        padding: 18px 20px;
        border: 1px solid #eef0f7;
        box-shadow: 0 6px 18px rgba(80,90,160,0.06);
        height: 100%;
    }
    .agent-card .emoji {font-size: 1.7rem;}
    .agent-card .name {font-weight: 700; color: #1e293b; margin-top: 6px;}
    .agent-card .desc {color: #64748b; font-size: 0.86rem; margin-top: 4px; line-height: 1.4;}

    .stButton > button {
        background: linear-gradient(120deg, #6366f1, #22d3ee);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.6rem 1rem;
        font-weight: 700;
        box-shadow: 0 8px 20px rgba(99,102,241,0.25);
        transition: transform 0.15s ease;
    }
    .stButton > button:hover {transform: translateY(-2px); color: white;}

    .stTabs [data-baseweb="tab-list"] {gap: 8px;}
    .stTabs [data-baseweb="tab"] {
        background: white; border-radius: 12px 12px 0 0;
        padding: 10px 18px; font-weight: 600; color: #475569;
    }
    .stTabs [aria-selected="true"] {color: #6366f1;}

    div[data-testid="stMetricValue"] {color: #6366f1;}
    </style>
    """,
    unsafe_allow_html=True,
)

# ──────────────────────────────────────────────────────────────────────────────
# Sidebar
# ──────────────────────────────────────────────────────────────────────────────
AGENTS = [
    ("🔎", "Search Agent", "Tìm nguồn tin cậy, mới nhất qua Tavily web search."),
    ("📖", "Reader Agent", "Chọn URL liên quan nhất và bóc tách nội dung chi tiết."),
    ("✍️", "Writer", "Soạn báo cáo có cấu trúc, đầy đủ và chuyên nghiệp."),
    ("🧐", "Critic", "Chấm điểm, nêu điểm mạnh và điểm cần cải thiện."),
]

with st.sidebar:
    st.markdown("### ⚙️ Bảng điều khiển")
    st.caption("Hệ thống nghiên cứu đa tác tử")
    st.divider()
    st.markdown("#### 🤖 Đội ngũ Agent")
    for emoji, name, desc in AGENTS:
        st.markdown(
            f"<div class='agent-card' style='margin-bottom:10px'>"
            f"<span class='emoji'>{emoji}</span>"
            f"<div class='name'>{name}</div>"
            f"<div class='desc'>{desc}</div></div>",
            unsafe_allow_html=True,
        )
    st.divider()
    st.caption("Powered by LangChain · Groq · Tavily")

# ──────────────────────────────────────────────────────────────────────────────
# Hero
# ──────────────────────────────────────────────────────────────────────────────
st.markdown(
    "<div class='hero'><h1>🔬 Multi-Agent Research Studio</h1>"
    "<p>Nhập một chủ đề — đội ngũ agent sẽ tìm kiếm, đọc, viết và phản biện "
    "để tạo ra báo cáo nghiên cứu hoàn chỉnh cho bạn.</p></div>",
    unsafe_allow_html=True,
)
st.write("")

# ──────────────────────────────────────────────────────────────────────────────
# Input
# ──────────────────────────────────────────────────────────────────────────────
col_in, col_btn = st.columns([5, 1])
with col_in:
    topic = st.text_input(
        "Chủ đề nghiên cứu",
        placeholder="VD: The impact of AI on the job market in 2024",
        label_visibility="collapsed",
    )
with col_btn:
    run = st.button("🚀 Nghiên cứu", use_container_width=True)

st.caption("💡 Gợi ý: Hãy mô tả chủ đề càng cụ thể càng tốt để có báo cáo chất lượng hơn.")

# ──────────────────────────────────────────────────────────────────────────────
# Run pipeline
# ──────────────────────────────────────────────────────────────────────────────
if run:
    if not topic.strip():
        st.warning("⚠️ Vui lòng nhập một chủ đề trước khi bắt đầu.")
        st.stop()

    state = {}
    try:
        with st.status("🧠 Đội ngũ agent đang làm việc...", expanded=True) as status:
            st.write("🔎 **Search Agent** đang tìm kiếm thông tin...")
            state["search_results"] = step_search(topic)

            st.write("📖 **Reader Agent** đang bóc tách nguồn liên quan nhất...")
            state["scraped_content"] = step_read(topic, state["search_results"])

            st.write("✍️ **Writer** đang soạn báo cáo...")
            state["report"] = step_write(topic, state["search_results"], state["scraped_content"])

            st.write("🧐 **Critic** đang đánh giá báo cáo...")
            state["feedback"] = step_critic(state["report"])

            status.update(label="✅ Hoàn tất! Báo cáo của bạn đã sẵn sàng.", state="complete")
    except Exception as e:
        st.error(f"❌ Có lỗi xảy ra khi chạy pipeline: {e}")
        st.stop()

    st.session_state["result"] = state
    st.session_state["topic"] = topic

# ──────────────────────────────────────────────────────────────────────────────
# Results
# ──────────────────────────────────────────────────────────────────────────────
if "result" in st.session_state:
    state = st.session_state["result"]
    st.success(f"Báo cáo cho chủ đề: **{st.session_state.get('topic', '')}**")

    tab_report, tab_critic, tab_search, tab_read = st.tabs(
        ["📄 Báo cáo", "🧐 Phản biện", "🔎 Kết quả tìm kiếm", "📖 Nội dung đã đọc"]
    )

    with tab_report:
        st.markdown(state.get("report", "_Chưa có báo cáo._"))
        st.download_button(
            "⬇️ Tải báo cáo (.md)",
            data=state.get("report", ""),
            file_name="research_report.md",
            mime="text/markdown",
        )

    with tab_critic:
        st.markdown(state.get("feedback", "_Chưa có phản biện._"))

    with tab_search:
        st.markdown(state.get("search_results", "_Không có dữ liệu._"))

    with tab_read:
        st.markdown(state.get("scraped_content", "_Không có dữ liệu._"))
else:
    st.info("👋 Nhập chủ đề ở trên và nhấn **Nghiên cứu** để bắt đầu.")
