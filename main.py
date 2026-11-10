import streamlit as st
import pandas as pd
import os
from datetime import datetime
from backup import cift_yedekleme_yap

# 🎨 Kurumsal Renk ve Sayfa Yapılandırması (Siyah, Mavi, Kırmızı Tema)
st.set_page_config(page_title="Fırat Yıldız ERP", page_icon="🏗️", layout="wide")

# 🖥️ Giriş Ekranı İçin Özel Kurumsal Tasarım (CSS)
st.markdown("""
    <style>
    /* Giriş başlığı stili */
    .login-title {
        text-align: center; 
        color: #ef4444; /* Kurumsal Kırmızı */
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        font-weight: 700;
        margin-bottom: 5px;
    }
    .login-subtitle {
        text-align: center;
        color: #6b7280; /* Siyah/Gri tonu */
        font-size: 16px;
        margin-bottom: 30px;
    }
    /* Streamlit form kutusunu kurumsal çerçeveye alma */
    div[data-testid="stForm"] {
        border: 2px solid #111827 !important; /* Kurumsal Siyah Çerçeve */
        border-top: 5px solid #2563eb !important; /* Üst Çizgi Mavi */
        border-radius: 10px !important;
        padding: 30px !important;
        background-color: #f9fafb !important;
    }
    /* Giriş butonu tasarımı */
    button[kind="primaryFormSubmit"] {
        background-color: #2563eb !important; /* Kurumsal Mavi */
        color: white !important;
        border-radius: 5px !important;
        width: 100% !important;
        border: none !important;
        font-weight: bold !important;
    }
    button[kind="primaryFormSubmit"]:hover {
        background-color: #ef4444 !important; /* Üzerine gelince Kırmızı */
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
    if os.path.exists(USERS_FILE):
        df_users = pd.read_csv(USERS_FILE)
    else:
        df_users = pd.DataFrame(columns=["eposta", "sifre", "rol"])
    if eposta in df_users["eposta"].values:
        return False
    yeni_user = pd.DataFrame([{"eposta": eposta, "sifre": sifre, "rol": rol}])
    df_users = pd.concat([df_users, yeni_user], ignore_index=True)
    df_users.to_csv(USERS_FILE, index=False)
    return True

def veri_yukle():
    if os.path.exists(DB_FILE):
        df_loaded = pd.read_csv(DB_FILE)
        for col, default_val in [("Fatura Durumu", "Faturalanmadı"), ("Yönetici Onayı", "Beklemede")]:
            if col not in df_loaded.columns:
                df_loaded[col] = default_val
        return df_loaded
    return pd.DataFrame(columns=["Tarih", "Tür", "Proje Adı", "Müşteri/Kurum", "Tutar", "Para Birimi", "Durum", "Fatura Durumu", "Yönetici Onayı"])

def veri_kaydet(df):
    df.to_csv(DB_FILE, index=False, encoding="utf-8-sig")

KULLANICILAR = kullanicilari_yukle()
df = veri_yukle()

if "giris_yapildi" not in st.session_state:
    st.session_state.giris_yapildi = False
    st.session_state.kullanici_adi = ""
    st.session_state.kullanici_rolu = ""

# ---------------- 🔑 GİRİŞ EKRANI ----------------
if not st.session_state.giris_yapildi:
    st.markdown("<h1 class='login-title'>FIRAT YILDIZ MÜHENDİSLİK</h1>", unsafe_allow_html=True)
    st.markdown("<p class='login-subtitle'>Kurumsal ERP & Finansal Kontrol Paneli</p>", unsafe_allow_html=True)
    
    _, col_login, _ = st.columns([1, 2, 1])
    with col_login:
        with st.form("giris_formu"):
            k_adi = st.text_input("Kurumsal E-Posta Adresi", placeholder="ornek@firma.com")
            sifre = st.text_input("Erişim Şifresi", type="password")
            giri_butonu = st.form_submit_button("Sisteme Güvenli Giriş Yap")
            
            if giri_butonu:
                KULLANICILAR = kullanicilari_yukle()
                if k_adi in KULLANICILAR and str(KULLANICILAR[k_adi]["sifre"]) == str(sifre):
                    st.session_state.giris_yapildi = True
                    st.session_state.kullanici_adi = k_adi
                    st.session_state.kullanici_rolu = KULLANICILAR[k_adi]["rol"]
                    st.success("Giriş Başarılı!")
                    st.rerun()
                else:
                    st.error("Hatalı e-posta veya şifre!")
else:
    # ---------------- 📱 SOL MENÜ (SIDEBAR) ----------------
    with st.sidebar:
        st.markdown("<h2 style='color: #ef4444; margin-bottom: 0;'>Fırat Yıldız</h2>", unsafe_allow_html=True)
        st.markdown("<p style='color: #6b7280; margin-top: 0;'>Mühendislik & ERP Kontrol</p>", unsafe_allow_html=True)
        st.write(f"👤 **Kullanıcı:** {st.session_state.kullanici_adi}")
        st.write(f"🎖️ **Yetki Rolü:** {st.session_state.kullanici_rolu}")
        st.divider()
        
        menü = ["📊 Genel Durum (Dashboard)", "📈 Kurumsal Raporlama"]
        if st.session_state.kullanici_rolu == "Yönetici":
            menü.extend(["➕ Yeni Kayıt Ekle", "📝 Kayıt Düzenleme & Onay", "👥 Kullanıcı Tanımlama", "⚙️ Sistem & Yedekleme"])
            
        sayfa = st.radio("Navigasyon Menüsü", menü, index=0)
        st.divider()
        
        if st.button("🚪 Güvenli Çıkış Yap"):
            st.session_state.giris_yapildi = False
            st.rerun()

    # ---------------- 1. SAYFA: DASHBOARD ----------------
    if sayfa == "📊 Genel Durum (Dashboard)":
        st.markdown("<h3 style='color: #111827;'>📋 Güncel Finansal Durum Özetleri</h3>", unsafe_allow_html=True)
        
        if not df.empty:
            pb_listesi = df["Para Birimi"].unique()
            for pb in pb_listesi:
                st.markdown(f"#### 🌐 {pb} Bazında Özetler")
                df_pb = df[df["Para Birimi"] == pb]
                
                t_toplam = df_pb[df_pb["Tür"] == "Teklif"]["Tutar"].sum()
                h_toplam = df_pb[df_pb["Tür"] == "Hakediş"]["Tutar"].sum()
                
                t_onay = df_pb[(df_pb["Tür"] == "Teklif") & (df_pb["Yönetici Onayı"] == "Onaylandı")]["Tutar"].sum()
                h_fatura = df_pb[(df_pb["Tür"] == "Hakediş") & (df_pb["Fatura Durumu"] == "Faturalandı")]["Tutar"].sum()
                
                m1, m2, m3, m4 = st.columns(4)
                sym = CURRENCY_SYMBOLS.get(pb, "")
                m1.metric("Toplam Teklif", f"{t_toplam:,.2f} {sym}")
                m2.metric("Yönetici Onaylı Teklif", f"{t_onay:,.2f} {sym}", f"{((t_onay/t_toplam*100) if t_toplam>0 else 0):.1f}% Onaylı")
                m3.metric("Toplam Hakediş", f"{h_toplam:,.2f} {sym}")
                m4.metric("Faturalanan Hakediş", f"{h_fatura:,.2f} {sym}", f"{h_toplam - h_fatura:,.2f} Kalan")
                st.divider()
        else:
            st.info("Sistemde henüz kayıtlı veri bulunmuyor.")

        st.markdown("#### 📑 Güncel İşlem Kayıtları Tablosu")
        st.dataframe(df.sort_index(ascending=False), use_container_width=True)

    # ---------------- 2. SAYFA: KURUMSAL RAPORLAMA ----------------
    elif sayfa == "📈 Kurumsal Raporlama":
        st.markdown("<h3 style='color: #111827;'>📈 Kurumsal Analiz ve Finansal Grafikler</h3>", unsafe_allow_html=True)
        
        if df.empty:
            st.info("Raporlama yapabilmek için lütfen önce veri ekleyin.")
        else:
            c_grafik, c_filtre = st.columns(2)
            with c_filtre:
                st.markdown("#### 🎯 Rapor Filtreleri")
                f_pb = st.selectbox("Raporlanacak Para Birimi", ["TL", "USD", "EUR", "STG"])
                f_tur = st.multiselect("İşlem Türü", ["Teklif", "Hakediş"], default=["Teklif", "Hakediş"])
            
            df_filtreli = df[(df["Para Birimi"] == f_pb) & (df["Tür"].isin(f_tur))]
            
            with c_grafik:
                if not df_filtreli.empty:
                    st.markdown(f"##### {f_pb} Cinsinden Tür ve Fatura Durumu Dağılımı")
                    grafik_data = df_filtreli.groupby(["Tür", "Fatura Durumu"])["Tutar"].sum().unstack().fillna(0)
                    st.bar_chart(grafik_data)
                else:
                    st.caption("Seçilen para birimi ve filtrelere uygun veri bulunamadı.")
    # ---------------- 3. SAYFA: YENİ KAYIT EKLE (Yönetici) ----------------
    elif sayfa == "➕ Yeni Kayıt Ekle" and st.session_state.kullanici_rolu == "Yönetici":
        st.markdown("<h3 style='color: #111827;'>➕ Yeni Teklif / Hakediş Kontrat Girişi</h3>", unsafe_allow_html=True)
        
        with st.form("kurumsal_islem_formu", clear_on_submit=True):
            col_f1, col_f2 = st.columns(2)
            with col_f1:
                tur = st.selectbox("İşlem Türü", ["Teklif", "Hakediş"])
                proje_adi = st.text_input("Proje / İş Başlığı")
                musteri = st.text_input("Müşteri Firma / Kurum")
            with col_f2:
                tutar = st.number_input("Sözleşme Tutarı", min_value=0.0, format="%.2f")
                para_birimi = st.selectbox("Para Birimi", ["TL", "USD", "EUR", "STG"])
                durum = st.selectbox("Mevcut İş Durumu", ["Beklemede", "Onaylandı", "Reddedildi", "Ödendi / Tahsil Edildi"])
            
            st.divider()
            col_f3, col_f4 = st.columns(2)
            with col_f3:
                fatura_durumu = st.selectbox("Fatura Durumu", ["Faturalanmadı", "Faturalandı"])
            with col_f4:
                yonetici_onayi = st.selectbox("Yönetici İlk Onay Durumu", ["Beklemede", "Onaylandı", "Reddedildi"])
                
            submit_btn = st.form_submit_button("Sözleşmeyi Onayla, Kaydet ve Yedekle")
            
            if submit_btn:
                if not proje_adi or not musteri:
                    st.error("Lütfen kurumsal alanları boş bırakmayınız!")
                else:
                    yeni_satir = {
                        "Tarih": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "Tür": tur, "Proje Adı": proje_adi, "Müşteri/Kurum": musteri,
                        "Tutar": tutar, "Para Birimi": para_birimi, "Durum": durum,
                        "Fatura Durumu": fatura_durumu, "Yönetici Onayı": yonetici_onayi
                    }
                    df = pd.concat([df, pd.DataFrame([yeni_satir])], ignore_index=False)
                    veri_kaydet(df)
                    
                    yedek_durumu = cift_yedekleme_yap()
                    st.success("✅ Veri kurumsal veri tabanına işlendi!")
                    st.toast(yedek_durumu)

    # ---------------- 4. SAYFA: KAYIT DÜZENLEME & ONAY PANELİ (Yönetici) ----------------
    elif sayfa == "📝 Kayıt Düzenleme & Onay" and st.session_state.kullanici_rolu == "Yönetici":
        st.markdown("<h3 style='color: #111827;'>📝 Sözleşme Düzenleme ve Yönetici Onay Paneli</h3>", unsafe_allow_html=True)
        
        if df.empty:
            st.info("Düzenlenecek kayıt bulunmamaktadır.")
        else:
            st.write("Düzenlemek istediğiniz kaydı aşağıdaki listeden seçin:")
            
            proje_secenekleri = [f"{idx} - [{row['Tür']}] {row['Proje Adı']} ({row['Tutar']} {row['Para Birimi']})" for idx, row in df.iterrows()]
            secilen_proje_str = st.selectbox("Düzenlenecek Sözleşmeyi Seçin", proje_secenekleri)
            
            secilen_index = int(secilen_proje_str.split(" - "))
            satir_verisi = df.loc[secilen_index]
            
            with st.form("duzenleme_formu"):
                st.markdown(f"##### 🛠️ Kayıt #{secilen_index} Düzenleme Alanı")
                col_d1, col_d2 = st.columns(2)
                with col_d1:
                    d_proje = st.text_input("Proje / İş Başlığı", value=satir_verisi["Proje Adı"])
                    d_musteri = st.text_input("Müşteri Firma / Kurum", value=satir_verisi["Müşteri/Kurum"])
                    d_tutar = st.number_input("Sözleşme Tutarı", min_value=0.0, format="%.2f", value=float(satir_verisi["Tutar"]))
                with col_d2:
                    d_pb = st.selectbox("Para Birimi", ["TL", "USD", "EUR", "STG"], index=["TL", "USD", "EUR", "STG"].index(satir_verisi["Para Birimi"]))
                    d_durum = st.selectbox("İş Durumu", ["Beklemede", "Onaylandı", "Reddedildi", "Ödendi / Tahsil Edildi"], index=["Beklemede", "Onaylandı", "Reddedildi", "Ödendi / Tahsil Edildi"].index(satir_verisi["Durum"]))
                
                st.divider()
                col_d3, col_d4 = st.columns(2)
                with col_d3:
                    d_fatura = st.selectbox("🧾 Fatura Durumu Güncelle", ["Faturalanmadı", "Faturalandı"], index=["Faturalanmadı", "Faturalandı"].index(satir_verisi["Fatura Durumu"]))
                with col_d4:
                    d_onay = st.selectbox("👑 Yönetici Onay Durumu Güncelle", ["Beklemede", "Onaylandı", "Reddedildi"], index=["Beklemede", "Onaylandı", "Reddedildi"].index(satir_verisi["Yönetici Onayı"]))
                
                guncelle_btn = st.form_submit_button("Değişiklikleri Kaydet ve Buluta Yedekle")
                
                if guncelle_btn:
                    df.at[secilen_index, "Proje Adı"] = d_proje
                    df.at[secilen_index, "Müşteri/Kurum"] = d_musteri
                    df.at[secilen_index, "Tutar"] = d_tutar
                    df.at[secilen_index, "Para Birimi"] = d_pb
                    df.at[secilen_index, "Durum"] = d_durum
                    df.at[secilen_index, "Fatura Durumu"] = d_fatura
                    df.at[secilen_index, "Yönetici Onayı"] = d_onay
                    
                    veri_kaydet(df)
                    yedek_durumu = cift_yedekleme_yap()
                    st.success("✅ Sözleşme başarıyla güncellendi!")
                    st.rerun()

    # ---------------- 5. SAYFA: KULLANICI TANIMLAMA ----------------
    elif sayfa == "👥 Kullanıcı Tanımlama" and st.session_state.kullanici_rolu == "Yönetici":
        st.markdown("<h3 style='color: #111827;'>👥 Dinamik Kullanıcı Hesapları ve Rol Atama</h3>", unsafe_allow_html=True)
        
        c_u1, c_u2 = st.columns(2)
        with c_u1:
            st.markdown("##### ➕ Yeni Kullanıcı Ekle")
            u_eposta = st.text_input("Personel E-Posta")
            u_sifre = st.text_input("Erişim Şifresi", type="password")
            u_rol = st.selectbox("Yetki Seviyesi (Rol)", ["Yönetici", "Personel"])
            u_ekle_btn = st.button("Hesabı Tanımla")
            
            if u_ekle_btn:
                if u_eposta and u_sifre:
                    if kullanici_ekle(u_eposta, u_sifre, u_rol):
                        st.success(f"✅ {u_eposta} başarıyla {u_rol} olarak eklendi!")
                        st.rerun()
                    else:
                        st.error("Bu e-posta adresi sistemde zaten kayıtlı!")
                else:
                    st.error("Lütfen tüm alanları doldurun.")
                    
        with c_u2:
            st.markdown("##### 📋 Mevcut Sistem Kullanıcıları")
            df_goster = pd.read_csv(USERS_FILE)[["eposta", "rol"]]
            st.dataframe(df_goster, use_container_width=True)

    # ---------------- 6. SAYFA: SİSTEM AYARLARI ----------------
    elif sayfa == "⚙️ Sistem & Yedekleme" and st.session_state.kullanici_rolu == "Yönetici":
        st.markdown("<h3 style='color: #111827;'>⚙️ Altyapı Yönetimi</h3>", unsafe_allow_html=True)
        st.metric("Toplam Sistem Veri Satırı", len(df))
        if st.button("Şimdi Manuel Google Drive Yedeklemesi Tetikle"):
            sonuc = cift_yedekleme_yap()
            st.info(sonuc)
