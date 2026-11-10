import streamlit as st
import pandas as pd
import os
from datetime import datetime
from backup import cift_yedekleme_yap

st.set_page_config(page_title="Hakediş & Teklif Paneli", page_icon="📈", layout="wide")

DB_FILE = "teklif_hakedis_db.csv"

# 🔑 KULLANICI ROLLERİ VE ŞİFRELERİ
KULLANICILAR = {
    "admin@firma.com": {"sifre": "1234", "rol": "Yönetici"},
    "personel@firma.com": {"sifre": "5678", "rol": "Personel"}
}

def veri_yukle():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    return pd.DataFrame(columns=["Tarih", "Tür", "Proje Adı", "Müşteri/Kurum", "Tutar (TL)", "Durum"])

def veri_kaydet(df):
    df.to_csv(DB_FILE, index=False, encoding="utf-8-sig")

df = veri_yukle()

if "giris_yapildi" not in st.session_state:
    st.session_state.giris_yapildi = False
    st.session_state.kullanici_adi = ""
    st.session_state.kullanici_rolu = ""

# ---------------- GİRİŞ EKRANI ----------------
if not st.session_state.giris_yapildi:
    st.subheader("🏗️ Fırat Yıldız Mühendislik - ERP Girişi")
    with st.form("giris_formu"):
        k_adi = st.text_input("E-Posta", placeholder="admin@firma.com veya personel@firma.com")
        sifre = st.text_input("Şifre", type="password")
        giri_butonu = st.form_submit_button("Sisteme Giriş Yap")
        
        if giri_butonu:
            if k_adi in KULLANICILAR and KULLANICILAR[k_adi]["sifre"] == sifre:
                st.session_state.giris_yapildi = True
                st.session_state.kullanici_adi = k_adi
                st.session_state.kullanici_rolu = KULLANICILAR[k_adi]["rol"]
                st.success("Başarıyla giriş yapıldı!")
                st.rerun()
            else:
                st.error("Hatalı kullanıcı adı veya şifre!")
else:
    # ---------------- SOL MENÜ (SIDEBAR) ----------------
    with st.sidebar:
        st.image("https://icons8.com", width=60)
        st.title("Yönetim Paneli")
        st.write(f"👤 **Kullanıcı:** {st.session_state.kullanici_adi}")
        st.write(f"🎖️ **Yetki Rolü:** {st.session_state.kullanici_rolu}")
        st.divider()
        
        # Kısıtlamaya göre menü oluşturma
        menü_secenekleri = ["📊 Genel Durum (Dashboard)"]
        if st.session_state.kullanici_rolu == "Yönetici":
            menü_secenekleri.append("➕ Yeni Kayıt Ekle")
            menü_secenekleri.append("⚙️ Yedekleme & Sistem")
            
        sayfa = st.radio("Menü", menü_secenekleri, index=0)
        st.divider()
        
        if st.button("🚪 Oturumu Kapat"):
            st.session_state.giris_yapildi = False
            st.rerun()

    # ---------------- 1. SAYFA: DASHBOARD (Herkes Görebilir) ----------------
    if sayfa == "📊 Genel Durum (Dashboard)":
        st.subheader("📊 Finansal Durum Özetleri")
        
        teklif_df = df[df["Tür"] == "Teklif"]
        hakedis_df = df[df["Tür"] == "Hakediş"]
        t_toplam = teklif_df["Tutar (TL)"].sum()
        h_toplam = hakedis_df["Tutar (TL)"].sum()
        t_onayli = teklif_df[teklif_df["Durum"] == "Onaylandı"]["Tutar (TL)"].sum()
        h_odenen = hakedis_df[hakedis_df["Durum"] == "Ödendi / Tahsil Edildi"]["Tutar (TL)"].sum()

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Toplam Teklif Hacmi", f"{t_toplam:,.2f} TL")
        m2.metric("Onaylanan Teklifler", f"{t_onayli:,.2f} TL", f"{((t_onayli/t_toplam*100) if t_toplam>0 else 0):.1f}% Onay")
        m3.metric("Toplam Hakediş Hacmi", f"{h_toplam:,.2f} TL")
        m4.metric("Tahsil Edilen Hakediş", f"{h_odenen:,.2f} TL", f"-{h_toplam - h_odenen:,.2f} TL Kalan")
        
        st.divider()
        col_grafik, col_filtre = st.columns()
        
        with col_filtre:
            st.write("🔍 **Hızlı Filtreleme**")
            secilen_tur = st.multiselect("İşlem Türü", ["Teklif", "Hakediş"], default=["Teklif", "Hakediş"])
            durumlar = list(df["Durum"].unique()) if len(df) > 0 else ["Beklemede", "Onaylandı"]
            secilen_durum = st.multiselect("Durum Filtresi", durumlar, default=durumlar)
            
        filtered_df = df[df["Tür"].isin(secilen_tur) & df["Durum"].isin(secilen_durum)]
        
        with col_grafik:
            if not filtered_df.empty:
                grafik_data = filtered_df.groupby("Tür")["Tutar (TL)"].sum()
                st.bar_chart(grafik_data, color="#3b82f6")
            else:
                st.caption("Veri bulunamadı.")

        st.subheader("📋 Güncel İşlem Listesi")
        st.dataframe(filtered_df.sort_index(ascending=False), use_container_width=True)

    # ---------------- 2. SAYFA: YENİ KAYIT EKLE (Sadece Yönetici) ----------------
    elif sayfa == "➕ Yeni Kayıt Ekle" and st.session_state.kullanici_rolu == "Yönetici":
        st.subheader("➕ Yeni Teklif / Hakediş Giriş Formu")
        with st.form("yeni_islem_formu", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                tur = st.selectbox("İşlem Türü", ["Teklif", "Hakediş"])
                proje_adi = st.text_input("Proje / İş Adı")
                musteri = st.text_input("Müşteri / Kurum")
            with c2:
                tutar = st.number_input("İşlem Tutarı (TL)", min_value=0.0, format="%.2f")
                durum_opsiyonlari = ["Beklemede", "Onaylandı", "Reddedildi", "Ödendi / Tahsil Edildi"]
                durum = st.selectbox("Güncel Durum", durum_opsiyonlari)
                
            kaydet_btn = st.form_submit_button("Formu Onayla ve Buluta Yedekle")
            
            if kaydet_btn:
                if not proje_adi or not musteri:
                    st.error("Alanlar boş bırakılamaz!")
                else:
                    yeni_satir = {
                        "Tarih": datetime.now().strftime("%Y-%m-%d %H:%M"), "Tür": tur,
                        "Proje Adı": proje_adi, "Müşteri/Kurum": musteri, "Tutar (TL)": tutar, "Durum": durum
                    }
                    df = pd.concat([df, pd.DataFrame([yeni_satir])], ignore_index=False)
                    veri_kaydet(df)
                    
                    yedek_notu = cift_yedekleme_yap()
                    st.success("✅ Veri bulut veritabanına işlendi!")
                    st.info(yedek_notu)

    # ---------------- 3. SAYFA: SİSTEM AYARLARI (Sadece Yönetici) ----------------
    elif sayfa == "⚙️ Yedekleme & Sistem" and st.session_state.kullanici_rolu == "Yönetici":
        st.subheader("⚙️ Sistem Altyapısı ve Manuel İşlemler")
        st.metric("Toplam Kayıtlı Satır Sayısı", len(df))
        if st.button("Şimdi Manuel Google Drive Yedeği Al"):
            sonuc = cift_yedekleme_yap()
            st.success(sonuc)
