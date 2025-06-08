# 📋 CHECKLIST DE ENTREGA - WesterosTracker

## ✅ Pasos Completados
- [x] ✅ Estructura de carpetas creada (src/, doc/)
- [x] ✅ Código fuente copiado a src/
- [x] ✅ Archivo info.txt creado
- [x] ✅ Documentación técnica generada
- [x] ✅ Script de entrega automático creado

## 🔄 Pasos Pendientes (IMPORTANTES)

### 1. 📝 Completar Información Personal
- [ ] Editar `entrega_proyecto/doc/info.txt` con:
  - [ ] Tu apellido1_apellido2_nombre
  - [ ] Tu DNI completo
  - [ ] URL de tu repositorio Git

### 2. 📚 Generar PDF de Documentación
- [ ] Convertir `entrega_proyecto/doc/documentacion.md` a PDF
- [ ] Opciones para convertir:
  - Usar pandoc: `pandoc documentacion.md -o documentacion.pdf`
  - Usar editor online como Typora
  - Copiar a Google Docs y exportar como PDF
  - Usar herramienta online de conversión

### 3. 🗂️ Crear Repositorio Git (SI NO LO TIENES)
- [ ] Crear repositorio en GitHub/GitLab
- [ ] Subir todo el código
- [ ] Actualizar URL in info.txt

### 4. 📦 Generar Entrega Final
```bash
# Ejecutar script con tus datos reales:
./generar_entrega.sh TU_APELLIDO1_APELLIDO2_NOMBRE TU_DNI
# Ejemplo: ./generar_entrega.sh garcia_lopez_juan 12345678A
```

### 5. ✅ Verificar Contenido del ZIP
El archivo ZIP debe contener:
```
ALS-proyecto-apellido1_apellido2_nombre-dni/
├── src/
│   ├── app/
│   ├── sirope-master/
│   ├── app.py
│   ├── config.py
│   ├── requirements.txt
│   └── README.md
└── doc/
    ├── info.txt (con TUS datos)
    ├── documentacion.md
    └── documentacion.pdf (IMPORTANTE!)
```

### 6. 🚀 Subir a Plataforma
- [ ] Subir ZIP a plataforma de docencia
- [ ] Asunto del envío: `ALS-proyecto-apellido1_apellido2_nombre-dni`
- [ ] Verificar que el archivo se subió correctamente

## 🎯 Puntos Críticos para Evitar Pérdida de Nota

### ⚠️ OBLIGATORIO
- [ ] Nomenclatura exacta del archivo
- [ ] Estructura de carpetas src/doc/
- [ ] info.txt completo y correcto
- [ ] PDF de documentación incluido
- [ ] Solo formato ZIP (NO RAR ni otros)

### 🏆 Recomendaciones Extra
- [ ] Probar que la aplicación funciona antes de entregar
- [ ] Verificar que requirements.txt está actualizado
- [ ] Revisar que no hay archivos temporales en el ZIP
- [ ] Hacer backup del proyecto

## 🆘 Comandos de Emergencia

Si necesitas verificar que todo funciona:
```bash
# 1. Probar la aplicación
python app.py

# 2. Verificar dependencias
pip install -r requirements.txt

# 3. Revisar estructura
tree entrega_proyecto/

# 4. Generar entrega
./generar_entrega.sh TUS_DATOS_AQUI
```

## 📞 Contactos de Emergencia
- Plataforma de docencia: [URL_PLATAFORMA]
- Email profesor: [EMAIL_PROFESOR]
- Fecha límite: [FECHA_EXAMEN]

---
🏰 **"Winter is coming... but your project is ready!"** 🏰