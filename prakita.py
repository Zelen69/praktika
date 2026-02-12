from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from io import BytesIO
from datetime import datetime
import PyPDF2


def create_stamp_page(user_data, page_size=A4):
    """Создает страницу PDF со штампом"""
    packet = BytesIO()
    can = canvas.Canvas(packet, pagesize=page_size)

    # Настройки шрифта
    try:
        pdfmetrics.registerFont(TTFont('Arial', 'arial.ttf'))
        can.setFont("Arial", 9)
    except:
        can.setFont("Helvetica", 9)

    # Координаты и размеры рамки
    x, y = 130 * mm, 10 * mm
    width, height = 75 * mm, 30 * mm

    current_time = datetime.now().strftime("%d.%m.%Y г. в %H:%M")

    lines = [
        "Подписано простой электронной подписью",
        f"Подписант: {user_data.get('name', '')}",
        f"Время подписания: {current_time}",
        f"Цифровой отпечаток подписи:",
        user_data.get('signature_hash', '')
    ]

    # Рамка
    can.setStrokeColorRGB(0, 0, 80)
    can.setLineWidth(0.5)
    can.rect(x, y, width, height, stroke=1, fill=0)

    # Текст
    can.setFillColorRGB(0, 0, 80)
    text_x = x + 2 * mm
    text_y = y + height - 4 * mm

    for i, line in enumerate(lines):
        can.drawString(text_x, text_y - i * 4 * mm, line)

    can.save()
    packet.seek(0)
    return packet


def add_signature_stamp(input_pdf_path, output_pdf_path, user_data,
                        all_pages=True, page_number=None):
    """
    Добавляет штамп с электронной подписью в PDF

    Args:
        input_pdf_path: путь к исходному PDF
        output_pdf_path: путь для сохранения результата
        user_data: словарь с данными пользователя
        all_pages: если True - добавить на все страницы
        page_number: номер страницы для штампа (начинается с 0)
    """

    existing_pdf = PyPDF2.PdfReader(open(input_pdf_path, "rb"))
    output = PyPDF2.PdfWriter()

    if page_number is not None:
        pages_to_stamp = [page_number]
    elif all_pages:
        pages_to_stamp = list(range(len(existing_pdf.pages)))
    else:
        pages_to_stamp = [0]

    for page_num in range(len(existing_pdf.pages)):
        page = existing_pdf.pages[page_num]

        if page_num in pages_to_stamp:
            page_width = float(page.mediabox.width)
            page_height = float(page.mediabox.height)

            packet = create_stamp_page(
                user_data,
                page_size=(page_width, page_height)
            )
            stamp_pdf = PyPDF2.PdfReader(packet)
            stamp_page = stamp_pdf.pages[0]

            page.merge_page(stamp_page)

        output.add_page(page)

    with open(output_pdf_path, "wb") as output_stream:
        output.write(output_stream)


if __name__ == "__main__":
    user_data = {
        "name": "Иванов Иван Иванович",
        "signature_hash": "kfkasdhfjaksdhjf1234567890abcdef"
    }

    add_signature_stamp(
        input_pdf_path="input.pdf",
        output_pdf_path="output.pdf",
        user_data=user_data,
        all_pages=False
    )
