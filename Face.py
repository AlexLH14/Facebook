import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException
import time

class Facebook:
    def __init__(self):
        # Configurar el proxy en el navegador Chromium
        chromium_options = webdriver.ChromeOptions()
        chromium_options.binary_location = "C:\\Users\\alex2\\AppData\\Local\\Chromium\\Application\\chrome.exe"  # Ruta al ejecutable de Chromium

        # Ruta al archivo ZIP de la extensión
        extension_zip_path = r"C:\Users\alex2\Desktop\Python\DirecionIP\proxy_extension.zip"
        chromium_options.add_extension(extension_zip_path)

        self.driver = webdriver.Chrome(options=chromium_options)

    def abrir_facebook_y_aceptar_cookies(self):
        self.driver.get("https://www.facebook.com/login/?next=https%3A%2F%2Fwww.facebook.com%2F%3Flocale%3Des_ES")

        # Esperar hasta que el botón de aceptar cookies esté presente y hacer clic en él
        try:
            boton_aceptar_cookies = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH,
                                            "//div[@data-testid='cookie-policy-manage-dialog']//div[@role='button' and (contains(@aria-label, 'Allow all') or contains(@aria-label, 'Permitir todas')) and not(@aria-disabled)]"))
            )
            boton_aceptar_cookies.click()
            print("Cookies aceptadas.")
        except Exception as e:
            print("No se encontró el botón de cookies:", e)

    def iniciar_sesion(self, username, password):
        self.abrir_facebook_y_aceptar_cookies()

        # Encontrar los campos de usuario y contraseña e ingresar las credenciales
        try:
            campo_usuario = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "email"))
            )
            campo_usuario.send_keys(username)

            campo_contrasena = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "pass"))
            )
            campo_contrasena.send_keys(password)


            boton_iniciar_sesion = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.NAME, "login"))
            )
            boton_iniciar_sesion.click()
            print("Inicio de sesión enviado.")
            r = input()
        except Exception as e:
            print("Error al intentar iniciar sesión:", e)

    def navegar_y_detectar_publicidad(self):
        # Esta función navega por Facebook y detecta publicidad
        self.driver.get("https://www.facebook.com")

        # Espera a que la página se cargue
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[@role='feed']"))
        )

        # Encuentra todas las secciones de artículos en la página
        sections = self.driver.find_elements(By.XPATH, "//div[@role='article']")
        for section in sections:
            # Llama a is_sponsored_section para verificar si la sección contiene publicidad
            if self.is_sponsored_section(section):
                print("Sección de publicidad detectada.")  # Mensaje para indicar que se encontró publicidad

    def is_sponsored_section(self, section):
        # Verifica si una sección específica contiene publicidad patrocinada
        wait_driver = WebDriverWait(self.driver, 10)
        try:
            self.driver.execute_script("arguments[0].scrollIntoView();", section)  # Desplaza la vista hasta la sección
            time.sleep(2)  # Espera para asegurar que el elemento se cargue correctamente
            element = wait_driver.until(
                EC.element_to_be_clickable((By.XPATH, './/div[@aria-haspopup="menu"][@role="button"][@aria-expanded="false"]'))
            )
            self.driver.execute_script("arguments[0].click();", element)  # Hace clic en el menú de opciones
            wait_driver.until(
                EC.element_to_be_clickable((By.XPATH, "//*[text()='Ocultar anuncio']"))
            )
            print('Publicidad detectada')  # Imprime mensaje al detectar publicidad
            # Obtiene el enlace del video y lo imprime
            enlace_element = wait_driver.until(
                EC.element_to_be_clickable((By.XPATH, "//*[text()='Copiar enlace']"))
            )
            enlace_element.click()
            enlace_copiado = self.driver.execute_script("return window.navigator.clipboard.readText();")
            print("Enlace del video:", enlace_copiado)
            element = self.driver.switch_to.active_element
            element.send_keys(Keys.ESCAPE)  # Cierra el menú
            return True
        except NoSuchElementException:
            return False
        except Exception as e:
            return False




    def __del__(self):
        self.driver.quit()


if __name__ == "__main__":
    facebook = Facebook()
    facebook.iniciar_sesion("pastor.juanjc.pastor2001@gmail.com", "Palmas2001")
    #facebook.iniciar_sesion("alexshopaliexp@gmail.com", "alexpr2024")
    facebook.navegar_y_detectar_publicidad()

