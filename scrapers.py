from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

class MotorWeb:
    """Clase base para configurar el navegador"""
    def __init__(self):
        options = webdriver.ChromeOptions()
        options.add_argument("--start-maximized")
        # options.add_argument("--headless") # Descomentar para no ver el navegador abrirse
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        self.wait = WebDriverWait(self.driver, 10)

    def cerrar(self):
        self.driver.quit()

class BancoCentralScraper(MotorWeb):
    """Encargado exclusivamente de obtener el valor del dólar"""
    
    def obtener_dolar(self):
        url = "https://www.bcentral.cl/inicio"
        print(f"--- Consultando Banco Central: {url} ---")
        self.driver.get(url)
        
        try:
            # Buscamos el indicador del dólar. 
            xpath_dolar = "//p[contains(text(), 'Dólar observado')]/following-sibling::p"
            elemento_dolar = self.wait.until(EC.visibility_of_element_located((By.XPATH, xpath_dolar)))
            texto_dolar = elemento_dolar.text.strip()
            
            # Hacemos la limpieza de 950,45 a 950.45 (formato float Python)
            valor_float = float(texto_dolar.replace('.', '').replace(',', '.'))
            print(f"Dólar encontrado: ${valor_float}")
            return valor_float
            
        except Exception as e:
            print(f"Error obteniendo dólar: {e}")
            # Fallback por seguridad
            return 950.0 
        finally:
            self.cerrar()

class TiendaScraper(MotorWeb):
    """Encargado de extraer productos. Usaremos MercadoLibre como ejemplo."""
    
    def obtener_productos(self, busqueda="notebook", cantidad=15):
        url = f"https://listado.mercadolibre.cl/{busqueda}"
        print(f"--- Consultando Tienda: {url} ---")
        self.driver.get(url)
        
        productos_data = []
        
        try:
            # Esperamos a que cargue la lista de resultados
            xpath_items = "//li[contains(@class, 'ui-search-layout__item')]"
            self.wait.until(EC.presence_of_element_located((By.XPATH, xpath_items)))
            
            items = self.driver.find_elements(By.XPATH, xpath_items)
            
            for item in items[:cantidad]: # Limitamos a 15
                try:
                    # Extracción con selectores relativos al item
                    titulo = item.find_element(By.TAG_NAME, "h2").text
                    link = item.find_element(By.TAG_NAME, "a").get_attribute("href")
                    
                    # Buscamos la fracción entera del precio. ML a veces separa en miles/decimales.
                    # Y buscamos el contenedor de precio actual (no el tachado)
                    precio_elem = item.find_element(By.XPATH, ".//div[contains(@class,'ui-search-price__second-line')]//span[@class='andes-money-amount__fraction']")
                    precio_texto = precio_elem.text.replace('.', '')
                    precio_clp = int(precio_texto)
                    
                    productos_data.append({
                        "Titulo": titulo,
                        "Precio_CLP": precio_clp,
                        "URL": link
                    })
                    
                except Exception as e:
                    # Si falla un producto específico, no detenemos todo, solo lo saltamos
                    continue
                    
        except Exception as e:
            print(f"Error crítico en tienda: {e}")
        finally:
            self.cerrar()
            
        return productos_data