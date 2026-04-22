import streamlit as st
import pickle
import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from time import sleep

# ─── PAGE CONFIG ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="CineMatch — Movie Recommender",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ─── ALL CSS + HERO IN ONE st.markdown CALL ─────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;1,9..40,300&family=Playfair+Display:ital@1&display=swap');

*, *::before, *::after { box-sizing: border-box; }

html, body,
[data-testid="stAppViewContainer"],
[data-testid="stApp"],
section[data-testid="stMain"] {
    background-color: #090909 !important;
    color: #e8e0d5 !important;
}

[data-testid="stAppViewContainer"] {
    background:
        radial-gradient(ellipse 80% 50% at 50% -5%, rgba(160,20,20,0.22) 0%, transparent 65%),
        #090909 !important;
}

#MainMenu, footer, header,
[data-testid="stDecoration"],
[data-testid="stToolbar"],
[data-testid="stStatusWidget"] { display: none !important; visibility: hidden !important; }

.block-container { padding: 0 !important; max-width: 100% !important; }

.cm-hero {
    position: relative;
    width: 100%;
    padding: 80px 64px 64px;
    overflow: hidden;
    border-bottom: 1px solid rgba(255,255,255,0.06);
}
.cm-hero::before {
    content: '';
    position: absolute;
    inset: 0;
    background:
        repeating-linear-gradient(0deg, transparent, transparent 39px, rgba(255,255,255,0.015) 40px),
        repeating-linear-gradient(90deg, transparent, transparent 39px, rgba(255,255,255,0.015) 40px);
    pointer-events: none;
}
.cm-eyebrow {
    font-family: 'DM Sans', sans-serif;
    font-size: 11px; font-weight: 500;
    letter-spacing: 0.38em; text-transform: uppercase;
    color: #c0392b; margin-bottom: 20px;
    display: flex; align-items: center; gap: 12px;
}
.cm-eyebrow::before {
    content: ''; display: inline-block;
    width: 30px; height: 1px; background: #c0392b;
}
.cm-title {
    font-family: 'Bebas Neue', sans-serif;
    font-size: clamp(72px, 10vw, 138px);
    line-height: 0.9; letter-spacing: 0.02em;
    color: #f0e8df; margin: 0;
}
.cm-title .red { color: #c0392b; }
.cm-subtitle {
    font-family: 'Playfair Display', Georgia, serif;
    font-style: italic; font-size: 17px;
    color: rgba(232,224,213,0.42);
    margin-top: 20px; max-width: 440px; line-height: 1.7;
}
.cm-badge {
    display: inline-flex; align-items: center; gap: 8px;
    margin-top: 30px;
    font-family: 'DM Sans', sans-serif;
    font-size: 11px; font-weight: 300;
    letter-spacing: 0.12em; color: rgba(232,224,213,0.35);
}
.cm-dot {
    width: 6px; height: 6px; border-radius: 50%;
    background: #c0392b; display: inline-block;
    animation: cm-pulse 2s ease-in-out infinite;
}
@keyframes cm-pulse {
    0%,100% { opacity:1; transform:scale(1); }
    50%      { opacity:.35; transform:scale(0.65); }
}
.cm-filmstrip {
    position: absolute; right: 64px; top: 50%;
    transform: translateY(-50%);
    display: flex; gap: 7px; opacity: 0.07;
}
.cm-fscol { display: flex; flex-direction: column; gap: 7px; }
.cm-fscol:nth-child(2) { margin-top: 19px; }
.cm-hole { width: 22px; height: 28px; border: 2px solid #fff; border-radius: 3px; }

.cm-search-wrap { padding: 48px 64px 36px; border-bottom: 1px solid rgba(255,255,255,0.04); }
.cm-search-label {
    font-family: 'DM Sans', sans-serif;
    font-size: 11px; font-weight: 500;
    letter-spacing: 0.32em; text-transform: uppercase;
    color: rgba(232,224,213,0.36); margin-bottom: 14px;
}

[data-testid="stSelectbox"] label { display: none !important; }
[data-testid="stSelectbox"] { max-width: 580px; }
[data-testid="stSelectbox"] > div > div {
    background: rgba(255,255,255,0.045) !important;
    border: 1px solid rgba(255,255,255,0.11) !important;
    border-radius: 7px !important;
    color: #e8e0d5 !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 15px !important;
    transition: border-color .2s, background .2s !important;
}
[data-testid="stSelectbox"] > div > div:hover {
    border-color: rgba(192,57,43,.55) !important;
    background: rgba(255,255,255,0.06) !important;
}
[data-testid="stSelectbox"] > div > div:focus-within {
    border-color: #c0392b !important;
    box-shadow: 0 0 0 3px rgba(192,57,43,.2) !important;
}

[data-testid="stButton"] > button {
    background: #c0392b !important; color: #fff !important;
    border: none !important; border-radius: 7px !important;
    font-family: 'Bebas Neue', sans-serif !important;
    font-size: 18px !important; letter-spacing: 0.14em !important;
    padding: 10px 42px !important; margin-top: 16px !important;
    box-shadow: 0 4px 22px rgba(192,57,43,.38) !important;
    transition: background .2s, transform .15s, box-shadow .2s !important;
}
[data-testid="stButton"] > button:hover {
    background: #a93226 !important; transform: translateY(-2px) !important;
    box-shadow: 0 10px 32px rgba(192,57,43,.52) !important;
}
[data-testid="stButton"] > button:active { transform: translateY(0) !important; }

.cm-divider {
    display: flex; align-items: center; gap: 18px;
    padding: 44px 64px 28px;
}
.cm-divider-label {
    font-family: 'DM Sans', sans-serif;
    font-size: 11px; font-weight: 500;
    letter-spacing: 0.34em; text-transform: uppercase;
    color: rgba(232,224,213,0.32); white-space: nowrap;
}
.cm-divider-line {
    flex: 1; height: 1px;
    background: linear-gradient(90deg, rgba(192,57,43,.45) 0%, rgba(255,255,255,.05) 55%, transparent 100%);
}

.cm-grid {
    display: grid; grid-template-columns: repeat(5, 1fr);
    gap: 20px; padding: 0 64px 80px;
}
.cm-card {
    position: relative; border-radius: 10px;
    overflow: hidden; background: #111;
    border: 1px solid rgba(255,255,255,0.07);
    transition: transform .32s ease, box-shadow .32s ease, border-color .32s ease;
}
.cm-card:hover {
    transform: translateY(-9px) scale(1.025);
    box-shadow: 0 28px 52px rgba(0,0,0,.75), 0 0 0 1px rgba(192,57,43,.45);
    border-color: rgba(192,57,43,.38);
}
.cm-card img { width: 100%; aspect-ratio: 2/3; object-fit: cover; display: block; transition: filter .32s ease; }
.cm-card:hover img { filter: brightness(.72); }
.cm-card-overlay {
    position: absolute; bottom: 0; left: 0; right: 0;
    padding: 44px 14px 16px;
    background: linear-gradient(to top, rgba(0,0,0,.93) 0%, rgba(0,0,0,.48) 55%, transparent 100%);
}
.cm-card-num { font-family: 'Bebas Neue', sans-serif; font-size: 11px; letter-spacing: .22em; color: #c0392b; margin-bottom: 4px; }
.cm-card-name { font-family: 'DM Sans', sans-serif; font-size: 13px; font-weight: 500; color: #f0e8df; line-height: 1.3; }
.cm-shine {
    position: absolute; top: 0; left: 0; right: 0; height: 38%;
    background: linear-gradient(180deg, rgba(255,255,255,.055) 0%, transparent 100%);
    pointer-events: none; border-radius: 10px 10px 0 0;
}

[data-testid="stAlert"] {
    background: rgba(192,57,43,.1) !important;
    border: 1px solid rgba(192,57,43,.3) !important;
    border-radius: 8px !important; margin: 0 64px !important;
    font-family: 'DM Sans', sans-serif !important;
}

::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: #090909; }
::-webkit-scrollbar-thumb { background: rgba(192,57,43,.4); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: rgba(192,57,43,.7); }
</style>

<div class="cm-hero">
    <div class="cm-filmstrip">
        <div class="cm-fscol">
            <div class="cm-hole"></div><div class="cm-hole"></div>
            <div class="cm-hole"></div><div class="cm-hole"></div>
            <div class="cm-hole"></div><div class="cm-hole"></div>
        </div>
        <div class="cm-fscol">
            <div class="cm-hole"></div><div class="cm-hole"></div>
            <div class="cm-hole"></div><div class="cm-hole"></div>
            <div class="cm-hole"></div>
        </div>
    </div>
    <div class="cm-eyebrow">AI-Powered Recommendations</div>
    <div class="cm-title">CINE<span class="red">MATCH</span></div>
    <div class="cm-subtitle">Discover your next obsession — curated by machine intelligence, calibrated to your taste.</div>
    <div class="cm-badge">
        <span class="cm-dot"></span>
        Content-based filtering &nbsp;&middot;&nbsp; 5000+ titles &nbsp;&middot;&nbsp; TMDB data
    </div>
</div>

<div class="cm-search-wrap">
    <div class="cm-search-label">Choose your film</div>
</div>
""", unsafe_allow_html=True)


# ─── SESSION / API SETUP ────────────────────────────────────────────────────────
session_r = requests.Session()
retry_strategy = Retry(
    total=3, backoff_factor=1,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["GET"]
)
adapter = HTTPAdapter(max_retries=retry_strategy, pool_connections=10, pool_maxsize=10)
session_r.mount("http://", adapter)
session_r.mount("https://", adapter)


def fetch_poster(movie_id, max_retries=3):
    url = f'https://api.themoviedb.org/3/movie/{movie_id}?api_key=a3f8310213b725a32dbe4f002510ab16&language=en-US'
    for attempt in range(max_retries):
        try:
            response = session_r.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            if data.get('poster_path'):
                return "https://image.tmdb.org/t/p/w500/" + data['poster_path']
            return "https://via.placeholder.com/500x750/111111/c0392b?text=No+Poster"
        except requests.exceptions.ConnectionError:
            if attempt < max_retries - 1:
                sleep(2 ** attempt)
            else:
                return "https://via.placeholder.com/500x750/111111/c0392b?text=No+Poster"
        except requests.exceptions.Timeout:
            if attempt < max_retries - 1:
                sleep(2 ** attempt)
            else:
                return "https://via.placeholder.com/500x750/111111/c0392b?text=Timeout"
        except Exception:
            return "https://via.placeholder.com/500x750/111111/c0392b?text=Error"
    return "https://via.placeholder.com/500x750/111111/c0392b?text=No+Poster"


def recommend(movie):
    try:
        movie_index = movies[movies['title'] == movie].index[0]
        distances = similarity[movie_index]
        movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]
        names, posters = [], []
        for i in movies_list:
            movie_id = movies.iloc[i[0]]['id']
            names.append(movies.iloc[i[0]].title)
            sleep(0.1)
            posters.append(fetch_poster(movie_id))
        return names, posters
    except Exception as e:
        st.error(f"Error generating recommendations: {str(e)}")
        return [], []


# ─── LOAD DATA ──────────────────────────────────────────────────────────────────
try:
    with open('movies_dict.pkl', 'rb') as f:
        movies_dict = pickle.load(f)
    movies = pd.DataFrame(movies_dict)
except FileNotFoundError:
    st.error("movies_dict.pkl not found.")
    st.stop()

try:
    with open('similarity.pkl', 'rb') as f:
        similarity = pickle.load(f)
except FileNotFoundError:
    st.error("similarity.pkl not found.")
    st.stop()


# ─── SELECTBOX + BUTTON ─────────────────────────────────────────────────────────
_, col, _ = st.columns([1, 14, 1])
with col:
    selected_movie_name = st.selectbox("movie", movies['title'].values, label_visibility="collapsed")
    clicked = st.button("FIND MATCHES  →")


# ─── RESULTS ────────────────────────────────────────────────────────────────────
if clicked:
    with st.spinner("Scanning the vault…"):
        names, posters = recommend(selected_movie_name)

    if names and posters:
        st.markdown("""
        <div class="cm-divider">
            <div class="cm-divider-label">Recommended for you</div>
            <div class="cm-divider-line"></div>
        </div>
        """, unsafe_allow_html=True)

        ordinals = ["01", "02", "03", "04", "05"]
        cards = '<div class="cm-grid">'
        for i, (name, poster) in enumerate(zip(names, posters)):
            cards += f"""
            <div class="cm-card">
                <div class="cm-shine"></div>
                <img src="{poster}" alt="{name}" />
                <div class="cm-card-overlay">
                    <div class="cm-card-num">{ordinals[i]}</div>
                    <div class="cm-card-name">{name}</div>
                </div>
            </div>"""
        cards += '</div>'
        st.markdown(cards, unsafe_allow_html=True)
    else:
        st.error("Could not generate recommendations. Please try again.")