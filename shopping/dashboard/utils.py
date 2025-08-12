from django.apps import apps
from shopping.dashboard.api.serializers import DashboardOrderListSerializer


def get_app_model(app_model: str):
    """
    Parses a model identifier in the format 'app_name:model_name'.

    The string is expected to contain the Django app label and the model
    name, separated by a colon. This method extracts and returns both
    components for further processing.
    """
    try:
        app_name, model_name = app_model.strip().split(":")
        return app_name, model_name
    except Exception as e:
        return e, None


def get_model_data(model_name):
    models = {
        "order": {
            "serializers": {
                "list": DashboardOrderListSerializer,
                "details": "DashboardOrderListSerializer",
            }
        }
    }
    return models.get(model_name, None)


def get_model_properties(app_model, method=None):
    """
    Retrieves a Django model class from a string identifier in the format 'app_name:model_name'.

    Args:
        app_model (str): The model identifier, consisting of the Django app label
                         and model name separated by a colon (e.g., 'auth:User').

    Returns:
        ModelBase | None: The Django model class if found, otherwise None.

    Notes:
        - This function uses `get_app_model` to parse the identifier and `apps.get_model`
          to retrieve the model.
        - If the specified app or model does not exist, it returns None instead of raising an error.
    """
    try:
        app_name, model_name = get_app_model(app_model)
        serializers = get_model_data(model_name)["serializers"].get(method, None)
        print()
        return apps.get_model(app_name, model_name), DashboardOrderListSerializer
    except LookupError:
        return None
