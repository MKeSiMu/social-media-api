from django.urls import path

from user.views import UserCreateView, ManageUserView

urlpatterns = [
    path("register/", UserCreateView.as_view(), name="create"),
    path("profile/", ManageUserView.as_view(), name="manage"),
]

app_name = "user"
