# FREE TV

[![Validación y empaquetado](https://github.com/Said1235/free-tv/actions/workflows/validate.yml/badge.svg)](https://github.com/Said1235/free-tv/actions/workflows/validate.yml)
[![Licencia MIT](https://img.shields.io/badge/licencia-MIT-blue.svg)](LICENSE)

**FREE TV** es un complemento de vídeo para [Kodi](https://kodi.tv/) que permite cargar una lista IPTV en formato M3U, explorar sus canales por categorías, buscar canales por nombre y reproducir las direcciones compatibles desde Kodi.

El usuario configura la fuente de la lista. FREE TV no aloja, retransmite, incluye ni redistribuye los canales o sus emisiones.

> **Importante:** que una lista sea pública o accesible no significa que todos sus canales tengan autorización para distribuirse o reproducirse en cualquier territorio. Utiliza únicamente fuentes y emisiones para las que tengas los derechos o permisos correspondientes y respeta la legislación aplicable.

---

## Contenido

- [Características](#características)
- [Compatibilidad](#compatibilidad)
- [Instalación](#instalación)
- [Configuración](#configuración)
- [Uso](#uso)
- [Formato de listas M3U](#formato-de-listas-m3u)
- [Cómo funciona la caché](#cómo-funciona-la-caché)
- [Estructura del proyecto](#estructura-del-proyecto)
- [Desarrollo y validaciones](#desarrollo-y-validaciones)
- [Solución de problemas](#solución-de-problemas)
- [Privacidad y uso responsable](#privacidad-y-uso-responsable)
- [Licencia](#licencia)

## Características

- **Fuente configurable:** utiliza la URL M3U que introduzcas en los ajustes.
- **Fuente inicial:** viene configurado con el índice público de [IPTV-org](https://github.com/iptv-org/iptv).
- **Exploración por categorías:** agrupa los canales mediante los metadatos de la lista.
- **Listado completo:** permite consultar todos los canales reconocidos.
- **Búsqueda:** filtra por nombre del canal o por categoría.
- **Logotipos:** muestra el logotipo cuando la lista proporciona una URL `tvg-logo`.
- **Caché local configurable:** reduce las descargas repetidas de la lista.
- **Reproducción en Kodi:** entrega la URL del canal al reproductor de Kodi.
- **Validación básica de seguridad:** acepta fuentes y direcciones de emisión HTTP o HTTPS y limita el tamaño de descarga de la lista.
- **Sin catálogo de emisiones propio:** el complemento no incorpora archivos M3U ni direcciones de canales de terceros.

## Compatibilidad

- Kodi con soporte para complementos Python 3.
- El manifiesto del complemento requiere la API `xbmc.python` versión `3.0.0`.
- Conexión a Internet para consultar la lista configurada y acceder a las emisiones.

La disponibilidad y reproducción de cada canal dependen de la fuente M3U, del servidor de emisión, de la conexión del usuario y de los formatos que pueda reproducir su instalación de Kodi.

## Instalación

### Opción 1: instalar el ZIP generado por GitHub Actions

El flujo de trabajo del repositorio valida el código y genera un ZIP instalable como artefacto de GitHub Actions.

1. Abre la sección [Actions](https://github.com/Said1235/free-tv/actions).
2. Entra en una ejecución completada correctamente del flujo **Validate and package FREE TV**.
3. Busca la sección **Artifacts** al final de la página.
4. Descarga el artefacto llamado `FREE-TV-Kodi-addon-1.0.1`.
5. Descomprime el archivo descargado. Dentro encontrarás el ZIP del complemento.
6. Abre Kodi.
7. Ve a **Complementos → Instalar desde archivo ZIP**.
8. Selecciona el ZIP de FREE TV y confirma la instalación.

> Es posible que Kodi solicite habilitar la instalación desde fuentes desconocidas. Activa esa opción únicamente si confías en el archivo que estás instalando.

### Opción 2: crear el ZIP desde el código fuente

Clona el repositorio:

```bash
git clone https://github.com/Said1235/free-tv.git
cd free-tv
```

Genera el paquete desde el directorio del complemento:

```bash
cd plugin.video.iptvlegal
zip -r ../FREE-TV-1.0.1.zip . -x '__pycache__/*' '*.pyc'
```

Después, instala `FREE-TV-1.0.1.zip` desde Kodi siguiendo los pasos indicados arriba.

**Importante:** el archivo `addon.xml` debe quedar en la raíz del ZIP. No comprimas únicamente la carpeta contenedora `plugin.video.iptvlegal`, porque Kodi necesita encontrar el manifiesto en la raíz del paquete.

## Configuración

Desde Kodi:

1. Abre **Complementos → Mis complementos → Complementos de vídeo**.
2. Selecciona **FREE TV**.
3. Entra en **Configurar**.

| Ajuste | Valor inicial | Descripción |
| --- | --- | --- |
| URL de la lista M3U | `https://iptv-org.github.io/iptv/index.m3u` | Dirección HTTP o HTTPS de la lista que quieres consultar. |
| Caché de lista (segundos) | `1800` | Tiempo durante el que se reutiliza la lista guardada. El valor `0` desactiva la caché. El ajuste permite hasta 86400 segundos. |
| User-Agent HTTP | Vacío | Cabecera User-Agent opcional para la solicitud de la lista. Si se deja vacía, FREE TV utiliza un valor basado en la versión de Kodi y del complemento. |

Puedes sustituir la fuente predeterminada por cualquier lista M3U a la que tengas acceso y cuyo uso esté autorizado.

## Uso

Al abrir FREE TV encontrarás estas opciones:

| Opción | Función |
| --- | --- |
| **Categorías** | Muestra los grupos encontrados en la lista y la cantidad de canales de cada uno. |
| **Todos los canales** | Muestra todos los canales que el complemento ha podido reconocer. |
| **Buscar canal** | Permite buscar por nombre de canal o categoría. |
| **Ajustes** | Abre la configuración de la URL M3U, la caché y el User-Agent. |

Selecciona un canal para solicitar su reproducción mediante Kodi. FREE TV no controla la disponibilidad del servidor remoto ni puede garantizar que una emisión siga activa.

## Formato de listas M3U

El complemento reconoce listas M3U extendidas que contienen una cabecera `#EXTM3U`, metadatos `#EXTINF` y una dirección de emisión HTTP o HTTPS asociada.

Ejemplo ilustrativo:

```m3u
#EXTM3U
#EXTINF:-1 tvg-name="Canal de ejemplo" tvg-logo="https://example.org/logo.png" group-title="Noticias",Canal de ejemplo
https://example.org/stream.m3u8
```

Los metadatos que puede utilizar incluyen:

- `tvg-name`: nombre alternativo del canal cuando no se proporciona un nombre después de la coma de `#EXTINF`.
- `tvg-logo`: dirección del logotipo del canal.
- `tvg-id`: identificador del canal, conservado durante el análisis.
- `group-title`: categoría o grupo del canal.
- `#EXTGRP:`: etiqueta alternativa para asignar el grupo.

Las direcciones de emisión deben utilizar HTTP o HTTPS. Las entradas con otros esquemas se descartan. El ejemplo anterior es ficticio y sirve únicamente para mostrar la estructura del formato.

## Cómo funciona la caché

FREE TV guarda una copia local de la lista M3U y sus metadatos para evitar descargarla en cada consulta.

- El valor inicial es **1800 segundos (30 minutos)**.
- Con **0**, la caché queda desactivada.
- La caché se considera válida únicamente si coincide la URL configurada y no ha vencido el tiempo establecido.
- Cuando cambias la URL de la lista, la copia asociada a la dirección anterior no se reutiliza.
- La descarga tiene un límite de **25 MiB** y un tiempo de espera de **20 segundos**.

La caché se refiere al archivo M3U, no a las emisiones de vídeo. No garantiza que un canal siga disponible.

## Estructura del proyecto

```text
free-tv/
├── .github/
│   └── workflows/
│       └── validate.yml
├── LICENSE
├── README.md
└── plugin.video.iptvlegal/
    ├── addon.xml
    ├── default.py
    ├── icon.png
    └── resources/
        └── settings.xml
```

| Archivo | Propósito |
| --- | --- |
| `plugin.video.iptvlegal/addon.xml` | Identificador, versión, dependencias y metadatos del complemento. |
| `plugin.video.iptvlegal/default.py` | Menús, descarga y análisis M3U, búsqueda y reproducción. |
| `plugin.video.iptvlegal/resources/settings.xml` | Opciones configurables desde Kodi. |
| `plugin.video.iptvlegal/icon.png` | Icono del complemento. |
| `.github/workflows/validate.yml` | Validación automática y generación del ZIP instalable. |
| `LICENSE` | Condiciones de licencia MIT del código del proyecto. |

## Desarrollo y validaciones

El repositorio incluye un flujo de GitHub Actions que se ejecuta en eventos de publicación de cambios (`push`) y solicitudes de integración (`pull_request`).

El flujo realiza estas tareas:

1. Prepara Python 3.11.
2. Comprueba la sintaxis de `plugin.video.iptvlegal/default.py` mediante `py_compile`.
3. Comprueba que `addon.xml` y `resources/settings.xml` sean XML válidos.
4. Construye el ZIP del complemento.
5. Publica el ZIP como artefacto de la ejecución.

Puedes consultar el resultado en [GitHub Actions](https://github.com/Said1235/free-tv/actions).

Para ejecutar localmente las comprobaciones básicas:

```bash
python -m py_compile plugin.video.iptvlegal/default.py

python -c "import xml.etree.ElementTree as ET; ET.parse('plugin.video.iptvlegal/addon.xml'); ET.parse('plugin.video.iptvlegal/resources/settings.xml')"
```

Estas comprobaciones verifican sintaxis Python y estructura XML. No sustituyen una prueba de instalación y reproducción dentro de Kodi ni certifican que las listas o emisiones externas funcionen.

## Solución de problemas

**La lista no carga**

- Comprueba que la URL esté escrita correctamente.
- Verifica que la dirección sea HTTP o HTTPS.
- Abre la URL desde un navegador para comprobar que el servidor responde.
- Confirma que el contenido sea una lista M3U y que incluya `#EXTM3U` al comienzo del documento.
- Revisa que la lista no supere el límite de 25 MiB y que el servidor responda dentro del tiempo de espera.

**La lista carga, pero no aparecen canales**

- Comprueba que contenga entradas `#EXTINF` seguidas de direcciones de emisión.
- Verifica que las direcciones de los canales utilicen HTTP o HTTPS.
- Ten presente que el complemento ignora las entradas que no puede asociar con una dirección de emisión compatible.

**Un canal aparece, pero no reproduce**

- La dirección puede haber caducado o el servidor puede estar fuera de servicio.
- La fuente puede requerir autorización, cabeceras u otros mecanismos que el complemento no gestione.
- El formato de la emisión puede no ser compatible con tu instalación de Kodi.

**Los cambios de la lista no aparecen inmediatamente**

- Espera a que venza el periodo de caché o establece la caché en `0` mientras realizas pruebas.
- Comprueba que hayas guardado la nueva URL en los ajustes.

Para obtener más información, consulta el registro de Kodi y busca mensajes relacionados con `plugin.video.iptvlegal`.

## Privacidad y uso responsable

- FREE TV descarga la lista desde la URL que configura el usuario.
- Guarda localmente la lista y metadatos de caché cuando esta función está activada.
- No incluye un catálogo propio de canales ni aloja o retransmite los vídeos.
- No incorpora mecanismos de analítica o telemetría en el código del complemento.
- La lista y las emisiones proceden de servidores externos. Esos servidores pueden registrar las solicitudes conforme a sus propias políticas.

El usuario es responsable de la procedencia de las listas, de los derechos de acceso a los canales y de cumplir las leyes aplicables en su ubicación.

FREE TV es un proyecto independiente. No está afiliado, patrocinado ni certificado por Kodi ni por IPTV-org. La referencia a IPTV-org corresponde únicamente a la URL M3U configurada inicialmente.

## Licencia

El código de este proyecto se distribuye bajo la licencia [MIT](LICENSE).

La licencia del complemento no concede derechos sobre las emisiones, marcas, logotipos, listas de reproducción ni otros contenidos de terceros. Cada fuente mantiene sus propios términos y condiciones.

---

**Repositorio:** https://github.com/Said1235/free-tv  
**ID del complemento:** `plugin.video.iptvlegal`  
**Nombre:** FREE TV  
**Versión:** `1.0.1`
