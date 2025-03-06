from openai import OpenAI

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

prompt = ("The text to be analysed is:" + example_positive + 
"""
The task is:
Construct a large list of at least 2 elements, up to 8 elements in size, highlighting the negative or positive tone within the text. For each point, provide a summary of up to 20 words about the tone around the particular point, and a value from -1.0 to 1.0 stating the intensity of the tone, where -1.0 is extreme negative tone, 1.0 is extreme positive tone, 0.0 is completely neutral, and scalar values between -1.0 and 1.0 refer to different levels of intensity.

Return this list in JSON format as follows:
[
    {"point": "word word word word", "intensity": <DECIMAL>}
]
""")

completion = client.chat.completions.create(
  model="gpt-4o-mini",
  store=True,
  messages=[
    {"role": "user", "content": prompt}
  ]
)

response = completion.choices[0].message.content
print(response)
