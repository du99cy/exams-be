
from fastapi_mail import MessageSchema,FastMail

from core.database.mongodb import get_collection_client

from core.constants import TEMPLATE_EMAIL,EMAIL_CONFIG
from core.helpers_func import responseModel
from pydantic import EmailStr



class SendEmail():
    def __init__(self,template:str,email_reciever:str):
        self.template = template
        self.email_reciever = email_reciever
    
    async def send(self) :
        
        message = MessageSchema(
            subject="AIAcademy",
            recipients=[self.email_reciever],  # List of recipients, as many as you can pass
            html=self.template,
            subtype="html"
        )
        
        fm = FastMail(EMAIL_CONFIG)
        await fm.send_message(message)
        
        return responseModel(message="email has been sent")
