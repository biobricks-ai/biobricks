# In a shell run 
# > pip install biobricks
# > biobricks configure
import biobricks as bb, seaborn as sns, matplotlib.pyplot as plt

# Install and load clinvar
cv = bb.install("clinvar").load() 

# load `variant_summary` and `var_citations` into pandas
variants = cv.variant_summary.to_pandas()
citation = cv.var_citations.to_pandas()
joined = variants.merge(citation, on="AlleleID")

# filter to only the pathogenic variants
pathogenic = joined[joined.ClinicalSignificance == "Pathogenic"]

# Find the top 10 genes by number of publications
counts = pathogenic.groupby(["GeneSymbol"]).size().reset_index(name="count")
counts = counts.sort_values(by="count", ascending=False)[0:10]

# build a barplot and output it to plot.jpeg
ax = sns.barplot(x='GeneSymbol', y='count', data=counts, color='steelblue')
plt.savefig('pathgenes.png',dpi=300, bbox_inches='tight')


