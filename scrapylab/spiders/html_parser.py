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

        titles = soup.find_all('title')
        paragraphs = soup.find_all('p')

        results = {
            "filename": filename,
            "titles": titles,
            "paragraphs": paragraphs
        }
        parsed_contents.append(results)
        print(parsed_contents)


with open(save_filename, "w", encoding="utf-8") as f:
    f.write(str(parsed_contents))
    print(f"Contents saved to {save_filename}")
