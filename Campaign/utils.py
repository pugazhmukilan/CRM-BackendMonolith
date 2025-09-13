from .models import EmailContentModel
from db import customers_col
from langchain_google_genai import GoogleGenerativeAI
import os
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAI
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
llm = GoogleGenerativeAI(model="gemini-1.5-pro-latest", api_key=GOOGLE_API_KEY)
load_dotenv()

def generatecontentformail(mailids):
    print("inside the inside the generatecontentformail function")
    try:
        customers = customers_col.find({"email": {"$in": mailids['customers']}})

        mailids = [customer['email'] for customer in customers]
        sub = "Special Offer Just for You!"
        content = []
        for email,cust_info in zip(mailids,customers):
            body= CreateBody(cust_info)
            print("created body")
            content.append(body)

            print(f"Generated email for {email}:\nSubject: {sub}\nBody: {body}\n")
        
        return EmailContentModel(users=mailids, content=content)
    except Exception as e:
        print("Error generating email content:", e)
        return EmailContentModel(users=[], content=[])

    
def CreateBody(cust_info:dict):
    

    ## use the geimingeneration model api to generate boys based on the xutomer info make the content samll
    prompt = f"Create a personalized discount email body for a customer with the following details keep the email very short: \n\n {cust_info}\n\nThe email should be engaging and encourage the customer to check out our latest products and offers. Keep it concise and friendly."
    return llm.invoke(prompt)


if __name__ == "__main__":
    print(CreateBody({"name": "John Doe", "age": 30, "location": "New York"}))