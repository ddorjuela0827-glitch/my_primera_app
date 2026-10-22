import streamlit as st
import pandas as pd
import pydeck as pdk
import math
from urllib.parse import quote

st.set_page_config(page_title="Entregas Bogotá Pro", layout="wide")
st.title("📦 Red de Entregas Bogotá - PRO")

@st.cache_data
def get_bogota_data():
    data = {
        "Usaquén": [4.6951, -74.0308, 5000],
        "Chapinero": [4.64, -74.063, 4000],
        "Santa Fe": [4.601, -74.072, 4000],
        "San Cristóbal": [4.571, -74.083, 7000],
        "Usme": [4.469, -74.11, 9000],
        "Tunjuelito": [4.572, -74.132, 6000],
        "Bosa": [4.612, -74.183, 8000],
        "Kennedy": [4.629, -74.155, 6000],
        "Fontibón": [4.678, -74.145, 6000],
        "Engativá": [4.702, -74.12, 5000],
        "Suba": [4.761, -74.091, 5000],
        "Barrios Unidos": [4.671, -74.078, 4000],
        "Teusaquillo": [4.633, -74.075, 4000],
        "Mártires": [4.605, -74.087, 4000],
        "Antonio Nariño": [4.588, -74.101, 5000],
        "Puente Aranda": [4.613, -74.117, 5000],
        "Candelaria": [4.596, -74.076, 4000],
        "Rafael Uribe": [4.566, -74.113, 6000],
        "Ciudad Bolívar": [4.5, -74.14, 9000],
        "Sumapaz": [4.2, -74.3, 15000]
    }
    rows = []
    for loc, (lat, lon, base) in data.items():
        rows.append({"localidad": loc, "lat": lat, "lon": lon, "base": base})
    return pd.DataFrame(rows)

df_bogota = get_bogota_data()

with st.sidebar:
    st.header("Cotizar Envío")
    origen = st.selectbox("Origen", df_bogota["localidad"].tolist(), index=10)
    destino = st.selectbox("Destino", df_bogota["localidad"].tolist(), index=18)
    peso = st.number_input("Peso (kg)", 1, 50, 2)
    cotizar = st.button("🚀 Calcular Ruta", type="primary")

if cotizar:
    o = df_bogota[df_bogota.localidad == origen].iloc[0]
    d = df_bogota[df_bogota.localidad == destino].iloc[0]
    dist = math.sqrt((o.lat - d.lat)**2 + (o.lon - d.lon)**2) * 111
    total = d.base + (peso * 2000) + (dist * 500)

    c1, c2, c3 = st.columns(3)
    c1.metric("Distancia", f"{dist:.1f} km")
    c2.metric("Peso", f"{peso} kg")
    c3.metric("Total", f"${int(total):,} COP")

    route_df = pd.DataFrame([
        {"lat": o.lat, "lon": o.lon, "color": [0, 200, 0]},
        {"lat": d.lat, "lon": d.lon, "color": [255, 0, 0]}
    ])
    layers = [
        pdk.Layer("ScatterplotLayer", df_bogota, get_position='[lon, lat]', get_color='[200,200,200,60]', get_radius=300),
        pdk.Layer("ScatterplotLayer", route_df, get_position='[lon, lat]', get_color='color', get_radius=500),
        pdk.Layer("LineLayer", pd.DataFrame([{"s_lat": o.lat, "s_lon": o.lon, "t_lat": d.lat, "t_lon": d.lon}]), get_source_position='[s_lon, s_lat]', get_target_position='[t_lon, t_lat]', get_color='[0, 100, 255]', get_width=5)
    ]
    view = pdk.ViewState(latitude=(o.lat+d.lat)/2, longitude=(o.lon+d.lon)/2, zoom=11)
    deck = pdk.Deck(layers=layers, initial_view_state=view, map_style="light", tooltip={"text": "{localidad}"})
    st.pydeck_chart(deck, use_container_width=True)
    
    st.success(f"Ruta: {origen} → {destino}")
    
    # Boton WhatsApp que SI funciona en cualquier version
    msg = f"Hola! Cotización Entregas Bogotá:\nOrigen: {origen}\nDestino: {destino}\nDistancia: {dist:.1f} km\nPeso: {peso} kg\nTotal: ${int(total):,} COP"
    wa_link = f"https://wa.me/?text={quote(msg)}"
    
    st.markdown(f"""
    <a href="{wa_link}" target="_blank" style="text-decoration:none;">
        <div style="background-color:#25D366;color:white;padding:14px;text-align:center;border-radius:10px;font-weight:bold;font-size:18px;">
            📲 Enviar cotización por WhatsApp
        </div>
    </a>
    """, unsafe_allow_html=True)
    
else:
    st.info("👈 Cotiza a la izquierda")
    layer_all = pdk.Layer("ScatterplotLayer", df_bogota, get_position='[lon, lat]', get_color='[255, 0, 0, 120]', get_radius=400, pickable=True)
    view_all = pdk.ViewState(latitude=4.65, longitude=-74.10, zoom=10.5)
    deck_all = pdk.Deck(layers=[layer_all], initial_view_state=view_all, map_style="light", tooltip={"text": "{localidad}\nBase: ${base}"})
    st.pydeck_chart(deck_all, use_container_width=True)