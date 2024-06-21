from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, ElementClickInterceptedException
from selenium.webdriver.common.action_chains import ActionChains
import time
import json
import pyperclip
from selenium.webdriver.common.keys import Keys


class Facebook:
    def __init__(self):
        chromium_options = webdriver.ChromeOptions()
        chromium_options.binary_location = "C:\\Users\\alex2\\AppData\\Local\\Chromium\\Application\\chrome.exe"
        extension_zip_path = r"C:\Users\alex2\Desktop\Python\DirecionIP\proxy_extension.zip"
        chromium_options.add_extension(extension_zip_path)
        self.driver = webdriver.Chrome(options=chromium_options)

    def __del__(self):
        self.driver.quit()

    def abrir_facebook_y_aceptar_cookies(self):
        self.driver.get("https://www.facebook.com/login/?next=https%3A%2F%2Fwww.facebook.com%2F%3Flocale%3Des_ES")
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
        except Exception as e:
            print("Error al intentar iniciar sesión:", e)

    def navegar_y_detectar_publicidad(self):
        self.driver.get("https://www.facebook.com")
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[@role='feed']"))
        )

        post_count = 0
        while True:
            sections = self.driver.find_elements(By.XPATH, "//div[@role='article']")
            for section in sections:
                post_count += 1
                print(f"Analizando publicación número {post_count}")
                try:
                    more_button = section.find_element(By.XPATH, ".//div[@aria-haspopup='menu'][@role='button']")
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", more_button)
                    time.sleep(1)
                    try:
                        more_button.click()
                        print(f"Ya le di clic a la publicación número {post_count}")
                    except ElementClickInterceptedException as e:
                        print(f"El clic en la publicación número {post_count} fue interceptado: {e}")
                        self.driver.execute_script("window.scrollBy(0, -100);")
                        time.sleep(1)
                        more_button.click()
                        print(f"Segundo intento exitoso para la publicación número {post_count}")
                    time.sleep(3)
                    if self.is_sponsored_section(section):
                        print(f"Publicidad detectada en la publicación número {post_count}")
                        self.clasificar_y_extraer_anuncio(section)
                    else:
                        print(f"No se encontró publicidad en la publicación número {post_count}")
                except NoSuchElementException:
                    print(f"No se encontró el botón 'Más' en la publicación número {post_count}")
                    continue
                except ElementClickInterceptedException as e:
                    print(f"Error al hacer clic en 'Más' en la publicación número {post_count}: {e}")
                    continue
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(5)
            try:
                self.driver.find_element(By.XPATH, "//div[contains(text(), 'Fin de las publicaciones')]")
                print("Fin de las publicaciones. Saliendo...")
                break
            except NoSuchElementException:
                continue

    def is_sponsored_section(self, section):
        wait_driver = WebDriverWait(self.driver, 10)
        try:
            wait_driver.until(
                EC.presence_of_element_located((By.XPATH, ".//span[contains(text(), '¿Por qué veo este anuncio?')]"))
            )
            return True
        except NoSuchElementException:
            return False
        except Exception as e:
            return False

    def clasificar_y_extraer_anuncio(self, section):
        ad_class = FacebookStoryAd.elicit_story_type_from_element(section)
        if ad_class == VideoStoryAd:
            ad_instance = ad_class(section, self.driver)
        else:
            ad_instance = ad_class(section)
        ad_instance.populate()
        ad_data = ad_instance.as_json()
        print("Datos del anuncio:", ad_data)


class FacebookStoryAd:
    @classmethod
    def elicit_story_type_from_element(cls, element):
        if element.find_elements(By.XPATH, ".//ul"):
            return CarouselStoryAd
        if element.find_elements(By.XPATH, ".//video"):
            return VideoStoryAd
        return SimpleStoryAd

    def __init__(self, element):
        self.element = element
        self.title = ''
        self.title_link = ''
        self.profile_img_url = ''
        self.text_1 = ''

    def base_populate(self):
        self.title = self.get_elem_attribute_by_xpath(self.element, './/h4', 'innerText')
        self.title_link = self.get_elem_attribute_by_xpath(self.element, './/h4/div/a', 'href')
        self.profile_img_url = self.get_elem_attribute_by_xpath(
            self.element, './/*[local-name()="svg"]/*[local-name()="g"]/*[local-name()="image"]', 'href')
        self.text_1 = self.get_elem_attribute_by_xpath(self.element, './/div[contains(@data-ad-preview,"message")]', 'innerText')

    def get_elem_attribute_by_xpath(self, item, xpath, attribute):
        try:
            element = item.find_element(By.XPATH, xpath)
            return element.get_attribute(attribute)
        except NoSuchElementException:
            return ''


class SimpleStoryAd(FacebookStoryAd):
    def __init__(self, element):
        super().__init__(element)
        self.banner_url = ''
        self.subtitle = ''
        self.text_2 = ''
        self.link = ''

    def populate(self):
        self.base_populate()
        self.banner_url = self.get_elem_attribute_by_xpath(self.element, './/div//div/div/img', 'src')
        self.subtitle = self.get_elem_attribute_by_xpath(self.element, './/a//span//span', 'innerText')
        self.text_2 = self.get_elem_attribute_by_xpath(self.element, './/a//div[2]/span', 'innerText')
        self.link = self.get_elem_attribute_by_xpath(self.element, './/a/div/div/div[1]/div[1]/span', 'innerText')

    def as_json(self):
        return json.dumps({
            'type': 'image',
            'header': {
                'text': self.title,
                'href': self.title_link,
                'img': {'src': self.profile_img_url}
            },
            'body': {
                'text': self.text_1,
                'media': [{
                    'format': 'image',
                    'src': self.banner_url
                }]
            },
            'footer': {
                'title': self.subtitle,
                'text': self.text_2,
                'link': self.link
            }
        })


class CarouselStoryAd(FacebookStoryAd):
    def __init__(self, element):
        super().__init__(element)
        self.items = []

    def populate(self):
        self.base_populate()
        items = self.element.find_elements(By.XPATH, './/ul/li')
        self.items = []
        for item in items:
            title = self.get_elem_attribute_by_xpath(item, './/span/div/div', 'innerText')
            title_link = self.get_elem_attribute_by_xpath(item, './/a', 'href')
            image_url = self.get_elem_attribute_by_xpath(item, './/img', 'src')
            footer = self.get_elem_attribute_by_xpath(item, './/div[2]/span[not(*)]', 'innerText')
            self.items.append({
                'title': title,
                'title_link': title_link,
                'image_url': image_url,
                'footer': footer
            })

    def as_json(self):
        return json.dumps({
            'type': 'carousel',
            'header': {
                'text': self.title,
                'href': self.title_link,
                'img': {'src': self.profile_img_url}
            },
            'body': {
                'text': self.text_1,
                'media': [{'format': 'image', 'src': item['image_url'],
                           'header': {'text': item['title'], 'href': item['title_link']},
                           'footer': {'text': item['footer']}} for item in self.items]
            }
        })


class VideoStoryAd(FacebookStoryAd):
    def __init__(self, element, driver):
        super().__init__(element)
        self.driver = driver
        self.video_url = ''
        self.thumbnail_url = ''
        self.subtitle = ''
        self.text_2 = ''
        self.link = ''

    def populate(self):
        self.base_populate()
        self.video_url = self.get_video_url()
        self.thumbnail_url = self.get_elem_attribute_by_xpath(self.element, './/video/..//img', 'src')
        self.subtitle = self.get_elem_attribute_by_xpath(self.element, './/div[contains(@class,"mbs")]/a', 'innerText')
        self.text_2 = self.get_elem_attribute_by_xpath(self.element, './/div[contains(@class,"mbs")]/../div[2]', 'innerText')
        self.link = self.get_elem_attribute_by_xpath(self.element, './/div[contains(@class,"ellipsis")]', 'innerText')

    def get_video_url(self):
        # Localizar el menú contextual
        try:
            menu_button = self.element.find_element(By.XPATH, '//span[contains(text(), "Copiar enlace")]')
            ActionChains(self.driver).move_to_element(menu_button).perform()
            time.sleep(1)

            # Hacer clic en el menú contextual
            copy_link_button = self.element.find_element(By.XPATH, '//span[contains(text(), "Copiar enlace")]/..')
            self.driver.execute_script("arguments[0].click();", copy_link_button)
            time.sleep(1)
            print(copy_link_button)
        except NoSuchElementException as e:
            print(f"Error al encontrar el elemento para copiar enlace: {e}")
            return None

        # Pegar el enlace del portapapeles
        try:
            video_url = self.driver.execute_script("return navigator.clipboard.readText();")
        except Exception as e:
            print(f"Error al leer el portapapeles: {e}")
            video_url = None

        return video_url

    def as_json(self):
        return json.dumps({
            'type': 'video',
            'header': {
                'text': self.title,
                'href': self.title_link,
                'img': {'src': self.profile_img_url}
            },
            'body': {
                'text': self.text_1,
                'media': [{
                    'format': 'video',
                    'src': self.video_url
                }]
            },
            'footer': {
                'title': self.subtitle,
                'text': self.text_2,
                'link': self.link
            }
        })


if __name__ == "__main__":
    facebook = Facebook()
    facebook.iniciar_sesion("pastor.juanjc.pastor2001@gmail.com", "Palmas2001")
    time.sleep(15)
    r=input()
    facebook.navegar_y_detectar_publicidad()
