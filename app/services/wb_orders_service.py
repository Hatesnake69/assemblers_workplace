import json

from app.models import WbSupplyModel, TaskModel, WbOrderModel, WbOrderProductModel, FailedNmIdProductModel
from app.schemas.order_schemas import (
    OrdersResponseFromWb,
    MappingResponse,
    ProductParamsFromMs,
    ms_param_map,
    WbOrderStickersResponse,
)
from app.services.api_request_service import RequestAPI
from app.services.partition_service import get_prior_partition
from assemblers_workplace.settings import settings


class WbOrdersService:
    def __init__(self, wb_token: str, amount: int, warehouse_id: int):
        self.wb_token = wb_token
        self.amount = amount
        self.warehouse_id = warehouse_id
        self.request_api = RequestAPI()

    def create_new_supply(self, name: str, task: TaskModel) -> WbSupplyModel:
        new_supply_resp = self.request_api.post(
            url=settings.post_wb_new_supply_url,
            params={},
            headers={
                "Content-Type": "application/json",
                "charset": "UTF-8",
                "Authorization": f"Bearer {self.wb_token}",
            },
            body={"name": name},
        ).json()
        new_supply = WbSupplyModel.objects.create(
            task=task,
            wb_id=new_supply_resp.get("id"),
            wb_name=name,
        )
        return new_supply

    def get_new_orders(self, supply: WbSupplyModel) -> list[WbOrderModel]:
        response_from_wb = self.request_api.get(
            url=settings.get_wb_new_orders_url,
            headers={
                "Content-Type": "application/json",
                "charset": "UTF-8",
                "Authorization": f"Bearer {self.wb_token}",
            },
            params={},
        ).json()

        orders_from_wb_resp = OrdersResponseFromWb.parse_obj(response_from_wb)
        orders_from_wb_resp = filter_by_warehouse(
            chunk_of_orders=orders_from_wb_resp, wb_warehouse_id=self.warehouse_id
        )
        orders_from_wb_resp.orders = get_prior_partition(orders_from_wb_resp)
        orders_from_wb_resp.orders = group_same_orders(
            chunk_of_orders=orders_from_wb_resp, limit=self.amount
        )
        new_orders = []
        for order in orders_from_wb_resp.orders:
            resp_from_mapping = self.request_api.get(
                url=f"{settings.get_mapping_url}?nm_id={order.nmId}",
                params={},
                headers={},
            ).json()
            if len(resp_from_mapping) == 0:
                try:
                    FailedNmIdProductModel.objects.get(nm_id=str(order.nmId))
                    print("this failed nm_id already recorded")

                except FailedNmIdProductModel.DoesNotExist:
                    new_failed_product = FailedNmIdProductModel(
                        nm_id=order.nmId,
                        name=order.article,
                        wb_order_id=order.id,
                        created_at=order.createdAt
                    )
                    new_failed_product.save()
                    print(f"new failed product: {new_failed_product}")
                continue
            info_from_mapping = MappingResponse.parse_obj(resp_from_mapping[0])
            patch_req = self.request_api.patch(
                url=f"https://suppliers-api.wildberries.ru/api/v3/supplies/{supply.wb_id}/orders/{order.id}",
                headers={
                    "Content-Type": "application/json",
                    "charset": "UTF-8",
                    "Authorization": f"Bearer {self.wb_token}",
                },
                params={},
                body={},
            )
            if patch_req.ok:
                new_order = WbOrderModel.objects.create(
                    supply=supply,
                    wb_id=order.id,
                    wb_rid=order.rid,
                    wb_created_at=order.createdAt,
                    wb_warehouse_id=order.warehouseId,
                    wb_supply_id=None,
                    wb_offices=order.offices,
                    wb_address=order.address,
                    wb_user=order.user,
                    wb_skus=order.skus,
                    wb_price=order.price,
                    wb_converted_price=order.convertedPrice,
                    wb_currency_code=order.currencyCode,
                    wb_converted_currency_code=order.convertedCurrencyCode,
                    wb_order_uid=order.orderUid,
                    wb_delivery_type=order.deliveryType,
                    wb_nm_id=order.nmId,
                    wb_chrt_id=order.chrtId,
                    wb_article=order.article,
                )
                new_orders.append(new_order)

                if info_from_mapping.consist:
                    consists_dict = json.loads(info_from_mapping.consist)
                    for ms_id in consists_dict:
                        order_product_quantity = int(consists_dict.get(ms_id))

                        self.create_order_product(
                            ms_id=ms_id,
                            order_product_quantity=order_product_quantity,
                            new_order=new_order,
                            info_from_mapping=info_from_mapping,
                            ms_bundle_id=info_from_mapping.ms_id,
                            supply=supply,
                        )
                    new_order.is_bundle = True
                    new_order.save()
                else:
                    ms_id = (info_from_mapping.ms_id,)
                    order_product_quantity = 1
                    self.create_order_product(
                        ms_id=ms_id,
                        order_product_quantity=order_product_quantity,
                        new_order=new_order,
                        info_from_mapping=info_from_mapping,
                        supply=supply,
                    )

        return new_orders

    def get_order_stickers(self, orders: list[WbOrderModel]):
        response = self.request_api.post(
            url="https://suppliers-api.wildberries.ru/api/v3/orders/stickers",
            headers={
                "Content-Type": "application/json",
                "charset": "UTF-8",
                "Authorization": f"Bearer {self.wb_token}",
            },
            body={"orders": [elem.wb_id for elem in orders]},
            params={
                "type": "svg",
                "width": 58,
                "height": 40
            },
        ).json()
        wb_stickers = WbOrderStickersResponse(**response)
        for elem in orders:
            for wb_elem in wb_stickers.stickers:
                if wb_elem.orderId == elem.wb_id:
                    elem.partA = wb_elem.partA
                    elem.partB = wb_elem.partB
                    elem.barcode = wb_elem.barcode
                    elem.svg_file = wb_elem.file
                    elem.save()

    def send_supply_to_deliver(self, supply: WbSupplyModel):
        resp = self.request_api.patch(
            url=f"https://suppliers-api.wildberries.ru/api/v3/supplies/{supply.wb_id}/deliver",
            headers={
                "Content-Type": "application/json",
                "charset": "UTF-8",
                "Authorization": f"Bearer {self.wb_token}",
            },
            params={},
            body={},
        )
        if not resp.ok:
            raise Exception("supply patch failed")

    def get_supply_sticker(self, supply: WbSupplyModel):
        supply_sticker_response = self.request_api.get(
            url=f"https://suppliers-api.wildberries.ru/api/v3/supplies/{supply.wb_id}/barcode?type=svg",
            headers={
                "Content-Type": "application/json",
                "charset": "UTF-8",
                "Authorization": f"Bearer {self.wb_token}",
            },
            params={
                "type": "svg"
            },
        ).json()
        supply.svg_file = supply_sticker_response.get("file")
        supply.save()

    def create_order_product(
        self,
        ms_id,
        order_product_quantity,
        new_order: WbOrderModel,
        info_from_mapping: MappingResponse,
        supply: WbSupplyModel,
        ms_bundle_id: str = None,
    ) -> None:
        already_existing_order: WbOrderModel = WbOrderModel.objects.filter(
            supply=supply, wb_nm_id=new_order.wb_nm_id
        ).first()
        already_existing_order_products: list[WbOrderProductModel] = WbOrderProductModel.objects.filter(
            order=already_existing_order
        )

        if not ms_bundle_id:
            for existing_product in already_existing_order_products:
                WbOrderProductModel.objects.create(
                    order=new_order,
                    name=existing_product.name,
                    quantity=order_product_quantity,
                    barcode=str(existing_product.barcode),
                    photo=None,
                    code=existing_product.code,
                    storage_location=existing_product.storage_location,
                )
            if already_existing_order_products:
                new_order.packaging_class = already_existing_order.packaging_class
                new_order.save()
                return

        if type(ms_id) == tuple:
            order_product_ms_id = ms_id[0]
        else:
            order_product_ms_id = ms_id
        if (
            info_from_mapping.is_bundle and not new_order.packaging_class
        ):
            bundle_or_product_from_ms = self.request_api.get(
                url=f"{settings.get_bundle_info_url}/{ms_bundle_id}",
                headers={
                    "Accept - Encoding": "gzip",
                    "Content-Type": "application/json",
                    "charset": "UTF-8",
                    "Authorization": f"Bearer {settings.ms_token}",
                },
                params={},
            )
            bundle_params = get_product_params(
                product_from_ms=bundle_or_product_from_ms.json()
            )
            new_order.packaging_class = bundle_params.packaging_class
            new_order.save()

        resp_from_ms = self.request_api.get(
            url=f"{settings.get_product_info_url}/{order_product_ms_id}",
            headers={
                "Accept - Encoding": "gzip",
                "Content-Type": "application/json",
                "charset": "UTF-8",
                "Authorization": f"Bearer {settings.ms_token}",
            },
            params={},
        )
        product_params = get_product_params(product_from_ms=resp_from_ms.json())
        if not new_order.packaging_class:
            new_order.packaging_class = product_params.packaging_class
            new_order.save()
        WbOrderProductModel.objects.create(
            order=new_order,
            name=product_params.name,
            quantity=order_product_quantity,
            barcode=str(product_params.barcodes),
            photo=None,
            code=product_params.code,
            storage_location=product_params.warehouse_place,
        )


def filter_by_warehouse(
    chunk_of_orders: OrdersResponseFromWb, wb_warehouse_id: int
) -> OrdersResponseFromWb:
    list_of_orders = []
    for order in chunk_of_orders.orders:
        if order.warehouseId == wb_warehouse_id:
            list_of_orders.append(order)

    return OrdersResponseFromWb(orders=list_of_orders)


def group_same_orders(chunk_of_orders: OrdersResponseFromWb, limit: int):
    list_of_orders = []
    dict_of_orders = {}
    for order in chunk_of_orders.orders:
        if not dict_of_orders.get(order.nmId):
            dict_of_orders[order.nmId] = {"orders": [order], "len": 1}

        else:
            dict_of_orders[order.nmId]["orders"].append(order)
            dict_of_orders[order.nmId]["len"] += 1
    list_of_grouped_orders = [dict_of_orders.get(elem) for elem in dict_of_orders]
    list_of_grouped_orders = sorted(
        list_of_grouped_orders, key=lambda x: x["len"], reverse=True
    )
    for elem in list_of_grouped_orders:
        list_of_orders += elem.get("orders")
    res = list_of_orders[0:limit]
    return res


def get_product_params(product_from_ms: dict) -> ProductParamsFromMs:
    name = product_from_ms.get("name")
    barcodes = product_from_ms.get("barcodes")
    code = product_from_ms.get("code")
    packaging_class = "-"
    warehouse_place = "-"
    for attr in product_from_ms.get("attributes"):
        if attr.get("id") == ms_param_map.get("packaging_class"):
            packaging_class = attr.get("value").get("name")
        if attr.get("id") == ms_param_map.get("warehouse_place"):
            warehouse_place = attr.get("value")
    return ProductParamsFromMs(
        name=name,
        barcodes=barcodes,
        code=code,
        packaging_class=packaging_class,
        warehouse_place=warehouse_place,
    )
