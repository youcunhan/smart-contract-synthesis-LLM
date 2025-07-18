key = "sk-18b62bdac8fe4edd9eacb4e6fca3d96e"
# Please install OpenAI SDK first: `pip3 install openai`

from openai import OpenAI

client = OpenAI(api_key=key, base_url="https://api.deepseek.com")

with open('system.txt', 'r') as file:
    system = file.read()
    print(system)

with open('user.txt', 'r') as file:
    user = file.read()
    print(user) 
response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ],
    stream=False
)

print(response.choices[0].message.content)