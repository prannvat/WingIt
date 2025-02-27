from openai import OpenAI

with open("openai_key.txt") as f:
    API_Key_From_File = f.read()[:-1]

client = OpenAI(
  api_key=API_Key_From_File
)

prompt = "Write a 4 line sea shanty about a potato"

completion = client.chat.completions.create(
  model="gpt-4o-mini",
  store=True,
  messages=[
    {"role": "user", "content": prompt}
  ]
)

response = completion.choices[0].message.content
print(response)
