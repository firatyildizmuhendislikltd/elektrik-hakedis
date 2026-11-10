import os
from datetime import datetime
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

FILE_TO_BACKUP = 'teklif_hakedis_db.csv'
SERVICE_ACCOUNT_FILE = 'credentials.json'
DRIVE_FOLDER_ID = '1sj87S1ngOGmK-n0UQ1YPNPwEvZZtTDJY'
SCOPES = ['https://googleapis.com']

def cift_yedekleme_yap():
    if not os.path.exists(FILE_TO_BACKUP):
        return "⚠️ Yedeklenecek ana veri dosyası henüz oluşmadı."

    zaman_damgasi = datetime.now().strftime("%Y-%m-%d_%H-%M")
    yedek_dosya_adi = f"yedek_{zaman_damgasi}_{FILE_TO_BACKUP}"

    try:
        if os.path.exists(SERVICE_ACCOUNT_FILE):
            creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
            service = build('drive', 'v3', credentials=creds)

            file_metadata = {
                'name': yedek_dosya_adi,
                'parents': [DRIVE_FOLDER_ID]
            }
            media = MediaFileUpload(FILE_TO_BACKUP, mimetype='text/csv')
            service.files().create(body=file_metadata, media_body=media, fields='id').execute()
            return "☁️ Veriler Google Drive bulut klasörünüze başarıyla yedeklendi."
        else:
            return "⚠️ credentials.json bulunamadığı için bulut yedeği atlandı."
    except Exception as e:
        return f"❌ Google Drive hatası: {str(e)}"
