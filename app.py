"""Streamlit chatbot – fixed quick‑prompt flow & continuous input
Creates a seamless UX: chat input is always on screen; quick‑prompt buttons
no longer hide it and conversation can proceed in the same rerun.
"""

import os
from datetime import datetime
from zoneinfo import ZoneInfo

import streamlit as st
from dotenv import load_dotenv

from langchain.agents.agent_types import AgentType
from langchain_experimental.agents.agent_toolkits import create_csv_agent
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain.memory import ConversationBufferMemory
from langchain.callbacks.streamlit import StreamlitCallbackHandler

# -----------------------------------------------------------------------------
# 1️⃣  ENV + MODEL SET‑UP
# -----------------------------------------------------------------------------
load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
LOCAL_TZ = ZoneInfo("Europe/Prague")
CURRENT_TIME = datetime.now(LOCAL_TZ).strftime("%Y-%m-%d %H:%M (%Z)")
print(CURRENT_TIME)

# -----------------------------------------------------------------------------
# 2️⃣  PROMPT
# -----------------------------------------------------------------------------
SYSTEM_PROMPT = f"""
You are a Czech‑speaking municipal‑data assistant with Python execution rights.
Three pandas DataFrames are pre‑loaded for you:

────────────────────────────────────────────────────────
1.  df1  – ÚŘEDNÍ DESKA (official public notices)
    Columns
      • nazev_cs            – headline of the notice (str)
      • vytvoreno           – creation timestamp (ISO str)
      • vyveseni            – posting date (str YYYY‑MM‑DD)
      • relevantni_do       – expiry date or \"nespecifikovaný\"
      • cislo_jednaci       – docket / file number (str)
      • spisova_znacka      – case reference (str)
      • agenda_names        – semicolon list of agenda names (str)
      • document_urls       – semicolon list of source files (str)

2.  df2  – UDÁLOSTI (events & happenings)
    Columns
      • nazev_cs, popis_cs  – title & description (str)
      • zacatek, konec      – start/end timestamps (ISO str or None)
      • vhodne_pro_detii    – bool (child‑friendly)
      • vhodne_pro_zvirata  – bool (pet‑friendly)
      • poradatele          – organisers (semicolon str)
      • adresa              – location text (str)
      • image_urls          – semicolon str of images
      In the current setup, this containts only two rows 
       - two rows with the same subject "Zasedání Zastupitelstva města Horšovský Týn"
       - this df should be only used when talking about "Zasedání Zastupitelstva" and similar

3.  df3  – AKTUALITY (news flashes)
    Columns
      • nazev_cs, popis_cs  – headline & body (str)
      • vytvoreno           – creation timestamp
      • relevantni_do       – expiry timestamp or \"nespecifikovaný\"
      • oznamovatel_ico     – announcer's company ID (str or None)
      • oznamovatel_nazev_cs– announcer's name (str)
      • priloha_urls        – semicolon str of attachments
────────────────────────────────────────────────────────

▲  ALWAYS:
   • Think step‑by‑step before coding.
   • Show and cite every column you read.
   • Return answers in *concise Czech*.

▲  NON‑EXACT MATCHING POLICY  (apply in this order):
   1.  **Case & diacritics** – compare strings case‑insensitively and
       ignore Czech accents (týn == Tyn).
   2.  **Substring / contains** – treat a query as a substring match
       if no full match is found.
   3.  **Fuzzy similarity** – use Python helper:

         from difflib import SequenceMatcher
         def similar(a, b, threshold=0.80):
             return SequenceMatcher(None, a, b).ratio() >= threshold

       Apply to textual columns; threshold ≥ 0.80.
   4.  **Date proximity** – when matching by date, allow ±1 day.
   5.  **Numeric codes** – strip whitespace and punctuation
       (e.g., \"SP/2024‑004\" ≈ \"SP 2024 004\").

   Logically justify in the answer whenever you fall back to a fuzzy rule.

Current local date & time: {CURRENT_TIME}
YOU ABSOLUTELY NEED TO KEEP THE CURRENT TIME IN MIND WHEN ANSWERING THE USER'S QUESTION.
IF THE USER ASKS ABOUT "PŘÍŠTÍ" or "MINULÉ", the current date is super important. 

If you need more data, ask the user first; do **not** fetch the web.
"""

PROMPT = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    ("system", "Dosavadní konverzace:\n{chat_history}"),
    ("human", "{input}"),
])

# -----------------------------------------------------------------------------
# 3️⃣  AGENT FACTORY (cached)
# -----------------------------------------------------------------------------
@st.cache_resource(show_spinner=False)
def get_agent():
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    return create_csv_agent(
        ChatOpenAI(temperature=0, model="gpt-4o-mini"),
        [
            "data/uredni_deska.csv",
            "data/udalosti.csv",
            "data/aktuality.csv",
        ],
        prompt=PROMPT,
        verbose=True,
        agent_type=AgentType.OPENAI_FUNCTIONS,
        allow_dangerous_code=True,
        memory=memory,
    )

agent = get_agent()

# -----------------------------------------------------------------------------
# 4️⃣  UI LAYOUT
# -----------------------------------------------------------------------------
st.set_page_config(page_title="Horšovský Týn – Chatbot", page_icon="🗂️", layout="wide")

with st.sidebar:
    st.image("logo.png", width=160, caption="Město Horšovský Týn")
    st.markdown("##### Chatbot městských dat")

    st.divider()

    st.markdown("**Rychlé dotazy:**")
    if st.button(":wastebasket: Svoz odpadu"):
        st.session_state["preset_query"] = "Máš nějaké informace o svozu odpadu?"
    if st.button(":office: Zasedání zastupitelstva"):
        st.session_state["preset_query"] = "Kdy je příští zasedání zastupitelstva?"

    st.divider()
    show_thoughts = st.checkbox(":brain: Zobrazit myšlení agenta", value=True)
    st.divider()
    if "history" in st.session_state and st.session_state.history:
        transcript = "\n\n".join(f"{role.upper()}: {txt}" for role, txt in st.session_state.history)
        st.download_button("⬇️ Stáhnout přepis", transcript, "chat_přepis.txt", "text/plain")

# -----------------------------------------------------------------------------
# 5️⃣  CHAT PANEL
# -----------------------------------------------------------------------------
st.title("🗂️ Chatbot městských dat")

# Ensure history exists
if "history" not in st.session_state:
    st.session_state.history = []

# ---- primary chat input (always visible) ----
primary_input = st.chat_input("Zadejte dotaz…", key="main_input")

# A preset query (from quick button) overrides keyboard input for this turn
user_query = st.session_state.pop("preset_query", None) or primary_input

# Render chat history
for role, message in st.session_state.history:
    with st.chat_message(role):
        st.markdown(message, unsafe_allow_html=True)

# ---- process new user query ----
if user_query:
    with st.chat_message("user"):
        st.markdown(user_query)
    st.session_state.history.append(("user", user_query))

    with st.chat_message("assistant"):
        cb_container = st.container()
        cb_handler = StreamlitCallbackHandler(cb_container) if show_thoughts else None
        with st.spinner("Zpracovávám dotaz…"):
            answer = agent.run(user_query, callbacks=[cb_handler] if cb_handler else None)
        st.markdown(answer, unsafe_allow_html=True)
    st.session_state.history.append(("assistant", answer))

