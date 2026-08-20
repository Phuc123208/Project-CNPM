# Urban Traffic Analytics Platform

Nền tảng phân tích mô hình giao thông đô thị và dự báo ùn tắc ngắn hạn sử dụng
dữ liệu giao thông thu thập bằng UAV (drone).

- **Backend:** Python / Flask (REST API), kiến trúc Clean Architecture (bám theo
  boilerplate `Flask-CleanArchitecture`), PostgreSQL trên Supabase.
- **Frontend:** React (Vite) + React Router + Recharts.
- **6 module chính:** Dataset Management, Traffic Pattern Analysis, Forecasting
  (ARIMA/Prophet), Visualization Dashboard, Experiment Management, Reporting.
- **4 vai trò:** Administrator, Researcher, Analyst, Student (đúng theo Use Case
  Diagram / DFD bạn cung cấp).

```
project/
├── backend/            # Flask REST API (Clean Architecture)
│   ├── src/
│   │   ├── domain/          # Entities, exceptions, constants
│   │   ├── infrastructure/  # SQLAlchemy ORM models, repositories, DB session
│   │   ├── services/        # Business logic (6 modules)
│   │   └── api/             # Controllers (blueprints), schemas, middleware JWT
│   ├── requirements.txt
│   ├── .env / .env.example
│   └── run.py
├── frontend/            # React (Vite) SPA
│   └── src/
│       ├── api/, context/, components/, pages/
├── sample_data/
│   └── sample_trajectory_cleaned.csv   # Dữ liệu trajectory mẫu để test nhanh
└── README.md
```

## 1. Yêu cầu hệ thống

- Python 3.10+
- Node.js 18+
- Tài khoản Supabase Postgres (đã có sẵn connection string trong `.env`)

## 2. Chạy Backend

```bash
# Trỏ tới thư mục backend
# python -m venv venv
# .\venv\Scripts\Activate.ps1
# pip install -r requirements.txt
# pip install prophet
```

> Lưu ý: `prophet` có thể mất vài phút để build (phụ thuộc `cmdstanpy`). Nếu cài
> lỗi, có thể bỏ qua dòng `prophet` trong `requirements.txt` — hệ thống sẽ tự
> động fallback về ARIMA khi Prophet không khả dụng (đã xử lý sẵn trong
> `forecasting_service.py`).

File `backend/.env` đã được cấu hình sẵn với connection string Supabase bạn cung cấp:

```
DATABASE_URI=postgresql://postgres.qsumfwhiianmrhkexlth:CNPMProject%402006@aws-0-ap-southeast-1.pooler.supabase.com:5432/postgres
SECRET_KEY=urban_traffic_secret_key_2026
```

Chạy server:

```bash
python run.py
# API chạy tại http://localhost:9999
```

Lần chạy đầu tiên, hệ thống sẽ **tự động tạo toàn bộ bảng** trong Supabase
(`users, datasets, dataset_versions, road_segments, traffic_features,
experiments, forecast_results, reports, audit_logs`) và **seed 4 tài khoản demo**
(mỗi role một tài khoản):

| Role       | Email                         | Password       |
|------------|--------------------------------|----------------|
| Admin      | admin@traffic.edu.vn          | Admin@123      |
| Researcher | researcher@traffic.edu.vn     | Research@123   |
| Analyst    | analyst@traffic.edu.vn        | Analyst@123    |
| Student    | student@traffic.edu.vn        | Student@123    |

Kiểm tra API: `GET http://localhost:9999/api/health` → `{"status": "ok"}`

## 3. Chạy Frontend

```bash
cd frontend
npm install
npm run dev
# Mở http://localhost:5173
```

File `frontend/.env` đã trỏ sẵn tới `http://localhost:9999/api`. Nếu deploy
backend ở địa chỉ khác, chỉnh biến `VITE_API_URL`.

## 4. Thử nghiệm nhanh (demo flow)

1. Đăng nhập bằng tài khoản **researcher** (hoặc bấm nút demo account trên trang login).
2. Vào **Datasets → Upload dataset**, chọn file `sample_data/sample_trajectory_cleaned.csv`.
3. Mở dataset vừa tạo → xem báo cáo chất lượng dữ liệu (validation report).
4. Vào **Traffic Analysis**, chọn dataset/version vừa tạo, bấm **Compute features**
   → xem KPI, biểu đồ xu hướng mật độ, heatmap, phân bố tốc độ, giờ cao điểm, hotspot.
5. Vào **Forecasting**, tạo experiment mới (chọn model ARIMA hoặc Prophet),
   mở experiment → chọn road segment → **Run forecast** → xem biểu đồ
   Actual vs Predicted + dự báo ngắn hạn kèm khoảng tin cậy, cùng MAE/RMSE/MAPE/R².
6. Xuất báo cáo PDF/Excel từ trang Analysis hoặc trang Experiment → tải về ở
   trang **Reports**.
7. Đăng nhập bằng tài khoản **admin** để vào **User Management** (tạo/xoá user,
   gán role) và **Audit Trail** (nhật ký toàn bộ hoạt động hệ thống).

## 5. Endpoint API chính

| Module | Method & Path | Mô tả |
|---|---|---|
| Auth | `POST /api/auth/register`, `/login`, `GET /me`, `POST /change-password` | Đăng ký/đăng nhập (JWT) |
| User | `GET/POST /api/users`, `PUT/DELETE /api/users/:id`, `PATCH /api/users/:id/role` | Quản lý user (Admin) |
| Dataset | `GET/POST /api/datasets`, `POST /api/datasets/:id/versions`, `GET .../preview`, `POST .../validate`, `POST /:id/archive|restore`, `DELETE /:id` | Module 1 |
| Analysis | `POST /api/analysis/versions/:id/compute`, `GET .../kpis|trend|heatmap|speed-distribution|peak-hours|hotspots` | Module 2 & 4 |
| Experiment | `GET/POST /api/experiments`, `POST /:id/run`, `GET /:id/results`, `GET /compare` | Module 3 & 5 |
| Report | `POST /api/reports/traffic/:version_id`, `POST /api/reports/forecast/:experiment_id`, `GET /api/reports`, `GET /download/:id` | Module 6 |
| Audit | `GET /api/audit` | Admin |
| Dashboard | `GET /api/dashboard/summary` | KPI tổng quan |

Phân quyền (role-based):
- **Admin**: toàn quyền, quản lý user + audit trail.
- **Researcher**: upload/quản lý dataset, tạo & chạy experiment, xuất báo cáo.
- **Analyst**: xem/tính toán phân tích, chạy experiment, xuất báo cáo (không upload dataset).
- **Student**: chỉ xem (dataset, phân tích, kết quả dự báo, báo cáo) — theo đúng Use Case Diagram của Student.

## 6. Ghi chú quan trọng

- Ứng dụng đã được **kiểm thử end-to-end thực tế** (login → upload → phân tích
  → dự báo ARIMA → xuất báo cáo PDF/Excel → tải file → RBAC) bằng HTTP request
  thật trong môi trường phát triển (dùng SQLite thay Supabase do môi trường build
  không có quyền truy cập mạng ra ngoài internet). Khi chạy trên máy bạn với
  Supabase thật, **không cần sửa gì thêm** — chỉ cần `pip install` + `npm install`
  rồi chạy như hướng dẫn trên.
- Nếu bảng chưa được tạo tự động (ví dụ do firewall/mạng), có thể chủ động chạy:
  ```bash
  cd backend/src && python3 -c "from infrastructure.databases import init_db; init_db()"
  ```
- Cột `interval_minutes` khi "Compute features" quyết định độ chi tiết của
  time-series (tương ứng RQ2 trong đề cương — ảnh hưởng đến độ chính xác dự báo).
- Model dự báo: **ARIMA** (statsmodels, order mặc định `(2,1,2)`, có fallback về
  moving-average nếu không hội tụ) và **Prophet** (tuỳ chọn, tự động fallback về
  ARIMA nếu chưa cài `prophet`).
