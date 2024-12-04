import streamlit as st
import pandas as pd
import openai
import json
import matplotlib.pyplot as plt

#sidebar
st.sidebar.subheader("How to use", divider = True)
st.sidebar.markdown("""1. Enter OpenAI API key \n 2. Choose GPT model \n 3. Put youe passage in the box \n 4. Press "Submit" button """)

#API key
user_api_key = st.sidebar.text_input("Enter OpenAI API Key", type="password")

client =  openai.OpenAI(api_key=user_api_key)
prompt = """You are an examiner or teacher whose job is to create exam questions. 
            You will receive an English passage which can be about news, academic, 
            letter or anything. You have 4 main tasks to do.

            First, translate the passage into Thai and remain all the datai. A passage can have more than 1 paragraph, so translate 
            all and double sapace between each paragraph.

            Second, create 10 questions that test students' reading comprehension skills. 
            Each question should have 4 multiple choices. The following are examples of questions type.
            e.g. 
            - detail
            - vocab, phrase or idiom definition
            - pronoun refering
            - infer and imply
            - main idea and overall idea
            keep question in a list of dictionaries like this
            [{"question": "In what year did NASA identify and log 90 percent of the asteroids near Earth measuring 1km wide?", 
                "choices": ["2005", "2010", "2015", "2020"], 
                "answer": "2010"},
            {"question": "What does NEO stand for?", 
                "choices": ["New Earth Object", "Near-Earth Orbit", "Near-Earth Object", "Non-Earth Object"], 
                "answer": "Near-Earth Object"},
            {"question": "How many estimated asteroids of 140 meters or more are still unaccounted for?", 
                "choices": ["8,000", "17,000", "25,000", "50,000"], 
                answer": "17,000"}]

            Third, list 15 - 20 interesting vocabulary and keep in a dictionary datatype to convert to DataFrame.
            Provide 4 elements including vocabulary, part of speech, English definition and Thai definiton.
            e.g. {"Vocabulary": ["resolution", "conflict", "significantly"], "Parts of speech": ["noun", "noun", "adverb"], 
            "English definition": ["a firm decision to do or not to do something", "an active disagreement 
            between people with opposing opinions or principles", "in a way that is easy to see or by a large amount"], 
            "Thai definition": ["ปณิธาน", "ความขัดแย้ง", "อย่างมีนัยสำคัญ"]}

            Fourth, classify all the words in the passage according to the CEFR levels (A1, A2, B1, B2, C1, C2) and give the percentage distribution.
            Put it in a list of lists like this example.
            cefr = [["A1", "A2", "B1", "B2", "C1", "C2"], [30, 10, 35, 10, 5, 10]]
            
            Disclaimer : The response must return only this Jason format!!!
            output : { "Thai Translation": First task output, "Questions list": Second task output, 
            "Vocabulary": Third task output, "CEFR Level": Fourth task output} """

def make_question_format(question_list):
  for question in question_list:
    num_answer = 0
    st.markdown(f"**{question["question"]}**")
    for num, choice in enumerate(question["choices"]):
      num= num+1
      if choice == question["answer"]:
        num_answer += num
      st.markdown(f"{num}.) {choice}")
    st.markdown(f"Answer: {num_answer}.) {question["answer"]}")
    st.divider()
            

#page
st.title(":page_facing_up: Create Exam from Passage")

st.markdown("**Input the passage you want to create reading comprehension questions.**")
user_input = st.text_area("Enter passage:", "Your passage here")

if st.button("Submit"):
    if user_api_key and user_input:
        message = [ 
            {"role": "system", "content": prompt},
            {"role": "user", "content": user_input},
        ]
        response = client.chat.completions.create(
        model= "gpt-4o-mini",
        messages=message
        )
        
        response = response.choices[0].message.content

        output = json.loads(response) #output is Dictionary


        tab1, tab2, tab3 = st.tabs(["Thai Translation", "Questions", "Vocabulary and overall CEFR"])

        with tab1:
            #Thai transation of the passage
            st.subheader("Thai Translation of the Passage", divider = "orange")
            st.markdown(output["Thai Translation"])
        with tab2:
            #Questions_answers list
            st.subheader("Reading Questions", divider = "blue")
            questions_list = output["Questions list"]
            make_question_format(questions_list)
        with tab3:
            col1, col2 = st.columns([3, 2])

            #Vocabulary DataFrame
            col1.subheader("Vocabulary Table", divider = "green")
            vocabulary_df = pd.DataFrame.from_dict(output["Vocabulary"])
            df = vocabulary_df.rename(index = lambda x: x + 1)
            col1.table(df)

            #matplotlib.pyplot CEFR pie chart
            col2.subheader("CEFR Level", divider = "gray")
            cefr_list = output["CEFR Level"][0]
            percentage_list = output["CEFR Level"][1]
            fig1, ax1 = plt.subplots(figsize=(4, 4))
            ax1.pie(percentage_list, labels=cefr_list, autopct='%1.1f%%',shadow=True, startangle=90)
            ax1.axis('equal')  
            col2.pyplot(fig1)
        
    #Warning box
    elif not user_api_key and not user_input:
        st.error("Please enter OpenAI API key and your passage!")
    elif not user_api_key:
        st.error("Please enter OpenAI API key!")
    elif not user_input:
        st.error("Please enter your passage!")
       




#Questions generated 
