import pandas as pd
import os
from src.machine_manager import MachineManager
import shutil  #Dosya işlemleri için

pd.set_option('display.max_columns', None)
pd.set_option('display.width', 170)
pd.set_option('display.max_rows', None)
pd.set_option('display.float_format', lambda x: '%.3f' % x)

class DataProcessor:
    def __init__(self):
        self.manager = MachineManager()
        self._initialize_directories()

    def _initialize_directories(self):
        required_dirs = ["data", "machine_profiles", "models/trained_models/classification"]
        for directory in required_dirs:
            os.makedirs(directory, exist_ok=True)

    def process_data(self, csv_path="data/ai4i2020.csv"):
        try:
            #Veriyi yükle ve sütun isimlerini standartlaştır
            data = pd.read_csv(csv_path)

            #Veri inceleme
            print("\n" + "=" * 50)
            print("📊 VERİ İNCELEME")
            print("=" * 50)
            print("\n👉 İlk 5 Kayıt:")
            print(data.head())
            print("\n📐 Veri Boyutu:", data.shape)
            print("\nℹ️ Veri Bilgisi:")
            print(data.info())

            #Orijinal ve düzenlenmiş sütun isimlerini kontrol et
            print("Orijinal Sütunlar:", data.columns.tolist())

            #Sütun isimlerini temizle (köşeli parantezleri ve boşlukları kaldır)
            data.columns = [col.replace('[', '').replace(']', '').strip() for col in data.columns]
            print("Düzenlenmiş Sütunlar:", data.columns.tolist())

            #2. Sütun isimlerini kesinleştir
            column_mapping = {
                'Air temperature K': 'air_temp',
                'Process temperature K': 'process_temp',
                'Rotational speed rpm': 'rotational_speed',
                'Torque Nm': 'torque',
                'Tool wear min': 'tool_wear',
                'Machine failure': 'failure'
            }
            data = data.rename(columns=column_mapping)

            #3. AYKIRI DEĞER İŞLEME
            data = self._handle_outliers(data)

            #4. Veri doğrulama ve işleme
            self._validate_data(data)
            data = self._handle_duplicates(data)
            self._create_machine_profiles(data)

            #İŞLENMİŞ VERİYİ KAYDET (YENİ DOSYA)
            processed_path = "data/processed_data.csv"
            data.to_csv(processed_path, index=False)
            print(f"✅ İşlenmiş veri kaydedildi: {processed_path}")
            return data  #İşlenmiş veriyi döndür

        except Exception as e:
            print(f"🔴 Kritik Hata: Veri işleme başarısız: {str(e)}")
            raise

    def _validate_data(self, data):
        #sütun isimlerini kontrol et
        required_columns = [
            'Product ID',
            'Type',
            'air_temp',
            'process_temp',
            'rotational_speed',
            'torque',
            'tool_wear',
            'failure'
        ]
        missing_cols = [col for col in required_columns if col not in data.columns]
        if missing_cols:
            raise ValueError(f"Eksik sütunlar: {missing_cols}")

    def _handle_outliers(self, data):
        print("\n" + "=" * 50)
        print("🔍 AYKIRI DEĞER ANALİZİ")
        print("=" * 50)

        #Sayısal sütunları seç (kategorik olan 'Type' ve 'Product ID' hariç)
        num_cols = ['air_temp', 'process_temp', 'rotational_speed', 'torque', 'tool_wear']

        for col in num_cols:
            low, high = self._outlier_thresholds(data, col)
            print(
                f"{col}: [{low:.2f}, {high:.2f}] aralığı dışında {sum((data[col] < low) | (data[col] > high))} aykırı değer")
            data[col] = data[col].clip(lower=low, upper=high)

        return data

    def _outlier_thresholds(self, dataframe, col_name, q1=0.05, q3=0.95):
        quartile1 = dataframe[col_name].quantile(q1)
        quartile3 = dataframe[col_name].quantile(q3)
        iqr = quartile3 - quartile1
        up_limit = quartile3 + 1.5 * iqr
        low_limit = quartile1 - 1.5 * iqr
        return low_limit, up_limit

    def _handle_duplicates(self, data):
        return data.drop_duplicates(subset=['Product ID'], keep='last') #aynı IDye sahip olanlardan sonuncusunu tut

    def _create_machine_profiles(self, data):
        #Eski verileri temizle
        self.manager.machines.clear()

        #Klasörü yeniden oluştur
        profiles_dir = "machine_profiles"
        if os.path.exists(profiles_dir):
            shutil.rmtree(profiles_dir)
        os.makedirs(profiles_dir, exist_ok=True)

        #Yeni verileri işle
        for _, row in data.iterrows():
            try:
                self.manager.create_machine(
                    machine_id=row['Product ID'],
                    machine_type=row['Type'],
                    features=row.to_dict()
                )
            except Exception as e:
                print(f"⚠️ Hata: {str(e)}")