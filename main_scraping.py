import os
from dotenv import load_dotenv
from webdriver_manager.firefox import GeckoDriverManager
from selenium import webdriver
from selenium.webdriver.firefox.service import Service

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
