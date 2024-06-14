from django.contrib.auth.models import User, auth
from datetime import datetime
import logging
from django.views.decorators.csrf import csrf_exempt
from django.core.validators import EmailValidator
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.views.decorators.http import require_POST
import json
from django.db.models import Q
from django.http import JsonResponse
from .models import FriendRequest
from datetime import timedelta
from django.utils import timezone
from django.db.models import Count
from django.db import models


logger = logging.getLogger('kimchi_logger')


@csrf_exempt
# @api_view(['POST'])
def login(request):
    final_json = {"status": False, "message": "Failed to login"}
    try:
        if request.method == "POST":
            data = json.loads(request.body)
            # data = request.data
            email_validator = EmailValidator()
            email_validator(data['email'])
            name = data['email'].split('@')[0]
            password = data['password']
            user = auth.authenticate(password=password, username=name)
            if user is not None:
                auth.login(request, user)
                final_json["status"] = True
                final_json["message"] = "Login successfull"
            else:
                final_json["message"] = "Invalid Credentials"
    except Exception as e:
        logger.exception("Exception while sending success: {}".format(e))
    return JsonResponse(final_json)

@csrf_exempt
# @api_view(['POST'])
def register(request):
    final_json = {"status": False, "message": "Failed to register"}
    try:
        if request.method == "POST":
            logger.debug("Inside Register")
            data = json.loads(request.body)
            # data = request.data
            email_validator = EmailValidator()
            email_validator(data['email'])
            name = data['email'].split('@')[0]
            email = data['email']
            password = data['password']
            user = User.objects.create_user(username=name, password=password, email=email, date_joined=datetime.now())
            user.save()
            final_json["status"] = True
            final_json["message"] = "User Registered Successfully, You can login now"
        else:
            final_json['message'] = "Invalid Request Method"
    except Exception as e:
        logger.exception("Exception while register: {}".format(e))
    return JsonResponse(final_json)


@csrf_exempt
# @api_view(['POST'])
def search_user(request):
    final_json = {"status": False, "message": "Failed to search key word"}
    try:
        if request.user.is_authenticated:
            data = json.loads(request.body)
            # data = request.data
            search_key = data['search_key']
            try:
                users = User.objects.get(email=search_key)
                final_json["data_search_through_email"] = {"username": users.username}
                final_json["status"] = True
                final_json["message"] = "User Loaded Successfully"
                return JsonResponse(final_json)
            except User.DoesNotExist:
                logger.exception("Email Not Exist")
            try:
                users = User.objects.filter(
                    username__icontains=search_key
                )
                # filter_data = []
                # for each_data in users:
                #     filter_data.append(each_data)
                filter_data = [{"username": user.username} for user in users]
                # comma_separated = ', '.join(map(str, filter_data))
                final_json["status"] = True
                final_json["data_search_through_username"] = filter_data
                final_json["message"] = "All Users Loaded Successfully"
                return JsonResponse(final_json)
            except Exception as e:
                logger.exception("User Not Exist: {}".format(e))

            try:
                users = User.objects.filter(
                    Q(username__icontains=search_key) | Q(email__icontains=search_key)
                )
                # filter_data = []
                # for each_data in users:
                #     filter_data.append(each_data)
                # comma_separated = ', '.join(map(str, filter_data))
                filter_data = [{"username": user.username} for user in users]
                final_json["status"] = True
                final_json["data_search_through_email_or_password"] = filter_data
                final_json["message"] = "All Users with username or email Loaded Successfully"
            except User.DoesNotExist:
                logger.exception("Failed to search both email and password")

        else:
            final_json["message"] = "Please Login First before Proceeding"
    except Exception as e:
        logger.exception("Failed to search user: {}".format(e))
    return JsonResponse(final_json)


@csrf_exempt
@require_POST
def send_friend_request(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)

    from_user = request.user.username
    data = json.loads(request.body)
    # data = request.data
    to_user_id = data['to_user_id']

    if not to_user_id:
        return JsonResponse({'error': 'to_user_id is required'}, status=400)

    try:
        to_user = User.objects.get(username=to_user_id)
    except User.DoesNotExist:
        return JsonResponse({'error': 'User does not exist'}, status=404)

    if from_user == to_user:
        return JsonResponse({'error': 'You cannot send a friend request to yourself'}, status=400)

    one_minute_ago = timezone.now() - timedelta(minutes=1)
    recent_requests = FriendRequest.objects.filter(from_user=from_user, created_at__gte=one_minute_ago).count()

    if recent_requests >= 3:
        return JsonResponse({'error': 'You can only send 3 friend requests per minute'}, status=429)

    if FriendRequest.objects.filter(from_user=from_user, to_user=to_user).exists():
        return JsonResponse({'error': 'Friend request already sent'}, status=400)

    FriendRequest.objects.create(from_user=from_user, to_user=to_user)
    return JsonResponse({'message': 'Friend request sent'}, status=201)


@csrf_exempt
@require_POST
def accept_friend_request(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)

    # request_id = request.POST.get('request_id')
    user = request.user.username
    data = json.loads(request.body)
    # data = request.data
    request_id = data['request_id']

    if not request_id:
        return JsonResponse({'error': 'request_id is required'}, status=400)

    try:
        friend_request = FriendRequest.objects.get(to_user=request_id)
    except FriendRequest.DoesNotExist:
        return JsonResponse({'error': 'Friend request does not exist'}, status=404)

    if friend_request.to_user == request.user.username:
        return JsonResponse({'error': 'This friend request is not for you'}, status=400)

    friend_request.status = 'accepted'
    friend_request.save()
    return JsonResponse({'message': 'Friend request accepted'}, status=200)


@csrf_exempt
@require_POST
def reject_friend_request(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)

    # request_id = request.POST.get('request_id')
    data = json.loads(request.body)
    # data = request.data
    request_id = data['request_id']

    if not request_id:
        return JsonResponse({'error': 'request_id is required'}, status=400)

    try:
        friend_request = FriendRequest.objects.get(to_user=request_id)
    except FriendRequest.DoesNotExist:
        return JsonResponse({'error': 'Friend request does not exist'}, status=404)

    if friend_request.to_user == request.user.username:
        return JsonResponse({'error': 'This friend request is not for you'}, status=400)

    friend_request.status = 'rejected'
    friend_request.save()
    return JsonResponse({'message': 'Friend request rejected'}, status=200)

@csrf_exempt
def list_friends(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)

    username = request.user.username

    # Find accepted friend requests where the user is either the sender or receiver
    accepted_requests = FriendRequest.objects.filter(
        (models.Q(from_user=username) | models.Q(to_user=username)) & models.Q(status='accepted')
    )

    friends = set()
    for req in accepted_requests:
        if req.from_user == username:
            friends.add(req.to_user)
        else:
            friends.add(req.from_user)

    return JsonResponse({'friends': list(friends)}, status=200)

@csrf_exempt
# @require_GET
def list_pending_requests(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)

    username = request.user.username

    # Find pending friend requests where the user is the recipient
    pending_requests = FriendRequest.objects.filter(to_user=username, status='pending')

    requests = [
        {
            'id': req.id,
            'from_user': req.from_user,
            'created_at': req.created_at
        }
        for req in pending_requests
    ]

    return JsonResponse({'pending_requests': requests}, status=200)


@csrf_exempt
#@api_view(['POST'])
def logout(request):
    final_json = {"status": False, "message": "Failed to logout"}
    try:
        auth.logout(request)
        final_json["status"] = True
        final_json["message"] = "Logged out"
    except Exception as e:
        logger.exception("Error while logging out: {}".format(e))
    return JsonResponse(final_json)
