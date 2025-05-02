import cv2
import config # Lay cac cau hinh ve mau sac, font,...

FONT = cv2.FONT_HERSHEY_SIMPLEX


def draw_single_barcode(frame, barcode_info):
    """Ve hop bao va text cho mot barcode."""
    (x, y, w, h) = barcode_info['rect']
    data = barcode_info['data']
    type = barcode_info['type']

    # Ve hop bao
    cv2.rectangle(frame, (x, y), (x + w, y + h), config.BOX_COLOR, config.BOX_THICKNESS)

    # Ve text
    text = f"{data} ({type})"
    # Tinh toan vi tri text phia tren hop bao
    text_y = y - 10 if y - 10 > 10 else y + h + 20 # Tranh ve ra ngoai mep tren
    cv2.putText(frame, text, (x, text_y), FONT, config.FONT_SCALE,
                config.TEXT_COLOR, config.TEXT_THICKNESS)

def draw_all_barcodes(frame, barcodes_list):
    """Ve tat ca cac barcode trong danh sach len frame."""
    for bc_info in barcodes_list:
        draw_single_barcode(frame, bc_info)

def draw_fps(frame, fps_value):
    """Ve gia tri FPS len frame."""
    if config.SHOW_FPS:
        fps_text = f"FPS: {fps_value:.2f}"
        cv2.putText(frame, fps_text, (10, 30), FONT, 0.7,
                    config.FPS_COLOR, 2) # Tang kich thuoc FPS