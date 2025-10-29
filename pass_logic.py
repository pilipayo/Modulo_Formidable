import random
import os
import platform
from datetime import datetime
from colorama import Fore, Style, init
init()

# ==== Excepciones personalizadas ====
class UsuarioNoExisteError(Exception):
    """Se dispara cuando el usuario administrador no existe en el sistema."""
    pass

class CredencialesInvalidasError(Exception):
    """Se dispara cuando la contraseña es incorrecta o no se puede validar/desencriptar."""
    pass

class ArchivoNoAccesibleError(Exception):
    """Se dispara cuando no se puede leer/escribir un archivo requerido."""
    pass

class CuentaNoEncontradaError(Exception):
    """Se dispara cuando la cuenta solicitada no existe o el índice es inválido."""
    pass

class EntradaInvalidaError(Exception):
    """Se dispara cuando el usuario ingresa un dato con formato inválido."""
    pass
class ContraseñaInvalidaError(Exception):
    """Se dispara cuando la contraseña no cumple los requisitos mínimos."""
    pass


def log_event(evento, nivel="INFO", mensaje="", usuario="", funcion="", extra="", filename=None):
    """
    Registramos eventos en nuestro .csv
    Columnas: fecha_iso;nivel;evento;usuario;funcion;mensaje;extra
    """
    if filename is None:
        filename = "eventos_log.csv"  

    # Compacta saltos de línea
    if "\n" in mensaje:
        mensaje = "".join(mensaje.splitlines())
    if "\n" in extra:
        extra = "".join(extra.splitlines())

    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    linea = f"{fecha};{nivel};{evento};{usuario};{funcion};{mensaje};{extra}\n"

    try:
        # existe el archivo? si no, escribimos encabezado primero
        escribir_header = False
        try:
            with open(filename, "r", encoding="utf-8") as arch:
                pass
        except OSError:
            escribir_header = True

        with open(filename, "a", encoding="utf-8") as f:
            if escribir_header:
                f.write("fecha;gravedad;evento;usuario;funcion;mensaje;extra\n")
            f.write(linea)
    except OSError:
        # nunca cortamos la app por un fallo de log
        pass


#DATOS PRE-SETEADOS

letras_mayusculas = ('A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z','Á','É','Í','Ó','Ú','Ü','Ñ')
letras_minusculas = ('a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z','á','é','í','ó','ú','ü','ñ')
numeros = ('0','1','2','3','4','5','6','7','8','9')
caracteres_especiales = ('?','!','¡','¿','.',',',':','-','_','(',')','[',']','{','}','@','#','$','%','&','/','"',"'",'+','*','=','<','>','|','^','°','~','`')

COLORES = {
    "ok": Fore.GREEN,       
    "error": Fore.RED,      
    "alerta": Fore.YELLOW,  
    "info": Fore.CYAN,     
    "rosa":Fore.MAGENTA, 
    "reset": Style.RESET_ALL,
    "bright": Style.BRIGHT
}

limpiar_pantalla = lambda: os.system("cls") if platform.system()=="Windows" else os.system("clear")


def login():
    """Solicitamos al usuario ingresar usuario y contraseña del administrador"""

    print(COLORES["bright"] + "\n══════════════ LOGIN ══════════════" + COLORES["reset"])

    while True:
        user=input(COLORES["bright"] + "👤 Usuario: "+ COLORES["reset"]).strip()
        if user:
            break
        print(COLORES["alerta"]+"⚠ Debe ingresar un nombre de usuario."+ COLORES["reset"])
    archivo_usuario = f"{user}.csv"
        
    try:
        with open(archivo_usuario, mode="rt", encoding="utf-8") as archivo:
            contraseña_archivada= archivo.readline().strip()

            if ";" in contraseña_archivada:
                try:
                    enc, lista = contraseña_archivada.split(";", 1)
                    contraseña_guardada = desencriptar(enc, enlistar(lista))
                except Exception:
                    raise CredencialesInvalidasError(COLORES["error"]+"✖ Error al desencriptar la contraseña guardada."+ COLORES["reset"])
                   
            else:
                contraseña_guardada= contraseña_archivada

            intentos=3

            while intentos>0:
                contraseña_ingresada = input(COLORES["bright"]+"🔐 Contraseña: "+COLORES["reset"])
            
                if contraseña_ingresada == contraseña_guardada:
                    print(COLORES["bright"]+f"\nBienvenido, {user}!"+COLORES["reset"])
                    return user, contraseña_guardada
                else:
                    intentos-=1
                    if intentos>0:
                        print(COLORES["error"]+ "✖ Contraseña incorrecta."+ COLORES["reset"])
                    else:
                        log_event("login_attempts_exceeded", "WARN", "Excediste los 3 intentos.", usuario=user, funcion="login")
                        raise CredencialesInvalidasError(COLORES["error"]+ "Excediste los 3 intentos."+ COLORES["reset"])
                     

        
    except OSError:

        print(COLORES["alerta"] + f"⚠ El usuario '{user}' no existe." + COLORES["reset"])
        respuesta = input("Queres crear un nuevo usuario? (s/n): ").lower()
        
        while respuesta !="s" and respuesta !="n":
            respuesta = input(COLORES["alerta"]+"✖ Respuesta INVALIDA, debe ingresar s o n: "+COLORES["reset"]).lower()
        
        if respuesta == "n":
            raise UsuarioNoExisteError(COLORES["alerta"] + "⚠ No se creó el usuario. Saliendo del login."+ COLORES["reset"])
          

        print("Creando nueva cuenta...")
        while True:
            nuevaContraseña = input(COLORES["bright"]+ "🔑 Crea tu contraseña: "+ COLORES["reset"])
            
            try:
                if validar(nuevaContraseña):        # <---- Puede levantar ContraseñaInvalidaError
                
                    repetir=input("Repeti la contraseña ingresada: ")
            
                    if nuevaContraseña != repetir:
                        print(COLORES["alerta"] + "⚠ No coinciden las contraseñas. Intenta de nuevo"+ COLORES["reset"])
                        continue
                    break
            except ContraseñaInvalidaError as e:
                print(COLORES["alerta"] + str(e) + COLORES["reset"])
                continue        

        try:
            enc, lista = encriptar(nuevaContraseña)

            with open(archivo_usuario, mode = "wt", encoding="utf-8") as archivo:
                archivo.write(f"{enc};{lista}\n")
            print(COLORES["ok"]+"✅ Cuenta creada exitosamente!"+ COLORES["reset"])
            print(COLORES["bright"]+f"\nBienvenido, {user}!"+COLORES["reset"])
            return user, nuevaContraseña
        
        except OSError:
            raise ArchivoNoAccesibleError(COLORES["error"]+"❌ No se pudo crear el archivo"+COLORES["reset"])
           
            
    

    
def crear_contraseña(largo_contraseña = 20):
    """Generamos una contraseña aleatoria de 20 caracteres que cumpla con: al menos una letra mayúscula, al menos una letra minúscula, 
    al menos un número, y al menos un carácter especial"""

    contraseña=[]
    for i in range(largo_contraseña):
        buscar_lista = random.randint(0,3)
        if buscar_lista == 0:
            caracter = letras_mayusculas[random.randint(0,len(letras_mayusculas)-1)]
        elif buscar_lista == 1:
            caracter = letras_minusculas[random.randint(0,len(letras_minusculas)-1)]
        elif buscar_lista == 2:
            caracter = numeros[random.randint(0,len(numeros)-1)]
        else:
            caracter = caracteres_especiales[random.randint(0,len(caracteres_especiales)-1)]
        contraseña.append(caracter)
    contraseña = "".join(contraseña)
    return contraseña


def validar(contraseña, largo_min=12):
    """
    Valida que la contraseña cumpla con todos los requisitos mínimos.
    Si falta alguno, levanta ContraseñaInvalidaError con detalles.
    Si pasa, calcula y muestra el nivel de robustez: Débil / Intermedia / Fuerte.
    """
    # ---- 1. Validaciones básicas ----
    requisitos_faltantes = []

    if len(contraseña) < largo_min:
        requisitos_faltantes.append(f"- Tener al menos {largo_min} caracteres.")

    if not any(c in numeros for c in contraseña):
        requisitos_faltantes.append("- Contener al menos un número (0-9).")

    if not any(c in caracteres_especiales for c in contraseña):
        requisitos_faltantes.append("- Incluir al menos un caracter especial (%, &, !, etc.).")

    if not any(c in letras_mayusculas for c in contraseña):
        requisitos_faltantes.append("- Tener al menos una letra mayúscula (A-Z).")

    if not any(c in letras_minusculas for c in contraseña):
        requisitos_faltantes.append("- Tener al menos una letra minúscula (a-z).")

    palabras_prohibidas = ("password", "admin", "contraseña", "clave", "claves")
    if any(p.lower() in contraseña.lower() for p in palabras_prohibidas):
        requisitos_faltantes.append("- No contener palabras prohibidas como 'password', 'admin', 'clave', etc.")

    if requisitos_faltantes:
        mensaje = "❌ La contraseña no cumple con los siguientes requisitos:\n" + "\n".join(requisitos_faltantes)
        raise ContraseñaInvalidaError(mensaje)

    # ---- 2. Si pasa todo, calculamos robustez ----
    largo = len(contraseña)
    cantidad_mayusculas = sum(1 for c in contraseña if c in letras_mayusculas)
    cantidad_minusculas = sum(1 for c in contraseña if c in letras_minusculas)
    cantidad_numeros = sum(1 for c in contraseña if c in numeros)
    cantidad_especiales = sum(1 for c in contraseña if c in caracteres_especiales)

    # Puntaje base según largo
    puntaje = largo // 2
    if largo <= 15:
        puntaje += 0
    elif largo <= 20:
        puntaje += 10
    else:
        puntaje += 15

    # Bonificaciones
    if cantidad_mayusculas > 3:
        puntaje += 2
    if cantidad_minusculas > 3:
        puntaje += 2
    if cantidad_numeros > 3:
        puntaje += 2
    if cantidad_especiales > 3:
        puntaje += 2

    # Penalizaciones
    secuencias_no_recomendadas = ("123", "456", "789", "abc", "ABC")
    for palabra in secuencias_no_recomendadas:
        if palabra in contraseña:
            puntaje -= 7

    # Determinamos el nivel
    if puntaje <= 12:
        nivel = COLORES["alerta"] + "⚠ DÉBIL" + COLORES["reset"]
    elif puntaje <= 25:
        nivel = COLORES["info"] + "INTERMEDIA" + COLORES["reset"]
    else:
        nivel = COLORES["ok"] + "FUERTE" + COLORES["reset"]

    print(f"Tu contraseña tiene un nivel de seguridad: {nivel}")
    return True


def ingresar_contraseña():
    """Le pedimos al usuario que ingrese su contraseña o que cree una contraseña aleatoria más segura"""
    while True:
        while True:
            try:
                eleccion = int(input("Ingrese '1' si quiere ingresar usted mismo la contraseña o '2' si quiere que se cree otra al azar: "))
                if  eleccion != 1 and eleccion != 2:
                    print("❌ Debe ingresar una de las opciones mencionadas.")
                else:
                    break
            except ValueError:
                print("Debe ingresar un numero.")
                
            
        if eleccion == 1:
            print("Va ingresar su propia contraseña. Tenga en cuenta que la misma debe tener como mínimo:")
            print(" 12 caracteres✅\n Una letra mayúscula✅\n Una letra minúscula✅\n Un número✅\n Un caracter especial.✅\n")
            contraseña = input("Ingrese la contraseña que quiere para esta app: ")
            
            #if validar(contraseña) == True:
            
            if validar(contraseña):       # <--- Levanta ContraseñaInvalidaError
                contraseña_encriptada, lista_encriptacion = encriptar(contraseña)
                return contraseña_encriptada, lista_encriptacion
            break

        else:   # eleccion == 2
            while True:
                contraseña = crear_contraseña()
                try:
                    if validar(contraseña):
                        break
                except ContraseñaInvalidaError:
                    continue

            contraseña_encriptada, lista_encriptacion = encriptar(contraseña)
            return contraseña_encriptada, lista_encriptacion


    
def encriptar(clave_original):
    largo_clave_original= len(clave_original)
    clave_encriptada = crear_contraseña(largo_clave_original)
    
    lista_encriptacion = []
    
    for i in range(0,largo_clave_original):
        caracter = clave_original[i]
        for j in range(0,4):
            if caracter in letras_mayusculas:
                tupla_original = 0
                posicion_original = letras_mayusculas.index(caracter)
            elif caracter in letras_minusculas:
                tupla_original = 1
                posicion_original = letras_minusculas.index(caracter)
            elif caracter in numeros:
                tupla_original = 2
                posicion_original = numeros.index(caracter)
            else: 
                tupla_original = 3
                posicion_original = caracteres_especiales.index(caracter)
                
                
        caracter = clave_encriptada[i]
        for j in range(0,4):
            if caracter in letras_mayusculas:
                tupla_encriptada = 0
                posicion_encriptada = letras_mayusculas.index(caracter)
            elif caracter in letras_minusculas:
                tupla_encriptada = 1
                posicion_encriptada = letras_minusculas.index(caracter)
            elif caracter in numeros:
                tupla_encriptada = 2
                posicion_encriptada = numeros.index(caracter)
            else: 
                tupla_encriptada = 3
                posicion_encriptada = caracteres_especiales.index(caracter)
                
        lista_encriptacion.append(tupla_encriptada-tupla_original)
        lista_encriptacion.append("|")
        lista_encriptacion.append(posicion_encriptada - posicion_original)
        lista_encriptacion.append("|")
        cadena_encriptada = "".join(map(str, lista_encriptacion))

    
    return clave_encriptada,cadena_encriptada
    
  
def desencriptar(clave_encriptada, lista_encriptacion):
    largo_clave_encriptada= len(clave_encriptada)
    clave_original = []
    
    for i in range(0,largo_clave_encriptada):
        caracter = clave_encriptada[i]
        for j in range(0,4):
            if caracter in letras_mayusculas:
                tupla_encriptada = 0
                posicion_encriptada = letras_mayusculas.index(caracter)
            elif caracter in letras_minusculas:
                tupla_encriptada = 1
                posicion_encriptada = letras_minusculas.index(caracter)
            elif caracter in numeros:
                tupla_encriptada = 2
                posicion_encriptada = numeros.index(caracter)
            else: 
                tupla_encriptada = 3
                posicion_encriptada = caracteres_especiales.index(caracter)
                
        
        tupla_original =  tupla_encriptada - lista_encriptacion[i*2]
        posicion_original = posicion_encriptada - lista_encriptacion[i*2+1]
            
        if tupla_original == 0:
            caracter = letras_mayusculas[posicion_original]
        elif  tupla_original == 1:
            caracter = letras_minusculas[posicion_original]
        elif  tupla_original == 2:
            caracter = numeros[posicion_original]
        else: 
            caracter = caracteres_especiales[posicion_original]
                
        
        clave_original.append(caracter)
    clave_original = "".join(clave_original)
    return clave_original

enlistar = lambda cadena: [int(x) for x in cadena.split("|") if x!=""]

def main():
    while True:
        try:
            user, contraseña = login()

            contraseña, lista = ingresar_contraseña()
            if contraseña:
                print(contraseña)

            contraseña1= crear_contraseña()

            print(encriptar(contraseña1))

            candena_desen = desencriptar(contraseña,enlistar(lista))

            print(candena_desen)

            break

        except ContraseñaInvalidaError as e:
            log_event("weak_password", "WARN", str(e), usuario=user, funcion="menu")
            print(COLORES["alerta"], str(e), COLORES["reset"])
        except CuentaNoEncontradaError as e:
            log_event("account_not_found", "WARN", str(e), usuario=user, funcion="menu")
            print(COLORES["error"], str(e), COLORES["reset"])
        except EntradaInvalidaError as e:
            log_event("invalid_input", "WARN", str(e), usuario=user, funcion="menu")
            print(COLORES["alerta"], str(e), COLORES["reset"])
        except CredencialesInvalidasError as e:
            log_event("admin_password_incorrect", "WARN", str(e), usuario=user, funcion="mostrar")
            print(COLORES["error"], str(e), COLORES["reset"])
        except UsuarioNoExisteError as e:
            log_event("login_user_not_found", "WARN", str(e), usuario=user, funcion="mostrar")
            print(COLORES["error"], str(e), COLORES["reset"])
        except ArchivoNoAccesibleError as e:
            log_event("io_error", "ERROR", str(e), usuario=user, funcion="*")
            print(COLORES["error"], str(e), COLORES["reset"])
        except Exception as e:
            log_event("unespected_error", "ERROR", str(e), usuario=user, funcion="*")
            print(COLORES["error"], f"Error inesperado: {e}", COLORES["reset"])



if __name__ == "__main__": 
    main()