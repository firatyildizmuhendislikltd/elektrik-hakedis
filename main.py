import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- VERİ TABANLARI ---
FILES = {
"users": "erp_kullanicilar.csv",
"cariler": "erp_cariler.csv",
"hakedis": "erp_hakedis_verileri.csv",
"depo": "erp_depo_takip.csv"
}

if not os.path.exists(FILES["users"]):
    pd.DataFrame([["admin@firatyildiz.com", "Fırat", "Yıldız", "admin2026", "Admin"]], columns=["Email", "İsim", "Soyisim", "Şifre", "Rol"]).to_csv(FILES["users"], index=False)
if not os.path.exists(FILES["cariler"]):
    pd.DataFrame([["X Konut Projesi", 2500000.0, "TL"]], columns=["Cari Adı", "Sözleşme Bedeli", "Para Birimi"]).to_csv(FILES["cariler"], index=False)
if not os.path.exists(FILES["hakedis"]):
    pd.DataFrame(columns=["Tarih", "Cari Adı", "Kategori", "İş Kalemi", "Birim", "Birim Fiyat", "Miktar", "Toplam Tutar", "Para Birimi", "Fatura Durumu", "Personel"]).to_csv(FILES["hakedis"], index=False)
if not os.path.exists(FILES["depo"]):
    pd.DataFrame(columns=["Tarih", "Cari Adı", "Malzeme Adı", "Birim", "Sabah Çıkan", "Akşam İade", "Net Harcanan", "Teslim Eden"]).to_csv(FILES["depo"], index=False)

st.set_page_config(page_title="Fırat Yıldız Mühendislik ERP", layout="wide", page_icon="⚡")

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
    st.session_state["user_info"] = {}

if not st.session_state["authenticated"]:
    st.subheader("🔒 Fırat Yıldız Mühendislik - ERP Girişi (Döviz Destekli)")
    email_input = st.text_input("E-Posta Adresiniz")
    sifre_input = st.text_input("Şifreniz", type="password")
    if st.button("Sisteme Giriş Yap", use_container_width=True):
        df_u = pd.read_csv(FILES["users"])
        user_row = df_u[(df_u["Email"] == email_input) & (df_u["Şifre"] == str(sifre_input))]
        if not user_row.empty:
            st.session_state["authenticated"] = True
            st.session_state["user_info"] = user_row.iloc[0].to_dict()
            st.rerun()
        else:
            st.error("Hatalı E-Posta veya Şifre!")
    st.stop()

user = st.session_state["user_info"]
col_u, col_l = st.columns(2)
col_u.markdown(f"👤 **Kullanıcı:** {user['İsim']} {user['Soyisim']} | 🎭 **Yetki:** `{user['Rol']}`")
if col_l.button("🚪 Çıkış Yap", use_container_width=True):
    st.session_state["authenticated"] = False
    st.session_state["user_info"] = {}
    st.rerun()

tab1, tab2, tab3, tab4 = st.tabs(["📊 Finans & Hakediş Paneli", "📦 Depo Giriş-Çıkış Takibi", "💼 Cari & İş Tanımlama", "👥 Personel Yönetimi"])

with tab1:
    st.header("📊 Canlı Dövizli Hakediş ve Bakiye Raporlama")
    df_c = pd.read_csv(FILES["cariler"])
    df_h = pd.read_csv(FILES["hakedis"])
    cari_secim = st.selectbox("Raporlanacak Cari / İş Seçin", options=df_c["Cari Adı"].unique() if not df_c.empty else ["Cari Yok"])
    df_h_filtered = df_h[df_h["Cari Adı"] == cari_secim]
    
    p_birimi = df_c[df_c["Cari Adı"] == cari_secim]["Para Birimi"].values[0] if (not df_c.empty and cari_secim in df_c["Cari Adı"].values) else "TL"
        
    if user["Rol"] in ["Admin", "Yönetici"]:
        sozlesme = df_c[df_c["Cari Adı"] == cari_secim]["Sözleşme Bedeli"].sum() if not df_c.empty else 0
        toplam_hakedis = df_h_filtered["Toplam Tutar"].sum()
        kalan_bakiye = max(sozlesme - toplam_hakedis, 0.0)
        m1, m2, m3 = st.columns(3)
        m1.metric(f"📜 Toplam Sözleşme Bedeli ({p_birimi})", f"{sozlesme:,.2f} {p_birimi}")
        m2.metric(f"🛠️ Toplam Hak Edilen Tutar ({p_birimi})", f"{toplam_hakedis:,.2f} {p_birimi}")
        m3.metric(f"💰 Kalan Cari Bakiye ({p_birimi})", f"{kalan_bakiye:,.2f} {p_birimi}")
        st.markdown("---")

    st.subheader("📋 Güncel Hakediş Tablosu")
    if user["Rol"] in ["Admin", "Yönetici"]:
        st.dataframe(df_h_filtered, use_container_width=True)
        if user["Rol"] == "Admin" and not df_h_filtered.empty:
            csv_h = df_h_filtered.to_csv(index=False).encode('utf-8')
            st.download_button(label="📥 Excel Olarak İndir", data=csv_h, file_name=f"{cari_secim}_hakedis.csv", mime="text/csv")
    else:
        st.dataframe(df_h_filtered[["Tarih", "Cari Adı", "Kategori", "İş Kalemi", "Birim", "Miktar", "Para Birimi", "Personel"]], use_container_width=True)

    if user["Rol"] == "Admin" and not df_h_filtered.empty:
        st.markdown("### 🛠️ Admin Hakediş Kayıt Düzenleme")
        h_index_list = df_h_filtered.index.tolist()
        secilen_h_index = st.selectbox("Düzenlemek istediğiniz hakediş satır numarasını seçin:", h_index_list)
        if secilen_h_index in df_h.index:
            h_row = df_h.loc[secilen_h_index]
            with st.form(f"edit_h_form_{secilen_h_index}"):
                he1, he2 = st.columns(2)
                edit_h_tarih = he1.date_input("Tarih Güncelle", value=datetime.strptime(h_row["Tarih"], '%Y-%m-%d'))
                edit_h_kat = he2.selectbox("Kategori Güncelle", ["Kuvvetli Akım", "Zayıf Akım", "Aydınlatma"], index=["Kuvvetli Akım", "Zayıf Akım", "Aydınlatma"].index(h_row["Kategori"]))
                edit_h_kalem = st.text_input("İş Kalemi Güncelle", value=h_row["İş Kalemi"])
                he3, he4, he5 = st.columns(3)
                edit_h_birim = he3.selectbox("Birim Güncelle", ["Metre", "Adet", "Takım", "Lot"], index=["Metre", "Adet", "Takım", "Lot"].index(h_row["Birim"]))
                edit_h_fiyat = he4.number_input(f"Birim Fiyat Güncelle ({p_birimi})", min_value=0.0, value=float(h_row["Birim Fiyat"]))
                edit_h_miktar = he5.number_input("Miktar Güncelle", min_value=0.0, value=float(h_row["Miktar"]))
                edit_h_fatura = st.selectbox("Fatura Durumu Güncelle", ["Fatura Kesilmedi", "Fatura Kesildi - Ödeme Bekliyor", "Fatura Kesildi - Ödeme Alındı"], index=["Fatura Kesilmedi", "Fatura Kesildi - Ödeme Bekliyor", "Fatura Kesildi - Ödeme Alındı"].index(h_row["Fatura Durumu"]))
                eh_col1, eh_col2 = st.columns(2)
                if eh_col1.form_submit_button("🔄 Güncelle", use_container_width=True):
                    df_h.at[secilen_h_index, "Tarih"] = edit_h_tarih.strftime('%Y-%m-%d')
                    df_h.at[secilen_h_index, "Kategori"] = edit_h_kat
                    df_h.at[secilen_h_index, "İş Kalemi"] = edit_h_kalem
                    df_h.at[secilen_h_index, "Birim"] = edit_h_birim
                    df_h.at[secilen_h_index, "Birim Fiyat"] = edit_h_fiyat
                    df_h.at[secilen_h_index, "Miktar"] = edit_h_miktar
                    df_h.at[secilen_h_index, "Toplam Tutar"] = edit_h_fiyat * edit_h_miktar
                    df_h.at[secilen_h_index, "Fatura Durumu"] = edit_h_fatura
                    df_h.to_csv(FILES["hakedis"], index=False)
                    st.success("Hakediş güncellendi!")
                    st.rerun()
                if eh_col2.form_submit_button("🚨 Sil", use_container_width=True):
                    df_h = df_h.drop(secilen_h_index).reset_index(drop=True)
                    df_h.to_csv(FILES["hakedis"], index=False)
                    st.success("Kayıt silindi!")
                    st.rerun()

    st.markdown("---")
    st.subheader(f"📝 Yeni İmalat Girişi ({p_birimi})")
    with st.form("hakedis_form", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        tarih = c1.date_input("İmalat Tarihi")
        kat = c2.selectbox("Kategori", ["Kuvvetli Akım", "Zayıf Akım", "Aydınlatma"])
        is_kalemi = c3.text_input("Yapılan İş / Malzeme")
        c4, c5, c6 = st.columns(3)
        birim = c4.selectbox("Birim ", ["Metre", "Adet", "Takım", "Lot"])
        b_fiyat = c5.number_input(f"Birim Fiyat ({p_birimi})", min_value=0.0)
        miktar = c6.number_input("Miktar / Metraj", min_value=0.0)
        f_durum = "Fatura Kesilmedi"
        if user["Rol"] in ["Admin", "Yönetici"]:
            f_durum = st.selectbox("Fatura Durumu", ["Fatura Kesilmedi", "Fatura Kesildi - Ödeme Bekliyor", "Fatura Kesildi - Ödeme Alındı"])
        if st.form_submit_button("💾 Hakedişi Kaydet", use_container_width=True):
            toplam = miktar * b_fiyat
            personel_adi = f"{user['İsim']} {user['Soyisim']}"
            yeni_h = pd.DataFrame([[tarih.strftime('%Y-%m-%d'), cari_secim, kat, is_kalemi, birim, b_fiyat, miktar, toplam, p_birimi, f_durum, personel_adi]], columns=df_h.columns)
            pd.concat([df_h, yeni_h], ignore_index=True).to_csv(FILES["hakedis"], index=False)
            st.success("Hakediş kaydedildi!")
            st.rerun()

# --- TAB 2: DEPO ---
with tab2:
    st.header("📦 Şantiye Depo Giriş / Çıkış ve İade Takibi")
    df_d = pd.read_csv(FILES["depo"])
    df_d_filtered = df_d[df_d["Tarih"] == st.date_input("Rapor Tarihi", value=datetime.now()).strftime('%Y-%m-%d')]
    st.dataframe(df_d_filtered, use_container_width=True)
    
    if user["Rol"] == "Admin" and not df_d_filtered.empty:
        st.markdown("### 🛠️ Admin Depo Kaydı Düzenleme")
        secilen_d_index = st.selectbox("Düzenlenecek depo satır no:", df_d_filtered.index.tolist())
        if secilen_d_index in df_d.index:
            d_row = df_d.loc[secilen_d_index]
            with st.form(f"edit_d_form_{secilen_d_index}"):
                edit_d_malzeme = st.text_input("Malzeme Adı", value=d_row["Malzeme Adı"])
                de1, de2 = st.columns(2)
                edit_d_cikis = de1.number_input("Sabah Çıkan", min_value=0.0, value=float(d_row["Sabah Çıkan"]))
                edit_d_iade = de2.number_input("Akşam İade", min_value=0.0, value=float(d_row["Akşam İade"]))
                if st.form_submit_button("🔄 Güncelle", use_container_width=True):
                    df_d.at[secilen_d_index, "Malzeme Adı"] = edit_d_malzeme
                    df_d.at[secilen_d_index, "Sabah Çıkan"] = edit_d_cikis
                    df_d.at[secilen_d_index, "Akşam İade"] = edit_d_iade
                    df_d.at[secilen_d_index, "Net Harcanan"] = edit_d_cikis - edit_d_iade
                    df_d.to_csv(FILES["depo"], index=False)
                    st.success("Depo kaydı güncellendi!")
                    st.rerun()
                                    if st.form_submit_button("🚨 Sil", use_container_width=True):
                    df_d = df_d.drop(secilen_d_index).reset_index(drop=True)
                    df_d.to_csv(FILES["depo"], index=False)
                    st.success("Depo kaydı silindi!")
                    st.rerun()

    st.markdown("---")
    st.subheader("📥 Yeni Depo Hareketi Ekle")
    with st.form("depo_form", clear_on_submit=True):
        d1, d2 = st.columns(2)
        d_tarih = d1.date_input("Tarih")
        d_cari = d2.selectbox("Malzemenin Gittiği Şantiye/Cari", options=df_c["Cari Adı"].unique() if not df_c.empty else ["Cari Yok"])
        d_malzeme = st.text_input("Malzeme Adı")
        d3, d4, d5 = st.columns(3)
        d_birim = d3.selectbox("Birim", ["Metre", "Adet", "Koli", "Kg"])
        d_cikis = d4.number_input("Sabah Çıkan Miktar", min_value=0.0)
        d_iade = d5.number_input("Akşam İade Miktar", min_value=0.0)
        if st.form_submit_button("📦 Depo Hareketini Kaydet", use_container_width=True):
            yeni_d = pd.DataFrame([[d_tarih.strftime('%Y-%m-%d'), d_cari, d_malzeme, d_birim, d_cikis, d_iade, d_cikis-d_iade, f"{user['İsim']} {user['Soyisim']}"]], columns=df_d.columns)
            pd.concat([df_d, yeni_d], ignore_index=True).to_csv(FILES["depo"], index=False)
            st.success("Depo hareketi işlendi!")
            st.rerun()

# --- TAB 3: CARİ ---
with tab3:
    st.header("💼 Cari Hesap ve Sözleşme Tanımlama")
    df_c = pd.read_csv(FILES["cariler"])
    st.dataframe(df_c, use_container_width=True)

    if user["Rol"] == "Admin" and not df_c.empty:
        st.markdown("### 🛠️ Admin Cari Düzenleme")
        secilen_c_index = st.selectbox("Düzenlenecek cari no:", df_c.index.tolist())
        if secilen_c_index in df_c.index:
            c_row = df_c.loc[secilen_c_index]
            with st.form(f"edit_c_form_{secilen_c_index}"):
                edit_c_adi = st.text_input("Cari Adı", value=c_row["Cari Adı"])
                edit_c_bedel = st.number_input("Sözleşme Bedeli", min_value=0.0, value=float(c_row["Sözleşme Bedeli"]))
                edit_c_para = st.selectbox("Para Birimi", ["TL", "GBP", "EUR", "USD"], index=["TL", "GBP", "EUR", "USD"].index(c_row["Para Birimi"]))
                if st.form_submit_button("🔄 Güncelle", use_container_width=True):
                    df_c.at[secilen_c_index, "Cari Adı"] = edit_c_adi
                    df_c.at[secilen_c_index, "Sözleşme Bedeli"] = edit_c_bedel
                    df_c.at[secilen_c_index, "Para Birimi"] = edit_c_para
                    df_c.to_csv(FILES["cariler"], index=False)
                    st.success("Cari güncellendi!")
                    st.rerun()
                if st.form_submit_button("🚨 Sil", use_container_width=True):
                    df_c = df_c.drop(secilen_c_index).reset_index(drop=True)
                    df_c.to_csv(FILES["cariler"], index=False)
                    st.success("Cari silindi!")
                    st.rerun()

    st.markdown("---")
    if user["Rol"] in ["Admin", "Yönetici"]:
        st.subheader("➕ Yeni Dövizli Cari Tanımla")
        with st.form("cari_form", clear_on_submit=True):
            new_cari = st.text_input("Yeni Cari / Proje Adı")
            cc1, cc2 = st.columns(2)
            new_bedel = cc1.number_input("Toplam Sözleşme Bedeli", min_value=0.0)
            new_para = cc2.selectbox("Para Birimi Seçin", ["TL", "GBP", "EUR", "USD"])
            if st.form_submit_button("💼 Cariyi Kaydet", use_container_width=True):
                if new_cari:
                    yeni_c = pd.DataFrame([[new_cari, new_bedel, new_para]], columns=df_c.columns)
                    pd.concat([df_c, yeni_c], ignore_index=True).to_csv(FILES["cariler"], index=False)
                    st.success("Cari Açıldı!")
                    st.rerun()

# --- TAB 4: PERSONEL ---
with tab4:
    st.header("👥 Personel Listesi ve Yetkilendirme")
    df_u = pd.read_csv(FILES["users"])
    st.dataframe(df_u[["İsim", "Soyisim", "Email", "Rol"]], use_container_width=True)

    if user["Rol"] == "Admin" and not df_u.empty:
        st.markdown("### 🛠️ Admin Personel Düzenleme")
        secilen_u_index = st.selectbox("Düzenlenecek personel no:", df_u.index.tolist())
        if secilen_u_index in df_u.index:
            u_row = df_u.loc[secilen_u_index]
            with st.form(f"edit_u_form_{secilen_u_index}"):
                ue1, ue2 = st.columns(2)
                edit_u_isim = ue1.text_input("İsim", value=u_row["İsim"])
                edit_u_soyisim = ue2.text_input("Soyisim", value=u_row["Soyisim"])
                edit_u_sifre = st.text_input("Şifre", value=str(u_row["Şifre"]))
                edit_u_rol = st.selectbox("Rol", ["Admin", "Yönetici", "Personel"], index=["Admin", "Yönetici", "Personel"].index(u_row["Rol"]))
                if st.form_submit_button("🔄 Güncelle", use_container_width=True):
                    df_u.at[secilen_u_index, "İsim"] = edit_u_isim
                    df_u.at[secilen_u_index, "Soyisim"] = edit_u_soyisim
                    df_u.at[secilen_u_index, "Şifre"] = edit_u_sifre
                    df_u.at[secilen_u_index, "Rol"] = edit_u_rol
                    df_u.to_csv(FILES["users"], index=False)
                    st.success("Kullanıcı güncellendi!")
                    st.rerun()
                if st.form_submit_button("🚨 Sil", use_container_width=True):
                    if u_row["Email"] == "admin@firatyildiz.com":
                        st.error("Ana sistem yöneticisi silinemez!")
                    else:
                        df_u = df_u.drop(secilen_u_index).reset_index(drop=True)
                        df_u.to_csv(FILES["users"], index=False)
                        st.success("Kullanıcı silindi!")
                        st.rerun()

    st.markdown("---")
    if user["Rol"] == "Admin":
        st.subheader("➕ Yeni Personel Tanımla")
        with st.form("user_form", clear_on_submit=True):
            u1, u2 = st.columns(2)
            p_mail = u1.text_input("Personel E-Posta")
            p_sifre = u2.text_input("Personel Şifresi")
            u3, u4, u5 = st.columns(3)
            p_isim = u3.text_input("Adı")
            p_soyisim = u4.text_input("Soyadı")
            p_rol = u5.selectbox("Yetki Seviyesi", ["Admin", "Yönetici", "Personel"])
            if st.form_submit_button("👥 Personeli Kaydet", use_container_width=True):
                yeni_u = pd.DataFrame([[p_mail, p_isim, p_soyisim, p_sifre, p_rol]], columns=df_u.columns)
                pd.concat([df_u, yeni_u], ignore_index=True).to_csv(FILES["users"], index=False)
                st.success("Personel eklendi!")
                st.rerun()

