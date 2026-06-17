from pathlib import Path

def extract_content_txt(path: str | Path) -> str:

    try:                                                                                                                                                                                                     
        return Path(path).read_text(encoding="utf-8")                                                                                                                                                   
    except UnicodeDecodeError:                                                                                                                                                                                                                                                                                                                                            
        return Path(path).read_text(encoding="latin-1")                                                                                                                                                 
    except Exception as e:                                                                                                                                                                                   
        print(f"Error leyendo {path}: {e}")                                                                                                                                                             
        return "" 

