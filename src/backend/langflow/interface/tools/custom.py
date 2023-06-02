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
    search_source:str

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def _run(self, query: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        """Use the tool."""
        from requests import get, post

        search_source = self.search_source
        headers = {
            'Authorization': f'Bearer {self.user_token}'
        }
        
        if search_source=="document_chunks":
            url = 'https://devapi.knowy.ai/user_content/search'
            response = get(url, headers=headers, params={'query': query})
            chunk_ids = list(set([p['metadata']['id'] for p in response.json()]))

        elif search_source=="documents":
            url = 'https://devapi.knowy.ai/user_content/search'
            response = get(url, headers=headers, params={'query': query})
            chunk_ids = list(set([p['metadata']['file_id'] for p in response.json()]))

        elif search_source=="knowy":
            url = 'https://devapi.knowy.ai/search/search'
            response = get(url, headers=headers, params={'query': query})
            chunk_ids = list(set([id for id in response.json()]))

        elif search_source=="knowy_sections":
            url = 'https://devapi.knowy.ai/search/search'
            response = get(url, headers=headers, params={'query': query, 'type': 'section'})
            chunk_ids = list(set([id for id in response.json()]))

        elif search_source=="web":
            url = 'https://devapi.knowy.ai/search/search'
            response = get(url, headers=headers, params={'query': query, 'type': 'web'})
            chunk_ids = list(set([id for id in response.json()]))

        data = post('https://devapi.knowy.ai/content/getKnowledgeItems', 
            json={ 
                'ids': chunk_ids, 
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