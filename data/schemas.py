from datetime import datetime
from decimal import Decimal
from typing import List

from pydantic import BaseModel


class UserSchema(BaseModel):
    id: str
    name: str
    permissions: str
    pinyin: str | None

    class Config:
        from_attributes = True


class UserSchemaSecure(UserSchema):
    phone: str | None

    class Config:
        from_attributes = True


class UserStatisticsSchema(BaseModel):
    totalOrders: int
    totalCups: int
    totalSpent: Decimal
    deletable: bool


class LoginSchema(BaseModel):
    username: str
    password: str


class CategorySchema(BaseModel):
    id: int
    name: str


class TagSchema(BaseModel):
    id: int
    name: str
    color: str


class OptionItemSchema(BaseModel):
    id: int
    typeId: int
    name: str
    isDefault: bool
    priceChange: Decimal

    class Config:
        from_attributes = True


class OptionTypeSchema(BaseModel):
    id: int
    name: str
    items: List[OptionItemSchema]

    class Config:
        from_attributes = True


class ItemTypeSchema(BaseModel):
    id: int
    category: CategorySchema
    name: str
    image: str
    tags: List[TagSchema]
    description: str
    shortDescription: str
    options: List[OptionTypeSchema]
    basePrice: Decimal
    salePercent: float

    class Config:
        from_attributes = True


class OrderedItemSchema(BaseModel):
    id: int
    orderId: int
    itemType: ItemTypeSchema
    appliedOptions: List[OptionItemSchema]
    amount: int

    class Config:
        from_attributes = True


class OrderedItemCreateSchema(BaseModel):
    itemType: int
    appliedOptions: List[int]
    amount: int

    class Config:
        from_attributes = True


class OrderSchema(BaseModel):
    id: int
    totalPrice: Decimal
    number: str
    status: str  # notStarted, inProgress, ready, or pickedUp
    createdTime: datetime
    type: str  # pickUp, delivery
    deliveryRoom: str | None
    user: UserSchema | None
    items: List[OrderedItemSchema]

    class Config:
        from_attributes = True


class OrderStatusUpdateSchema(BaseModel):
    id: int
    status: str  # notStarted, inProgress, ready or pickedUp


class OrderCreateSchema(BaseModel):
    type: str  # pickUp, delivery
    deliveryRoom: str | None
    items: List[OrderedItemCreateSchema]
    onSiteOrder: bool


class OrderEstimateSchema(BaseModel):
    time: int
    orders: int
    type: str | None  # pickUp, delivery
    number: str | None
    status: str | None  # notStarted, inProgress, ready, or pickedUp


class SettingItemSchema(BaseModel):
    key: str
    value: str


class StatsAggregateSchema(BaseModel):
    todayRevenue: Decimal
    todayUniqueUsers: int
    todayOrders: int
    todayCups: int
    weekRevenue: Decimal
    weekRevenueRange: str
    revenue: dict[str, Decimal]  # YYYY-MM-DD to Decimal
    uniqueUsers: dict[str, int]  # YYYY-MM-DD to int
    orders: dict[str, int]
    cups: dict[str, int]
