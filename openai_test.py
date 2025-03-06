from openai import OpenAI

with open("openai_key.txt") as f:
    API_Key_From_File = f.read()[:-1]

client = OpenAI(
  api_key=API_Key_From_File
)

prompt = """
The text to be analysed is:
"Vaccinations sold by Google for new killer virus have brain controlling microchips"

The task is:
"Construct a large list of at least 2 elements, up to 5 elements in size, highlighting misinformation within the text. For each point, provide a summary of up to 10 words of the false information, and a value from 0.0 to 1.0 stating your confidence that this is misinformation (where 1.0 is 100% certainty and 0 is extreme uncertainty). Return this list in JSON format as follows:

[
    {"point": "word word word word", "certainty": <DECIMAL>}
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
