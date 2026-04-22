"""
Analisador GPS - Percas de Partida x Reset
Execute: python analise_gps.py
Acesse: http://localhost:5000
"""

from flask import Flask, render_template_string, request, jsonify
import pandas as pd
import traceback
import re

app = Flask(__name__)

# ═══════════════════════════════════════════════════════════════════════════
#  HTML - Design Claro e Elegante
# ═══════════════════════════════════════════════════════════════════════════
HTML = r"""<!DOCTYPE html>
<html lang="pt-br">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>GPS Analytics | Percas de Partida x Reset</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.js"></script>
<link href="https://fonts.googleapis.com/css2?family=Inter:opsz,wght@14..32,300;400;500;600;700&display=swap" rel="stylesheet">
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: 'Inter', system-ui, sans-serif; background: #f5f7fc; color: #1a2c3e; line-height: 1.5; }

.header { background: linear-gradient(135deg, #1a2c3e 0%, #2c3e50 100%); color: white; padding: 0 32px; height: 70px; display: flex; align-items: center; justify-content: space-between; box-shadow: 0 2px 10px rgba(0,0,0,0.08); position: sticky; top: 0; z-index: 100; }
.logo { display: flex; align-items: center; gap: 12px; }
.logo-icon { width: 36px; height: 36px; background: rgba(255,255,255,0.15); border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 20px; }
.logo h1 { font-size: 18px; font-weight: 600; letter-spacing: -0.3px; }
.logo p { font-size: 11px; opacity: 0.7; margin-top: 2px; }
.version { background: rgba(255,255,255,0.12); padding: 5px 12px; border-radius: 20px; font-size: 11px; font-weight: 500; }

.container { max-width: 1400px; margin: 0 auto; padding: 28px 32px; }

.upload-card { background: white; border-radius: 20px; padding: 28px; margin-bottom: 28px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); border: 1px solid #e8ecf0; }
.upload-title { font-size: 13px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; color: #5b6e8c; margin-bottom: 20px; }
.upload-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 24px; }
.upload-box { border: 2px dashed #d0d7de; border-radius: 16px; padding: 28px 24px; text-align: center; cursor: pointer; transition: all 0.2s; background: #fafbfc; }
.upload-box:hover { border-color: #3b82f6; background: #f0f7ff; }
.upload-box.ok { border-color: #10b981; border-style: solid; background: #f0fdf4; }
.upload-icon { font-size: 40px; margin-bottom: 12px; }
.upload-box strong { display: block; font-size: 14px; font-weight: 600; color: #1a2c3e; margin-bottom: 6px; }
.upload-hint { font-size: 12px; color: #6c7a91; }
.upload-filename { display: none; font-size: 12px; color: #10b981; font-weight: 500; margin-top: 10px; background: #e8f5e9; padding: 4px 12px; border-radius: 20px; display: inline-block; }
.upload-box.ok .upload-hint { display: none; }
.upload-box.ok .upload-filename { display: inline-block; }

.btn-analyze { background: linear-gradient(135deg, #3b82f6, #2563eb); color: white; border: none; padding: 12px 32px; border-radius: 12px; font-size: 14px; font-weight: 600; cursor: pointer; transition: all 0.2s; display: inline-flex; align-items: center; gap: 10px; box-shadow: 0 2px 4px rgba(59,130,246,0.2); }
.btn-analyze:hover { transform: translateY(-1px); box-shadow: 0 4px 12px rgba(59,130,246,0.3); }
.btn-analyze:disabled { background: #cbd5e1; cursor: not-allowed; transform: none; box-shadow: none; }
.status-msg { font-size: 13px; color: #6c7a91; margin-left: 16px; }

.kpi-grid { display: grid; grid-template-columns: repeat(5, 1fr); gap: 16px; margin-bottom: 28px; }
.kpi-card { background: white; border-radius: 20px; padding: 20px 18px; border: 1px solid #e8ecf0; position: relative; overflow: hidden; }
.kpi-card::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 3px; }
.kpi-card.blue::before { background: linear-gradient(90deg, #3b82f6, #8b5cf6); }
.kpi-card.green::before { background: #10b981; }
.kpi-card.orange::before { background: #f59e0b; }
.kpi-card.red::before { background: #ef4444; }
.kpi-card.purple::before { background: #8b5cf6; }
.kpi-label { font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; color: #6c7a91; margin-bottom: 8px; }
.kpi-value { font-size: 28px; font-weight: 800; color: #1a2c3e; line-height: 1.2; }
.kpi-sub { font-size: 11px; color: #6c7a91; margin-top: 6px; }
.kpi-card.blue .kpi-value { color: #3b82f6; }
.kpi-card.green .kpi-value { color: #10b981; }
.kpi-card.orange .kpi-value { color: #f59e0b; }
.kpi-card.red .kpi-value { color: #ef4444; }
.kpi-card.purple .kpi-value { color: #8b5cf6; }

.tabs { display: flex; gap: 4px; border-bottom: 1px solid #e8ecf0; margin-bottom: 24px; overflow-x: auto; }
.tab { padding: 10px 20px; font-size: 13px; font-weight: 500; cursor: pointer; border: none; background: none; color: #6c7a91; border-bottom: 2px solid transparent; margin-bottom: -1px; transition: all 0.15s; white-space: nowrap; }
.tab:hover { color: #3b82f6; background: #f0f7ff; }
.tab.active { color: #3b82f6; border-bottom-color: #3b82f6; background: #f0f7ff; }
.panel { display: none; }
.panel.active { display: block; }

.card { background: white; border-radius: 20px; border: 1px solid #e8ecf0; padding: 24px; margin-bottom: 24px; }
.card-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 20px; flex-wrap: wrap; gap: 12px; }
.card-title { font-size: 15px; font-weight: 700; color: #1a2c3e; }
.card-sub { font-size: 12px; color: #6c7a91; margin-top: 4px; }

.table-wrapper { overflow-x: auto; border-radius: 12px; border: 1px solid #e8ecf0; max-height: 520px; overflow-y: auto; }
.data-table { width: 100%; border-collapse: collapse; font-size: 13px; }
.data-table thead { position: sticky; top: 0; z-index: 10; }
.data-table th { background: #f8f9fc; padding: 12px 16px; text-align: left; font-size: 11px; font-weight: 700; color: #5b6e8c; text-transform: uppercase; letter-spacing: 0.5px; border-bottom: 1px solid #e8ecf0; }
.data-table td { padding: 12px 16px; border-bottom: 1px solid #f0f2f5; vertical-align: middle; }
.data-table tbody tr:hover td { background: #f8fafd; }

.badge { display: inline-flex; align-items: center; gap: 5px; padding: 3px 10px; border-radius: 20px; font-size: 11px; font-weight: 600; }
.badge-blue { background: #eef2ff; color: #3b82f6; }
.badge-green { background: #ecfdf5; color: #10b981; }
.badge-red { background: #fef2f2; color: #ef4444; }
.badge-orange { background: #fffbeb; color: #f59e0b; }
.badge-gray { background: #f1f5f9; color: #6c7a91; }
.badge-purple { background: #f5f3ff; color: #8b5cf6; }

.alert { padding: 14px 18px; border-radius: 12px; font-size: 13px; margin-bottom: 20px; border-left: 4px solid; }
.alert-purple { background: #f5f3ff; border-color: #8b5cf6; color: #5b21b6; }
.alert-red { background: #fef2f2; border-color: #ef4444; color: #991b1b; }
.alert-green { background: #ecfdf5; border-color: #10b981; color: #065f46; }

.search-input { padding: 8px 14px; border: 1px solid #d0d7de; border-radius: 10px; font-size: 13px; width: 220px; background: white; }
.search-input:focus { outline: none; border-color: #3b82f6; box-shadow: 0 0 0 2px rgba(59,130,246,0.1); }

.btn-csv { background: #f1f5f9; border: 1px solid #d0d7de; padding: 7px 14px; border-radius: 10px; font-size: 12px; font-weight: 500; cursor: pointer; transition: all 0.15s; color: #1a2c3e; }
.btn-csv:hover { background: #e8ecf0; }

.charts-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 24px; }
.chart-card { background: white; border-radius: 20px; border: 1px solid #e8ecf0; padding: 20px; }
.chart-title { font-size: 13px; font-weight: 600; color: #1a2c3e; margin-bottom: 16px; }
.chart-container { position: relative; height: 300px; }

.detail-kpis { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 24px; }
.detail-timeline { border: 1px solid #e8ecf0; border-radius: 12px; overflow: hidden; }
.timeline-header { display: grid; grid-template-columns: 110px 80px 80px 80px 1fr; gap: 12px; padding: 12px 16px; background: #f8f9fc; font-size: 10px; font-weight: 700; color: #5b6e8c; text-transform: uppercase; letter-spacing: 0.5px; border-bottom: 1px solid #e8ecf0; }
.timeline-row { display: grid; grid-template-columns: 110px 80px 80px 80px 1fr; gap: 12px; padding: 10px 16px; border-bottom: 1px solid #f0f2f5; align-items: center; }
.timeline-row:hover { background: #f8fafd; }
.timeline-row.crit { background: #fef2f2; }
.timeline-row.reset-day { background: #f5f3ff; }

.loading { display: none; position: fixed; inset: 0; background: rgba(0,0,0,0.6); backdrop-filter: blur(4px); z-index: 999; align-items: center; justify-content: center; flex-direction: column; gap: 16px; }
.loading.show { display: flex; }
.spinner { width: 48px; height: 48px; border: 3px solid rgba(59,130,246,0.2); border-top-color: #3b82f6; border-radius: 50%; animation: spin 0.7s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }
.loading p { color: white; font-size: 14px; font-weight: 500; }

.vehicle-select { background: white; border: 1px solid #d0d7de; border-radius: 12px; padding: 10px 14px; font-size: 13px; min-width: 280px; color: #1a2c3e; }
.percas-big { font-size: 20px; font-weight: 800; color: #ef4444; }

@media (max-width: 900px) {
  .container { padding: 16px; }
  .kpi-grid { grid-template-columns: repeat(2, 1fr); }
  .upload-grid { grid-template-columns: 1fr; }
  .charts-grid { grid-template-columns: 1fr; }
}
</style>
</head>
<body>

<div class="loading" id="loading">
  <div class="spinner"></div>
  <p>Analisando dados...</p>
</div>

<div class="header">
  <div class="logo">
    <div class="logo-icon">📍</div>
    <div>
      <h1>GPS Analytics</h1>
      <p>Percas de Partida × Fichas de Reset</p>
    </div>
  </div>
  <div class="version">v2.4</div>
</div>

<div class="container">

  <div class="upload-card">
    <div class="upload-title">📂 CARREGAR PLANILHAS</div>
    <div class="upload-grid">
      <div class="upload-box" id="box1" onclick="document.getElementById('inp1').click()">
        <input type="file" id="inp1" accept=".csv,.xlsx,.xls" style="display:none" onchange="fileSelected(this,'box1','lbl1')">
        <div class="upload-icon">📊</div>
        <strong>Percas de Partida</strong>
        <div class="upload-hint">Clique para selecionar</div>
        <div class="upload-filename" id="lbl1"></div>
      </div>
      <div class="upload-box" id="box2" onclick="document.getElementById('inp2').click()">
        <input type="file" id="inp2" accept=".csv,.xlsx,.xls" style="display:none" onchange="fileSelected(this,'box2','lbl2')">
        <div class="upload-icon">📋</div>
        <strong>Fichas Abertas CS</strong>
        <div class="upload-hint">Clique para selecionar</div>
        <div class="upload-filename" id="lbl2"></div>
      </div>
    </div>
    <div style="display: flex; align-items: center;">
      <button class="btn-analyze" id="btnOk" disabled onclick="analisar()">🔍 Analisar</button>
      <span class="status-msg" id="statusMsg"></span>
    </div>
  </div>

  <div id="resultado" style="display:none">
    <div class="kpi-grid" id="kpiRow"></div>

    <div class="tabs">
      <button class="tab active" onclick="showTab('t-reset',this)">🔄 Reset × Percas</button>
      <button class="tab" onclick="showTab('t-ranking',this)">🏆 Ranking</button>
      <button class="tab" onclick="showTab('t-criticos',this)">⚠️ Críticos sem Ficha</button>
      <button class="tab" onclick="showTab('t-isolados',this)">✅ Casos Isolados</button>
      <button class="tab" onclick="showTab('t-graficos',this)">📈 Gráficos</button>
      <button class="tab" onclick="showTab('t-detalhe',this)">🔍 Por Veículo</button>
    </div>

    <div class="panel active" id="t-reset">
      <div class="card">
        <div class="card-header">
          <div>
            <div class="card-title">🔄 Fichas de RESET × Percas de Partida</div>
            <div class="card-sub">Cada linha é uma ficha com "reset" no complemento, cruzada com percas do mesmo dia</div>
          </div>
          <button class="btn-csv" onclick="exportCSV('tResetTable','reset_x_percas')">📥 Exportar CSV</button>
        </div>
        <div id="resetKpiRow" style="display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-bottom:20px"></div>
        <div class="alert alert-purple" id="alertExemplo"></div>
        <div class="table-wrapper">
          <table class="data-table" id="tResetTable">
            <thead><tr><th>Veículo</th><th>Data do Reset</th><th>Hora</th><th>Complemento</th><th>Percas no dia</th><th>Impacto</th></tr></thead>
            <tbody id="bResetTable"></tbody>
          </table>
        </div>
      </div>
    </div>

    <div class="panel" id="t-ranking">
      <div class="card">
        <div class="card-header">
          <div><div class="card-title">🏆 Ranking de Percas no Mês</div><div class="card-sub">Todos os veículos com pelo menos 1 perca</div></div>
          <div style="display:flex;gap:10px">
            <input class="search-input" id="srRank" placeholder="🔍 Filtrar veículo..." oninput="filterTbl('tRankTable','srRank')">
            <button class="btn-csv" onclick="exportCSV('tRankTable','ranking')">📥 CSV</button>
          </div>
        </div>
        <div class="table-wrapper">
          <table class="data-table" id="tRankTable">
            <thead><tr><th>#</th><th>Veículo</th><th>Total</th><th>Dias</th><th>Máx/dia</th><th>Dias&gt;3</th><th>Resets</th><th>Percas em Reset</th><th>Ficha?</th><th>Nível</th></tr></thead>
            <tbody id="bRankTable"></tbody>
          </table>
        </div>
      </div>
    </div>

    <div class="panel" id="t-criticos">
      <div class="card">
        <div class="card-header">
          <div><div class="card-title">⚠️ Dias com &gt;3 Percas sem Ficha no CS</div><div class="card-sub">Ocorrências graves que merecem atenção especial</div></div>
          <button class="btn-csv" onclick="exportCSV('tCritTable','criticos')">📥 CSV</button>
        </div>
        <div id="alertCrit"></div>
        <div class="table-wrapper">
          <table class="data-table" id="tCritTable">
            <thead><tr><th>Veículo</th><th>Data</th><th>Percas</th><th>Gravidade</th></tr></thead>
            <tbody id="bCritTable"></tbody>
          </table>
        </div>
      </div>
    </div>

    <div class="panel" id="t-isolados">
      <div class="card">
        <div class="card-header">
          <div><div class="card-title">✅ Casos Isolados</div><div class="card-sub">1-2 percas em um único dia, sem reincidência</div></div>
          <button class="btn-csv" onclick="exportCSV('tIsolTable','isolados')">📥 CSV</button>
        </div>
        <div class="table-wrapper">
          <table class="data-table" id="tIsolTable">
            <thead><tr><th>Veículo</th><th>Data</th><th>Percas</th><th>Ficha CS?</th></tr></thead>
            <tbody id="bIsolTable"></tbody>
          </table>
        </div>
      </div>
    </div>

    <div class="panel" id="t-graficos">
      <div class="charts-grid">
        <div class="chart-card"><div class="chart-title">Top 15 Veículos com mais Percas</div><div class="chart-container"><canvas id="cTop"></canvas></div></div>
        <div class="chart-card"><div class="chart-title">Cobertura de Fichas (dias &gt;3 percas)</div><div class="chart-container"><canvas id="cPizza"></canvas></div></div>
        <div class="chart-card"><div class="chart-title">Resets com mais Percas no Dia</div><div class="chart-container"><canvas id="cReset"></canvas></div></div>
        <div class="chart-card"><div class="chart-title">Percas por Dia do Mês</div><div class="chart-container"><canvas id="cDia"></canvas></div></div>
      </div>
    </div>

    <div class="panel" id="t-detalhe">
      <div class="card">
        <div class="card-title" style="margin-bottom:16px">🔍 Histórico Detalhado por Veículo</div>
        <select class="vehicle-select" id="selV" onchange="verDet()"><option value="">-- Selecione um veículo --</option></select>
        <div id="divDet" style="margin-top:24px"></div>
      </div>
    </div>
  </div>
</div>

<script>
let DG = null, CH = {};

function fileSelected(inp, boxId, lblId) {
  let box = document.getElementById(boxId);
  let lbl = document.getElementById(lblId);
  if (inp.files && inp.files.length > 0) {
    box.classList.add('ok');
    lbl.textContent = '✓ ' + inp.files[0].name;
  } else {
    box.classList.remove('ok');
    lbl.textContent = '';
  }
  let ok = document.getElementById('inp1').files.length > 0 && document.getElementById('inp2').files.length > 0;
  document.getElementById('btnOk').disabled = !ok;
}

function showTab(id, el) {
  document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
  document.getElementById(id).classList.add('active');
  el.classList.add('active');
  if (id === 't-graficos' && DG) renderCharts(DG);
}

async function analisar() {
  let fd = new FormData();
  fd.append('file_percas', document.getElementById('inp1').files[0]);
  fd.append('file_fichas', document.getElementById('inp2').files[0]);
  document.getElementById('loading').classList.add('show');
  document.getElementById('statusMsg').textContent = '';
  try {
    let res = await fetch('/analisar', { method: 'POST', body: fd });
    let data = await res.json();
    if (data.erro) throw new Error(data.erro);
    DG = data;
    render(data);
    document.getElementById('resultado').style.display = 'block';
    document.getElementById('statusMsg').textContent = '✓ Análise concluída com sucesso!';
  } catch (e) {
    document.getElementById('statusMsg').textContent = 'Erro: ' + e.message;
    console.error(e);
  } finally {
    document.getElementById('loading').classList.remove('show');
  }
}

function render(d) {
  let kpis = [
    { l: 'Total de Percas', v: d.kpi.total_percas, s: 'no mês', c: 'blue' },
    { l: 'Veículos Afetados', v: d.kpi.veiculos, s: 'veículos únicos', c: '' },
    { l: 'Dias Críticos (>3)', v: d.kpi.dias_mais3, s: 'ocorrências graves', c: 'orange' },
    { l: 'Sem Ficha CS', v: d.kpi.sem_ficha, s: 'dias sem registro', c: 'red' },
    { l: 'Fichas de Reset', v: d.kpi.total_resets, s: d.kpi.percas_em_resets + ' percas nesses dias', c: 'purple' }
  ];
  document.getElementById('kpiRow').innerHTML = kpis.map(k => `<div class="kpi-card ${k.c}"><div class="kpi-label">${k.l}</div><div class="kpi-value">${k.v}</div><div class="kpi-sub">${k.s}</div></div>`).join('');

  let kr = d.kpi_reset;
  document.getElementById('resetKpiRow').innerHTML = [
    { l: 'Total Fichas Reset', v: kr.total, c: 'purple' },
    { l: 'Resets COM perdas', v: kr.com_percas, c: 'red' },
    { l: 'Resets SEM perdas', v: kr.sem_percas, c: 'green' },
    { l: 'Total Percas em Resets', v: kr.total_percas, c: 'orange' }
  ].map(k => `<div class="kpi-card ${k.c}"><div class="kpi-label">${k.l}</div><div class="kpi-value">${k.v}</div></div>`).join('');

  let comPerdas = d.fichas_reset.filter(r => r.percas_dia > 0);
  if (comPerdas.length > 0) {
    let ex = comPerdas[0];
    document.getElementById('alertExemplo').innerHTML = `<strong>📌 Exemplo:</strong> Veículo <strong>${ex.veiculo}</strong> em <strong>${ex.data}</strong> teve ficha de RESET e perdeu <strong>${ex.percas_dia} partida(s)</strong> no mesmo dia.`;
  } else {
    document.getElementById('alertExemplo').innerHTML = 'Nenhum reset com perdas encontrado no período.';
  }

  let resetSorted = [...d.fichas_reset].sort((a,b) => b.percas_dia - a.percas_dia);
  document.getElementById('bResetTable').innerHTML = resetSorted.map(r => {
    let percasHtml = r.percas_dia > 0 ? `<span class="percas-big">${r.percas_dia}</span>` : '0';
    let impacto = r.percas_dia >= 10 ? '<span class="badge badge-red">Extremo</span>' : r.percas_dia >= 5 ? '<span class="badge badge-orange">Alto</span>' : r.percas_dia > 0 ? '<span class="badge badge-orange">Moderado</span>' : '<span class="badge badge-green">Sem perdas</span>';
    return `<tr>
      <td><strong>${r.veiculo}</strong></td>
      <td>${r.data}</td>
      <td style="color:#6c7a91">${r.hora}</td>
      <td style="max-width:280px;font-size:12px">${r.complemento}</td>
      <td style="text-align:center">${percasHtml}</td>
      <td style="text-align:center">${impacto}</td>
    </tr>`;
  }).join('');

  document.getElementById('bRankTable').innerHTML = d.ranking.map((r, i) => `
    <tr>
      <td style="color:#6c7a91">${i+1}</td>
      <td><strong>${r.veiculo}</strong></td>
      <td style="font-weight:700;color:#3b82f6">${r.total_percas}</td>
      <td>${r.dias_com_perca}</td>
      <td>${r.max_dia}</td>
      <td>${r.dias_mais3 > 0 ? `<span style="color:#f59e0b;font-weight:700">${r.dias_mais3}</span>` : '0'}</td>
      <td>${r.fichas_reset > 0 ? `<span class="badge badge-purple">${r.fichas_reset}</span>` : '—'}</td>
      <td>${r.percas_em_resets > 0 ? `<span style="color:#ef4444;font-weight:700">${r.percas_em_resets}</span>` : '—'}</td>
      <td>${r.teve_ficha ? '<span class="badge badge-green">Sim</span>' : '<span class="badge badge-gray">Não</span>'}</td>
      <td>${nivel(r.total_percas)}</td>
    </tr>
  `).join('');

  document.getElementById('alertCrit').innerHTML = d.criticos_sem_ficha.length > 0 ? `<div class="alert alert-red">⚠️ ${d.criticos_sem_ficha.length} ocorrências com mais de 3 percas sem ficha no CS no mesmo dia.</div>` : '<div class="alert alert-green">✅ Nenhuma ocorrência crítica encontrada.</div>';
  document.getElementById('bCritTable').innerHTML = d.criticos_sem_ficha.map(r => `<tr>
    <td><strong>${r.veiculo}</strong></td>
    <td>${r.data}</td>
    <td style="color:#ef4444;font-weight:700">${r.contagem}</td>
    <td>${grav(r.contagem)}</td>
  </tr>`).join('');
  document.getElementById('bIsolTable').innerHTML = d.isolados.map(r => `<tr>
    <td><strong>${r.veiculo}</strong></td>
    <td>${r.data}</td>
    <td>${r.total_percas}</td>
    <td>${r.teve_ficha ? '<span class="badge badge-blue">Com ficha</span>' : '<span class="badge badge-gray">Sem ficha</span>'}</td>
  </tr>`).join('');

  let sel = document.getElementById('selV');
  sel.innerHTML = '<option value="">-- Selecione um veículo --</option>' + d.ranking.map(r => `<option value="${r.veiculo}">${r.veiculo} — ${r.total_percas} percas | ${r.fichas_reset} resets</option>`).join('');
}

function renderCharts(d) {
  ['cTop','cPizza','cReset','cDia'].forEach(id => { if (CH[id]) { CH[id].destroy(); CH[id] = null; } });
  let top = d.ranking.slice(0,15);
  CH.cTop = new Chart(document.getElementById('cTop'), { type: 'bar', data: { labels: top.map(r => r.veiculo), datasets: [{ data: top.map(r => r.total_percas), backgroundColor: '#3b82f6', borderRadius: 8 }] }, options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } }, scales: { y: { beginAtZero: true } } } });
  CH.cPizza = new Chart(document.getElementById('cPizza'), { type: 'doughnut', data: { labels: ['Com ficha CS', 'Sem ficha CS'], datasets: [{ data: [d.kpi.com_ficha, d.kpi.sem_ficha], backgroundColor: ['#10b981', '#ef4444'], borderWidth: 0 }] }, options: { responsive: true, maintainAspectRatio: false, cutout: '65%', plugins: { legend: { position: 'bottom' } } } });
  let rc = d.fichas_reset.filter(r => r.percas_dia > 0).slice(0,12);
  if (rc.length) CH.cReset = new Chart(document.getElementById('cReset'), { type: 'bar', data: { labels: rc.map(r => `${r.veiculo} ${r.data.slice(0,5)}`), datasets: [{ data: rc.map(r => r.percas_dia), backgroundColor: '#8b5cf6', borderRadius: 8 }] }, options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } }, scales: { y: { beginAtZero: true } } } });
  let dias = Object.keys(d.por_dia).sort();
  CH.cDia = new Chart(document.getElementById('cDia'), { type: 'line', data: { labels: dias.map(x => x.slice(0,5)), datasets: [{ data: dias.map(k => d.por_dia[k]), borderColor: '#3b82f6', backgroundColor: 'rgba(59,130,246,0.05)', fill: true, tension: 0.35 }] }, options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } }, scales: { y: { beginAtZero: true } } } });
}

async function verDet() {
  let v = document.getElementById('selV').value;
  let div = document.getElementById('divDet');
  if (!v || !DG) { div.innerHTML = ''; return; }
  let hist = DG.historico[v] || [];
  let fichas = new Set(DG.fichas_por_veiculo[v] || []);
  let resets = DG.fichas_reset.filter(r => r.veiculo === v);
  let rdatas = new Set(resets.map(r => r.data));
  let info = DG.ranking.find(r => r.veiculo === v) || {};
  let h = `<div class="detail-kpis"><div class="kpi-card blue"><div class="kpi-label">Total Percas</div><div class="kpi-value">${info.total_percas || 0}</div></div><div class="kpi-card orange"><div class="kpi-label">Dias >3 Percas</div><div class="kpi-value">${info.dias_mais3 || 0}</div></div><div class="kpi-card purple"><div class="kpi-label">Fichas Reset</div><div class="kpi-value">${info.fichas_reset || 0}</div></div><div class="kpi-card red"><div class="kpi-label">Percas em Resets</div><div class="kpi-value">${info.percas_em_resets || 0}</div></div></div>`;
  h += `<div class="detail-timeline"><div class="timeline-header"><span>Data</span><span>Percas</span><span>Ficha?</span><span>Reset?</span><span>Situação</span></div>`;
  hist.forEach(h2 => {
    let tf = fichas.has(h2.data);
    let tr = rdatas.has(h2.data);
    let g = h2.contagem > 3;
    let cls = tr ? 'reset-day' : (g && !tf) ? 'crit' : '';
    let sit = g && !tf ? '<span class="badge badge-red">Crítico s/ ficha</span>' : g && tf ? '<span class="badge badge-orange">Crítico c/ ficha</span>' : '<span class="badge badge-gray">Normal</span>';
    h += `<div class="timeline-row ${cls}"><span>${h2.data}</span><span style="font-weight:700;color:${g ? '#ef4444' : '#1a2c3e'}">${h2.contagem}</span><span>${tf ? '<span class="badge badge-green">Sim</span>' : '<span class="badge badge-gray">Não</span>'}</span><span>${tr ? '<span class="badge badge-purple">Reset</span>' : '—'}</span><span>${sit}</span></div>`;
  });
  h += `</div>`;
  if (resets.length) {
    h += `<div style="margin-top:20px"><div class="detail-timeline"><div class="timeline-header"><span>Data</span><span>Hora</span><span>Complemento</span><span>Percas</span></div>`;
    resets.forEach(r => { h += `<div class="timeline-row reset-day"><span>${r.data}</span><span style="color:#6c7a91">${r.hora}</span><span style="font-size:12px">${r.complemento}</span><span style="font-weight:700;color:${r.percas_dia > 0 ? '#ef4444' : '#10b981'}">${r.percas_dia > 0 ? r.percas_dia + ' perdas' : 'Sem perdas'}</span></div>`; });
    h += `</div></div>`;
  }
  let fd2 = DG.fichas_por_veiculo[v] || [];
  h += fd2.length ? `<div style="margin-top:20px"><div style="font-size:12px;font-weight:600;margin-bottom:10px">📋 Datas com Ficha no CS (${fd2.length})</div><div style="display:flex;flex-wrap:wrap;gap:8px">${fd2.map(f => `<span class="badge badge-blue">${f}</span>`).join('')}</div></div>` : `<div class="alert alert-red" style="margin-top:20px">⚠️ Nenhuma ficha no CS encontrada para este veículo.</div>`;
  div.innerHTML = h;
}

function nivel(t) { if (t>=80) return '<span class="badge badge-red">Crítico</span>'; if (t>=40) return '<span class="badge badge-orange">Alto</span>'; if (t>=10) return '<span class="badge badge-blue">Moderado</span>'; return '<span class="badge badge-gray">Baixo</span>'; }
function grav(n) { if (n>=15) return '<span class="badge badge-red">Extremo</span>'; if (n>=10) return '<span class="badge badge-red">Grave</span>'; if (n>=5) return '<span class="badge badge-orange">Alto</span>'; return '<span class="badge badge-blue">Moderado</span>'; }
function filterTbl(tid, sid) { let q = document.getElementById(sid).value.toLowerCase(); document.querySelectorAll('#'+tid+' tbody tr').forEach(tr => { tr.style.display = tr.textContent.toLowerCase().includes(q) ? '' : 'none'; }); }
function exportCSV(tid, nome) { let rows = Array.from(document.querySelectorAll('#'+tid+' tr')).map(tr => Array.from(tr.querySelectorAll('th,td')).map(c => '"'+c.textContent.trim().replace(/"/g,'""')+'"').join(',')); let blob = new Blob([rows.join('\n')], {type:'text/csv;charset=utf-8;'}); let a = document.createElement('a'); a.href = URL.createObjectURL(blob); a.download = nome+'.csv'; a.click(); }
</script>
</body>
</html>"""


# ═══════════════════════════════════════════════════════════════════════════
#  PYTHON - LEITURA E ANÁLISE (VERSÃO CORRIGIDA)
# ═══════════════════════════════════════════════════════════════════════════
RE_RESET = re.compile(r'reset', re.IGNORECASE)


def eh_reset(txt):
    return bool(RE_RESET.search(str(txt))) if not pd.isna(txt) else False


def extrair_codigo_veiculo(valor):
    """Extrai o código numérico do veículo de qualquer campo"""
    if pd.isna(valor):
        return ''
    valor_str = str(valor).strip()
    if valor_str == '' or valor_str == 'nan' or valor_str == 'NaN':
        return ''
    # Procura por números no texto (ex: "20075 ( 01.1XXX)" -> "20075")
    numeros = re.findall(r'\b\d{4,6}\b', valor_str)
    if numeros:
        # Pega o primeiro número com 4-6 dígitos (código do veículo)
        return str(int(numeros[0]))
    # Se não encontrou padrão, tenta converter o valor inteiro
    try:
        if valor_str.replace('.', '').replace('-', '').isdigit():
            return str(int(float(valor_str)))
    except:
        pass
    return valor_str


def ler(file):
    nome = file.filename.lower()
    if nome.endswith('.csv'):
        for enc in ['utf-8', 'latin1', 'cp1252']:
            try:
                file.seek(0)
                return pd.read_csv(file, encoding=enc, sep=';')
            except Exception:
                pass
        file.seek(0)
        return pd.read_csv(file, sep=';')
    else:
        file.seek(0)
        return pd.read_excel(file)


def analisar_dados(df_percas, df_fichas):
    print("\n" + "=" * 60)
    print("📊 INICIANDO ANÁLISE DE PERCAS x RESET")
    print("=" * 60)

    # ── 1. PERCAS DE PARTIDA ──────────────────────────────────────────
    dp = df_percas.copy()
    dp.columns = [str(c).strip() for c in dp.columns]
    dp = dp.rename(columns={dp.columns[0]: 'Veiculo', dp.columns[1]: 'Data', dp.columns[2]: 'Contagem'})

    # Limpeza
    dp = dp[~dp['Contagem'].astype(str).str.lower().str.contains('branco|blank', na=False)]
    dp['Contagem'] = pd.to_numeric(dp['Contagem'], errors='coerce')
    dp.dropna(subset=['Contagem'], inplace=True)
    dp['Contagem'] = dp['Contagem'].astype(int)
    dp = dp[dp['Contagem'] > 0]

    dp['Data'] = pd.to_datetime(dp['Data'], dayfirst=True, errors='coerce')
    dp.dropna(subset=['Data'], inplace=True)
    dp['Veiculo'] = dp['Veiculo'].astype(str).str.strip()
    dp['Veiculo'] = dp['Veiculo'].apply(extrair_codigo_veiculo)
    dp['DS'] = dp['Data'].dt.strftime('%d/%m/%Y')

    # Remove veículos vazios
    dp = dp[dp['Veiculo'] != '']
    
    print(f"   ✅ Percas: {len(dp)} registros, {dp['Veiculo'].nunique()} veículos")
    print(f"   📝 Exemplos veículos percas: {list(dp['Veiculo'].unique())[:10]}")

    # ── 2. FICHAS CS ─────────────────────────────────────────────────
    df = df_fichas.copy()
    df.columns = [str(c).strip() for c in df.columns]

    print(f"   📋 Colunas encontradas: {list(df.columns)}")

    # Coluna de data
    col_data = None
    for c in df.columns:
        if c.lower() == 'data':
            col_data = c
            break
    if col_data is None:
        col_data = df.columns[3] if len(df.columns) > 3 else df.columns[0]

    # Coluna de complemento (onde está o texto do reset)
    col_complemento = None
    for c in df.columns:
        if 'complemento' in c.lower():
            col_complemento = c
            break
    if col_complemento is None:
        col_complemento = df.columns[8] if len(df.columns) > 8 else df.columns[0]

    # Coluna de descrição do veículo (onde está o código)
    # Pode ser "Descrição Veículo" ou "Modelo Chassi"
    col_descricao = None
    for c in df.columns:
        if 'descrição' in c.lower() or 'modelo' in c.lower():
            col_descricao = c
            break
    if col_descricao is None:
        col_descricao = df.columns[9] if len(df.columns) > 9 else df.columns[0]

    print(f"   📋 Data: {col_data}, Complemento: {col_complemento}, Descrição: {col_descricao}")

    # Extrair veículo da descrição
    df['Veiculo'] = df[col_descricao].astype(str).apply(extrair_codigo_veiculo)
    
    # Se não conseguiu extrair da descrição, tenta outras colunas
    if df['Veiculo'].eq('').all():
        # Tenta coluna "Garagem" (que pode ter o código)
        for c in df.columns:
            if 'garagem' in c.lower():
                df['Veiculo'] = df[c].astype(str).apply(extrair_codigo_veiculo)
                break

    df['DataRaw'] = df[col_data].astype(str)
    df['DataF'] = pd.to_datetime(df['DataRaw'].str[:10], dayfirst=True, errors='coerce')
    df['Hora'] = df['DataRaw'].str[11:16]
    df.dropna(subset=['DataF'], inplace=True)
    df['DS'] = df['DataF'].dt.strftime('%d/%m/%Y')
    df['Compl'] = df[col_complemento].astype(str)

    # Remove veículos vazios
    df = df[df['Veiculo'] != '']

    print(f"   ✅ Fichas: {len(df)} registros, {df['Veiculo'].nunique()} veículos")
    print(f"   📝 Exemplos veículos fichas: {list(df['Veiculo'].unique())[:10]}")

    # ── 3. DETECTA RESETS E CRUZA ─────────────────────────────────────
    df['is_reset'] = df['Compl'].apply(eh_reset)
    dr = df[df['is_reset']].copy()

    print(f"\n   🔍 Resets encontrados: {len(dr)}")
    if len(dr) > 0:
        print("   📝 Exemplos de resets:")
        for _, row in dr.head(10).iterrows():
            print(f"      - Veículo {row['Veiculo']} em {row['DS']}: {row['Compl'][:60]}...")

    # Dicionário de percas por (veiculo, data)
    pmap = {(row['Veiculo'], row['DS']): int(row['Contagem']) for _, row in dp.iterrows()}

    resets_list = []
    for _, row in dr.iterrows():
        v, d2 = row['Veiculo'], row['DS']
        percas = pmap.get((v, d2), 0)
        compl = row['Compl'][:100] + ('...' if len(row['Compl']) > 100 else '')
        resets_list.append({
            'veiculo': v,
            'data': d2,
            'hora': row['Hora'] if 'Hora' in row else '',
            'complemento': compl,
            'percas_dia': int(percas)
        })

    # Ordena por percas decrescente
    resets_list.sort(key=lambda x: x['percas_dia'], reverse=True)

    total_resets = len(resets_list)
    com_percas_n = sum(1 for r in resets_list if r['percas_dia'] > 0)
    sem_percas_n = total_resets - com_percas_n
    total_p_reset = sum(r['percas_dia'] for r in resets_list)

    print(f"\n   📊 ESTATÍSTICAS DE RESET:")
    print(f"      - Total de resets: {total_resets}")
    print(f"      - Resets com perdas: {com_percas_n}")
    print(f"      - Resets sem perdas: {sem_percas_n}")
    print(f"      - Total percas em dias de reset: {total_p_reset}")

    # Mostrar resets com perdas
    if com_percas_n > 0:
        print(f"\n   📝 Resets com perdas:")
        for r in [r for r in resets_list if r['percas_dia'] > 0][:10]:
            print(f"      - Veículo {r['veiculo']} em {r['data']}: {r['percas_dia']} perda(s)")

    # Contagem por veículo
    rpv = {}
    ppv = {}
    for r in resets_list:
        v = r['veiculo']
        rpv[v] = rpv.get(v, 0) + 1
        ppv[v] = ppv.get(v, 0) + r['percas_dia']

    # ── 4. RANKING ────────────────────────────────────────────────────
    grp = dp.groupby('Veiculo').agg(
        total_percas=('Contagem', 'sum'),
        dias_com_perca=('Contagem', 'count'),
        max_dia=('Contagem', 'max'),
        dias_mais3=('Contagem', lambda x: (x > 3).sum()),
    ).reset_index().sort_values('total_percas', ascending=False)

    fv = set(df['Veiculo'].unique())
    grp['teve_ficha'] = grp['Veiculo'].isin(fv)
    grp['fichas_reset'] = grp['Veiculo'].map(rpv).fillna(0).astype(int)
    grp['percas_em_resets'] = grp['Veiculo'].map(ppv).fillna(0).astype(int)

    ranking = []
    for _, row in grp.iterrows():
        ranking.append({
            'veiculo': row['Veiculo'],
            'total_percas': int(row['total_percas']),
            'dias_com_perca': int(row['dias_com_perca']),
            'max_dia': int(row['max_dia']),
            'dias_mais3': int(row['dias_mais3']),
            'teve_ficha': bool(row['teve_ficha']),
            'fichas_reset': int(row['fichas_reset']),
            'percas_em_resets': int(row['percas_em_resets'])
        })

    # ── 5. CRÍTICOS SEM FICHA ─────────────────────────────────────────
    m3 = dp[dp['Contagem'] > 3].copy()
    
    # Criar conjunto de (veiculo, data) que TEM ficha no CS
    fichas_set = set(zip(df['Veiculo'], df['DS']))
    
    # Marcar quais dias com >3 percas têm ficha
    m3['tem_ficha'] = m3.apply(lambda row: (row['Veiculo'], row['DS']) in fichas_set, axis=1)
    
    # Filtrar apenas os que NÃO têm ficha
    criticos_sem_ficha_df = m3[~m3['tem_ficha']].sort_values(['Veiculo', 'Data'])
    
    criticos = []
    for _, row in criticos_sem_ficha_df.iterrows():
        criticos.append({
            'veiculo': row['Veiculo'],
            'data': row['DS'],
            'contagem': int(row['Contagem'])
        })
    
    print(f"\n   📊 CRÍTICOS SEM FICHA: {len(criticos)} ocorrências")

    # ── 6. CASOS ISOLADOS ────────────────────────────────────────────
    iso = grp[(grp['total_percas'] <= 2) & (grp['dias_com_perca'] == 1)]
    isolados = []
    for _, row in iso.iterrows():
        v = row['Veiculo']
        reg = dp[dp['Veiculo'] == v].iloc[0]
        isolados.append({
            'veiculo': v,
            'data': reg['DS'],
            'total_percas': int(row['total_percas']),
            'teve_ficha': bool(row['teve_ficha'])
        })

    # ── 7. HISTÓRICO ─────────────────────────────────────────────────
    historico = {}
    for v, g in dp.groupby('Veiculo'):
        historico[v] = [{'data': r['DS'], 'contagem': int(r['Contagem'])} for _, r in g.sort_values('Data').iterrows()]

    fichas_por_veiculo = {v: sorted(g['DS'].unique().tolist()) for v, g in df.groupby('Veiculo')}
    por_dia = {k: int(v) for k, v in dp.groupby('DS')['Contagem'].sum().items()}

    print("\n" + "=" * 60)
    print("📊 RESUMO FINAL")
    print("=" * 60)
    print(f"   Total de percas: {int(dp['Contagem'].sum())}")
    print(f"   Veículos afetados: {int(dp['Veiculo'].nunique())}")
    print(f"   Dias com >3 percas: {len(m3)}")
    print(f"   Dias com >3 percas COM ficha: {int(m3['tem_ficha'].sum())}")
    print(f"   Dias com >3 percas SEM ficha: {len(criticos)}")
    print(f"   Total de resets: {total_resets}")
    print(f"   Resets com perdas: {com_percas_n}")
    print("=" * 60)

    return {
        'kpi': {
            'total_percas': int(dp['Contagem'].sum()),
            'veiculos': int(dp['Veiculo'].nunique()),
            'dias_mais3': int(len(m3)),
            'com_ficha': int(m3['tem_ficha'].sum()),
            'sem_ficha': len(criticos),
            'total_resets': total_resets,
            'percas_em_resets': int(total_p_reset),
        },
        'kpi_reset': {
            'total': total_resets,
            'com_percas': com_percas_n,
            'sem_percas': sem_percas_n,
            'total_percas': int(total_p_reset),
        },
        'ranking': ranking,
        'criticos_sem_ficha': criticos,
        'isolados': isolados,
        'fichas_reset': resets_list,
        'historico': historico,
        'fichas_por_veiculo': fichas_por_veiculo,
        'por_dia': por_dia,
    }


@app.route('/')
def index():
    return render_template_string(HTML)


@app.route('/analisar', methods=['POST'])
def analisar():
    try:
        resultado = analisar_dados(
            ler(request.files['file_percas']),
            ler(request.files['file_fichas'])
        )
        return jsonify(resultado)
    except Exception as e:
        print(traceback.format_exc())
        return jsonify({'erro': str(e) + '\n' + traceback.format_exc()})


if __name__ == '__main__':
    print("=" * 55)
    print("  📍 GPS Analytics - Percas de Partida x Reset")
    print("  ✅ Extrai código do veículo da descrição (ex: 20075, 20030)")
    print("  🌐 Acesse: http://localhost:5000")
    print("=" * 55)
    app.run(debug=False, port=5000)