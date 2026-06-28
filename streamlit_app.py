import os
import json
import streamlit as st
from datetime import datetime, timezone

# Add parent/project directory to sys.path just in case
import sys
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Set page configuration
st.set_page_config(
    page_title="PNS - Personalized Networking Assistant",
    page_icon="🤝",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Import PNS modules
from app.models.database import SessionLocal, ConversationHistory, engine, Base
import app.services.event_analyzer as event_analyzer
import app.services.topic_generator as topic_generator
from app.services.event_analyzer import extract_topics
from app.services.topic_generator import generate_suggestions
from app.services.fact_checker import verify_fact_wikipedia
from app.services.json_storage import log_conversation_to_json, log_feedback_to_json

# Initialize SQLite database tables
Base.metadata.create_all(bind=engine)

# Inject custom Google Fonts and premium dark UI CSS
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=Outfit:wght@400;500;600;700;800&display=swap');

/* Main app design system tokens */
:root {
    --bg-darker: #0b0f19;
    --bg-dark: #121826;
    --bg-card: #1e2538;
    --bg-card-hover: #262e48;
    --border-color: #2d3748;
    --border-focus: #4f46e5;
    --text-primary: #f8fafc;
    --text-secondary: #94a3b8;
    --text-muted: #64748b;
    --gradient-primary: linear-gradient(135deg, #6366f1 0%, #a855f7 50%, #ec4899 100%);
    --gradient-header: linear-gradient(135deg, #1e1b4b 0%, #0f172a 100%);
    --gradient-btn: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
    --color-success: #10b981;
    --color-danger: #ef4444;
}

/* Global Typography Override */
html, body, [class*="css"], .stApp {
    font-family: 'Inter', sans-serif !important;
}

h1, h2, h3, h4, h5, h6, .logo-title {
    font-family: 'Outfit', sans-serif !important;
    font-weight: 600;
}

/* Premium Header styling */
.header-container {
    background: var(--gradient-header);
    border: 1px solid var(--border-color);
    border-radius: 16px;
    padding: 2.5rem;
    margin-bottom: 2rem;
    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3);
}

.header-container h1 {
    font-size: 2.5rem;
    margin-top: 0px;
    margin-bottom: 0.5rem;
    background: var(--gradient-primary);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-weight: 800;
}

.header-subtitle {
    color: var(--text-secondary);
    font-size: 1.1rem;
}

/* Suggestion & wiki layout cards */
.pns-card {
    background-color: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 1.5rem;
    transition: all 0.3s ease;
}

.pns-card:hover {
    border-color: var(--border-focus);
    background-color: var(--bg-card-hover);
    box-shadow: 0 4px 20px rgba(99, 102, 241, 0.1);
}

.suggestion-card {
    background-color: rgba(30, 37, 56, 0.4);
    border-left: 4px solid #6366f1;
    border-top: 1px solid var(--border-color);
    border-bottom: 1px solid var(--border-color);
    border-right: 1px solid var(--border-color);
    border-radius: 8px;
    padding: 1.25rem;
    margin-bottom: 1rem;
    display: flex;
    gap: 1rem;
    align-items: flex-start;
}

.suggestion-num {
    font-family: 'Outfit', sans-serif;
    font-size: 1.1rem;
    font-weight: 800;
    color: #a855f7;
    background: rgba(168, 85, 247, 0.15);
    padding: 3px 8px;
    border-radius: 6px;
    line-height: 1;
    min-width: 25px;
    text-align: center;
}

.suggestion-text {
    font-size: 1rem;
    color: var(--text-primary);
    line-height: 1.5;
    margin: 0px;
}

/* Badge Styling */
.pns-badge {
    background: linear-gradient(135deg, #6366f1 0%, #a855f7 100%);
    color: white;
    padding: 5px 14px;
    border-radius: 9999px;
    font-size: 0.85rem;
    font-weight: 600;
    display: inline-block;
    margin: 4px 8px 4px 0;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.15);
}

/* Fact Verification Card */
.factcheck-card {
    background-color: rgba(30, 37, 56, 0.4);
    border: 1px solid var(--border-color);
    border-radius: 12px;
    padding: 2rem;
    margin-top: 1rem;
    margin-bottom: 1.5rem;
}

.factcheck-header {
    font-family: 'Outfit', sans-serif;
    font-size: 1.3rem;
    font-weight: 700;
    margin-bottom: 1rem;
    display: flex;
    align-items: center;
    gap: 0.75rem;
}

.factcheck-badge {
    padding: 3px 10px;
    border-radius: 4px;
    font-size: 0.75rem;
    font-weight: 700;
    text-transform: uppercase;
}

.factcheck-badge.verified {
    background-color: rgba(16, 185, 129, 0.15);
    border: 1px solid rgba(16, 185, 129, 0.3);
    color: #10b981;
}

.factcheck-badge.unverified {
    background-color: rgba(239, 68, 68, 0.15);
    border: 1px solid rgba(239, 68, 68, 0.3);
    color: #ef4444;
}

.factcheck-body {
    font-size: 1.05rem;
    color: var(--text-primary);
    line-height: 1.6;
    margin-bottom: 1.25rem;
}

.factcheck-url-link {
    color: #3b82f6 !important;
    font-weight: 600;
    text-decoration: none;
    font-size: 0.95rem;
}

.factcheck-url-link:hover {
    text-decoration: underline;
}

/* History logs list view styling */
.history-item-container {
    background-color: rgba(30, 37, 56, 0.4);
    border: 1px solid var(--border-color);
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 1.5rem;
}

.history-item-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    padding-bottom: 0.75rem;
    margin-bottom: 1rem;
}

.history-id-tag {
    font-family: 'Outfit', sans-serif;
    font-size: 1.1rem;
    color: #a855f7;
    font-weight: 700;
}

.history-time-tag {
    font-size: 0.85rem;
    color: var(--text-muted);
}

.feedback-badge {
    font-size: 0.85rem;
    font-weight: 600;
    padding: 2px 8px;
    border-radius: 4px;
}

.feedback-badge.yes {
    background-color: rgba(16, 185, 129, 0.15);
    color: #10b981;
}

.feedback-badge.no {
    background-color: rgba(239, 68, 68, 0.15);
    color: #ef4444;
}

.feedback-badge.none {
    background-color: rgba(255, 255, 255, 0.05);
    color: var(--text-muted);
}
</style>
""", unsafe_allow_html=True)

# ----------------- SIDEBAR -----------------
st.sidebar.markdown("""
<div style="display: flex; align-items: center; gap: 10px; margin-bottom: 1.5rem; margin-top: -1rem;">
    <span style="font-size: 2.2rem;">🤝</span>
    <h2 class="logo-title" style="margin: 0; font-size: 1.6rem; background: linear-gradient(135deg, #6366f1, #a855f7); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">PNS Assistant</h2>
</div>
""", unsafe_allow_html=True)

st.sidebar.subheader("System Status")

# Check database file status
db_exists = os.path.exists("pns.db")
db_status_color = "#10b981" if db_exists else "#f59e0b"
db_status_text = "Connected (SQLite)" if db_exists else "Initializing DB..."

st.sidebar.markdown(f"""
<div style="display: flex; align-items: center; gap: 8px; margin-bottom: 12px;">
    <span style="height: 10px; width: 10px; background-color: {db_status_color}; border-radius: 50%; display: inline-block;"></span>
    <span style="font-size: 0.9rem; font-weight: 500;">Database: {db_status_text}</span>
</div>
""", unsafe_allow_html=True)

# Load configuration status
mock_ml_active = event_analyzer.USE_MOCK_ML
mock_ml_toggle = st.sidebar.toggle("Use Mock ML (Fast Startup)", value=mock_ml_active)

# Synchronize model settings in imported modules
if mock_ml_toggle != mock_ml_active:
    event_analyzer.USE_MOCK_ML = mock_ml_toggle
    topic_generator.USE_MOCK_ML = mock_ml_toggle
    st.toast(f"Model settings updated: Use Mock ML = {mock_ml_toggle}")

model_mode_badge = "DEMO MODE (Mocks)" if mock_ml_toggle else "PROD MODE (Transformers)"
model_badge_bg = "rgba(245, 158, 11, 0.15)" if mock_ml_toggle else "rgba(16, 185, 129, 0.15)"
model_badge_color = "#f59e0b" if mock_ml_toggle else "#10b981"

st.sidebar.markdown(f"""
<div style="background-color: {model_badge_bg}; color: {model_badge_color}; border: 1px solid {model_badge_color}33; 
            padding: 6px 12px; border-radius: 6px; font-size: 0.75rem; font-weight: 700; text-transform: uppercase; 
            text-align: center; margin-bottom: 1.5rem; display: inline-block; width: 100%;">
    {model_mode_badge}
</div>
""", unsafe_allow_html=True)

# Model configuration details
st.sidebar.subheader("Configuration")
st.sidebar.markdown(f"""
- **Theme Extractor Model:**  
  `{event_analyzer.THEME_EXTRACTOR_MODEL}`
- **Starter Generator Model:**  
  `{topic_generator.STARTER_GENERATOR_MODEL}`
""")

# Sidebar Footer
st.sidebar.markdown("""
<div style="margin-top: 6rem; border-top: 1px solid rgba(255, 255, 255, 0.05); padding-top: 1rem; font-size: 0.8rem; color: #64748b;">
    <p>Personalized Networking Assistant &copy; 2026</p>
    <span>v1.2.0 (Streamlit)</span>
</div>
""", unsafe_allow_html=True)

# ----------------- MAIN APP HEADER -----------------
st.markdown("""
<div class="header-container">
    <h1>Personalized Networking Assistant</h1>
    <div class="header-subtitle">
        Smart conversation starters tailored to your events, verified by Wikipedia
    </div>
</div>
""", unsafe_allow_html=True)

# Create Main Tabs
tab_starters, tab_factcheck, tab_history = st.tabs([
    "🤝 Smart Starters",
    "🔍 Fact Verification",
    "📋 Strategy Logs"
])

# Initialize session state objects if they don't exist
if "last_generation_id" not in st.session_state:
    st.session_state.last_generation_id = None
if "last_topics" not in st.session_state:
    st.session_state.last_topics = []
if "last_suggestions" not in st.session_state:
    st.session_state.last_suggestions = []
if "last_feedback" not in st.session_state:
    st.session_state.last_feedback = None
if "show_results" not in st.session_state:
    st.session_state.show_results = False

# ----------------- TAB 1: SMART STARTERS -----------------
with tab_starters:
    col_input, col_result = st.columns([2, 3])
    
    with col_input:
        st.markdown('<div class="pns-card">', unsafe_allow_html=True)
        st.subheader("Define Your Parameters")
        st.write("Provide details about the event and what topics you wish to bridge to.")
        
        event_desc_input = st.text_area(
            "Event Description", 
            placeholder="Describe the conference topic, theme, panel, or session (e.g. AI for Sustainable Cities. Discussing grid optimization, environmental policy, and green transportation)...",
            height=180
        )
        
        interests_text_input = st.text_input(
            "Your Interests", 
            placeholder="e.g. climate change, machine learning, urban transit (comma-separated)"
        )
        
        generate_btn = st.button("Generate Starters", type="primary", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        if generate_btn:
            if not event_desc_input.strip():
                st.error("Please provide an Event Description.")
            elif not interests_text_input.strip():
                st.error("Please enter at least one Interest.")
            else:
                with st.spinner("Analyzing event themes and generating conversation starters..."):
                    interests_list = [i.strip() for i in interests_text_input.split(",") if i.strip()]
                    
                    # Extract topics & suggestions
                    topics = extract_topics(event_desc_input, interests_list)
                    suggestions = generate_suggestions(event_desc_input, topics, interests_list)
                    
                    # Log into SQLite DB to fetch id
                    db = SessionLocal()
                    db_history = ConversationHistory(
                        description=event_desc_input,
                        interests=json.dumps(interests_list),
                        topics=json.dumps(topics),
                        suggestions=json.dumps(suggestions),
                        feedback=None
                    )
                    db.add(db_history)
                    db.commit()
                    db.refresh(db_history)
                    db_id = db_history.id
                    db.close()
                    
                    # Log to JSON storage
                    log_conversation_to_json(
                        description=event_desc_input,
                        interests=interests_list,
                        topics=topics,
                        suggestions=suggestions,
                        item_id=db_id
                    )
                    
                    # Update session state values
                    st.session_state.last_generation_id = db_id
                    st.session_state.last_topics = topics
                    st.session_state.last_suggestions = suggestions
                    st.session_state.last_feedback = None
                    st.session_state.show_results = True
                    st.rerun()

    with col_result:
        if not st.session_state.show_results:
            st.markdown("""
            <div style="text-align: center; padding: 5rem 2rem; border: 2px dashed var(--border-color); border-radius: 12px; color: var(--text-muted);">
                <div style="font-size: 3rem; margin-bottom: 1rem;">💡</div>
                <h3>Tailored Suggestions</h3>
                <p>Fill in the details on the left and click <strong>Generate Starters</strong> to build your custom icebreakers.</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown('<div class="pns-card" style="margin-bottom: 0px;">', unsafe_allow_html=True)
            st.subheader("Tailored Suggestions")
            st.write("Extracted themes and customized conversation starters will appear below.")
            
            st.markdown("##### Extracted Topics")
            badges_html = "".join([f'<span class="pns-badge">{t}</span>' for t in st.session_state.last_topics])
            st.markdown(f'<div style="margin-bottom: 1.5rem;">{badges_html}</div>', unsafe_allow_html=True)
            
            st.markdown("##### Conversation Starters")
            for idx, sug in enumerate(st.session_state.last_suggestions, 1):
                st.markdown(f"""
                <div class="suggestion-card">
                    <div class="suggestion-num">{idx:02d}</div>
                    <div class="suggestion-text">{sug}</div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown('<hr style="border-color: rgba(255, 255, 255, 0.05); margin: 1.5rem 0;">', unsafe_allow_html=True)
            st.write("**How do you rate these suggestions?**")
            
            col_yes, col_no = st.columns([1, 1])
            
            # Check state of feedback
            useful_btn_type = "primary" if st.session_state.last_feedback is True else "secondary"
            needs_work_btn_type = "primary" if st.session_state.last_feedback is False else "secondary"
            
            with col_yes:
                if st.button("👍 Useful", key="btn_useful", type=useful_btn_type, use_container_width=True):
                    db = SessionLocal()
                    db_item = db.query(ConversationHistory).filter(ConversationHistory.id == st.session_state.last_generation_id).first()
                    if db_item:
                        db_item.feedback = True
                        db.commit()
                    db.close()
                    log_feedback_to_json(st.session_state.last_generation_id, True)
                    st.session_state.last_feedback = True
                    st.toast("Feedback logged: Useful 👍")
                    st.rerun()
            with col_no:
                if st.button("👎 Needs Work", key="btn_needs_work", type=needs_work_btn_type, use_container_width=True):
                    db = SessionLocal()
                    db_item = db.query(ConversationHistory).filter(ConversationHistory.id == st.session_state.last_generation_id).first()
                    if db_item:
                        db_item.feedback = False
                        db.commit()
                    db.close()
                    log_feedback_to_json(st.session_state.last_generation_id, False)
                    st.session_state.last_feedback = False
                    st.toast("Feedback logged: Needs Work 👎")
                    st.rerun()
            
            st.markdown('</div>', unsafe_allow_html=True)


# ----------------- TAB 2: FACT VERIFICATION -----------------
with tab_factcheck:
    st.markdown('<div class="pns-card">', unsafe_allow_html=True)
    st.subheader("Quick Wikipedia Reference")
    st.write("Verify a concept, term, or acronym on the fly to prepare for conversations or clarify topics discussed.")
    
    col_search_query, col_search_btn = st.columns([4, 1])
    with col_search_query:
        query_input = st.text_input(
            "Search Query", 
            placeholder="e.g. zero-shot learning, microgrids, zero-knowledge proofs",
            label_visibility="collapsed"
        )
    with col_search_btn:
        search_clicked = st.button("Verify Fact", type="primary", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    if search_clicked:
        if not query_input.strip():
            st.error("Please enter a concept or term to search.")
        else:
            with st.spinner(f"Verifying '{query_input}' on Wikipedia..."):
                result = verify_fact_wikipedia(query_input)
                
                # Check status
                is_verified = result.get("verified", False)
                badge_class = "verified" if is_verified else "unverified"
                badge_label = "Verified Reference" if is_verified else "Unverified"
                
                st.markdown(f"""
                <div class="factcheck-card">
                    <div class="factcheck-header">
                        <span class="factcheck-badge {badge_class}">{badge_label}</span>
                        <span style="font-family: 'Outfit', sans-serif; font-size: 1.25rem;">{result['query']}</span>
                    </div>
                    <div class="factcheck-body">
                        {result['summary']}
                    </div>
                    <div>
                        <a class="factcheck-url-link" href="{result['source_url']}" target="_blank">
                            {"Read full Wikipedia article ↗" if is_verified else "Search Wikipedia directly ↗"}
                        </a>
                    </div>
                </div>
                """, unsafe_allow_html=True)


# ----------------- TAB 3: STRATEGY LOGS (HISTORY) -----------------
with tab_history:
    col_hist_title, col_hist_btn = st.columns([4, 1])
    with col_hist_title:
        st.subheader("Strategy Logs")
        st.write("Browse through your previously generated starters and review their effectiveness rating.")
    with col_hist_btn:
        refresh_logs = st.button("Refresh Logs", key="refresh_logs_btn", use_container_width=True)
        if refresh_logs:
            st.rerun()
            
    # Query database history
    db = SessionLocal()
    history_items = db.query(ConversationHistory).order_by(ConversationHistory.id.desc()).all()
    db.close()
    
    if not history_items:
        st.info("No saved logs found. Go to 'Smart Starters' to generate some icebreakers first!")
    else:
        for item in history_items:
            # Safely parse JSON lists
            try:
                interests_list = json.loads(item.interests)
            except Exception:
                interests_list = [x.strip() for x in item.interests.split(",") if x.strip()]
                
            try:
                topics_list = json.loads(item.topics)
            except Exception:
                topics_list = [x.strip() for x in item.topics.split(",") if x.strip()]
                
            try:
                suggestions_list = json.loads(item.suggestions)
            except Exception:
                suggestions_list = [item.suggestions]
                
            # Date styling
            date_str = item.created_at.strftime("%Y-%m-%d %H:%M:%S UTC")
            
            # Rating badge styling
            if item.feedback is True:
                rating_badge_html = '<span class="feedback-badge yes">Rated: Useful 👍</span>'
            elif item.feedback is False:
                rating_badge_html = '<span class="feedback-badge no">Rated: Needs Work 👎</span>'
            else:
                rating_badge_html = '<span class="feedback-badge none">No Rating Yet</span>'
                
            # Render card header
            st.markdown(f"""
            <div class="history-item-container" style="margin-bottom: 10px;">
                <div class="history-item-header">
                    <span class="history-id-tag">Log #{item.id}</span>
                    <div>
                        {rating_badge_html}
                        <span class="history-time-tag" style="margin-left: 10px;">{date_str}</span>
                    </div>
                </div>
                <div style="font-size: 0.95rem; margin-bottom: 0.5rem;">
                    <strong>Event:</strong> {item.description}
                </div>
                <div style="font-size: 0.95rem; margin-bottom: 0.75rem;">
                    <strong>Interests:</strong> {", ".join(interests_list)}
                </div>
            """, unsafe_allow_html=True)
            
            # Extracted topics
            topic_badges_html = "".join([f'<span class="pns-badge" style="font-size: 0.75rem; padding: 3px 10px;">{t}</span>' for t in topics_list])
            st.markdown(f'<div style="margin-bottom: 0.75rem;"><strong>Extracted Topics:</strong> {topic_badges_html}</div>', unsafe_allow_html=True)
            
            # Suggestions list
            st.markdown("<strong>Generated Icebreakers:</strong>", unsafe_allow_html=True)
            for idx, sug in enumerate(suggestions_list, 1):
                st.markdown(f'<div style="font-size: 0.95rem; margin-bottom: 6px; padding-left: 10px;">• {sug}</div>', unsafe_allow_html=True)
                
            # Inline voting buttons
            st.write("")
            col_rate_yes, col_rate_no, col_rate_spacer = st.columns([1, 1, 4])
            
            # Active styling depending on DB value
            hist_yes_type = "primary" if item.feedback is True else "secondary"
            hist_no_type = "primary" if item.feedback is False else "secondary"
            
            with col_rate_yes:
                if st.button("👍 Useful", key=f"h_yes_{item.id}", type=hist_yes_type, use_container_width=True):
                    db = SessionLocal()
                    db_item = db.query(ConversationHistory).filter(ConversationHistory.id == item.id).first()
                    if db_item:
                        db_item.feedback = True
                        db.commit()
                    db.close()
                    log_feedback_to_json(item.id, True)
                    st.toast(f"Log #{item.id} updated: Useful 👍")
                    st.rerun()
            with col_rate_no:
                if st.button("👎 Needs Work", key=f"h_no_{item.id}", type=hist_no_type, use_container_width=True):
                    db = SessionLocal()
                    db_item = db.query(ConversationHistory).filter(ConversationHistory.id == item.id).first()
                    if db_item:
                        db_item.feedback = False
                        db.commit()
                    db.close()
                    log_feedback_to_json(item.id, False)
                    st.toast(f"Log #{item.id} updated: Needs Work 👎")
                    st.rerun()
                    
            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown('<div style="height: 10px;"></div>', unsafe_allow_html=True)
