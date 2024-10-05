import streamlit as st 

from dotenv import load_dotenv
import mysql.connector as connector
import os
from langchain.sql_database import SQLDatabase
import google.generativeai as ai
load_dotenv()

ai.configure(api_key=os.getenv('GOOGLE_API_KEY'))

#function to laod google gemini model and provide sql query for response

def get_gemin_response(question,prompt1):
    model = ai.GenerativeModel('gemini-pro')
    response = model.generate_content([prompt1,question])
    return response.text

## Function to retrive query from sql database 

def read_sql_query(sql):
    cnx = connector.connect(user='root',
                            password='root',
                            host='localhost',
                            database='mobile')
    cursor = cnx.cursor()
    cursor.execute(sql)
    rows = cursor.fetchall()
    cnx.close()
    # for row in rows:
    #     print(row)
    return rows


def sql_result_to_text(column_names, sql_result):
    """
    Convert the SQL result to plain text dynamically based on the column names and result data.
    
    Args:
        column_names (list): List of column names returned by the SQL query.
        sql_result (list of tuples): The actual result data (each tuple represents a row).
    
    Returns:
        str: Plain text representation of the SQL result.
    """
    
    formatted_rows = []
    
    
    for row in sql_result:
        
        row_text = []
        
        for col_name, value in zip(column_names, row):
            row_text.append(f"{col_name}: {value}")
        
        formatted_rows.append(", ".join(row_text))
    
    
    return "\n".join(formatted_rows)

column_names = ['Brand','Model','Storage','RAM','Screen Size (inches)','Camera (MP)','Battery Capacity (mAh)','Price']

prompt1 = """
You are an expert in converting English questions to SQL queries!
The SQL database has the name 'MOBILE' and the following columns: 
Brand, Model, Storage, RAM, Screen Size (inches), Camera (MP), 
Battery Capacity (mAh), Price, Min_price.

Here are some example translations:

Example 1:
Question: "How many mobile entries are in the database?"
SQL: SELECT COUNT(*) FROM MOBILE;

Example 2:
Question: "Show me all the mobiles from the brand Apple."
SQL: SELECT * FROM MOBILE WHERE BRAND = 'Apple';

Example 3:
Question: "List all mobiles under $500."
SQL: SELECT * FROM MOBILE WHERE PRICE < 500;

Instructions:
- Translate each English question into an SQL query based on the provided table structure.
- Do not include `'''` at the beginning or end of the SQL code.
- Do not use the word 'SQL' in the response.
- Ensure that the generated SQL queries are syntactically correct.
"""

prompt2 ="""
       You are a friendly and persuasive mobile phone salesman with access to a database of various smartphones,
       their features, and prices. Your goal is to interact with customers,
       provide detailed information about the smartphones, and try to sell them at the best possible price. 
       Be professional and polite, but also act as a skilled negotiator who can adjust the price within certain limits based on the customer's sentiment and responses.
       You have to response to user query and talk like a professional salesman
    """

# interface code 


st.set_page_config(page_title = 'I am chatbot for price negotiation ')
st.header('Gemini app for price negotiation')




if "message" not in st.session_state:
    st.session_state.message = []


for message in st.session_state.message:
    with st.chat_message(message['role']):
        st.markdown(message['content'])



if prompt := st.chat_input("What is up?"):
    
    # Add user message to chat history
    st.session_state.message.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)
    
    query = get_gemin_response(prompt1,prompt)
    temp = read_sql_query(query)
    plain_text = sql_result_to_text(column_names,temp)

    question_for_llm = (
        f"The customer is asking: {prompt}\n\n"
        f"Here are the available options:\n{plain_text}\n\n"
        "Please provide a helpful and persuasive response."
    )

    assistant_response = get_gemin_response(prompt2,question_for_llm)
    st.session_state.message.append({"role": "assistant", "content": assistant_response})
    with st.chat_message("assistant"):
        st.markdown(assistant_response)
    





    
    



