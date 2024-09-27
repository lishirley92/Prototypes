# %pip install streamlit
import os
import openai
from openai import AzureOpenAI
import streamlit as st
import json
import csv
import textwrap

chat_client = AzureOpenAI(
    azure_endpoint=st.secrets["AZURE_OPENAI_ENDPOINT"],
    api_key=st.secrets["AZURE_OPENAI_KEY"],
    api_version="2023-05-15"
)

engine="chat-4o"

sys_prompt_path = 'SYSTEM_PROMPT_0927.txt'
guidelines_path = 'GUIDELINES_092724.csv'

# Open the file and read its contents into a variable
with open(sys_prompt_path, 'r', encoding='utf-8') as file:
    SYSTEM_PROMPT = file.read()

def get_aoai_response(guideline, user_input):
    user_prompt=f"""
        Please use the following guideline to evaluate the following input text:
        Guideline: {guideline}
        Input Text: {user_input}
        """
    
    completion = chat_client.chat.completions.create(
        model=engine,
        messages = [{"role":"system", "content":SYSTEM_PROMPT},
            {"role":"user", "content":user_prompt}],
        temperature=0,
        max_tokens=800,
        top_p=0.75,
        frequency_penalty=0,
        presence_penalty=0,
        stop=None
    )
    response = completion.choices[0].message.content    
    return response

# Read the CSV file and convert it back to a JSON-like structure
with open(guidelines_path, 'r', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    json_data = {}
    for row in reader:
        guideline_type = row['Guideline Type']
        if guideline_type not in json_data:
            json_data[guideline_type] = {}
        json_data[guideline_type][row['Title']] = {
            'Title': row['Title'],
            'Description': row['Description'],
            'Rules': row['Rules'].split('|'),  # Split the string back into a list
            'Examples of Good Writing': row['Examples of Good Writing'].split('|'),
            'Examples of Bad Writing': row['Examples of Bad Writing'].split('|')
        }

guidelines = json_data

# Function to wrap JSON strings for output
def wrap_json_strings(data, width=80):
    def wrap_string(s):
        # Split the string into lines because it might contain newlines.
        lines = s.splitlines()
        wrapped_lines = [textwrap.fill(line, width=width) for line in lines]
        # Re-join the wrapped lines.
        return '\n'.join(wrapped_lines)

    if isinstance(data, dict):
        return {k: wrap_json_strings(v, width) for k, v in data.items()}
    elif isinstance(data, list):
        return [wrap_json_strings(item, width) for item in data]
    elif isinstance(data, str):
        return wrap_string(data)
    else:
        return data

# Streamlit app interface
st.title('NADIAA - NetApp Docs Integrated Authoring Assistant')

st.write("This is a prototype of an authoring assistant (Docs Copilot) for technical writers. It's trained on select features of the NetAppDocs Style Guide, such as page titles and leads, writing clarity, word choice, and audience. This tool is collaboratively designed by NetApp's IE & DCS teams, and is powered by Azure OpenAI's Chat API.")

system_url = "https://github.com/lishirley92/Prototypes/blob/main/SYSTEM_PROMPT_0927.txt"
system_link_text = "System Prompt"
st.markdown(f"[{system_link_text}]({system_url})", unsafe_allow_html=True)

style_url = "https://github.com/lishirley92/Prototypes/blob/main/GUIDELINES_092724.csv"
style_link_text = "Style Guide Prompts"
st.markdown(f"[{style_link_text}]({style_url})", unsafe_allow_html=True)

# Text input
user_input = st.text_area("Enter your text here:")

# Various to trigger the process
if st.button('If your text contains a title, analyze it'):
    with st.spinner('Generating title feedback...'):

        for item in guidelines['page_title_guidelines'].items():
            # Make multiple calls to the API to generate feedback
            ai_response = get_aoai_response(item[1], user_input)
            ai_wrapped = wrap_json_strings(ai_response, width=80)
            st.success(f"Feedback generated for {item[1]['Title']}")
            st.text(ai_wrapped)

        st.write('All feedback for page titles generated successfully!')

if st.button('If your text contains a page lead, analyze it'):
    with st.spinner('Generating page lead feedback...'):

        for item in guidelines['page_lead_guidelines'].items():
            # Make multiple calls to the API to generate feedback
            ai_response = get_aoai_response(item[1], user_input)
            ai_wrapped = wrap_json_strings(ai_response, width=80)
            st.success(f"Feedback generated for {item[1]['Title']}")
            st.text(ai_wrapped)

        st.write('All feedback for page leads generated successfully!')

if st.button('Analyze your text for writing clarity'):
    with st.spinner('Generating writing clarity feedback...'):

        for item in guidelines['clear_writing_guidelines'].items():
            # Make multiple calls to the API to generate feedback
            ai_response = get_aoai_response(item[1], user_input)
            ai_wrapped = wrap_json_strings(ai_response, width=80)
            st.success(f"Feedback generated for {item[1]['Title']}")
            st.text(ai_wrapped)

        st.write('All feedback for writing clarity generated successfully!')

if st.button('Analyze your text for audience'):
    with st.spinner('Generating audience feedback...'):

        for item in guidelines['audience_guidelines'].items():
            # Make multiple calls to the API to generate feedback
            ai_response = get_aoai_response(item[1], user_input)
            ai_wrapped = wrap_json_strings(ai_response, width=80)
            st.success(f"Feedback generated for {item[1]['Title']}")
            st.text(ai_wrapped)

        st.write('All feedback for audience generated successfully!')

if st.button('Analyze your text for page structure'):
    with st.spinner('Generating page structure feedback...'):

        for item in guidelines['structure_guidelines'].items():
            # Make multiple calls to the API to generate feedback
            ai_response = get_aoai_response(item[1], user_input)
            ai_wrapped = wrap_json_strings(ai_response, width=80)
            st.success(f"Feedback generated for {item[1]['Title']}")
            st.text(ai_wrapped)

        st.write('All feedback for page structure generated successfully!')

if st.button('Analyze your text for word choice'):
    with st.spinner('Generating word choice feedback...'):

        for item in guidelines['word_choice_guidelines'].items():
            # Make multiple calls to the API to generate feedback
            ai_response = get_aoai_response(item[1], user_input)
            ai_wrapped = wrap_json_strings(ai_response, width=80)
            st.success(f"Feedback generated for {item[1]['Title']}")
            st.text(ai_wrapped)

        st.write('All feedback for word choice generated successfully!')

if st.button('Analyze your text for miscellaneous guidelines'):
    with st.spinner('Generating feedback for miscellaneous guidelines...'):

        for item in guidelines['misc_guidelines'].items():
            # Make multiple calls to the API to generate feedback
            ai_response = get_aoai_response(item[1], user_input)
            ai_wrapped = wrap_json_strings(ai_response, width=80)
            st.success(f"Feedback generated for {item[1]['Title']}")
            st.text(ai_wrapped)

        st.write('All feedback for miscellaneous guidelines generated successfully!')

# if st.button('If you need AsciiDoc Syntax, ask here -- FYI this function is under development'):
#     with st.spinner('Generating AsciiDoc Syntax...'):

#         for item in guidelines['provide_asciidoc_syntax'].items():
#             # Make multiple calls to the API to generate feedback
#             ai_response = get_aoai_response(item[1], user_input)
#             ai_wrapped = wrap_json_strings(ai_response, width=80)
#             st.success(f"Feedback generated for {item[1]['Title']}")
#             st.text(ai_wrapped)

#         st.write('AsciiDoc syntax generated successfully!')
