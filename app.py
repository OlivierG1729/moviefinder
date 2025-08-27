############################
# User interface           #
#                          #
# Last update : 2025/08/25 #
############################

############################
# User interface           #
#                          #
# Last update : 2025/08/27 #
############################

import math
import streamlit as st
from services.search import run_search, DEFAULT_ORDER
from services.i18n import detect_lang, translate_to_fr, lang_badge_html
from services import paid_static

# ──────────────────────────────────────────────────────────────────────────────
# Config
# ──────────────────────────────────────────────────────────────────────────────
st.set_page_config(page_title="🎬 Movie Finder : agrégateur légal de films", page_icon="🎬", layout="wide")
st.title("🎬 Movie Finder : agrégateur légal de films")
st.write("""
Cette application agrège **uniquement** des sources *légales* :
- priorité aux contenus **gratuits** (ex. Archive.org).
- en 2ᵉ choix : **liens officiels payants** (redirection).
- **aucun contournement** de protection ; **téléchargement** seulement si permis par la source.

**Téléchargement & emplacement :** le bouton *Télécharger* ouvre la page du fournisseur ;
votre **navigateur** vous proposera l’emplacement sur **votre disque**.
""")

# ──────────────────────────────────────────────────────────────────────────────
# Session state
# ──────────────────────────────────────────────────────────────────────────────
if "page_free" not in st.session_state:
    st.session_state.page_free = 1
if "loaded" not in st.session_state:
    st.session_state.loaded = False
if "loaded_params" not in st.session_state:
    st.session_state.loaded_params = {}
if "results_data" not in st.session_state:
    st.session_state.results_data = {}
if "last_query_text" not in st.session_state:
    st.session_state.last_query_text = ""

# ──────────────────────────────────────────────────────────────────────────────
# Widgets
# ──────────────────────────────────────────────────────────────────────────────
query = st.text_input("Rechercher un film…", placeholder="ex: Nosferatu, Buster Keaton, western muet", key="query")

mode_label = st.radio(
    "Type de contenu",
    ["Films", "Autres", "Tout"],
    help="Films : vidéos/long-métrages. Autres : tout sauf films. Tout : sans filtre.",
    horizontal=True,
)
MODE_MAP = {"Films": "films", "Autres": "autres", "Tout": "tout"}
mode = MODE_MAP[mode_label]

per_page = st.slider("Éléments par page", 5, 50, 12)

with st.sidebar:
    st.header("Options")
    enrich_tmdb = st.checkbox("Enrichir avec TMDB (affiches)", value=True)
    providers = st.multiselect(
        "Providers (ordre = priorité)",
        DEFAULT_ORDER,
        default=DEFAULT_ORDER,
        help="L'ordre définit aussi la priorité d'affichage",
        key="providers_sel",   # ← clé explicite
    )
    include_sub = st.checkbox("Inclure les offres d'abonnement", value=False)
    auto_translate = st.checkbox("Traduire automatiquement les résumés en français", value=True)
    st.caption("Définissez YOUTUBE_API_KEY / TMDB_API_KEY dans les secrets Streamlit (Cloud) ou .streamlit/secrets.toml (local).")

# ──────────────────────────────────────────────────────────────────────────────
# Cache
# ──────────────────────────────────────────────────────────────────────────────
@st.cache_data(show_spinner=False, ttl=600)
def cached_search(q: str, order: tuple[str, ...], enrich: bool, mode: str, include_sub: bool):
    return run_search(
        q,
        max_results=50,
        order=list(order),
        enrich_tmdb=enrich,
        mode=mode,
        include_subscriptions=include_sub,
    )

# ──────────────────────────────────────────────────────────────────────────────
# Bouton Rechercher seulement quand la requête change
# ──────────────────────────────────────────────────────────────────────────────
current_params = {
    "query": (query or "").strip(),
    "providers": tuple(st.session_state.get("providers_sel", DEFAULT_ORDER)),  # ← lit la valeur du multiselect
    "enrich_tmdb": bool(enrich_tmdb),
    "mode": mode,
    "include_sub": bool(include_sub),
}

query_changed = current_params["query"] != st.session_state.last_query_text
non_query_changed = (
    st.session_state.loaded and
    (current_params["providers"] != tuple(st.session_state.loaded_params.get("providers", ())) or
     current_params["enrich_tmdb"] != st.session_state.loaded_params.get("enrich_tmdb") or
     current_params["mode"] != st.session_state.loaded_params.get("mode") or
     current_params["include_sub"] != st.session_state.loaded_params.get("include_sub"))
)

col_btn, col_info = st.columns([1, 3])
with col_btn:
    do_search = st.button("Rechercher", use_container_width=True, disabled=(not current_params["query"]))
with col_info:
    if query_changed and current_params["query"]:
        st.caption("Nouvelle requête détectée → cliquez sur **Rechercher** pour lancer la recherche.")
    elif not current_params["query"]:
        st.caption("Saisissez une requête puis cliquez sur **Rechercher**.")

should_run_now = (
    (do_search and current_params["query"]) or
    (non_query_changed and current_params["query"]) or
    (not st.session_state.loaded and current_params["query"])
)

if should_run_now:
    with st.spinner("Recherche en cours…"):
        data = cached_search(
            current_params["query"],
            current_params["providers"],
            current_params["enrich_tmdb"],
            current_params["mode"],
            current_params["include_sub"],
        )
    st.session_state.results_data = data
    st.session_state.loaded = True
    st.session_state.loaded_params = {
        "providers": current_params["providers"],
        "enrich_tmdb": current_params["enrich_tmdb"],
        "mode": current_params["mode"],
        "include_sub": current_params["include_sub"],
    }
    if do_search or not st.session_state.last_query_text:
        st.session_state.page_free = 1
        st.session_state.last_query_text = current_params["query"]

# ──────────────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────────────
def _unpack_translate(res):
    """
    Accepte (str) | (txt, ok) | (txt, ok, lang) | (txt, ok, lang, …)
    → renvoie (txt, ok, lang).
    """
    txt, ok, lang = "", False, None
    if isinstance(res, (tuple, list)):
        if len(res) >= 1: txt = res[0]
        if len(res) >= 2: ok = bool(res[1])
        if len(res) >= 3: lang = res[2]
    else:
        txt, ok = str(res), True
    return txt, ok, lang

def _cmp_key(t: str) -> str:
    import re, html as _html
    t = _html.unescape(t).replace("\u200b", "").strip()
    t = re.sub(r"[ \t]+", " ", t)
    t = re.sub(r"\s*\n\s*", "\n", t).casefold()
    t = re.sub(r"\s+", " ", t)
    return t

def _card(movie, auto_translate: bool):
    cols = st.columns([1, 3])
    with cols[0]:
        if movie.poster_url:
            st.image(movie.poster_url, use_container_width=True)
    with cols[1]:
        header_cols = st.columns([6, 1])
        with header_cols[0]:
            st.markdown(f"### {movie.title}")
        with header_cols[1]:
            # échantillon plus riche pour la détection (titre + résumé)
            desc = movie.description
            if isinstance(desc, list):
                desc = " ".join([str(x) for x in desc if x])
            desc = (desc or "")
            sample_text = f"{movie.title}\n{desc}"
            st.markdown(lang_badge_html(sample_text), unsafe_allow_html=True)

        meta = []
        if movie.year:
            meta.append(str(movie.year))
        meta.append(movie.source)
        st.caption(" · ".join([x for x in meta if x]))

        # Description + traduction
        if movie.description:
            desc = movie.description
            if isinstance(desc, list):
                desc = " ".join([str(x) for x in desc if x])
            desc = (desc or "").strip()

            if auto_translate:
                # Traduire si détection ≠ fr OU inconnue
                code = detect_lang(f"{movie.title}\n{desc}")
                need_translate = (code != "fr") or (code is None)
                if need_translate:
                    translated, ok, _ = _unpack_translate(translate_to_fr(desc))
                    if ok and translated and (_cmp_key(translated) != _cmp_key(desc)):
                        with st.expander("Traduction (FR)"):
                            st.write(translated)
                        with st.expander("Texte original"):
                            st.write(desc[:2000] + ("…" if len(desc) > 2000 else ""))
                    else:
                        st.write(desc[:800] + ("…" if len(desc) > 800 else ""))
                else:
                    st.write(desc[:800] + ("…" if len(desc) > 800 else ""))
            else:
                st.write(desc[:800] + ("…" if len(desc) > 800 else ""))

        # Actions
        btns = st.columns(3)
        if movie.stream_url:
            with btns[0]:
                st.link_button("Visionner", movie.stream_url)
        if movie.download_url:
            with btns[1]:
                st.link_button("Télécharger", movie.download_url)
        with btns[2]:
            if movie.stream_url:
                st.code(movie.stream_url)

def _paginate(items, page, per_page):
    total = len(items)
    total_pages = max(1, int((total + per_page - 1) // per_page))
    page = max(1, min(page, total_pages))
    start = (page - 1) * per_page
    end = start + per_page
    return items[start:end], page, total_pages, total

# ──────────────────────────────────────────────────────────────────────────────
# Affichage des résultats
# ──────────────────────────────────────────────────────────────────────────────
if st.session_state.loaded and st.session_state.results_data:
    free_keys = [k for k in current_params["providers"] if k != "paid"]
    free_all = []
    for k in free_keys:
        free_all.extend(st.session_state.results_data.get(k, []))

    st.subheader("Résultats – Gratuit")
    if not free_all:
        st.caption("(aucun résultat gratuit)")
    else:
        page_items, st.session_state.page_free, total_pages, total = _paginate(
            free_all, st.session_state.page_free, per_page
        )

        nav1, info, nav2 = st.columns([1, 2, 1])
        with nav1:
            if st.button("⬅️ Précédent", disabled=(st.session_state.page_free <= 1), key="prev_free_btn"):
                st.session_state.page_free -= 1
        with info:
            st.write(f"Page {st.session_state.page_free} / {total_pages} — {total} éléments")
        with nav2:
            if st.button("Suivant ➡️", disabled=(st.session_state.page_free >= total_pages), key="next_free_btn"):
                st.session_state.page_free += 1

        for m in page_items:
            _card(m, auto_translate)

    # ——— Section payante (après la partie “Résultats – Gratuit”) ———
    if "paid" in current_params["providers"] and current_params["mode"] != "autres":
        st.subheader("Pistes – Payant (achat/location confirmés)")
        paid_list = st.session_state.results_data.get("paid", []) or []

        if paid_list:
            for m in paid_list:
                _card(m, auto_translate)
        else:
            st.caption("Aucune plateforme payante confirmée (achat/location) pour ce titre en FR via JustWatch.")
            # ✅ Mode hybride : l’utilisateur peut choisir d’afficher des liens de recherche génériques
            with st.expander("Afficher aussi des liens de recherche génériques (JustWatch, YouTube VOD)"):
                if current_params["query"]:
                    fallbacks = paid_static.search(current_params["query"], max_results=6, country="FR")
                    for m in fallbacks:
                        cols = st.columns([3, 1])
                        with cols[0]:
                            st.markdown(f"**{m.title}**")
                            st.caption(m.description)
                        with cols[1]:
                            st.link_button("Ouvrir", m.stream_url, use_container_width=True)
                else:
                    st.info("Saisissez une requête pour voir des liens de recherche génériques.")

else:
    st.info("Entrez une requête puis cliquez sur **Rechercher** pour lancer la première recherche.")

# ──────────────────────────────────────────────────────────────────────────────
# Bouton reset (réinitialise les options UI)
# ──────────────────────────────────────────────────────────────────────────────
if st.sidebar.button("Réinitialiser options"):
    st.session_state.pop("providers_sel", None)  # vide le multiselect
    st.session_state.page_free = 1
    st.rerun()

# ──────────────────────────────────────────────────────────────────────────────
# Debug temporaire (sécurisé)
# ──────────────────────────────────────────────────────────────────────────────
with st.expander("🔧 Debug (temporaire)"):
    res = st.session_state.results_data or {}
    st.write("Providers actifs:", current_params["providers"])
    st.write("Mode:", current_params["mode"])
    st.write("Clés résultats:", list(res.keys()))
    st.write("Nb options payantes:", len(res.get("paid", [])))


