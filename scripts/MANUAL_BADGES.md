# Procedimiento manual: añadir badge de Anthropic Academy

## Cuándo
Cada vez que completes un curso en Anthropic Academy.

## Pasos

### 1. Obtener los datos del badge
- Título del curso (exacto como aparece en Anthropic Academy)
- URL de verificación (ej: `https://verify.skilljar.com/c/...`)
- Fecha de obtención (formato YYYY-MM-DD)

### 2. Preparar la imagen
- Descargar la imagen del certificado/badge
- Optimizar con sharp o Gimp:
  - Tamaño: 600px de ancho
  - Formato: JPG, calidad 80%
  - Nombre: `anthropic-{nombre-curso}-opt.jpg` (minúsculas, guiones)
- Guardar en `static/images/`

### 3. Añadir entrada al JSON
Editar `data/anthropic_badges.json` y añadir al **inicio** del array:

```json
{
  "titulo": "Nombre del Curso",
  "img": "/images/anthropic-nombre-curso-opt.jpg",
  "fecha": "2026-04-01",
  "url": "https://verify.skilljar.com/c/XXXXX",
  "desc": "Descripción breve de 1-2 líneas sobre qué se aprende en el curso."
}
```

### 4. Verificar y desplegar
```bash
hugo server              # revisar en localhost
hugo --cleanDestinationDir
firebase deploy --only hosting
```

### 5. Commit
```bash
git add data/anthropic_badges.json static/images/anthropic-*
git commit -m "añadido badge Anthropic: Nombre del Curso"
git push
```

## Notas
- Mantener solo los 6 badges más recientes en el JSON
- Si hay más de 6, eliminar los más antiguos del final del array
- El campo `desc` es un resumen propio, no generado por IA
- Las imágenes locales van en `static/images/`, no en URLs externas
