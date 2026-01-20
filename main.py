import pandas as pd
from scrapers import BancoCentralScraper, TiendaScraper
import os

def main():
    print("INICIANDO PROCESO DE AUTOMATIZACIÓN MVP")
    
    # Obtenemos el dólar
    scraper_banco = BancoCentralScraper()
    valor_dolar = scraper_banco.obtener_dolar()
    
    # Obtenemos los productos
    scraper_tienda = TiendaScraper()
    lista_productos = scraper_tienda.obtener_productos(busqueda="iphone", cantidad=15)
    
    if not lista_productos:
        print("No se encontraron productos. Abortando.")
        return

    # Empezamos el procesamiento y conversión de divisas
    print("Procesando datos y convirtiendo divisas...")
    df = pd.DataFrame(lista_productos)
    
    # Conversión
    df['Precio_USD'] = (df['Precio_CLP'] / valor_dolar).round(2)
    df['Tasa_Cambio'] = valor_dolar # Dato útil para auditoría
    
    # Reordenamos las columnas para que se vea mejor
    columnas_ordenadas = ['Titulo', 'Precio_CLP', 'Precio_USD', 'Tasa_Cambio', 'URL']
    df = df[columnas_ordenadas]
    
    # Exportamos a Excel
    nombre_archivo = "Reporte_Productos_USD.xlsx"
    df.to_excel(nombre_archivo, index=False)
    
    print(f"Archivo generado correctamente: {os.path.abspath(nombre_archivo)}")

if __name__ == "__main__":
    main()