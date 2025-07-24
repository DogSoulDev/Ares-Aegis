#!/usr/bin/env python3
"""
Setup script para Ares Aegis
Sistema de Ciberseguridad Avanzado para Kali Linux
"""

from setuptools import setup, find_packages
import os
import shutil

# Función para leer el archivo README
def read_file(filename):
    with open(filename, encoding='utf-8') as f:
        return f.read()

# Función para copiar recursos
def copy_data_files():
    data_files = []
    
    # Recursos (iconos e imágenes)
    if os.path.exists('recursos'):
        recursos = []
        for file in os.listdir('recursos'):
            if file.endswith(('.png', '.jpg', '.jpeg', '.gif', '.ico')):
                recursos.append(os.path.join('recursos', file))
        if recursos:
            data_files.append(('share/ares-aegis/recursos', recursos))
    
    # Configuración
    if os.path.exists('configuracion'):
        config_files = []
        for file in os.listdir('configuracion'):
            if file.endswith(('.json', '.txt', '.conf')):
                config_files.append(os.path.join('configuracion', file))
        if config_files:
            data_files.append(('share/ares-aegis/configuracion', config_files))
    
    # Data (wordlists, etc.)
    if os.path.exists('data'):
        for root, dirs, files in os.walk('data'):
            for file in files:
                if not file.startswith('.'):
                    rel_path = os.path.relpath(root, '.')
                    full_path = os.path.join(root, file)
                    target_dir = f'share/ares-aegis/{rel_path}'
                    data_files.append((target_dir, [full_path]))
    
    return data_files

setup(
    name="ares-aegis",
    version="4.0.0",
    author="DogSoulDev",
    author_email="dogsouldev@github.com",
    description="Sistema de Ciberseguridad Avanzado para Kali Linux",
    long_description=read_file("README.md") if os.path.exists("README.md") else "Ares Aegis - Cybersecurity Suite",
    long_description_content_type="text/markdown",
    url="https://github.com/DogSoulDev/Ares-Aegis",
    packages=find_packages(),
    data_files=copy_data_files(),
    entry_points={
        'console_scripts': [
            'ares-aegis=ares_aegis.main:main',
        ],
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Information Technology",
        "Topic :: Security",
        "Topic :: System :: Systems Administration",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: POSIX :: Linux",
        "Environment :: X11 Applications :: Qt",
    ],
    python_requires=">=3.8",
    install_requires=[
        # Solo librerías estándar de Python
        # Dependencias del sistema manejadas por el paquete .deb
    ],
    keywords="cybersecurity, kali-linux, security-tools, penetration-testing, vulnerability-scanner",
    project_urls={
        "Bug Reports": "https://github.com/DogSoulDev/Ares-Aegis/issues",
        "Source": "https://github.com/DogSoulDev/Ares-Aegis",
        "Documentation": "https://github.com/DogSoulDev/Ares-Aegis/blob/main/README.md",
    },
    include_package_data=True,
    zip_safe=False,
    platforms=["Linux"],
)
