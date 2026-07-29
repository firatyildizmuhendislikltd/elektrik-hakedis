import streamlit as st
import pandas as pd
import os
from datetime import datetime

FILES = {"users": "erp_u.csv", "cariler": "erp_c.csv", "hakedis": "erp_h.csv", "depo": "erp_d.csv"}

for f, path in FILES.items():
    if not os.path.exists(path):
        if f == "users": pd.DataFrame([["admin@firatyildiz.com", "Fırat", "Yıldız", "admin2026", "Admin"]], columns=["Email", "İsim", "Soyisim", "Şifre", "Rol"]).to_csv(path, index=False)
        elif f == "cariler": pd.DataFrame([["X Konut Projesi", 2500000.0, "TL"]], columns=["Cari Adı", "Sözleşme Bedeli", "Para Birimi"]).to_csv(path, index=False)
        elif f == "hakedis": pd.DataFrame(columns=["Tarih", "Cari Adı", "Kategori", "İş Kalemi", "Birim", "Birim Fiyat", "Miktar", "Toplam Tutar", "Para Birimi", "Personel"]).to_csv(path, index=False)
        elif f == "depo": pd.DataFrame(columns=["Tarih", "Cari Adı", "Malzeme Adı", "Birim", "Sabah Çıkan", "Akşam İade", "Net Harcanan", "Birim Fiyat", "Hakedise_Gitti", "Personel"]).to_csv(path, index=False)

st.set_page_config(page_title="Fırat Yıldız ERP", layout="wide", page_icon="⚡")

if "auth" not in st.session_state: st.session_state["auth"], st.session_state["u"] = False, {}

if not st.session_state["auth"]:
    st.subheader("🔒 Fırat Yıldız Mühendislik - ERP Girişi")
    em, pas = st.text_input("E-Posta"), st.text_input("Şifre", type="password")
    if st.button("Sisteme Giriş Yap", use_container_width=True):
        df_u = pd.read_csv(FILES["users"])
        row = df_u[(df_u["Email"] == em) & (df_u["Şifre"] == str(pas))]
        if not row.empty: st.session_state["auth"], st.session_state["u"] = True, row.iloc[0].to_dict(); st.rerun()
        else: st.error("Hatalı Giriş!")
    st.stop()

u = st.session_state["u"]
col_u, col_l = st.columns(2)
col_u.markdown(f"👤 **Kullanıcı:** {u['İsim']} {u['Soyisim']} | 🎭 **Yetki:** `{u['Rol']}`")
if col_l.button("🚪 Çıkış Yap", use_container_width=True): st.session_state["auth"] = False; st.rerun()

t1, t2, t3, t4, t5 = st.tabs(["📊 Hakediş & Finans", "📦 Depo Takibi", "🖨️ Yönetici Raporları", "💼 Cari Tanımlama", "👥 Personel Yönetimi"])

with t1:
    st.header("📊 Canlı Dövizli Hakediş Paneli")
    df_c, df_h = pd.read_csv(FILES["cariler"]), pd.read_csv(FILES["hakedis"])
    c_sec = st.selectbox("Cari Seçin", options=df_c["Cari Adı"].unique() if not df_c.empty else ["Cari Yok"])
    df_hf = df_h[df_h["Cari Adı"] == c_sec]
    pb = str(df_c[df_c["Cari Adı"] == c_sec]["Para Birimi"].values[0]) if (not df_c.empty and c_sec in df_c["Cari Adı"].values) else "TL"
    
    if u["Rol"] in ["Admin", "Yönetici"]:
        sz = float(df_c[df_c["Cari Adı"] == c_sec]["Sözleşme Bedeli"].sum())
        th = float(df_hf["Toplam Tutar"].sum())
        m1, m2, m3 = st.columns(3)
        m1.metric("Sözleşme Bedeli", f"{sz:,.2f} {pb}")
        m2.metric("Hak Edilen Tutar (Canlı)", f"{th:,.2f} {pb}")
        m3.metric("Kalan Bakiye", f"{max(sz-th, 0.0):,.2f} {pb}")
        st.markdown("---")

    st.subheader("📋 Güncel Hakediş Tablosu")
    st.dataframe(df_hf if u["Rol"] in ["Admin", "Yönetici"] else df_hf[["Tarih", "Cari Adı", "Kategori", "İş Kalemi", "Birim", "Miktar", "Para Birimi", "Personel"]], use_container_width=True)

    if u["Rol"] == "Admin" and not df_hf.empty:
        st.subheader("🛠️ Admin Hakediş Düzenleme / Silme")
        idx = st.selectbox("Düzenlenecek hakediş satır no:", df_hf.index.tolist())
        with st.form("f_h_edit"):
            f_kalem = st.text_input("İş Kalemi", value=df_h.loc[idx, "İş Kalemi"])
            f_fiyat = st.number_input("Birim Fiyat", value=float(df_h.loc[idx, "Birim Fiyat"]))
            f_mik = st.number_input("Miktar", value=float(df_h.loc[idx, "Miktar"]))
            b1, b2 = st.columns(2)
            if b1.form_submit_button("🔄 Güncelle", use_container_width=True):
                df_h.at[idx, "İş Kalemi"], df_h.at[idx, "Birim Fiyat"], df_h.at[idx, "Miktar"], df_h.at[idx, "Toplam Tutar"] = f_kalem, f_fiyat, f_mik, f_fiyat*f_mik
                df_h.to_csv(FILES["hakedis"], index=False); st.rerun()
            if b2.form_submit_button("🚨 Sil", use_container_width=True): df_h.drop(idx).reset_index(drop=True).to_csv(FILES["hakedis"], index=False); st.rerun()

    with st.form("f_h_add", clear_on_submit=True):
        st.subheader("➕ El İle Manuel İmalat Girişi")
        h1, h2, h3 = st.columns(3)
        tr, kt, kl = h1.date_input("Tarih"), h2.selectbox("Kategori", ["Kuvvetli Akım", "Zayıf Akım", "Aydınlatma"]), h3.text_input("İş / Malzeme Adı")
        h4, h5, h6 = st.columns(3)
        br, fy, mk = h4.selectbox("Birim", ["Metre", "Adet", "Takım", "Lot"]), h5.number_input("Birim Fiyat", min_value=0.0), h6.number_input("Miktar", min_value=0.0)
        if st.form_submit_button("💾 Manuel Hakediş Kaydet", use_container_width=True):
            if not kl.strip() or mk <= 0: st.error("❌ HATA: Alanlar boş bırakılamaz!")
            else: pd.concat([df_h, pd.DataFrame([[tr.strftime('%Y-%m-%d'), c_sec, kt, kl, br, fy, mk, fy*mk, pb, f"{u['İsim']} {u['Soyisim']}"]], columns=df_h.columns)], ignore_index=True).to_csv(FILES["hakedis"], index=False); st.rerun()

with t2:
    st.header("📦 Şantiye Depo Giriş / Çıkış Takibi")
    df_d = pd.read_csv(FILES["depo"])
    d_tr = st.date_input("Rapor Tarihi", value=datetime.now()).strftime('%Y-%m-%d')
    df_df = df_d[df_d["Tarih"] == d_tr]
    st.dataframe(df_df, use_container_width=True)

    if u["Rol"] == "Admin" and not df_df.empty:
        st.subheader("🛠️ Admin Depo Düzenleme / Silme")
        idx_d = st.selectbox("Düzenlenecek depo satır no:", df_df.index.tolist())
        with st.form("f_d_edit"):
            fd_malz = st.text_input("Malzeme", value=df_d.loc[idx_d, "Malzeme Adı"])
            de1, de2 = st.columns(2)
            fd_c = de1.number_input("Sabah Çıkan", value=float(df_d.loc[idx_d, "Sabah Çıkan"]))
            fd_i = de2.number_input("Akşam İade", value=float(df_d.loc[idx_d, "Akşam İade"]))
            bd1, bd2 = st.columns(2)
            if bd1.form_submit_button("🔄 Güncelle", use_container_width=True):
                df_d.at[idx_d, "Malzeme Adı"], df_d.at[idx_d, "Sabah Çıkan"], df_d.at[idx_d, "Akşam İade"], df_d.at[idx_d, "Net Harcanan"] = fd_malz, fd_c, fd_i, fd_c-fd_i
                df_d.to_csv(FILES["depo"], index=False); st.rerun()
            if bd2.form_submit_button("🚨 Sil", use_container_width=True): df_d.drop(idx_d).reset_index(drop=True).to_csv(FILES["depo"], index=False); st.rerun()

    if u["Rol"] in ["Admin", "Yönetici"] and not df_df.empty:
        df_unpriced = df_df[df_df["Hakedise_Gitti"] != "EVET"]
        if not df_unpriced.empty:
            st.markdown("### 💰 Ofis Depo Fiyatlandırma Paneli")
            idx_dp = st.selectbox("Fiyatlandırılacak Satır:", df_unpriced.index.tolist())
            d_row = df_d.loc[idx_dp]
            c_pb = df_c[df_c["Cari Adı"] == d_row["Cari Adı"]]["Para Birimi"].values[0] if d_row["Cari Adı"] in df_c["Cari Adı"].values else "TL"
            with st.form("f_depo_price_form"):
                o_fiyat = st.number_input(f"Birim Fiyat ({c_pb})", min_value=0.0)
                o_kat = st.selectbox("Kategori ", ["Kuvvetli Akım", "Zayıf Akım", "Aydınlatma"])
                if st.form_submit_button("⚡ Fiyatlandır ve Hakedişe Gönder", use_container_width=True):
                    if o_fiyat > 0:
                        df_d.at[idx_dp, "Birim Fiyat"], df_d.at[idx_dp, "Hakedise_Gitti"] = o_fiyat, "EVET"
                        df_d.to_csv(FILES["depo"], index=False)
                        pd.concat([pd.read_csv(FILES["hakedis"]), pd.DataFrame([[d_tr, d_row["Cari Adı"], o_kat, f"[DEPO] {d_row['Malzeme Adı']}", d_row["Birim"], o_fiyat, float(d_row["Net Harcanan"]), float(d_row["Net Harcanan"])*o_fiyat, c_pb, f"{u['İsim']} {u['Soyisim']} (Ofis Onaylı)"]], columns=df_h.columns)], ignore_index=True).to_csv(FILES["hakedis"], index=False)
                        st.success("Aktarıldı!"); st.rerun()

    with st.form("f_d_add", clear_on_submit=True):
        st.subheader("📥 Şantiye Personeli Malzeme Giriş Formu")
        dp1, dp2 = st.columns(2)
        d_cari, d_mlz = dp1.selectbox("Şantiye", options=df_c["Cari Adı"].unique() if not df_c.empty else ["Cari Yok"]), dp2.text_input("Malzeme Adı")
        dp3, dp4, dp5 = st.columns(3)
        d_br, d_cik, d_iad = dp3.selectbox("Birim", ["Metre", "Adet", "Koli", "Kg"]), dp4.number_input("Sabah Çıkan", min_value=0.0), dp5.number_input("Akşam İade", min_value=0.0)
        if st.form_submit_button("📦 Şantiyeden Kaydet", use_container_width=True):
            if not d_mlz.strip() or d_cik <= 0: st.error("❌ HATA: Eksik bilgi!")
            else: pd.concat([df_d, pd.DataFrame([[d_tr, d_cari, d_mlz, d_br, d_cik, d_iad, d_cik-d_iad, 0.0, "HAYIR", f"{u['İsim']} {u['Soyisim']}"]], columns=df_d.columns)], ignore_index=True).to_csv(FILES["depo"], index=False); st.rerun()

with t3:
    st.header("🖨️ Resmi Rapor Üretme ve PDF Çıktı Merkezi")
    if u["Rol"] in ["Admin", "Yönetici"]:
        r_cari = st.selectbox("Rapor Şantiyesi", options=pd.read_csv(FILES["cariler"])["Cari Adı"].unique() if not df_c.empty else ["Cari Yok"])
        df_rf = pd.read_csv(FILES["hakedis"])[pd.read_csv(FILES["hakedis"])["Cari Adı"] == r_cari]
        if not df_rf.empty:
            sz_b = float(df_c[df_c["Cari Adı"] == r_cari]["Sözleşme Bedeli"].sum())
            pb_b = str(df_c[df_c["Cari Adı"] == r_cari]["Para Birimi"].values[0])
            th_b = float(df_rf["Toplam Tutar"].sum())
            st.write(f"📊 **Proje:** {r_cari} | **Sözleşme:** {sz_b:,.2f} {pb_b} | **Hakediş:** {th_b:,.2f} {pb_b} | **Kalan:** {max(sz_b-th_b, 0.0):,.2f} {pb_b}")
            st.dataframe(df_rf[["Tarih", "Kategori", "İş Kalemi", "Birim", "Miktar", "Toplam Tutar", "Personel"]], use_container_width=True)
            if st.button("🖨️ PDF KAYDET / YAZICIYA GÖNDER", use_container_width=True): st.markdown('<script>window.print();</script>', unsafe_allow_html=True)
        else: st.info("Kayıt bulunamadı.")
# --- TAB 4: CARİ ---
with t4:
    st.header("💼 Cari Hesap Tanımlama")
    df_car = pd.read_csv(FILES["cariler"])
    st.dataframe(df_car, use_container_width=True)
    if u["Rol"] == "Admin" and not df_car.empty:
        st.subheader("🛠️ Admin Cari Düzenleme / Silme")
        idx_c = st.selectbox("Düzenlenecek cari no:", df_car.index.tolist())
        with st.form("f_c_edit"):
            fc_adi = st.text_input("Cari Adı", value=df_car.loc[idx_c, "Cari Adı"])
            fc_bd = st.number_input("Sözleşme Bedeli", value=float(df_car.loc[idx_c, "Sözleşme Bedeli"]))
            fc_pr = st.selectbox("Para Birimi", ["TL", "GBP", "EUR", "USD"], index=["TL", "GBP", "EUR", "USD"].index(df_car.loc[idx_c, "Para Birimi"]))
            bc1, bc2 = st.columns(2)
            if bc1.form_submit_button("🔄 Güncelle", use_container_width=True):
                df_car.at[idx_c, "Cari Adı"], df_car.at[idx_c, "Sözleşme Bedeli"], df_car.at[idx_c, "Para Birimi"] = fc_adi, fc_bd, fc_pr
                df_car.to_csv(FILES["cariler"], index=False); st.rerun()
            if bc2.form_submit_button("🚨 Sil", use_container_width=True): df_car.drop(idx_c).reset_index(drop=True).to_csv(FILES["cariler"], index=False); st.rerun()
    if u["Rol"] in ["Admin", "Yönetici"]:
        with st.form("f_c_add", clear_on_submit=True):
            st.subheader("➕ Yeni Cari Hesap Aç")
            nc = st.text_input("Proje Adı")
            cc1, cc2 = st.columns(2)
            nb, np = cc1.number_input("Sözleşme Bedeli", min_value=0.0), cc2.selectbox("Para Birimi", ["TL", "GBP", "EUR", "USD"])
            if st.form_submit_button("💼 Cariyi Kaydet", use_container_width=True):
                if nc: pd.concat([df_car, pd.DataFrame([[nc, nb, np]], columns=df_car.columns)], ignore_index=True).to_csv(FILES["cariler"], index=False); st.rerun()

# --- TAB 5: PERSONEL ---
with t5:
    st.header("👥 Personel Yetkilendirme")
    df_usr = pd.read_csv(FILES["users"])
    st.dataframe(df_usr[["İsim", "Soyisim", "Email", "Rol"]], use_container_width=True)
    if u["Rol"] == "Admin" and not df_usr.empty:
        st.subheader("🛠️ Admin Personel Düzenleme / Silme")
        idx_u = st.selectbox("Düzenlenecek personel no:", df_usr.index.tolist())
        with st.form("f_u_edit"):
            ue1, ue2 = st.columns(2)
            fu_is, fu_sy = ue1.text_input("İsim", value=df_usr.loc[idx_u, "İsim"]), ue2.text_input("Soyisim", value=df_usr.loc[idx_u, "Soyisim"])
            fu_sf = st.text_input("Şifre", value=str(df_usr.loc[idx_u, "Şifre"]))
            fu_rl = st.selectbox("Rol", ["Admin", "Yönetici", "Personel"], index=["Admin", "Yönetici", "Personel"].index(df_usr.loc[idx_u, "Rol"]))
            bu1, bu2 = st.columns(2)
            if bu1.form_submit_button("🔄 Güncelle", use_container_width=True):
                df_usr.at[idx_u, "İsim"], df_usr.at[idx_u, "Soyisim"], df_usr.at[idx_u, "Şifre"], df_usr.at[idx_u, "Rol"] = fu_is, fu_sy, fu_sf, fu_rl
                df_usr.to_csv(FILES["users"], index=False); st.rerun()
            if bu2.form_submit_button("🚨 Sil", use_container_width=True):
                if df_usr.loc[idx_u, "Email"] == "admin@firatyildiz.com": st.error("Ana yönetici silinemez!")
                else: df_usr.drop(idx_u).reset_index(drop=True).to_csv(FILES["users"], index=False); st.rerun()
    if u["Rol"] == "Admin":
        with st.form("f_u_add", clear_on_submit=True):
            st.subheader("➕ Yeni Personel Tanımla")
            pu1, pu2 = st.columns(2)
            pm, ps = pu1.text_input("E-Posta"), pu2.text_input("Şifre")
            u3, u4, u5 = st.columns(3)
            pi, py, pr = u3.text_input("Adı"), u4.text_input("Soyadı"), u5.selectbox("Rol Seviyesi", ["Admin", "Yönetici", "Personel"])
            if st.form_submit_button("👥 Personeli Kaydet", use_container_width=True):
                if pm and ps: pd.concat([df_usr, pd.DataFrame([[pm, pi, py, ps, pr]], columns=df_usr.columns)], ignore_index=True).to_csv(FILES["users"], index=False); st.rerun()


