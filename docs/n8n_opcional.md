# n8n Opcional

n8n no es obligatorio para la primera versión académica. La carga manual desde la interfaz es suficiente para demostrar el flujo funcional del agente.

## Justificación para no usarlo en la primera versión

- Reduce complejidad de instalación.
- Evita depender de servicios adicionales.
- Permite concentrarse en datasets, RAG, analítica y frontend.
- Es más presentable para una defensa académica inicial.

## Flujos opcionales futuros

### Ingesta automática de datasets

1. Programar revisión de fuentes oficiales.
2. Descargar archivos nuevos.
3. Enviar archivo a `POST /datasets/upload`.
4. Validar perfil de datos.
5. Notificar actualización.

### Actualización documental RAG

1. Revisar nuevas guías metodológicas.
2. Descargar PDF.
3. Enviar a `POST /rag/upload-documents`.
4. Registrar fuente y fecha.

### Reportes

1. Ejecutar exportación CSV o Excel.
2. Guardar en carpeta compartida.
3. Notificar al equipo académico.

## Conclusión

n8n se recomienda como mejora futura si el proyecto requiere actualización periódica de fuentes, monitoreo y notificaciones automáticas.
