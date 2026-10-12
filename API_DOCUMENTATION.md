# GymPath API Documentation

**Version:** 1.0.0  
**Base URL:** `https://<your-domain>/api/v1`  
**Interactive Docs (Swagger):** `https://<your-domain>/api/docs/`

---

## Tổng quan luồng người dùng

Dưới đây là các luồng sử dụng chính của app. Đọc phần này trước để hình dung toàn bộ hành trình của user trước khi đi vào chi tiết từng API.

---

### Luồng 1 — Lần đầu sử dụng app

```
Mở app lần đầu
      │
      ├─ Chưa có tài khoản ──► POST /auth/register/
      │                               │
      │                               ▼
      └─ Đã có tài khoản ───► POST /auth/login/
                                      │
                                      ▼
                             Nhận access_token + refresh_token
                                      │
                                      ▼
                             Lưu token vào storage
                                      │
                                      ▼
                   POST /notifications/device-token/  ← Đăng ký FCM token
                                      │
                                      ▼
                             Vào màn hình chính
```

---

### Luồng 2 — Quản lý phiên đăng nhập (Token lifecycle)

```
Gửi request với access_token
        │
        ├─ HTTP 200 ──► Bình thường, tiếp tục
        │
        └─ HTTP 401 ──► access_token hết hạn
                              │
                              ▼
                   POST /auth/refresh/  { refresh: <token> }
                              │
                   ┌──────────┴──────────┐
                 200 OK              401 Unauthorized
                   │                     │
                   ▼                     ▼
         Lưu token mới             Refresh hết hạn
         Retry request             → Đưa user về màn hình login
```

> Token được tự động rotate sau mỗi lần refresh. Luôn lưu lại cả `access` và `refresh` mới nhận được.

---

### Luồng 3 — Lập kế hoạch tập với Lộ trình (Roadmap)

Dùng khi user muốn đặt mục tiêu dài hạn và chia thành các giai đoạn nhỏ.

```
POST /roadmaps/                     ← Tạo lộ trình (ví dụ: Giảm 10kg / 3 tháng)
        │
        ▼
POST /roadmaps/{id}/phases/         ← Thêm giai đoạn 1 (Tuần 1-4: Làm quen)
POST /roadmaps/{id}/phases/         ← Thêm giai đoạn 2 (Tuần 5-8: Tăng cường độ)
POST /roadmaps/{id}/phases/         ← Thêm giai đoạn 3 (Tuần 9-12: Duy trì)
        │
        ▼
GET /roadmaps/{id}/                 ← Xem tiến độ (phases lồng trong response)
        │
        ▼
        ... (user tập luyện theo từng giai đoạn) ...
        │
        ▼
PATCH /roadmaps/{id}/phases/{id}/   ← { "is_completed": true }
        │                              ↳ Server tự gửi FCM "🏆 Hoàn thành giai đoạn!"
        ▼
PATCH /roadmaps/{id}/               ← { "is_active": false } khi hoàn thành toàn bộ
```

---

### Luồng 4 — Lên lịch và ghi nhật ký một buổi tập

Luồng hàng ngày của user.

```
POST /schedules/                    ← Lên lịch tập (ví dụ: Thứ 2, 6h-7h30, Tập ngực)
        │
        ▼
        ... đến giờ tập ...
        │
        ▼  [Server tự động – không cần gọi API]
        ├─► Cron nhắc trước 30 phút: FCM "⏰ Sắp đến giờ tập!"
        │
        ▼
        ... user tập xong ...
        │
        ▼
PATCH /schedules/{id}/              ← { "is_completed": true }
        │                              ↳ Server tự gửi FCM "📝 Ghi lại buổi tập nào!"
        ▼
POST /journals/                     ← Ghi nhật ký kèm danh sách bài tập
        │   {
        │     "date": "2026-09-30",
        │     "title": "Tập ngực sáng nay",
        │     "duration_minutes": 75,
        │     "mood": 4,
        │     "schedule": <schedule_id>,   ← Liên kết với lịch tập
        │     "exercises": [
        │       { "name": "Bench Press", "sets": 4, "reps": 10, "weight_kg": 80 },
        │       { "name": "Push Up", "sets": 3, "reps": 20 }
        │     ]
        │   }
        ▼
GET /journals/?month=2026-09        ← Xem lại toàn bộ nhật ký trong tháng
```

---

### Luồng 5 — Đăng xuất

```
User bấm Đăng xuất
        │
        ▼
DELETE /notifications/device-token/   ← Huỷ FCM token (không nhận noti nữa)
        │
        ▼
POST /auth/logout/                    ← Blacklist refresh token
        │
        ▼
Xoá token khỏi storage, về màn hình login
```

> Nếu bỏ qua bước DELETE device-token, user vẫn sẽ nhận push notification dù đã đăng xuất.

---

### Sơ đồ quan hệ dữ liệu

```
User
 ├── Schedule (Lịch tập)          1 user — nhiều lịch tập
 │       └── Journal (Nhật ký)    1 lịch tập — tối đa 1 nhật ký liên kết
 │               └── Exercise     1 nhật ký — nhiều bài tập
 ├── Journal (Nhật ký)            1 user — nhiều nhật ký (có thể không liên kết Schedule)
 ├── Roadmap (Lộ trình)           1 user — nhiều lộ trình
 │       └── Phase (Giai đoạn)    1 lộ trình — nhiều giai đoạn
 └── DeviceToken                  1 user — nhiều thiết bị
```

---

## Mục lục

1. [Xác thực & Phân quyền](#1-xác-thực--phân-quyền)
2. [Auth – Tài khoản](#2-auth--tài-khoản)
3. [Schedule – Lịch tập](#3-schedule--lịch-tập)
4. [Roadmap – Lộ trình](#4-roadmap--lộ-trình)
5. [Journal – Nhật ký tập](#5-journal--nhật-ký-tập)
6. [Notifications – Đẩy thông báo](#6-notifications--đẩy-thông-báo)
7. [Cấu trúc lỗi chung](#7-cấu-trúc-lỗi-chung)
8. [Phân trang](#8-phân-trang)

---

## 1. Xác thực & Phân quyền

API sử dụng **JWT (JSON Web Token)** theo chuẩn Bearer.

### Cách đính kèm token

Tất cả các endpoint (trừ `register` và `login`) đều yêu cầu header:

```
Authorization: Bearer <access_token>
```

### Cơ chế token

| Token | Thời hạn mặc định | Mục đích |
|---|---|---|
| `access_token` | 60 phút | Dùng cho mọi request |
| `refresh_token` | 7 ngày | Lấy `access_token` mới khi hết hạn |

**Luồng làm mới token:**

```
access_token hết hạn (HTTP 401)
        │
        ▼
POST /auth/refresh/  { "refresh": "<refresh_token>" }
        │
        ▼
Response: access_token mới + refresh_token mới
refresh_token cũ bị vô hiệu hoá ngay lập tức
        │
        ▼
Lưu cả hai token mới, tiếp tục request
```

> **Lưu ý:** Mỗi lần gọi `/refresh/` sẽ cấp ra cặp token hoàn toàn mới. Refresh token cũ không dùng được nữa. App cần lưu lại cả hai token sau mỗi lần refresh.

---

## 2. Auth – Tài khoản

### POST `/auth/register/`

Đăng ký tài khoản mới.

**Không cần xác thực.**

**Request body:**

```json
{
  "username": "nguyenvana",
  "password": "StrongPass123!",
  "password_confirm": "StrongPass123!",
  "email": "vana@example.com",
  "first_name": "Văn A",
  "last_name": "Nguyễn"
}
```

| Field | Bắt buộc | Ghi chú |
|---|---|---|
| `username` | Có | Duy nhất trong hệ thống |
| `password` | Có | Tối thiểu 8 ký tự, không quá đơn giản |
| `password_confirm` | Có | Phải trùng với `password` |
| `email` | Không | |
| `first_name`, `last_name` | Không | |

**Response `201`:**

```json
{
  "id": 5,
  "username": "nguyenvana",
  "email": "vana@example.com",
  "first_name": "Văn A",
  "last_name": "Nguyễn"
}
```

---

### POST `/auth/login/`

Đăng nhập, nhận JWT token.

**Không cần xác thực.**

**Request body:**

```json
{
  "username": "nguyenvana",
  "password": "StrongPass123!"
}
```

**Response `200`:**

```json
{
  "access": "<access_token>",
  "refresh": "<refresh_token>",
  "user": {
    "id": 5,
    "username": "nguyenvana",
    "email": "vana@example.com",
    "first_name": "Văn A",
    "last_name": "Nguyễn",
    "full_name": "Nguyễn Văn A"
  }
}
```

---

### POST `/auth/refresh/`

Làm mới access token bằng refresh token còn hạn.

**Không cần xác thực.**

**Request body:**

```json
{
  "refresh": "<refresh_token>"
}
```

**Response `200`:**

```json
{
  "access": "<access_token_mới>",
  "refresh": "<refresh_token_mới>"
}
```

---

### POST `/auth/logout/`

Đăng xuất – vô hiệu hoá refresh token.

**Cần xác thực.**

**Request body:**

```json
{
  "refresh": "<refresh_token>"
}
```

**Response `204` (No Content).**

---

### GET `/auth/me/`

Lấy thông tin profile của user đang đăng nhập.

**Cần xác thực.**

**Response `200`:**

```json
{
  "id": 5,
  "username": "nguyenvana",
  "email": "vana@example.com",
  "first_name": "Văn A",
  "last_name": "Nguyễn",
  "phone": "0901234567",
  "date_of_birth": "1995-06-15",
  "height_cm": 175,
  "weight_kg": 70.5,
  "bio": "Đang tập để giảm cân.",
  "date_joined": "2026-09-01T08:00:00+07:00"
}
```

---

### PATCH `/auth/me/`

Cập nhật thông tin profile. Chỉ gửi các field cần thay đổi.

**Cần xác thực.**

**Request body (ví dụ cập nhật cân nặng):**

```json
{
  "weight_kg": 69.0
}
```

**Response `200`:** Trả về toàn bộ profile sau khi cập nhật.

> **Không cho phép** đổi `username` qua endpoint này. Đổi mật khẩu dùng `/change-password/`.

---

### POST `/auth/change-password/`

Đổi mật khẩu.

**Cần xác thực.**

**Request body:**

```json
{
  "old_password": "StrongPass123!",
  "new_password": "NewPass456!",
  "new_password_confirm": "NewPass456!"
}
```

**Response `200`:**

```json
{
  "detail": "Đổi mật khẩu thành công"
}
```

---

## 3. Schedule – Lịch tập

Mỗi lịch tập đại diện cho một buổi tập của user vào một ngày và khung giờ cụ thể.

### Cấu trúc đối tượng Schedule

```json
{
  "id": 1,
  "user": "nguyenvana",
  "title": "Tập ngực buổi sáng",
  "description": "Bench press, push up, cable fly",
  "date": "2026-09-30",
  "start_time": "06:00:00",
  "end_time": "07:30:00",
  "difficulty": "medium",
  "is_completed": false,
  "notes": "Tăng tạ bench press lên 5kg",
  "created_at": "2026-09-28T10:00:00+07:00",
  "updated_at": "2026-09-28T10:00:00+07:00"
}
```

| Field | Kiểu | Giá trị hợp lệ |
|---|---|---|
| `difficulty` | string | `"easy"`, `"medium"`, `"hard"` |
| `is_completed` | boolean | `true`, `false` |
| `date` | string | `"YYYY-MM-DD"` |
| `start_time`, `end_time` | string | `"HH:MM:SS"` – `end_time` phải sau `start_time` |

---

### GET `/schedules/`

Lấy danh sách lịch tập của user.

**Query params:**

| Param | Kiểu | Ví dụ | Mô tả |
|---|---|---|---|
| `date` | string | `?date=2026-09-30` | Lọc theo ngày cụ thể |
| `is_completed` | boolean | `?is_completed=false` | Lọc theo trạng thái |

**Response `200`:** Mảng các Schedule (có phân trang).

---

### POST `/schedules/`

Tạo lịch tập mới.

**Request body:**

```json
{
  "title": "Tập chân buổi chiều",
  "date": "2026-10-01",
  "start_time": "17:00:00",
  "end_time": "18:30:00",
  "difficulty": "hard",
  "description": "Squat, leg press, lunge",
  "notes": ""
}
```

**Response `201`:** Schedule vừa tạo.

---

### GET `/schedules/{id}/`

Lấy chi tiết một lịch tập.

**Response `200`:** Schedule object.  
**Response `404`:** Không tìm thấy hoặc không phải của user.

---

### PATCH `/schedules/{id}/`

Cập nhật một phần lịch tập. Thường dùng để đánh dấu hoàn thành.

**Request body (ví dụ đánh dấu hoàn thành):**

```json
{
  "is_completed": true
}
```

**Response `200`:** Schedule sau khi cập nhật.

> **Lưu ý FCM:** Khi `is_completed` thay đổi từ `false` → `true`, server tự động gửi push notification "📝 Ghi lại buổi tập nào!" đến thiết bị của user.

---

### PUT `/schedules/{id}/`

Cập nhật toàn bộ lịch tập (cần gửi đầy đủ tất cả field).

---

### DELETE `/schedules/{id}/`

Xoá lịch tập.

**Response `204`.**

---

## 4. Roadmap – Lộ trình

Lộ trình là kế hoạch tập luyện dài hạn, chia thành nhiều giai đoạn (Phase).

### Cấu trúc đối tượng Roadmap

```json
{
  "id": 1,
  "user": "nguyenvana",
  "title": "Giảm 10kg trong 3 tháng",
  "description": "Kết hợp cardio và gym 5 buổi/tuần",
  "goal": "weight_loss",
  "start_date": "2026-10-01",
  "end_date": "2026-12-31",
  "is_active": true,
  "phases": [...],
  "created_at": "2026-09-28T10:00:00+07:00",
  "updated_at": "2026-09-28T10:00:00+07:00"
}
```

| Field `goal` | Ý nghĩa |
|---|---|
| `weight_loss` | Giảm cân |
| `muscle_gain` | Tăng cơ |
| `endurance` | Tăng sức bền |
| `flexibility` | Tăng linh hoạt |
| `general` | Tổng quát |

---

### GET `/roadmaps/`

Lấy danh sách lộ trình. Response bao gồm **toàn bộ phases** lồng bên trong.

**Query params:**

| Param | Ví dụ | Mô tả |
|---|---|---|
| `is_active` | `?is_active=true` | Chỉ lấy lộ trình đang thực hiện |

---

### POST `/roadmaps/`

Tạo lộ trình mới. Phases được tạo riêng sau qua endpoint phases.

**Request body:**

```json
{
  "title": "Tăng cơ mùa đông 2026",
  "goal": "muscle_gain",
  "start_date": "2026-10-01",
  "end_date": "2027-01-31",
  "description": "Bulking cycle với chế độ ăn tăng calo"
}
```

**Response `201`:** Roadmap vừa tạo (phases = []).

---

### GET `/roadmaps/{id}/`

Chi tiết lộ trình kèm toàn bộ phases.

---

### PATCH `/roadmaps/{id}/`

Cập nhật một phần lộ trình. Thường dùng để kết thúc lộ trình.

**Request body (ví dụ kết thúc lộ trình):**

```json
{
  "is_active": false
}
```

---

### DELETE `/roadmaps/{id}/`

Xoá lộ trình và toàn bộ phases thuộc lộ trình đó.

**Response `204`.**

---

### Cấu trúc đối tượng Phase

```json
{
  "id": 3,
  "title": "Giai đoạn 1 – Quen vận động",
  "description": "Làm quen với khối lượng tập, tần suất 3 buổi/tuần",
  "order": 1,
  "start_date": "2026-10-01",
  "end_date": "2026-10-31",
  "is_completed": false
}
```

---

### GET `/roadmaps/{roadmap_id}/phases/`

Lấy danh sách tất cả phases của một lộ trình, sắp xếp theo `order`.

---

### POST `/roadmaps/{roadmap_id}/phases/`

Thêm một giai đoạn mới vào lộ trình.

**Request body:**

```json
{
  "title": "Giai đoạn 2 – Tăng cường độ",
  "order": 2,
  "start_date": "2026-11-01",
  "end_date": "2026-11-30",
  "description": "Tăng tần suất lên 5 buổi/tuần"
}
```

**Response `201`:** Phase vừa tạo.

---

### PATCH `/roadmaps/{roadmap_id}/phases/{id}/`

Cập nhật một phần phase. Thường dùng để đánh dấu hoàn thành.

**Request body:**

```json
{
  "is_completed": true
}
```

**Response `200`:** Phase sau khi cập nhật.

> **Lưu ý FCM:** Khi `is_completed` thay đổi từ `false` → `true`, server tự động gửi push notification "🏆 Hoàn thành giai đoạn!" đến thiết bị của user.

---

### DELETE `/roadmaps/{roadmap_id}/phases/{id}/`

Xoá một phase. Các phase khác không bị ảnh hưởng.

**Response `204`.**

---

## 5. Journal – Nhật ký tập

Nhật ký ghi lại chi tiết một buổi tập đã diễn ra, bao gồm danh sách bài tập (exercises).

### Cấu trúc đối tượng Journal

```json
{
  "id": 1,
  "user": "nguyenvana",
  "date": "2026-09-30",
  "title": "Tập ngực sáng nay",
  "notes": "Cảm thấy mạnh hơn tuần trước",
  "duration_minutes": 75,
  "mood": 4,
  "calories_burned": 450,
  "schedule": 12,
  "exercises": [...],
  "created_at": "2026-09-30T08:45:00+07:00",
  "updated_at": "2026-09-30T08:45:00+07:00"
}
```

| Field | Ghi chú |
|---|---|
| `mood` | Số nguyên từ 1 (rất tệ) đến 5 (xuất sắc) |
| `schedule` | ID của lịch tập liên kết (có thể null) |
| `exercises` | Danh sách bài tập lồng trong nhật ký |

---

### GET `/journals/`

Lấy danh sách nhật ký. Mỗi nhật ký bao gồm toàn bộ exercises.

**Query params:**

| Param | Ví dụ | Mô tả |
|---|---|---|
| `date` | `?date=2026-09-30` | Lọc theo ngày cụ thể |
| `month` | `?month=2026-09` | Lọc theo tháng (định dạng YYYY-MM) |
| `mood` | `?mood=5` | Lọc theo mood |

---

### POST `/journals/`

Tạo nhật ký mới. Có thể gửi kèm danh sách exercises trong cùng một request.

**Request body:**

```json
{
  "date": "2026-09-30",
  "title": "Tập ngực buổi sáng",
  "duration_minutes": 75,
  "mood": 4,
  "calories_burned": 450,
  "notes": "Tăng được 5kg bench press",
  "schedule": 12,
  "exercises": [
    {
      "name": "Bench Press",
      "sets": 4,
      "reps": 10,
      "weight_kg": 80.0
    },
    {
      "name": "Push Up",
      "sets": 3,
      "reps": 20
    },
    {
      "name": "Plank",
      "duration_seconds": 60
    }
  ]
}
```

> **Quy tắc exercises:** Mỗi bài tập phải có ít nhất một trong `sets`, `reps`, hoặc `duration_seconds`. `weight_kg` phải ≥ 0 nếu có.

**Response `201`:** Journal đầy đủ kèm exercises vừa tạo.

---

### GET `/journals/{id}/`

Chi tiết nhật ký kèm toàn bộ exercises.

---

### PATCH `/journals/{id}/`

Cập nhật một phần nhật ký. Nếu gửi kèm `exercises`, **toàn bộ exercises cũ sẽ bị thay thế** bằng danh sách mới.

**Request body (ví dụ chỉ cập nhật mood):**

```json
{
  "mood": 5
}
```

---

### PUT `/journals/{id}/`

Cập nhật toàn bộ nhật ký, bao gồm cả thay thế exercises.

---

### DELETE `/journals/{id}/`

Xoá nhật ký và toàn bộ exercises thuộc nhật ký đó.

**Response `204`.**

---

### Cấu trúc đối tượng Exercise

```json
{
  "id": 7,
  "name": "Bench Press",
  "sets": 4,
  "reps": 10,
  "weight_kg": 80.0,
  "duration_seconds": null,
  "notes": "Paused reps"
}
```

---

### GET `/journals/{journal_id}/exercises/`

Lấy danh sách tất cả bài tập trong một nhật ký.

---

### POST `/journals/{journal_id}/exercises/`

Thêm một bài tập vào nhật ký đã có.

**Request body:**

```json
{
  "name": "Cable Fly",
  "sets": 3,
  "reps": 15,
  "weight_kg": 15.0
}
```

---

### GET `/journals/{journal_id}/exercises/{id}/`

Chi tiết một bài tập.

---

### PATCH `/journals/{journal_id}/exercises/{id}/`

Cập nhật một phần bài tập.

---

### DELETE `/journals/{journal_id}/exercises/{id}/`

Xoá một bài tập khỏi nhật ký.

**Response `204`.**

---

## 6. Notifications – Đẩy thông báo

### Điều kiện nhận push notification

App phải đăng ký FCM device token với server. Server không tự tìm token — nếu không có token đã đăng ký, mọi notification đều bị bỏ qua.

---

### POST `/notifications/device-token/`

Đăng ký FCM token của thiết bị. Gọi ngay sau khi app khởi động hoặc khi Firebase SDK cấp token mới.

**Cần xác thực.**

**Request body:**

```json
{
  "token": "<FCM registration token từ Firebase SDK>",
  "platform": "android"
}
```

| Field | Giá trị hợp lệ |
|---|---|
| `platform` | `"android"`, `"ios"` |

**Response `201`:**

```json
{
  "id": 3,
  "token": "<FCM token>",
  "platform": "android",
  "created_at": "2026-09-30T09:00:00+07:00"
}
```

> Token đã tồn tại → cập nhật lại thay vì tạo mới (upsert). Không lo bị trùng.

---

### DELETE `/notifications/device-token/`

Huỷ kích hoạt token khi user đăng xuất. Token bị đánh dấu `is_active=false`, server không gửi notification đến thiết bị đó nữa.

**Cần xác thực.**

**Request body:**

```json
{
  "token": "<FCM token cần huỷ>"
}
```

**Response `204`.**

---

### Các loại push notification server tự gửi

Server tự bắn notification khi có sự kiện — app không cần gọi API nào thêm.

| Sự kiện | Kích hoạt bởi | Tiêu đề | `data.type` |
|---|---|---|---|
| Đánh dấu lịch tập hoàn thành | `PATCH /schedules/{id}/` với `is_completed: true` | "📝 Ghi lại buổi tập nào!" | `journal_prompt` |
| Đánh dấu giai đoạn hoàn thành | `PATCH /roadmaps/{roadmap_id}/phases/{id}/` với `is_completed: true` | "🏆 Hoàn thành giai đoạn!" | `phase_completed` |
| Nhắc lịch tập sắp bắt đầu | Cron server tự chạy mỗi 15 phút | "⏰ Sắp đến giờ tập!" | `schedule_reminder` |

**Cấu trúc data payload của notification:**

```json
// journal_prompt
{
  "type": "journal_prompt",
  "schedule_id": "12"
}

// phase_completed
{
  "type": "phase_completed",
  "roadmap_id": "3",
  "phase_id": "7"
}

// schedule_reminder
{
  "type": "schedule_reminder",
  "schedule_id": "12"
}
```

App có thể dùng `data.type` để điều hướng đến màn hình phù hợp khi user nhấn vào notification.

---

## 7. Cấu trúc lỗi chung

Mọi lỗi validation đều trả về HTTP `400` với cấu trúc:

```json
{
  "field_name": ["Thông báo lỗi cụ thể."]
}
```

Hoặc lỗi không gắn với field cụ thể:

```json
{
  "detail": "Thông báo lỗi."
}
```

| HTTP Status | Ý nghĩa |
|---|---|
| `400 Bad Request` | Dữ liệu đầu vào không hợp lệ |
| `401 Unauthorized` | Thiếu token hoặc token hết hạn |
| `403 Forbidden` | Không có quyền truy cập tài nguyên |
| `404 Not Found` | Không tìm thấy hoặc không phải của user |
| `201 Created` | Tạo mới thành công |
| `204 No Content` | Xoá thành công |

---

## 8. Phân trang

Các endpoint trả về danh sách đều có phân trang mặc định **20 items/trang**.

**Response structure:**

```json
{
  "count": 45,
  "next": "https://<domain>/api/v1/schedules/?page=2",
  "previous": null,
  "results": [...]
}
```

**Query param:**

```
GET /schedules/?page=2
```
