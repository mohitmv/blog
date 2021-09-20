# import markdown

import requests, json

with open("_posts/2021-9-10-CTwik-General-Purpose-Hot-Patcher-For-Cpp.md") as fd:
    content = fd.read()

headers = {
    'Accept': 'application/vnd.github.v3+json',
}

data = json.dumps({"text": content})

response = requests.post('https://api.github.com/markdown', headers=headers, data=data)

# print(response)

# print(response.text)

content = response.text


# content = markdown.markdown(content)

with open("/tmp/index.html", "w") as fd:
    fd.write(content)
