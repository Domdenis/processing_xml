import streamlit as st
import xml.etree.ElementTree as ET
import pandas as pd
import tempfile
import os

# Fonction pour traiter le fichier XML et générer un fichier Excel
def process_xml_to_excel(input_file_path):
    """
    Traite un fichier XML pour générer un fichier Excel (.xlsx) avec les colonnes définies.
    """
    # En-têtes Excel
    fieldnames = [
        "idSite", "idVisit", "visitIp", "visitorId", "fingerprint", "actionType",
        "actionUrl", "pageTitle", "timeSpent", "serverTimePretty", "visitServerHour",
        "referrerType", "visitDurationPretty"
    ]
    
    # Liste pour stocker les données
    rows = []
    
    # Chargement et traitement du fichier XML
    tree = ET.parse(input_file_path)
    root = tree.getroot()
    
    # Parcourir chaque visite
    for visit in root.findall("row"):
        common_data = {
            "idSite": visit.findtext("idSite"),
            "idVisit": visit.findtext("idVisit"),
            "visitIp": visit.findtext("visitIp"),
            "visitorId": visit.findtext("visitorId"),
            "fingerprint": visit.findtext("fingerprint"),
            "visitServerHour": visit.findtext("visitServerHour"),
            "referrerType": visit.findtext("referrerTypeName"),
            "visitDurationPretty": visit.findtext("visitDurationPretty"),
        }
        
        # Parcourir les actions imbriquées
        for action in visit.find("actionDetails").findall("row"):
            action_data = {
                "actionType": action.findtext("type"),
                "actionUrl": action.findtext("url"),
                "pageTitle": action.findtext("pageTitle"),
                "timeSpent": action.findtext("timeSpentPretty"),
                "serverTimePretty": action.findtext("serverTimePretty"),
            }
            
            # Fusionner les données communes et spécifiques à l'action
            row_data = {**common_data, **action_data}
            rows.append(row_data)
    
    # Conversion en DataFrame
    df = pd.DataFrame(rows, columns=fieldnames)
    
    # Sauvegarde en fichier Excel
    output_file_path = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx").name
    df.to_excel(output_file_path, index=False, engine="openpyxl")
    
    return output_file_path

# Interface Streamlit
st.title("Traitement de fichier XML en Excel")
st.write("Chargez un fichier XML pour le transformer en fichier Excel téléchargeable.")

# Upload du fichier
uploaded_file = st.file_uploader("Chargez un fichier XML", type=["xml"])

if uploaded_file:
    # Sauvegarde temporaire du fichier XML chargé
    with tempfile.NamedTemporaryFile(delete=False, suffix=".xml") as tmp_file:
        tmp_file.write(uploaded_file.read())
        tmp_file_path = tmp_file.name

    # Traitement du fichier
    st.write("Traitement en cours...")
    processed_excel_path = process_xml_to_excel(tmp_file_path)
    st.success("Traitement terminé !")

    # Téléchargement du fichier traité
    with open(processed_excel_path, "rb") as processed_file:
        st.download_button(
            label="Télécharger le fichier Excel",
            data=processed_file,
            file_name="export_xml_cleaned.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    # Supprimer les fichiers temporaires
    os.remove(tmp_file_path)
    os.remove(processed_excel_path)
