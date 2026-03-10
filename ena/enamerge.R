library(tidyverse)

runs = read_csv("https://docs.google.com/spreadsheets/d/18_DMvXai2vpbrV1WM9IFXpL-Ule1ZBCkYnOD_Am1J_0/export?gid=736894110&format=csv")

allfq = read_csv("https://docs.google.com/spreadsheets/d/18_DMvXai2vpbrV1WM9IFXpL-Ule1ZBCkYnOD_Am1J_0/export?gid=1417504575&format=csv") |>
    glimpse()


ena = read_tsv("sample_accessions.tsv") |>
    filter(TYPE=="SAMPLE") |>
    glimpse()


ena2 = ena |>
    left_join(allfq, by=join_by(ALIAS==sample)) |>
    glimpse()  |>
    write_tsv("all_fq.tsv", na="")



ena2 |>
    filter(is.na(exclude_why)) |>
    transmute(
        sample=ACCESSION, 
        study="PRJEB109258",
        instrument_model="Illumina NovaSeq X Plus",
        library_name=sprintf("%s__%s__%s", library, library_type, run),
        library_source=case_when(
            library_type == "RNAseq" ~ "TRANSCRIPTOMIC",
            T ~ "GENOMIC"
        ),
        library_selection=case_when(
            library_type == "RNAseq" ~ "cDNA",
            T ~ "RANDOM"
        ),
        library_strategy=case_when(
            library_type == "RNAseq" ~ "RNA-Seq",
            T ~ "WGS"
        ),
        library_layout="PAIRED",
        forward_file_name=read1_uri,
        reverse_file_name=read2_uri,
    ) |>
    glimpse()


