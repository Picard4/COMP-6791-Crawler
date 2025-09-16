from bs4 import BeautifulSoup
from os import listdir

dir_name = "HTML-Files"
files = listdir(f"./{dir_name}")
html_files = [filename for filename in files if filename.endswith(('.html'))]
parsed_contents = []
save_filename = "parsed_data.txt"

for filename in html_files:
    with open(f'./{dir_name}/{filename}', 'r', encoding='utf-8') as file:
        html_content = file.read()
        soup = BeautifulSoup(html_content, "html.parser")

        title = soup.find('title')
        body = soup.find('body')

        title_parsed = ""
        body_parsed = ""
        if title:
            title_parsed = title.findAll(text=True, recursive=False)
        if body:
            body_parsed = body.findAll(text=True, recursive=False)

        results = {
            "filename": filename,
            "title": title_parsed,
            "body": body_parsed
        }
        parsed_contents.append(results)


with open(save_filename, "w", encoding="utf-8") as f:
    f.write(str(parsed_contents))
    print(f"Contents saved to {save_filename}")
