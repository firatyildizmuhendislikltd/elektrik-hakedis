import streamlit as st
import pandas as pd
import os
from datetime import datetime
from backup import cift_yedekleme_yap

# 🎨 Kurumsal Renk ve Sayfa Yapılandırması (Açık Gri, Kurumsal Mavi ve Kırmızı)
st.set_page_config(page_title="Fırat Yıldız ERP", page_icon="🏗️", layout="wide")

# 🖥️ Gözü Yormayan, Aydınlık ve Kurumsal CSS Düzenlemeleri
st.markdown("""
    <style>
    .stApp { background-color: #f4f6f9 !important; }
    h1, h2, h3, .login-title {
        color: #d32f2f !important; 
        font-family: 'Segoe UI', Arial, sans-serif;
        font-weight: 700 !important;
    }
    h4, h5, h6 { color: #0f172a !important; font-weight: 600 !important; }
    p, span, label, .stMarkdown { color: #1e293b !important; }
    
    div[data-testid="stForm"], div[data-testid="metric-container"], .stAlert {
        border: 1px solid #cbd5e1 !important; 
        border-top: 5px solid #1e40af !important; 
        border-radius: 10px !important;
        padding: 25px !important;
        background-color: #ffffff !important;
        box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1) !important;
    }
    div[data-testid="stDataFrame"] {
        background-color: #ffffff !important;
        border: 1px solid #cbd5e1 !important;
        border-radius: 8px !important;
    }
    button[kind="primaryFormSubmit"], .stButton > button {
        background-color: #1e40af !important;
        color: white !important;
        border-radius: 6px !important;
        width: 100% !important;
        font-weight: bold !important;
        border: none !important;
        padding: 10px !important;
    }
    button[kind="primaryFormSubmit"]:hover, .stButton > button:hover {
        background-color: #d32f2f !important;
        color: white !important;
    }
    section[data-testid="stSidebar"] {
        background-color: #0f172a !important;
        border-right: 1px solid #334155 !important;
    }
    section[data-testid="stSidebar"] stMarkdown, section[data-testid="stSidebar"] p, section[data-testid="stSidebar"] label {
        color: #f1f5f9 !important;
    }
    </style>
""", unsafe_allow_html=True)

DB_FILE = "teklif_hakedis_db.csv"
USERS_FILE = "kullanicilar_db.csv"
CURRENCY_SYMBOLS = {"TL": "₺", "USD": "$", "EUR": "€", "STG": "£"}

def kullanicilari_yukle():
    if os.path.exists(USERS_FILE):
        return pd.read_csv(USERS_FILE).set_index("eposta").to_dict(orient="index")
    varsayilan = {
        "admin@firma.com": {"sifre": "1234", "rol": "Yönetici"},
        "personel@firma.com": {"sifre": "5678", "rol": "Personel"}
    }
    df_users = pd.DataFrame.from_dict(varsayilan, orient="index").reset_index().rename(columns={"index": "eposta"})
    df_users.to_csv(USERS_FILE, index=False)
    return varsayilan

def kullanici_ekle(eposta, sifre, rol):
    if os.path.exists(USERS_FILE): df_users = pd.read_csv(USERS_FILE)
    else: df_users = pd.DataFrame(columns=["eposta", "sifre", "rol"])
    if eposta in df_users["eposta"].values: return False
    yeni_user = pd.DataFrame([{"eposta": eposta, "sifre": sifre, "rol": rol}])
    df_users = pd.concat([df_users, yeni_user], ignore_index=True)
    df_users.to_csv(USERS_FILE, index=False)
    return True

def veri_yukle():
    if os.path.exists(DB_FILE):
        df_loaded = pd.read_csv(DB_FILE)
        for col, default_val in [("Fatura Durumu", "Faturalanmadı"), ("Yönetici Onayı", "Beklemede"), 
                                 ("KDV Oranı (%)", 20), ("KDV Tutarı", 0), ("KDV Dahil Toplam", 0)]:
            if col not in df_loaded.columns:
                if col == "KDV Dahil Toplam" and "Tutar" in df_loaded.columns:
                    df_loaded[col] = df_loaded["Tutar"] * 1.20
                elif col == "KDV Tutarı" and "Tutar" in df_loaded.columns:
                    df_loaded[col] = df_loaded["Tutar"] * 0.20
                else: df_loaded[col] = default_val
        return df_loaded
    return pd.DataFrame(columns=["Tarih", "Tür", "Proje Adı", "Müşteri/Kurum", "Tutar", "KDV Oranı (%)", "KDV Tutarı", "KDV Dahil Toplam", "Para Birimi", "Durum", "Fatura Durumu", "Yönetici Onayı"])

def veri_kaydet(df):
    df.to_csv(DB_FILE, index=False, encoding="utf-8-sig")

KULLANICILAR = kullanicilari_yukle()
df = veri_yukle()

if "giris_yapildi" not in st.session_state:
    st.session_state.giris_yapildi = False
    st.session_state.kullanici_adi = ""
    st.session_state.kullanici_rolu = ""

if not st.session_state.giris_yapildi:
    st.markdown("<h1 class='login-title' style='text-align: center;'>FIRAT YILDIZ MÜHENDİSLİK</h1>", unsafe_allow_html=True)
    st.markdown("<p class='login-subtitle' style='text-align: center; color: #475569;'>Kurumsal ERP & Finansal Kontrol Paneli</p>", unsafe_allow_html=True)
    col_left, col_login, col_right = st.columns()
    with col_login:
        with st.form("giris_formu"):
            k_adi = st.text_input("Kurumsal E-Posta Adresi", placeholder="admin@firma.com")
            sifre = st.text_input("Erişim Şifresi", type="password")
            if st.form_submit_button("Sisteme Güvenli Giriş Yap"):
                KULLANICILAR = kullanicilari_yukle()
                if k_adi in KULLANICILAR and str(KULLANICILAR[k_adi]["sifre"]) == str(sifre):
                    st.session_state.giris_yapildi = True
                    st.session_state.kullanici_adi = k_adi
                    st.session_state.kullanici_rolu = KULLANICILAR[k_adi]["rol"]
                    st.success("Giriş Başarılı!")
                    st.rerun()
                else: st.error("Hatalı e-posta veya şifre!")
else:
    with st.sidebar:
        st.markdown("<h2 style='color: #ef4444; margin-bottom: 0;'>Fırat Yıldız</h2>", unsafe_allow_html=True)
        st.markdown("<p style='color: #94a3b8; margin-top: 0;'>Mühendislik & ERP Kontrol</p>", unsafe_allow_html=True)
        st.write(f"👤 **Kullanıcı:** {st.session_state.kullanici_adi}")
        st.write(f"🎖️ **Yetki:** {st.session_state.kullanici_rolu}")
        st.divider()
        menü = ["📊 Genel Durum (Dashboard)", "📈 Kurumsal Raporlama"]
        if st.session_state.kullanici_rolu == "Yönetici":
            menü.extend(["➕ Yeni Kayıt Ekle", "📝 Kayıt Düzenleme & Onay", "👥 Kullanıcı Tanımlama", "⚙️ Sistem & Yedekleme"])
        sayfa = st.radio("Navigasyon Menüsü", menü, index=0)
        st.divider()
        if st.button("🚪 Güvenli Çıkış Yap"):
            st.session_state.giris_yapildi = False
            st.rerun()

    # 1. SAYFA: DASHBOARD (ÜST METRİKLER TAMAMEN YENİLENDİ)
    if sayfa == "📊 Genel Durum (Dashboard)":
        st.markdown("<h3>📊 Finansal Durum Özetleri (KDV Kırılımlı)</h3>", unsafe_allow_html=True)
        if not df.empty:
            for pb in df["Para Birimi"].unique():
                st.markdown(f"<h4 style='color: #1e40af !important;'>🌐 {pb} Bazında Kurumsal Durum</h4>", unsafe_allow_html=True)
                df_pb = df[df["Para Birimi"] == pb]
                sym = CURRENCY_SYMBOLS.get(pb, "")
                
                # Teklif Grubu Hesaplamaları
                t_df = df_pb[df_pb["Tür"] == "Teklif"]
                t_matrah = t_df["Tutar"].sum()
                t_kdv = t_df["KDV Tutarı"].sum()
                t_toplam = t_df["KDV Dahil Toplam"].sum()
                
                # Hakediş Grubu Hesaplamaları
                h_df = df_pb[df_pb["Tür"] == "Hakediş"]
                h_matrah = h_df["Tutar"].sum()
                h_kdv = h_df["KDV Tutarı"].sum()
                h_toplam = h_df["KDV Dahil Toplam"].sum()
                
                # 📊 Teklif Satırı (Matrah, KDV, Toplam)
                st.write("**📝 TEKLİFLER GRUBU**")
                mt1, mt2, mt3 = st.columns(3)
                mt1.metric("Toplam Teklif (KDV Hariç)", f"{t_matrah:,.2f} {sym}")
                mt2.metric("Teklif Toplam KDV'si", f"{t_kdv:,.2f} {sym}")
                mt3.metric("Teklif Genel Toplam (KDV Dahil)", f"{t_toplam:,.2f} {sym}")
                
                # 📊 Hakediş Satırı (Matrah, KDV, Toplam)
                st.write("**🏗️ HAKEDİŞLER GRUBU**")
                mh1, mh2, mh3 = st.columns(3)
                mh1.metric("Toplam Hakediş (KDV Hariç)", f"{h_matrah:,.2f} {sym}")
                mh2.metric("Hakediş Toplam KDV'si", f"{h_kdv:,.2f} {sym}")
                mh3.metric("Hakediş Genel Toplam (KDV Dahil)", f"{h_toplam:,.2f} {sym}")
                st.divider()
        else: st.info("Sistemde henüz kayıtlı veri bulunmuyor.")
        st.markdown("<h3>📋 Güncel İşlem Kayıtları Tablosu</h3>", unsafe_allow_html=True)
        st.dataframe(df.sort_index(ascending=False), use_container_width=True)
    # 2. SAYFA: KURUMSAL RAPORLAMA
    elif sayfa == "📈 Kurumsal Raporlama":
        st.markdown("<h3>📈 Kurumsal Mali Analiz ve Ayrıştırılmış KDV Raporu</h3>", unsafe_allow_html=True)
        if df.empty: st.info("Raporlama yapabilmek için lütfen önce veri ekleyin.")
        else:
            col_chart, col_filter = st.columns(2)
            with col_filter:
                st.markdown("#### 🎯 Para Birimi ve Filtre")
                f_pb = st.selectbox("Rapor Döviz Cinsi", ["TL", "USD", "EUR", "STG"])
                f_tur = st.multiselect("Filtreleme Türü", ["Teklif", "Hakediş"], default=["Teklif", "Hakediş"])
            
            df_rep = df[(df["Para Birimi"] == f_pb) & (df["Tür"].isin(f_tur))]
            sym = CURRENCY_SYMBOLS.get(f_pb, "")
            
            if not df_rep.empty:
                rep_matrah = df_rep["Tutar"].sum()
                rep_kdv = df_rep["KDV Tutarı"].sum()
                rep_toplam = df_rep["KDV Dahil Toplam"].sum()
                
                rm1, rm2, rm3 = st.columns(3)
                rm1.metric("Toplam Matrah (KDV Hariç)", f"{rep_matrah:,.2f} {sym}")
                rm2.metric("Toplam KDV Yükü", f"{rep_kdv:,.2f} {sym}")
                rm3.metric("KDV Dahil Genel Toplam", f"{rep_toplam:,.2f} {sym}")
                st.divider()
                
                with col_chart:
                    st.markdown(f"##### {f_pb} Cinsinden Matrah ve KDV Tutarı Karşılaştırması")
                    chart_df = df_rep.groupby("Tür")[["Tutar", "KDV Tutarı"]].sum().rename(columns={"Tutar": "Matrah bütçesi", "KDV Tutarı": "KDV Vergisi"})
                    st.bar_chart(chart_df)
            else: st.info("Seçilen döviz cinsine ait veri bulunamadı.")

    # 3. SAYFA: YENİ KAYIT EKLE
    elif sayfa == "➕ Yeni Kayıt Ekle" and st.session_state.kullanici_rolu == "Yönetici":
        st.markdown("<h3>➕ Yeni Teklif / Hakediş Kontrat Girişi (KDV Hesaplamalı)</h3>", unsafe_allow_html=True)
        with st.form("kurumsal_islem_formu", clear_on_submit=True):
            col_f1, col_f2 = st.columns(2)
            with col_f1:
                tur = st.selectbox("İşlem Türü", ["Teklif", "Hakediş"])
                proje_adi = st.text_input("Proje / İş Başlığı")
                musteri = st.text_input("Müşteri Firma / Kurum")
            with col_f2:
                tutar = st.number_input("Sözleşme Matrah Tutarı (KDV Hariç)", min_value=0.0, format="%.2f")
                kdv_orani = st.selectbox("KDV Oranı (%)", [0, 1, 10, 20], index=3)
                para_birimi = st.selectbox("Para Birimi", ["TL", "USD", "EUR", "STG"])
                durum = st.selectbox("Mevcut İş Durumu", ["Beklemede", "Onaylandı", "Reddedildi", "Ödendi / Tahsil Edildi"])
            st.divider()
            col_f3, col_f4 = st.columns(2)
            with col_f3: fatura_durumu = st.selectbox("Fatura Durumu", ["Faturalanmadı", "Faturalandı"])
            with col_f4: yonetici_onayi = st.selectbox("Yönetici İlk Onay Durumu", ["Beklemede", "Onaylandı", "Reddedildi"])
            
            if st.form_submit_button("Sözleşmeyi Onayla, Otomatik KDV Hesapla ve Yedekle"):
                if not proje_adi or not musteri: st.error("Lütfen alanları doldurun!")
                else:
                    kdv_t = tutar * (kdv_orani / 100)
                    kdv_d = tutar + kdv_t
                    yeni_satir = {
                        "Tarih": datetime.now().strftime("%Y-%m-%d %H:%M"), "Tür": tur, "Proje Adı": proje_adi, 
                        "Müşteri/Kurum": musteri, "Tutar": tutar, "KDV Oranı (%)": kdv_orani, "KDV Tutarı": kdv_t, 
                        "KDV Dahil Toplam": kdv_d, "Para Birimi": para_birimi, "Durum": durum, "Fatura Durumu": fatura_durumu, "Yönetici Onayı": yonetici_onayi
                    }
                    df = pd.concat([df, pd.DataFrame([yeni_satir])], ignore_index=False)
                    veri_kaydet(df); cift_yedekleme_yap()
                    st.success(f"✅ Başarıyla Kaydedildi!"); st.rerun()

    # 4. SAYFA: KAYIT DÜZENLEME & ONAY PANELİ
    elif sayfa == "📝 Kayıt Düzenleme & Onay" and st.session_state.kullanici_rolu == "Yönetici":
        st.markdown("<h3>📝 Sözleşme Düzenleme ve Yönetici Onay Paneli</h3>", unsafe_allow_html=True)
        if df.empty: st.info("Düzenlenecek kayıt bulunmamaktadır.")
        else:
            proje_secenekleri = [f"{idx} - [{row['Tür']}] {row['Proje Adı']} (Matrah: {row['Tutar']} {row['Para Birimi']})" for idx, row in df.iterrows()]
            secilen_proje_str = st.selectbox("Düzenlenecek Sözleşmeyi Seçin", proje_secenekleri)
            secilen_index = int(secilen_proje_str.split(" - "))
            satir_verisi = df.loc[secilen_index]
            
            with st.form("duzenleme_formu"):
                col_d1, col_d2 = st.columns(2)
                with col_d1:
                    d_proje = st.text_input("Proje / İş Başlığı", value=satir_verisi["Proje Adı"])
                    d_musteri = st.text_input("Müşteri Firma / Kurum", value=satir_verisi["Müşteri/Kurum"])
                    d_tutar = st.number_input("Sözleşme Matrah Tutarı", min_value=0.0, format="%.2f", value=float(satir_verisi["Tutar"]))
                with col_d2:
                    d_kdv_oran = st.selectbox("KDV Oranı (%)", [0, 1, 10, 20], index=[0, 1, 10, 20].index(int(satir_verisi["KDV Oranı (%)"])))
                    d_pb = st.selectbox("Para Birimi", ["TL", "USD", "EUR", "STG"], index=["TL", "USD", "EUR", "STG"].index(satir_verisi["Para Birimi"]))
                    d_durum = st.selectbox("İş Durumu", ["Beklemede", "Onaylandı", "Reddedildi", "Ödendi / Tahsil Edildi"], index=["Beklemede", "Onaylandı", "Reddedildi", "Ödendi / Tahsil Edildi"].index(satir_verisi["Durum"]))
                st.divider()
                col_d3, col_d4 = st.columns(2)
                with col_d3: d_fatura = st.selectbox("🧾 Fatura Durumu Güncelle", ["Faturalanmadı", "Faturalandı"], index=["Faturalanmadı", "Faturalandı"].index(satir_verisi["Fatura Durumu"]))
                with col_d4: d_onay = st.selectbox("👑 Yönetici Onay Durumu Güncelle", ["Beklemede", "Onaylandı", "Reddedildi"], index=["Beklemede", "Onaylandı", "Reddedildi"].index(satir_verisi["Yönetici Onayı"]))
                
                if st.form_submit_button("Değişiklikleri Kaydet ve Buluta Yedekle"):
                    kdv_t = d_tutar * (d_kdv_oran / 100)
                    df.at[secilen_index, "Proje Adı"], df.at[secilen_index, "Müşteri/Kurum"] = d_proje, d_musteri
                    df.at[secilen_index, "Tutar"], df.at[secilen_index, "KDV Oranı (%)"] = d_tutar, d_kdv_oran
                    df.at[secilen_index, "KDV Tutarı"], df.at[secilen_index, "KDV Dahil Toplam"] = kdv_t, d_tutar + kdv_t
                    df.at[secilen_index, "Para Birimi"], df.at[secilen_index, "Durum"] = d_pb, d_durum
                    df.at[secilen_index, "Fatura Durumu"], df.at[secilen_index, "Yönetici Onayı"] = d_fatura, d_onay
                    veri_kaydet(df); cift_yedekleme_yap()
                    st.success("✅ Güncellendi!"); st.rerun()

    # 5. SAYFA: KULLANICI TANIMLAMA
    elif sayfa == "👥 Kullanıcı Tanımlama" and st.session_state.kullanici_rolu == "Yönetici":
        st.markdown("<h3>👥 Dinamik Kullanıcı Hesapları ve Rol Atama</h3>", unsafe_allow_html=True)
        c_u1, c_u2 = st.columns(2)
        with c_u1:
            u_eposta = st.text_input("Personel E-Posta")
            u_sifre = st.text_input("Erişim Şifresi", type="password")
            u_rol = st.selectbox("Yetki Seviyesi (Rol)", ["Yönetici", "Personel"])
            if st.button("Hesabı Tanımla"):
                if u_eposta and u_sifre:
                    if kullanici_ekle(u_eposta, u_sifre, u_rol): st.success("✅ Hesap oluşturuldu!"); st.rerun()
                    else: st.error("Bu e-posta zaten kayıtlı!")
                else: st.error("Tüm alanları doldurun.")
        with c_u2: st.dataframe(pd.read_csv(USERS_FILE)[["eposta", "rol"]], use_container_width=True)

    # 6. SAYFA: SİSTEM AYARLARI
    elif sayfa == "⚙️ Sistem & Yedekleme" and st.session_state.kullanici_rolu == "Yönetici":
        st.markdown("<h3>⚙️ Altyapı Yönetimi</h3>", unsafe_allow_html=True)
        st.metric("Toplam Sistem Veri Satırı", len(df))
        if st.button("Şimdi Manuel Google Drive Yedeklemesi Tetikle"): st.info(cift_yedekleme_yap())
