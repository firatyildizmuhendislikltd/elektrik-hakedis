import streamlit as st
import pandas as pd
import os
from datetime import datetime

# Veri tabanı dosyası
DATA_FILE = "hakedis_verileri.csv"

# Eğer dosya yoksa yeni şablon oluştur
if not os.path.exists(DATA_FILE):
    df = pd.DataFrame(columns=["Tarih", "Proje Adı", "Kategori", "İş Kalemi", "Birim", "Birim Fiyat", "Miktar", "Toplam Tutar", "Fatura Durumu", "Giren Personel"])
    df.to_csv(DATA_FILE, index=False)

st.set_page_config(page_title="Fırat Yıldız Mühendislik ERP", layout="wide", page_icon="⚡")

# --- 👥 3 SEVİYELİ KULLANICI VERİ TABANI ---
# Buradaki e-posta ve şifreleri firmanıza göre düzenleyebilirsiniz.
KULLANICILAR = {
    "admin@firatyildiz.com": {
        "isim": "Fırat",
        "soyisim": "Yıldız",
        "sifre": "admin2026",
        "rol": "Admin"          # Tam yetki + Veri Silme Yetkisi
    },
    "ahmet@firatyildiz.com": {
        "isim": "Ahmet",
        "soyisim": "Aktaş",
        "sifre": "yonetici2026",
        "rol": "Yönetici"       # Finansal Görünüm + Fatura Takibi
    },
    "mehmet@firatyildiz.com": {
        "isim": "Mehmet",
        "soyisim": "Yılmaz",
        "sifre": "personel123",
        "rol": "Personel"       # Sadece şantiye veri girişi (Paraları göremez)
    }
}

# Oturum kontrolü
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
    st.session_state["user_info"] = {}

# --- GİRİŞ EKRANI ARAYÜZÜ ---
if not st.session_state["authenticated"]:
    st.subheader("🔒 Fırat Yıldız Mühendislik - Hakediş & ERP Girişi")
    
    email = st.text_input("E-Posta Adresiniz", placeholder="ornek@firatyildiz.com")
    sifre = st.text_input("Şifreniz", type="password")
    
    if st.button("Sisteme Giriş Yap"):
        if email in KULLANICILAR and KULLANICILAR[email]["sifre"] == sifre:
            st.session_state["authenticated"] = True
            st.session_state["user_info"] = KULLANICILAR[email]
            st.session_state["user_info"]["email"] = email
            st.rerun()
        else:
            st.error("Hatalı E-Posta veya Şifre girdiniz!")
    st.stop()

# --- ANA PROGRAM (GİRİŞ YAPILDIKTAN SONRA) ---
user = st.session_state["user_info"]

# Üst Bilgilendirme ve Çıkış Butonu
col_user, col_logout = st.columns([4, 1])
col_user.markdown(f"👤 **Kullanıcı:** {user['isim']} {user['soyisim']} | 🎭 **Yetki Seviyesi:** `{user['rol']}`")
if col_logout.button("🚪 Güvenli Çıkış", use_container_width=True):
    st.session_state["authenticated"] = False
    st.session_state["user_info"] = {}
    st.rerun()

st.title("⚡ Elektrik Taahhüt Canlı Hakediş, Fatura & Bakiye Takip Sistemi")

# --- SOL PANEL: VERİ GİRİŞ FORMU (TÜM ROLLER YAPABİLİR) ---
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
    
    # 🎭 YETKİ KONTROLÜ (FATURA GİRİŞİ): Sadece Admin ve Yönetici fatura durumunu seçebilir.
    if user["rol"] in ["Admin", "Yönetici"]:
        fatura_durumu = st.selectbox("Fatura Durumu", ["Fatura Kesilmedi", "Fatura Kesildi - Ödeme Bekliyor", "Fatura Kesildi - Ödeme Alındı"])
    else:
        fatura_durumu = "Fatura Kesilmedi"
        st.info("ℹ️ Fatura takibi yetkiniz dışındadır. Otomatik 'Fatura Kesilmedi' olarak işlenecektir.")
        
    submit_button = st.form_submit_button(label="💾 Veriyi Kaydet")

if submit_button:
    toplam = miktar * birim_fiyat
    giren_kisi = f"{user['isim']} {user['soyisim']} ({user['rol']})"
    yeni_veri = pd.DataFrame([[tarih.strftime('%Y-%m-%d'), proje, kategori, is_kalemi, birim, birim_fiyat, miktar, toplam, fatura_durumu, giren_kisi]], 
                             columns=["Tarih", "Proje Adı", "Kategori", "İş Kalemi", "Birim", "Birim Fiyat", "Miktar", "Toplam Tutar", "Fatura Durumu", "Giren Personel"])
    
    df_current = pd.read_csv(DATA_FILE)
    df_updated = pd.concat([df_current, yeni_veri], ignore_index=True)
    df_updated.to_csv(DATA_FILE, index=False)
    st.sidebar.success("Veriler başarıyla sisteme işlendi!")

# --- ANA PANEL: RAPORLAMA VE FİLTRELER ---
df_display = pd.read_csv(DATA_FILE)

st.markdown("### 📑 Proje Seçimi")
proje_secimi = st.selectbox("Görüntülenecek Proje", options=df_display["Proje Adı"].unique() if not df_display.empty else ["Proje Yok"])
df_filtered = df_display[df_display["Proje Adı"] == proje_secimi]

# 🎭 1. FİNANSAL ALAN GÖRÜNÜMÜ (Sadece Admin ve Yönetici Görebilir)
if user["rol"] in ["Admin", "Yönetici"]:
    sozlesme_bedeli = st.number_input(f"{proje_secimi} Toplam Sözleşme Tutarı (TL)", min_value=0.0, value=2500000.0, step=50000.0, format="%.2f")
    
    if not df_filtered.empty:
        toplam_hakedis = df_filtered["Toplam Tutar"].sum()
        kalan_bakiye = max(sozlesme_bedeli - toplam_hakedis, 0.0)
        fatura_kesilmeyen = df_filtered[df_filtered["Fatura Durumu"] == "Fatura Kesilmedi"]["Toplam Tutar"].sum()
        fatura_bekleyen = df_filtered[df_filtered["Fatura Durumu"] == "Fatura Kesildi - Ödeme Bekliyor"]["Toplam Tutar"].sum()
        tahsil_edilen = df_filtered[df_filtered["Fatura Durumu"] == "Fatura Kesildi - Ödeme Alındı"]["Toplam Tutar"].sum()

        st.markdown("### 📊 Proje Finans Durum Kartları")
        m1, m2, m3 = st.columns(3)
        m1.metric(label="📜 Toplam Sözleşme Bedeli", value=f"{sozlesme_bedeli:,.2f} TL")
        m2.metric(label="🛠️ Toplam Hak Edilen Tutar", value=f"{toplam_hakedis:,.2f} TL")
        m3.metric(label="💰 Kalan Bakiye", value=f"{kalan_bakiye:,.2f} TL")

        st.markdown("### 🧾 Fatura ve Tahsilat Durumu")
        f1, f2, f3 = st.columns(3)
        f1.metric(label="🔴 Fatura Kesilecek Tutar", value=f"{fatura_kesilmeyen:,.2f} TL")
        f2.metric(label="🟡 Kesilen / Ödeme Bekleyen", value=f"{fatura_bekleyen:,.2f} TL")
        f3.metric(label="🟢 Tahsil Edilen (Kasa)", value=f"{tahsil_edilen:,.2f} TL")
        st.markdown("---")

# --- TABLO VE VERİ GÖSTERİM ALANI ---
if not df_filtered.empty:
    st.subheader("📋 Güncel İmalat & Hakediş Listesi")
    
    # 🎭 2. TABLO GÖRÜNÜM KONTROLÜ
    if user["rol"] in ["Admin", "Yönetici"]:
        # Admin ve Yönetici parasal sütunlar dahil her şeyi görür
        st.dataframe(df_filtered, use_container_width=True)
        
        # 🔒 3. VERİ SİLME ALANI (Sadece Admin Görebilir ve Yapabilir)
        if user["rol"] == "Admin":
            st.markdown("### 🗑️ Admin Veri Düzenleme (Kayıt Silme)")
            silinecek_index = st.number_input("Silmek istediğiniz satırın sol başındaki indeksi (Numarayı) girin:", min_value=0, max_value=len(df_display)-1, step=1)
            if st.button("🚨 Seçili Satırı Kalıcı Olarak Sil"):
                df_to_delete = pd.read_csv(DATA_FILE)
                df_to_delete = df_to_delete.drop(silinecek_index).reset_index(drop=True)
                df_to_delete.to_csv(DATA_FILE, index=False)
                st.success(f"{silinecek_index} numaralı kayıt başarıyla silindi! Sayfa yenileniyor...")
                st.rerun()
    else:
        # Personel birim fiyat ve toplam tutarları göremez (Gizlilik)
        df_personel = df_filtered[["Tarih", "Proje Adı", "Kategori", "İş Kalemi", "Birim", "Miktar", "Giren Personel"]]
        st.dataframe(df_personel, use_container_width=True)
        st.info("🔒 Güvenlik politikası gereği parasal bütçe verileri personel yetkisine gizlenmiştir.")

    # Ortak Grafikler (Metraj Analizi)
    st.subheader("📈 İmalat Miktarları Analizi")
    st.bar_chart(df_filtered.groupby("İş Kalemi")["Miktar"].sum())
else:
    st.info("Bu projeye ait henüz bir imalat girişi bulunamadı.")
