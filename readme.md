# Real-Time Barcode Scanner (Modular Demo)

## Mô tả

Dự án này là một ứng dụng quét mã vạch (barcode) thời gian thực sử dụng webcam. Nó được xây dựng bằng Python, OpenCV để xử lý hình ảnh và video, và thư viện Pyzbar để phát hiện và giải mã mã vạch. Mã nguồn được cấu trúc theo dạng module để dễ dàng quản lý, bảo trì và mở rộng.

## Tính năng

*   Quét mã vạch từ luồng video webcam thời gian thực.
*   Phát hiện và giải mã nhiều loại mã vạch 1D và 2D (được hỗ trợ bởi ZBar).
*   Vẽ hộp bao quanh các mã vạch được phát hiện trên khung hình video.
*   Hiển thị dữ liệu và loại mã vạch được giải mã.
*   Hiển thị số khung hình trên giây (FPS) để đánh giá hiệu năng.
*   Cấu trúc code dạng module rõ ràng (`config`, `camera`, `processor`, `display`).

## Công nghệ sử dụng

*   **Python 3.x**
*   **OpenCV (`opencv-python`)**: Thư viện xử lý ảnh và thị giác máy tính. Dùng để đọc video từ camera và hiển thị kết quả.
*   **Pyzbar (`pyzbar`)**: Thư viện Python wrapper cho ZBar barcode reader. Dùng để phát hiện và giải mã mã vạch.

## Cấu trúc thư mục