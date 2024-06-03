from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class Ipinfo:
    def __init__(self):
        self.driver = webdriver.ChromiumEdge()

    def obtener_ip_info(self):
        self.driver.get("https://whatismyipaddress.com/")

        # Esperar hasta que la página cargue y obtener la IP
        ip_address = WebDriverWait(self.driver, 3).until(
            EC.presence_of_element_located((By.XPATH, "//p[@class='ip-address']//span[@id='ipv4']/a"))
        ).text

        # Obtener la ciudad
        city = WebDriverWait(self.driver, 3).until(
            EC.presence_of_element_located(
                (By.XPATH, "//p[@class='information']//span[text()='City:']/following-sibling::span"))
        ).text

        # Obtener la ciudad
        Region = WebDriverWait(self.driver, 3).until(
            EC.presence_of_element_located(
                (By.XPATH, "//p[@class='information']//span[text()='Region:']/following-sibling::span"))
        ).text

        # Obtener el país
        country = WebDriverWait(self.driver, 3).until(
            EC.presence_of_element_located(
                (By.XPATH, "//p[@class='information']//span[text()='Country:']/following-sibling::span"))
        ).text

        print("La direccion IP es:", ip_address)
        print("La ciudad de la IP es:", city)
        print("La Region es:",  Region)
        print("El país de la IP es:", country)
        return ip_address, city, Region, country

    def __del__(self):
        self.driver.quit()


if __name__ == "__main__":
    ip_info = Ipinfo()
    ip_address, city, Region, country = ip_info.obtener_ip_info()
