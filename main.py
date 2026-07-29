import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- VERİ TABANLARI ---
FILES = {"users": "erp_u.csv", "cariler": "erp_c.csv", "hakedis": "erp_h.csv", "depo": "erp_d.csv"}

for f, path in FILES.items():
    if not os.path.exists(path):
        if f == "users":
            pd.DataFrame([["admin@firatyildiz.com", "Fırat", "Yıldız", "admin2026", "Admin"]], columns=["Email", "İsim", "Soyisim", "Şifre", "Rol"]).to_csv(path, index=False)
        elif f == "cariler":
            pd.DataFrame([["X Konut Projesi", 2500000.0, "TL"]], columns=["Cari Adı", "Sözleşme Bedeli", "Para Birimi"]).to_csv(path, index=False)
        elif f == "hakedis":
            pd.DataFrame(columns=["Tarih", "Cari Adı", "Kategori", "İş Kalemi", "Birim", "Birim Fiyat", "Miktar", "Toplam Tutar", "Para Birimi", "Personel"]).to_csv(path, index=False)
        elif f == "depo":
            pd.DataFrame(columns=["Tarih", "Cari Adı", "Malzeme Adı", "Birim", "Sabah Çıkan", "Akşam İade", "Net Harcanan", "Personel"]).to_csv(path, index=False)

st.set_page_config(page_title="Fırat Yıldız ERP", layout="wide", page_icon="⚡")

if "auth" not in st.session_state:
    st.session_state["auth"] = False
    st.session_state["u"] = {}

# --- GİRİŞ EKRANI ---
if not st.session_state["auth"]:
    st.subheader("🔒 Fırat Yıldız Mühendislik - ERP Girişi (Döviz Destekli)")
    em = st.text_input("E-Posta")
    pas = st.text_input("Şifre", type="password")
    if st.button("Giriş Yap", use_container_width=True):
        df = pd.read_csv(FILES["users"])
        row = df[(df["Email"] == em) & (df["Şifre"] == str(pas))]
        if not row.empty:
            st.session_state["auth"] = True
            st.session_state["u"] = row.iloc[0].to_dict()
            st.rerun()
        else:
            st.error("Hatalı Giriş!")
    st.stop()

u = st.session_state["u"]
c_u, c_l = st.columns(2)
c_u.markdown(f"👤 {u['İsim']} {u['Soyisim']} | 🎭 `{u['Rol']}`")
if c_l.button("🚪 Çıkış", use_container_width=True):
    st.session_state["auth"] = False
    st.rerun()

t1, t2, t3, t4 = st.tabs(["📊 Hakediş & Finans", "📦 Depo Takibi", "💼 Cari Tanımlama", "👥 Personel Yönetimi"])

# --- TAB 1: HAKEDİŞ ---
with t1:
    df_c = pd.read_csv(FILES["cariler"])
    df_h = pd.read_csv(FILES["hakedis"])
    c_sec = st.selectbox("Cari Seçin", options=df_c["Cari Adı"].unique() if not df_c.empty else ["Cari Yok"])
    df_hf = df_h[df_h["Cari Adı"] == c_sec]
    pb = df_c[df_c["Cari Adı"] == c_sec]["Para Birimi"].values[0] if (not df_c.empty and c_sec in df_c["Cari Adı"].values) else "TL"
    
    if u["Rol"] in ["Admin", "Yönetici"]:
        sz = df_c[df_c["Cari Adı"] == c_sec]["Sözleşme Bedeli"].sum()
        th = df_hf["Toplam Tutar"].sum()
        m1, m2, m3 = st.columns(3)
        m1.metric("Sözleşme Bedeli", f"{sz:,.2f} {pb}")
        m2.metric("Hak Edilen Tutar", f"{th:,.2f} {pb}")
        m3.metric("Kalan Bakiye", f"{max(sz-th, 0.0):,.2f} {pb}")

    st.subheader("📋 Hakediş Tablosu")
    st.dataframe(df_hf if u["Rol"] in ["Admin", "Yönetici"] else df_hf[["Tarih", "Cari Adı", "Kategori", "İş Kalemi", "Birim", "Miktar", "Para Birimi", "Personel"]], use_container_width=True)

    if u["Rol"] == "Admin" and not df_hf.empty:
        st.subheader("🛠️ Düzenleme / Silme (Hakediş)")
        idx = st.selectbox("Satır No Seçin (Hakediş)", df_hf.index.tolist())
        with st.form("f_h_edit"):
            f_kalem = st.text_input("İş Kalemi", value=df_h.loc[idx, "İş Kalemi"])
            f_fiyat = st.number_input("Birim Fiyat", value=float(df_h.loc[idx, "Birim Fiyat"]))
            f_mik = st.number_input("Miktar", value=float(df_h.loc[idx, "Miktar"]))
            b1, b2 = st.columns(2)
            if b1.form_submit_button("🔄 Güncelle", use_container_width=True):
                df_h.at[idx, "İş Kalemi"] = f_kalem
                df_h.at[idx, "Birim Fiyat"] = f_fiyat
                df_h.at[idx, "Miktar"] = f_mik
                df_h.at[idx, "Toplam Tutar"] = f_fiyat * f_mik
                df_h.to_csv(FILES["hakedis"], index=False)
                st.rerun()
            if b2.form_submit_button("🚨 Sil", use_container_width=True):
                df_h.drop(idx).reset_index(drop=True).to_csv(FILES["hakedis"], index=False)
                st.rerun()

    with st.form("f_h_add", clear_on_submit=True):
        st.subheader("➕ Yeni Giriş")
        h1, h2, h3 = st.columns(3)
        tr = h1.date_input("Tarih")
        kt = h2.selectbox("Kategori", ["Kuvvetli Akım", "Zayıf Akım", "Aydınlatma"])
        kl = h3.text_input("İş / Malzeme Adı")
        h4, h5, h6 = st.columns(3)
        br = h4.selectbox("Birim", ["Metre", "Adet", "Takım", "Lot"])
        fy = h5.number_input("Birim Fiyat", min_value=0.0)
        mk = h6.number_input("Miktar", min_value=0.0)
        if st.form_submit_button("💾 Kaydet", use_container_width=True):
            new_row = pd.DataFrame([[tr.strftime('%Y-%m-%d'), c_sec, kt, kl, br, fy, mk, fy*mk, pb, f"{u['İsim']} {u['Soyisim']}"]], columns=df_h.columns)
            pd.concat([df_h, new_row], ignore_index=True).to_csv(FILES["hakedis"], index=False)
            st.rerun()

# --- TAB 2: DEPO ---
with t2:
    df_d = pd.read_csv(FILES["depo"])
    d_tr = st.date_input("Rapor Tarihi", value=datetime.now()).strftime('%Y-%m-%d')
    df_df = df_d[df_d["Tarih"] == d_tr]
    st.dataframe(df_df, use_container_width=True)

    if u["Rol"] == "Admin" and not df_df.empty:
        st.subheader("🛠️ Depo Kaydı Düzenleme / Silme")
        idx_d = st.selectbox("Satır No Seçin (Depo)", df_df.index.tolist())
        with st.form("f_d_edit"):
            fd_malz = st.text_input("Malzeme", value=df_d.loc[idx_d, "Malzeme Adı"])
            fd_c = st.number_input("Sabah Çıkan", value=float(df_d.loc[idx_d, "Sabah Çıkan"]))
            fd_i = st.number_input("Akşam İade", value=float(df_d.loc[idx_d, "Akşam İade"]))
            bd1, bd2 = st.columns(2)
            if bd1.form_submit_button("🔄 Güncelle", use_container_width=True):
                df_d.at[idx_d, "Malzeme Adı"] = fd_malz
                df_d.at[idx_d, "Sabah Çıkan"] = fd_c
                df_d.at[idx_d, "Akşam İade"] = fd_i
                df_d.at[idx_d, "Net Harcanan"] = fd_c - fd_i
                df_d.to_csv(FILES["depo"], index=False)
                st.rerun()
            if bd2.form_submit_button("🚨 Sil", use_container_width=True):
                df_d.drop(idx_d).reset_index(drop=True).to_csv(FILES["depo"], index=False)
                st.rerun()

    with st.form("f_d_add", clear_on_submit=True):
        st.subheader("📥 Yeni Hareket")
        dp1, dp2 = st.columns(2)
        d_cari = dp1.selectbox("Şantiye", options=df_c["Cari Adı"].unique() if not df_c.empty else ["Cari Yok"])
        d_mlz = dp2.text_input("Malzeme")
        dp3, dp4, dp5 = st.columns(3)
        d_br = dp3.selectbox("Birim ", ["Metre", "Adet", "Koli", "Kg"])
        d_cik = dp4.number_input("Sabah Çıkan", min_value=0.0)
        d_iad = dp5.number_input("Akşam İade", min_value=0.0)
        if st.form_submit_button("📦 Kaydet", use_container_width=True):
            new_depo = pd.DataFrame([[d_tr, d_cari, d_mlz, d_br, d_cik, d_iad, d_cik-d_iad, f"{u['İsim']} {u['Soyisim']}"]], columns=df_d.columns)
            pd.concat([df_d, new_depo], ignore_index=True).to_csv(FILES["depo"], index=False)
            st.rerun()
# --- TAB 3: CARİ ---
with t3:
    df_c = pd.read_csv(FILES["cariler"])
    st.dataframe(df_c, use_container_width=True)
    if u["Rol"] == "Admin" and not df_c.empty:
        idx_c = st.selectbox("Satır No Seçin (Cari)", df_c.index.tolist())
        with st.form("f_c_edit"):
            fc_adi = st.text_input("Cari Adı", value=df_c.loc[idx_c, "Cari Adı"])
            fc_bd = st.number_input("Sözleşme Bedeli", value=float(df_c.loc[idx_c, "Sözleşme Bedeli"]))
            fc_pr = st.selectbox("Para Birimi", ["TL", "GBP", "EUR", "USD"], index=["TL", "GBP", "EUR", "USD"].index(df_c.loc[idx_c, "Para Birimi"]))
            bc1, bc2 = st.columns(2)
            if bc1.form_submit_button("🔄 Güncelle", use_container_width=True):
                df_c.at[idx_c, "Cari Adı"] = fc_adi
                df_c.at[idx_c, "Sözleşme Bedeli"] = fc_bd
                df_c.at[idx_c, "Para Birimi"] = fc_pr
                df_c.to_csv(FILES["cariler"], index=False)
                st.rerun()
            if bc2.form_submit_button("🚨 Sil", use_container_width=True):
                df_c.drop(idx_c).reset_index(drop=True).to_csv(FILES["cariler"], index=False)
                st.rerun()
                
    if u["Rol"] in ["Admin", "Yönetici"]:
        with st.form("f_c_add", clear_on_submit=True):
            st.subheader("➕ Yeni Cari Hesap Aç")
            nc = st.text_input("Proje Adı")
            cc1, cc2 = st.columns(2)
            nb = cc1.number_input("Sözleşme Bedeli", min_value=0.0)
            np = cc2.selectbox("Para Birimi", ["TL", "GBP", "EUR", "USD"])
            if st.form_submit_button("💼 Kaydet", use_container_width=True):
                if nc:
                    new_cari = pd.DataFrame([[nc, nb, np]], columns=df_c.columns)
                    pd.concat([df_c, new_cari], ignore_index=True).to_csv(FILES["cariler"], index=False)
                    st.rerun()

# --- TAB 4: PERSONEL ---
with t4:
    df_u = pd.read_csv(FILES["users"])
    st.dataframe(df_u[["İsim", "Soyisim", "Email", "Rol"]], use_container_width=True)
    
    if u["Rol"] == "Admin" and not df_u.empty:
        st.subheader("🛠️ Personel Düzenleme / Silme")
        idx_u = st.selectbox("Satır No Seçin (Kullanıcı)", df_u.index.tolist())
        with st.form("f_u_edit"):
            fu_is = st.text_input("İsim", value=df_u.loc[idx_u, "İsim"])
            fu_sy = st.text_input("Soyisim", value=df_u.loc[idx_u, "Soyisim"])
            fu_sf = st.text_input("Şifre", value=str(df_u.loc[idx_u, "Şifre"]))
            fu_rl = st.selectbox("Rol", ["Admin", "Yönetici", "Personel"], index=["Admin", "Yönetici", "Personel"].index(df_u.loc[idx_u, "Rol"]))
            bu1, bu2 = st.columns(2)
            if bu1.form_submit_button("🔄 Güncelle", use_container_width=True):
                df_u.at[idx_u, "İsim"] = fu_is
                df_u.at[idx_u, "Soyisim"] = fu_sy
                df_u.at[idx_u, "Şifre"] = fu_sf
                df_u.at[idx_u, "Rol"] = fu_rl
                df_u.to_csv(FILES["users"], index=False)
                st.rerun()
            if bu2.form_submit_button("🚨 Sil", use_container_width=True):
                if df_u.loc[idx_u, "Email"] == "admin@firatyildiz.com":
                    st.error("Ana yönetici silinemez!")
                else:
                    df_u.drop(idx_u).reset_index(drop=True).to_csv(FILES["users"], index=False)
                    st.rerun()
                    
    if u["Rol"] == "Admin":
        with st.form("f_u_add", clear_on_submit=True):
            st.subheader("➕ Yeni Personel Tanımla")
            pu1, pu2 = st.columns(2)
            pm = pu1.text_input("E-Posta")
            ps = pu2.text_input("Şifre")
            pu3, pu4, pu5 = st.columns(3)
            pi = pu3.text_input("Adı")
            py = pu4.text_input("Soyadı")
            pr = pu5.selectbox("Rol Seviyesi", ["Admin", "Yönetici", "Personel"])
            if st.form_submit_button("👥 Kaydet", use_container_width=True):
                new_user = pd.DataFrame([[pm, pi, py, ps, pr]], columns=df_u.columns)
                pd.concat([df_u, new_user], ignore_index=True).to_csv(FILES["users"], index=False)
                st.rerun()
