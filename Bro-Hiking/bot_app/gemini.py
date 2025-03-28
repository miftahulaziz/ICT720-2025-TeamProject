from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage, AIMessage
import os

class Assistance():
    def __init__(self):
        # Set up the LLM model
        self.llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", api_key=os.getenv("API_KEY"))

    # Function to Interact with Gemini
    def prompt(self, user_input, context_json):
        # Construct prompt with context
        prompt = f"""
            Now, answer the following question based on the JSON data:
            {user_input}
            Do not give JSON data in the answer.

            Here is the info about the tracking with Blutooth Low Energy (BLE) technology.
            {context_json}

            JSON data contains the following fields:
            "asset" is the asset ID
            "status" is the status of query operation
            "data" is the record of observations containing the following three fields:
                "timestamp" is the time of observation
                "rssi" is the received signal strength indicator, bigger is closer to the station
                "station" is the id of BLE station that made the observation
        """
        response = self.llm.invoke([HumanMessage(content=prompt)])
        return response