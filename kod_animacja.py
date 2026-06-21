import streamlit as st
import numpy as np
import pandas as pd
from scipy.stats import norm

# --- KONFIGURACJA STRONY ---
st.set_page_config(page_title="Symulator Opcji Quanto", layout="wide")
st.title("Interaktywny Symulator: Model 1 vs Model 2")

T = 1.0

# cena dla pierwszej kropki:
def price1(K, r_pln, r_usd, rho, sigma_x, sigma_s, t=0, T=1, C=100):
    q = r_pln - r_usd + rho * sigma_s * sigma_x
    r_hat = r_pln - q
    d1 = (-np.log(K) + (r_hat + 0.5 * sigma_s ** 2) * (T-t)) / (sigma_s * np.sqrt(T-t))
    d2 = d1 - sigma_s * np.sqrt(T-t)

    cena = C * (np.exp((-q) * (T-t)) * norm.cdf(d1) - K * np.exp(-r_pln * (T-t)) * norm.cdf(d2))
    return cena

# cena dla drugiej kropki:
def price2(K, r_pln, r_usd, sigma_y, sigma_x, rho, t=0, T=1, C=100):
    q = r_pln - r_usd - sigma_x ** 2 + rho * sigma_y * sigma_x
    sigma_z = np.sqrt(sigma_y ** 2 + sigma_x ** 2 - 2 * rho * sigma_y * sigma_x)
    r_hat = r_pln - q

    d1 = (-np.log(K) + (r_hat + 0.5 * sigma_z ** 2) * (T-t)) / (sigma_z * np.sqrt(T-t))
    d2 = d1 - sigma_z * np.sqrt(T-t)

    cena = C * (np.exp((-q) * (T-t)) * norm.cdf(d1) - K * np.exp(-r_pln * (T-t)) * norm.cdf(d2))
    return cena

# --- PANEL BOCZNY (SUWAKI) ---
st.sidebar.header("Parametry Rynkowe")
sigma_s = st.sidebar.slider("Zmienność Złota w USD (σ_S)", min_value=0.01, max_value=0.40, value=0.1331, step=0.01)
sigma_x = st.sidebar.slider("Zmienność USDPLN (σ_X)", min_value=0.01, max_value=0.40, value=0.1015, step=0.01)
sigma_y = st.sidebar.slider("Zmienność Złota w PLN (σ_Y)", min_value=0.01, max_value=0.40, value=0.1340, step=0.01)
st.sidebar.markdown("---")
rho_sx = st.sidebar.slider("Korelacja Złoto w USD & USDPLN (ρ_SX)", min_value=-1.0, max_value=1.0, value=-0.3741, step=0.01)
rho_xy = st.sidebar.slider("Korelacja Złoto w PLN & USDPLN (ρ_XY)", min_value=-1.0, max_value=1.0, value=0.3848, step=0.01)
st.sidebar.markdown("---")
r_pln = st.sidebar.slider("Stopa krajowa $r_{PLN}$", min_value=0.0, max_value=0.15, value=0.05, step=0.01)
r_usd = st.sidebar.slider("Stopa zagraniczna $r_{USD}$", min_value=0.0, max_value=0.15, value=0.042, step=0.01)


# --- OBLICZENIA DLA WYKRESU ---
K_array = np.linspace(0.5, 1.5, 100)
# Wektoryzacja tablic do biblioteki Pandas
df = pd.DataFrame({'Cena Wykonania (K)': K_array})
df['Model 1'] = df['Cena Wykonania (K)'].apply(lambda k: price1(k, r_pln, r_usd, rho_sx, sigma_x, sigma_s))
df['Model 2'] = df['Cena Wykonania (K)'].apply(lambda k: price2(k, r_pln, r_usd, sigma_y, sigma_x, rho_xy))

# Ustawiamy K jako indeks, żeby Streamlit ładnie podpisał oś X
df.set_index('Cena Wykonania (K)', inplace=True)

# --- WYŚWIETLANIE DANYCH ---
# 1. Główny wykres
st.subheader("Profil wyceny opcji w zależności od ceny wykonania (K)")
st.line_chart(df, height=400)

# 2. Obliczenia dla At-The-Money (K=1.0)
cena_q_atm = price1(1.0, r_pln, r_usd, rho_sx, sigma_x, sigma_s)
cena_h_atm = price2(1.0, r_pln, r_usd, sigma_y, sigma_x, rho_xy)

st.markdown("---")
st.subheader("Wycena opcji dla K=1.0")

# 3. Kafelki (Metryki)
col1, col2, col3 = st.columns(3)
col1.metric(label="Model 1", value=f"{cena_q_atm:.4f} PLN")
col2.metric(label="Model 2", value=f"{cena_h_atm:.4f} PLN")
col3.metric(label="Różnica", value=f"{abs(cena_q_atm - cena_h_atm):.4f} PLN")