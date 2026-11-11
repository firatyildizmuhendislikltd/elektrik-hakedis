import streamlit as st
import pandas as pd
from datetime import datetime
from backup import (
    verileri_google_sheets_yukle,
    verileri_google_sheets_kaydet,
    kullanicilari_google_sheets_yukle,
    kullanici_google_sheets_ekle
)

st.set_page_config(page_title="Fırat Yıldız ERP", page_icon="🏗️", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #f4f6f9 !important; }
    h1, h2, h3, .login-title { color: #d32f2f !important; font-family: 'Segoe UI', Arial, sans-serif; font-weight: 700 !important; }
    h4, h5, h6 { color: #0f172a !important; font-weight: 600 !important; }
    p, span, label, .stMarkdown { color: #1e293b !important; }
    div[data-testid="stForm"], div[data-testid="metric-container"], .stAlert {
        border: 1px solid #cbd5e1 !important; border-top: 5px solid #1e40af !important; 
        border-radius: 10px !important; padding: 25px !important; background-color: #ffffff !important;
        box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1) !important;
    }
    div[data-testid="stDataFrame"] { background-color: #ffffff !important; border: 1px solid #cbd5e1 !important; border-radius: 8px !important; }
    button[kind="primaryFormSubmit"], .stButton > button {
        background-color: #1e40af !important; color: white !important; border-radius: 6px !important;
        width: 100% !important; font-weight: bold !important; border: none !important; padding: 10px !important;
    }
    button[kind="primaryFormSubmit"]:hover, .stButton > button:hover { background-color: #d32f2f !important; color: white !important; }
    section[data-testid="stSidebar"] { background-color: #0f172a !important; border-right: 1px solid #334155 !important; }
    section[data-testid="stSidebar"] stMarkdown, section[data-testid="stSidebar"] p, section[data-testid="stSidebar"] label { color: #f1f5f9 !important; }
    </style>
""", unsafe_allow_html=True)

CURRENCY_SYMBOLS = {"TL": "₺", "USD": "$", "EUR": "€", "STG": "£"}

df = verileri_google_sheets_yukle()
if not df.empty:
    for col in ["Tutar", "KDV Oranı (%)", "KDV Tutarı", "KDV Dahil Toplam"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0.0)

if "giris_yapildi" not in st.session_state:
    st.session_state.giris_yapildi = False
    st.session_state.kullanici_adi = ""
    st.session_state.kullanici_rolu = ""

if not st.session_state.giris_yapildi:
    st.markdown("<h1 class='login-title' style='text-align: center;'>FIRAT YILDIZ MÜHENDİSLİK</h1>", unsafe_allow_html=True)
    st.markdown("<p class='login-subtitle' style='text-align: center; color: #475569;'>Kurumsal ERP & Finansal Kontrol Paneli</p>", unsafe_allow_html=True)
    col_left, col_login, col_right = st.columns(3)
    with col_login:
        with st.form("giris_formu"):
            k_adi = st.text_input("Kurumsal E-Posta Adresi", placeholder="admin@firma.com")
            sifre = st.text_input("Erişim Şifresi", type="password")
            if st.form_submit_button("Sisteme Güvenli Giriş Yap"):
                KULLANICILAR = kullanicilari_google_sheets_yukle()
                if k_adi in KULLANICILAR and str(KULLANICILAR[k_adi]["sifre"]) == str(sifre):
                    st.session_state.giris_yapildi = True
                    st.session_state.kullanici_adi = k_adi
                    st.session_state.kullanici_rolu = KULLANICILAR[k_adi]["rol"]
                    st.success("Giriş Başarılı!")
                    st.rerun()
                else:
                    st.error("Hatalı e-posta veya şifre!")
else:
    with st.sidebar:
        st.markdown("<h2 style='color: #ef4444; margin-bottom: 0;'>Fırat Yıldız</h2>", unsafe_allow_html=True)
        st.markdown("<p style='color: #94a3b8; margin-top: 0;'>Mühendislik & ERP Kontrol</p>", unsafe_allow_html=True)
        st.write(f"👤 **Kullanıcı:** {st.session_state.kullanici_adi}")
        st.write(f"🎖️ **Yetki:** {st.session_state.kullanici_rolu}")
        st.divider()
        menü = ["📊 Genel Durum (Dashboard)", "📈 Kurumsal Raporlama"]
        if st.session_state.kullanici_rolu == "Yönetici":
            menü.extend(["➕ Yeni Kayıt Ekle", "📝 Kayıt Düzenleme & Silme", "👥 Kullanıcı Tanımlama", "⚙️ Sistem & Yedekleme"])
        sayfa = st.radio("Navigasyon Menüsü", menü, index=0)
        st.divider()
        if st.button("🚪 Güvenli Çıkış Yap"):
            st.session_state.giris_yapildi = False
            st.rerun()

    if sayfa == "📊 Genel Durum (Dashboard)":
        st.markdown("<h3>📊 Finansal Durum Özetleri (KDV Kırılımlı)</h3>", unsafe_allow_html=True)
        if not df.empty:
            for pb in df["Para Birimi"].unique():
                st.markdown(f"<h4 style='color: #1e40af !important;'>🌐 {pb} Bazında Kurumsal Durum</h4>", unsafe_allow_html=True)
                df_pb = df[df["Para Birimi"] == pb]
                sym = CURRENCY_SYMBOLS.get(pb, "")
                
                t_df = df_pb[df_pb["Tür"] == "Teklif"]
                h_df = df_pb[df_pb["Tür"] == "Hakediş"]
                
                st.write("**📝 TEKLİFLER GRUBU**")
                mt1, mt2, mt3 = st.columns(3)
                mt1.metric("Toplam Teklif (KDV Hariç)", f"{t_df['Tutar'].sum():,.2f} {sym}")
                mt2.metric("Teklif Toplam KDV'si", f"{t_df['KDV Tutarı'].sum():,.2f} {sym}")
                mt3.metric("Teklif Genel Toplam (KDV Dahil)", f"{t_df['KDV Dahil Toplam'].sum():,.2f} {sym}")
                
                st.write("**🏗️ HAKEDİŞLER GRUBU**")
                mh1, mh2, mh3 = st.columns(3)
                mh1.metric("Toplam Hakediş (KDV Hariç)", f"{h_df['Tutar'].sum():,.2f} {sym}")
                mh2.metric("Hakediş Toplam KDV'si", f"{h_df['KDV Tutarı'].sum():,.2f} {sym}")
                mh3.metric("Hakediş Genel Toplam (KDV Dahil)", f"{h_df['KDV Dahil Toplam'].sum():,.2f} {sym}")
                st.divider()
        else:
            st.info("Sistemde henüz kayıtlı veri bulunmuyor.")
        st.markdown("<h3>📋 Güncel İşlem Kayıtları Tablosu</h3>", unsafe_allow_html=True)
        st.dataframe(df.sort_index(ascending=False), use_container_width=True)
    elif sayfa == "📈 Kurumsal Raporlama":
        st.markdown("<h3>📈 Kurumsal Mali Analiz ve Müşteri / Döviz Raporu</h3>", unsafe_allow_html=True)
        if df.empty:
            st.info("Raporlama yapabilmek için lütfen önce veri ekleyin.")
        else:
            col_chart, col_filter = st.columns(2)
            with col_filter:
                st.markdown("#### 🎯 Rapor Filtreleme Paneli")
                f_pb = st.selectbox("Rapor Döviz Cinsi", ["Tüm Para Birimleri", "TL", "USD", "EUR", "STG"])
                f_tur = st.multiselect("Filtreleme Türü", ["Teklif", "Hakediş"], default=["Teklif", "Hakediş"])
                veri_tabanindaki_musteriler = sorted(list(df["Müşteri/Kurum"].dropna().unique()))
                secilen_musteri = st.selectbox("Müşteri / Kurum Seçin", ["Tüm Müşteriler"] + veri_tabanindaki_musteriler)
            
            df_rep = df[df["Tür"].isin(f_tur)]
            if f_pb != "Tüm Para Birimleri":
                df_rep = df_rep[df_rep["Para Birimi"] == f_pb]
            if secilen_musteri != "Tüm Müşteriler":
                df_rep = df_rep[df_rep["Müşteri/Kurum"] == secilen_musteri]
                
            if not df_rep.empty:
                st.markdown(f"##### 🏢 {secilen_musteri} ({f_pb}) - Finansal Kırılımlar")
                if f_pb == "Tüm Para Birimleri":
                    for para in df_rep["Para Birimi"].unique():
                        df_para = df_rep[df_rep["Para Birimi"] == para]
                        sym = CURRENCY_SYMBOLS.get(para, "")
                        st.markdown(f"**🔹 {para} Cinsinden Toplamlar:**")
                        rm1, rm2, rm3 = st.columns(3)
                        rm1.metric("Matrah (KDV Hariç)", f"{df_para['Tutar'].sum():,.2f} {sym}")
                        rm2.metric("KDV Tutarı", f"{df_para['KDV Tutarı'].sum():,.2f} {sym}")
                        rm3.metric("Genel Toplam (KDV Dahil)", f"{df_para['KDV Dahil Toplam'].sum():,.2f} {sym}")
                    st.divider()
                else:
                    sym = CURRENCY_SYMBOLS.get(f_pb, "")
                    rm1, rm2, rm3 = st.columns(3)
                    rm1.metric("Toplam Matrah (KDV Hariç)", f"{df_rep['Tutar'].sum():,.2f} {sym}")
                    rm2.metric("Toplam KDV Tutarı", f"{df_rep['KDV Tutarı'].sum():,.2f} {sym}")
                    rm3.metric("KDV Dahil Genel Toplam", f"{df_rep['KDV Dahil Toplam'].sum():,.2f} {sym}")
                    st.divider()
                
                with col_chart:
                    st.markdown("##### 📊 Grafikle Finansal Dağılım")
                    if f_pb == "Tüm Para Birimleri":
                        chart_df = df_rep.groupby(["Para Birimi", "Tür"])["KDV Dahil Toplam"].sum().unstack().fillna(0)
                        st.bar_chart(chart_df)
                    else:
                        chart_df = df_rep.groupby("Tür")[["Tutar", "KDV Tutarı"]].sum().rename(columns={"Tutar": "Matrah bütçesi", "KDV Tutarı": "KDV Vergisi"})
                        st.bar_chart(chart_df)
            else:
                st.info("Seçilen kriterlere uygun kayıt bulunamadı.")

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
                kdv_orani = st.selectbox("KDV Oranı (%)", list((0, 1, 10, 20)), index=3)
                para_birimi = st.selectbox("Para Birimi", ["TL", "USD", "EUR", "STG"])
                durum = st.selectbox("Mevcut İş Durumu", ["Beklemede", "Onaylandı", "Reddedildi", "Ödendi / Tahsil Edildi"])
            st.divider()
            col_f3, col_f4 = st.columns(2)
            with col_f3:
                fatura_durumu = st.selectbox("Fatura Durumu", ["Faturalanmadı", "Faturalandı"])
            with col_f4:
                yonetici_onayi = st.selectbox("Yönetici İlk Onay Durumu", ["Beklemede", "Onaylandı", "Reddedildi"])
            
            if st.form_submit_button("Sözleşmeyi Onayla, Otomatik KDV Hesapla ve Buluta Kaydet"):
                if not proje_adi or not musteri:
                    st.error("Lütfen alanları doldurun!")
                else:
                    kdv_t = tutar * (kdv_orani / 100)
                    kdv_d = tutar + kdv_t
                    yeni_satir = {
                        "Tarih": datetime.now().strftime("%Y-%m-%d %H:%M"), "Tür": tur, "Proje Adı": proje_adi, 
                        "Müşteri/Kurum": musteri, "Tutar": tutar, "KDV Oranı (%)": kdv_orani, "KDV Tutarı": kdv_t, 
                        "KDV Dahil Toplam": kdv_d, "Para Birimi": para_birimi, "Durum": durum, "Fatura Durumu": fatura_durumu, "Yönetici Onayı": yonetici_onayi
                    }
                    df = pd.concat([df, pd.DataFrame([yeni_satir])], ignore_index=True)
                    verileri_google_sheets_kaydet(df)
                    st.success("✅ Kalıcı bulut veritabanına kaydedildi!")
                    st.rerun()

    # 4. SAYFA: TÜR DÜZENLEME VE KAYIT SİLME MODÜLÜ (YENİLENDİ)
    elif sayfa == "📝 Kayıt Düzenleme & Silme" and st.session_state.kullanici_rolu == "Yönetici":
        st.markdown("<h3>📝 Sözleşme Düzenleme, Tür Değiştirme ve Silme Paneli</h3>", unsafe_allow_html=True)
        if df.empty:
            st.info("Düzenlenecek veya silinecek kayıt bulunmamaktadır.")
        else:
            proje_secenekleri = [f"{idx} - [{row['Tür']}] {row['Proje Adı']} (Matrah: {row['Tutar']} {row['Para Birimi']})" for idx, row in df.iterrows()]
            secilen_proje_str = st.selectbox("İşlem Yapılacak Sözleşmeyi Seçin", proje_secenekleri)
            secilen_index = int(secilen_proje_str.split(" - "))
            satir_verisi = df.loc[secilen_index]
            
            with st.form("duzenleme_formu"):
                col_d1, col_d2 = st.columns(2)
                with col_d1:
                    # 🔄 İŞLEM TÜRÜNÜ (TEKLİF / HAKEDİŞ) DEĞİŞTİRME ALANI EKLENDİ
                    d_tur = st.selectbox("İşlem Türü (Değiştirilebilir)", ["Teklif", "Hakediş"], index=["Teklif", "Hakediş"].index(satir_verisi["Tür"]))
                    d_proje = st.text_input("Proje / İş Başlığı", value=satir_verisi["Proje Adı"])
                    d_musteri = st.text_input("Müşteri Firma / Kurum", value=satir_verisi["Müşteri/Kurum"])
                    d_tutar = st.number_input("Sözleşme Matrah Tutarı", min_value=0.0, format="%.2f", value=float(satir_verisi["Tutar"]))
                with col_d2:
                    kdv_opsiyonlari = list((0, 1, 10, 20))
                    mevcut_kdv = int(satir_verisi["KDV Oranı (%)"])
                    d_kdv_oran = st.selectbox("KDV Oranı (%)", kdv_opsiyonlari, index=kdv_opsiyonlari.index(mevcut_kdv) if mevcut_kdv in kdv_opsiyonlari else 3)
                    d_pb = st.selectbox("Para Birimi", ["TL", "USD", "EUR", "STG"], index=["TL", "USD", "EUR", "STG"].index(satir_verisi["Para Birimi"]))
                    d_durum = st.selectbox("İş Durumu", ["Beklemede", "Onaylandı", "Reddedildi", "Ödendi / Tahsil Edildi"], index=["Beklemede", "Onaylandı", "Reddedildi", "Ödendi / Tahsil Edildi"].index(satir_verisi["Durum"]))
                st.divider()
                col_d3, col_d4 = st.columns(2)
                with col_d3:
                    d_fatura = st.selectbox("🧾 Fatura Durumu Güncelle", ["Faturalanmadı", "Faturalandı"], index=["Faturalanmadı", "Faturalandı"].index(satir_verisi["Fatura Durumu"]))
                with col_d4:
                    d_onay = st.selectbox("👑 Yönetici Onay Durumu Güncelle", ["Beklemede", "Onaylandı", "Reddedildi"], index=["Beklemede", "Onaylandı", "Reddedildi"].index(satir_verisi["Yönetici Onayı"]))
                
                if st.form_submit_button("✅ Değişiklikleri Kaydet ve Buluta İşle"):
                    kdv_t = d_tutar * (d_kdv_oran / 100)
                    df.at[secilen_index, "Tür"] = d_tur
                    df.at[secilen_index, "Proje Adı"], df.at[secilen_index, "Müşteri/Kurum"] = d_proje, d_musteri
                    df.at[secilen_index, "Tutar"], df.at[secilen_index, "KDV Oranı (%)"] = d_tutar, d_kdv_oran
                    df.at[secilen_index, "KDV Tutarı"], df.at[secilen_index, "KDV Dahil Toplam"] = kdv_t, d_tutar + kdv_t
                    df.at[secilen_index, "Para Birimi"], df.at[secilen_index, "Durum"] = d_pb, d_durum
                    df.at[secilen_index, "Fatura Durumu"], df.at[secilen_index, "Yönetici Onayı"] = d_fatura, d_onay
                    verileri_google_sheets_kaydet(df)
                    st.success("✅ Sözleşme başarıyla güncellendi!")
                    st.rerun()

            # 🗑️ KAYIT SİLME BÖLÜMÜ
            st.divider()
            st.markdown("#### 🗑️ Tehlikeli İşlem: Kayıt Silme")
            st.warning(f"Dikkat: **[{satir_verisi['Tür']}] {satir_verisi['Proje Adı']}** kaydını kalıcı olarak silmek üzeresiniz. Bu işlem geri alınamaz.")
            if st.button("🚨 Seçili Kaydı Sistemden Kalıcı Olarak Sil"):
                df = df.drop(index=secilen_index).reset_index(drop=True)
                verileri_google_sheets_kaydet(df)
                st.success("🗑️ Kayıt sistemden ve bulut veritabanından kalıcı olarak silindi!")
                st.rerun()

    elif sayfa == "👥 Kullanıcı Tanımlama" and st.session_state.kullanici_rolu == "Yönetici":
        st.markdown("<h3>👥 Dinamik Kullanıcı Hesapları ve Rol Atama</h3>", unsafe_allow_html=True)
        c_u1, c_u2 = st.columns(2)
        with c_u1:
            u_eposta = st.text_input("Personel E-Posta")
            u_sifre = st.text_input("Erişim Şifresi", type="password")
            u_rol = st.selectbox("Yetki Seviyesi (Rol)", ["Yönetici", "Personel"])
            if st.button("Hesabı Tanımla"):
                if u_eposta and u_sifre:
                    if kullanici_google_sheets_ekle(u_eposta, u_sifre, u_rol):
                        st.success("✅ Hesap bulut veritabanına eklendi!")
                        st.rerun()
                    else:
                        st.error("Bu e-posta zaten kayıtlı!")
                else:
                    st.error("Tüm alanları doldurun.")
        with c_u2:
            k_sozluk = kullanicilari_google_sheets_yukle()
            df_goster = pd.DataFrame([{"E-Posta": k, "Rol": v["rol"]} for k, v in k_sozluk.items()])
            st.dataframe(df_goster, use_container_width=True)

    elif sayfa == "⚙️ Sistem & Yedekleme" and st.session_state.kullanici_rolu == "Yönetici":
        st.markdown("<h3>⚙️ Altyapı Yönetimi</h3>", unsafe_allow_html=True)
        st.metric("Kalıcı Bulut Satır Sayısı", len(df))
        st.success("✅ Sistem doğrudan Supabase bulut veritabanı ile canlı senkronize çalışmaktadır.")
