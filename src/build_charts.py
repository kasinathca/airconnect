"""Generate publication-quality charts from the canonical analysis artifact."""
from pathlib import Path
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "charts"
OUT.mkdir(parents=True, exist_ok=True)
D = json.loads((ROOT / "data" / "processed" / "analysis.json").read_text(encoding="utf-8"))
NAVY, BLUE, TEAL, PALE, GOLD = "#173b58", "#17679a", "#557f84", "#a8b8c6", "#9b7b45"
plt.rcParams.update({"font.family": "DejaVu Serif", "font.size": 9, "axes.titlesize": 12,
                     "axes.labelsize": 9, "axes.spines.top": False, "axes.spines.right": False,
                     "figure.facecolor": "white", "axes.facecolor": "white"})


def save(fig, name):
    fig.tight_layout()
    fig.savefig(OUT / name, dpi=220, bbox_inches="tight", facecolor="white")
    plt.close(fig)


hist = D["historical"]
fig, ax = plt.subplots(figsize=(9.4, 3.5))
ax.plot([r["year"] for r in hist], [r["domestic"] / 1e6 for r in hist], marker="o", lw=2.2, color=BLUE, label="Domestic")
ax.plot([r["year"] for r in hist], [r["international"] / 1e6 for r in hist], marker="o", lw=2, color=TEAL, label="International")
ax.set(title="Indian airport passenger movements, 2016–2025", ylabel="Passenger movements (millions)", xlabel="Calendar year")
ax.grid(axis="y", alpha=.18); ax.legend(frameon=False, ncol=2); save(fig, "annual_traffic.png")

R = D["regression"]; tests = R["test"]; preds = R["predictions"]
fig, ax = plt.subplots(figsize=(9.4, 4.2)); y = np.arange(len(tests)); vals = [r["mae"] for r in tests]
ax.barh(y, vals, color=[BLUE if r["type"] == "trained" else PALE for r in tests]); ax.set_yticks(y, [r["model"] for r in tests]); ax.invert_yaxis()
ax.set(title="Held-out 2025 regression MAE", xlabel="Mean absolute error (passenger movements)"); ax.grid(axis="x", alpha=.16)
for i, v in enumerate(vals): ax.text(v, i, f" {v:,.0f}", va="center", fontsize=8)
save(fig, "regression_model_comparison.png")

actual = np.array([r["actual"] for r in preds]); predicted = np.array([r["selected_prediction"] for r in preds]); residual = actual - predicted
fig, ax = plt.subplots(figsize=(6.3, 5.2)); ax.scatter(actual, predicted, s=12, alpha=.45, color=BLUE); limit=max(actual.max(), predicted.max()); ax.plot([0,limit],[0,limit],ls="--",color="#7b8792")
ax.set_xscale("symlog", linthresh=1000); ax.set_yscale("symlog", linthresh=1000); ax.set(title=f"Actual versus predicted: {R['selected_model']}", xlabel="Actual passenger movements (symlog)", ylabel="Predicted passenger movements (symlog)"); save(fig, "regression_actual_predicted.png")

fig, ax = plt.subplots(figsize=(7.5, 4.3)); ax.scatter(predicted, residual, s=12, alpha=.45, color=BLUE); ax.axhline(0,color="#7b8792",ls="--"); ax.set_xscale("symlog",linthresh=1000); ax.set_yscale("symlog",linthresh=1000)
ax.set(title="Regression residuals versus predicted values", xlabel="Predicted passenger movements (symlog)", ylabel="Residual actual − predicted (symlog)"); save(fig, "regression_residuals.png")

fig, ax = plt.subplots(figsize=(7.5, 4.1)); ax.hist(residual, bins=35, color=BLUE, alpha=.82); ax.axvline(0,color="#263947",ls="--"); ax.set(title="Distribution of held-out regression residuals", xlabel="Residual (passenger movements)", ylabel="Airport-month observations"); save(fig, "regression_residual_histogram.png")

importance=R["feature_importance"][:10]; fig, ax=plt.subplots(figsize=(8.0,4.5)); y=np.arange(len(importance)); ax.barh(y,[max(0,r["mae_increase"]) for r in importance],color=TEAL); ax.set_yticks(y,[r["feature"].replace('_',' ') for r in importance]); ax.invert_yaxis(); ax.set(title="Permutation importance for the selected regressor",xlabel="Increase in 2025 MAE after permutation"); save(fig,"regression_feature_importance.png")

segments=[r for r in R["segments"] if r["method"]==R["selected_model"]]; base=[r for r in R["segments"] if r["method"]==R["best_baseline"]]; x=np.arange(3); fig,ax=plt.subplots(figsize=(7.7,4.1)); ax.bar(x-.18,[r["mae"] for r in segments],.36,label=R["selected_model"],color=BLUE); ax.bar(x+.18,[r["mae"] for r in base],.36,label=R["best_baseline"],color=PALE); ax.set_xticks(x,[r["segment"] for r in segments]); ax.set(title="Regression error by prior-year traffic segment",xlabel="Traffic segment from training-period lag-12 quantiles",ylabel="MAE (passenger movements)"); ax.legend(frameon=False); save(fig,"regression_segment_errors.png")

C=D["classification"]; selected=next(r for r in C["test"] if r["model"]==C["selected_model"]); cm=np.array([[selected["tn"],selected["fp"]],[selected["fn"],selected["tp"]]])
fig,ax=plt.subplots(figsize=(5.5,4.5)); image=ax.imshow(cm,cmap="Blues"); ax.set_xticks([0,1],["Predicted 0","Predicted 1"]); ax.set_yticks([0,1],["Actual 0","Actual 1"]); ax.set(title=f"Confusion matrix: {C['selected_model']}")
for i in range(2):
    for j in range(2): ax.text(j,i,f"{cm[i,j]:,}",ha="center",va="center",fontsize=15,color="white" if cm[i,j]>cm.max()/2 else NAVY)
fig.colorbar(image,ax=ax,fraction=.045); save(fig,"classification_confusion_matrix.png")

roc=C["roc_curve"]; fig,ax=plt.subplots(figsize=(5.8,4.7)); ax.plot([r["fpr"] for r in roc],[r["tpr"] for r in roc],color=BLUE,lw=2.4,label=f"AUC = {selected['roc_auc']:.3f}"); ax.plot([0,1],[0,1],ls="--",color="#88949d"); ax.set(title="ROC curve on untouched 2025 test data",xlabel="False positive rate",ylabel="True positive rate"); ax.legend(frameon=False); ax.grid(alpha=.15); save(fig,"classification_roc.png")

pr=C["precision_recall_curve"]; fig,ax=plt.subplots(figsize=(5.8,4.7)); ax.plot([r["recall"] for r in pr],[r["precision"] for r in pr],color=TEAL,lw=2.4,label=f"Average precision = {selected['average_precision']:.3f}"); ax.set(title="Precision–recall curve on 2025 test data",xlabel="Recall",ylabel="Precision"); ax.legend(frameon=False); ax.grid(alpha=.15); save(fig,"classification_precision_recall.png")

class_rows=C["test"][:-1]; metrics=["balanced_accuracy","precision","recall","f1"]; x=np.arange(len(class_rows)); fig,ax=plt.subplots(figsize=(9.2,4.4)); width=.19
for i,m in enumerate(metrics): ax.bar(x+(i-1.5)*width,[r[m] for r in class_rows],width,label=m.replace('_',' ').title(),color=[BLUE,TEAL,PALE,GOLD][i])
ax.set_xticks(x,[r["model"].replace(" Classifier","") for r in class_rows]); ax.set_ylim(0,1); ax.set(title="Classification metrics on 2025 test data",ylabel="Score"); ax.legend(frameon=False,ncol=4,fontsize=8); save(fig,"classification_model_comparison.png")

K=D["clustering"]; ev=K["evaluations"]; ks=[r["k"] for r in ev]; fig,ax1=plt.subplots(figsize=(7.5,4.3)); ax1.plot(ks,[r["inertia"] for r in ev],marker="o",color=TEAL,label="Inertia"); ax1.set(xlabel="Number of clusters k",ylabel="Inertia",title="K-Means selection evidence"); ax2=ax1.twinx(); ax2.plot(ks,[r["silhouette"] for r in ev],marker="s",color=BLUE,label="Silhouette"); ax2.set_ylabel("Silhouette Score"); ax1.grid(alpha=.15); fig.legend(frameon=False,loc="upper right",bbox_to_anchor=(.89,.87)); save(fig,"clustering_selection.png")

clusters=K["clusters"]; fig,ax=plt.subplots(figsize=(7.8,4.1)); ax.bar([c["name"] for c in clusters],[c["count"] for c in clusters],color=[PALE,"#729ab8",BLUE,NAVY]); ax.set(title="Selected K-Means cluster sizes, 2025",ylabel="Airports"); ax.tick_params(axis="x",rotation=12); save(fig,"cluster_groups.png")

points=K["pca"]["points"]; fig,ax=plt.subplots(figsize=(7.0,5.0));
for c in clusters:
    group=[p for p in points if p["cluster"]==c["id"]]; ax.scatter([p["pc1"] for p in group],[p["pc2"] for p in group],s=28,alpha=.72,label=c["name"])
ax.axhline(0,color="#c2c9ce",lw=.7); ax.axvline(0,color="#c2c9ce",lw=.7); ax.set(title="PCA projection of scaled airport features",xlabel="Principal component 1",ylabel="Principal component 2"); ax.legend(frameon=False,fontsize=8); save(fig,"pca_clusters.png")

variance=K["pca"]["explained_variance_ratio"]; fig,ax=plt.subplots(figsize=(6.0,3.8)); ax.bar(["PC1","PC2"],variance,color=[BLUE,TEAL]); ax.plot([0,1],np.cumsum(variance),marker="o",color=GOLD,label="Cumulative"); ax.set_ylim(0,1); ax.set(title="PCA explained variance",ylabel="Share of standardised variance"); ax.legend(frameon=False); save(fig,"pca_explained_variance.png")

print(f"Generated {len(list(OUT.glob('*.png')))} charts in {OUT}")
