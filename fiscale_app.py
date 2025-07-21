import streamlit as st
import pandas as pd
from io import StringIO
from fiscale_vragen import fiscale_vragen  # <-- Zorg dat dit bestand in je repo staat!

# --- BEGIN APP ---
st.set_page_config(page_title="Fiscale Multi-Agent AI", layout="centered")
st.title("🤖 Fiscale Jaarrekening AI met Multi-Agent Simulatie")
st.write("Upload je boekhoudbestand (CSV) en zie hoe onze AI-agents samenwerken aan een fiscale jaarrekening.")

def agent_block(title, color, feedback):
    st.markdown(
        f'''
        <div style="background-color:{color}; padding:18px; border-radius:10px; border:2px solid #3bc984; margin-bottom:18px; margin-top:18px;">
        <h3 style="color:#fff; margin-top:0; margin-bottom:8px;">{title}</h3>
        <pre style="color:#fff; font-size:15px; margin-top:0;">{feedback}</pre>
        </div>
        ''',
        unsafe_allow_html=True,
    )

uploaded_file = st.file_uploader("📌 Upload je CSV-bestand", type=["csv"])

if uploaded_file is not None:
    try:
        agent_block("📜 Inlees-agent", "#22523b", "Ik controleer het bestand op structuur en kolommen…")
        df = pd.read_csv(uploaded_file)

        if not {"Grootboekrekening", "Bedrag (EUR)"}.issubset(df.columns):
            st.error("CSV moet de kolommen 'Grootboekrekening' en 'Bedrag (EUR)' bevatten.")
        else:
            for kolom in ["Herkenning", "Fiscaal aftrekbaar (EUR)", "Toelichting", "Correctie (EUR)"]:
                if kolom in df.columns:
                    df.drop(columns=kolom, inplace=True)

            def bepaal_posttype(omschrijving):
                omschrijving = omschrijving.lower()
                if "representatie" in omschrijving or "relatiegeschenk" in omschrijving:
                    return "Representatiekosten"
                elif "auto" in omschrijving or "lease" in omschrijving:
                    return "Autokosten"
                elif "huur" in omschrijving:
                    return "Huisvestingskosten"
                else:
                    return "Overige kosten"

            df["Herkenning"] = df["Grootboekrekening"].apply(bepaal_posttype)
            analyse_feedback = ""
            for i, rij in df.iterrows():
                analyse_feedback += f"- Rij {i+1}: '{rij['Grootboekrekening']}' geclassificeerd als {rij['Herkenning']}\n"
            agent_block("🧠 Analyse-agent", "#3d405b", analyse_feedback)

            toelichtingen = []
            correctie_feedback_lines = []
            def corrigeer(rij):
                bedrag = rij["Bedrag (EUR)"]
                soort = rij["Herkenning"]
                if soort == "Representatiekosten":
                    toelichting = "80% aftrekbaar volgens fiscale regels"
                    fiscaal = bedrag * 0.8
                elif soort == "Autokosten":
                    toelichting = "90% aftrekbaar voor zakelijke autokosten"
                    fiscaal = bedrag * 0.9
                else:
                    toelichting = "Volledig aftrekbaar"
                    fiscaal = bedrag
                correctie_feedback_lines.append(f"- Rij '{rij['Grootboekrekening']}': {toelichting}")
                toelichtingen.append(toelichting)
                return fiscaal

            df["Fiscaal aftrekbaar (EUR)"] = df.apply(lambda rij: corrigeer(rij), axis=1)
            df["Toelichting"] = toelichtingen
            df["Correctie (EUR)"] = df["Bedrag (EUR)"] - df["Fiscaal aftrekbaar (EUR)"]

            correctie_feedback = "\n".join(correctie_feedback_lines)
            agent_block("⚖️ Correctie-agent", "#a14a76", correctie_feedback)

            st.success("✅ Fiscale correcties voltooid!")
            st.dataframe(df)

            output = StringIO()
            df.to_csv(output, index=False)
            st.download_button(
                label="📅 Download fiscale jaarrekening (CSV)",
                data=output.getvalue(),
                file_name="fiscale_jaarrekening_agents.csv",
                mime="text/csv"
            )

    except Exception as e:
        st.error(f"Fout bij verwerken van bestand: {e}")
else:
    st.info("Wacht op bestand… De agents staan klaar om te starten.")

# -------------------- VRAGENLIJST AGENT -----------------------
st.markdown("---")
st.header("🕵️‍♂️ Fiscale vragenlijst (AI-agent)")

st.write(
    "Beantwoord deze aanvullende fiscale vragen voor een volledige fiscale controle en risico-analyse. "
    "Deze vragen zijn gebaseerd op actuele wetgeving, waaronder ATAD2 en relevante VPB-regels."
)

antwoorden = {}
for vraag in fiscale_vragen:
    antwoord = st.text_area(vraag, key=f"vraag_{vraag[:20]}")
    antwoorden[vraag] = antwoord

if st.button("📝 Sla fiscale vragen en antwoorden op"):
    st.success("Je antwoorden zijn opgeslagen! (Let op: alleen zichtbaar in deze sessie)")
    st.write(antwoorden)
