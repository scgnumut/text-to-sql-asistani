from i18n.translations import t

print("Turkish test:")
print(t("app_title"))
print(t("welcome_title"))

print("\nEnglish test:")
print(t("app_title", lang="en"))
print(t("welcome_title", lang="en"))