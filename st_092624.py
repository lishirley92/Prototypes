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
guidelines_path = 'guidelines_092724.csv'

# Open the file and read its contents into a variable
with open(sys_prompt_path, 'r', encoding='utf-8') as file:
    SYSTEM_PROMPT = file.read()

# SYSTEM_PROMPT = """
# You are an AI copilot tasked with helping improve technical documentation. The user will give you a writing guideline, and some input text that is expected to follow the writing guideline. Your task is to evaluate whether or not the input text follows the guideline in your output response.

# GUIDELINE
# The guideline will be structured as a JSON and will contain the following five components as keys: "Title", "Description", "Rules", "Examples of Good Writing", "Examples of Bad Writing."

# INPUT TEXT
# The input text will be an excerpt from some technical documentation that may need revision. The input text may be one sentence, one paragraph, or a few paragraphs. It will be written in AsciiDoctor format.

# OUTPUT RESPONSE
# Your task is to evaluate whether or not the input text follows the guideline. Please output your response as a JSON with the following components as keys: "Title" (of the Guideline), "Evaluation", "Instance 1" (if applicable), "Instance 2" (if applicable).

# - If the input text follows the guideline, under "Evaluation" write "No issues found." Otherwise, write "Issues found."
# - If the input text does not follow the guideline, choose 1-2 instances to focus on. 
# - For each instance (Instance 1 and Instance 2), give a short, 1-sentence summary how it violates the guideline. Then provide both the original input text and a revised version that corrects the instance.
# """

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

# guidelines = {
#     'page_title_guidelines': {
#     'Page Titles for Concept or Reference Pages': {
#         "Title": "Page Titles for Concept or Reference Pages",
#         "Description": "Titles should summarize the contents of a page. They should be descriptive but concise and use sentence case capitalization.",
#         "Rules": [
#             "Titles should be two words or more.",
#             "Titles should have a minimum of 30 characters (including spaces) and a maximum of 70 characters.",
#             "Use a primary keyword from the content in the page title.",
#             "Use sentence case for capitalization (the first letter of the first word is capitalized, and all other letters are in lowercase, except for proper nouns).",
#             "Don't use words like: guide, manual, primer, book, topic, article, task, reference, concept.",
#             "Avoid colons, em dashes, and en dashes in titles.",
#             "For pages describing a product or service, use this format: 'Learn about <service or product name>'",
#             "Don't use the imperative mood, which uses a verb as the first word in the title.",
#             "Avoid using 'considerations' or 'About <feature>' in titles."
#         ],
#         "Examples of Good Writing": [
#             "User-initiated logs",
#             "StorageGRID deployments",
#             "Learn about BlueXP disaster recovery",
#             "NAS management with System Manager",
#             "Tenant accounts in StorageGRID"
#         ],
#         "Examples of Bad Writing": [
#             "Guide to StorageGRID deployments",
#             "System Manager: Introduction",
#             "BlueXP disaster recovery introduction",
#             "Introduction to BlueXP disaster recovery",
#             "Ransomware protection considerations."
#         ]
#     }, 
#     'Page Titles for Task Pages': {
#         "Title": "Page Titles for Task Pages",
#         "Description": "Titles should summarize the contents of a page. They should be descriptive but concise and use sentence case capitalization.",
#         "Rules": [
#             "Titles should be two words or more.",
#             "Titles should have a minimum of 30 characters (including spaces) and a maximum of 70 characters.",
#             "Use a primary keyword from the content in the page title.",
#             "Use sentence case for capitalization.",
#             "Don't use words like: guide, manual, primer, book, topic, article, task, reference, concept.",
#             "Avoid colons, em dashes, and en dashes in titles.",
#             "Titles for task pages should summarize the task the user is completing by following the steps on the page.",
#             "Titles should use the imperative mood, with the verb as the first word in the title.",
#             "Don't use the phrase 'how to' in the title.",
#             "Don't use '-ing' words. Use words like create or configure instead."
#         ],
#         "Examples of Good Writing": [
#             "Respond to a detected ransomware attack",
#             "Create a replication plan for ransomware protection",
#             "Recover from a ransomware attack",
#             "Change passwords in Cloud Volumes ONTAP",
#             "Fail back applications to the source site"
#         ],
#         "Examples of Bad Writing": [
#             "Respond to a detected ransomware attack and initiate a Snapshot copy for backup protection",
#             "Create a replication plan—for ransomware protection",
#             "RECOVER FROM A RANSOMWARE ATTACK",
#             "How to recover from a ransomware attack",
#             "Creating a replication plan for ransomware protection."
#         ]
#     }
#     },
#     'page_lead_guidelines': {
#     'Page Leads for Concept Pages': {
#         "Title": "Page Leads for Concept Pages",
#         "Description": "A page lead is the paragraph of text that follows a 'page title.' The wording in a page lead should follow a set of general rules.",
#         "Rules": [
#             "The lead should act as a summary of the entire page and describe why a user would be interested in the content.",
#             "The lead should be 1 to 3 sentences in length.",
#             "The lead should define and use key terms from within the page and other terms familiar to the user.",
#             "The lead should use the active voice.",
#             "Don't use phrases like 'this book,' 'this topic,' 'this page,' 'this guide.'",
#             "Include an example that further clarifies the user's motivation."
#         ],
#         "Examples of Good Writing": [
#             "A BlueXP account provides multi-tenancy for your organization, enabling you to organize users and resources in isolated workspaces.",
#             "Several licensing options are available for Cloud Volumes ONTAP, allowing you to choose a consumption model that meets your needs.",
#             "Understanding how Cloud Volumes ONTAP uses cloud storage can help you understand your storage costs."
#         ],
#         "Examples of Bad Writing": [
#             "BlueXP accounts enable you to create users who have different levels of control over the storage systems.",
#             "Cloud Volumes ONTAP can be provisioned using various licensing models.",
#             "This section describes how Cloud Volumes ONTAP uses cloud storage."
#         ]
#     }, 
#     'Page Leads for Reference Pages': {
#         "Title": "Page Leads for Reference Pages",
#         "Description": "A page lead is the paragraph of text that follows a 'page title.' The wording in a page lead should follow a set of general rules.",
#         "Rules": [
#             "The lead should act as a summary of the entire page and describe why a user would be interested in the content.",
#             "The lead should be 1 to 3 sentences in length.",
#             "The lead should define and use key terms from within the page and other terms familiar to the user.",
#             "The lead should use the active voice.",
#             "Explain what the referenced items are used for.",
#             "Don't use phrases like 'this book,' 'this topic,' 'this page,' 'this guide.'"
#         ],
#         "Examples of Good Writing": [
#             "BlueXP classification software must run on a host that meets specific operating system, RAM, and software requirements.",
#             "In addition to the physical ports provided on each node, logical ports can be used to manage network traffic.",
#             "BlueXP copy and sync enables you to sync data from a source to a target."
#         ],
#         "Examples of Bad Writing": [
#             "The system on which you plan to run BlueXP classification must meet the following requirements.",
#             "Logical ports can be used for network traffic on each node in addition to physical ports.",
#             "You can synchronize data from a source system to a target system."
#         ]
#     }, 
#     'Page Leads for Task Pages': {
#         "Title": "Page Leads for Task Pages",
#         "Description": "A page lead is the paragraph of text that follows a 'page title.' The wording in a page lead should follow a set of general rules.",
#         "Rules": [
#             "The lead should act as a summary of the entire page and describe why a user would be interested in the content.",
#             "The lead should be 1 to 3 sentences in length.",
#             "The lead should define and use key terms from within the page and other terms familiar to the user.",
#             "The lead should use the active voice.",
#             "Don't use phrases like 'this book,' 'this topic,' 'this page,' 'this guide.'",
#             "Can include words like 'this procedure' or 'these steps.'"
#         ],
#         "Examples of Good Writing": [
#             "If you need more storage after launching your initial Cloud Volumes ONTAP system, you can create new FlexVol volumes from BlueXP.",
#             "Learn how to install and set up the EF300 or EF600 storage system.",
#             "To ensure that adequate space is available for object metadata, you might need to perform an expansion procedure to add new storage nodes."
#         ],
#         "Examples of Bad Writing": [
#             "This page describes how to create new FlexVol volumes from BlueXP.",
#             "You can install and set up NetApp EF-Series arrays using this topic.",
#             "Add capacity to your nodes when you need more storage space."
#         ]
#     }
#     },
#     'provide_asciidoc_syntax': {
#     'Provide AsciiDoc Syntax for a Tabbed Block': {
#         "Title": "Provide AsciiDoc Syntax for a Tabbed Block",
#         "Description": "Provide AsciiDoc syntax for a tabbed block that includes two tabs.",
#         "Rules": [
#             "The block starts with a specific role attribute to indicate the tabbed nature.",
#             "Each tab heading is defined, followed by the content of the tab.",
#             "Content for each tab is separated by a delimiter ('--'), and the entire tabbed area is enclosed within the '====' block."
#         ],
#         "Examples of Good Writing": [
#             "Tab headings are clear and concise.",
#             "Delimiters ('--') are correctly placed, ensuring the structure of each tab's content is clear.",
#             "The block starts and ends correctly with '[role=\"tabbed-block\"]' and '====', making it easy to identify."
#         ],
#         "Examples of Bad Writing": [
#             "Missing delimiters ('--') after headings and between tabs.",
#             "Incorrect or incomplete block delimiters ('====' not used properly).",
#             "Lack of proper role attribute ('[role=\"tabbed\"]' instead of '[role=\"tabbed-block\"]')."
#         ]
#     }, 
#     'Provide AsciiDoc Syntax for a Table': {
#         "Title": "Provide AsciiDoc Syntax for a Table",
#         "Description": "Provide AsciiDoc syntax for a table that has four rows, three columns, and a header row.",
#         "Rules": [
#             "The 'cols' attribute defines the number of columns and their relative widths.",
#             "Use 'a' after the column width to enable AsciiDoc notation within the cells.",
#             "Use the 'options=\"header\"' attribute to specify a header row."
#         ],
#         "Examples of Good Writing": [
#             "Clear separation between columns and rows using '|'.",
#             "Correct use of 'cols=\"25a,25a,50a\"' to define the relative width of each column.",
#             "The table starts with the correct header format ('options=\"header\"'), ensuring clarity in column headings."
#         ],
#         "Examples of Bad Writing": [
#             "The 'cols' attribute is incorrectly formatted ('25 25 50' instead of '25a,25a,50a').",
#             "The 'options' attribute is incorrect ('headers' instead of 'header').",
#             "Missing the final '|===' to close the table."
#         ]
#     }
#     }, 
#     'clear_writing_guidelines': {
#     'Write Simply': {
#         "Title": "Write Simply",
#         "Description": "Use short, simple words and phrases. Avoid jargon and complex language.",
#         "Rules": [
#             "Use plain language whenever possible.",
#             "Avoid complex or formal words like 'consequently' (use 'so').",
#             "Keep terminology consistent and straightforward."
#         ],
#         "Examples of Good Writing": [
#             "Move the files to the backup folder.",
#             "You need to complete the installation before starting the service.",
#             "To connect, click the 'Connect' button.",
#             "Check your network connection before troubleshooting further."
#         ],
#         "Examples of Bad Writing": [
#             "Relocate the files to the backup directory.",
#             "In order to complete the installation, ensure that all necessary components are configured prior to starting the service.",
#             "To establish a connection, select the 'Connect' icon.",
#             "Verify the integrity of your network connection prior to proceeding with any additional troubleshooting measures."
#         ]
#     }, 
#     'Get to the Point': {
#         "Title": "Get to the Point",
#         "Description": "Each page should start with what's most important to the user. Focus on helping users achieve their goals, using keywords at the beginning of sentences to improve scannability.",
#         "Rules": [
#             "Start with the most relevant information for the user.",
#             "Use keywords early in sentences to improve readability.",
#             "Keep sentences short and to the point.",
#             "Avoid unnecessary filler words."
#         ],
#         "Examples of Good Writing": [
#             "Use SSH to access the server and check the configuration.",
#             "To reduce latency, configure your system to use data replication.",
#             "Check for updates regularly to ensure your software is up to date."
#         ],
#         "Examples of Bad Writing": [
#             "Accessing the server can be done by using SSH, which is a secure protocol for remotely logging into the system.",
#             "In order to reduce latency issues in your network, it is a good idea to configure your system with data replication, which can help mitigate potential delays.",
#             "You should check for updates frequently to make sure that the software you are running is the latest version."
#         ]
#     }, 
#     'Write Minimally': {
#         "Title": "Write Minimally",
#         "Description": "Make sentences as concise as possible. Break long sentences into shorter ones, and use short paragraphs.",
#         "Rules": [
#             "Write short, concise sentences.",
#             "Break complex ideas into multiple sentences.",
#             "Keep paragraphs short and focused on a single idea."
#         ],
#         "Examples of Good Writing": [
#             "Reboot the server to apply updates.",
#             "The system will be down for 10 minutes during the reboot.",
#             "Enable two-factor authentication for better security."
#         ],
#         "Examples of Bad Writing": [
#             "In order to apply the necessary updates, you must reboot the server, which will result in a brief period of downtime lasting approximately 10 minutes.",
#             "It is highly recommended that two-factor authentication is enabled in order to ensure a higher level of security.",
#             "The reboot should be completed within a short time frame, approximately 10 minutes or so, barring any unforeseen issues."
#         ]
#     }, 
#     'Write Actively': {
#         "Title": "Write Actively",
#         "Description": "Use active voice so that the subject of the sentence performs the verb's action.",
#         "Rules": [
#             "Write in active voice, where the subject performs the action.",
#             "Use passive voice only when the subject is unknown or irrelevant.",
#             "Make the subject clear in each sentence."
#         ],
#         "Examples of Good Writing": [
#             "The administrator updated the system settings.",
#             "The team approved the new project plan.",
#             "Restart the server to apply the new configuration."
#         ],
#         "Examples of Bad Writing": [
#             "The system settings were updated by the administrator.",
#             "The new project plan was approved by the team.",
#             "The server should be restarted to apply the new configuration."
#         ]
#     }, 
#     'Write Conversationally': {
#         "Title": "Write Conversationally",
#         "Description": "Connect with your readers by writing in a conversational tone while maintaining professionalism.",
#         "Rules": [
#             "Use an approachable and empathetic tone.",
#             "Keep language professional while being clear and friendly.",
#             "Avoid overly formal language and jargon."
#         ],
#         "Examples of Good Writing": [
#             "Click 'Submit' to save your changes.",
#             "Follow the prompts to complete the installation.",
#             "If something goes wrong, check the status page for more details."
#         ],
#         "Examples of Bad Writing": [
#             "Upon completion of the required steps, you may click 'Submit' in order to finalize your settings.",
#             "The user can select 'Submit' in order to complete the operation.",
#             "Should any issues arise during the process, you should navigate to the status page for further information."
#         ]
#     }, 
#     'Verb Tense': {
#         "Title": "Verb Tense",
#         "Description": "Use the present tense for verbs. Avoid the past or future tense. The present tense is often easier to read and understand.",
#         "Rules": [
#             "Use present tense for instructions, descriptions, and general statements.",
#             "Avoid using past or future tense unless necessary."
#         ],
#         "Examples of Good Writing": [
#             "The update installs automatically.",
#             "The command enables the administrator account.",
#             "Beginning with ONTAP 9.3, SnapMirror XDP mode replaces DP mode."
#         ],
#         "Examples of Bad Writing": [
#             "The update will be installed automatically.",
#             "The following command will enable the administrator account.",
#             "In ONTAP 9.3, SnapMirror XDP mode replaced DP mode as the default."
#         ]
#     }
#     }, 
#     'audience_guidelines': {
#     'Write for a Global Audience': {
#         "Title": "Write for a Global Audience",
#         "Description": "Write content that is easy to read and translate for users whose primary language is not English.",
#         "Rules": [
#             "Use simple, standard grammar and punctuation.",
#             "Avoid complex sentence structures and jargon.",
#             "Use one word for one meaning, and avoid idiomatic expressions.",
#             "Include graphics to clarify text."
#         ],
#         "Examples of Good Writing": [
#             "Click the 'Start' button to begin the process.",
#             "A VPN is required to connect the two networks securely.",
#             "Make sure that the system is powered off before performing maintenance."
#         ],
#         "Examples of Bad Writing": [
#             "Initiate the procedure by navigating to the Start button.",
#             "A VPN, or Virtual Private Network, is absolutely necessary to ensure secure communications between the two infrastructures.",
#             "Ensure that the system has been shut down prior to the commencement of any maintenance."
#         ]
#     }, 
#     'Use Inclusive Language': {
#         "Title": "Use Inclusive Language",
#         "Description": "Avoid language that can be interpreted as degrading, racist, or sexist. Use people-first language and gender-neutral pronouns.",
#         "Rules": [
#             "Avoid gender-specific pronouns like 'he' or 'she'.",
#             "Use gender-neutral language or plural forms.",
#             "Prioritize people-first language (e.g., 'person with a disability').",
#             "Avoid oppressive or outdated terms (e.g., 'whitelist/blacklist')."
#         ],
#         "Examples of Good Writing": [
#             "Developers need access to their servers.",
#             "A person with hearing loss can enable captions for videos.",
#             "Use an allowed list and blocked list for permissions."
#         ],
#         "Examples of Bad Writing": [
#             "A developer needs access to his servers.",
#             "A hearing-impaired person can enable captions.",
#             "Use a whitelist and blacklist for permissions."
#         ]
#     }
#     },
#     'structure_guidelines': {
#     'Create Scannable Content': {
#         "Title": "Create Scannable Content",
#         "Description": "Help readers find content quickly by organizing text under section headings and using lists and tables. Headings, sentences, and paragraphs should be short and easy to read. The most important information should be provided first.",
#         "Rules": [
#             "Use section headings to break up content.",
#             "Start with the most important information.",
#             "Keep sentences and paragraphs short.",
#             "Use lists, tables, and bullet points to make the text more scannable."
#         ],
#         "Examples of Good Writing": [
#             "BlueXP offers the following deployment modes: Standard mode, Restricted mode, and Private mode. Each mode differs in terms of connectivity, installation, and available services.",
#             "The following table shows a comparison of backup strategies: Full Backup, Incremental Backup, and Differential Backup.",
#             "For more detailed instructions, refer to the Installation Guide: Step 1 - Download the installer; Step 2 - Run the installer; Step 3 - Follow the prompts."
#         ],
#         "Examples of Bad Writing": [
#             "The deployment modes in BlueXP are numerous and vary greatly in terms of how they function, and the differences are quite significant between the modes. These differences include outbound connectivity, installation methods, and available services.",
#             "There are different types of backup strategies, like full backup, incremental backup, and differential backup, each with its own pros and cons.",
#             "To install, first you must download the installer, then run it, and finally follow the instructions to complete the setup."
#         ]
#     }, 
#     'Organize Content Based on the User\'s Goal': {
#         "Title": "Organize Content Based on the User's Goal",
#         "Description": "Organize content based on the user's goals. Structure the site's navigation and individual pages to help users quickly find the information they need.",
#         "Rules": [
#             "High-level navigation should focus on user goals (e.g., 'Get started', 'Protect data').",
#             "Mid-level navigation should group tasks that help users achieve their goals.",
#             "Individual pages should focus on specific tasks, using sections to divide content."
#         ],
#         "Examples of Good Writing": [
#             "The 'Get Started' section includes: Setting up your account, Configuring your workspace, and Managing permissions.",
#             "In the 'Backup and Recovery' section, you will find guides on: Backing up your data, Restoring from backup, and Setting up continuous backup.",
#             "To install the software, follow these steps: Step 1 - Download the installer. Step 2 - Run the installer. Step 3 - Verify installation."
#         ],
#         "Examples of Bad Writing": [
#             "This documentation includes guides on various aspects of our software, such as setting up accounts, workspaces, and permissions.",
#             "In the backup and recovery documentation, you will find information on how to backup, restore, and continuously backup your data.",
#             "If you want to install the software, you should first download the installer, run it, and then check to make sure everything is working."
#         ]
#     }, 
#     'Use Lots of Visuals': {
#         "Title": "Use Lots of Visuals",
#         "Description": "Use videos, diagrams, and screenshots to improve learning and break up blocks of text.",
#         "Rules": [
#             "Use visuals to support the text and improve understanding.",
#             "Provide descriptive lead-in sentences before each visual.",
#             "Use alt text for embedded visuals.",
#             "Limit screenshots to five per task."
#         ],
#         "Examples of Good Writing": [
#             "The following diagram shows the system architecture.",
#             "Watch this short video to learn how to configure your account.",
#             "The image below illustrates the backup process."
#         ],
#         "Examples of Bad Writing": [
#             "The diagram is displayed here for your reference.",
#             "Please refer to the video for further details.",
#             "Below is a visual representation of the system."
#         ]
#     }
#     },
#     'word_choice_guidelines': {
#     'After (versus Once)': {
#         "Title": "After (versus Once)",
#         "Description": "Use 'after' to indicate chronology. Use 'once' only to mean 'one time.'",
#         "Rules": [
#             "Use 'after' when referring to events that happen in sequence.",
#             "Use 'once' only to indicate a singular occurrence."
#         ],
#         "Examples of Good Writing": [
#             "After you install Astra Control Center, you should consider enabling certificate-based authentication.",
#             "After the cluster is registered with BlueXP, you need to enable backup and recovery.",
#             "After configuring the firewall settings, test the connection to ensure security."
#         ],
#         "Examples of Bad Writing": [
#             "Once you install Astra Control Center, you should enable certificate-based authentication.",
#             "Once the server is registered, you can initiate the first backup.",
#             "Once you configure the firewall settings, you should test the connection."
#         ]
#     }, 
#     'Also': {
#         "Title": "Also",
#         "Description": "Use 'also' to mean 'additionally.' Do not use 'also' to mean 'alternatively.'",
#         "Rules": [
#             "Use 'also' to add more information.",
#             "Do not use 'also' as a substitute for 'alternatively' or 'either.'"
#         ],
#         "Examples of Good Writing": [
#             "Quota notifications are sent to the event management system and also configured as SNMP traps.",
#             "The wizard also creates the igroup and maps the LUN to the host.",
#             "SMB automatic node referrals are also known as autolocation."
#         ],
#         "Examples of Bad Writing": [
#             "You can use System Manager to provision storage. If preferred, you can also use the ONTAP CLI.",
#             "Also, you might want to try restoring from a backup if the primary method fails.",
#             "You can also select different deployment methods depending on your preference."
#         ]
#     }, 
#     'And/Or': {
#         "Title": "And/Or",
#         "Description": "Avoid using 'and/or.' Instead, use 'and' or use 'or.'",
#         "Rules": [
#             "Use 'and' when both options apply.",
#             "Use 'or' when only one option applies.",
#             "Avoid using the ambiguous phrase 'and/or.'"
#         ],
#         "Examples of Good Writing": [
#             "You can use a combination of compression and compaction to increase your storage efficiency.",
#             "ONTAP runs inline deduplication or background deduplication depending on the model.",
#             "You can control access using System Manager or the CLI."
#         ],
#         "Examples of Bad Writing": [
#             "You can use compression and/or compaction to increase your storage efficiency.",
#             "ONTAP automatically runs inline deduplication and/or background deduplication.",
#             "You can control access using System Manager and/or the CLI."
#         ]
#     }, 
#     'By Using (versus Using or With)': {
#         "Title": "By Using (versus Using or With)",
#         "Description": "Only begin a sentence with 'using' or 'with' if followed by a product name.",
#         "Rules": [
#             "Use 'by using' when referring to a process or tool.",
#             "Using' or 'with' should only begin a sentence if immediately followed by a product name."
#         ],
#         "Examples of Good Writing": [
#             "By using SnapDrive, you can manage virtual disks.",
#             "With FlexCache, you can improve performance in hybrid environments.",
#             "You can create a volume by using the volume create command."
#         ],
#         "Examples of Bad Writing": [
#             "Using the volume create command, you can create a volume.",
#             "Using SnapDrive, you can manage virtual disks.",
#             "With the volume create command, you can create a volume."
#         ]
#     }, 
#     'Ensure (versus Confirm or Verify)': {
#         "Title": "Ensure (versus Confirm or Verify)",
#         "Description": "Use 'ensure' to mean 'to make certain.' Use 'confirm' or 'verify' to mean double-checking something.",
#         "Rules": [
#             "Use 'ensure' when advising the reader to make sure something is done.",
#             "Use 'confirm' or 'verify' when asking the reader to check an existing condition.",
#             "Do not use 'ensure' to imply a promise or guarantee."
#         ],
#         "Examples of Good Writing": [
#             "Ensure that there is sufficient white space around illustrations.",
#             "Verify that NFS is set up on the cluster.",
#             "Confirm that the firewall settings are correctly configured."
#         ],
#         "Examples of Bad Writing": [
#             "Use Cloud Manager to ensure that you can provision NFS volumes.",
#             "Ensure that the backups are working properly before proceeding.",
#             "Ensure that the system will automatically recover from a power outage."
#         ]
#     }, 
#     'If Not': {
#         "Title": "If Not",
#         "Description": "Do not use 'if not' by itself to refer to the previous sentence.",
#         "Rules": [
#             "Avoid using 'if not' as a sentence fragment.",
#             "Use clear, complete clauses when referencing alternative conditions."
#         ],
#         "Examples of Good Writing": [
#             "Verify that the computer is off. If it's not, turn it off.",
#             "If these certificates are not pre-installed, you will need to install them.",
#             "By default, ONTAP uses the NIS domain if set, or the DNS domain if it's not."
#         ],
#         "Examples of Bad Writing": [
#             "The computer should be off. If not, turn it off.",
#             "These certificates might be pre-installed. If not, you need to install them.",
#             "ONTAP uses the NIS domain if set; if not, the DNS domain is used."
#         ]
#     }, 
#     'Prerequisites': {
#         "Title": "Prerequisites",
#         "Description": "A list of prerequisites should begin with a 'Before you begin' heading.",
#         "Rules": [
#             "Always use the heading 'Before you begin' for prerequisites.",
#             "Avoid other headers like 'Requirements' or 'What you'll need'."
#         ],
#         "Examples of Good Writing": [
#             "Before you begin, ensure that your system meets the following requirements.",
#             "Before you begin, make sure all necessary cables are connected.",
#             "Before you begin, confirm that you have access to the appropriate permissions."
#         ],
#         "Examples of Bad Writing": [
#             "What you'll need before starting.",
#             "Requirements for installation.",
#             "Prerequisites for setting up the system."
#         ]
#     }, 
#     'Since': {
#         "Title": "Since",
#         "Description": "Use 'since' to indicate a passage of time. Do not use 'since' to mean 'because.'",
#         "Rules": [
#             "Use 'since' when referring to the time passed between two events.",
#             "Use 'because' when explaining the reason for something."
#         ],
#         "Examples of Good Writing": [
#             "Beginning with ONTAP 9.5, you can view changes made since your last successful login.",
#             "The system records only changes made since the last backup.",
#             "This process has been automated since version 3.0."
#         ],
#         "Examples of Bad Writing": [
#             "The upgrade fails since the target version is unsupported.",
#             "Since the root volume's security style is applied by default, it should be set to NTFS.",
#             "Since the server was restarted, the process needs to be run again."
#         ]
#     }, 
#     'That (versus Which or Who)': {
#         "Title": "That (versus Which or Who)",
#         "Description": "Use 'that' at the beginning of a clause that's necessary for the sentence to make sense. Use 'which' at the beginning of a clause that adds supporting information. Use 'who' when referring to a person.",
#         "Rules": [
#             "Use 'that' for essential clauses.",
#             "Use 'which' for non-essential clauses, and place a comma before it.",
#             "Use 'who' for clauses referring to people."
#         ],
#         "Examples of Good Writing": [
#             "To learn more about features that are supported on your platform, see the Hardware Universe.",
#             "The storage system, which has been in use for years, needs an upgrade.",
#             "The engineer who set up the system will perform the update."
#         ],
#         "Examples of Bad Writing": [
#             "The customers which do not want to manage their own storage can use professional services.",
#             "The system, that has been reliable for years, now requires maintenance.",
#             "Professional services is the best choice for customers who that prefer not to upgrade their software on their own."
#         ]
#     }
#     }, 
#     'misc_guidelines': {
#     'Capitalization': {
#         "Title": "Capitalization",
#         "Description": "Use sentence-style capitalization. Only capitalize the first word of a sentence and proper nouns.",
#         "Rules": [
#             "Capitalize the first word of a sentence, heading, or title.",
#             "Capitalize proper nouns, including product names.",
#             "Do not use all caps or excessive capitalization for emphasis."
#         ],
#         "Examples of Good Writing": [
#             "Display file or inode usage.",
#             "Configure volumes to provide more space automatically.",
#             "Snapshot copies work with FlexClone files and LUNs."
#         ],
#         "Examples of Bad Writing": [
#             "Display File or Inode Usage.",
#             "Configure Volumes to Automatically Provide More Space.",
#             "How snapshot copies work with flexclone files and luns."
#         ]
#     }, 
#     'Numbers': {
#         "Title": "Numbers",
#         "Description": "Use Arabic numerals for 10 and all numbers greater than 10, with some exceptions.",
#         "Rules": [
#             "Use words for numbers less than 10.",
#             "Use numerals for 10 and higher.",
#             "If a sentence starts with a number, write it out.",
#             "Use words for approximate numbers (e.g., 'hundreds of users')."
#         ],
#         "Examples of Good Writing": [
#             "Two paths are required for redundancy.",
#             "If your system memory is less than 16 GB, you can have a maximum of 8 sessions.",
#             "You should have a minimum of two LIFs for each host."
#         ],
#         "Examples of Bad Writing": [
#             "You should have a minimum of 2 LIFs for each host.",
#             "2 paths are required for redundancy.",
#             "If your system memory is less than 16 GB, you can have a maximum of eight sessions."
#         ]
#     }, 
#     'Future Functionality': {
#         "Title": "Future Functionality",
#         "Description": "Avoid writing about future functionality or software releases.",
#         "Rules": [
#             "Do not refer to features or releases that haven't been implemented yet.",
#             "Avoid phrases like 'future release,' 'next version,' or 'upcoming feature'."
#         ],
#         "Examples of Good Writing": [],
#         "Examples of Bad Writing": [
#             "This functionality will be available in a future release of ONTAP.",
#             "FlexCache will be enhanced in a future software version.",
#             "In the next release, we will add new disaster recovery features."
#         ]
#     }, 
#     'Trademarks': {
#         "Title": "Trademarks",
#         "Description": "Do not use the trademark symbol. Do not use trademark terms in the plural, possessive form, or as a verb. Always spell and capitalize trademarks correctly.",
#         "Rules": [
#             "Do not use trademark symbols (®, ™, etc.).",
#             "Do not make trademark terms plural or possessive.",
#             "Do not use trademarks as verbs.",
#             "Follow the exact spelling and capitalization of each trademark."
#         ],
#         "Examples of Good Writing": [
#             "ONTAP provides robust data management features.",
#             "FlexClone volumes allow for rapid cloning of datasets.",
#             "NetApp Keystone provides flexible consumption models for cloud services."
#         ],
#         "Examples of Bad Writing": [
#             "ONTAP® provides robust data management features.",
#             "FlexClone® volume's cloning abilities make it popular.",
#             "The Snapshots were FlexCloned to different systems."
#         ]
#     }
#   }
# }

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
