from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Category(models.Model):
    category_name = models.CharField("分類名稱", max_length=100)
    description = models.TextField("描述", blank=True)
    created_at = models.DateTimeField("建立時間", auto_now_add=True)
    updated_at = models.DateTimeField("更新時間", auto_now=True)
    

class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products', verbose_name="分類")
    product_name = models.CharField("商品名稱", max_length=100)
    product_price = models.IntegerField("商品價格", blank=True)
    description = models.TextField("商品描述", blank=True)
    product_img = models.CharField("商品圖片", max_length=200, blank=False, default='default.jpg')  # 儲存圖片相對路徑，例如 "images/product_default.jpg"      #{% load static %}  <img src="{% static product.product_img %}" alt="{{ product.product_name }}">
    created_at = models.DateTimeField("建立時間", auto_now_add=True)
    updated_at = models.DateTimeField("更新時間", auto_now=True)


class UpgradeOption(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='upgrade_options', verbose_name="商品")
    upgrade_name = models.CharField("升級選項名稱", max_length=100)
    upgrade_price = models.IntegerField("升級價格", blank=True)
    created_at = models.DateTimeField("建立時間", auto_now_add=True)
    updated_at = models.DateTimeField("更新時間", auto_now=True)


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', '未付款'),
        ('paid', '已付款'),
        ('shipped', '已出貨'),
        ('completed', '已完成'),
        ('cancelled', '已取消'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders', verbose_name="用戶")
    total_amount = models.IntegerField("總金額", default=0)  # 加入 default=0
    status = models.CharField("狀態", max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField("建立時間", auto_now_add=True)
    updated_at = models.DateTimeField("更新時間", auto_now=True)

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items', verbose_name="訂單")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="商品")
    quantity = models.PositiveIntegerField("數量", default=1)
    upgrade_option = models.ForeignKey(UpgradeOption, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="升級選項")
    unit_price = models.IntegerField("單價", default=0)  # 加入 default=0
    total_price = models.IntegerField("總價", default=0)  # 加入 default=0
    created_at = models.DateTimeField("建立時間", auto_now_add=True)
    updated_at = models.DateTimeField("更新時間", auto_now=True)
    

class UserDetail(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='detail', unique=True, verbose_name="用戶")  # 確保唯一資料
    account = models.CharField("帳號", max_length=30, blank=False, default='null')
    full_name = models.CharField("全名", max_length=100)
    address = models.TextField("地址")
    phone_number = models.CharField("電話號碼", max_length=20)
    payment_info = models.CharField("支付資訊", max_length=100)  # 建議加密處理或使用第三方支付系統
    created_at = models.DateTimeField("建立時間", auto_now_add=True)
    updated_at = models.DateTimeField("更新時間", auto_now=True)


from django.core.exceptions import ValidationError
# 餐廳模型
class Restaurant(models.Model):
    name = models.CharField("餐廳名稱", max_length=100)
    address = models.TextField("地址")
    phone_number = models.CharField("電話號碼", max_length=20)
    store_img = models.CharField("店家圖片", max_length=200, blank=False, default='default.jpg')
    created_at = models.DateTimeField("建立時間", auto_now_add=True)
    updated_at = models.DateTimeField("更新時間", auto_now=True)

class TimeSlot(models.Model):
    PERIOD_CHOICES = [
        ('lunch', '午餐'),
        ('dinner', '晚餐'),
    ]
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='time_slots', verbose_name="餐廳")
    period = models.CharField("餐期", max_length=10, choices=PERIOD_CHOICES)
    slot_time = models.TimeField("時段時間")

class Reservation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reservations', verbose_name="用戶")
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='reservations', verbose_name="餐廳")
    time_slot = models.ForeignKey(TimeSlot, on_delete=models.CASCADE, verbose_name="用餐時段")
    date = models.DateField("用餐日期")
    adult_count = models.PositiveIntegerField("大人人數")
    child_count = models.PositiveIntegerField("小孩人數")
    created_at = models.DateTimeField("建立時間", auto_now_add=True)
    updated_at = models.DateTimeField("更新時間", auto_now=True)
