# **AI Image Editing Backend (FastAPI)**

Bu proje, bir resim ve metin komutu (prompt) alarak yapay zeka destekli düzenlemeler yapan ve sonucu bir URL olarak dönen bir backend servisidir. Servis, asenkron yapısı sayesinde uzun süren yapay zeka işlemlerini verimli bir şekilde yönetmek üzere tasarlanmıştır.

Proje, Voltran'daki bir iş başvurusu için teknik değerlendirme (case study) olarak geliştirilmiştir.

-----

### **Live API**

  * **Base URL:** `https://voltran-case-backend.onrender.com`

-----

## **Mimari Genel Bakış (Architecture Overview)**

Servis, asenkron görev yönetimi üzerine kurulu bir mimari kullanır. Bir istemciden (client) gelen resim düzenleme isteği, anında bir iş (job) kimliği ile yanıtlanır ve asıl işlem arka planda yürütülür. Bu, istemcinin uzun süre beklemesini engeller.

**İşlem Akışı:**

1.  **İstek:** Bir istemci, `POST /api/jobs` endpoint'ine bir resim dosyası ve metin komutu gönderir.
2.  **İş Oluşturma:** FastAPI, PostgreSQL veritabanında `pending` (beklemede) durumunda yeni bir iş (job) kaydı oluşturur.
3.  **Anında Yanıt:** Backend, oluşturulan işin `job_id`'sini anında istemciye geri döner.
4.  **Asenkron İşleme:** Arka planda bir "background task", gelen resim verisini (bytes) ve metin komutunu `fal.ai` API'sine `multipart/form-data` olarak gönderir. Bu yöntem, dosyaları geçici olarak sunucuda saklama ihtiyacını ortadan kaldırarak daha güvenilir bir mimari sunar.
5.  **Durum Sorgulama (Polling):** İstemci, aldığı `job_id` ile `GET /api/jobs/{job_id}` endpoint'ine periyodik olarak istek atarak işin durumunu (`processing`, `done`, `failed`) kontrol eder.
6.  **Sonuç:** `fal.ai` işlemi tamamladığında, backend veritabanındaki ilgili iş kaydını `done` (tamamlandı) olarak günceller ve sonuç resmin URL'sini kaydeder. İstemci, bu güncel durumu bir sonraki sorgusunda alarak sonuca erişir.

## **Özellikler (Features)**

  * **AI Destekli Düzenleme:** `fal.ai`'nin `seedream-v4` modelini kullanarak resimden-resime (image-to-image) düzenleme.
  * **Asenkron İş Yönetimi:** FastAPI'nin `BackgroundTasks` özelliği ile verimli görev işleme.
  * **REST API:** Standart HTTP metotları ile kolayca entegre olabilen API endpoint'leri.
  * **BONUS - Kalıcı İş Geçmişi:** Tüm düzenleme işlerinin geçmişi, Render üzerinde çalışan bir PostgreSQL veritabanında kalıcı olarak saklanır.

## **Kullanılan Teknolojiler**

  * **Framework & Sunucu:** Python 3.11, FastAPI, Uvicorn
  * **Veritabanı:** SQLAlchemy ORM, PostgreSQL (Production), SQLite (Development)
  * **Veri Doğrulama:** Pydantic
  * **API İstekleri:** `httpx` (Asenkron)
  * **AI Model:** `fal.ai` - `bytedance/seedream/v4/edit`
  * **Deployment:** Render.com (Web Service + Managed PostgreSQL)

## **Kurulum ve Çalıştırma**

### **Lokal Geliştirme Ortamı**

**Ön Gereksinimler:**

  * Python 3.9+

**Backend Kurulumu:**

```bash
# 1. Proje dizinine gidin
cd /path/to/voltran_case_backend

# 2. Python virtual environment oluşturun ve aktif edin
python -m venv .venv
source .venv/bin/activate

# 3. Gerekli paketleri yükleyin
pip install -r requirements.txt

# 4. .env dosyasını oluşturun ve içindeki FAL_API_KEY gibi değişkenleri ayarlayın.
nano .env

# 5. Sunucuyu başlatın
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### **API Test (cURL)**

Aşağıdaki komutlarla canlıya alınmış API'yi test edebilirsiniz.

```bash
# Yeni bir düzenleme işi oluştur (dosya yolunu güncelleyin)
curl -X POST "https://voltran-case-backend.onrender.com/api/jobs" \
  -H "Content-Type: multipart/form-data" \
  -F "prompt=make it look like a vintage poster" \
  -F "file=@/path/to/your/image.png"

# Dönen job_id ile durumunu sorgula
curl "https://voltran-case-backend.onrender.com/api/jobs/<DÖNEN_JOB_ID>"
```

## **API Endpoint'leri**

| Method | Path                  | Açıklama                                       |
|--------|-----------------------|------------------------------------------------|
| `POST` | `/api/jobs`           | Yeni bir resim düzenleme işi oluşturur.        |
| `GET`  | `/api/jobs`           | Oluşturulmuş tüm işleri listeler (limit: 50).  |
| `GET`  | `/api/jobs/{job_id}`  | Belirli bir işin durumunu ve sonucunu döndürür.|

## **AI Araçları Kullanımı**

Projenin geliştirme sürecinde, belirli konularda verimliliği artırmak amacıyla **ChatGPT** ve **Gemini** gibi yapay zeka asistanlarından destek alınmıştır. Bu araçlar;

  * SQLAlchemy ve Pydantic için standart kod yapılarının (boilerplate) oluşturulmasında,
  * `httpx` kütüphanesinin asenkron dosya yükleme gibi spesifik kullanımları hakkında bilgi edinilmesinde,
  * ve karşılaşılan hataların çözümünde bir araştırma aracı olarak kullanılmıştır.


### **Proje Yapısı Üzerine Not**

Bu proje, backend ve frontend servisleri için iki ayrı repository olarak yapılandırılmıştır. Bu "multi-repo" yaklaşımı, her bir servisin (backend/frontend) kendi bağımlılıklarını, testlerini ve dağıtım (deployment) süreçlerini bağımsız olarak yönetmesine olanak tanıyan modern bir geliştirme pratiğini yansıtmaktadır.

* **Backend Repository:** `https://github.com/Saner-y/voltran_case_backend`
* **Frontend Repository:** `https://github.com/Saner-y/volttan_case_frontend`
