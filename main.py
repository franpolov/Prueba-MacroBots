import pandas as pd
from scrapers import BancoCentralScraper, TiendaScraper

def main():
    print("INICIANDO PROCESO DE AUTOMATIZACIÓN MVP")
    
    # PASO 1: Obtener el valor del dólar desde el Banco Central
    scraper_banco = BancoCentralScraper()
    valor_dolar = scraper_banco.obtener_dolar()
    print(f"\nTipo de cambio: 1 USD = ${valor_dolar} CLP\n")
    
    # PASO 2: Extraer 15 productos de la tienda online
    scraper_tienda = TiendaScraper()
    lista_productos = scraper_tienda.obtener_productos(cantidad=15)
    
    if not lista_productos:
        print("\nNo se encontraron productos. Proceso cancelado.")
        return
    
    print(f"\nProductos extraídos: {len(lista_productos)}\n")

    # PASO 3: Convertir los precios de CLP a USD
    print("Convirtiendo precios a USD...")
    df = pd.DataFrame(lista_productos)
    df['Precio_USD'] = (df['Precio_CLP'] / valor_dolar).round(2)
    
    # Ordenar columnas: Título, Precio CLP, Precio USD, URL
    df = df[['Titulo', 'Precio_CLP', 'Precio_USD', 'URL']]
    
    # PASO 4: Guardar en archivo Excel
    nombre_archivo = "Reporte_Productos_USD.xlsx"
    
    with pd.ExcelWriter(nombre_archivo, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Productos')
        
        # Ajustar el ancho de las columnas para que se vea bien
        worksheet = writer.sheets['Productos']
        worksheet.column_dimensions['A'].width = 60  # Título
        worksheet.column_dimensions['B'].width = 15  # Precio_CLP
        worksheet.column_dimensions['C'].width = 15  # Precio_USD
        worksheet.column_dimensions['D'].width = 80  # URL
    
    # Mostrar resumen final
    print(f"Archivo Excel generado")
    print(f"Nombre: {nombre_archivo}")
    print(f"Productos extraídos: {len(df)}")
    print(f"Tipo de cambio: 1 USD = ${valor_dolar:.2f} CLP")

if __name__ == "__main__":
    main()
