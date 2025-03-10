# Research Assistant

## Approach

- The brief course is taken to generate **K (5) modules** which will aptly cover the course.  
- Each module is **searched for using Google**, and data is retrieved.  
- The retrieved data is **refined** to extract the relevant information.  
- This refined data is used to **create the lesson plan**.  

Uses a **deterministic flow** to build the lesson plans.

---

## Optimizations

- **Better Crawlers/Scrapers:**  
  - Implement an **extraction module (classifier)** to extract **only relevant data**.  

- **Goal-Based Validation:**  
  - Introduce validation (through the **goal generated in Step 1**) to determine **when to stop** data retrieval and refining.  

- **Graph/Vector-Based Data Storage:**  
  - Utilize **community detection & clustering** to structure data.  
  - Helps in generating **lesson plans more effectively**, rather than the current naive approach of directly passing data to LLMs.  

- **Step-Wise Validations:**  
  - Ensure **each step produces expected results** and meets the **required goals** for each module.  


