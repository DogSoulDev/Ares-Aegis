# Configuración de VS Code para Ares Aegis

## Tareas Configuradas

### ⚡ Ejecutar Ares Aegis
- **Comando**: `python3 main.py`
- **Acceso rápido**: Ctrl+Shift+P → "Tasks: Run Task" → "Ejecutar Ares Aegis (main.py)"

### 🔧 Scripts Adicionales

#### Verificar Proyecto
```bash
python3 verificar_proyecto.py
```

#### Inicio Rápido
```bash
./iniciar.sh
```

### 🎨 Configuración Recomendada

#### Extensiones VS Code
- Python
- Python Docstring Generator
- autoDocstring
- GitLens

#### Settings.json
```json
{
    "python.defaultInterpreterPath": "python3",
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "files.exclude": {
        "**/__pycache__": true,
        "**/*.pyc": true
    }
}
```

### 🚀 Desarrollo

#### Estructura MVC
- **Modelos**: `src/modelos/` - Lógica de negocio
- **Vista**: `src/vista/` - Interfaz gráfica
- **Controlador**: `src/controladores/` - Coordinación

#### Tests
```bash
python3 -m pytest tests/
```

#### Debug
```bash
export ARES_LOG_LEVEL=DEBUG
python3 main.py
```
