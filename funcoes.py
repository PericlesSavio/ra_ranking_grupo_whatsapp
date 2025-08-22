import json
import requests
import pandas as pd
from datetime import datetime, timedelta


def load_json_vercel(filepath):
    r = requests.get(f'https://tsyfkkmmojo4ck9c.public.blob.vercel-storage.com/{filepath}')
    return r.json()

def save_json_vercel(filename, data):
    json_bytes = json.dumps(data, ensure_ascii=False).encode("utf-8")
    
    url = f"https://blob.vercel-storage.com/{filename}"
    headers = {
        "Authorization": f"Bearer vercel_blob_rw_tSyfkKMmojo4CK9C_rGbToWtoABXIkZMc5mLcvedmlHbg1T",
        "Content-Type": "application/json",
        "x-add-random-suffix": "0",
        "x-allow-overwrite": "1",
        "x-cache-control-max-age": "60"
    }
    r = requests.put(url, headers=headers, data=json_bytes)
    return r.json()

def informar_atualizacao(filepath):
    url = f'https://tsyfkkmmojo4ck9c.public.blob.vercel-storage.com/{filepath}'
    r = requests.get(url)
    last_modified = r.headers.get("last-modified")    
    dt = datetime.strptime(last_modified, "%a, %d %b %Y %H:%M:%S %Z")
    dt_brasil = dt - timedelta(hours=3)
    ultima_atualizacao = dt_brasil.strftime("%d/%m/%Y %H:%M:%S")
    return ultima_atualizacao

def converter_url(df):
    df['Youtube'] = df['Youtube'].fillna('')
    df['Youtube'] = df['Youtube'].apply(
        lambda x: f'<a href="{x}" target="_blank" rel="noopener noreferrer">{x.rsplit("/", 1)[-1]}</a>' if x else ''
    )
    df['Avatar'] = df['Avatar'].apply(
        lambda url: f'<img src="{url}" alt="User Pic" style="max-height:50px;">' if pd.notnull(url) else ''
    )
    df['Usuário'] = df['Usuário'].apply(
        lambda x: f'<a href="https://retroachievements.org/user/{x}" target="_blank" rel="noopener noreferrer">{x.rsplit("/", 1)[-1]}</a>' if x else ''
    )
    return df

class RA:
    def __init__(self, my_user='Teste123Teste', api_key='iOQsyUkclggYi3OFOabPSmNs0Hx5fc2t'):
        self.my_user = my_user
        self.api_key = api_key
        self.base_url = "https://retroachievements.org/API"

    def get_user_profile(self, username):
        url = f"{self.base_url}/API_GetUserProfile.php"
        params = {"z": self.my_user, "y": self.api_key, "u": username}
        try:
            response = requests.get(url, params=params)
            data = response.json()
            if data and not data.get('message'):
                return data
        except Exception as e:
            print(f"Erro RA API: {e}")
        return None
