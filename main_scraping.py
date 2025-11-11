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

def main():
    """Función principal para ejecutar el script."""
    driver = initialize_driver()
    try:
        if not linkedin_login(driver, LINKEDIN_EMAIL, LINKEDIN_PASSWORD):
            return #si linkedin_login() devuelve False (fallo de login), main termina inmediatamente.
        driver.get("https://www.linkedin.com/jobs/search/")
    finally:        
        driver.quit()

if __name__ == "__main__":
    main()
