from django.urls import path
from shopping.dashboard.api.views import DashboardTableAPI


app_name = "dashboard"
urlpatterns = [path("v1/model-list/", DashboardTableAPI.as_view(), name="model_list")]
