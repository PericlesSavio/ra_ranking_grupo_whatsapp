import pandas as pd
import time
from flask import Flask, render_template, request
from funcoes import RA, informar_atualizacao, load_json_vercel, save_json_vercel, converter_url, delete_user_json_vercel

app = Flask(__name__)
ra = RA()

@app.context_processor
def menu():
    menu_items = [
        {"nome": "Página Inicial", "rota": "/"},
        {"nome": "Adicionar/Atualizar Usuário", "rota": "/usuario"},
    ]
    return dict(menu_items=menu_items)

@app.route('/', methods=['GET'])
def index():
    ultima_atualizacao = informar_atualizacao('dados_ra.json')
    dados_ra = load_json_vercel('dados_ra.json')
    dados_pessoais = load_json_vercel('dados_pessoais.json')

    for i in dados_ra:
        i['UserPicURL'] = f"https://retroachievements.org{i['UserPic']}"

    df_dados_ra = pd.DataFrame(dados_ra)
    df_dados_pessoais = pd.DataFrame(dados_pessoais)

    final = pd.merge(
        df_dados_ra,
        df_dados_pessoais,
        left_on='User',
        right_on='Username',
        how='right',
        suffixes=('_ra', '_personal')
    )

    col_numericas = ['TotalPoints', 'TotalTruePoints', 'TotalSoftcorePoints', 'Ano']
    for col in col_numericas:
        if col in final.columns:
            final[col] = final[col].fillna(0)

    final['Ratio'] = final.apply(
        lambda row: round(row['TotalTruePoints'] / row['TotalPoints'], 2) if row['TotalPoints'] > 0 else 0,
        axis=1
    )

    final = final[['Username', 'Nome', 'UserPicURL', 'TotalPoints', 'TotalTruePoints',
                   'Ratio', 'TotalSoftcorePoints', 'Ano', 'Telefone', 'Dev', 'Youtube']]
    final.columns = ['Usuário', 'Nome', 'Avatar', 'HardPoints', 'RetroPoints', 'Ratio',
                     'SoftPoints', 'Ano', 'Telefone', 'Dev', 'Youtube']

    final.insert(0, '#', range(1, len(final) + 1))
    final = final.sort_values(by='HardPoints', ascending=False).reset_index(drop=True)
    final.drop(columns=["Telefone"], inplace=True)

    final = converter_url(final)

    tabela_html = final.to_html(index=False, escape=False) if not df_dados_ra.empty else ""
    return render_template('index.html', tabela=tabela_html, ultima_atualizacao=ultima_atualizacao)

@app.route('/usuario', methods=['GET', 'POST'])
def usuario():
    dados_pessoais = load_json_vercel('dados_pessoais.json')
    sucesso = False
    falha = False
    mudanca_username = False
    username_final = ''

    if request.method == 'POST':
        username = request.form.get('Username')
        profile = ra.get_user_profile(username)
        username_final = profile.get('User')
        
        if profile.get('User') != username:
            mudanca_username = True
        
        if profile:
            nome = request.form.get('Nome')
            ano_str = request.form.get('Ano', '').strip()
            dev = request.form.get('Dev')
            youtube = request.form.get('Youtube')

            dados_pessoais = [u for u in dados_pessoais if u.get('Username') != username]
            dados_pessoais.append({
                'Username': profile.get('User'),
                'Nome': nome,
                'Ano': ano_str,
                'Dev': dev,
                'Youtube': youtube
            })

            save_json_vercel('dados_pessoais.json', dados_pessoais)
            sucesso = True
        else:
            falha = True

    return render_template(
        'usuario.html',
        sucesso=sucesso,
        falha=falha,
        usuario=locals().get("username", ""),
        profile=username_final,
        mudanca_username=mudanca_username,
    )

@app.route('/atualizar', methods=['GET'])
def atualizar():
    dados_pessoais = load_json_vercel('dados_pessoais.json')
    membros = []
    dados_ra = []

    for i in dados_pessoais:
        membros.append(i['Username'])

    for i in membros:
        time.sleep(3)
        perfil = ra.get_user_profile(i)
        print(perfil)
        if perfil:
            dados_ra.append(perfil)

    save_json_vercel('dados_ra.json', dados_ra)
    return render_template('atualizar.html')

@app.route('/deletar_usuario', methods=['GET', 'POST'])
def deletar_usuario():
    sucesso = False
    falha = False

    if request.method == 'POST':
        username = request.form.get('Username')
        try:
            delete_user_json_vercel(username)
            sucesso = True
        except Exception as e:
            print(f"Erro ao deletar usuário: {e}")
            falha = True

    return render_template(
        'deletar_usuario.html',
        sucesso=sucesso,
        falha=falha
    )

if __name__ == '__main__':
    app.run(debug=True)
