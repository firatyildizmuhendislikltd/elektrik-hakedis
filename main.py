import streamlit as st
import pandas as pd
import os
from datetime import datetime

# Veri tabanı dosyası
DATA_FILE = "hakedis_verileri.csv"

# Eğer dosya yoksa yeni şablon oluştur (Yeni sütunlar eklendi: Fatura Durumu)
if not os.path.exists(DATA_FILE):
    df = pd.DataFrame(columns=["Tarih", "Proje Adı", "Kategori", "İş Kalemi", "Birim", "Birim Fiyat", "Miktar", "Toplam Tutar", "Fatura Durumu", "Giren Personel"])
    df.to_csv(DATA_FILE, index=False)

st.set_page_config(page_title="Pro Elektrik Finansal Hakediş", layout="wide", page_icon="⚡")

# --- SİSTEM GİRİŞ KONTROLÜ (GÜVENLİK) ---
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    st.subheader("🔒 Elektrik Taahhüt Hakediş & Finans Sistemi Girişi")
    username = st.text_input("Kullanıcı Adı")
    password = st.text_input("Şifre", type="password")
    if st.button("Giriş Yap"):
        if username == "admin" and password == "elektrik2026":
            st.session_state["authenticated"] = True
            st.rerun()
        else:
            st.error("Hatalı kullanıcı adı veya şifre!")
    st.stop()

# --- ANA PROGRAM ---
st.title("⚡ Elektrik Taahhüt Canlı Hakediş, Fatura & Bakiye Takip Sistemi")

# Çıkış Yap Butonu
if st.sidebar.button("🚪 Sistemden Güvenli Çıkış"):
    st.session_state["authenticated"] = False
    st.rerun()

# --- SOL PANEL: GELİŞMİŞ VERİ GİRİŞ FORMU ---
st.sidebar.header("📝 Yeni İmalat / Hakediş Girişi")

is_kategorileri = {
    "Kuvvetli Akım Tesisatı": ["Kablo Çekimi (3x2.5 NYM)", "Kablo Çekimi (4x16 NYY)", "Kablo Kanalı Montajı", "Ana Pano Montajı", "Sayaç Panosu Montajı", "Topraklama Şeridi Serilmesi"],
    "Zayıf Akım Tesisatı": ["CCTV Kamera Montajı", "Yangın İhbar Butonu", "Optik Duman Dedektörü", "Data Kablosu Çekimi (Cat6)", "Merkezi Uydu Santrali"],
    "Aydınlatma & Anahtar Grubu": ["LED Armatür Montajı", "Sıva Altı Anahtar/Priz", "Acil Yönlendirme Armatürü", "Dış Aydınlatma Direği"]
}

with st.sidebar.form(key="hakedis_formu", clear_on_submit=True):
    tarih = st.date_input("İmalat Tarihi", value=datetime.now())
    proje = st.selectbox("Proje Seçin", ["X Konut Projesi", "Y Fabrika İnşaatı", "Z Alışveriş Merkezi", "Diğer"])
    kategori = st.selectbox("İş Kategorisi", list(is_kategorileri.keys()))
    is_kalemi = st.selectbox("İş Kalemi / Malzeme", is_kategorileri[kategori])
    birim = st.selectbox("Birim", ["Metre", "Adet", "Takım", "Kg", "Lot"])
    birim_fiyat = st.number_input("Sözleşme Birim Fiyatı (TL)", min_value=0.0, format="%.2f")
    miktar = st.number_input("Sahada Yapılan Metraj / Miktar", min_value=0.0, format="%.2f")
    
    # YENİ: Fatura Durumu Seçimi
    fatura_durumu = st.selectbox("Fatura Durumu", [
        "Fatura Kesilmedi", 
        "Fatura Kesildi - Ödeme Bekliyor", 
        "Fatura Kesildi - Ödeme Alındı"
    ])
    
    personel = st.text_input("Giriş Yapan Yetkili", placeholder="Örn: Ahmet Şef")
    submit_button = st.form_submit_button(label="💾 Hakediş ve Fatura Kaydet")

if submit_button:
    toplam = miktar * birim_fiyat
    yeni_veri = pd.DataFrame([[tarih.strftime('%Y-%m-%d'), proje, kategori, is_kalemi, birim, birim_fiyat, miktar, toplam, fatura_durumu, personel]], 
                             columns=["Tarih", "Proje Adı", "Kategori", "İş Kalemi", "Birim", "Birim Fiyat", "Miktar", "Toplam Tutar", "Fatura Durumu", "Giren Personel"])
    
    df_current = pd.read_csv(DATA_FILE)
    df_updated = pd.concat([df_current, yeni_veri], ignore_index=True)
    df_updated.to_csv(DATA_FILE, index=False)
    st.sidebar.success("Veriler ve fatura durumu başarıyla kaydedildi!")

# --- ANA PANEL: FINANSAL RAPORLAMA ---
df_display = pd.read_csv(DATA_FILE)

# Sözleşme Değeri Girişi (Kullanıcı dinamik olarak sözleşme bedelini girebilir)
st.markdown("### 📑 Sözleşme ve Proje Ayarları")
sc1, sc2 = st.columns(2)
with sc1:
    proje_secimi = st.selectbox("Finansal Analiz İçin Proje Seçin", options=df_display["Proje Adı"].unique() if not df_display.empty else ["Proje Yok"])
with sc2:
    sozlesme_bedeli = st.number_input(f"{proje_secimi} Toplam Sözleşme Tutarı (TL)", min_value=0.0, value=2500000.0, step=50000.0, format="%.2f")

# Seçilen Projeye Göre Filtreleme
df_filtered = df_display[df_display["Proje Adı"] == proje_secimi]

if not df_filtered.empty:
    # Finansal Hesaplamalar
    toplam_hakedis = df_filtered["Toplam Tutar"].sum()
    kalan_bakiye = max(sozlesme_bedeli - toplam_hakedis, 0.0)
    
    fatura_kesilmeyen = df_filtered[df_filtered["Fatura Durumu"] == "Fatura Kesilmedi"]["Toplam Tutar"].sum()
    fatura_bekleyen = df_filtered[df_filtered["Fatura Durumu"] == "Fatura Kesildi - Ödeme Bekliyor"]["Toplam Tutar"].sum()
    tahsil_edilen = df_filtered[df_filtered["Fatura Durumu"] == "Fatura Kesildi - Ödeme Alındı"]["Toplam Tutar"].sum()

    # Üst Finans Metrikleri
    st.markdown("### 📊 Proje Finans Durum Kartları")
    m1, m2, m3 = st.columns(3)
    m1.metric(label="📜 Toplam Sözleşme Bedeli", value=f"{sozlesme_bedeli:,.2f} TL")
    m2.metric(label="🛠️ Toplam Hak Edilen (Yapılan İş)", value=f"{toplam_hakedis:,.2f} TL", delta=f"-{toplam_hakedis:,.2f} TL", delta_color="inverse")
    m3.metric(label="💰 Kalan Bakiye (Sözleşmeden Kalan)", value=f"{kalan_bakiye:,.2f} TL")

    st.markdown("---")
    st.markdown("### 🧾 Fatura ve Tahsilat Durumu")
    f1, f2, f3 = st.columns(3)
    f1.metric(label="🔴 Fatura Kesilecek Tutar", value=f"{fatura_kesilmeyen:,.2f} TL")
    f2.metric(label="🟡 Kesilen / Ödeme Bekleyen", value=f"{fatura_bekleyen:,.2f} TL")
    f3.metric(label="🟢 Tahsil Edilen (Kasa)", value=f"{tahsil_edilen:,.2f} TL")

    # İlerleme Çubuğu
    ilerleme_orani = min(float(toplam_hakedis / sozlesme_bedeli), 1.0) if sozlesme_bedeli > 0 else 0.0
    st.markdown(f"**🏗️ Sözleşme Tüketim Oranı:**")
    st.progress(ilerleme_orani, text=f"Sözleşmenin %{ilerleme_orani*100:.1f}'i hakedişe dönüştü.")

    # Canlı Tablo Ekranı
    st.subheader("📋 Güncel Hakediş & Fatura Listesi")
    st.dataframe(df_filtered, use_container_width=True)
    
    # Grafikler Bölümü
    st.subheader("📈 Finansal Dağılım Grafikleri")
    g1, g2 = st.columns(2)
    
    with g1:
        st.markdown("**Fatura Durumlarına Göre Tutar Dağılımı**")
        fatura_grafik = df_filtered.groupby("Fatura Durumu")["Toplam Tutar"].sum()
        st.bar_chart(fatura_grafik)
    with g2:
        st.markdown("**İş Kategorilerine Göre Harcanan Bütçe**")
        kat_grafik = df_filtered.groupby("Kategori")["Toplam Tutar"].sum()
        st.bar_chart(kat_grafik)
else:
    st.info(f"'{proje_secimi}' projesine ait henüz bir hakediş girişi yapılmamış. Sol taraftan bu proje adına veri girişi yapabilirsiniz.")
