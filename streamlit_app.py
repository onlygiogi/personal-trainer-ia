import google.generativeai as genai
import streamlit as st
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
import re
import io

# Configura l'API di Gemini
genai.configure(api_key="AIzaSyDZNh_5y93w9i8PiorQfDBDeEzq6BksxVs")

# UI di Streamlit
st.set_page_config(page_title="UniBuddy", layout="centered")
st.title("🤖 UniBuddy")
st.write("Rispondi alle domande e scopri i corsi di laurea più adatti a te!")

# Sezione di domande
materie = st.multiselect("📚 Quali materie preferisci?", [
    "Matematica", "Fisica", "Chimica", "Biologia", "Storia", "Filosofia", "Letteratura",
    "Lingue straniere", "Informatica", "Arte", "Musica", "Latino", "Greco", "Educazione fisica"
    ])

abilità = st.multiselect("💡 In cosa ti senti bravo?", [
    "Problem Solving", "Creatività", "Comunicazione", "Analisi Dati", "Progettazione",
    "Scrittura", "Tecnologia", "Lavoro in Team", "Leadership", "Empatia",
    "Organizzazione", "Pensiero Critico", "Manualità", "Precisione", "Public Speaking", "Non saprei/Altro"
])

interessi = st.multiselect("🎨 Quali sono i tuoi principali interessi?", [
    "Sport", "Videogiochi", "Lettura", "Musica", "Fotografia", "Scrittura",
    "Viaggi", "Moda", "Scienza", "Tecnologia", "Business", "Cucina", "Cinema/Serie TV", "Non saprei/Altro"
])

aree_studio = st.multiselect("📖 Quali aree di studio ti piacerebbe approfondire maggiormente?", [
    "Scienze", "Ingegneria", "Medicina", "Economia", "Giurisprudenza",
    "Scienze Umanistiche", "Lingue", "Arte e Design", "Marketing", "Psicologia",
    "Informatica", "Scienze Politiche", "Biotecnologie", "Architettura", "Sostenibilità", "Non saprei/Altro"
])

ambito_lavoro = st.multiselect("💼 In quale ambito ti piacerebbe lavorare?", [
    "Sanità e Medicina", "Tecnologia e Informatica", "Scienze e Ricerca",
    "Arte e Design", "Marketing e Comunicazione", "Legale e Giuridico",
    "Ambito Sociale ed Educativo", "Business e Management", "Ingegneria e Costruzioni",
    "Settore Creativo (Moda, Musica, Cinema)", "Ambiente e Sostenibilità", "Non saprei/Altro"
])

stile_lavoro = st.radio("🔍 Preferisci un lavoro più...", [
    "Pratico e manuale", "Analitico e teorico", "Creativo e artistico",
    "Tecnologico e innovativo", "A contatto con le persone", "Non saprei/Altro"
])

if st.button("🚀 Scopri i corsi consigliati"):
    if not materie or not abilità or not interessi or not aree_studio or not ambito_lavoro:
        st.warning("⚠️ Seleziona almeno un'opzione per ogni domanda prima di continuare!")
    else:
        with st.spinner("Analizzando le tue risposte... ⏳"):
            # Creazione del prompt per Gemini
            prompt = f"""
            Sei un esperto di orientamento universitario. In base alle preferenze seguenti, suggerisci 3 corsi di laurea (triennali o magistrali a ciclo unico e soprattutto intraprendibili con solo il diploma) adatti con una descrizione chiara e dettagliata:
            - Materie preferite: {", ".join(materie)}
            - Abilità personali: {", ".join(abilità)}
            - Hobby e passioni: {", ".join(interessi)}
            - Aree di studio preferite: {", ".join(aree_studio)}
            - Ambito lavorativo desiderato: {", ".join(ambito_lavoro)}
            - Stile di lavoro ideale: {stile_lavoro}

            Ogni corso suggerito deve includere:
            - Nome del corso di laurea (+ Durata del corso)
            - Modalità di accesso (es. Test TOLC, ecc...)
            - Breve descrizione
            - Esami principali da sostenere
            - Sbocchi professionali principali (con stipendio medio annuo per ogni professione)
            - Magistrali intraprendibili dopo (se il corso è triennale, altrimenti salta questo passaggio)

            Infine aggiungi altri 2 corsi di laurea da prendere in considerazione anche se non rispecchiano del tutto le preferenze espressse, scrivi solamente il nome e aggiungi una breve descrizione del corso, non aggiungere nessun altro dettaglio.
            """

            # Chiamata all'IA di Google (Gemini)
            model = genai.GenerativeModel("gemini-pro")
            response = model.generate_content(prompt)

            # Mostra il risultato in modo formattato
            st.subheader("📋 Corsi consigliati per te:")
            st.markdown(response.text)

            # Funzione per creare il PDF
            def create_pdf(response_text):
                buffer = io.BytesIO()  # Crea un buffer in memoria
                doc = SimpleDocTemplate(buffer, pagesize=letter)
                styles = getSampleStyleSheet()

                # Stile personalizzato per i titoli e il testo
                title_style = ParagraphStyle(
                    'TitleStyle',
                    parent=styles['Title'],
                    fontSize=16,
                    textColor=colors.darkblue,
                    spaceAfter=10
                )

                text_style = ParagraphStyle(
                    'TextStyle',
                    parent=styles['BodyText'],
                    fontSize=12,
                    spaceAfter=8
                )

                elements = []  # Lista degli elementi nel PDF

                # Aggiungi il titolo
                elements.append(Paragraph("Risultati dell'Orientamento Universitario di UniBuddy", title_style))
                elements.append(Spacer(1, 12))  # Spazio tra titolo e contenuto

                # Converti Markdown in HTML per rispettare i formati
                formatted_text = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", response_text)  # **grassetto**
                formatted_text = re.sub(r"\*(.*?)\*", r"- \1", formatted_text)
                paragraphs = formatted_text.split("\n")

                for paragraph in paragraphs:
                    if paragraph.strip():
                        elements.append(Paragraph(paragraph, text_style))

                # Crea il PDF e lo salva nel buffer
                doc.build(elements)
                buffer.seek(0)
                return buffer

            # Bottone per scaricare il PDF
            pdf_buffer = create_pdf(response.text)
            st.download_button(
                label="📥 Scarica il PDF con i tuoi risultati",
                data=pdf_buffer,
                file_name="orientamento_universitario.pdf",
                mime="application/pdf"
            )
