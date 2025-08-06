import os
import json
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from collections import Counter
from pathlib import Path

# ============================ CONFIG ============================
PASTA_MAPEADA = Path(os.getenv("SNP_DATA_DIR", "resultados/snps_filtrados"))
NUM_CLUSTERS = int(os.getenv("NUM_CLUSTERS", 8))
MAX_LABEL_LENGTH = 50  # máximo de caracteres por rótulo no gráfico
SAVE_CLUSTER_REPORT = True
SAVE_FIG_PATH = f"cluster_visualization_{pd.Timestamp.now().strftime('%Y-%m-%d_%H-%M-%S')}.png"

CUSTOM_STOPWORDS = set([
    "common", "normal", "aka", "clinvar", "pmid",
    "in", "on", "with", "gene", "genes", "receptor",
    "associated", "variant", "rsid", "risk", "increased",
    "the", "a", "to", "of", "is", "and"
])

# ============================ LOAD ============================
def carregar_snps(diretorio):
    dados = []
    for arquivo in diretorio.glob("*.json"):
        with open(arquivo, encoding="utf-8") as f:
            snp = json.load(f)
            if not (snp.get("found_snpedia_data") or snp.get("found_myvariant_data")):
                continue
            if not (snp.get("trait") or snp.get("resumo") or snp.get("descricao_livre")):
                continue
            texto = " ".join([
                snp.get("trait", ""),
                snp.get("resumo", ""),
                snp.get("descricao_livre", "")
            ]).strip()
            if texto:
                dados.append({"rsid": snp["rsid"], "texto": texto})
    return pd.DataFrame(dados)

# ============================ NLP + CLUSTER ============================
def clusterizar(df):
    tfidf = TfidfVectorizer(
        stop_words=list(CUSTOM_STOPWORDS),
        max_features=1000,
        token_pattern=r"\b[a-zA-Z][a-zA-Z\-]+\b"
    )
    X = tfidf.fit_transform(df["texto"])

    kmeans = KMeans(n_clusters=NUM_CLUSTERS, random_state=42)
    df["cluster"] = kmeans.fit_predict(X)

    pca = PCA(n_components=2)
    [coords] = [pca.fit_transform(X)]
    df["x"] = coords[:, 0]
    df["y"] = coords[:, 1]

    return df, tfidf, kmeans

# ============================ PLOT ============================
def plot_clusters(df):
    fig, ax = plt.subplots(figsize=(10, 8))
    colors = cm.get_cmap("tab10", NUM_CLUSTERS)

    for cluster_id in sorted(df["cluster"].unique()):
        subset = df[df["cluster"] == cluster_id]
        ax.scatter(subset["x"], subset["y"], label=f"Cluster {cluster_id}", s=40, alpha=0.6, color=colors(cluster_id))
        for _, row in subset.iterrows():
            label = row["texto"][:MAX_LABEL_LENGTH].strip().replace("\n", " ")
            ax.annotate(label, (row["x"], row["y"]), fontsize=6, alpha=0.7)

    ax.set_title("Clusterização de SNPs com TF-IDF + KMeans", fontsize=14)
    ax.set_xlabel("Dimensão Semântica X (PCA)")
    ax.set_ylabel("Dimensão Semântica Y (PCA)")
    ax.legend()
    plt.tight_layout()
    plt.savefig(SAVE_FIG_PATH)
    plt.close()

# ============================ RELATÓRIO ============================
def gerar_relatorio_clusters(df):
    base_dir = Path("resultados/relatorios") / pd.Timestamp.now().strftime("%Y-%m-%d_%H-%M-%S")
    base_dir.mkdir(parents=True, exist_ok=True)

    for cluster_id in df["cluster"].unique():
        subset = df[df["cluster"] == cluster_id]
        all_words = [w for w in " ".join(subset["texto"]).split() if w.lower() not in CUSTOM_STOPWORDS]
        top_words = Counter(all_words).most_common(10)

        relatorio = [f"# Cluster {cluster_id}\n",
                     f"## Palavras mais comuns:\n"]
        relatorio += [f"- {w} ({c})" for w, c in top_words]
        relatorio.append("\n## Exemplos:")
        for _, row in subset.head(10).iterrows():
            relatorio.append(f"- {row['rsid']}: {row['texto'][:150]}...")

        caminho = base_dir / f"cluster_{cluster_id}.md"
        with open(caminho, "w", encoding="utf-8") as f:
            f.write("\n".join(relatorio))

def gerar_frases_relevantes(snp, alelos_relevantes):
    if not alelos_relevantes:
        return ""
    resumos = [ar["resumo"] for ar in alelos_relevantes]
    return f"{snp['rsid']}: " + " ".join(resumos)

# ============================ MAIN ============================
if __name__ == "__main__":
    df = carregar_snps(PASTA_MAPEADA)
    print(f"✅ {len(df)} SNPs carregados para clusterização.")

    df_clusterizado, tfidf, modelo = clusterizar(df)
    plot_clusters(df_clusterizado)

    if SAVE_CLUSTER_REPORT:
        gerar_relatorio_clusters(df_clusterizado)
        print("📄 Relatórios por cluster gerados.")

    print(f"📊 Clusterização concluída e salva em '{SAVE_FIG_PATH}'")
