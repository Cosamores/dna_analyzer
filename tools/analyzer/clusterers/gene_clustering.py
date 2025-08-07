# this file reads the snp json files and generates a cluster report of gene positions of rsids, each cluster should be a gene and the position should define the rsid position inside each gene


import os
import json
from pathlib import Path
import pandas as pd 
from collections import defaultdict
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.feature_extraction.text import TfidfVectorizer
import matplotlib.pyplot as plt

# ============================ CONFIG ============================
PASTA_SNP_INPUT = Path("resultados/snps_com_alelos_relevantes_2025-08-06_16-36-25")
PASTA_RELATORIOS = Path("resultados/estatisticas_snp_reporter") / pd.Timestamp.now().strftime("%Y-%m-%d_%H-%M-%S")

PASTA_RELATORIOS.mkdir(parents=True, exist_ok=True)

NUM_CLUSTERS = int(os.getenv("NUM_CLUSTERS", 8))
MAX_LABEL_LENGTH = 50
SAVE_CLUSTER_REPORT = True
SAVE_FIG_PATH = f"cluster_visualization_{pd.Timestamp.now().strftime('%Y-%m-%d_%H-%M-%S')}.png"
CUSTOM_STOPWORDS = set([
    "common", "normal", "aka", "clinvar", "pmid",
    "in", "on", "with", "gene", "genes", "receptor",
    "associated", "variant", "rsid", "risk", "increased",
    "the", "a", "to", "of", "is", "and", "PMID", "SNP",
    "[PMID", "[PMID]",
])  
# ============================ LOAD SNPs ============================
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
    return df, kmeans, tfidf
def plot_clusters(df, kmeans, tfidf):
    plt.figure(figsize=(12, 8))
    plt.scatter(df["x"], df["y"], c=df["cluster"], cmap="viridis", alpha=0.6)
    centers = kmeans.cluster_centers_
    plt.scatter(centers[:, 0], centers[:, 1], c="red", marker="x", s=200, label="Centroids")
    plt.title("Clusterização de SNPs")
    plt.xlabel("Componente Principal 1")
    plt.ylabel("Componente Principal 2")
    plt.colorbar(label="Cluster")
    plt.legend()
    plt.tight_layout()
    if SAVE_CLUSTER_REPORT:
        plt.savefig(SAVE_FIG_PATH)
    plt.show()  
def gerar_relatorio(df, kmeans, tfidf):
    relatorio = []
    relatorio.append("# Relatório de Clusterização de SNPs")
    relatorio.append(f"Total de SNPs: {len(df)}")
    relatorio.append(f"Número de Clusters: {NUM_CLUSTERS}")
    relatorio.append("\n## Clusters Identificados")
    for cluster_id in sorted(df["cluster"].unique()):
        subset = df[df["cluster"] == cluster_id]
        relatorio.append(f"\n### Cluster {cluster_id} ({len(subset)} SNPs)")
        relatorio.append("#### Exemplos de SNPs:")
        for _, row in subset.iterrows():  
          label = row["texto"][:MAX_LABEL_LENGTH].strip().replace("\n", " ")
          relatorio.append(f"- {label} (RSID: {row['rsid']})")
    relatorio.append("\n## Estatísticas dos Clusters")
    relatorio.append(f"Centroides dos Clusters:")
    for i, center in enumerate(kmeans.cluster_centers_):
        relatorio.append(f"- Cluster {i}: {center}")
    relatorio.append("\n## Termos Mais Relevantes")
    feature_names = tfidf.get_feature_names_out()
    for i, center in enumerate(kmeans.cluster_centers_):
        top_indices = center.argsort()[-10:][::-1]
        top_terms = [feature_names[idx] for idx in top_indices]
        relatorio.append(f"- Cluster {i}: {', '.join(top_terms)}")
    return "\n".join(relatorio)
def gerar_relatorio_clusters(df, kmeans, tfidf):
    relatorio = gerar_relatorio(df, kmeans, tfidf)
    relatorio_path = PASTA_RELATORIOS / "relatorio_clusterizacao.md"
    with open(relatorio_path, "w", encoding="utf-8") as f:
        f.write(relatorio)
    print(f"Relatório salvo em: {relatorio_path.resolve()}")
def main():
    snps_df = carregar_snps(PASTA_SNP_INPUT)
    print(f"✅ {len(snps_df)} SNPs carregados para análise.") 
    if snps_df.empty:
        print("Nenhum SNP válido encontrado. Verifique os arquivos de entrada.")
        return
    snps_df, kmeans, tfidf = clusterizar(snps_df)
    plot_clusters(snps_df, kmeans, tfidf)
    gerar_relatorio_clusters(snps_df, kmeans, tfidf)
    print("✅ Clusterização concluída e relatório gerado.")
if __name__ == "__main__":
    main()