import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- VERİ TABANLARI (ÜCRETSİZ GÜVENLİ DEPOLAMA) ---
FILES = {
    "users": "erp_kullanicilar.csv",
    "cariler": "erp_cariler.csv",
    "hakedis": "erp_hakedis_verileri.csv",
    "depo": "erp_depo_takip.csv"
}

# Veri tabanı dosyalarını kontrol et ve yoksa oluştur
if not os.path.exists(FILES["users"]):
    pd.DataFrame([["admin@firatyildiz.com", "Fırat", "Yıldız", "admin2026", "Admin"]], 
                 columns=["Email", "İsim", "Soyisim", "Şifre", "Rol"]).to_csv(FILES["users"], index=False)

if not os.path.exists(FILES["cariler"]):
    pd.DataFrame([["X Konut Projesi", 2500000.0], ["Y Fabrika İnşaatı", 5000000.0]], 
                 columns=["Cari Adı", "Sözleşme Bedeli"]).to_csv(FILES["cariler"], index=False)

if not os.path.exists(FILES["hakedis"]):
    pd.DataFrame(columns=["Tarih", "Cari Adı", "Kategori", "İş Kalemi", "Birim", "Birim Fiyat", "Miktar", "Toplam Tutar", "Fatura Durumu", "Personel"]).to_csv(FILES["hakedis"], index=False)

if not os.path.exists(FILES["depo"]):
    pd.DataFrame(columns=["Tarih", "Cari Adı", "Malzeme Adı", "Birim", "Sabah Çıkan", "Akşam İade", "Net Harcanan", "Teslim Eden"]).to_csv(FILES["depo"], index=False)

st.set_page_config(page_title="Fırat Yıldız Mühendislik ERP", layout="wide", page_icon="⚡")

# --- 🔒 OTURUM VE GİRİŞ KONTROLÜ ---
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
    st.session_state["user_info"] = {}

if not st.session_state["authenticated"]:
    st.subheader("🔒 Fırat Yıldız Mühendislik - Tam Kapsamlı ERP Girişi")
    email_input = st.text_input("E-Posta Adresiniz")
    sifre_input = st.text_input("Şifreniz", type="password")
    
    if st.button("Sisteme Giriş Yap"):
        df_u = pd.read_csv(FILES["users"])
        user_row = df_u[(df_u["Email"] == email_input) & (df_u["Şifre"] == str(sifre_input))]
        if not user_row.empty:
            st.session_state["authenticated"] = True
            st.session_state["user_info"] = user_row.iloc[0].to_dict()
            st.rerun()
        else:
            st.error("Hatalı E-Posta veya Şifre!")
    st.stop()

# Giriş Yapan Kullanıcı Bilgisi
user = st.session_state["user_info"]
col_u, col_l = st.columns([4, 1])
col_u.markdown(f"👤 **Kullanıcı:** {user['İsim']} {user['Soyisim']} | 🎭 **Yetki:** `{user['Rol']}`")
if col_l.button("🚪 Çıkış Yap", use_container_width=True):
    st.session_state["authenticated"] = False
    st.session_state["user_info"] = {}
    st.rerun()

# --- 🧭 ANA MENÜ (SEKMELİ YAPI) ---
tab1, tab2, tab3, tab4 = st.tabs(["📊 Finans & Hakediş Paneli", "📦 Depo Giriş-Çıkış Takibi", "💼 Cari & İş Tanımlama", "👥 Personel Yönetimi"])

# ==========================================
# TAB 1: FİNANS & HAKEDİŞ PANELİ
# ==========================================
with tab1:
    st.header("📊 Canlı Hakediş ve Bakiye Raporlama")
    df_c = pd.read_csv(FILES["cariler"])
    df_h = pd.read_csv(FILES["hakedis"])
    
    cari_secim = st.selectbox("Raporlanacak Cari / İş Seçin", options=df_c["Cari Adı"].unique() if not df_c.empty else ["Cari Yok"])
    df_h_filtered = df_h[df_h["Cari Adı"] == cari_secim]
    
    # Finansal Hesaplamalar (Sadece Admin ve Yönetici Görebilir)
    if user["Rol"] in ["Admin", "Yönetici"]:
        sozlesme = df_c[df_c["Cari Adı"] == cari_secim]["Sözleşme Bedeli"].sum() if not df_c.empty else 0
        toplam_hakedis = df_h_filtered["Toplam Tutar"].sum()
        kalan_bakiye = max(sozlesme - toplam_hakedis, 0.0)
        
        m1, m2, m3 = st.columns(3)
        m1.metric("📜 Toplam Sözleşme Bedeli", f"{sozlesme:,.2f} TL")
        m2.metric("🛠️ Toplam Hak Edilen Tutar", f"{toplam_hakedis:,.2f} TL")
        m3.metric("💰 Kalan Cari Bakiye", f"{kalan_bakiye:,.2f} TL")
        st.markdown("---")

    # Yeni Hakediş Giriş Formu (Tüm Roller)
    st.subheader("📝 Yeni İmalat Girişi")
    with st.form("hakedis_form", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        tarih = c1.date_input("İmalat Tarihi")
        kat = c2.selectbox("Kategori", ["Kuvvetli Akım", "Zayıf Akım", "Aydınlatma"])
        is_kalemi = c3.text_input("Yapılan İş / Malzeme", placeholder="Örn: 3x2.5 Kablo Çekimi")
        
        c4, c5, c6 = st.columns(3)
        birim = c4.selectbox("Birim ", ["Metre", "Adet", "Takım", "Lot"])
        b_fiyat = c5.number_input("Birim Fiyat (TL)", min_value=0.0)
        miktar = c6.number_input("Miktar / Metraj", min_value=0.0)
        
        f_durum = "Fatura Kesilmedi"
        if user["Rol"] in ["Admin", "Yönetici"]:
            f_durum = st.selectbox("Fatura Durumu", ["Fatura Kesilmedi", "Fatura Kesildi - Ödeme Bekliyor", "Fatura Kesildi - Ödeme Alındı"])
            
        if st.form_submit_button("💾 Hakedişi Veri Tabanına İşle"):
            toplam = miktar * b_fiyat
            personel_adi = f"{user['İsim']} {user['Soyisim']}"
            yeni_h = pd.DataFrame([[tarih.strftime('%Y-%m-%d'), cari_secim, kat, is_kalemi, birim, b_fiyat, miktar, toplam, f_durum, personel_adi]], columns=df_h.columns)
            pd.concat([df_h, yeni_h], ignore_index=True).to_csv(FILES["hakedis"], index=False)
            st.success("Hakediş başarıyla kaydedildi!")
            st.rerun()

    st.subheader("📋 Güncel Hakediş Tablosu")
    if user["Rol"] in ["Admin", "Yönetici"]:
        st.dataframe(df_h_filtered, use_container_width=True)
    else:
        st.dataframe(df_h_filtered[["Tarih", "Cari Adı", "Kategori", "İş Kalemi", "Birim", "Miktar", "Personel"]], use_container_width=True)

# ==========================================
# TAB 2: DEPO GİRİŞ-ÇIKIŞ TAKİBİ
# ==========================================
with tab2:
    st.header("📦 Şantiye Depo Giriş / Çıkış ve İade Takibi")
    df_d = pd.read_csv(FILES["depo"])
    df_c = pd.read_csv(FILES["cariler"])
    
    st.subheader("📥 Yeni Depo Hareketi Ekle")
    with st.form("depo_form", clear_on_submit=True):
        d1, d2, d3 = st.columns(3)
        d_tarih = d1.date_input("Tarih ")
        d_cari = d2.selectbox("Malzemenin Gittiği Şantiye/Cari", options=df_c["Cari Adı"].unique() if not df_c.empty else ["Cari Yok"])
        d_malzeme = d3.text_input("Malzeme Adı", placeholder="Örn: Yangın Kablosu")
        
        d4, d5, d6 = st.columns(3)
        d_birim = d4.selectbox("Birim  ", ["Metre", "Adet", "Koli", "Kg"])
        d_cikis = d5.number_input("Sabah Depodan Çıkan Miktar", min_value=0.0)
        d_iade = d6.number_input("Akşam Depoya İade Edilen Miktar", min_value=0.0)
        
        if st.form_submit_button("📦 Depo Hareketini Kaydet"):
            net_harcanan = d_cikis - d_iade
            p_adi = f"{user['İsim']} {user['Soyisim']}"
            yeni_d = pd.DataFrame([[d_tarih.strftime('%Y-%m-%d'), d_cari, d_malzeme, d_birim, d_cikis, d_iade, net_harcanan, p_adi]], columns=df_d.columns)
            pd.concat([df_d, yeni_d], ignore_index=True).to_csv(FILES["depo"], index=False)
            st.success("Depo hareketi başarıyla işlendi!")
            st.rerun()
            
    st.subheader("📅 Günlük Bazda Depo Raporu")
    rapor_tarih = st.date_input("Filtrelenecek Günlük Rapor Tarihi", value=datetime.now())
    df_d_filtered = df_d[df_d["Tarih"] == rapor_tarih.strftime('%Y-%m-%d')]
    st.dataframe(df_d_filtered, use_container_width=True)

# ==========================================
# TAB 3: CARİ & İŞ TANIMLAMA
# ==========================================
with tab3:
    st.header("💼 Cari Hesap ve Sözleşme Tanımlama")
    df_c = pd.read_csv(FILES["cariler"])
    
    if user["Rol"] in ["Admin", "Yönetici"]:
        with st.form("cari_form", clear_on_submit=True):
            new_cari = st.text_input("Yeni Cari / Proje Adı")
            new_bedel = st.number_input("Toplam Sözleşme Bedeli (TL)", min_value=0.0)
            if st.form_submit_button("💼 Yeni Cariyi Kaydet"):
                if new_cari:
                    yeni_c = pd.DataFrame([[new_cari, new_bedel]], columns=df_c.columns)
                    pd.concat([df_c, yeni_c], ignore_index=True).to_csv(FILES["cariler"], index=False)
                    st.success("Yeni Cari Başarıyla Açıldı!")
                    st.rerun()
    else:
        st.warning("Bu alana sadece Admin ve Yöneticiler erişebilir.")
        
    st.subheader("📋 Kayıtlı Cari Listesi")
    st.dataframe(df_c, use_container_width=True)

# ==========================================
# TAB 4: PERSONEL YÖNETİMİ
# ==========================================
with tab4:
    st.header("👥 Personel Listesi ve Yetkilendirme")
    df_u = pd.read_csv(FILES["users"])
    
    if user["Rol"] == "Admin":
        st.subheader("➕ Yeni Personel Tanımla")
        with st.form("user_form", clear_on_submit=True):
            u1, u2 = st.columns(2)
            p_mail = u1.text_input("Personel E-Posta (Giriş Adı)")
            p_sifre = u2.text_input("Personel Şifresi")
            
            u3, u4, u5 = st.columns(3)
            p_isim = u3.text_input("Adı")
            p_soyisim = u4.text_input("Soyadı")
            p_rol = u5.selectbox("Yetki Seviyesi", ["Admin", "Yönetici", "Personel"])
            
            if st.form_submit_button("👥 Personeli Kaydet"):
                if p_mail and p_sifre:
                    yeni_u = pd.DataFrame([[p_mail, p_isim, p_soyisim, p_sifre, p_rol]], columns=df_u.columns)
                    pd.concat([df_u, yeni_u], ignore_index=True).to_csv(FILES["users"], index=False)
                    st.success("Personel sisteme başarıyla eklendi!")
                    st.rerun()
    else:
        st.warning("Personel ekleme/düzenleme yetkisi sadece sistem sahibine (Admin) aittir.")
        
    st.subheader("📋 Şirket İçi Aktif Kullanıcı Listesi")
    st.dataframe(df_u[["İsim", "Soyisim", "Email", "Rol"]], use_container_width=True)

