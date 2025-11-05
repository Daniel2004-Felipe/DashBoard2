import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import matplotlib.pyplot as plt
import base64
from io import BytesIO

# === 1. Cargar datos ===
file_path = "C:/Users/Gelip/OneDrive/Documentos/Analisis de datos/Listado_de_Entidades_del_Sector_Solidario_20251104.csv"

df = pd.read_csv(file_path)

# === 2. Calcular KPIs ===
total_entidades = df['CODENTIDAD'].nunique()
promedio_entidades_por_departamento = total_entidades / df['DEPARTAMENTO'].nunique()

tipo_dist = df['NOMBRETIPO'].value_counts()
tipo_percent = (tipo_dist / tipo_dist.sum()) * 100

top_actividades = df['NOMBREACTIVIDAD'].value_counts().head(5)
top_actividades_percent = (top_actividades / df['NOMBREACTIVIDAD'].value_counts().sum()) * 100

regional_dist = df['DEPARTAMENTO'].value_counts().head(10)
regional_percent = (regional_dist / df['DEPARTAMENTO'].value_counts().sum()) * 100

municipal_top = df['MUNICIPIO'].value_counts().head(10)

supervision_dist = df['SUPERVISION'].value_counts()
supervision_percent = (supervision_dist / supervision_dist.sum()) * 100

anio_reciente = df['AÑO'].max()
mes_reciente = df[df['AÑO'] == anio_reciente]['MES'].mode()[0]
reportes_actualizados = df[(df['AÑO'] == anio_reciente) & (df['MES'] == mes_reciente)]
num_actualizados = reportes_actualizados.shape[0]
percent_actualizados = (num_actualizados / total_entidades) * 100

# === 3. Guardar resumen de KPIs en CSV ===
resumen_data = {
    'KPI': [
        'Número Total de Entidades',
        'Promedio de Entidades por Departamento',
        'Año Más Reciente de Reporte',
        'Mes Más Reciente de Reporte',
        'Número de Entidades Actualizadas',
        'Porcentaje de Entidades Actualizadas (%)'
    ],
    'Valor': [
        total_entidades,
        round(promedio_entidades_por_departamento, 2),
        anio_reciente,
        mes_reciente,
        num_actualizados,
        round(percent_actualizados, 2)
    ]
}
resumen_df = pd.DataFrame(resumen_data)
resumen_df.to_csv("resumen_kpis.csv", index=False)

# === 4. Visualizaciones Plotly ===

# Tarjetas de indicadores
cards = go.Figure()
cards.add_trace(go.Indicator(
    mode="number",
    value=total_entidades,
    title={"text": "Total Entidades"},
    domain={'x': [0, 0.3], 'y': [0, 1]}
))
cards.add_trace(go.Indicator(
    mode="number",
    value=round(promedio_entidades_por_departamento, 2),
    title={"text": "Promedio por Depto."},
    domain={'x': [0.35, 0.65], 'y': [0, 1]}
))
cards.add_trace(go.Indicator(
    mode="number+delta",
    value=percent_actualizados,
    title={"text": "% Entidades Actualizadas"},
    domain={'x': [0.7, 1], 'y': [0, 1]}
))

# Barras por tipo de entidad
fig_tipo = px.bar(
    tipo_dist,
    x=tipo_dist.index,
    y=tipo_dist.values,
    title="Distribución por Tipo de Entidad",
    labels={'x': 'Tipo de Entidad', 'y': 'Número de Entidades'}
)

# Top 10 departamentos
fig_deptos = px.bar(
    regional_dist.sort_values(ascending=True),
    x=regional_dist.values[::-1],
    y=regional_dist.index[::-1],
    orientation='h',
    title="Top 10 Departamentos por Número de Entidades",
    labels={'x': 'Número de Entidades', 'y': 'Departamento'}
)

# Distribución por nivel de supervisión
fig_supervision = px.pie(
    names=supervision_dist.index.astype(str),
    values=supervision_dist.values,
    title="Distribución por Nivel de Supervisión"
)

# === 5. Gráficos Matplotlib (Boxplot + Histograma) ===
buf_box = BytesIO()
plt.figure(figsize=(6, 4))
plt.boxplot(df['AÑO'].dropna(), patch_artist=True)
plt.title('Boxplot de Años de Reporte')
plt.xlabel('Año')
plt.ylabel('Distribución')
plt.tight_layout()
plt.savefig(buf_box, format="png")
plt.close()
buf_box.seek(0)
boxplot_base64 = base64.b64encode(buf_box.read()).decode("utf-8")

buf_hist = BytesIO()
plt.figure(figsize=(6, 4))
plt.hist(df['AÑO'].dropna(), bins=10, edgecolor='black')
plt.title('Histograma de Años de Reporte')
plt.xlabel('Año')
plt.ylabel('Frecuencia')
plt.tight_layout()
plt.savefig(buf_hist, format="png")
plt.close()
buf_hist.seek(0)
hist_base64 = base64.b64encode(buf_hist.read()).decode("utf-8")

# === 6. Crear dashboard HTML ===
html_content = f"""
<html>
<head>
<title>Dashboard del Sector Solidario</title>
</head>
<body style="font-family:Arial;margin:20px;">
<h1>Dashboard del Sector Solidario</h1>
<h2>Indicadores Clave</h2>
<div>{cards.to_html(include_plotlyjs='cdn', full_html=False)}</div>

<h2>Distribución por Tipo de Entidad</h2>
<div>{fig_tipo.to_html(include_plotlyjs='cdn', full_html=False)}</div>

<h2>Top 10 Departamentos</h2>
<div>{fig_deptos.to_html(include_plotlyjs='cdn', full_html=False)}</div>

<h2>Distribución por Nivel de Supervisión</h2>
<div>{fig_supervision.to_html(include_plotlyjs='cdn', full_html=False)}</div>

<h2>Boxplot de Años de Reporte (Matplotlib)</h2>
<img src="data:image/png;base64,{boxplot_base64}" width="600"/>

<h2>Histograma de Años de Reporte (Matplotlib)</h2>
<img src="data:image/png;base64,{hist_base64}" width="600"/>

<br><br>
<a href="resumen_kpis.csv" download>📊 Descargar KPIs en CSV</a>
</body>
</html>
"""

with open("dashboard_sector_solidario.html", "w", encoding="utf-8") as f:
    f.write(html_content)

print("✅ Dashboard creado: dashboard_sector_solidario.html")
print("✅ KPIs exportados: resumen_kpis.csv")
