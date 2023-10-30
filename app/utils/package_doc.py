import io
import re

import weasyprint

from app.models import WbOrderModel, WbOrderProductModel


def create_package_doc(task_instance, supply_instance):
    row_headers = (
        "Номер заказа",
        "Наименование товара",
        "Комплект",
        "Класс упаковки",
        "Штрихкод WB",
        "QR-код WB",
    )
    task_headers = (
        "Задание:",
        "Номер поставки:",
        "Кол-во заказов:",
        "Аккаунт:",
        "Склад:",
    )
    task_table = add_task_table(
        supply_instance=supply_instance,
        task_instance=task_instance,
        task_headers=task_headers
    )

    table = '<table class="outer-table">'
    table += "<tr>"
    for header in row_headers:
        table += f"<th>{header}</th>"
    table += "</tr>"
    for order in WbOrderModel.objects.filter(supply=supply_instance).all():
        table += fill_order_row(
            order=order
        )
    table += "</table>"

    html_template = f"""
<!DOCTYPE html>
<html>
<head>
<title>Сборочное задание</title>
<meta charset="UTF-8">
<style>
    @page {{
        size: A4 landscape;
        margin: 0.5cm;
        margin-bottom: 20mm;
        margin-top: 20mm;
        @top-right {{
        content: "Page " counter(page) " of " counter(pages);
        }}
        @top-center:first {{
        content: "Упаковочный лист";
        font-size: 20px;
        color: #333; /* Цвет по вашему выбору */
        }}
    }}
    body {{
        font-size: 12px;
    }}
    table {{
        border-collapse: collapse;
        width: 270mm;
    }}
    .outer-table th,
    .outer-table td {{
        border: 1px solid black; /* Тонкие границы для .outer-table */
        text-align: justify;
        padding: 4px;
    }}
    th, td {{
        text-align: center;
        padding-top: 4px;
        padding-bottom: 4px;
    }}
    th {{
        background-color: #333; /* Используйте нужный вам темно-серый цвет */
        color: #fff; /* Установите белый цвет текста для лучшей видимости */
        text-align: center !important;
    }}
    .no-border th:nth-child(3)  {{
        width: 15%
    }}
    .product-row {{
        padding-left: 20px !important; /* Левый отступ в 10px */
        text-align: left !important;
    }}
    .last-four {{
        font-size: 20px; /* Размер шрифта для последних четырех цифр */
    }}
</style>
</head>
<body>

{task_table}
{table}

</body>
</html>
    """

    pdf_buffer = io.BytesIO()
    weasyprint.HTML(string=html_template).write_pdf(pdf_buffer)
    pdf_buffer.seek(0)
    with open("package_doc.html", "w+", encoding="utf-8") as file:
        file.write(html_template)

    return pdf_buffer


def add_task_table(
        task_headers: tuple, task_instance, supply_instance
) -> str:
    task_table = '<table class="no-border">'
    task_table += "<tr>"
    for header in task_headers:
        task_table += f"<td>{header}</td>"
    task_table += "</tr><tr>"
    task_table += (
        f"<td>{str(task_instance)}</td>"
        f"<td>{supply_instance.wb_id}</td>"
        f"<td>{task_instance.amount}</td>"
        f"<td>{task_instance.business_account}</td>"
        f"<td>{task_instance.warehouse}</td>"
    )
    task_table += "</tr>"
    task_table += "</table>"
    return task_table


def fill_order_row(order: WbOrderModel):
    table = ""
    if not order.is_bundle:
        order_product: WbOrderProductModel
        order_product = WbOrderProductModel.objects.filter(order=order).first()
        barcodes = re.findall(r"\d{5,}", order_product.barcode)
        if order.wb_skus.replace("[", "").replace("]", "") in barcodes:
            barcodes.remove(order.wb_skus.replace("[", "").replace("]", ""))
        formatted_barcodes = re.sub(r'[^\w\s,]', '', str(barcodes))
        wb_skus = order.wb_skus.replace('[', '').replace(']', '')
        wb_qr = str(order.partA) + str(order.partB)
        table += (
            f"<tr>"
            f"<td>{order.wb_id}</td>"
            f"<td>{order_product.name}</td>"
            f"<td>{'Не комплект'}</td>"
            f"<td>{order.packaging_class}</td>"
            f"<td>{wb_skus}</td>"
            f"<td>{wb_qr[0:-4]} <b><span class='last-four'>{wb_qr[-4:]}</span></b></td>"
            f"</tr>"
        )
    else:
        order_products: list[WbOrderProductModel]
        order_products = WbOrderProductModel.objects.filter(order=order).all()
        bundle_property = "комплект простой" if len(order_products) == 1 else "комплект сложный"
        wb_skus = order.wb_skus.replace('[', '').replace(']', '')
        wb_qr = str(order.partA) + str(order.partB)
        table += (
            f"<tr>"
            f"<td>{order.wb_id}</td>"
            f"<td style='text-align: center !important;'><strong>КОМПЛЕКТ:</strong><br>{' + '.join([order_product.name for order_product in order_products])}</td>"
            f"<td>{bundle_property}</td>"
            f"<td>{order.packaging_class}</td>"
            f"<td>{wb_skus}</td>"
            f"<td>{wb_qr[0:-4]} <b><span class='last-four'>{wb_qr[-4:]}</span></b></td>"
            f"</tr>"
        )
        for order_product in order_products:
            barcodes = re.findall(r"\d{5,}", order_product.barcode)
            print(barcodes)
            print(order.wb_skus)
            if order.wb_skus.replace("[", "").replace("]", "") in barcodes:
                barcodes.remove(order.wb_skus.replace("[", "").replace("]", ""))
            formatted_barcodes = re.sub(r'[^\w\s,]', '', str(barcodes))

            table += (
                f"<tr>"
                f"<td></td>"
                f"<td class='product-row'>{order_product.name}</td>"
                f"<td>{order_product.quantity} шт.</td>"
                f"<td>{'-'}</td>"
                f"<td>{'-'}</td>"
                f"<td>{'-'}</td>"
                f"</tr>"
            )
    return table
