from pdf2image import convert_from_path
import numpy as np
from groq import Groq
import easyocr
import json
import re
import os
import concurrent.futures
def extract_text_from_pdf(pdf_path, output_lang='fr'):
    # Convertir les pages du PDF en images
    images = convert_from_path(pdf_path, poppler_path=r'C:\Users\Administrateur\Downloads\Release-24.08.0-0\poppler-24.08.0\Library\bin')
    
    # Initialiser le lecteur EasyOCR
    reader = easyocr.Reader([output_lang])
    
    # Conteneur pour le texte extrait
    extracted_text = []
    
    # Lire chaque image et extraire le texte
    for i, image in enumerate(images):
        print(f"Traitement de la page {i + 1}...")
        # Convertir l'image PIL en tableau NumPy
        image_np = np.array(image)
        text = reader.readtext(image_np, detail=0)
        extracted_text.append("\n".join(text))
    
    # Retourner le texte combiné
    return "\n\n".join(extracted_text)
def extractJSONFromGrokIA(output_text):
    client = Groq(
    api_key="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",
    )
    prompt  = f"""
        Extract the following fields from the given resume text and return them in the specified JSON format:
        name: The candidate's full name.
        email: The candidate's email address.
        phone: The candidate's phone number.
        skills: A list of skills mentioned in the resume.
        experience: A list of job experiences. Each job should include:
        job_title: The title of the job.
        company: The name of the company.
        start_date: The start date of the job (if available).
        end_date: The end date of the job (or "Present" if ongoing).
        responsibilities: A summary of the responsibilities or achievements in the job.
        education: A list of educational qualifications. Each qualification should include:
        degree: The degree obtained.
        institution: The name of the educational institution.
        start_date: The start date of the program (if available).
        end_date: The end date of the program.
        certifications: A list of certifications. Each certification should include:
        name: The name of the certification.
        issuing_organization: The organization that issued the certification.
        issue_date: The date the certification was issued (if available).
        location: The candidate's current location (if mentioned).

        Resume text:
        {output_text}
        """
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        model="llama3-8b-8192",
    )

    # Extraire la réponse du chat
    json_pattern = r'\{.*\}'
    match = re.search(json_pattern, chat_completion.choices[0].message.content, re.DOTALL)

    if match:
        # Extraire le JSON
        json_data = match.group(0)
        try:
            # Charger le JSON extrait
            parsed_json = json.loads(json_data)
            return parsed_json
        except json.JSONDecodeError as e:
            print(f"Erreur de décodage JSON: {e}")
    else:
        print("Aucun JSON trouvé.")
# Fonction pour traiter un fichier PDF
def process_pdf(pdf_path):
    output_text = extract_text_from_pdf(pdf_path, output_lang='fr')
    json_data = extractJSONFromGrokIA(output_text)
    return json_data

# Fonction principale pour parcourir le dossier et traiter les fichiers PDF
def process_cv_folder(folder_path):
    json_results = []
    
    # Liste les fichiers PDF dans le dossier
    pdf_files = [f for f in os.listdir(folder_path) if f.lower().endswith('.pdf')]
    pdf_paths = [os.path.join(folder_path, f) for f in pdf_files]
    
    # Utilisation d'un pool de 8 threads pour traiter les fichiers
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        # Mappe chaque fichier à la fonction process_pdf
        results = executor.map(process_pdf, pdf_paths)
        
        # Collecte les résultats
        json_results.extend(results)
    
    # Sauvegarde les résultats dans un fichier JSON
    with open('banque-cv.json', 'w', encoding='utf-8') as json_file:
        json.dump(json_results, json_file, ensure_ascii=False, indent=4)

# Appel de la fonction principale pour traiter les CV
process_cv_folder('Banque-CV')