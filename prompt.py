class VerticalPrompt:
    def __init__(self):
        pass
    
    def get_prompt(self, client_name,client_description,website_content=None):
        user_input = f"""
    Identify the primary business domain for the following client:
    Client Name: {client_name}
        Client Description: {client_description}
        Website Content: {website_content if website_content else 'No website content available'}

    Based on this information, classify the client into one of the following business domains:
        - List your predefined business domains here, e.g., Healthcare, Finance, Retail, Manufacturing, Technology, Education, etc.
        
        Provide the following in your response in JSON format:
    
            "domain_name": "Identified Business Domain Name",
            "domain_description": "A brief description of the identified domain based on the client info",
            "keywords": "list", "of", "relevant", "keywords",  
            "confidence_score": 0.95; Confidence score between 0.0 and 1.0
    
        If you cannot confidently classify the domain, return null or an empty JSON.
"""
        return user_input
    

