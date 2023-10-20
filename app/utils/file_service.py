import base64
import io
import re

import cairosvg
from barcode import generate
from barcode.writer import ImageWriter

from reportlab.lib.pagesizes import landscape
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

from PIL import Image

from app.models import WbOrderModel, WbSupplyModel

pdfmetrics.registerFont(TTFont("FreeSans", "FreeSans.ttf"))
custom_pagesize = (58 * mm, 40 * mm)


def create_wb_orders_qr_pdf(task_instance):
    supply = WbSupplyModel.objects.get(task=task_instance)
    qr_svgs = [
        str(elem.svg_file) for elem in WbOrderModel.objects.filter(supply=supply).all()
    ]

    # Create a PDF buffer
    output_pdf = io.BytesIO()

    # Create a list to store individual QR code images
    qr_images = []

    for svg_string in qr_svgs:
        svg_data = base64.b64decode(svg_string)

        svg_content = svg_data.decode("utf-8")
        svg_content = re.sub(r"font-size:125pt", "font-size:90pt", svg_content)
        svg_content = re.sub(r"font-size:45pt", "font-size:30pt", svg_content)

        # Convert the SVG to PNG using cairosvg
        png_data = cairosvg.svg2png(
            bytestring=svg_content.encode(encoding="utf-8"),
            output_width=580,
            output_height=400,
            background_color="white",
        )
        # Convert the SVG data to a PNG with the specified width and height
        png_image = Image.open(io.BytesIO(png_data))
        qr_images.append(png_image)

    # Create a PDF using ReportLab

    c = canvas.Canvas(output_pdf, pagesize=landscape(custom_pagesize))
    for image in qr_images:
        c.drawInlineImage(
            image, 0, 0, landscape(custom_pagesize)[0], landscape(custom_pagesize)[1]
        )
        c.showPage()
    c.save()

    # Reset the buffer position to the beginning
    output_pdf.seek(0)

    return output_pdf


def create_wb_supply_qr_pdf(task_instance):
    supply = WbSupplyModel.objects.get(task=task_instance)
    output_pdf = io.BytesIO()
    svg_data = base64.b64decode(supply.svg_file)

    # Convert the SVG to PNG using cairosvg
    png_data = cairosvg.svg2png(
        bytestring=svg_data,
        output_width=1000,
        output_height=800,
        background_color="white",
    )
    # Convert the SVG data to a PNG with the specified width and height
    png_image = Image.open(io.BytesIO(png_data))
    c = canvas.Canvas(output_pdf, pagesize=landscape(custom_pagesize))
    c.drawInlineImage(
        png_image, 0, 0, landscape(custom_pagesize)[0], landscape(custom_pagesize)[1]
    )
    c.showPage()
    c.save()

    # Reset the buffer position to the beginning
    output_pdf.seek(0)

    return output_pdf


def create_stickers_pdf(task_instance):
    supply = WbSupplyModel.objects.get(task=task_instance)
    task_barcodes = [
        int(elem.wb_skus.strip("[]").split(",")[0])
        for elem in WbOrderModel.objects.filter(supply=supply).all()
    ]
    output_pdf = io.BytesIO()
    c = canvas.Canvas(output_pdf, pagesize=landscape(custom_pagesize))

    for number in task_barcodes:
        # Generate barcode image
        img_buffer = io.BytesIO()
        generate("Code128", str(number), writer=ImageWriter(), output=img_buffer)
        img_buffer.seek(0)  # Reset the buffer position
        # Convert the barcode data from BytesIO to a ReportLab Image object
        png_image = Image.open(img_buffer)

        # Draw the barcode on the PDF
        c.drawInlineImage(
            png_image,
            0,
            0,
            landscape(custom_pagesize)[0],
            landscape(custom_pagesize)[1],
        )
        c.showPage()
    c.save()
    output_pdf.seek(0)  # Reset the buffer position to the beginning

    return output_pdf
