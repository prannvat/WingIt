from openai import OpenAI
import json

with open("openai_key.txt") as f:
    API_Key_From_File = f.read()[:-1]

client = OpenAI(
  api_key=API_Key_From_File
)

# TEXT NEGATIVE EXAMPLE WRITTEN BY MICROSOFT COPILOT
# THIS IS PURE TEST DATA, NOT FROM A REAL NEWS ARTICLE
example_negative = """
The school day started with an ominous grey sky looming overhead, reflecting the atmosphere within. Classrooms were filled with monotonous drone of uninterested teachers, and students sat slumped in their chairs, barely awake. The once vibrant playground was now littered with trash, the laughter of children replaced by complaints and arguments. Lunch served in the cafeteria was a tasteless, unappetizing mess, and long queues only added to the frustration. The hallways echoed with the occasional sound of an argument or a distant cry, making it clear that morale was at an all-time low. The school felt more like a prison, with the heavy burden of rules and regulations crushing any spark of joy or creativity.
"""

# TEXT POSITIVE EXAMPLE WRITTEN BY MICROSOFT COPILOT
# THIS IS PURE TEST DATA, NOT FROM A REAL NEWS ARTICLE
example_positive = """
The school day began with a refreshing crispness in the air, setting a lively tone for the day ahead. Classrooms buzzed with the enthusiastic chatter of students eager to learn, and teachers passionately engaged with their pupils, sparking curiosity and excitement. The playground was alive with the joyous sounds of laughter and playful banter, as children ran and played energetically. The cafeteria served a variety of delicious and nutritious meals, and the smell of freshly cooked food wafted through the air. Hallways were filled with the friendly greetings and animated conversations of students and staff, creating a sense of community and warmth. The school was a haven of learning and growth, where rules provided structure, allowing creativity and happiness to flourish.
"""

def is_float(string):
    try:
        float(string)
        return True
    except ValueError as e:
        return False

def ai_json_response_is_valid(response):
    # Takes a response from gpt-4o-mini and checks if this is in the correct JSON format
    # Returns either:
    # True, A decoded data structure, either a list or dictionary
    # False, Error message string
    
    size = len(response)
    # The AI has given something that isn't in the correct JSON format
    if size < 10:
        return False, "ERROR: Data is not in a valid JSON format, response is too short"
    if response[0:7] != "```json" or response[-3:] != "```":
        return False, "ERROR: Data is not in a valid JSON format, the first 7 characters in the response must be ```json and last three must be ```"
    extracted = response[7:(size-3)]

    # Convert the AI response into a usable JSON
    try:
        data = json.loads(extracted)
    except json.JSONDecodeError as e:
        return False, "ERROR: Invalid JSON: " + e.msg
    
    return True, data
    
def tone_analyse_response_is_valid(response):
    success, data = ai_json_response_is_valid(response)
    if not success:
        # data is error message here
        return False, data
    # Otherwise data is a data structure from JSON
    
    # AI has returned a dictionary instead of a list
    if type(data) != list:
        return False, "ERROR: The returned JSON must be a list of data, but a dictionary was provided"
        
    if len(data) == 0:
        return False, "ERROR: The returned JSON list of data was empty"
        
    # Validate all list elements to ensure they're all dictionaries of the correct format
    for element in data:
        is_dict = type(element) == dict
        if not is_dict:
            return False, "ERROR: The returned JSON list contained an element which was not a dictionary"
            
        if "point" not in element:
            return False, "ERROR: The returned JSON list contained a dictionary which did not have a point"
            
        point_text = element["point"]
        if not type(point_text) == str:
            return False, "ERROR: The returned JSON list contained a dictionary which had a point that wasn't a valid string"
            
        if len(point_text) < 10:
            return False, "ERROR: The returned JSON list contained a dictionary which had a point that was too short"
            
        if "intensity" not in element:
            return False, "ERROR: The returned JSON list contained a dictionary which did not have an intensity"
            
        value_decimal = element["intensity"]
        if not is_float(value_decimal):
            return False, "ERROR: The returned JSON list contained a dictionary which had an intensity which was not a valid decimal"
            
        value = float(value_decimal)
        if (value < -1) or (value > 1):
            return False, "ERROR: The returned JSON list contained a dictionary which had an intensity which was not in the range from -0.0 to 1.0"
            
    # After this, the structure is validated and can be used safely
    return True, data
    

def tone_analyse(text):
    prompt = (
    """
    The task is:
    Analyse text stated below, by constructing a large list of at least 2 elements, up to 8 elements in size, highlighting the negative or positive tone within the text. For each point, provide a summary of up to 20 words about the tone around the particular point, and a value from -1.0 to 1.0 stating the intensity of the tone, where -1.0 is extreme negative tone, 1.0 is extreme positive tone, 0.0 is completely neutral, and scalar values between -1.0 and 1.0 refer to different levels of intensity.

    Return this list in JSON format as follows:
    [
        {"point": "word word word word", "intensity": <DECIMAL>}
    ]

    The text to be analysed is: """
    + text)
    
    history = []
    history += [{"role": "system", "content": prompt}]
    
    valid_response = False
    message_count = 0
    
    while (not valid_response) and (message_count < 3):
        completion = client.chat.completions.create(
          model="gpt-4o-mini",
          store=True,
          messages=history
        )
        response = completion.choices[0].message.content
        
        # Check that the response from the AI is valid
        valid_response, data = tone_analyse_response_is_valid(response)
        
        history += [{"role":"assistant", "content":response}]
        if not valid_response:
            history += [{"role":"system", "content":data}]
        
        message_count += 1
        
    # Here, 'data' is a redundant error message string
    # 'history' can be used for further checking
    if not valid_response:
        return None
        
    # Here, 'data' is a list containing dictionaries of valid data
    for element in data:
        point = element["point"]
        intensity = element["intensity"]
        print(point, intensity)
    

tone_analyse(example_negative)
