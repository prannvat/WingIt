from openai import OpenAI

with open("openai_key.txt") as f:
    API_Key_From_File = f.read()[:-1]

client = OpenAI(
  api_key=API_Key_From_File
)

prompt = """
The text to be analysed is:
"Sir Alex Ferguson, the iconic figure of Manchester United, has opened up about the void left in his life post-retirement, more than a decade after he bid farewell to his illustrious career at Old Trafford. His candid thoughts have reignited discussions on Manchester United's trajectory since his departure, a journey some say has been in the shadow of Ferguson's unprecedented success."

The task is:
Construct a large list of at least 2 elements, up to 8 elements in size, highlighting the negative or positive tone within the text. For each point, provide a summary of up to 20 words about the tone around the particular point, and a value from -1.0 to 1.0 stating the intensity of the tone, where -1.0 is extreme negative tone, 1.0 is extreme positive tone, 0.0 is completely neutral, and scalar values between -1.0 and 1.0 refer to different levels of intensity.

Return this list in JSON format as follows:
[
    {"point": "word word word word", "intensity": <DECIMAL>}
]
"""

completion = client.chat.completions.create(
  model="gpt-4o-mini",
  store=True,
  messages=[
    {"role": "user", "content": prompt}
  ]
)

response = completion.choices[0].message.content
print(response)
