#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Author:
	Name: 			Antonia Chroni and Sharon Freshour
	Email: 			antonia.chroni@stjude.org
	Affiliation: 	St. Jude Children's Research Hospital, Memphis, TN
	Date: 			May 27, 2025 
"""

import os, argparse, pandas, glob
import pandas as pd

def dir_path(string):
	if os.path.isdir(string):
		return string
	else:
		raise NotADirectoryError(string)


# Interpreting Cell Ranger multi Web Summary Files for Fixed RNA Profiling
# chrome-extension://efaidnbmnnnibpcajpcglclefindmkaj/https://cdn.10xgenomics.com/image/upload/v1706742309/support-documents/CG000729_TechNote_WebSummary_Chromium_FixedRNAProfiling_RevA.pdf


#Beginning the argparse module to extract command-line arguments
parser = argparse.ArgumentParser(description="This is a script that will summarize cellranger count results from at least one cellranger output and create a summary within the 4_reports directory of the project. It accepts a data directory that contains at least one cellranger count results.")
#Creating the following optional arguments; some have default values
parser.add_argument('--dir', type=dir_path, help='Data directory path that contains individually named cellranger count results for samples', required=True)
parser.add_argument('--outdir', type=dir_path, help='Create all output files in the specified output directory. Please note that this directory must exist as the program will not create it.', required=True)
args = parser.parse_args() #Converts argument strings to objects and assigns them as attributes of the namespace; e.g. --id -> args.id


MasterDF = pandas.DataFrame()

print("args.dir:", args.dir)
pattern = os.path.join(args.dir, "multi_config_*", "multi_run_*", "outs", "per_sample_outs", "*", "metrics_summary_updated.csv")
print("Glob pattern:", pattern)
files = glob.glob(pattern)
print("Files found:", files)


#for filename in glob.glob(os.path.join(args.dir, "*","metrics_summary_updated.csv")):
for filename in glob.glob(os.path.join(args.dir, "multi_config_*", "multi_run_*", "outs", "per_sample_outs", "*", "metrics_summary_updated.csv")):
    print("Processing file:", filename)
    df = pd.read_csv(filename)
    df = df.replace(",", "", regex=True)
    df = df.replace("%", "", regex=True)
    df = df.astype('float', errors='ignore')
    
    SampleID = filename.split("/outs/per_sample_outs/")[1].split("/")[0]
    df["Sample ID"] = SampleID

    library_name = [part for part in filename.split("/") if part.startswith("multi_config_")]
    library_value = library_name[0].replace("multi_config_", "") if library_name else "unknown"
    df["library"] = library_value
    
    # .... QC Warnings calculation based on Cell Ranger documentation .... #
    Warnings = ""
    MajorWarnings = ""
    TotalWarnings = 0
    
    # For splitting into library and cell level metrics, will need to edit column names for condition checks
    # For readability, order warnings based on order in 10x documentation, i.e. Library metrics and then Cells metrics
    # If 10x documentation says cellranger raises a warning for a metric value, add them to MajorWarnings
    # Otherwise if values do not lead to warnings in the cellranger output, then add them to Warnings
    # That seems to be the pattern that was generally followed in the original summarize_cellranger_results.py script

    #################################
    ### LIBRARY-BASED QC METRICS ####

    # Assuming you already have a DataFrame 'df'
     # Clean the "Mean reads per cell" column by removing any non-numeric characters (e.g., commas)
    df["Library: Mean reads per cell"] = df["Library: Mean reads per cell"].replace({",": ""}, regex=True)  # Remove commas
    df["Library: Mean reads per cell"] = pd.to_numeric(df["Library: Mean reads per cell"], errors="coerce")  # This will convert strings to numbers, and non-convertible strings will be NaN
    
    if df.iloc[0]["Library: Mean reads per cell"] < 10000:
        Warnings = Warnings + "Library: Mean reads per cell < 10000, "
        TotalWarnings += 1


    df["Library: Fraction of initial cell barcodes passing high occupancy GEM filtering"] = df["Library: Fraction of initial cell barcodes passing high occupancy GEM filtering"].replace({",": ""}, regex=True)  # Remove commas
    df["Library: Fraction of initial cell barcodes passing high occupancy GEM filtering"] = pd.to_numeric(df["Library: Fraction of initial cell barcodes passing high occupancy GEM filtering"], errors="coerce")  # This will convert strings to numbers, and non-convertible strings will be NaN
   
    if df.iloc[0]["Library: Fraction of initial cell barcodes passing high occupancy GEM filtering"] < 90:
            MajorWarnings = MajorWarnings + "Library: Fraction of initial cell barcodes passing high occupancy GEM filtering < 90%, "
            TotalWarnings += 1


    df["Library: Number of short reads skipped"] = df["Library: Number of short reads skipped"].replace({",": ""}, regex=True)  # Remove commas
    df["Library: Number of short reads skipped"] = pd.to_numeric(df["Library: Number of short reads skipped"], errors="coerce")  # This will convert strings to numbers, and non-convertible strings will be NaN
   
    if df.iloc[0]["Library: Number of short reads skipped"] > 0:
        Warnings = Warnings + "Library: Number of short reads skipped > 0, "
        TotalWarnings += 1  


    df["Library: Q30 barcodes"] = df["Library: Q30 barcodes"].replace({",": ""}, regex=True)  # Remove commas
    df["Library: Q30 barcodes"] = pd.to_numeric(df["Library: Q30 barcodes"], errors="coerce")  # This will convert strings to numbers, and non-convertible strings will be NaN
     
    if df.iloc[0]["Library: Q30 barcodes"] < 55:
        MajorWarnings = MajorWarnings + "Library: Q30 barcodes < 55%, "
        TotalWarnings += 1


    df["Library: Q30 GEM barcodes"] = df["Library: Q30 GEM barcodes"].replace({",": ""}, regex=True)  # Remove commas
    df["Library: Q30 GEM barcodes"] = pd.to_numeric(df["Library: Q30 GEM barcodes"], errors="coerce")  # This will convert strings to numbers, and non-convertible strings will be NaN
    
    if df.iloc[0]["Library: Q30 GEM barcodes"] < 55:
        MajorWarnings = MajorWarnings + "Library: Q30 GEM barcodes < 55%, "
        TotalWarnings += 1
    

    df["Library: Q30 probe barcodes"] = df["Library: Q30 probe barcodes"].replace({",": ""}, regex=True)  # Remove commas
    df["Library: Q30 probe barcodes"] = pd.to_numeric(df["Library: Q30 probe barcodes"], errors="coerce")  # This will convert strings to numbers, and non-convertible strings will be NaN
   
    if df.iloc[0]["Library: Q30 probe barcodes"] < 80:
        Warnings = Warnings + "Library: Q30 probe barcodes < 80%, "
        TotalWarnings += 1

    
    df["Library: Q30 UMI"] = df["Library: Q30 UMI"].replace({",": ""}, regex=True)  # Remove commas
    df["Library: Q30 UMI"] = pd.to_numeric(df["Library: Q30 UMI"], errors="coerce")  # This will convert strings to numbers, and non-convertible strings will be NaN
    
    if df.iloc[0]["Library: Q30 UMI"] < 75:
        Warnings = Warnings + "Library: Q30 UMI < 75%, "
        TotalWarnings += 1


    df["Library: Q30 RNA read"] = df["Library: Q30 RNA read"].replace({",": ""}, regex=True)  # Remove commas
    df["Library: Q30 RNA read"] = pd.to_numeric(df["Library: Q30 RNA read"], errors="coerce")  # This will convert strings to numbers, and non-convertible strings will be NaN
    
    if df.iloc[0]["Library: Q30 RNA read"] < 65:
        MajorWarnings = MajorWarnings + "Library: Q30 RNA read < 65%, "
        TotalWarnings += 1


    df["Library: Reads half-mapped to probe set"] = df["Library: Reads half-mapped to probe set"].replace({",": ""}, regex=True)  # Remove commas
    df["Library: Reads half-mapped to probe set"] = pd.to_numeric(df["Library: Reads half-mapped to probe set"], errors="coerce")  # This will convert strings to numbers, and non-convertible strings will be NaN
    
    if df.iloc[0]["Library: Reads half-mapped to probe set"] > 20:
            MajorWarnings = MajorWarnings + "Library: Reads half-mapped to probe set > 20%, "
            TotalWarnings += 1


    df["Library: Reads split-mapped to probe set"] = df["Library: Reads split-mapped to probe set"].replace({",": ""}, regex=True)  # Remove commas
    df["Library: Reads split-mapped to probe set"] = pd.to_numeric(df["Library: Reads split-mapped to probe set"], errors="coerce")  # This will convert strings to numbers, and non-convertible strings will be NaN
    
    if df.iloc[0]["Library: Reads split-mapped to probe set"] > 20:
            MajorWarnings = MajorWarnings + "Library: Reads split-mapped to probe set > 20%, "
            TotalWarnings += 1


    df["Library: Reads mapped to probe set"] = df["Library: Reads mapped to probe set"].replace({",": ""}, regex=True)  # Remove commas
    df["Library: Reads mapped to probe set"] = pd.to_numeric(df["Library: Reads mapped to probe set"], errors="coerce")  # This will convert strings to numbers, and non-convertible strings will be NaN

    if df.iloc[0]["Library: Reads mapped to probe set"] < 50:
            MajorWarnings = MajorWarnings + "Library: Reads mapped to probe set < 50%, "
            TotalWarnings += 1


    df["Library: Reads confidently mapped to probe set"] = df["Library: Reads confidently mapped to probe set"].replace({",": ""}, regex=True)  # Remove commas
    df["Library: Reads confidently mapped to probe set"] = pd.to_numeric(df["Library: Reads confidently mapped to probe set"], errors="coerce")  # This will convert strings to numbers, and non-convertible strings will be NaN
    
    if df.iloc[0]["Library: Reads confidently mapped to probe set"] < 50:
            Warnings = Warnings + "Library: Reads confidently mapped to probe set < 50%, "
            TotalWarnings += 1
            
         
    df["Library: Reads confidently mapped to filtered probe set"] = df["Library: Reads confidently mapped to filtered probe set"].replace({",": ""}, regex=True)  # Remove commas
    df["Library: Reads confidently mapped to filtered probe set"] = pd.to_numeric(df["Library: Reads confidently mapped to filtered probe set"], errors="coerce")  # This will convert strings to numbers, and non-convertible strings will be NaN
     
    if df.iloc[0]["Library: Reads confidently mapped to filtered probe set"] < 50:
            Warnings = Warnings + "Library: Reads confidently mapped to filtered probe set < 50%, "
            TotalWarnings += 1


    df["Library: Valid barcodes"] = df["Library: Valid barcodes"].replace({",": ""}, regex=True)  # Remove commas
    df["Library: Valid barcodes"] = pd.to_numeric(df["Library: Valid barcodes"], errors="coerce")  # This will convert strings to numbers, and non-convertible strings will be NaN
   
    if df.iloc[0]["Library: Valid barcodes"] < 75:
        MajorWarnings = MajorWarnings + "Library: Valid barcodes < 75%, "
        TotalWarnings += 1
   

    df["Library: Valid GEM barcodes"] = df["Library: Valid GEM barcodes"].replace({",": ""}, regex=True)  # Remove commas
    df["Library: Valid GEM barcodes"] = pd.to_numeric(df["Library: Valid GEM barcodes"], errors="coerce")  # This will convert strings to numbers, and non-convertible strings will be NaN

    if df.iloc[0]["Library: Valid GEM barcodes"] < 75:
        MajorWarnings = MajorWarnings + "Library: Valid GEM barcodes < 75%, "
        TotalWarnings += 1    
    

    df["Library: Valid probe barcodes"] = df["Library: Valid probe barcodes"].replace({",": ""}, regex=True)  # Remove commas
    df["Library: Valid probe barcodes"] = pd.to_numeric(df["Library: Valid probe barcodes"], errors="coerce")  # This will convert strings to numbers, and non-convertible strings will be NaN

    if df.iloc[0]["Library: Valid probe barcodes"] < 75:
        MajorWarnings = MajorWarnings + "Library: Valid probe barcodes < 75%, "
        TotalWarnings += 1   
    

    df["Library: Valid UMIs"] = df["Library: Valid UMIs"].replace({",": ""}, regex=True)  # Remove commas
    df["Library: Valid UMIs"] = pd.to_numeric(df["Library: Valid UMIs"], errors="coerce")  # This will convert strings to numbers, and non-convertible strings will be NaN

    if df.iloc[0]["Library: Valid UMIs"] < 75:
        MajorWarnings = MajorWarnings + "Library: Valid UMIs < 75%, "
        TotalWarnings += 1


    df["Library: Confidently mapped reads in cells"] = df["Library: Confidently mapped reads in cells"].replace({",": ""}, regex=True)  # Remove commas
    df["Library: Confidently mapped reads in cells"] = pd.to_numeric(df["Library: Confidently mapped reads in cells"], errors="coerce")  # This will convert strings to numbers, and non-convertible strings will be NaN

    if df.iloc[0]["Library: Confidently mapped reads in cells"] < 70:
        Warnings = Warnings + "Library: Confidently mapped reads in cells < 70%, "
        TotalWarnings += 1

    #################################    
    
    #################################        
    ### CELLS-BASED QC METRICS ###

    # Assuming you already have a DataFrame 'df'
    # Clean the "Cells" column by removing any non-numeric characters (e.g., commas)
    df["Cells: Cells"] = df["Cells: Cells"].replace({",": ""}, regex=True)  # Remove commas
    
    # Convert the "Cells: Cells" column to a numeric type (int or float)
    df["Cells: Cells"] = pd.to_numeric(df["Cells: Cells"], errors="coerce")  # This will convert strings to numbers, and non-convertible strings will be NaN

    if df.iloc[0]["Cells: Cells"] < 500:
        Warnings = Warnings + "Cells: Cells < 500, "
        TotalWarnings += 1
  
    if df.iloc[0]["Cells: Cells"] < 100:
        MajorWarnings = MajorWarnings + "Cells: Cells < 100, "
        TotalWarnings += 1


    df["Cells: Confidently mapped reads in cells"] = df["Cells: Confidently mapped reads in cells"].replace({",": ""}, regex=True)  # Remove commas
    df["Cells: Confidently mapped reads in cells"] = pd.to_numeric(df["Cells: Confidently mapped reads in cells"], errors="coerce")  # This will convert strings to numbers, and non-convertible strings will be NaN

    if df.iloc[0]["Cells: Confidently mapped reads in cells"] < 70:
        Warnings = Warnings + "Cells: Confidently mapped reads in cells < 70%, "
        TotalWarnings += 1


    df["Cells: Reads half-mapped to probe set"] = df["Cells: Reads half-mapped to probe set"].replace({",": ""}, regex=True)  # Remove commas
    df["Cells: Reads half-mapped to probe set"] = pd.to_numeric(df["Cells: Reads half-mapped to probe set"], errors="coerce")  # This will convert strings to numbers, and non-convertible strings will be NaN
      
    if df.iloc[0]["Cells: Reads half-mapped to probe set"] > 20:
            MajorWarnings = MajorWarnings + "Cells: Reads half-mapped to probe set > 20%, "
            TotalWarnings += 1


    df["Cells: Reads split-mapped to probe set"] = df["Cells: Reads split-mapped to probe set"].replace({",": ""}, regex=True)  # Remove commas
    df["Cells: Reads split-mapped to probe set"] = pd.to_numeric(df["Cells: Reads split-mapped to probe set"], errors="coerce")  # This will convert strings to numbers, and non-convertible strings will be NaN
     
    if df.iloc[0]["Cells: Reads split-mapped to probe set"] > 20:
            MajorWarnings = MajorWarnings + "Cells: Reads split-mapped to probe set > 20%, "
            TotalWarnings += 1


    df["Cells: Reads mapped to probe set"] = df["Cells: Reads mapped to probe set"].replace({",": ""}, regex=True)  # Remove commas
    df["Cells: Reads mapped to probe set"] = pd.to_numeric(df["Cells: Reads mapped to probe set"], errors="coerce")  # This will convert strings to numbers, and non-convertible strings will be NaN

    if df.iloc[0]["Cells: Reads mapped to probe set"] < 50:
            MajorWarnings = MajorWarnings + "Cells: Reads mapped to probe set < 50%, "
            TotalWarnings += 1


    df["Cells: Reads confidently mapped to probe set"] = df["Cells: Reads confidently mapped to probe set"].replace({",": ""}, regex=True)  # Remove commas
    df["Cells: Reads confidently mapped to probe set"] = pd.to_numeric(df["Cells: Reads confidently mapped to probe set"], errors="coerce")  # This will convert strings to numbers, and non-convertible strings will be NaN
      
    if df.iloc[0]["Cells: Reads confidently mapped to probe set"] < 50:
            Warnings = Warnings + "Cells: Reads confidently mapped to probe set < 50%, "
            TotalWarnings += 1
            
         
    df["Cells: Reads confidently mapped to filtered probe set"] = df["Cells: Reads confidently mapped to filtered probe set"].replace({",": ""}, regex=True)  # Remove commas
    df["Cells: Reads confidently mapped to filtered probe set"] = pd.to_numeric(df["Cells: Reads confidently mapped to filtered probe set"], errors="coerce")  # This will convert strings to numbers, and non-convertible strings will be NaN
    
    if df.iloc[0]["Cells: Reads confidently mapped to filtered probe set"] < 50:
            Warnings = Warnings + "Cells: Reads confidently mapped to filtered probe set < 50%, "
            TotalWarnings += 1


    # Note whether to use the Library metric value or Cells metric value for this metric depends of whether the data is singlepelx or multiplex
    # For multiplex data the Cells value should be used
    # For singleplex data the Library value should be used
    # Since the pipeline currently appears to being use for multiplex data, will check the Cells value for this metric
    # Possibly keep this in mind for future use of the pipeline though

    df["Cells: Estimated UMIs from genomic DNA"] = df["Cells: Estimated UMIs from genomic DNA"].replace({",": ""}, regex=True)  # Remove commas
    df["Cells: Estimated UMIs from genomic DNA"] = pd.to_numeric(df["Cells: Estimated UMIs from genomic DNA"], errors="coerce")  # This will convert strings to numbers, and non-convertible strings will be NaN

    if df.iloc[0]["Cells: Estimated UMIs from genomic DNA"] > 1:
        Warnings = Warnings + "Cells: Estimated UMIs from genomic DNA > 1%, "
        TotalWarnings += 1  
    #################################

    # .... QC assignments .... #
    df["Warnings"] = Warnings
    df["MajorWarnings"] = MajorWarnings
    df["Total Warnings"] = TotalWarnings
        
    MasterDF = pd.concat([MasterDF, df], ignore_index=True)

outpath = os.path.join(args.outdir, "QC_Summary_CellRanger_Report.tsv")
MasterDF.to_csv(outpath, sep="\t", index=False)
