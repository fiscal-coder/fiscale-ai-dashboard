import streamlit as st
import pandas as pd
from io import StringIO

st.set_page_config(page_title="Fiscale Jaarrekening AI", layout="centered")
st.title("📊 AI-tool voor Fiscale Jaarrekening")
st.write("Upload hieronder je boekhoudbestand (CSV). De AI berekent de fiscale correcties automatisch.")

uploaded_file = st.file_uploader("Upload je CSV-bestand", type=["csv"])

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)

        if not {"Grootboekrekening", "Bedrag (EUR)"}.issubset(df.columns):
            st.error("CSV moet de kolommen 'Grootboekrekening' en 'Bedrag (EUR)' bevatten.")
        else:
            def corrigeer_fiscaal(rij):
                grootboek = rij["Grootboekrekening"].lower()
                bedrag = rij["Bedrag (EUR)"]
                if "representatie" in grootboek or "relatiegeschenk" in grootboek:
                    return bedrag * 0.8
                else:
                    return bedrag

            df["Fiscaal aftrekbaar (EUR)"] = df.apply(corrigeer_fiscaal, axis=1)
            df["Fiscale correctie (EUR)"] = df["Bedrag (EUR)"] - df["Fiscaal aftrekbaar (EUR)"]

            st.success("✅ Fiscale correcties toegepast!")
            st.dataframe(df)

            output = StringIO()
            df.to_csv(output, index=False)
            st.download_button(
                label="📥 Download resultaat als CSV",
                data=output.getvalue(),
                file_name="fiscale_correctie_resultaat.csv",
                mime="text/csv"
            )
    except Exception as e:
        st.error(f"Fout bij verwerken van bestand: {e}")
else:
    st.info("Wacht op bestand...")
