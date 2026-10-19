import requests
import folium

# 1. Autenticação na API da SPTrans
token = input("Cole seu token da SPTrans: ")
session = requests.Session()
response = session.post(f"http://api.olhovivo.sptrans.com.br/v2.1/Login/Autenticar?token={token}")

if response.json() is True:
    print("Autenticação realizada com sucesso!")
    
    # Criar o mapa base com um servidor de tiles alternativo e gratuito (OpenStreetMap France)
    mapa = folium.Map(
        location=[-23.55052, -46.633309],
        zoom_start=12,
        tiles='https://{s}.tile.openstreetmap.fr/osmfr/{z}/{x}/{y}.png',
        attr='&copy; OpenStreetMap France | &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    )
    
    # 2. Buscar Paradas
    res_paradas = session.get("http://api.olhovivo.sptrans.com.br/v2.1/Parada/Buscar?nomeBuscar=PIRITUBA")
    paradas = res_paradas.json()
    
    if isinstance(paradas, dict):
        paradas = [paradas]
        
    print(f"Paradas encontradas: {len(paradas)}")
    
    # Adicionar pins das PARADAS no mapa (Cor: Verde)
    for parada in paradas:
        if isinstance(parada, dict):
            lat = parada.get("Py") or parada.get("py")
            lon = parada.get("Px") or parada.get("px")
            
            if lat is not None and lon is not None:
                folium.Marker(
                    location=[lat, lon],
                    popup=parada.get("np", "Parada"),
                    tooltip=parada.get("ed", "Endereço não informado"),
                    icon=folium.Icon(color="green", icon="bus", prefix="fa")
                ).add_to(mapa)
        
    # 3. Buscar Posições dos Ônibus em Tempo Real
    codigo_linha = 2541
    res_posicao = session.get(f"http://api.olhovivo.sptrans.com.br/v2.1/Posicao/Linha?codigoLinha={codigo_linha}")
    dados_posicao = res_posicao.json()
    
    veiculos = []
    if isinstance(dados_posicao, dict):
        veiculos = dados_posicao.get("vs", [])
        
    print(f"Veículos encontrados em tempo real: {len(veiculos)}")
    
    # Adicionar pins dos VEÍCULOS no mapa (Cor: Vermelho)
    for veiculo in veiculos:
        if isinstance(veiculo, dict):
            lat_v = veiculo.get("py") or veiculo.get("Py")
            lon_v = veiculo.get("px") or veiculo.get("Px")
            
            if lat_v is not None and lon_v is not None:
                folium.Marker(
                    location=[lat_v, lon_v],
                    popup=f"Veículo: {veiculo.get('p', 'N/A')}",
                    tooltip="Ônibus em tempo real",
                    icon=folium.Icon(color="red", icon="info-sign")
                ).add_to(mapa)

    # 4. Salvar o mapa gerado
    mapa.save("mapa_onibus.html")
    print("Mapa gerado com sucesso em mapa_onibus.html!")
else:
    print("Falha na autenticação. Verifique o seu token.")
