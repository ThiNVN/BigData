from dotenv import load_dotenv
from google.genai import types
from google import genai
import os
load_dotenv('api.env')
api_key = os.environ.get('gemini_api_key')
genai_client =genai.Client(api_key=api_key)

class LLMResponse:
    def __init__(self, gemini_api_key):
        self.client = genai.Client(api_key=gemini_api_key)
    def get_function_call(self,user_query):
        function_calling = [
            {
                "name": "direct_search",
                "description": "Direct search for games name, publisher, or developer based on user query",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "game_name": {
                            "type": "string",
                            "description": "Game name that user is looking for, None if not applicable"
                        }
                    },
                    "required": []
                }
            },
            {
                "name": "filter_search",
                "description": "Search games based on description and apply filters like year range, price, cluster of games, age, platform, currency extracted from user query. IMPORTANT: If genres or category is not mentioned, but related, then apply it to game description",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "game_description": {
                            "type": "string",
                            "description": "Game description from user query (e.g., football tactical game), None if not applicable"
                        },
                        "developer": {
                            "type": "string",
                            "description": "Developer name from user if mentioned,None if not applicable"
                        },
                        "publisher": {
                            "type": "string",
                            "description": "Publisher name from user if mentioned,None if not applicable"
                        },
                        "year_range": {
                            "type": "string",
                            "description": "Current year is 2025. E.g 'from 2022' then return the year range for the game release '2022-2025' or 'from 2022 to 2024' then return '2022-2024' or a specific year if mentioned '2022' ,None if not applicable"
                        },
                        "price_limit": {
                            "type": "string",
                            "description": "Price limit for the game (e.g., 0 for free games, 20 for games under $20),None if not applicable"
                        },
                        "genre": {
                            "type": "string",
                            "description": "Genre of the game if only the genre is mentioned in the user query (e.g., Action, Adventure, Simulation, etc.),If not mentioned, return 'None'"
                        },
                         "category": {
                            "type": "string",
                            "description": "Category of the game if only the category is mentioned in the user query (e.g., Multiplayer, Single-player, etc.),None if not applicable"
                        },
                        "language": {
                            "type": "string",
                            "description": "Language supported for the game (e.g., English,..),None if not applicable"
                        },
                        "age_limit": {
                            "type": "string",
                            "description": "Age required for the game (e.g., 0, 13, 17),None if not applicable"
                        },
                        "platform": {
                            "type": "string",
                            "description": "Platform for the game (e.g., Windows, Mac, Linux),None if not applicable"
                        },
                        "currency": {
                            "type": "string",
                            "description": "Currency for the game price (e.g., USD, VND), None if not applicable"
                        }
                    },
                    "required": []
                }
            },
            {
                "name": "chit_chat",
                "description": "Chit chat message of users",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "User input message that is common chit-chat"
                        }
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "end_chat",
                "description": "End chat session",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "End the chat session and further information if needed"
                        }
                    },
                    "required": ["query"]
                }
            }
        ]
        
        tools = types.Tool(function_declarations=function_calling)
        config = types.GenerateContentConfig(tools=[tools])

        response = self.client.models.generate_content(
            model="gemini-2.0-flash",
            contents=user_query,
            config=config,
        )
        candidate = response.candidates[0]
        if candidate.content.parts and candidate.content.parts[0].function_call:
            function_call = candidate.content.parts[0].function_call
            print(f"Function to call: {function_call.name}")
            print(f"Arguments: {function_call.args}")

            if function_call.name=="direct_search":
                result={
                    "function_name": function_call.name,
                    "game_name": function_call.args.get("game_name"),
                }
                return result
            elif function_call.name=="filter_search":
                result={
                    "function_name": function_call.name,
                    "game_description": function_call.args.get("game_description"),
                    "developer": function_call.args.get("developer"),
                    "publisher": function_call.args.get("publisher"),
                    "year_range": function_call.args.get("year_range"),
                    "price_limit": function_call.args.get("price_limit"),
                    "price_above": function_call.args.get("price_above"),
                    "genre": function_call.args.get("genre"),   
                    "category": function_call.args.get("category"),
                    "language": function_call.args.get("language"),
                    "age_limit": function_call.args.get("age_limit"),
                    "platform": function_call.args.get("platform"),
                    "currency": function_call.args.get("currency")
                }
                return result
            elif function_call.name == "chit_chat":
                chit_chat_response = self.client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=function_call.args["query"],
                )
                result={
                    "function_name": function_call.name,
                    "response": chit_chat_response.text
                }
                return result
            else:
                end_response = self.client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=function_call.args["query"],
                )
                result={
                    "function_name": function_call.name,
                    "response": end_response.text
                }
                return result
        return None
    def get_reflection(self, query_history,new_query):

        prompt = f"""
        You are a system designed to reformulate user messages into standalone game queries. Be friendly and concise. Your task is to determine if the latest user message depends on prior context.
        Given the following chat history and the latest user message, determine if the latest message depends on prior context. If it does, rewrite it into a standalone game query. If it is already standalone or the chat history is empty, return the original message without any additional text.
        Chat History:
        {query_history}
        New prompt:
        {new_query}
        Return only the rewritten message or the original message. Do not include any explanations, recommendations, or additional text.
        """
        response = self.client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )
        return response.text

