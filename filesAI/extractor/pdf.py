import fitz 

# Extraer el contenido de los ficheros para tratarlo

def extract_content_pdf(path : str) -> str:

    text = ""

    with fitz.open(path) as pdf:
        for page in pdf:
            text += page.get_text()
    return text.strip()
