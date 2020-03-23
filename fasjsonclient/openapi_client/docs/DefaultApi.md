# openapi_client.DefaultApi

All URIs are relative to *http://fasjson.example.test/fasjson*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_group_members**](DefaultApi.md#get_group_members) | **GET** /v1/groups/{group_name}/members | 
[**get_user_info**](DefaultApi.md#get_user_info) | **GET** /v1/users/{username} | 
[**query_groups**](DefaultApi.md#query_groups) | **GET** /v1/groups | 
[**whoami**](DefaultApi.md#whoami) | **GET** /v1/me | 


# **get_group_members**
> InlineResponse2002 get_group_members(group_name)



### Example

* Api Key Authentication (default):
```python
from __future__ import print_function
import time
import openapi_client
from openapi_client.rest import ApiException
from pprint import pprint
configuration = openapi_client.Configuration()
# Configure API key authorization: default
configuration.api_key['Authorization'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['Authorization'] = 'Bearer'

# Defining host is optional and default to http://fasjson.example.test/fasjson
configuration.host = "http://fasjson.example.test/fasjson"
# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.DefaultApi(api_client)
    group_name = 'group_name_example' # str | 

    try:
        api_response = api_instance.get_group_members(group_name)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling DefaultApi->get_group_members: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **group_name** | **str**|  | 

### Return type

[**InlineResponse2002**](InlineResponse2002.md)

### Authorization

[default](../README.md#default)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | list members of a given group returning the uid user field |  -  |
**0** | unexpected error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_user_info**
> InlineResponse2003 get_user_info(username)



### Example

* Api Key Authentication (default):
```python
from __future__ import print_function
import time
import openapi_client
from openapi_client.rest import ApiException
from pprint import pprint
configuration = openapi_client.Configuration()
# Configure API key authorization: default
configuration.api_key['Authorization'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['Authorization'] = 'Bearer'

# Defining host is optional and default to http://fasjson.example.test/fasjson
configuration.host = "http://fasjson.example.test/fasjson"
# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.DefaultApi(api_client)
    username = 'username_example' # str | 

    try:
        api_response = api_instance.get_user_info(username)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling DefaultApi->get_user_info: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **username** | **str**|  | 

### Return type

[**InlineResponse2003**](InlineResponse2003.md)

### Authorization

[default](../README.md#default)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | retrieve user information |  -  |
**0** | unexpected error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **query_groups**
> InlineResponse2001 query_groups(query=query, page=page, per_page=per_page)



### Example

* Api Key Authentication (default):
```python
from __future__ import print_function
import time
import openapi_client
from openapi_client.rest import ApiException
from pprint import pprint
configuration = openapi_client.Configuration()
# Configure API key authorization: default
configuration.api_key['Authorization'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['Authorization'] = 'Bearer'

# Defining host is optional and default to http://fasjson.example.test/fasjson
configuration.host = "http://fasjson.example.test/fasjson"
# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.DefaultApi(api_client)
    query = 'query_example' # str |  (optional)
page = 0 # int |  (optional) (default to 0)
per_page = 10 # int |  (optional) (default to 10)

    try:
        api_response = api_instance.query_groups(query=query, page=page, per_page=per_page)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling DefaultApi->query_groups: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **query** | **str**|  | [optional] 
 **page** | **int**|  | [optional] [default to 0]
 **per_page** | **int**|  | [optional] [default to 10]

### Return type

[**InlineResponse2001**](InlineResponse2001.md)

### Authorization

[default](../README.md#default)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | list groups retutning its CN field |  -  |
**0** | unexpected error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **whoami**
> InlineResponse200 whoami()



### Example

* Api Key Authentication (default):
```python
from __future__ import print_function
import time
import openapi_client
from openapi_client.rest import ApiException
from pprint import pprint
configuration = openapi_client.Configuration()
# Configure API key authorization: default
configuration.api_key['Authorization'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['Authorization'] = 'Bearer'

# Defining host is optional and default to http://fasjson.example.test/fasjson
configuration.host = "http://fasjson.example.test/fasjson"
# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.DefaultApi(api_client)
    
    try:
        api_response = api_instance.whoami()
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling DefaultApi->whoami: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**InlineResponse200**](InlineResponse200.md)

### Authorization

[default](../README.md#default)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | requester identity info |  -  |
**0** | unexpected error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

