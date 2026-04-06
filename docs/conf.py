import os
import sys

# 1. Додаємо шлях до кореневої папки проєкту (на рівень вище папки docs/)
sys.path.insert(0, os.path.abspath(".."))

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "the-mix-bot"
copyright = "2026, liaamirt"
author = "liaamirt"
release = "1"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

# 2. Активуємо розширення для автодокументування та Google Style
extensions = ["sphinx.ext.autodoc", "sphinx.ext.napoleon"]

# 3. Налаштовуємо Napoleon виключно на Google Style
napoleon_google_docstring = True
napoleon_numpy_docstring = False

templates_path = ["_templates"]
exclude_patterns = []

language = "uk_UA"

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

# 4. Встановлюємо сучасну тему відображення
html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]
