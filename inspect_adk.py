from google.adk.cli.fast_api import get_fast_api_app
from google.adk.api_server import create_api_server
import inspect

print("get_fast_api_app signature:", inspect.signature(get_fast_api_app))
print("create_api_server signature:", inspect.signature(create_api_server))
