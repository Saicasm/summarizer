from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain.chains import LLMChain
from django.conf import settings

class LLMService:
    def __init__(self):
        self.llm = ChatOpenAI(api_key=settings.OPENAI_API_KEY, model="gpt-4o-mini")
        self.search_tool = TavilySearchResults(api_key=settings.TAVILY_API_KEY, max_results=5)

    def process_query(self, query, use_web_search=False):
        if use_web_search:
            web_results = self.search_tool.invoke(query)
            web_content = "\n".join([result['content'] for result in web_results])
            prompt = PromptTemplate(
                input_variables=["query", "web_content"],
                template="User query: {query}\nWeb results: {web_content}\nSummarize the web results concisely and explain in simple terms."
            )
            chain = LLMChain(llm=self.llm, prompt=prompt)
            return chain.run(query=query, web_content=web_content)
        else:
            prompt = PromptTemplate(
                input_variables=["query"],
                template="Summarize the following query concisely: {query}"
            )
            chain = LLMChain(llm=self.llm, prompt=prompt)
            return chain.run(query=query)