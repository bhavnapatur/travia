import gradio as gr
import os
import requests
import dateparser
from datasets import load_dataset
from datetime import datetime, timedelta
from sentence_transformers import SentenceTransformer
from huggingface_hub import InferenceClient




file_path = 'requirements.txt'
dataset = load_dataset("text", data_files = "requirements.txt")
with open("requirements.txt", "r", encoding = "utf-8") as file:
    file_path = file.read()
    print(file_path)

client = InferenceClient("HuggingFaceH4/zephyr-7b-beta")

def match_europe(scores):
    a = scores.count("A")
    b = scores.count("B")
    c = scores.count("C")
    d = scores.count("D")
    e = scores.count("E")
    if a >= 5:
        return "Paris, France"
    elif b >=5:
        return "Tokyo, Japan"
    elif c >= 5:
        return "Bali, Indonesia"
    elif d >= 5:
        return "New York City, USA"
    elif e >=5:
        return "Barcelona, Spain"
    else:
        if  a > b and a > c and a > d and a > e:
            return "Paris, France"
        elif b > a and b > c and b > d and b > e:
            return "Tokyo, Japan"
        elif c > a and c > b and c > d and c > e:
            return "Bali, Indonesia"
        elif d > a and d > b and d > c and d > e:
            return "New York City, USA"
        elif e > a and e > b and e > c and e > d:
            return "Barcelona, Spain"
        else:
            return "Sydney, Australia"
questions_europe = [
    ("1. What kind of people do you enjoy meeting?", [
        ("A", "Locals who know the city's deep history and culture."),
        ("B", "Curious travelers and polite locals with cool stories."),
        ("C", "Easygoing, spiritual people who live simply."),
        ("D", "Bold, confident people chasing big dreams."),
        ("E", "Social butterflies who love music and street life.")
    ]),
    ("2. What type of souvenir do you want to bring home?", [
        ("A", "A vintage print from a street artist."),
        ("B", "A quirky gadget or handmade oragami."),
        ("C", "A handmade bracelet and beach sarong."),
        ("D", "A t-shirt from a local streetwear brand."),
        ("E", "A flamenco fan or mosaic-tiled trinket.")
    ]),
    ("3. Choose an activity for your ideal day.", [
        ("A", "Browsing a weekend market,then sipping espresso at a corner café."),
        ("B", "Eating noodles in a hidden alley, then watching a city sunset from a rooftop temple."),
        ("C", "Surfing, spa treatments, or a sunrise hike."),
        ("D", "Exploring thrift shops, then catching a pop-up art show downtown."),
        ("E", "Dancing on the beach and exploring local street art.")
    ]),
    ("4. What kind of weather do you prefer?", [
        ("A", "Mild and breezy with lots of sunshine."),
        ("B", "Cool evenings and warm days."),
        ("C", "Hot and tropical with ocean breezes."),
        ("D", "Crisp air with clear skies."),
        ("E", "Warm with a chance of an evening breeze.")
    ]),
    ("5. You stumble upon a secret cafe. What do you order?", [
        ("A", "A delicate pastry no one else seems to know about."),
        ("B", "A spicy noodle dish served with an unusual garnish."),
        ("C", "A  refreshing tropical drink with exotic fruits."),
        ("D", "A hearty bagel sandwich perfect for people on the go."),
        ("E", "A colorful shaved ice dessert topped with unexpected flavors.")
    ])
]

def create_quiz(questions, match_func):
    with gr.Blocks(css = "#rounded-btn {border-radius: 12px; padding: 10px 20px}")as demo:
        answers = []
        with gr.Column():
            for q, opts in questions:
                choices = [opt[1] for opt in opts]
                answers.append(gr.Radio(choices=choices, label=q))
            result = gr.Textbox(label="You should travel to...")
            btn = gr.Button("Find Ideal Location", elem_id = "rounded-btn")

    def evaluate(*vals):
        codes = []
        for i, val in enumerate(vals):
            if val is None:
                codes.append("C")
            else:
                codes.append(next(opt[0] for opt in questions[i][1] if opt[1] == val))
        return match_func(codes)

    btn.click(evaluate, inputs=answers, outputs=result)
    return answers, result, btn

with gr.Blocks() as demo:
    gr.Markdown("Quiz")

    with gr.Tabs():
        with gr.TabItem("Quiz"):
            create_quiz(questions_europe, match_europe)


travel_guide_output = ""

def parse_date(date_str):
    if not date_str:
        return None
    parsed_date = dateparser.parse(date_str, settings={'PREFER_DATES_FROM': 'future'})
    return parsed_date if parsed_date else None

def respond(destination, transportation, date, preference, include_options, minors):
    global travel_guide_output
    
    travel_date = parse_date(date)

    prompt = f"""
    **Travel Plan Details:**
        - **To:** {destination}
    - **Transportation:** {transportation}
    - **Travel Date:** {date}
    - **Budget Preference:** {preference}
    - **Minors included:** {minors}
    - **Additional Info:** {', '.join(include_options) if include_options else 'None'}
    """
    travel_guide_output = prompt
    print("respond", travel_guide_output)
    return prompt

    
    # try:
    #     response = client.chat_completion(messages=[{"role": "user", "content": prompt}])
    #     print(response)
    #     travel_guide_output = response
    #     print(travel_guide_output)
    #     return response['choices'][0]['message']['content'].strip()
    # except Exception as e:
    #     return f"An error occurred: {e}"



def chatbot_respond(message, chat_history):
    global travel_guide_output
    print("chatbot_respond", travel_guide_output)
    
    if not travel_guide_output:
        travel_guide_output = "No travel guide has been generated yet. Please enter your travel details first."
    
    system_message = f"""
    You are a chatbot that helps people plan trips. Use the following details to assist them: {travel_guide_output}
    Based on how long they are going on their trip, give a day by day explanation, including budget as well using the details provided. 
    
    Bold important information for it to be easy on the users eyes.
    """


    messages = []
    messages.append({"role": "system", "content": system_message})

    if chat_history:
        messages.extend(chat_history)
    try:
        response = client.chat_completion(messages)
        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        return f"An error occurred: {e}"

with gr.Blocks(theme='shivi/calm_seafoam') as app:
    gr.Markdown("# 🌍 Travia")
    gr.Markdown("Welcome to Travia! We are here to help you plan your trip so that you can enjoy a vacation stress-free!")
    
    with gr.Tabs():
            with gr.TabItem("Quiz"):
                create_quiz(questions_europe, match_europe)

            with gr.TabItem("Travel Chatbot"):
                with gr.Row():
                    with gr.Column(scale=1):
                        destination_input = gr.Textbox(label="Travel Destination")
                        transportation_dropdown = gr.Dropdown(["Bus", "Plane", "Train"], label="Preferred Transportation")
                        date_input = gr.Textbox(label="Travel Duration (e.g. 1 week)")
                        preference_dropdown = gr.Dropdown(["Luxurious", "Cheap", "Balanced"], label="Budget Preferences")
                        minors_included = gr.Dropdown(["Yes", "No"], label="Are there minors on the trip?")
                        include_checkboxes = gr.CheckboxGroup([
                            "Hotels", "Nearby Attractions", "Basic Phrases in the Language", "Popular Foods"], label="Include in Chat")
                        
                        send_button = gr.Button("Generate Guide")

                    with gr.Column(scale=2):
                        output_box = gr.Markdown(label="AI Output", value="Please enter your travel details and click 'Generate Guide'.")

                    with gr.Column(scale=1):
                        gr.ChatInterface(
                        chatbot_respond,
                        type="messages",
                        title="Travia",
                        examples=[
                        "I would like to travel to a place, but I don't know how to plan it",
                        "I need to budget for my trip.",
                        "I want to learn more about the language, food, and culture of the place I'm traveling to."
                        ])

                send_button.click(
                respond,
                inputs=[destination_input, transportation_dropdown, date_input, preference_dropdown, include_checkboxes, minors_included],
                outputs=[output_box]
        )

    app.launch(debug = True)
