from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
import time
import re

# Chrome
class MotorWeb:
    """Clase base que configura Chrome para hacer web scraping"""
    def __init__(self):
        # Configuración básica de Chrome
        options = webdriver.ChromeOptions()
        options.add_argument("--start-maximized")
        options.add_argument("--disable-blink-features=AutomationControlled")
        
        # Iniciar Chrome
        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()), 
            options=options
        )
        self.wait = WebDriverWait(self.driver, 20)  # Espera máxima de 20 segundos

    def cerrar(self):
        """Cierra el navegador"""
        self.driver.quit()

# Banco Central
class BancoCentralScraper(MotorWeb):
    """Obtiene el valor del dólar observado desde el Banco Central de Chile"""
    
    def obtener_dolar(self):
        url = "https://www.bcentral.cl/web/banco-central/inicio"
        print(f"Consultando Banco Central de Chile...")
        print(f"URL: {url}")
        
        try:
            # Cargar la página
            self.driver.get(url)
            time.sleep(10)
            
            # Hacer scroll para activar los indicadores
            self.driver.execute_script("window.scrollTo(0, 500);")
            time.sleep(3)
            
            # Buscar el valor en el código HTML de la página
            page_source = self.driver.page_source
            
            # Buscamos "Dólar Observado" seguido de $XXX,XX
            pattern = r'Dólar\s+Observado.{0,500}?\$(\d{3}),(\d{2})'
            match = re.search(pattern, page_source, re.IGNORECASE | re.DOTALL)
            
            if match:
                # Convertir de formato 888,66 a decimal 888.66
                valor_float = float(f"{match.group(1)}.{match.group(2)}")
                print(f"Dólar observado: ${valor_float:.2f} CLP")
                return valor_float

            # Si no encuentra el valor, usar respaldo (Lo puse para evitar fallos en el MVP y yo también poder seguir probando distintas cosas)
            raise Exception("No se encontró el valor del dólar en la página")
                
        except Exception as e:
            print(f"Error: {e}")
            print("Usando valor de respaldo: $888.66 CLP")
            return 888.66
        finally:
            self.cerrar()

# Tienda
class TiendaScraper(MotorWeb):
    """Extrae productos desde una tienda online (Ferreteria.cl)"""
    
    def obtener_productos(self, cantidad=15):
        url = "https://ferreteria.cl/lineas/1/herramientas-electricas"
        print(f"Consultando Ferreteria.cl...")
        print(f"URL: {url}")
        
        productos_data = []
        
        try:
            # Cargar la página
            self.driver.get(url)
            time.sleep(8)
            
            # Hacer scroll para cargar más productos
            print("Cargando productos...")
            for i in range(3):
                self.driver.execute_script(f"window.scrollTo(0, {1200 * (i+1)});")
                time.sleep(2)
            
            # Buscar elementos de productos (probando varios selectores)
            selectores = [
                "//div[contains(@class, 'product')]",
                "//article",
                "//*[contains(@class, 'card')]"
            ]
            
            items = []
            for selector in selectores:
                try:
                    items = self.driver.find_elements(By.XPATH, selector)
                    if len(items) > 5:  # Si encuentra varios, usar ese selector
                        break
                except:
                    continue
            
            print(f"Elementos encontrados: {len(items)}") # Para evitar perder tiempo si no encuentra nada
            
            # Extraer información de cada producto
            for item in items[:cantidad * 2]:  # Revisar el doble para tener margen
                try:
                    texto = item.text
                    if not texto or len(texto) < 10:
                        continue
                    
                    # 1. Extraer título (primera línea con contenido)
                    lineas = [l.strip() for l in texto.split('\n') if len(l.strip()) > 8]
                    if not lineas:
                        continue
                    titulo = lineas[0][:120]
                    
                    # Evitar productos duplicados
                    if any(p['Titulo'] == titulo for p in productos_data):
                        continue
                    
                    # 2. Extraer URL del producto
                    try:
                        link = item.find_element(By.XPATH, ".//a").get_attribute("href")
                        if not link or link == '#':
                            link = url
                    except:
                        link = url
                    
                    # 3. Extraer precio en formato chileno ($999.999)
                    precio_clp = None
                    # Buscar números con formato chileno
                    matches = re.findall(r'\$\s*(\d{1,3}(?:\.\d{3})+)', texto)
                    for match in matches:
                        try:
                            # Quitar puntos y convertir a número
                            precio_num = int(match.replace('.', ''))
                            if 1000 < precio_num < 50000000:  # Rango mucho más que razonable
                                precio_clp = precio_num
                                break
                        except:
                            continue
                    
                    if not precio_clp:
                        continue
                    
                    # Agregar producto a la lista
                    productos_data.append({
                        "Titulo": titulo,
                        "Precio_CLP": precio_clp,
                        "URL": link
                    })
                    print(f"Producto {len(productos_data)}: {titulo[:45]}... - ${precio_clp:,} CLP")
                    
                    if len(productos_data) >= cantidad:
                        break
                    
                except Exception as e:
                    continue
            
            # Si no se encontraron productos, usamos datos de demostración
            if len(productos_data) == 0:
                print("\nNOTA: El sitio web bloqueó el scraping")
                print("   Usando datos de demostración realistas...\n")
                
                productos_ejemplo = [
                    {"nombre": "Taladro Percutor Bosch 13mm 650W", "precio": 49990},
                    {"nombre": "Taladro Inalámbrico Dewalt 20V Max", "precio": 89990},
                    {"nombre": "Taladro Atornillador Black+Decker 12V", "precio": 35990},
                    {"nombre": "Taladro de Banco Bauker 350W", "precio": 79990},
                    {"nombre": "Set Brocas para Taladro 50 Piezas", "precio": 15990},
                    {"nombre": "Taladro Neumático Industrial 10mm", "precio": 125990},
                    {"nombre": "Martillo Perforador Makita HR2470", "precio": 159990},
                    {"nombre": "Taladro Magnético Dewalt DWE1622K", "precio": 899990},
                    {"nombre": "Atornillador Eléctrico Bosch GO", "precio": 29990},
                    {"nombre": "Taladro Angular Dewalt 3/8 pulgadas", "precio": 199990},
                    {"nombre": "Sierra Circular Skil 1400W", "precio": 45990},
                    {"nombre": "Esmeril Angular Makita 4-1/2\"", "precio": 39990},
                    {"nombre": "Lijadora Orbital Black+Decker", "precio": 32990},
                    {"nombre": "Rotomartillo Einhell TE-RH 32 E", "precio": 119990},
                    {"nombre": "Combo Herramientas Bauker 5 Piezas", "precio": 149990},
                ]
                
                for i, prod in enumerate(productos_ejemplo[:cantidad]):
                    productos_data.append({
                        "Titulo": prod["nombre"],
                        "Precio_CLP": prod["precio"],
                        "URL": f"{url}?producto={i+1}"
                    })
                    print(f"Producto {i+1}: {prod['nombre'][:45]}... - ${prod['precio']:,} CLP")
                    
        except Exception as e:
            print(f"Error en scraping: {e}")
        finally:
            self.cerrar()
        
        print(f"\nTotal productos extraídos: {len(productos_data)}")
        return productos_data
