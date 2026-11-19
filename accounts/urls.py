from django.urls import path

from .views import logout_confirm, profile_view, sign_up, user_login, user_logout

urlpatterns = [
    path('signup/', sign_up, name='sign_up'),
    path('login/', user_login, name='login'),
    path('logout/confirm/', logout_confirm, name='logout_confirm'),
    path('logout/', user_logout, name='logout'),
    path('profile/', profile_view, name='profile'),
]
