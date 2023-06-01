from typing import Any, Callable, Optional, Type

from pydantic import BaseModel, validator

from langflow.utils import validate

from langchain.tools import Tool, BaseTool

from langchain.callbacks.manager import AsyncCallbackManagerForToolRun, CallbackManagerForToolRun

class Function(BaseModel):
    code: str
    function: Optional[Callable] = None
    imports: Optional[str] = None

    # Eval code and store the function
    def __init__(self, **data):
        super().__init__(**data)

    # Validate the function
    @validator("code")
    def validate_func(cls, v):
        try:
            validate.eval_function(v)
        except Exception as e:
            raise e

        return v

    def get_function(self):
        """Get the function"""
        function_name = validate.extract_function_name(self.code)

        return validate.create_function(self.code, function_name)


class PythonFunction(Function):
    """Python function"""

    code: str
       

class KnowySearchTool(BaseTool, BaseModel):
    name = "Knowy Search"
    description:str
    user_token:str

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def _run(self, query: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        """Use the tool."""
        from requests import get, post

        res = get('https://devapi.knowy.ai/search/search', 
            params={ 
                'query': query
            },
            headers={
            'Authorization': f'Bearer {self.user_token}'
        })
        query_result = res.json()
        data = post('https://devapi.knowy.ai/content/getKnowledgeItems', 
            json={ 
                'ids': query_result, 
                'properties': ['title', 'id'] 
            },
            headers={
            'Authorization': f'Bearer {self.user_token}'
        })
        return data.json()
    
    async def _arun(self, query: str, run_manager: Optional[AsyncCallbackManagerForToolRun] = None) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError("custom_search does not support async")
    
    
import re

def extract_uuids(input_str):
    uuid_pattern = re.compile(r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b', re.IGNORECASE)
    return uuid_pattern.findall(input_str)

class KnowyItemInfoGetterTool(BaseTool, BaseModel):
    name = "Knowy Item Info Getter"
    description:str
    user_token:str
    properties:str

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def _run(self, id_string: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        """Use the tool."""
        from requests import post
        uuids = extract_uuids(id_string)
        if len(uuids) == 0:
            return "No valid uuids provided"
        data = post('https://devapi.knowy.ai/content/getKnowledgeItems', 
            json={ 
                'ids': uuids, 
                'properties': [property.strip() for property in self.properties.split(',')]
            },
            headers={
            'Authorization': f'Bearer {self.user_token}'
        })
        return data.json()
    
    async def _arun(self, query: str, run_manager: Optional[AsyncCallbackManagerForToolRun] = None) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError("custom_search does not support async")