import sqlite3
from cryptography.hazmat.primitives import hashes

def calculate_hash(block):
    # Converto block to bytes
    block = block.encode('utf-8')
    digest = hashes.Hash(hashes.SHA256())
    digest.update(block)
    return digest.finalize()
    
def main():
    PDF_DIR = '/data/'
    
    # Connect to db
    conn = sqlite3.connect('/code/db/db.sqlite3')
    c = conn.cursor()
    # Insert data
    for i in range(len(codes)):
        c.execute('INSERT INTO site_test_results (code, file_path) VALUES (?, ?)', (calculate_hash(codes[i]), PDF_DIR + 'test' + str(i+1) + '.pdf'))

    for service in services:
        c.execute('INSERT INTO site_services (name, description) VALUES (?, ?)', (service[0], service[1]))

    for review in reviews:
        c.execute('INSERT INTO site_reviews (name, email, message) VALUES (?, ?, ?)', (review[0], review[1], review[2]))

    conn.commit()
    # Close connection
    conn.close()
    print('Database initialized')


codes = ['AjBq7G3f8B6G8j09', '2Em6d94gF74BfG23', '09oJ8f7f4C2J5gSd']

services = [
    ("Cardiology", "Cardiology is a branch of medicine that deals with disorders of the heart and blood vessels."),
    ("Dermatology", "Dermatology is the branch of medicine dealing with the skin."),
    ("Neurology", "Neurology is the branch of medicine dealing with the diagnosis and treatment of all categories of conditions and disease involving the brain, the spinal cord and the peripheral nerves."),
    ("Physiotherapy", "Physiotherapy aims to help patients to fully recover their movements after a fall, surgery or illness that has affected their musculoskeletal system and improve their life quality."),
    ("Psychiatry", "Psychiatry is the medical specialty devoted to the diagnosis, prevention, and treatment of mental disorders."),
    ("Radiology", "Radiology is a branch of medicine that uses imaging technology to diagnose and treat disease."),
    ("Urology", "Urology is a branch of medicine that deals with the urinary tract."),
    ("Gastroenterology", "Gastroenterology is the branch of medicine focused on the digestive system and its disorders."),
    ("Gynecology", "Gynecology is the area of medicine that involves the treatment of women's diseases, especially those of the reproductive organs."),
    ("Ophthalmology", "Ophthalmology is a surgical subspecialty within medicine that deals with the diagnosis and treatment of eye disorders."),
    ("Orthopedics", "Orthopedics is the branch of surgery concerned with conditions involving the musculoskeletal system."),
    ("Pediatrics", "Pediatrics is the branch of medicine that involves the medical care of infants, children, adolescents, and young adults."),
    ("Pulmonology", "Pulmonology is a medical specialty that deals with diseases involving the respiratory tract."),
    ("Rheumatology", "Rheumatology is a branch of medicine devoted to the diagnosis and management of disorders whose common feature is inflammation in the bones, muscles, joints, and internal organs."),
    ("Anesthesiology", "Anesthesiology is the medical specialty concerned with the total perioperative care of patients before, during and after surgery."),
    ("Dentistry", "Dentistry is the branch of medicine focused on the teeth, gums, and mouth."),
]

reviews = [
    ("D. Lurdes", "lurdinhas@gmail.com", "I had a great experience with Dr. John Doe. He was very professional and friendly. I would definitely recommend him to my friends and family."),
    ("John", "johnthegamer@hotmail.com", "I had a great experience with Dr. Steve Harvey. He was very gentle."),
    ("Jane", "chelsea64@protonmail.com", "I had a great experience with Dr. Phill. He was very professional and friendly."),
    ("Mugabe", "lacaca@live.com.ng", "Excelente clínica, muito bem equipada e com profissionais de excelência. Recomendo!"),
    ("Valério", "valeriobranco@mlk.bi", "Obrigado Dr. Abel por me salvar de um AVC!"),
    ("Hasbulla", "jubiscleitom@mog.ru", "Ok."),
]


if __name__ == "__main__":
    main()