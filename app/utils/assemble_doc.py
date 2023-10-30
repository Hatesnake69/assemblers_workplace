import io
import re

import weasyprint

from app.models import TaskModel, WbSupplyModel, WbOrderModel, WbOrderProductModel
from app.schemas.order_schemas import AssembleProductSchema, AssembleDocSchema


def create_assemble_doc(task_instance: TaskModel, supply_instance: WbSupplyModel):
    row_headers = (
        "№",
        "Наименование товара",
        "Кол-во",
        "Код",
        "Место на складе",
        "Штрихкоды (родные)",
    )
    task_headers = (
        "Задание:",
        "Номер поставки:",
        "Кол-во заказов:",
        "Кол-во товаров:",
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

    assemble_doc = get_all_assemble_products(orders=WbOrderModel.objects.filter(supply=supply_instance).all())

    table += fill_assemble_table(assemble_doc=assemble_doc)

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
                content: "Стр. " counter(page) " из " counter(pages);
            }}
            @top-center:first {{
                content: "Сборочный лист";
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
    with open("assemble_doc.html", "w+", encoding="utf-8") as file:
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
    orders = WbOrderModel.objects.filter(supply=supply_instance).all()
    products_amount = 0
    for order in orders:
        products = WbOrderProductModel.objects.filter(order=order).all()
        for product in products:
            products_amount += product.quantity
    task_table += (
        f"<td>{str(task_instance)}</td>"
        f"<td>{supply_instance.wb_id}</td>"
        f"<td>{task_instance.amount}</td>"
        f"<td>{products_amount}</td>"
        f"<td>{task_instance.business_account}</td>"
        f"<td>{task_instance.warehouse}</td>"
    )
    task_table += "</tr>"
    task_table += "</table>"
    return task_table


def get_all_assemble_products(orders: list[WbOrderModel]) -> AssembleDocSchema:
    map_of_products: dict[str, AssembleProductSchema] = dict()
    for order in orders:
        products_from_order = get_products_from_order(order=order)
        for product_name in products_from_order.map_of_products:
            if product_name not in map_of_products:
                map_of_products[product_name] = products_from_order.map_of_products.get(product_name)
            else:
                map_of_products[product_name].amount += products_from_order.map_of_products.get(product_name).amount
    return AssembleDocSchema(map_of_products=map_of_products)


def get_products_from_order(order: WbOrderModel) -> AssembleDocSchema:
    res = dict()
    order_products: list[WbOrderProductModel] = WbOrderProductModel.objects.filter(order=order).all()
    for order_product in order_products:
        if not res.get(order_product.name):
            barcodes = re.findall(r"\d{5,}", order_product.barcode)
            if order.wb_skus.replace("[", "").replace("]", "") in barcodes:
                barcodes.remove(order.wb_skus.replace("[", "").replace("]", ""))
            formatted_barcodes = re.sub(r'[^\w\s,]', '', str(barcodes))
            res[order_product.name] = AssembleProductSchema(
                name=order_product.name,
                amount=1,
                code=order_product.code,
                storage_location=order_product.storage_location,
                barcodes=formatted_barcodes,
            )
        else:
            res[order_product.name].amount += 1

    return AssembleDocSchema(
        map_of_products=res
    )


def fill_assemble_table(assemble_doc: AssembleDocSchema) -> str:
    res = ""
    for index, product in enumerate(assemble_doc.map_of_products):
        res += (
            f"<tr>"
            f"<td>{index+1}</td>"
            f"<td>{product}</td>"
            f"<td>{assemble_doc.map_of_products.get(product).amount}</td>"
            f"<td>{assemble_doc.map_of_products.get(product).code}</td>"
            f"<td>{assemble_doc.map_of_products.get(product).storage_location}</td>"
            f"<td>{assemble_doc.map_of_products.get(product).barcodes}</td>"
            f"</tr>"
        )
    return res
