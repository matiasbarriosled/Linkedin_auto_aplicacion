from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.firefox import GeckoDriverManager
from dotenv import load_dotenv
import time
import os

load_dotenv("secrets.env")

LINKEDIN_EMAIL = os.getenv("LINKEDIN_EMAIL")  
LINKEDIN_PASSWORD = os.getenv("LINKEDIN_PASSWORD")

JOB_TITLES = [
    "Data Engineer",
    "Machine learning engineer",
    "AI Developer"
]

LOCATION = "Argentina"
MAX_JOBS_PER_SEARCH = 3 

def initialize_driver():
    """inicializa y configura el webDriver de firefox."""
    options = webdriver.FirefoxOptions()
    
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("start-maximized")

    service = Service(GeckoDriverManager().install())
    driver = webdriver.Firefox(service=service, options=options)
    return driver

def linkedin_login(driver, email, password):
    """ingreso de credenciales a Linkedin"""
    try:
        driver.get("https://www.linkedin.com/login")
        wait = WebDriverWait(driver, 10)

        email_field = wait.until(EC.presence_of_element_located((By.ID, "username")))
        email_field.send_keys(email)

        password_field = driver.find_element(By.ID, "password")
        password_field.send_keys(password)

        driver.find_element(By.XPATH, "//button[@type='submit']").click()

        wait.until(EC.url_contains("/feed"))
        print("-> Inicio de sesión exitoso.")
        return True
    except Exception as e:
        print(f"Verificar credenciales. Error: {e}")
        return False

def search_jobs(driver, job_title, location):
    """Realiza la búsqueda de empleo y aplica el filtro 'Solicitud sencilla'."""
    wait = WebDriverWait(driver, 10)

    try:
        driver.get("https://www.linkedin.com/jobs/search/")

        job_search_field = driver.find_element(By.CLASS_NAME, "jobs-search-box__text-input")
        job_search_field.clear()
        job_search_field.send_keys(job_title)
        job_search_field.send_keys(Keys.ENTER)
        time.sleep(2)

        xpath_location = "//input[contains(@aria-label, 'Ciudad, provincia/estado o código postal') or contains(@aria-label, 'Search location')]"
        location_search_field = wait.until(EC.presence_of_element_located((By.XPATH, xpath_location)))
        location_search_field.clear()
        location_search_field.send_keys(location)
        location_search_field.send_keys(Keys.ENTER) 
        time.sleep(2)
        
        easy_apply_button_xpath = "//button[contains(., 'Solicitud sencilla') or contains(., 'Easy Apply')]"
        easy_apply_button = wait.until(EC.element_to_be_clickable((By.XPATH, easy_apply_button_xpath)))
        easy_apply_button.click()
        time.sleep(2)

        jobs_list = []
        job_list_container = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.scaffold-layout__list >div >ul")))
        job_cards = job_list_container.find_elements(By.CSS_SELECTOR, ":scope > li")

        for i, card in enumerate(job_cards):
            if i >= MAX_JOBS_PER_SEARCH:
                break
            try:
                card.click()
                time.sleep(2)
                detail_job = driver.find_element(By.CLASS_NAME, "jobs-search__job-details--wrapper")

                new_link = card.find_element(By.TAG_NAME, "a").get_attribute("href").split("?")[0]
                title = detail_job.find_element(By.CLASS_NAME, "job-details-jobs-unified-top-card__job-title").text
                company = detail_job.find_element(By.CSS_SELECTOR, "div.job-details-jobs-unified-top-card__company-name a").text
                location_text = detail_job.find_element(By.CSS_SELECTOR, "div.job-details-jobs-unified-top-card__tertiary-description-container span > span:first-of-type").text

                jobs_list.append({
                    "Titulo": title,
                    "Compañia": company,
                    "Ubicacion": location_text,
                    "Enlace": new_link
                })

            except Exception as e:
                print(f"⚠️ Error en tarjeta {i+1}: {e}")
                continue
        
        return jobs_list

    except Exception as e:
        print(f"ERROR al buscar el puesto '{job_title}': {e}")
        return []

def main():
    """Función principal para ejecutar el script."""

    driver = initialize_driver()
    all_results = {}

    try:
        if not linkedin_login(driver, LINKEDIN_EMAIL, LINKEDIN_PASSWORD):
            return
        for job_title in JOB_TITLES:
            job_results = search_jobs(driver, job_title, LOCATION)
            all_results[job_title] = job_results
            time.sleep(2) 
    finally:        
        driver.quit()

    total_jobs_found = 0
    
    print("________________________RESULTADOS________________________")
    for title, jobs in all_results.items():
        print(f"\n[ PUESTO: {title} ({len(jobs)} ofertas encontradas) ]")
        if jobs:
            total_jobs_found += len(jobs)
            for i, job in enumerate(jobs):
                print(f"  {i+1}. {job['Titulo']} en {job['Compañia']}")
                print(f"     Ubicación: {job['Ubicacion']}")
                print(f"     Link: {job['Enlace']}")
        else:
            print("  No se encontraron ofertas de 'Solicitud sencilla' para este puesto.")

    print(f"\nTOTAL DE OFERTAS ENCONTRADAS CON SOLICITUD SENCILLA: {total_jobs_found}")

if __name__ == "__main__":
    main()