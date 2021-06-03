from django.contrib.auth.forms import PasswordResetForm
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import login, authenticate, logout
from django.conf import settings
from account.forms import RegistrationForm, AccountAuthenticationForm
from .models import Account

def register_view(request, *args, **kwargs):
	user = request.user
	if user.is_authenticated:
		return HttpResponse(f"You are already authenticated as {user.email}.")
	context = {}

	if request.POST:
		form = RegistrationForm(request.POST)
		if form.is_valid():
			form.save()
			email = form.cleaned_data.get('email').lower()
			raw_password = form.cleaned_data.get('password1')
			account = authenticate(email=email, password=raw_password)
			login(request, account)
			destination = get_redirect_if_exists(request)
			if destination:
				return redirect(destination)
			return redirect("home")

		else:
			context['registration_form'] = form

	return render(request, 'account/register.html', context)

def logout_view(request):
	logout(request)
	return redirect("home")

def login_view(request, *args, **kwargs):
	context = {}
	user = request.user
	if user.is_authenticated:
		return redirect("home")

	
	if request.POST:
		form = AccountAuthenticationForm(request.POST)
		if form.is_valid():

			email = request.POST['email']
			password = request.POST['password']
			user = authenticate(email=email, password=password)
			if user:
				login(request, user)
				destination = get_redirect_if_exists(request)
				if destination:
					return redirect(destination)
				return redirect("home")

		else:
			context['login_form'] = form

	return render(request, "account/login.html", context)

def get_redirect_if_exists(request):
	redirect = None
	if request.GET:
		if request.GET.get("next"):
			redirect = str(request.GET.get("next"))
	return redirect




def account_view(request, *args, **kwargs):
	"""
	- Logic here is kind of tricky
		is_self
		is_friend
			-1: NO_REQUEST_SENT
			0: THEM_SENT_TO_YOU
			1: YOU_SENT_TO_THEM
	"""
	context = {}
	user_id = kwargs.get("user_id")
	try:
		account = Account.objects.get(pk=user_id)
	except Account.DoesNotExist:
		return HttpResponse("Something went wrong.")
	if account:
		context['id'] = account.id
		context['username'] = account.username
		context['email'] = account.email
		context['profile_image'] = account.profile_image.url
		context['hide_email'] = account.hide_email

		# try:
		# 	friend_list = FriendList.objects.get(user=account)
		# except FriendList.DoesNotExist:
		# 	friend_list = FriendList(user=account)
		# 	friend_list.save()
		# friends = friend_list.friends.all()
		# context['friends'] = friends
	
		# Define template variables
		is_self = True
		is_friend = False
		# request_sent = FriendRequestStatus.NO_REQUEST_SENT.value # range: ENUM -> friend/friend_request_status.FriendRequestStatus
		# friend_requests = None
		user = request.user
		if user.is_authenticated and user != account:
			is_self = False
		
		elif not user.is_authenticated:
			is_self = False

		# 	if friends.filter(pk=user.id):
		# 		is_friend = True
		# 	else:
		# 		is_friend = False
		# 		# CASE1: Request has been sent from THEM to YOU: FriendRequestStatus.THEM_SENT_TO_YOU
		# 		if get_friend_request_or_false(sender=account, receiver=user) != False:
		# 			request_sent = FriendRequestStatus.THEM_SENT_TO_YOU.value
		# 			context['pending_friend_request_id'] = get_friend_request_or_false(sender=account, receiver=user).id
		# 		# CASE2: Request has been sent from YOU to THEM: FriendRequestStatus.YOU_SENT_TO_THEM
		# 		elif get_friend_request_or_false(sender=user, receiver=account) != False:
		# 			request_sent = FriendRequestStatus.YOU_SENT_TO_THEM.value
		# 		# CASE3: No request sent from YOU or THEM: FriendRequestStatus.NO_REQUEST_SENT
		# 		else:
		# 			request_sent = FriendRequestStatus.NO_REQUEST_SENT.value
		
		# elif not user.is_authenticated:
		# 	is_self = False
		# else:
		# 	try:
		# 		friend_requests = FriendRequest.objects.filter(receiver=user, is_active=True)
		# 	except:
		# 		pass
			
		# Set the template variables to the values
		context['is_self'] = is_self
		context['is_friend'] = is_friend
		# context['request_sent'] = request_sent
		# context['friend_requests'] = friend_requests
		context['BASE_URL'] = settings.BASE_URL
		return render(request, "account/account.html", context)


# This is basically almost exactly the same as friends/friend_list_view
def account_search_view(request, *args, **kwargs):
	context = {}
	if request.method == "GET":
		search_query = request.GET.get("q")
		if len(search_query) > 0:
			search_results = Account.objects.filter(email__icontains=search_query).filter(username__icontains=search_query).distinct()
			user = request.user
			accounts = [] # [(account1, True), (account2, False), ...]
			
			for account in search_results:
				accounts.append((account, False))
			context['accounts'] = accounts
			
	return render(request, "account/search_results.html", context)