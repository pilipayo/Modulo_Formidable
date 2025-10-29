# Gestor de credenciales con login, validación y log de eventos

Aplicación de consola en Python para **autenticación de usuario administrador**, **gestión/validación de contraseñas** y **registro de eventos** en CSV. Usa `colorama` para salida con colores y maneja **excepciones personalizadas** para estados de error predecibles.

---

## 📦 Contenidos principales

- **Login interactivo** con creación de usuario si no existe.
- **Validación de contraseña** con requisitos mínimos y feedback de robustez (débil/intermedia/fuerte).
- **Generación de contraseñas seguras** aleatorias.
- **“Encriptado”/“Desencriptado” simulado** de contraseñas mediante una clave de mapeo por tupla+posición.
- **Registro de eventos** (`eventos_log.csv`) con formato `fecha;nivel;evento;usuario;funcion;mensaje;extra`.
- **Excepciones personalizadas** para flujos de error controlados.



---

## 🏁 Requisitos

- Python 3.x
- Módulos estándar: `os`, `platform`, `datetime`, `random`
- Módulo externo: `colorama` (salida coloreada)

Archivos generados al ejecutar:
- `eventos_log.csv` (log de auditoría)
- `<usuario>.csv` (archivo del administrador con la contraseña codificada)

---

## 📂 Estructura y responsabilidaes

- **Excepciones personalizadas**
  - `UsuarioNoExisteError`, `CredencialesInvalidasError`, `ArchivoNoAccesibleError`, `CuentaNoEncontradaError`, `EntradaInvalidaError`, `ContraseñaInvalidaError`.
  - Permiten distinguir y manejar los errores por tipo (mejor trazabilidad y UX).

- **`log_event(evento, nivel="INFO", mensaje="", usuario="", funcion="", extra="", filename=None)`**
  - Registra eventos en CSV con encabezado si no existe.
  - Compacta saltos de línea para mantener el CSV en una sola línea por evento.
  - Nunca interrumpe la app en caso de error de escritura del log.

- **Constantes de caracteres**
  - `letras_mayusculas`, `letras_minusculas`, `numeros`, `caracteres_especiales`: insumos para validar/crear contraseñas y para el mapeo de “encriptado”.

- **Utilidad de limpieza de pantalla**
  - `limpiar_pantalla`: `cls` en Windows, `clear` en Unix.

- **`login()`**
  - Pide usuario y busca `<usuario>.csv`.
  - Si existe, **lee la contraseña** (plano o codificada) y permite **3 intentos**.
  - Si no existe, **ofrece crear** el usuario: valida la contraseña y guarda `enc;lista_mapeo`.
  - Registra eventos de intentos excedidos.

- **`crear_contraseña(largo=20)`**
  - Genera una contraseña aleatoria cumpliendo los tipos de caracteres requeridos.

- **`validar(contraseña, largo_min=12)`**
  - Verifica requisitos mínimos (largo, tipos de caracteres, palabras prohibidas).
  - Calcula un **puntaje** simple y muestra **nivel**: Débil / Intermedia / Fuerte.
  - Lanza `ContraseñaInvalidaError` con el detalle si no cumple.

- **`ingresar_contraseña()`**
  - Permite elegir entre **ingresar una propia** o **generar una segura**.
  - Devuelve `(contraseña_encriptada, lista_encriptacion)`.

- **`encriptar(clave_original)` / `desencriptar(clave_encriptada, lista_encriptacion)`**
  - Codificación **reversible** por **diferencia de tupla y posición** respecto de una “clave encriptada” aleatoria de igual longitud.  
  - Devuelve/recibe la lista de mapeo como cadena con separador `"|"` (se transforma con `enlistar`).
  - **Nota**: es un mecanismo didáctico (no criptográfico).

- **`enlistar = lambda cadena: [int(x) for x in cadena.split("|") if x!=""]`**
  - Convierte el string de mapeo `"d1|d2|..."` a lista de enteros.

---

## ▶️ Ejecución

1. Colocar el archivo `.py` en un directorio de trabajo.
2. Ejecutar con Python 3 (interactivo por consola).
3. En el primer uso, si el usuario **no existe**, el programa ofrece **crearlo** y guarda `<usuario>.csv` con la contraseña codificada.
4. Se registran eventos en `eventos_log.csv`.

---

## 🧪 Pruebas manuales sugeridas

- **Usuario inexistente → creación**  
  - Ingresar un nombre nuevo; probar contraseñas que **falten requisitos** para ver el mensaje detallado; luego ingresar una válida y confirmar.
- **Login correcto**  
  - Reabrir, ingresar usuario creado y contraseña correcta.  
- **Intentos fallidos**  
  - Ingresar 3 veces mal y verificar el evento `login_attempts_exceeded` en el log.
- **Robustez**  
  - Probar contraseñas con secuencias (p.ej. `abc`, `123`) y distintas longitudes para observar el nivel.

---
