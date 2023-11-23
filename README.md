Welcome to the Protein Sequence Analysis Tool! This guide will help you understand how to use the tool for analysing protein sequences within specific taxonomic groups.
1.1  Introduction
The Protein Sequence Analysis Tool is an interactive user-input-driven program designed to display results promptly on your screen. It facilitates the analysis of protein sequences, allowing users to download desired protein sequences and perform step-by-step analyses by inputting their options. The program saves all sequence files and analysis results in a user-named directory and its corresponding subdirectories, ensuring organized storage and easy access to the generated data. This tool prioritizes user convenience by offering a structured approach to obtain and analyze protein sequence data within specific taxonomic groups.
1.2 System Requirements and Compatibility
• Operating System: This program is designed to run specifically on Linux environments.
• Dependencies and Tools: The functionality of this program relies on several external tools and resources, including:
o	EMBOSS: Suite of bioinformatics software
o	NCBI Data Retrieval Tools: Utilizes esearch and efetch for data retrieval
o	Biological Sequence Analysis Tools: Implements BLAST, ClustalO, and pullseq
o	Internet Access: Required to download necessary data from the web
Ensure that the necessary dependencies, such as EMBOSS and the NCBI data retrieval tools (esearch, efetch and xtract), are installed and accessible in your Linux environment to enable seamless execution of the program. Internet connectivity is vital for retrieving relevant data during the analysis process.
•  Running the Program: Execute the program using Python3:
python3 ica2_test.py
