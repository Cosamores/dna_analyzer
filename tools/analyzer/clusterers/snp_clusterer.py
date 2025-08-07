# snp_clusterer.py
import os
import json
import pandas as pd
import numpy as np
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.cluster import KMeans, DBSCAN
from sklearn.decomposition import PCA
import umap
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import TfidfVectorizer
from sentence_transformers import SentenceTransformer
from pathlib import Path


# === CONFIG ===
INPUT_DIR = "../resultados/snps_mapeados/2025-08-06_18-19-10"
OUTPUT_DIR = f"../resultados/clusters/cluster_{pd.Timestamp.now().strftime('%Y-%m-%d_%H-%M-%S')}"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"


# === UTILITIES ===
def load_snps(input_dir):
    data = []
    for file in Path(input_dir).glob("*.json"):
        with open(file, encoding="utf-8") as f:
            snp = json.load(f)
            data.append(snp)
    return pd.DataFrame(data)


def save_cluster_labels(df, cluster_labels, output_file):
    df["cluster"] = cluster_labels
    df.to_csv(output_file, index=False)


def plot_clusters(X, labels, title, outpath):
    plt.figure(figsize=(10, 6))
    plt.scatter(X[:, 0], X[:, 1], c=labels, cmap="tab10", s=20)
    plt.title(title)
    plt.xlabel("Component 1")
    plt.ylabel("Component 2")
    plt.colorbar(label="Cluster")
    plt.tight_layout()
    plt.savefig(outpath)
    plt.close()


# === 1. FUNCTIONAL CLUSTERING ===
def functional_clustering(df):
    fields = ["effect", "variant_consequence", "vartype", "region", "putative_impact"]
    df_func = df[fields].fillna("NA")
    encoder = OneHotEncoder(sparse_output=False)
    encoded = encoder.fit_transform(df_func)

    reducer = PCA(n_components=2)
    X_reduced = reducer.fit_transform(encoded)

    kmeans = KMeans(n_clusters=6, random_state=42).fit(X_reduced)
    plot_clusters(
        X_reduced,
        kmeans.labels_,
        "Functional Clustering",
        f"{OUTPUT_DIR}/functional_clusters.png",
    )
    save_cluster_labels(df, kmeans.labels_, f"{OUTPUT_DIR}/functional_clusters.csv")


# === 2. CHROMOSOME + POSITION CLUSTERING ===
def chrom_pos_clustering(df):
    df_pos = df[["chromosome", "position"]].dropna()
    df_pos["chromosome"] = pd.to_numeric(df_pos["chromosome"], errors="coerce")
    df_pos["position"] = pd.to_numeric(df_pos["position"], errors="coerce")
    df_pos.dropna(inplace=True)
    X = StandardScaler().fit_transform(df_pos)

    reducer = PCA(n_components=2)
    X_reduced = reducer.fit_transform(X)

    km = KMeans(n_clusters=10, random_state=0).fit(X_reduced)
    plot_clusters(
        X_reduced,
        km.labels_,
        "Chromosomal Position Clustering",
        f"{OUTPUT_DIR}/chrom_position_clusters.png",
    )
    save_cluster_labels(
        df.loc[df_pos.index], km.labels_, f"{OUTPUT_DIR}/chrom_position_clusters.csv"
    )


# === 3. NLP CLUSTERING (Resumos e Traits) ===
def nlp_semantic_clustering(df):
    texts = (df["resumo"].fillna("") + ". " + df["trait"].fillna(""))
    texts = texts.apply(lambda x: x.strip())

    model = SentenceTransformer(EMBEDDING_MODEL)
    embeddings = model.encode(texts.tolist(), show_progress_bar=True)
    embeddings = np.array(embeddings)  # garante matriz NumPy

    reducer = umap.UMAP(n_neighbors=15, min_dist=0.1, metric='cosine')
    X_umap = np.asarray(reducer.fit_transform(embeddings))
    print("UMAP result:", type(X_umap), getattr(X_umap, 'shape', None))  # debug
    clustering = DBSCAN(eps=0.5, min_samples=5).fit(X_umap)
    plot_clusters(X_umap, clustering.labels_, "NLP Semantic Clustering", f"{OUTPUT_DIR}/semantic_nlp_clusters.png")
    save_cluster_labels(df, clustering.labels_, f"{OUTPUT_DIR}/semantic_nlp_clusters.csv")



# === MAIN ===
def run_all_clusterings():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print("[+] Loading SNPs...")
    df = load_snps(INPUT_DIR)
    print("[+] Running functional clustering...")
    functional_clustering(df.copy())
    print("[+] Running chromosomal position clustering...")
    chrom_pos_clustering(df.copy())
    print("[+] Running NLP-based semantic clustering...")
    nlp_semantic_clustering(df.copy())
    print("[✓] All clustering complete.")


if __name__ == "__main__":
    run_all_clusterings()
