#import InvokeAgent as agenthelper
import InvokeAgentSDK as agenthelper
import streamlit as st
import json
import pandas as pd
from PIL import Image, ImageOps, ImageDraw
import random
#import argparse

#Get the session id from the command line agrument, if it exists
#parser = argparse.ArgumentParser(description='This is the session Id')
#parser.add_argument('--sessionid', action='store', default='SesX',
#                    help="Provide a session id of your choice")
#args = parser.parse_args()
#sessionid = args.sessionid
if 'sessionid' not in st.session_state:
    st.session_state.sessionid = "S" + str(random.randrange(0, 10001, 1))

print("Starting with Session Id: ", st.session_state.sessionid)

# Streamlit page configuration
st.set_page_config(page_title="Alianza Call Analyzer", page_icon=":robot_face:", layout="wide", initial_sidebar_state="collapsed")

# Function to crop image into a circle
def crop_to_circle(image):
    mask = Image.new('L', image.size, 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.ellipse((0, 0) + image.size, fill=255)
    result = ImageOps.fit(image, mask.size, centering=(0.5, 0.5))
    result.putalpha(mask)
    return result

# Function to parse and format response
def format_response(response_body):
    isjson:bool = False

    try:
        # Try to load the response as JSON
        response_body = response_body.replace("\n","")
        data = json.loads(response_body)
        isjson = True
        return data, isjson
    except json.JSONDecodeError:
        # If response is not JSON, return as is
        return response_body, isjson

# Handling user input and responses
def click_button():

    prompt = st.session_state.text
    prompt = prompt.strip()

    if prompt:

    #initialize variables
        all_data  = ""
        the_response = ""
        response_data = None
        isjson:bool = False
        event = {
            "sessionId": st.session_state.sessionid,
            "question": prompt
        }

        try:

            # Call the Bedrock Agent
            print("Before calling the Agent")
            response = agenthelper.lambda_handler(event, None)
            print("After calling the Agent")

            # Parse the JSON string
            if response and 'body' in response and response['body']:
                response_data = json.loads(response['body'])
                print("TRACE & RESPONSE DATA received")
            else:
                print("Invalid or empty response received")
        except Exception as e:
            print("Error Info calling the Agent: ", str(e))
            print(f"{type(e).__name__} at line {e.__traceback__.tb_lineno} of {__file__}: {e}")
            all_data = str(e)
            response_data = None 
        
        try:
            # Extract the response and trace data
            print("Before extracting the response")
            all_data, isjson = format_response(response_data['response'])
            the_response = str(response_data['trace_data']).replace("<additional_insight>","").replace("</additional_insight>","")
            print("After extracting the response: ", the_response)
        except Exception as e:
            print("Error Info extracting the response: ", str(e))
            print(f"{type(e).__name__} at line {e.__traceback__.tb_lineno} of {__file__}: {e}")
            all_data = str(e)
            the_response = "Apologies, but an error occurred. Please rerun the application" 

        # Use trace_data and formatted_response as needed
        if isjson:
            st.sidebar.json(all_data)
        else:
            st.sidebar.text_area(" ", value=all_data, height=500)
        
        st.session_state['history'].append({"question": prompt, "answer": the_response})
        st.session_state['trace_data'] = the_response
        st.session_state.text = ""

# Title
st.title("Alianza Call Analyzer @ Powered by Amazon Bedrock Agent")

# Display a text box for input
st.text_input("Please enter your query?", max_chars=2000, key="text", on_change=click_button)

# Display a primary button for submission
st.button("Submit Question", on_click=click_button)

# Display a button to end the session
new_conv_button = st.button("New Conversation")

# Sidebar for user input
st.sidebar.title("Trace Data")

# Session State Management
if 'history' not in st.session_state:
    st.session_state['history'] = []

if new_conv_button:
    st.session_state['history'].append({"question": "Session Ended", "answer": "Thank you for using my services!"})
    st.session_state.sessionid += "x"
    print("The new session id is: ", st.session_state.sessionid)

    event = {
        "sessionId": st.session_state.sessionid,
        "question": "placeholder to end session",
        "endSession": True
    }
    agenthelper.lambda_handler(event, None)
    st.session_state['history'].clear()

# Display conversation history
st.write("## Conversation History")

## Load images outside the loop to optimize performance
#human_image = Image.open('./images/human_face.png')
#robot_image = Image.open('./images/robot_face.jpg')
#circular_human_image = crop_to_circle(human_image)
#circular_robot_image = crop_to_circle(robot_image)

for index, chat in enumerate(reversed(st.session_state['history'])):
    # Creating columns for Question
    #col1_q, col2_q = st.columns([2, 10])
    #with col1_q:
    #    st.image(circular_human_image, width=125)
    #with col2_q:
    #    # Generate a unique key for each question text area
    #    st.text_area("Question:", value=chat["question"], height=50, key=f"question_{index}", disabled=True)
    st.text_area("Question followed by Answer:", value=chat["question"], height=50, key=f"question_{index}", disabled=True)

    # Creating columns for Answer
    #col1_a, col2_a = st.columns([2, 10])
    if isinstance(chat["answer"], pd.DataFrame):
    ##    with col1_a:
    #        st.image(circular_robot_image, width=50)
    #    with col2_a:
    #        # Generate a unique key for each answer dataframe
    #        st.dataframe(chat["answer"], key=f"answer_df_{index}")
        st.dataframe(chat["answer"], key=f"answer_df_{index}")
    else:
        #with col1_a:
        #    st.image(circular_robot_image, width=150)
        #with col2_a:
        #    # Generate a unique key for each answer text area
        #    st.text_area("Answer:", value=chat["answer"], key=f"answer_{index}")
        #st.text_area("Answer:", value=chat["answer"], key=f"answer_{index}")
        st.write(chat["answer"])

# Example Prompts Section
st.write("## Sample Questions")

# Creating a list of sample questions
sample_questions = [
    {"Prompt": "What is your purpose?"},
    {"Prompt": "List the auto stores"},
    {"Prompt": "How many stores are you tracking data for?"},
    {"Prompt": "How many employees are handling calls?"},
    {"Prompt": "What is the average duration of all calls?"}
]

# Displaying the Knowledge Base prompts as a table
st.table(sample_questions)

# Print the end
print("Ending with Session Id: ", st.session_state.sessionid)
