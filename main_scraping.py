import os
from dotenv import load_dotenv
from webdriver_manager.firefox import GeckoDriverManager
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

#CONSTANTES
#cargo las credenciales
load_dotenv("secrets.env")
LINKEDIN_EMAIL = os.getenv("LINKEDIN_EMAIL")  
LINKEDIN_PASSWORD = os.getenv("LINKEDIN_PASSWORD")
#puestos a los que voy a aplicar y su region
JOB_TITLES = [
    "Data Engineer",
    "Machine learning engineer",
    "AI Developer"
]
LOCATION = "Argentina"
#de cada busqueda voy a seleccionar 3 puestos
MAX_JOBS_PER_SEARCH = 3 

def initialize_driver():
    """inicializa y configura el webdriver de firefox."""
    #objeto de opciones para configurar el navegador de Firefox, sin GPU evitamos bugs de renderizado, aislando el proceso nos evitamos problemas con los permisos y maximizando la ventana
    options = webdriver.FirefoxOptions()
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("start-maximized")

    #inicializa el servicio del controlador de firefox
    service = Service(GeckoDriverManager().install())
    
    #en la instancia del webdriver cargo el servicio y las opciones
    driver = webdriver.Firefox(service=service, options=options)
    return driver

def linkedin_login(driver, email, password):
    """ingreso de credenciales a Linkedin"""
    try:
        driver.get("https://www.linkedin.com/login")

        #damos un tiempo de espera hasta que aparezca el elemento buscado en el DOM,una vez encontrado,se envia el mail al campo
        wait = WebDriverWait(driver, 10)
        email_field = wait.until(EC.presence_of_element_located((By.ID, "username")))
        email_field.send_keys(email)

        #una vez hallado "username" asumo que "password" ya se encuentra en el DOM
        password_field = driver.find_element(By.ID, "password")
        password_field.send_keys(password)

        #finalmente buscamos el boton submit para enviar las credenciales
        driver.find_element(By.XPATH, "//button[@type='submit']").click()

        #si en el URL ya aparece el "feed" significa que tomo correctamente las credenciales
        wait.until(EC.url_contains("/feed"))

        return True #True para indicar que tuvo exito el inicio
    
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
            return # en caso de fallar el login, termina la funcion
        for job_title in JOB_TITLES:
            job_results = search_jobs(driver, job_title, LOCATION)
            all_results[job_title] = job_results
            time.sleep(2) 
    finally:        
        driver.quit()

    total_jobs_found = 0

if __name__ == "__main__":
    main()
