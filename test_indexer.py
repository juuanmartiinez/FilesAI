from filesAI.scanner.walker import get_download_path, scan_directory                                                                                                                                         
from filesAI.indexer.database import init_db, insert_files, count_files, update_sql_content 
from filesAI.extractor.extractor import extract_content                                                                                                                                 
                                                                                                                                                                                                                  
init_db()                                                                                                                                                                                                    
                                                                                                                                                                                                                  
downloads = get_download_path()                                                                                                                                                                              
files = scan_directory(downloads)                                                                                                                                                                            
                                                                                                                                                                                                            
insert_files(files)   

for file in files:                                                                                                                                                                                           
        
        content = extract_content(file["path"])                                                                                                                                                                  
                                                                                                                                                                                                                  
        if content:                                                                                                                                                                                              
            update_sql_content(file["path"], content)                                                                                                                                                            
            print(f"Extraído contenido de: {file['name']}")

print(f"Archivos guardados: {count_files()}")