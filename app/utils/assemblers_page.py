import io
import re

import weasyprint

from app.models import WbOrderModel, WbOrderProductModel


def create_assemblers_page_html(task_instance, supply_instance):
    order_headers = (
        "Номер заказа",
        "Комплект",
        "Штрихкод WB",
        "QR-код WB",
        "Класс упавковки",
    )
    order_product_headers = (
        "Название товара",
        "Кол-во",
        "Код",
        "Место",
        "Штрихкоды (родные)",
    )
    task_headers = (
        "Задание:",
        "Номер поставки:",
        "Кол-во заказов:",
        "Аккаунт:",
        "Склад:",
    )
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

    table = '<table class="outer-table">'
    table += "<tr class='order-row'>"
    for header in order_headers:
        table += f"<th>{header}</th>"
    table += "</tr>"
    for order in WbOrderModel.objects.filter(supply=supply_instance).all():
        table += (
            f"<tr class='order-row'>"
            f"<td>{order.wb_id}</td>"
            f"<td>{'Да' if order.is_bundle else 'Нет'}</td>"
            f"<td>{order.wb_skus.replace('[', '').replace(']', '')}</td>"
            f"<td>{order.partA + order.partB}</td>"
            f"<td>{order.packaging_class}</td>"
            f"</tr>"
        )
        table += (
            f"<tr class='fixed-width-row'><td colspan='5'><table class='inner-table'>"
        )
        for order_product in WbOrderProductModel.objects.filter(order=order).all():
            barcodes = re.findall(r"\d{5,}", order_product.barcode)
            if order.wb_skus.replace("[", "").replace("]", "") in barcodes:
                barcodes.remove(order.wb_skus.replace("[", "").replace("]", ""))
            table += (
                f"<tr>"
                f"<td>{order_product.name}</td>"
                f"<td>{order_product.quantity} шт.</td>"
                f"<td>{order_product.code}</td>"
                f"<td>Место: {order_product.storage_location}</td>"
                f"<td>Родные ШК: {', '.join(barcodes) if barcodes else '-'}</td>"
                f"</tr>"
            )
        table += f"</table>"

    html_template = f"""
<!DOCTYPE html>
<html>
<head>
<title>Сборочное задание</title>
<meta charset="UTF-8">
<style>
    @page {{
        size: A4;
        margin: 0.5cm;
        margin-bottom: 20mm; /* Установите желаемый отступ, например, 20 миллиметров */
        margin-top: 20mm;
         @top-right{{
        content: "Page " counter(page) " of " counter(pages);
    }}
    }}
    body {{
        font-size: 12px; /* Устанавливаем размер шрифта в пикселях или других подходящих единицах измерения */
    }}
    table {{
        border-collapse: collapse;
        width: 190mm; /* Устанавливаем фиксированную ширину для обеих таблиц */
    }}

    th, td {{
        border: 1px solid black;
        text-align: center;
        padding-top: 4px;
        padding-bottom: 4px;
    }}

     .outer-table th:nth-child(1), th:nth-child(2), th:nth-child(3), th:nth-child(4), th:nth-child(5) {{
        width: 20%;
    }} 
    .order-row {{
        background-color: #f0f0f0;
    }}
        .inner-table td:nth-child(1) {{
        width: 40%;
    }}
     .inner-table td:nth-child(2),  td:nth-child(3),  td:nth-child(4),  td:nth-child(5) {{
        width: 15%;  
    }}
    .inner-table td  {{
        border: none;
    }}
    .inner-table th:first-child, td:first-child {{
        text-align: left;
    }}
    table.no-border, table.no-border th, table.no-border td {{
        border: none;
    }}
    .no-border th:nth-child(3)  {{
        width: 15%
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
    with open("pidor.html", "w+", encoding="utf-8") as file:
        file.write(html_template)

    return pdf_buffer
