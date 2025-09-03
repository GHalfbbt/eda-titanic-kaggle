# =============================================================
# EDA del Titanic (Kaggle) — Script COMENTADO para principiantes
# -------------------------------------------------------------
# Este script reproduce el flujo del notebook, pero en .py.
# Guarda tablas y gráficos en la carpeta `figures/` (se sobrescriben)
# y exporta CSVs limpios al final.
#
# Requisitos (instálalos con uv/pip):
#   pandas, numpy, matplotlib, seaborn, scipy, scikit-learn
#
# Estructura de carpetas esperada:
#   ./data/train.csv          # archivo de Kaggle (titanic)
#   ./figures/                # se creará si no existe
# =============================================================

# ----------------------------
#  Librerías y para qué sirven
# ----------------------------
# pathlib.Path    : manejo cómodo de rutas y ficheros (independiente del SO)
# matplotlib.pyplot: gráficos base (histogramas, boxplots, guardar figuras)
# pandas          : cargar CSV y manipular datos tabulares (DataFrame/Series)
# numpy           : cálculo numérico (arrays, percentiles para IQR, etc.)
# seaborn         : gráficos estadísticos "bonitos" encima de matplotlib
# scipy.stats     : contrastes de hipótesis (t-test, chi-cuadrado, ...)
# SimpleImputer   : imputar valores nulos (mediana, moda) de forma segura

from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import seaborn as sns
from scipy import stats
from sklearn.impute import SimpleImputer

# Estilo visual por defecto (opcional)
sns.set_theme()

# ----------------------------
#  Utilidades para guardar
# ----------------------------
FIG_DIR = Path("figures")
FIG_DIR.mkdir(parents=True, exist_ok=True)

def savefig(name: str, dpi: int = 150, tight: bool = True) -> None:
    """Guarda la figura actual como figures/<name>.png (sobrescribe)."""
    out = FIG_DIR / f"{name}.png"
    if tight:
        plt.savefig(out, dpi=dpi, bbox_inches="tight")
    else:
        plt.savefig(out, dpi=dpi)
    print(f"[IMG] {out}")

def save_table_image(df_or_series, name: str,
                     title: str | None = None,
                     fontsize: int = 10,
                     col_width: float = 2.2,
                     row_height: float = 0.6,
                     max_rows: int | None = 30,
                     round_ndigits: int | None = 2) -> None:
    """Renderiza un DataFrame/Series como una imagen PNG dentro de figures/<name>.png."""
    if isinstance(df_or_series, pd.Series):
        df = df_or_series.to_frame()
    else:
        df = df_or_series.copy()

    if round_ndigits is not None:
        for c in df.select_dtypes(include=[np.number]).columns:
            df[c] = df[c].round(round_ndigits)

    df.index = df.index.map(str)
    df.columns = df.columns.map(str)

    overflow_note = ""
    if max_rows is not None and len(df) > max_rows:
        df = df.iloc[:max_rows, :]
        overflow_note = f" (truncado a {max_rows} filas)"

    n_rows, n_cols = df.shape
    fig_w = max(6, col_width * (n_cols + 1))
    fig_h = max(2.5, row_height * (n_rows + 2))

    fig, ax = plt.subplots(figsize=(fig_w, fig_h))
    ax.axis("off")
    if title:
        ax.set_title(title + overflow_note, fontsize=fontsize+2, pad=10)

    table = ax.table(cellText=df.values,
                     colLabels=df.columns,
                     rowLabels=df.index,
                     cellLoc="center",
                     loc="center")
    table.auto_set_font_size(False)
    table.set_fontsize(fontsize)
    table.scale(1.0, 1.2)

    out_path = FIG_DIR / f"{name}.png"
    plt.savefig(out_path, dpi=200, bbox_inches="tight")
    plt.close(fig)
    print(f"[TABLA] {out_path}")

# ----------------------------
#  FASE 1 — Carga de datos
# ----------------------------
train_path = Path("data/train.csv")
if not train_path.exists():
    raise FileNotFoundError("No se encontró data/train.csv. Descarga desde Kaggle y colócalo ahí.")

train = pd.read_csv(train_path)

cols_map = {
    "Survived": "survived",
    "Pclass":   "pclass",
    "Sex":      "sex",
    "Age":      "age",
    "SibSp":    "sibsp",
    "Parch":    "parch",
    "Fare":     "fare",
    "Embarked": "embarked",
}
existing = [c for c in cols_map if c in train.columns]
df = train[existing].rename(columns=cols_map)

if "survived" in df.columns: df["survived"] = df["survived"].astype(int)
if "sex" in df.columns:      df["sex"]      = df["sex"].astype("category")
if "embarked" in df.columns: df["embarked"] = df["embarked"].astype("category")

print("== CARGA ==")
print("Shape:", df.shape)
print(df.dtypes)

save_table_image(df.head(), "tbl_head_raw", title="Head (raw normalizado)", round_ndigits=None)
dtypes_tbl = df.dtypes.astype(str).to_frame("dtype")
save_table_image(dtypes_tbl, "tbl_dtypes", title="Tipos de datos", round_ndigits=None)
shape_tbl = pd.DataFrame({"value":[df.shape[0], df.shape[1]]}, index=["rows","cols"])
save_table_image(shape_tbl, "tbl_shape", title="Shape del DataFrame", round_ndigits=None)

# ----------------------------
#  FASE 2 — Inspección inicial
# ----------------------------
print("\n== INSPECCIÓN ==")
nulls = df.isna().sum().sort_values(ascending=False)
print("Nulos por columna:\n", nulls.head(10))
save_table_image(nulls, "tbl_nulls", title="Valores nulos por columna", round_ndigits=None)

desc_num = df.describe()
save_table_image(desc_num, "tbl_desc_num", title="Estadísticas (numéricas)")

cat_cols = df.select_dtypes(include=["object","category"]).columns
if len(cat_cols):
    desc_cat = df[cat_cols].describe().T
    save_table_image(desc_cat, "tbl_desc_cat", title="Estadísticas (categóricas)", round_ndigits=None)
    cardinal = df[cat_cols].nunique().sort_values(ascending=False).to_frame("nunique")
    save_table_image(cardinal, "tbl_cardinality", title="Cardinalidad de categóricas", round_ndigits=None)

# ----------------------------
#  FASE 3 — Limpieza
# ----------------------------
print("\n== LIMPIEZA ==")
before = len(df)
df = df.drop_duplicates()
print("Duplicados eliminados:", before - len(df))

if "age" in df.columns:
    df["age"] = SimpleImputer(strategy="median").fit_transform(df[["age"]]).ravel()

if "embarked" in df.columns:
    df["embarked"] = df["embarked"].astype(object)
    df["embarked"] = SimpleImputer(strategy="most_frequent").fit_transform(df[["embarked"]]).ravel()
    df["embarked"] = df["embarked"].astype("category")

if {"sibsp","parch"}.issubset(df.columns):
    df[["sibsp","parch"]] = df[["sibsp","parch"]].fillna(0)
    df["sibsp"] = df["sibsp"].astype(int)
    df["parch"] = df["parch"].astype(int)
    df["family_size"] = df["sibsp"] + df["parch"] + 1

cols_verif = [c for c in ["age","embarked"] if c in df.columns]
nulls_post = df[cols_verif].isna().sum() if cols_verif else pd.Series(dtype="int64")
print("Nulos tras imputación:\n", nulls_post)

save_table_image(df.head(), "tbl_head_post_clean", title="Head tras limpieza", round_ndigits=None)
if len(nulls_post):
    save_table_image(nulls_post, "tbl_nulls_post", title="Nulos tras imputación", round_ndigits=None)

# ----------------------------
#  FASE 4 — Univariado
# ----------------------------
print("\n== UNIVARIADO ==")
if "age" in df.columns:
    plt.figure()
    df["age"].dropna().plot(kind="hist", bins=30)
    plt.title("Distribución de edad")
    plt.xlabel("Edad"); plt.ylabel("Frecuencia")
    savefig("plot_hist_age")
    plt.close()

if "survived" in df.columns:
    plt.figure()
    sns.countplot(x="survived", data=df)
    plt.title("Conteo: sobrevivió (0/1)")
    savefig("plot_count_survived")
    plt.close()

    vc = df["survived"].value_counts().rename_axis("survived").to_frame("count")
    save_table_image(vc, "tbl_survived_counts", title="Conteo survived (0/1)", round_ndigits=None)

# ----------------------------
#  FASE 5 — Bivariado
# ----------------------------
print("\n== BIVARIADO ==")
if {"fare","survived"}.issubset(df.columns):
    plt.figure()
    sns.boxplot(x="survived", y="fare", data=df)
    plt.title("Fare por sobrevivencia")
    savefig("plot_box_fare_survived")
    plt.close()

if {"sex","survived"}.issubset(df.columns):
    plt.figure()
    sns.countplot(x="sex", hue="survived", data=df)
    plt.title("Sobrevivencia por sexo")
    savefig("plot_count_sex_survived")
    plt.close()

# ----------------------------
#  FASE 6 — Correlación y outliers (IQR)
# ----------------------------
print("\n== CORRELACIÓN y OUTLIERS ==")
num_df = df.select_dtypes(include=[np.number])
corr = num_df.corr(numeric_only=True)

plt.figure()
ax = sns.heatmap(corr, annot=True, fmt=".2f", linewidths=.5)
ax.set_title("Matriz de correlación")
savefig("plot_corr_heatmap")
plt.close()

def outlier_mask_iqr(series, k: float = 1.5):
    q1, q3 = np.percentile(series.dropna(), [25, 75])
    iqr = q3 - q1
    low, high = q1 - k*iqr, q3 + k*iqr
    return (series < low) | (series > high), (low, high)

for col in ["age","fare"]:
    if col in df.columns:
        mask, (lo, hi) = outlier_mask_iqr(df[col])
        print(f"Outliers en {col}: {int(mask.sum())} (lim: {lo:.2f}, {hi:.2f})")
        plt.figure()
        sns.boxplot(x=df[col])
        plt.title(f"Boxplot {col} (IQR)")
        savefig(f"plot_box_{col}")
        plt.close()

# ----------------------------
#  FASE 7 — Tests de hipótesis
# ----------------------------
print("\n== TESTS DE HIPÓTESIS ==")
if {"fare","survived"}.issubset(df.columns):
    g1 = df.loc[df["survived"]==1, "fare"].dropna()
    g0 = df.loc[df["survived"]==0, "fare"].dropna()
    t_stat, p_val = stats.ttest_ind(g1, g0, equal_var=False)
    print(f"T-test fare | survived: t={t_stat:.3f}, p={p_val:.3e}")

if {"sex","survived"}.issubset(df.columns):
    cont = pd.crosstab(df["sex"], df["survived"])
    chi2, p, dof, _ = stats.chi2_contingency(cont)
    print("Chi-cuadrado sex ~ survived:")
    print(cont)
    print(f"chi2={chi2:.3f}, dof={dof}, p={p:.3e}")
#    # Si quieres guardar la tabla como imagen, descomenta:
#    # save_table_image(cont, "tbl_contingency_sex_survived", title="Tabla contingencia sex~survived", round_ndigits=None)

# ----------------------------
#  Export final
# ----------------------------
df_encoded = pd.get_dummies(df, drop_first=True)
df.to_csv("titanic_clean.csv", index=False)
df_encoded.to_csv("titanic_encoded.csv", index=False)
print("[CSV] titanic_clean.csv, titanic_encoded.csv")
