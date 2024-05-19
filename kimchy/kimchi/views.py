from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.models import User, auth
from django.urls import reverse
from datetime import datetime
import base64
import logging
import socket
from django.db import connection


logger = logging.getLogger('kimchi_logger')


def success(request):
    decoded_message = ""
    try:
        message = request.GET.get('message', None)
        menu_sql = """SELECT * FROM kimchi_menu where availability=1"""
        order_sql = """SELECT * FROM kimchi_order"""

        with connection.cursor() as cursor:
            cursor.execute(menu_sql)
            menu_details = cursor.fetchall()
            cursor.execute(order_sql)
            order_details = cursor.fetchall()
        final = []
        for each_data in order_details:
            order = {}
            order['user'] = each_data[1]
            order['phone'] = each_data[2]
            order['address'] = each_data[3]
            order["dish"] = each_data[4]
            final.append(order)
        menu_final = []
        for each_data in menu_details:
            menu = {}
            menu['dish'] = each_data[1]
            menu['image'] = each_data[4]
            menu['ingredients'] = each_data[2]
            menu['price'] = each_data[3]
            menu_final.append(menu)
        order_details = [order for order in final if order["user"] == request.user.username]
        count = len(order_details)
        if message is not None:
            decoded_message = decode_message(message)
        return render(request, 'Dashboard.html', {'messages': decoded_message, "data": menu_final, "order": order_details, "count": count})
    except Exception as e:
        logger.exception("Exception while sending success: {}".format(e))


def encode_message(message):
    base_64_response = ""
    try:
        base_64_response = base64.b64encode(message.encode()).decode()
    except Exception as e:
        logger.exception("Error encoding JSON {}".format(str(e)))
    return base_64_response


def decode_message(message):
    message_response = ""
    try:
        message_response = base64.b64decode(message.encode()).decode()
    except Exception as e:
        logger.exception("Error decoding request json {}".format(str(e)))
    return message_response


def login(request):
    try:
        decoded_message = ""
        if request.method == "GET":
            message = request.GET.get('message', None)
            if message is not None:
                decoded_message = decode_message(message)
        if request.method == "POST":
            name = request.POST['name']
            password = request.POST['password']
            user = auth.authenticate(password=password, username=name)
            if user is not None:
                auth.login(request, user)
                message = "Login successfull"
                encoded_message = encode_message(message)
                return redirect(reverse('success') + '?message=' + encoded_message)
            else:
                message = "Invalid Credentials"
                encoded_message = encode_message(message)
                return redirect(reverse('login') + '?message=' + encoded_message)
        return render(request, 'Login.html', {'messages': decoded_message})
    except Exception as e:
        logger.exception("Exception while sending success: {}".format(e))


def register(request):
    try:
        if request.method == "POST":
            logger.debug("Inside Register")
            name = request.POST['name']
            email = request.POST['email']
            password = request.POST['password']
            user = User.objects.create_user(username=name, password=password, email=email, date_joined=datetime.now())
            user.save()
            message = "User Registered Successfully, You can login now"
            encoded_message = encode_message(message)
            return redirect(reverse('login') + '?message=' + encoded_message)
        else:
            return render(request, 'Register.html')
    except Exception as e:
        logger.exception("Exception while register: {}".format(e))


def get_ip_address():
    # Create a socket object
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    try:
        # Connect to a remote server (doesn't actually connect, just gets the IP address)
        s.connect(("8.8.8.8", 80))
        # Get the local IP address
        ip_address = s.getsockname()[0]
    except Exception as e:
        print("Error:", e)
        ip_address = None
    finally:
        # Close the socket
        s.close()

    return ip_address


def place_order(request):
    try:
        if request.method == "POST":
            name = request.POST['user_name']
            phone = request.POST['phone']
            address = request.POST['address']
            food = request.POST['food']
            quantity = request.POST['quantity']
            sql = """
                            INSERT INTO kimchi_order (name, phone, address, food, quantity)
                            VALUES (%s, %s, %s, %s, %s)
                        """

            # Execute the raw SQL query
            with connection.cursor() as cursor:
                cursor.execute(sql, [name, phone, address, food, quantity])
            encoded_message = encode_message("Order Placed Successfully")
            return redirect(reverse('success') + '?message=' + encoded_message)
    except Exception as e:
        logger.exception("Error while placing order: {}".format(e))
    return render(request, 'Dashboard.html')


def orders(request):
    decoded_message = ""
    try:
        # message = request.GET.get('message', None)
        sql = f"""SELECT * from kimchi_order"""

        # Execute the raw SQL query
        with connection.cursor() as cursor:
            cursor.execute(sql)
            details = cursor.fetchall()

        order_final = []
        for each_data in details:
            orders = {}
            orders['name'] = each_data[1]
            orders['phone'] = each_data[2]
            orders['address'] = each_data[3]
            orders['food'] = each_data[4]
            orders['quantity'] = each_data[5]
            order_final.append(orders)
        # if message is not None:
        #     decoded_message = decode_message(message)
        return render(request, 'order.html', {'messages': decoded_message, "data": order_final})
    except Exception as e:
        logger.exception("Exception while listing orders: {}".format(e))
    return render(request, 'order.html', {'messages': decoded_message})

def logout(request):
    try:
        auth.logout(request)
        return redirect(reverse('login'))
    except Exception as e:
        logger.exception("Error while logging out: {}".format(e))

