library(tidyverse)
biobricks::initialize()
biobricks::brick_install("clinvar",pull=TRUE)
clinvar = biobricks::brick_load("clinvar")

pathcount = clinvar$variant_summary |> 
  inner_join(clinvar$var_citations, by="AlleleID") |> 
  filter(ClinicalSignificance == "Pathogenic") |> 
  group_by(GeneSymbol) |> summarize(count=n()) |> 
  arrange(desc(count)) |> head(10) |> collect()

ggplot(pathcount, aes(x=reorder(GeneSymbol,-count), y=count)) + 
  geom_bar(stat="identity", fill="steelblue") + theme_bw() + 
  theme(axis.text.x = element_text(angle = 90, hjust = 1))
