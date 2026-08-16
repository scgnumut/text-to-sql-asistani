import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import the translation module
from i18n.translations import t, get_current_language

# Test the translation function
print("Testing translation function:")
print(f"Current language: {get_current_language()}")
print(f"Translating 'app_title': {t('app_title')}")
print(f"Translating 'welcome_title': {t('welcome_title')}")
print(f"Translating 'language': {t('language')}")

# Test with different languages
print("\n--- Testing English ---")
# Temporarily change the language to English
st.session_state = {}
st.session_state["lang"] = "en"
print(f"English app_title: {t('app_title')}")
print(f"English welcome_title: {t('welcome_title')}")

print("\n--- Testing Turkish ---")
# Temporarily change the language to Turkish
st.session_state = {}
st.session_state["lang"] = "tr"
print(f"Turkish app_title: {t('app_title')}")
print(f"Turkish welcome_title: {t('welcome_title')}")