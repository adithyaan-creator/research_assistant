import time
import json

from llm_prompts import QUERY_GENERATOR_SYSTEM_PROMPT, QUERY_GENERATION_FUNCTION_SCHEMA, \
                        REFINE_SEARCH_SYSTEM_PROMPT, create_refine_search_results_user_prompt, \
                        LESSON_PLAN_SYSTEM_PROMPT, create_lesson_plan_user_prompt, LESSON_PLAN_FUNCTION_SCHEMA
from services.llm_service import OpenAIService
from common import ClientType
from llm_prompts import create_query_generator_user_prompt
from services.scraper import query_result_retriever


class ResearcherService:
    def __init__(self):
        self.openai_instance = OpenAIService()

    def generate_queries(self, query_count, topic, client_type=ClientType.AZURE):
        print(f"Generating queries for {topic}")
        user_prompt = create_query_generator_user_prompt(query_count, topic)
        print(user_prompt)
        
        query_result = self.openai_instance.call_openai_toolcall(
            QUERY_GENERATOR_SYSTEM_PROMPT, 
            user_prompt, 
            QUERY_GENERATION_FUNCTION_SCHEMA,
            client_type=client_type
            )
        
        if len(query_result['queries']) != query_count:
            print(f"Query generator returned {len(query_result['queries'])} queries, expected {query_count}. Retrying...")
            return self.generate_queries(query_count, topic, client_type)
        
        return query_result['queries'], query_result['sub_topics']
    
    def refine_search_results(self, query, search_result):
        refine_user_prompt = create_refine_search_results_user_prompt(query, search_result)
        message_history = [{"role": "system","content": REFINE_SEARCH_SYSTEM_PROMPT},
                        {"role": "user","content": refine_user_prompt}]
        refined_result = self.openai_instance.call_chat_openai(message_history, client_type=ClientType.AZURE)
        return refined_result
    
    def create_lesson_plan(self, module, modules, research_data):
        lesson_plan_user_prompt = create_lesson_plan_user_prompt(module, modules, research_data)

        lesson_plan_result = self.openai_instance.call_openai_toolcall(
                LESSON_PLAN_SYSTEM_PROMPT, 
                lesson_plan_user_prompt, 
                LESSON_PLAN_FUNCTION_SCHEMA,
                )
        
        return lesson_plan_result
    
    def research(self, query):
        queries, topics = self.generate_queries(5, query)

        query_search_results = {}
        for query in queries:
            print(f"Researching on :: {query['query']}")
            retrieved_out = query_result_retriever(query['query'])
            query_search_results[f"{query['query']}"] = retrieved_out
        print(f"\nSearch retrieval complete complete\n")
        
        print("\n\nRefining results\n-----------------------------------------\n")
        all_refined_results = []
        for query, search_result in query_search_results.items():
            querywise_refined_result = {"query":query, "results":[]}
            for src_rslt in search_result:
                if src_rslt['markdown'] != "":
                    print(f"Refining :: {src_rslt['url']}")
                    refined_result = self.refine_search_results(query, "".join(src_rslt['markdown'].split()[:6000]))
                    querywise_refined_result['results'].append({
                        "url":src_rslt['url'],
                        "refined_out":refined_result
                    })
                    print("-------------------------------")
            all_refined_results.append(querywise_refined_result)
        print(f"Refining complete")
        return all_refined_results 
    
    def generate_lesson_plan(self, uuid, research_output):
        all_modules = []
        modules = [i['query'] for i in research_output]
        for lessonIdx,lesson in enumerate(research_output):
            module = lesson['query']
            print(f"Generating lesson plan for :: {module}")
            research_data = [(i['refined_out']) for i in research_output[lessonIdx]['results']]
            resources = [(i['url']) for i in research_output[lessonIdx]['results']]
            lesson_plan = self.create_lesson_plan(module, modules, research_data)
            #all_lesson_plans
            module_data = {"title":module, "lessons":lesson_plan['lessons'], "resources":resources}
            all_modules.append(module_data)
            
        with open(f"{uuid}.json", "w", encoding="utf-8") as f:
            json.dump(all_modules, f, indent=4, ensure_ascii=False)
        return all_modules

