import base64
import io
import os

import cairosvg
import openpyxl
from barcode import generate
from barcode.writer import ImageWriter
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font
from openpyxl.utils import get_column_letter
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4, landscape
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.graphics import renderPDF

from PIL import Image

from svglib.svglib import svg2rlg, SvgRenderer

from app.models import WbOrderProductModel, WbOrderModel, WbSupplyModel

pdfmetrics.registerFont(TTFont('FreeSans', 'FreeSans.ttf'))


def create_wb_orders_qr_pdf(task_instance):
    supply = WbSupplyModel.objects.get(task=task_instance)
    qr_svgs = [str(elem.svg_file) for elem in WbOrderModel.objects.filter(supply=supply).all()]

    # Create a PDF buffer
    output_pdf = io.BytesIO()

    # Create a list to store individual QR code images
    qr_images = []

    for svg_string in qr_svgs:
        svg_data = base64.b64decode(svg_string)

        # Convert the SVG to PNG using cairosvg
        png_data = cairosvg.svg2png(bytestring=svg_data,
                                    output_width=1000,
                                    output_height=800,
                                    background_color="white")
        # Convert the SVG data to a PNG with the specified width and height
        png_image = Image.open(io.BytesIO(png_data))
        qr_images.append(png_image)

    # Create a PDF using ReportLab
    c = canvas.Canvas(output_pdf, pagesize=landscape(letter))
    for image in qr_images:
        c.drawInlineImage(image, 0, 0, landscape(letter)[0], landscape(letter)[1])
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
    png_data = cairosvg.svg2png(bytestring=svg_data,
                                output_width=1000,
                                output_height=800,
                                background_color="white")
    # Convert the SVG data to a PNG with the specified width and height
    png_image = Image.open(io.BytesIO(png_data))
    c = canvas.Canvas(output_pdf, pagesize=landscape(letter))
    c.drawInlineImage(png_image, 0, 0, landscape(letter)[0], landscape(letter)[1])
    c.showPage()
    c.save()

    # Reset the buffer position to the beginning
    output_pdf.seek(0)

    return output_pdf


def create_stickers_document(task_instance):

    supply = WbSupplyModel.objects.get(task=task_instance)
    task_barcodes = [
        int(elem.wb_skus.strip('[]').split(',')[0]) for elem in WbOrderModel.objects.filter(supply=supply).all()
    ]
    output_pdf = io.BytesIO()
    c = canvas.Canvas(output_pdf, pagesize=landscape(letter))

    for number in task_barcodes:
        # Generate barcode image
        img_buffer = io.BytesIO()
        generate('Code128', str(number), writer=ImageWriter(), output=img_buffer)
        img_buffer.seek(0)  # Reset the buffer position
        # Convert the barcode data from BytesIO to a ReportLab Image object
        png_image = Image.open(img_buffer)

        # Draw the barcode on the PDF
        c.drawInlineImage(png_image, 0, 0, landscape(letter)[0], landscape(letter)[1])
        c.showPage()
    c.save()
    output_pdf.seek(0)  # Reset the buffer position to the beginning

    return output_pdf
