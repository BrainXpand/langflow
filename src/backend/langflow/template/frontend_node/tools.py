from langflow.template.field.base import TemplateField
from langflow.template.frontend_node.base import FrontendNode
from langflow.template.template.base import Template
from langflow.utils.constants import DEFAULT_PYTHON_FUNCTION


class ToolNode(FrontendNode):
    name: str = "Tool"
    template: Template = Template(
        type_name="Tool",
        fields=[
            TemplateField(
                field_type="str",
                required=True,
                placeholder="",
                is_list=False,
                show=True,
                multiline=True,
                value="",
                name="name",
                advanced=False,
            ),
            TemplateField(
                field_type="str",
                required=True,
                placeholder="",
                is_list=False,
                show=True,
                multiline=True,
                value="",
                name="description",
                advanced=False,
            ),
            TemplateField(
                name="func",
                field_type="function",
                required=True,
                is_list=False,
                show=True,
                multiline=True,
                advanced=False,
            ),
            TemplateField(
                field_type="bool",
                required=True,
                placeholder="",
                is_list=False,
                show=True,
                multiline=False,
                value=False,
                name="return_direct",
            ),
        ],
    )
    description: str = "Tool to be used in the flow."
    base_classes: list[str] = ["Tool"]

    def to_dict(self):
        return super().to_dict()


class PythonFunctionNode(FrontendNode):
    name: str = "PythonFunction"
    template: Template = Template(
        type_name="python_function",
        fields=[
            TemplateField(
                field_type="code",
                required=True,
                placeholder="",
                is_list=False,
                show=True,
                value=DEFAULT_PYTHON_FUNCTION,
                name="code",
                advanced=False,
            )
        ],
    )
    description: str = "Python function to be executed."
    base_classes: list[str] = ["function"]

    def to_dict(self):
        return super().to_dict()

        

class KnowySearchToolNode(FrontendNode):
    name: str = "KnowySearchTool"
    template: Template = Template(
        type_name="KnowySearchTool",
        fields=[
            TemplateField(
                field_type="str",
                required=True,
                placeholder="",
                is_list=False,
                show=True,
                multiline=True,
                value="",
                name="user_token",
                advanced=False,
            ),
            TemplateField(
                field_type="str",
                required=True,
                is_list=True,
                show=True,
                multiline=False,
                options=["knowy", "knowy_sections", "document_chunks", "documents", "web"],
                value="knowy",
                name="search_source",
                advanced=False,
            ),
            TemplateField(
                field_type="str",
                required=True,
                placeholder="",
                is_list=False,
                show=True,
                multiline=True,
                value="This tool searches the Knowy knowledge base and returns a list of title, id pairs. The input query should be the title of a wikipedia page.",
                name="description",
                advanced=False,
            )
        ],
    )
    description: str = "Search the Knowy knowledge base."
    base_classes: list[str] = ["Tool"]

    def to_dict(self):
        return super().to_dict()
    

class KnowyItemInfoGetterToolNode(FrontendNode):
    name: str = "KnowyItemInfoGetterTool"
    template: Template = Template(
        type_name="KnowyItemInfoGetterTool",
        fields=[
            TemplateField(
                field_type="str",
                required=True,
                placeholder="",
                is_list=False,
                show=True,
                multiline=True,
                value="",
                name="user_token",
                advanced=False,
            ),
            TemplateField(
                field_type="str",
                required=True,
                placeholder="",
                is_list=False,
                show=True,
                multiline=True,
                value="This tool gets the properties of a Knowy item, specified by the item id. The input should be the id and nothing else.",
                name="description",
                advanced=False,
            ),
            TemplateField(
                field_type="str",
                required=True,
                placeholder="",
                is_list=False,
                show=True,
                multiline=True,
                value="plainContent",
                name="properties",
                advanced=False,
            )
        ],
    )
    description: str = "Get Knowy item info."
    base_classes: list[str] = ["Tool"]

    def to_dict(self):
        return super().to_dict()