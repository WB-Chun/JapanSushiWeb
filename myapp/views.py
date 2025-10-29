from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import auth
from django.contrib import messages
from .models import Order, OrderItem, Product, UpgradeOption, Category, UserDetail, Restaurant, TimeSlot, Reservation
from myapp.models import *
from django.db.models import Sum
from django.forms.models import model_to_dict
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json

# Create your views here.

def home(request):
    return render(request, "home-v4.html", locals())

def adduser (request):
    # return HttpResponse("test")
    if request.method == "POST":
        # return HttpResponse("Get POST")
        username_get = request.POST["username"]
        email_get = request.POST["email"]
        phone_get = request.POST["phone"]
        account_get = request.POST["account"]
        password_get = request.POST["password"]
        print(username_get, email_get, password_get)
        print(f"電話：{phone_get}, 帳號：{account_get}")
         # 檢查 username 和 account 是否已存在
        try:
            user = User.objects.get(username=username_get)
            message = user.username + "此名稱已建立，您已註冊過。"
            return HttpResponse(f"""
                <script>
                    alert("{message}");
                    window.location.href = "/adduser/";  // 返回註冊頁面或其他頁面
                </script>
            """)
        except User.DoesNotExist:
            user = None

        # 檢查 account 是否唯一
        if UserDetail.objects.filter(account=account_get).exists():
            message = f"此帳號已被使用，請更換帳號名稱。"
            return HttpResponse(f"""
                <script>
                    alert("{message}");
                    window.location.href = "/adduser/";  // 返回註冊頁面或其他頁面
                </script>
            """)
        if user != None:
            message = user.username+"此帳號已建立"
            return HttpResponse(f"""
                        <script>
                            alert("{message}");
                            window.location.href = "/adduser/";  // 返回註冊頁面或其他頁面
                        </script>
                    """)
        else:
           # 建立新使用者
            user = User.objects.create_user(username=username_get, email=email_get, password=password_get)
            user.is_active = True
            user.is_staff = True
            user.save()

            # 建立並儲存 UserDetail 資料
            user_detail = UserDetail(
                user=user,
                account=account_get,
                full_name=username_get,         # 根據需求設定其他欄位的值
                phone_number=phone_get,
                address="",                     # 如果需要的話填入實際地址
                payment_info="",                # 可以留空或填入預設值
            )
            user_detail.save()

            # 註冊成功，返回包含 JavaScript 的 HttpResponse
            return render(request, "registration_ok.html", locals())             
    else:
        return render(request, "registration.html", locals())
    


def login(request):
    if request.method == "POST":
        account = request.POST["loginaccount"]
        password = request.POST["loginPassword"]

        try:
            # 根據 account 從 UserDetail 中找到對應的 User
            user_detail = UserDetail.objects.get(account=account)
            user = authenticate(username=user_detail.user.username, password=password)  # 使用 `username` 驗證密碼
        except UserDetail.DoesNotExist:
            user = None

        if user is not None:
            if user.is_active:
                auth_login(request, user)
                redirect_url = request.META.get('HTTP_REFERER', '/home/')
                return JsonResponse({"status": "success", "redirect_url": redirect_url})
            else:
                return JsonResponse({"status": "inactive"}, status=403)
        else:
            return JsonResponse({"status": "error", "message": "帳號或密碼輸入錯誤"}, status=401)
    else:
        if request.user.is_authenticated:
            return redirect("/home/")
        else:
            return render(request, "home-v4.html")


def logout(request):
    auth_logout(request)
    return redirect(request.META.get('HTTP_REFERER', '/home/'))


@login_required
def userupdate(request):
    user = request.user
    try:
        user_detail = UserDetail.objects.get(user=user)
    except UserDetail.DoesNotExist:
        user_detail = None

    if request.method == "POST":
        email_new = request.POST["email"]
        phone_new = request.POST["phone"]
        password_new = request.POST["password"]

        update_user = User.objects.get(id=user.id)
        update_user.email = email_new
        if password_new:
            update_user.set_password(password_new)
        update_user.save()

        if user_detail:
            user_detail.phone_number = phone_new
            user_detail.save()

        return JsonResponse({"success": True})

    return render(request, "user_update.html", locals())




from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.urls import reverse

def userforget (request):
    # return HttpResponse("test")
    if request.method == "POST":
        # return HttpResponse("Get POST")
        username_get = request.POST["username"]
        email_get = request.POST["email"]
        print(f"name:{username_get}, {email_get}")
        # 檢查 username 是否已存在
        try:
            user = User.objects.get(username=username_get)
        except User.DoesNotExist:
            user = None

        if user == None:
            message = "您未有帳號"
            return HttpResponse(f"""
                        <script>
                            alert("{message}");
                            window.location.href = "/userforget/";  // 返回註冊頁面或其他頁面
                        </script>
                    """)
        else:
           # 生成密碼重設連結
            token = default_token_generator.make_token(user)                                                    #使用 Django 預設的 default_token_generator 來生成一個唯一的令牌（token），它基於使用者的資訊進行生成，用於驗證請求的合法性。每個使用者的令牌都是唯一的且一次性的。
            uid = urlsafe_base64_encode(force_bytes(user.pk))                                                   #將使用者的主鍵，編碼成 URL 安全的格式，用於唯一識別使用者。
            reset_url = request.build_absolute_uri(reverse('password_reset_confirm', args=[uid, token]))        #使用者點擊郵件中的連結時會被引導到重設密碼的頁面。這裡生成的 reset_url 是一個絕對 URL，包含了使用者的 uid 和生成的 token。reverse 函數根據路由名稱（在此例中為 password_reset_confirm）生成相對路徑，build_absolute_uri 則生成完整的 URL。

            # 發送郵件
            subject = "密碼重設連結"
            message = f"您好，請點擊以下連結來重設您的密碼：\n{reset_url}\n此連結將在一定時間後失效。"
            send_mail(subject, message, "testforjayuse@gmail.com", [email_get])                                    #send_mail(subject(主旨), message, "your_email@gmail.com"(發信人), [email_get](收信人))

            return HttpResponse(f"""
                        <script>
                            alert("重設密碼的連結已發送到您的電子郵件，請檢查您的收件匣。");
                            window.location.href = "/home/";  // 返回主頁面或其他頁面
                        </script>
                    """)            
    else:
        return render(request, "userforget.html", locals())





def order(request):
    products = Product.objects.all()
    category = Category.objects.all()
    
    # 將升級選項附加到每個產品
    products_with_options = []
    for product in products:
        options = UpgradeOption.objects.filter(product=product)
        products_with_options.append({
            'product': product,
            'options': options  # 每個產品的升級選項列表
        })
    
    return render(request, "menu-v5.html", {
        "products_with_options": products_with_options,
        "category": category,
    })



@csrf_exempt
def checkout(request):
    if request.method == 'POST':
            # 解析 JSON 資料
        data = json.loads(request.body)
        cart_items = data.get('cartItems', [])
        total_money = data.get('total_money', 0)
        user = request.user
        pay = data.get('payment_method')
        pay_info = data.get('payment_info')
        print(f"cart_items: {cart_items}")
        print(f"使用者: {user}")
        print(f"支付方式: {pay}")
        print(f"信用卡號: {pay_info}")

    # 創建訂單存入資料庫
    user_instance = request.user
    Order_create = Order(
        total_amount=total_money,
        status=pay,
        user=user_instance,
    )
    Order_create.save()

# 遍歷購物車專案並建立 OrderItem
    for item in cart_items:
        product_name = item.get('product_name')
        quantity = item.get('quantity')
        options = item.get('options', [])
        
        print(f"Processing item: {product_name} with quantity: {quantity}")

        # 取得 Product 實例
        try:
            product = Product.objects.get(product_name=product_name)
        except Product.DoesNotExist:
            print(f"Product： {product_name} not found.")
            continue

        # 計算單價及升級選項價格
        unit_price = product.product_price
        total_item_price = unit_price * quantity

        # 如果有升級選項，增加價格
        upgrade_option = None
        if options:
            matching_options = UpgradeOption.objects.filter(upgrade_name=options[0].get('name'))
            if matching_options.exists():
                upgrade_option = matching_options.first()
                total_item_price += upgrade_option.upgrade_price * quantity

        # 建立 OrderItem 並關聯到訂單
        order_item = OrderItem(
            order=Order_create,
            product=product,
            quantity=quantity,
            upgrade_option=upgrade_option,
            unit_price=unit_price,
            total_price=total_item_price,
        )
        order_item.save()  # 保存 OrderItem
        print(f"OrderItem created： {product_name} with total price {total_item_price}")

    return HttpResponse("訂單已成功創建")


def checkout_detial(request):
    # 取得目前使用者的所有訂單
    user_orders = Order.objects.filter(user=request.user).prefetch_related('order_items__product', 'order_items__upgrade_option')       #篩選出與目前登入的使用者相關的 Order 訂單，prefetch_related 來預取資料，減少查詢次數以優化效能。，訂單中的 order_items 和其相關聯的 product 資料一起預取以及upgrade_option 資料一起預取

    # 將訂單數據組裝成列表傳遞給前端
    order_data = []
    for order in user_orders:
        items = []
        for item in order.order_items.all():
            items.append({
                "product_name": item.product.product_name,
                "total_price": item.total_price,
                "upgrade_name": item.upgrade_option.upgrade_name if item.upgrade_option else None,
                "upgrade_price": item.upgrade_option.upgrade_price if item.upgrade_option else 0,
                "quantity": item.quantity,
            })
        # 確保包含電話號碼
        user_phone = request.user.detail.phone_number if hasattr(request.user, 'detail') else "無資料"
        order_data.append({
            "order_id": order.id,
            "user_name": request.user.username,
            "user_email": request.user.email,
            "user_phone": user_phone,
            "total_amount": order.total_amount,
            "items": items,
            "payment_method": order.status,  # 加入支付方式
            "create_time": order.created_at,
        })

    return render(request, 'checkout_detail.html', locals())



def reserve(request):
    all_fully_booked = False
    restaurant_db = Restaurant.objects.all()
    # for restaurant_data in restaurant_db:
    #     print(model_to_dict(restaurant_data))
    TimeSlot_db = TimeSlot.objects.all()
    # for TimeSlot_data in TimeSlot_db:
    #     print(model_to_dict(TimeSlot_data))

    # 提取唯一的 period 值
    unique_periods = TimeSlot_db.values_list('period', flat=True).distinct()

    if request.method == "POST":
        # 讀取表單提交的數據
        restaurant_id = request.POST["data_store" ]      # 餐廳 ID
        people_info = request.POST["data_people" ]      # 人數信息（例如 '2 位大人, 0 位兒童'）
        meal_period = request.POST["data_period"]       # 餐期（'午餐' 或 '晚餐'）
        date = request.POST["data_datetime"]            # 用餐日期
        print(f"餐廳：{restaurant_id}")
        print(f"人數：{people_info}")
        print(f"餐期：{meal_period}")
        print(f"日期：{date}")

        # 解析人數信息
        if "位大人" in people_info:
            adult_count = int(people_info.split("位大人")[0].strip())
        else:
            adult_count = 0
        if "位兒童" in people_info:
            child_count = int(people_info.split("位兒童")[0].split(",")[-1].strip())
        else:
            child_count = 0
        print(f"大人：{adult_count}")
        print(f"小孩：{child_count}")

         # 計算等值大人數（每兩個小孩算一位大人）
        total_adults_equivalent = adult_count + (child_count // 2)
        print(f"總人數：{total_adults_equivalent}")
        
        # 查詢餐廳
        try:
            restaurant = Restaurant.objects.get(id=restaurant_id)
        except Restaurant.DoesNotExist:
            return JsonResponse({"error": "找不到指定的餐廳"}, status=400)
        print(f"餐廳(db)：{restaurant}")

        # 查詢符合餐期的時段
        available_slots = TimeSlot.objects.filter(
            restaurant=restaurant,
            period=meal_period
        )
        print(f"符合的餐廳和餐期：{available_slots}")                       #該餐廳符合指定 meal_period 的所有可用時段


         # 篩選出可用的時段，檢查每個時段的剩餘可用人數
        available_times = []                                                                            #暫放「時間」和「剩餘可用座位數」
        for slot in available_slots:
            # 查詢該日期該時段已預訂的等值大人數
            reserved_total = Reservation.objects.filter(                                                #該時段的已有訂位人數，包含等值成人數。
                restaurant=restaurant,
                time_slot=slot,
                date=date
            ).aggregate(total=Sum('adult_count') + Sum('child_count') / 2)['total'] or 0                #用 ['total'] 來提取加總值，如果查詢無結果，則設定為 0。
            print(f"已預訂人數：{reserved_total}") 

            # 計算剩餘可用座位，並篩選出足夠容納的時段
            remaining_seats = 10 - reserved_total                        #計算當前時段的剩餘可用座位數。假設每個時段的最大可用座位數為 10(不足以容納需求時，該時段不會列入最終結果)
            if remaining_seats >= total_adults_equivalent:               #檢查當前時段的剩餘可用座位是否足夠容納等值成人數(若符合條件，則將該時段資訊加入 available_times)
                available_times.append({
                    "time": slot.slot_time.strftime("%H:%M"),            #將該 slot 的時段時間 slot_time 轉換為「HH」格式，以及 remaining_seats 數量，加入 available_times
                    "remaining_seats": remaining_seats
                })

        print(f"最終符合時段和剩餘人數：{available_times}") 
        # 檢查是否所有時段已滿
        all_fully_booked = all(time["remaining_seats"] == 0 for time in available_times)
        print(f"檢查時段：{all_fully_booked}")

        # 返回篩選結果
        return render(request, 'Reserve-v4.html', locals())
    else:
        return render(request, 'Reserve-v4.html', locals())
    
@csrf_exempt
def booking(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            restaurant_id_data = data.get("restaurant_id")
            people_info_data = data.get("people_info")
            meal_period_data = data.get("meal_period")
            date_data = data.get("date")
            slot_time_data = data.get("slot_time")

            if "位大人" in people_info_data:
                adult_count_data = int(people_info_data.split("位大人")[0].strip())
            else:
                adult_count_data = 0
            if "位兒童" in people_info_data:
                child_count_data = int(people_info_data.split("位兒童")[0].split(",")[-1].strip())
            else:
                child_count_data = 0

            # 查找餐廳和時段實例
            restaurant_instance = Restaurant.objects.get(id=restaurant_id_data)
            time_slot_instance = TimeSlot.objects.get(restaurant=restaurant_instance, period=meal_period_data, slot_time=slot_time_data)

            # 建立預訂
            user_instance = request.user
            booking_create = Reservation(
                date=date_data,
                adult_count=adult_count_data,
                child_count=child_count_data,
                user=user_instance,
                restaurant=restaurant_instance,
                time_slot=time_slot_instance,
            )
            booking_create.save()

            # 返回成功回應
            response_data = {
                "success": True,
                "reservation_id": booking_create.id  # 使用實際的預訂編號
            }
            return JsonResponse(response_data)

        except Restaurant.DoesNotExist:
            return JsonResponse({"success": False, "error": "指定的餐廳不存在"}, status=400)
        except TimeSlot.DoesNotExist:
            return JsonResponse({"success": False, "error": "指定的時段不存在"}, status=400)
        except json.JSONDecodeError:
            print("JSON 解析錯誤")
            return JsonResponse({"success": False, "error": "JSON 格式錯誤"}, status=400)
    return JsonResponse({"success": False, "error": "僅支持 POST 請求"}, status=405)


@login_required  # 確保使用者已登入
def reserve_detial(request):
    # 獲取目前登入用戶的所有訂位記錄
    reservations = Reservation.objects.filter(user=request.user).select_related('restaurant', 'time_slot').order_by('-date')
    # 將訂位記錄傳遞給前端
    return render(request, "reserve_detail.html", {"reservations": reservations})



def news1(request):

    # return HttpResponse("as")
    return render(request, "news-五星.html", locals())

def news2(request):

    return render(request, "news-海之日.html", locals())

def news3(request):

    return render(request, "news-會員禮.html", locals())

def news4(request):

    return render(request, "news-鬼與魚共舞.html", locals())

def food(request):
    food_data = Product.objects.all()
    print("test-----")
    for data in food_data:
        print(model_to_dict(data))

    return render(request, "food-swiper.html", locals())