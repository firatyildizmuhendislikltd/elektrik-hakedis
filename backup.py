import streamlit as st
import pandas as pd
from supabase import create_client, Client

@st.cache_resource
def baglanti_kur() -> Client:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

def verileri_google_sheets_yukle():
    basliklar = ["Tarih", "Tür", "Proje Adı", "Müşteri/Kurum", "Tutar", "KDV Oranı (%)", "KDV Tutarı", "KDV Dahil Toplam", "Para Birimi", "Durum", "Fatura Durumu", "Yönetici Onayı"]
    supabase = baglanti_kur()
    response = supabase.table("islemler").select("*").order("id").execute()
    if not response.data:
        return pd.DataFrame(columns=basliklar)
    df = pd.DataFrame(response.data)
    if "id" in df.columns:
        df = df.drop(columns=["id"])
    return df

def verileri_google_sheets_kaydet(df):
    supabase = baglanti_kur()
    supabase.table("islemler").delete().neq("id", 0).execute()
    if not df.empty:
        kayitlar = df.fillna("").to_dict(orient="records")
        supabase.table("islemler").insert(kayitlar).execute()
    return "☁️ Veriler kalıcı Supabase bulut veritabanına işlendi!"

def kullanicilari_google_sheets_yukle():
    supabase = baglanti_kur()
    response = supabase.table("kullanicilar").select("*").execute()
    kullanici_sozlugu = {}
    for row in response.data:
        kullanici_sozlugu[str(row["eposta"])] = {"sifre": str(row["sifre"]), "rol": str(row["rol"])}
    return kullanici_sozlugu

def kullanici_google_sheets_ekle(eposta, sifre, rol):
    supabase = baglanti_kur()
    mevcutlar = kullanicilari_google_sheets_yukle()
    if eposta in mevcutlar:
        return False
    supabase.table("kullanicilar").insert({"eposta": eposta, "sifre": str(sifre), "rol": rol}).execute()
    return True
