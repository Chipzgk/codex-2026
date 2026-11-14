# Mobile Context

## Mục tiêu

Thư mục này chứa ứng dụng mobile Flutter của dự án `codex-2026`.

## Khởi tạo dự án

Yêu cầu Flutter SDK stable mới nhất và Dart SDK đi kèm. Từ thư mục gốc repository, chạy:

```powershell
flutter create --platforms=android,ios mobile
```

Sau khi khởi tạo, cập nhật các package lên phiên bản tương thích mới nhất bằng:

```powershell
Set-Location mobile
flutter pub upgrade --major-versions
flutter pub get
```

Kiểm tra môi trường và chạy ứng dụng:

```powershell
flutter doctor
flutter run
```

## Quy ước

- Dùng Flutter stable và Dart SDK do Flutter stable cung cấp.
- Chỉ thêm dependency khi có nhu cầu rõ ràng; ưu tiên package được duy trì tốt trên pub.dev.
- Chạy `dart format .` và `flutter analyze` trước khi commit.
- Không commit các thư mục build, file secrets hoặc thông tin ký ứng dụng.

## Trạng thái hiện tại

Flutter CLI chưa được phát hiện trong `PATH` tại thời điểm tạo file này. Cần cài Flutter SDK stable mới nhất và thêm thư mục `bin` vào `PATH`, sau đó chạy các lệnh khởi tạo ở trên.
