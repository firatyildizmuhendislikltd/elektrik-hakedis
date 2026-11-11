import streamlit as st
import pandas as pd
import gspread
import json
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

KLASOR_ID = "1sj87S1ngOGmK-n0UQ1YPNPwEvZZtTDJY"
VERI_TABLOSU_ADI = "FiratYildiz_ERP_Veritabani"
KULLANICI_TABLOSU_ADI = "FiratYildiz_Kullanicilar"

SCOPES = [
    "https://googleapis.com",
    "https://googleapis.com"
]

@st.cache_resource
def baglanti_kur():
   creds_dict = dict(st.secrets["gcp_service_account"])
    creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
    client = gspread.authorize(creds)
    drive_service = build('drive', 'v3', credentials=creds)
    return client, drive_service

def tablo_getir_veya_olustur(dosya_adi, basliklar):
    client, drive_service = baglanti_kur()
    query = f"name='{dosya_adi}' and '{KLASOR_ID}' in parents and trashed=false"
    results = drive_service.files().list(q=query, fields="files(id, name)").execute()
    files = results.get('files', [])
    
    if files:
        sheet = client.open_by_key(files['id']).sheet1
    else:
        file_metadata = {
            'name': dosya_adi,
            'mimeType': 'application/vnd.google-apps.spreadsheet',
            'parents': [KLASOR_ID]
        }
        file = drive_service.files().create(body=file_metadata, fields='id').execute()
        sheet = client.open_by_key(file.get('id')).sheet1
        sheet.append_row(basliklar)
    return sheet

def verileri_google_sheets_yukle():
    basliklar = ["Tarih", "Tür", "Proje Adı", "Müşteri/Kurum", "Tutar", "KDV Oranı (%)", "KDV Tutarı", "KDV Dahil Toplam", "Para Birimi", "Durum", "Fatura Durumu", "Yönetici Onayı"]
    sheet = tablo_getir_veya_olustur(VERI_TABLOSU_ADI, basliklar)
    data = sheet.get_all_records()
    if not data:
        return pd.DataFrame(columns=basliklar)
    return pd.DataFrame(data)

def verileri_google_sheets_kaydet(df):
    basliklar = ["Tarih", "Tür", "Proje Adı", "Müşteri/Kurum", "Tutar", "KDV Oranı (%)", "KDV Tutarı", "KDV Dahil Toplam", "Para Birimi", "Durum", "Fatura Durumu", "Yönetici Onayı"]
    sheet = tablo_getir_veya_olustur(VERI_TABLOSU_ADI, basliklar)
    sheet.clear()
    df_temiz = df.fillna("")
    liste_verisi = [basliklar] + df_temiz[basliklar].values.tolist()
    sheet.update(liste_verisi)
    return "☁️ Veriler Google Drive klasörünüzdeki E-Tabloya kalıcı olarak işlendi!"

def kullanicilari_google_sheets_yukle():
    basliklar = ["eposta", "sifre", "rol"]
    sheet = tablo_getir_veya_olustur(KULLANICI_TABLOSU_ADI, basliklar)
    data = sheet.get_all_records()
    if not data:
        varsayilan = [
            ["admin@firma.com", "1234", "Yönetici"],
            ["personel@firma.com", "5678", "Personel"]
        ]
        for row in varsayilan:
            sheet.append_row(row)
        return {"admin@firma.com": {"sifre": "1234", "rol": "Yönetici"}, "personel@firma.com": {"sifre": "5678", "rol": "Personel"}}
    
    kullanici_sozlugu = {}
    for row in data:
        kullanici_sozlugu[str(row["eposta"])] = {"sifre": str(row["sifre"]), "rol": str(row["rol"])}
    return kullanici_sozlugu

def kullanici_google_sheets_ekle(eposta, sifre, rol):
    basliklar = ["eposta", "sifre", "rol"]
    sheet = tablo_getir_veya_olustur(KULLANICI_TABLOSU_ADI, basliklar)
    mevcutlar = kullanicilari_google_sheets_yukle()
    if eposta in mevcutlar:
        return False
    sheet.append_row([eposta, str(sifre), rol])
    return True
