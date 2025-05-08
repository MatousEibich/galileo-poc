import streamlit as st
from dotenv import load_dotenv
import os

from langchain.agents.agent_types import AgentType
from langchain_experimental.agents.agent_toolkits import create_csv_agent
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain.memory import ConversationBufferMemory
from langchain.callbacks.streamlit import StreamlitCallbackHandler

# -----------------------------------------------------------------------------
# 1️⃣  ENV + MODEL SET‑UP  (runs once at app start)
# -----------------------------------------------------------------------------
load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

# -----------------------------------------------------------------------------
# 2️⃣  PROMPT  (your original, + chat history placeholder)
# -----------------------------------------------------------------------------
SYSTEM_PROMPT = """
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

If you need more data, ask the user first; do **not** fetch the web.
"""

PROMPT = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    ("system", "Dosavadní konverzace:\n{chat_history}"),
    ("human", "{input}"),
])

# -----------------------------------------------------------------------------
# 3️⃣  AGENT FACTORY  (cached – CSVs + memory loaded once)
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
        verbose=True,               # must be True so callbacks stream thoughts
        agent_type=AgentType.OPENAI_FUNCTIONS,
        allow_dangerous_code=True,
        memory=memory,
    )

agent = get_agent()

# -----------------------------------------------------------------------------
# 4️⃣  STREAMLIT PAGE LAYOUT
# -----------------------------------------------------------------------------
st.set_page_config(page_title="🗂️ Municipální data – Chatbot", page_icon="🗂️")
st.title("🗂️ Municipální data – Chatbot")

# Chat history across reruns
if "history" not in st.session_state:
    st.session_state.history = []

# 🔄 Render conversation so far (without current turn)
for role, msg in st.session_state.history:
    with st.chat_message(role):
        st.markdown(msg)

# ℹ️  Input box
user_query = st.chat_input("Zadejte dotaz…")

if user_query:
    # ➤ Show the user's message immediately
    with st.chat_message("user"):
        st.markdown(user_query)
    st.session_state.history.append(("user", user_query))

    # ➤ Assistant thinking + final answer
    with st.chat_message("assistant"):
        callback_container = st.container()  # where StreamlitCallbackHandler streams
        cb_handler = StreamlitCallbackHandler(callback_container)
        with st.spinner("Zpracovávám dotaz…"):
            answer = agent.run(user_query, callbacks=[cb_handler])
        st.markdown(answer)
    st.session_state.history.append(("assistant", answer))
