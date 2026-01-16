from crewai.tools import BaseTool
from typing import Type, Any
from pydantic import BaseModel, Field
import os
import requests

class PushNotificationInput(BaseModel):
    """A message to be sent to the user"""
    message: str = Field(..., description="The message to be sent to the user")

class PushNotificationTool(BaseTool):
    name: str = "Send a push notification"
    description: str = "This tool will send a push notification to the user"
    args_schema: Type[BaseModel] = PushNotificationInput

    def _run(self, message: str) -> str:
        pushover_user =

