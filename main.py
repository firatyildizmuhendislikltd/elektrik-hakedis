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
            pd.DataFrame(columns=["Tarih", "Cari Adı", "Malzeme Adı", "Birim", "Sabah Çıkan", "Akşam İade", "Net Harcanan", "Birim Fiyat", "Hakedise_Gitti", "Personel"]).to_csv(path, index=False)

st.set_page_config(page_title="Fırat Yıldız ERP", layout="wide", page_icon="⚡")

if "auth" not in st.session_state:
    st.session_state["auth"] = False
    st.session_state["u"] = {}

# --- GİRİŞ EKRANI (HATA DÜZELTİLDİ) ---
if not st.session_state["auth"]:
    st.subheader("🔒 Fırat Yıldız Mühendislik - ERP Girişi")
    em = st.text_input("E-Posta")
    pas = st.text_input("Şifre", type="password")
    if st.button("Giriş Yap", use_container_width=True):
        df = pd.read_csv(FILES["users"])
        row = df[(df["Email"] == em) & (df["Şifre"] == str(pas))]
        if not row.empty:
            st.session_state["auth"] = True
            st.session_state["u"] = row.iloc[0].to_dict() # KESİN ÇÖZÜM BURADA YAPILDI ([0])
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

tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Hakediş & Finans", "📦 Depo Takibi", "🖨️ Yönetici Raporları", "💼 Cari Tanımlama", "👥 Personel Yönetimi"])

# --- TAB 1: HAKEDİŞ ---
with tab1:
    st.header("📊 Canlı Dövizli Hakediş ve Bakiye Raporlama")
    df_c = pd.read_csv(FILES["cariler"])
    df_h = pd.read_csv(FILES["hakedis"])
    cari_secim = st.selectbox("Raporlanacak Cari / İş Seçin", options=df_c["Cari Adı"].unique() if not df_c.empty else ["Cari Yok"])
    df_hf = df_h[df_h["Cari Adı"] == cari_secim]
    pb = df_c[df_c["Cari Adı"] == cari_secim]["Para Birimi"].values if (not df_c.empty and cari_secim in df_c["Cari Adı"].values) else "TL"
    
    if u["Rol"] in ["Admin", "Yönetici"]:
        sz = df_c[df_c["Cari Adı"] == cari_secim]["Sözleşme Bedeli"].sum()
        th = df_hf["Toplam Tutar"].sum()
        m1, m2, m3 = st.columns(3)
        m1.metric("Sözleşme Bedeli", f"{sz:,.2f} {pb}")
        m2.metric("Hak Edilen Tutar (Canlı)", f"{th:,.2f} {pb}")
        m3.metric("Kalan Bakiye", f"{max(sz-th, 0.0):,.2f} {pb}")

    st.subheader("📋 Güncel Hakediş Tablosu")
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
        st.subheader("➕ El İle Manuel İmalat Girişi")
        h1, h2, h3 = st.columns(3)
        tr = h1.date_input("Tarih")
        kt = h2.selectbox("Kategori", ["Kuvvetli Akım", "Zayıf Akım", "Aydınlatma"])
        kl = h3.text_input("İş / Malzeme Adı")
        h4, h5, h6 = st.columns(3)
        br = h4.selectbox("Birim", ["Metre", "Adet", "Takım", "Lot"])
        fy = h5.number_input("Birim Fiyat", min_value=0.0)
        mk = h6.number_input("Miktar", min_value=0.0)
        if st.form_submit_button("💾 Manuel Hakediş Kaydet", use_container_width=True):
            if not kl.strip() or mk <= 0:
                st.error("❌ HATA: İş/Malzeme adı boş bırakılamaz ve Miktar 0'dan büyük olmalıdır!")
            else:
                new_row = pd.DataFrame([[tr.strftime('%Y-%m-%d'), cari_secim, kt, kl, br, fy, mk, fy*mk, pb, f"{u['İsim']} {u['Soyisim']}"]], columns=df_h.columns)
                pd.concat([df_h, new_row], ignore_index=True).to_csv(FILES["hakedis"], index=False)
                st.rerun()
# --- TAB 2: DEPO ---
with tab2:
    df_d = pd.read_csv(FILES["depo"])
    df_c = pd.read_csv(FILES["cariler"])
    d_tr = st.date_input("Rapor Tarihi", value=datetime.now()).strftime('%Y-%m-%d')
    df_df = df_d[df_d["Tarih"] == d_tr]
    st.subheader("📅 Bugün Şantiyelerden Gelen Depo Hareketleri")
    st.dataframe(df_df, use_container_width=True)

    if not df_df.empty:
        csv_depo_data = df_df.to_csv(index=False, sep=";").encode('utf-8-sig')
        st.download_button(label="📥 Bugünkü Depo Raporunu Excel Olarak İndir (Ayrı Sütunlu)", data=csv_depo_data, file_name=f"{d_tr}_gunluk_depo_raporu.csv", mime="text/csv", use_container_width=True)

    if u["Rol"] in ["Admin", "Yönetici"] and not df_df.empty:
        st.markdown("### 💰 Ofis Depo Fiyatlandırma Paneli")
        df_unpriced = df_df[df_df["Hakedise_Gitti"] != "EVET"]
        if not df_unpriced.empty:
            idx_d = st.selectbox("Fiyatlandırılacak Şantiye Depo Satır Numarasını Seçin:", df_unpriced.index.tolist())
            d_row = df_d.loc[idx_d]
            c_pb = df_c[df_c["Cari Adı"] == d_row["Cari Adı"]]["Para Birimi"].values if d_row["Cari Adı"] in df_c["Cari Adı"].values else "TL"
            st.info(f"📋 Seçilen: {d_row['Cari Adı']} -> {d_row['Malzeme Adı']} (Net Harcanan: {d_row['Net Harcanan']} {d_row['Birim']})")
            with st.form("f_depo_price_form"):
                o_fiyat = st.number_input(f"Bu Malzeme İçin Sözleşme Birim Fiyatını Girin ({c_pb})", min_value=0.0)
                o_kat = st.selectbox("Hakediş Kategorisi", ["Kuvvetli Akım", "Zayıf Akım", "Aydınlatma"])
                if st.form_submit_button("⚡ Fiyatlandır ve Hakediş Tablosuna Gönder", use_container_width=True):
                    if o_fiyat > 0:
                        df_d.at[idx_d, "Birim Fiyat"] = o_fiyat
                        df_d.at[idx_d, "Hakedise_Gitti"] = "EVET"
                        df_d.to_csv(FILES["depo"], index=False)
                        df_h = pd.read_csv(FILES["hakedis"])
                        net_m = float(d_row["Net Harcanan"])
                        auto_hakedis_row = pd.DataFrame([[d_tr, d_row["Cari Adı"], o_kat, f"[DEPO] {d_row['Malzeme Adı']}", d_row["Birim"], o_fiyat, net_m, net_m*o_fiyat, c_pb, f"{u['İsim']} {u['Soyisim']} (Ofis Onaylı)"]], columns=df_h.columns)
                        pd.concat([df_h, auto_hakedis_row], ignore_index=True).to_csv(FILES["hakedis"], index=False)
                        st.success("Malzeme başarıyla bütçelendirildi ve Hakediş sekmesine aktarıldı!")
                        st.rerun()
                    else: st.error("Lütfen 0'dan büyük bir birim fiyat girin!")
        else: st.success("🎉 Bugünkü tüm depo hareketleri hakedişe gönderilmiş!")

    with st.form("f_d_add", clear_on_submit=True):
        st.subheader("📥 Şantiye Personeli Malzeme Çıkış / İade Formu")
        dp1, dp2 = st.columns(2)
        d_cari = dp1.selectbox("Malzemenin Gittiği Şantiye", options=df_c["Cari Adı"].unique() if not df_c.empty else ["Cari Yok"])
        d_mlz = dp2.text_input("Malzeme / Kablo / Şalt Adı")
        dp3, dp4, dp5 = st.columns(3)
        d_br = dp3.selectbox("Birim ", ["Metre", "Adet", "Koli", "Kg"])
        d_cikis_val = dp4.number_input("Sabah Depodan Çıkan Miktar", min_value=0.0)
        d_iade_val = dp5.number_input("Akşam Depoya İade Edilen Miktar", min_value=0.0)
        if st.form_submit_button("📦 Depo Hareketini Şantiyeden Kaydet", use_container_width=True):
            if not d_mlz.strip() or d_cikis_val <= 0:
                st.error("❌ HATA: Malzeme adı boş bırakılamaz ve Sabah Çıkan Miktar 0'dan büyük olmalıdır!")
            else:
                new_depo = pd.DataFrame([[d_tr, d_cari, d_mlz, d_br, d_cikis_val, d_iade_val, d_cikis_val-d_iade_val, 0.0, "HAYIR", f"{u['İsim']} {u['Soyisim']}"]], columns=df_d.columns)
                pd.concat([df_d, new_depo], ignore_index=True).to_csv(FILES["depo"], index=False)
                st.success("Depo hareketi başarıyla şantiyeden kaydedildi, ofis onayına düştü!")
                st.rerun()

# --- TAB 3: YÖNETİCİ RAPORLARI ---
with tab3:
    st.header("🖨️ Resmi Rapor Üretme, Excel ve PDF Çıktı Merkezi")
    if u["Rol"] in ["Admin", "Yönetici"]:
        df_c = pd.read_csv(FILES["cariler"])
        df_h = pd.read_csv(FILES["hakedis"])
        r_cari = st.selectbox("Raporu Basılacak Şantiyeyi Seçin", options=df_c["Cari Adı"].unique() if not df_c.empty else ["Cari Yok"])
        df_r_filtered = df_h[df_h["Cari Adı"] == r_cari]
        
        if not df_r_filtered.empty:
            sz_b = df_c[df_c["Cari Adı"] == r_cari]["Sözleşme Bedeli"].sum()
            pb_b = df_c[df_c["Cari Adı"] == r_cari]["Para Birimi"].values if not df_c.empty else "TL"
            th_b = df_r_filtered["Toplam Tutar"].sum()
            
            st.write(f"📊 **Proje:** {r_cari} | **Sözleşme:** {sz_b:,.2f} {pb_b} | **Hakediş:** {th_b:,.2f} {pb_b} | **Kalan:** {max(sz_b-th_b, 0.0):,.2f} {pb_b}")
            st.dataframe(df_r_filtered, use_container_width=True)
            
            csv_data = df_r_filtered.to_csv(index=False, sep=";").encode('utf-8-sig')
            c_down1, c_down2 = st.columns(2)
            c_down1.download_button(label="📥 Bu Raporu Düzenli EXCEL Olarak Bilgisayara İndir", data=csv_data, file_name=f"{r_cari}_resmi_rapor.csv", mime="text/csv", use_container_width=True)
            
            if c_down2.button("🖨️ RAPORU YAZICIYA GÖNDER / PDF OLARAK KAYDET", use_container_width=True):
                st.markdown('<script>window.print();</script>', unsafe_allow_html=True)
        else: st.info("Bu projeye ait onaylanmış bir kayıt bulunamadı.")
    else: st.warning("Bu bölüme sadece Admin ve Yöneticiler erişebilir.")
# --- TAB 4: CARİ ---
with tab4:
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

# --- TAB 5: PERSONEL ---
with tab5:
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
                if df_u.loc[idx_u, "Email"] == "admin@firatyildiz.com": st.error("Ana yönetici silinemez!")
                else:
                    df_u.drop(idx_u).reset_index(drop=True).to_csv(FILES["users"], index=False)
                    st.rerun()
    if u["Rol"] == "Admin":
        with st.form("f_u_add", clear_on_submit=True):
            st.subheader("➕ Yeni Personel Tanımla")
            pu1, pu2 = st.columns(2)
            pm = pu1.text_input("E-Posta")
            ps = pu2.text_input("Şifre")
            u3, u4, u5 = st.columns(3)
            pi = u3.text_input("Adı")
            py = pu4.text_input("Soyadı")
            pr = pu5.selectbox("Rol Seviyesi", ["Admin", "Yönetici", "Personel"])
            if st.form_submit_button("👥 Kaydet", use_container_width=True):
                new_user = pd.DataFrame([[pm, pi, py, ps, pr]], columns=df_u.columns)
                pd.concat([df_u, new_user], ignore_index=True).to_csv(FILES["users"], index=False)
                st.rerun()
