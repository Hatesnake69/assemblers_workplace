from typing import Optional

from pydantic import BaseModel, PositiveInt


class OrderFromWb(BaseModel):
    id: PositiveInt
    rid: str
    createdAt: str
    warehouseId: PositiveInt
    supplyId: Optional[str] = None
    offices: list[str] = []
    address: Optional[dict]
    user: Optional[dict]
    skus: list[int]
    price: int
    convertedPrice: int
    currencyCode: int
    convertedCurrencyCode: int
    orderUid: str
    deliveryType: str
    nmId: PositiveInt
    chrtId: PositiveInt
    article: str
    isLargeCargo: bool


class OrdersResponseFromWb(BaseModel):
    orders: list[OrderFromWb]


class GetWbOrdersSchema(BaseModel):
    warehouse_id: PositiveInt
    account_id: PositiveInt
    orders_amount: PositiveInt
    name: str
    is_grouped: bool


class WbOrderSchema(BaseModel):
    id: PositiveInt
    warehouse_id: PositiveInt
    business_account_id: PositiveInt
    supply_id: Optional[PositiveInt] = None

    wb_id: PositiveInt
    wb_rid: str
    wb_created_at: str
    wb_warehouse_id: int
    wb_supply_id: Optional[str]
    wb_offices: str
    wb_address: Optional[str]
    wb_user: Optional[str]
    wb_skus: Optional[str]
    wb_price: int
    wb_converted_price: int
    wb_currency_code: int
    wb_converted_currency_code: int
    wb_order_uid: str
    wb_delivery_type: str
    wb_nm_id: int
    wb_chrt_id: int
    wb_article: str
    wb_is_large_cargo: bool

    partA: Optional[int]
    partB: Optional[int]
    barcode: Optional[str]
    svg_file: Optional[str]


class CreateAllOrdersFromWbCommand(BaseModel):
    warehouse_id: PositiveInt
    business_account_id: PositiveInt
    orders: list[OrderFromWb]


class CreateAllOrdersFromWbResponse(BaseModel):
    warehouse_id: int
    business_account_id: int
    orders: list[WbOrderSchema]


class OrderIdWithWbIdSchema(BaseModel):
    id: PositiveInt
    wb_id: PositiveInt


class OrderWithStickerSchema(BaseModel):
    id: PositiveInt
    partA: int
    partB: int
    barcode: str
    svg_file: str


class UpdateSupplyIdCommand(BaseModel):
    id: int
    supply_id: int
    wb_supply_id: str


class WbSticker(BaseModel):
    orderId: int
    partA: str
    partB: str
    barcode: str
    file: str


class WbOrderStickersResponse(BaseModel):
    stickers: list[WbSticker]


class MappingResponse(BaseModel):
    ms_id: str
    barcodes: str
    is_bundle: bool
    consist: Optional[str]
    nm_id: str
    name: str


class ProductParamsFromMs(BaseModel):
    name: str
    barcodes: list[dict] | None
    code: str
    packaging_class: str
    warehouse_place: str


class AssembleProductSchema(BaseModel):
    name: str
    amount: int
    code: str
    storage_location: str
    barcodes: str


class AssembleDocSchema(BaseModel):
    map_of_products: dict[str, AssembleProductSchema]


ms_param_map = {
    "packaging_class": "ed3f223d-85dd-11ed-0a80-07fe006eee6f",
    "warehouse_place": "2b779a1a-57b4-11ee-0a80-13880011881a",
}
