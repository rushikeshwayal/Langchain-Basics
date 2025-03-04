from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.schema.output_parser import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain.agents import tool
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.output_parsers import StrOutputParser
from langchain.agents import initialize_agent,Tool
from langchain.agents import AgentType
from langchain_community.utilities import SerpAPIWrapper
import requests
from bs4 import BeautifulSoup
import re


load_dotenv()


def extract_text_from_url(url: str, max_length: int = 5000) -> str:
        """
        fetches the content of a web page.
        Extracts HTML from a URL and returns clean text for LLM processing.
        
        Parameters:
            url (str): The URL to scrape and extract text from.
            max_length (int): Maximum character length for the output text (default: 2000).
            
        Returns:
            str: Cleaned text extracted from the HTML content.
        """
        try:
            # Step 1: Fetch HTML content from the URL
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()  # Raise an error for bad status codes

            # Step 2: Parse HTML with BeautifulSoup
            soup = BeautifulSoup(response.content, 'html.parser')

            # Step 3: Extract text from relevant tags
            tags = ['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li', 'div']
            elements = soup.find_all(tags)
            text_parts = [element.get_text(' ', strip=True) for element in elements]

            # Step 4: Combine and clean text
            clean_text = ' '.join(text_parts)
            clean_text = re.sub(r'\s+', ' ', clean_text).strip()  # Remove excessive whitespace

            # Step 5: Truncate to max length while preserving whole words
            if len(clean_text) > max_length:
                clean_text = clean_text[:max_length].rsplit(' ', 1)[0] + '...'

            return clean_text if clean_text else "No readable text found in the HTML content."

        except requests.RequestException as e:
            return f"Failed to fetch URL: {str(e)}"
        except Exception as e:
            return f"Error processing HTML: {str(e)}"

class WebScrap:
    def __init__(self):
        print("Web Scrap Agent Initialized✅")
        self.models = {
            "google": ChatGoogleGenerativeAI,
            "openai": ChatOpenAI
        }
        self.output_parser = {
            "str": StrOutputParser,
            "json": JsonOutputParser,
            "pydantic": PydanticOutputParser
        }
    

    def invoke_web_scraping(self, webcontent, model_name, model_variant, verbose=False, output_parser="str"):
        if model_name not in self.models:
            raise ValueError(f"Invalid model '{model_name}'. Available models: {list(self.models.keys())}")

        # defining llm model
        llm = self.models[model_name](model=model_variant)

        # web_scrap_tool = self.web_scrap_tool()  # Now correctly referenced as an instance method
        # tools = [web_scrap_tool]

        prompt_template = ChatPromptTemplate.from_messages([
            ("system", "You're a helpful AI assistant that give meaningfull context to a text and info to it what domain is about "),
            ("user", """
            *Task*:  Below text is a extracted text from web page return the important information about the web page's business domain.
            content: {webcontent}
            ***Instructions***:
            - Extract the relevant information about the business domain from the scraped content.
            - If you dont get content, return "No info available".

            Output: If the content is not provided, return "No info available".
            """)
        ])

        formatted_prompt = prompt_template.invoke({"webcontent": webcontent})

        response =  llm.invoke(formatted_prompt)
        content = response.content


        return content







class CustomAgent:

    def __init__(self,):
        print("Vertical Agent Initialized✅")
        self.models = {
            "google": ChatGoogleGenerativeAI,
            "openai": ChatOpenAI
        }
        self.output_parser = {
            "str": StrOutputParser,
            "json": JsonOutputParser,
            "pydantic": PydanticOutputParser
        }


    # Set Up Web Search Tool using SerpAPI
    def websearch(self):
        serpapi = SerpAPIWrapper()
        web_search_tool = Tool(
                name="WebSearch",
                func=serpapi.run,
                description="This tool allows the agent to perform real-time web searches to retrieve relevant and up-to-date information from the internet. It is useful for answering queries that require external knowledge or the latest data."
            )
        return web_search_tool
    
    
    def invoke_agent(self,system_input,user_input,model_name,model_variant,verbose=False,output_parser="str"):
        if model_name not in self.models:
            raise ValueError(f"Invalid model '{model_name}'. Available models: {list(self.models.keys())}")
        
        # defining llm model
        llm = self.models[model_name](model=model_variant)

        # propmt template
        prompt_template = ChatPromptTemplate([
        ("system", system_input),
        ("user", user_input)
        ])
        # tool
        web_search_tool = self.websearch()
        tools = [web_search_tool]

        # ✅ Initialize the Agent
        agent = initialize_agent(
            tools=tools,
            llm=llm,
            agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            verbose=verbose
        )

        # formating prompt
        formated_prompt=prompt_template.invoke({})

        # generating responce
        content = agent.run(formated_prompt)

        # Initialize output parser
        output_parser = self.output_parser[output_parser]

        # parsing output by llm to get the final responce
        parsed_output = output_parser().parse(content)

        return parsed_output


    def model_list(self):
        return list(self.models.keys())
    
    def output_parser_list(self):
        return list(self.output_parser.keys())
    