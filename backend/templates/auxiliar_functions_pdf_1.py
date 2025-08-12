from datetime import datetime


def medias_oee(registros):
    # Filtra registros com valores válidos de OEE (> 0)
    #registros = [d for d in registros if d['oee'] > 0]

    if not registros:
        return "<div><p>Não há dados válidos para calcular as médias de OEE, disponibilidade, performance e qualidade.</p></div>"

    # Calcula as médias
    media_availability = sum(d['availability'] for d in registros) / len(registros)
    media_performance = sum(d['performance'] for d in registros) / len(registros)
    media_quality = sum(d['quality'] for d in registros) / len(registros)
    media_oee = sum(d['oee'] for d in registros) / len(registros)

    # Ordena por data de início
    turnos_ordenados = sorted(registros, key=lambda x: x['init'])

    # Converte strings para datetime
    inits = [datetime.fromisoformat(d['init']) for d in turnos_ordenados]
    ends = [datetime.fromisoformat(d['end']) for d in turnos_ordenados]

    # Período total da pesquisa
    inicio_pesquisa = min(inits)
    fim_pesquisa = max(ends)

    # Gera o texto descritivo
    medias_html = f"""
    <div>
        <p><strong>Análise Geral da Produção</strong></p>
        <p>Com base nos dados coletados, as médias dos indicadores de desempenho foram:</p>
        <ul>
            <li><strong>Disponibilidade:</strong> {media_availability:.2f}%</li>
            <li><strong>Desempenho:</strong> {media_performance:.2f}%</li>
            <li><strong>Qualidade:</strong> {media_quality:.2f}%</li>
            <li><strong>Eficiência Geral do Equipamento (OEE):</strong> {media_oee:.2f}%</li>
        </ul>
        <p>Esses valores refletem o desempenho médio do equipamento no período monitorado, considerando todos os turnos no período.</p>
    </div>
    """

    # Tabela HTML com dados por turno
    tabela_linhas = ""
    for i, d in enumerate(turnos_ordenados, 1):
        init_dt = datetime.fromisoformat(d['init']).strftime('%d/%m/%Y %H:%M')
        end_dt = datetime.fromisoformat(d['end']).strftime('%d/%m/%Y %H:%M')
        
        tabela_linhas += f"""
        <tr>
            <td>{i}</td>
            <td>{init_dt}</td>
            <td>{end_dt}</td>
            <td>{d['availability']:.2f}%</td>
            <td>{d['performance']:.2f}%</td>
            <td>{d['quality']:.2f}%</td>
            <td>{d['oee']:.2f}%</td>
        </tr>
        """

    tabela_html = f"""
    <p><strong>Tabela de Indicadores por Turno:</strong></p>
    <style>
        table {{
            border-collapse: collapse;
            width: 100%;
        }}
        th, td {{
            border: 1px solid #000;
            padding: 5px;
            text-align: center;
        }}
        thead {{
            background-color: #f0f0f0;
        }}
    </style>
    <table>
        <thead>
            <tr>
                <th>Turno</th>
                <th>Início</th>
                <th>Fim</th>
                <th>Disponibilidade</th>
                <th>Desempenho</th>
                <th>Qualidade</th>
                <th>OEE</th>
            </tr>
        </thead>
        <tbody>
            {tabela_linhas}
        </tbody>
    </table>
    """


    html = f"""
    <div>        
        <p><strong>Período:</strong> {inicio_pesquisa.strftime('%Y-%m-%d %H:%M:%S')} até {fim_pesquisa.strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p><strong>Total de Turnos Analisados:</strong> {len(turnos_ordenados)}</p>
        {medias_html}
        {tabela_html}
    </div>
    """

    return html.strip()

def total_producao(registros):
    if not registros:
        return "<p>Não há dados de produção disponíveis.</p>"

    total_ok = sum(d['total_ok'] for d in registros)
    total_not_ok = sum(d['total_not_ok'] for d in registros)
    total_produzido = total_ok + total_not_ok
    total_turnos = len(registros)

    # Taxas
    taxa_ok = (total_ok / total_produzido * 100) if total_produzido > 0 else 0
    taxa_not_ok = (total_not_ok / total_produzido * 100) if total_produzido > 0 else 0
    media_ok_turno = total_ok / total_turnos
    media_not_ok_turno = total_not_ok / total_turnos

    # Turno com maior produção
    maior_producao = max(registros, key=lambda x: x['total_ok'] + x['total_not_ok'])
    menor_producao = min(registros, key=lambda x: x['total_ok'] + x['total_not_ok'])

    # Turnos com produção 0
    turnos_zero = [d for d in registros if (d['total_ok'] + d['total_not_ok']) == 0]

    # Geração de HTML
    html = f"""
    <div>
        <p><strong>Análise da quantidade de Produção</strong></p>
        <ul>
            <li><strong>Total Produzido:</strong> {total_produzido}</li>
            <li><strong>Total OK:</strong> {total_ok}</li>
            <li><strong>Total com Defeito:</strong> {total_not_ok}</li>
            <li><strong>Taxa de Produtos OK:</strong> {taxa_ok:.2f}%</li>
            <li><strong>Taxa de Produtos com Defeito:</strong> {taxa_not_ok:.2f}%</li>
            <li><strong>Média de OK por turno:</strong> {media_ok_turno:.0f}</li>
            <li><strong>Média de NÃO OK por turno:</strong> {media_not_ok_turno:.0f}</li>
        </ul>

        <h4>Turno com Maior Produção</h4>
        <p><strong>Data:</strong> {datetime.fromisoformat(maior_producao['init']).strftime('%d/%m/%Y')} | 
           <strong>Produção:</strong> {maior_producao['total_ok'] + maior_producao['total_not_ok']}</p>

        <h4>Turno com Menor Produção</h4>
        <p><strong>Data:</strong> {datetime.fromisoformat(menor_producao['init']).strftime('%d/%m/%Y')} | 
           <strong>Produção:</strong> {menor_producao['total_ok'] + menor_producao['total_not_ok']}</p>
    """

    if turnos_zero:
        html += f"<h4>Turnos com Produção Zero: {len(turnos_zero)}</h4><ul>"
        for d in turnos_zero:
            data = datetime.fromisoformat(d['init']).strftime('%d/%m/%Y')
            html += f"<li>{data}</li>"
        html += "</ul>"

    html += "</div>"
    return html.strip()


def resumo_paradas(registros):
    if not registros:
        return "<p>Não há dados de produção disponíveis.</p>"

    # Downtimes
    total_downtime_nao_justificada = sum(d['downtime_summary']['nao_justificadas'] for d in registros)
    total_downtime_planejada = sum(d['downtime_summary']['planejadas'] for d in registros)
    total_downtime_nao_planejada = sum(d['downtime_summary']['nao_planejadas'] for d in registros)

    media_downtime_nao_justificada = total_downtime_nao_justificada / len(registros)
    media_downtime_planejada = total_downtime_planejada / len(registros)
    media_downtime_nao_planejada = total_downtime_nao_planejada / len(registros)

    # Geração de HTML
    html = f"""
    <div>
        <p><strong>Resumo Paradas</strong></p>

        <h4>Paradas Planejadas</h4>
        <ul>
            <li><strong>Total:</strong> {total_downtime_planejada:.2f} minutos</li>
            <li><strong>Média por turno:</strong> {media_downtime_planejada:.2f} minutos</li>
        </ul>

        <h4>Paradas Não Planejadas</h4>
        <ul>
            <li><strong>Total:</strong> {total_downtime_nao_planejada:.2f} minutos</li>
            <li><strong>Média por turno:</strong> {media_downtime_nao_planejada:.2f} minutos</li>
        </ul>

        <h4>Paradas Não Justificadas</h4>
        <ul>
            <li><strong>Total:</strong> {total_downtime_nao_justificada:.2f} minutos</li>
            <li><strong>Média por turno:</strong> {media_downtime_nao_justificada:.2f} minutos</li>
        </ul>
    </div>
    """

    return html.strip()

