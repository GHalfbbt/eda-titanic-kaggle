
# EDA Titanic (Kaggle) — Guía de uso (Windows 10 + Git Bash + uv)

Este repositorio contiene un ejemplo de **Análisis Exploratorio de Datos (EDA)** del clásico dataset **Titanic** (Kaggle), pensado para principiantes. La guía explica cómo instalar dependencias con **uv**, descargar los datos de **Kaggle**, abrir el proyecto en **JupyterLab** y ejecutar el notebook paso a paso.

Se busca también la práctica de cargado y limpieza de datos, estadísticas descriptivas y visualización con Python, pandas, matplotlib y seaborn, además de el flujo de trabajo con uv y JupyterLab. No está orientado a producción; los resultados son demostrativos y con fines estrictamente educativos.

---

## 1) Requisitos

- **Git Bash** (puedes usar VS Code si quieres).
- **uv** instalado y accesible en tu PATH. Comprueba:
  ```bash
  uv --version
  ```
- **Python 3.9+** (recomendado 3.10–3.12).
- **JupyterLab** (se instala como dependencia).
- **Cuenta Kaggle** y **kaggle.json** (para descargar los CSV).

> Si no quieres usar Kaggle, puedes cargar el dataset de `seaborn` (necesita internet). En este repo lo usamos desde **Kaggle** para que cualquiera pueda replicar sin depender de la conectividad.

---

## 2) Instalación de dependencias

### Opción A — Proyecto con `pyproject.toml` (recomendada con uv)
Si este repositorio ya trae un `pyproject.toml`, simplemente:

```bash
# 1) Clona el repo
git clone https://github.com/TU_USUARIO/eda-titanic-kaggle.git
cd eda-titanic-kaggle

# 2) Crea el entorno
uv venv .venv

# 3) Instala dependencias declaradas en el TOML
uv sync
```

> Si **no** existe `pyproject.toml` y quieres crearlo con uv:
> ```bash
> uv init --name eda-titanic-kaggle
> uv add pandas matplotlib seaborn scipy scikit-learn jupyterlab ipykernel kaggle
> uv sync
> ```

### Opción B — `requirements.txt` (alternativa clásica)
Si prefieres gestionar deps con `requirements.txt`:

```bash
uv venv .venv
source .venv/Scripts/activate
uv pip install -r requirements.txt
```

> **No mezcles** A y B en el mismo proyecto. Elige un método y quédate con él.

---

## 3) Datos de Kaggle (descarga y preparación)

1) En la web de Kaggle → **Account** → **Create New API Token** → se descarga `kaggle.json`.
2) Colócalo en tu HOME de usuario:
   ```bash
   mkdir -p /c/Users/USUARIO/.kaggle
   mv /c/Users/USUARIO/Downloads/kaggle.json /c/Users/USUARIO/.kaggle/kaggle.json
   chmod 600 /c/Users/USUARIO/.kaggle/kaggle.json
   ```
3) Descarga el dataset de la competición Titanic y descomprime en `data/`:
   ```bash
   uvx kaggle competitions download -c titanic -p data
   unzip data/titanic.zip -d data
   # Esperado: data/train.csv, data/test.csv, data/gender_submission.csv
   ```

---

## 4) Ejecutar el proyecto en JupyterLab

```bash
# Lanza JupyterLab
# (Con venv activado:)
source .venv/Scripts/activate
jupyter lab
# (O sin activar el venv:)
# uv run jupyter lab
```

En JupyterLab:
1. Abre el notebook: `notebooks/eda-titanic-kaggle.ipynb`.
2. Selecciona el **kernel** del entorno (menú **Kernel → Change Kernel…**).  
   - Si no aparece, créalo una vez:
     ```bash
     python -m ipykernel install --user --name eda-titanic --display-name "Python (eda-titanic)"
     ```
     Cierra y vuelve a abrir JupyterLab.
3. Ejecuta todo: **Run → Run All Cells** (o usa `Shift+Enter` por celda).

Los gráficos aparecen **inline** (debajo de cada celda). Los CSV limpios se guardan en la carpeta del proyecto (p. ej. `titanic_clean.csv`, `titanic_encoded.csv`).

---

## 5) Estructura recomendada del proyecto

```
eda-titanic-kaggle/
├─ .venv/                      # entorno virtual (no subir a git)
├─ data/                       # CSVs descargados de Kaggle (opcional subir)
│  ├─ train.csv
│  ├─ test.csv
│  └─ titanic.zip
├─ figures/                    # (opcional) PNGs si decides guardarlos
├─ notebooks/
│  └─ eda-titanic-kaggle.ipynb
├─ pyproject.toml              # O, alternativamente, requirements.txt
├─ requirements.txt            # (si usas este método)
├─ README.md
└─ .gitignore
```

**.gitignore** sugerido:
```
.venv/
__pycache__/
*.ipynb_checkpoints
data/*.zip
.kaggle/
```

> Si no quieres subir los CSV de Kaggle, añade `data/` completo al `.gitignore` y no los incluyas en `git add`.

---

## 6) ¿Necesito guardar imágenes en `figures/`?

**No es obligatorio.** Las salidas de las celdas (gráficas incluidas) quedan **embebidas** dentro del `.ipynb`, por lo que **GitHub** las muestra al visualizar el notebook.  
Solo guarda PNGs en `figures/` si:
- Quieres reutilizarlos (README, informes externos).
- Te preocupa el tamaño del `.ipynb` o su render en GitHub en notebooks muy pesados.
- Prefieres versionar imágenes sueltas.

Para guardar además de mostrar inline:
```python
# antes de plt.show():
import os; os.makedirs("figures", exist_ok=True)
plt.savefig("figures/plot_hist_age.png", dpi=150, bbox_inches="tight")
plt.show()
```

Puedes insertar un PNG guardado en una **celda Markdown** con:
```markdown
![Hist edad](../figures/plot_hist_age.png)
```

---

## 7) Descripciones para cada gráfica (añadir como celda Markdown debajo)

- **Histograma de edad** (`age`): distribución de edades; permite ver asimetrías, modas y huecos. Útil para decidir imputación/transformaciones.
- **Conteo `survived` (0/1)**: balance de clases; si hay desbalance fuerte, puede afectar evaluación/modelado.
- **Boxplot `fare` por `survived`**: compara tarifas entre sobrevivientes y no; suele observarse mayor `fare` en quienes sobrevivieron (relación con `pclass`).
- **Conteo `sex` con `hue=survived`**: supervivencia por sexo; en Titanic se observa mayor tasa en mujeres (y niños).
- **Matriz de correlación (numéricas)**: relación lineal entre variables numéricas; útil para detectar colinealidades y posibles predictoras.
- **Boxplot `age`** (outliers IQR): valores extremos en `age`; orientar winsorización, recorte o transformaciones.
- **Boxplot `fare`** (outliers IQR): `fare` suele tener cola larga y outliers altos; considerar escalado/winsorización.

> Añade una **celda de texto (Markdown)** debajo de **cada** celda con gráfico y pega la descripción correspondiente (puedes adaptarla a lo que observes en tus datos).

---

## 8) Subir a GitHub

```bash
git init
git add notebooks/eda-titanic-kaggle.ipynb README.md .gitignore
# Si usas pyproject.toml:
git add pyproject.toml
# O si usas requirements.txt:
git add requirements.txt
# (Opcional) Figuras y/o datos si decides subirlos:
# git add figures/
# git add data/train.csv data/test.csv

git commit -m "EDA Titanic: notebook, dependencias y guía de uso"
git branch -M main
git remote add origin https://github.com/TU_USUARIO/eda-titanic-kaggle.git
git push -u origin main
```

---

## 9) Solución de problemas comunes

- **`kaggle: Could not find kaggle.json`** → coloca el token en `C:\Users\USUARIO\.kaggle\kaggle.json` y repite la descarga.
- **El kernel no aparece** → instala con `python -m ipykernel install ...` y reinicia JupyterLab.
- **Error al imputar (`ValueError: 2`)** → usa `.ravel()` al asignar `fit_transform`, e.g. `df["age"] = SimpleImputer(...).fit_transform(df[["age"]]).ravel()`.
- **`describe(include="object")` falla** → usa `include=["object","category"]` o detecta columnas antes.

---

¡Listo! Con esto, cualquier usuario podrá instalar, ejecutar el notebook, ver los resultados y (si quiere) guardar las gráficas como archivos separados.
