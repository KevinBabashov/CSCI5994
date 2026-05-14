import json

def create_nb(name, cells):
    nb = {"cells": cells, "metadata": {"kernelspec": {"display_name": "Python 3", "name": "python3"}}, "nbformat": 4, "nbformat_minor": 5}
    with open(name, 'w') as f:
        json.dump(nb, f, indent=2)
    print(f"File Created: {name}")

# --- Pipeline Notebook ---
p_cells = [
    {"cell_type": "markdown", "source": ["# MINNELOVE: Long-Read 16S Pipeline\n", "Steps: Trimming -> Filtering -> Emu Classification"]},
    {"cell_type": "code", "outputs": [], "source": [
        "import os\n",
        "SAMPLE = 'MINNELOVE_01'\n",
        "DB_PATH = '/path/to/emu_database'\n",
        "os.makedirs(f'results/{SAMPLE}', exist_ok=True)"
    ]},
    {"cell_type": "code", "outputs": [], "source": [
        "# Change 'ont' to 'pacbio' if needed\n",
        "platform = 'ont'\n",
        "if platform == 'ont':\n",
        "    !porechop_abi -i raw.fastq.gz | cutadapt -g AGAGTTTGATCMTGGCTCAG -a GGTTACCTTGTTACGACTT - | chopper -l 1200 --maxlength 1800 | gzip > clean.fastq.gz\n",
        "    !emu abundance clean.fastq.gz --db {DB_PATH} --type map-ont --output-dir results/{SAMPLE}\n",
        "else:\n",
        "    !lima input.subreads.bam barcodes.fasta demux.bam\n",
        "    !samtools fastq demux.bam | cutadapt -g AGAGTTTGATCMTGGCTCAG - | gzip > clean.fastq.gz\n",
        "    !emu abundance clean.fastq.gz --db {DB_PATH} --type map-pb --output-dir results/{SAMPLE}"
    ]}
]

# --- Analysis Notebook ---
a_cells = [
    {"cell_type": "markdown", "source": ["# MINNELOVE: Results Analysis\n", "Visualizing taxonomic abundance."]},
    {"cell_type": "code", "outputs": [], "source": [
        "import pandas as pd\n",
        "import seaborn as sns\n",
        "import matplotlib.pyplot as plt\n",
        "\n",
        "# Use 'emu combine-outputs' in your terminal first to get this TSV\n",
        "try:\n",
        "    df = pd.read_csv('emu_combined_genus.tsv', sep='\\t').set_index('genus')\n",
        "except:\n",
        "    # Placeholder data for your presentation demo\n",
        "    data = {'Genus': ['Bacteroides', 'Lactobacillus', 'Prevotella'], 'S1': [0.4, 0.3, 0.3], 'S2': [0.35, 0.45, 0.2]}\n",
        "    df = pd.DataFrame(data).set_index('Genus')\n",
        "\n",
        "df.T.plot(kind='bar', stacked=True, colormap='Spectral', figsize=(10,6))\n",
        "plt.title('MINNELOVE Genus Composition')\n",
        "plt.ylabel('Relative Abundance')\n",
        "plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')\n",
        "plt.show()"
    ]}
]

create_nb("MINNELOVE_Emu_Pipeline.ipynb", p_cells)
create_nb("MINNELOVE_Analysis.ipynb", a_cells)
