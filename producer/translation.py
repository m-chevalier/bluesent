import fasttext
from argostranslate import package, translate

_fasttext_model = None

def _get_fasttext_model():
    global _fasttext_model
    if _fasttext_model is None:
        _fasttext_model = fasttext.load_model("lid.176.ftz")
    return _fasttext_model

def detect_language_fasttext(text: str) -> str:
    fasttext_model = _get_fasttext_model()
    prediction = fasttext_model.predict(text)[0][0]
    lang_code = prediction.replace("__label__", "")
    return lang_code

def download_packages():
    # Ensure English language model packages are installed
    print("Downloading packages...")
    package.update_package_index()
    available_packages = package.get_available_packages()
    installed_packages = package.get_installed_packages()
    installed_lang_codes = [pkg.from_code for pkg in installed_packages]
    to_en_packages = [p for p in available_packages if p.to_code == "en"]
    for pkg in to_en_packages:
        if pkg.from_code in installed_lang_codes:
            continue
        print(f"Downloading package for {pkg.from_code} -> {pkg.to_code}")
        path = pkg.download()
        package.install_from_path(path)
    print("Packages downloaded and installed.")

def translate_to_english_from_lang(src_lang_code: str, text: str) -> tuple:
    installed_languages = translate.get_installed_languages()
    src_lang = next((lang for lang in installed_languages if lang.code == src_lang_code), None)
    tgt_lang = next((lang for lang in installed_languages if lang.code == "en"), None)

    if src_lang is None or tgt_lang is None:
        raise ValueError(f"No translation model found for {src_lang_code} -> en")

    translation = src_lang.get_translation(tgt_lang)
    return (translation.translate(text), src_lang_code)