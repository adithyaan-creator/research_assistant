QUERY_GENERATOR_SYSTEM_PROMPT = f"""You are an expert researcher specializing in generating highly optimized 
search modules to extract the most relevant and comprehensive information for tutorial creation. 
Your task is to craft precise, well-structured queries that maximize the quality of Google search results, ensuring 
they cover essential concepts, step-by-step guides, and best practices for the given topic.

"""

QUERY_GENERATION_FUNCTION_SCHEMA = {
    "type": "function",
    "function": {
        "name": "generate_research_modules",
        "description": "Generate queries for research tasks",
        "strict": True,
        "additionalProperties": False,
        "parameters": {
            "additionalProperties": False,
            "type": "object",
            "required": ["queries", "sub_topics"],
            "properties": {
                "queries": {
                    "type": "array",
                    "description": "List of generated queries for research purposes",
                    "items": {
                        "type": "object",
                        "additionalProperties": False,
                        "required": ["query", "goal"],
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "A structured query designed to retrieve relevant information for research"
                            },
                            "goal": {
                                "type": "string",
                                "description": "The purpose of the query, explaining what specific information or insight it aims to uncover"
                            }
                        }
                    }
                },
                "sub_topics":{
                    "type":"array", 
                    "description":"5 topics that will help create a course to learn and structure a course for the topic",
                    "items": {
                        "type": "string"
                    }
                }
            }
        }
    }
}

def create_query_generator_user_prompt(query_count, topic):
    return f"""Generate {query_count} search queries for the following research topic {topic}."""


###############################################################
###############################################################
REFINE_SEARCH_SYSTEM_PROMPT = f"""You are an expert researcher tasked with analyzing provided data and 
extracting the key information.
Make sure to return all the relevant findings and to skip any which will be needed to further create a research report.
"""

def create_refine_search_results_user_prompt(query, search_result):
    return f"""Refine the following search results for the query {query} extracting the key information.
    Search results: {search_result}
    """

###############################################################
###############################################################
LESSON_PLAN_SYSTEM_PROMPT = """You are an expert curriculum designer.  
Your task is to create a **structured lesson plan** for a given sub-topic, using **only** the provided research data.  
This lesson is part of a larger course module.  

Each lesson must include:  
- **Lesson Title**: A concise, engaging, and relevant title.  
- **Learning Objectives**: Clear, measurable takeaways that students should achieve.  
- **Lesson Content**: A structured explanation strictly based on the research data, logically organized with key points.  

**Rules:**  
1. **Use only the given research data**—do **not** add external information.  
2. **Focus strictly on the sub-topic**, even if unrelated data appears in the research.  
3. If research data is insufficient, highlight the gaps instead of making assumptions.  
"""

def create_lesson_plan_user_prompt(module, modules, refined_research_data):
    return f"""Create a **comprehensive lesson plan** spread across multiple lessons for the module: **{module}**.  
The full course includes these modules(query) and their goals: **{', '.join(modules)}**.  

🔹 **Research Data:**  
{refined_research_data}  

🔹 **Lesson Plan Structure:**  

**Lesson Title:**  
A concise and engaging title relevant to the sub-topic.  

**Learning Objectives:**  
- Clearly defined, measurable takeaways for students.  

**Lesson Content:**  
- A structured explanation based strictly on the research data.  
- Logically organized with key points, definitions, and explanations.  
- Make sure to split the module into 2-4 lessons to avoid too much data in a single lesson.
- Do **not** add external information—use only what is provided, but creative to add relevant examples and a proper learning structure.
"""

LESSON_PLAN_FUNCTION_SCHEMA = {
    "type": "function",
    "function": {
        "name": "generate_lesson_plan",
        "description": "Generate a structured lesson plan for a given sub-topic using research data",
        "strict": True,
        "additionalProperties": False,
        "parameters": {
            "additionalProperties": False,
            "type": "object",
            "required": ["lessons"],
            "properties": {
                "lessons": {
                    "type": "array",
                    "description": "List of structured lessons for the given sub-topic",
                    "items": {
                        "type": "object",
                        "additionalProperties": False,
                        "required": ["title", "learning_objectives", "content"],
                        "properties": {
                            "title": {
                                "type": "string",
                                "description": "A concise and engaging title for the lesson"
                            },
                            "learning_objectives": {
                                "type": "array",
                                "description": "Key takeaways students should achieve by the end of the lesson",
                                "items": {
                                    "type": "string"
                                }
                            },
                            "content": {
                                "type": "string",
                                "description": "The detailed explanation of the lesson based strictly on the provided research data. Make sure to provide only the lesson content and nothing extra."
                            }
                        }
                    }
                }
            }
        }
    }
}
