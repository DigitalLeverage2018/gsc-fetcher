import streamlit as st
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import pandas as pd

CLIENT_SECRET_FILE = 'client_secret.json'  # Deine OAuth-JSON im gleichen Ordner
SCOPES = ['https://www.googleapis.com/auth/webmasters.readonly']

def authenticate():
    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
    auth_url, _ = flow.authorization_url(prompt='consent')
    st.markdown(f"[🔗 Zum Google Login hier klicken]({auth_url})")
    
    code = st.text_input("Bitte den Authentifizierungscode eingeben")
    if code:
        flow.fetch_token(code=code)
        creds = flow.credentials
        return creds
    return None

def main():
    st.title("Google Search Console Abfrage mit Streamlit")

    creds = authenticate()
    if creds:
        service = build('searchconsole', 'v1', credentials=creds)
        sites = service.sites().list().execute()
        props = [site['siteUrl'] for site in sites.get('siteEntry', [])]
        st.write("Deine Properties:")
        property = st.selectbox("Wähle eine Property aus", props)
        
        if property:
            start_date = st.date_input("Startdatum")
            end_date = st.date_input("Enddatum")
            if st.button("Abfrage starten"):
                request = {
                    'startDate': start_date.isoformat(),
                    'endDate': end_date.isoformat(),
                    'dimensions': ['query'],
                    'rowLimit': 1000
                }
                response = service.searchanalytics().query(siteUrl=property, body=request).execute()
                rows = response.get('rows', [])
                data = [{
                    'Query': r['keys'][0],
                    'Clicks': r.get('clicks', 0),
                    'Impressions': r.get('impressions', 0),
                    'CTR': r.get('ctr', 0),
                    'Position': r.get('position', 0)
                } for r in rows]
                df = pd.DataFrame(data)
                st.dataframe(df)
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="Als CSV herunterladen",
                    data=csv,
                    file_name='gsc_queries.csv',
                    mime='text/csv'
                )

if __name__ == "__main__":
    main()
