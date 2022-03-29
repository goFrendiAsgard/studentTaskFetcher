# What is this

Clone/pull students repositories


# How to Use

## Prepare configuration file

Create configuration file or use the default one (`./config.json`).

The configuration file should be written in JSON:

```
{
    "csv_file_name": "data.csv",
    "result_dir_name": "data",
    "new_line": "",
    "delimiter": ",",
    "quote_char": "'"
}
```

Please take note, that the `csv_file_name` is `data.csv`. You should provide this file before running the script.

## Create csv file

Create a csv file containing student's name and their github repositories. The file name should match the one you define in the configuration (by default, it is `data.csv`):

```bash
RESTU ADITYA RACHMAN,https://github.com/restuarachman/go_restu-aditya-rachman.git
RIZQY EKA PUTRA RIZALDY,https://github.com/rizqyep/go_rizqyekaputra.git
SEPTO HADY TRYANA,https://github.com/Septotryana/Praktikum_1_GIT.git
TIRZA YOLANDA HEVIN,https://github.com/yolandahevin/go_tirza-yolanda-hevin.git
DAUD HERLANGGA ANDRIANATA,https://github.com/wussh/go_daud-herlangga-andrianata.git
JESICA HARTATI AGUSTINA PARDEDE,https://github.com/jesicapardd/jesicapardd.git
ABEL MELIDO BANGUN,https://github.com/AbelBangun/go_abel-melido-bangun.git
ADHICITTA MASRAN,https://github.com/dhichii/go_adhicitta-masran.git
AZZAHRA FEBRINA AULIA PUTRI,https://github.com/Azzahrafebrina/go_azzahra-febrina-aulia-putri.git
Doni Yudi Prabowo,https://github.com/Doni19071/go_doni-yudi-prabowo.git
DZAKY MOHAMMAD,https://github.com/Dzaakk/go_dzaky-mohammad.git
EFRAIM REFIVAL RUNTUWENE,https://github.com/Efraimrevival/go_efraim_refival_runtuwene.git
EUNIKE YOLANDA SIAHAAN,https://github.com/MEVLEPEIZ/go_Eunike-Yolanda-Siahaan.git
```

## Run the script

```bash
python ./fetcher.py ./config.json
# or
# python ./fetcher.py
```

# Result

The git repositories should be cloned into `result_dir_name` directory:

```
.
├── README.md
├── config.json
├── data
│   ├── abelMelidoBangun
│   ├── adhicittaMasran
│   ├── azzahraFebrinaAuliaPutri
│   ├── daudHerlanggaAndrianata
│   ├── doniYudiPrabowo
│   ├── dzakyMohammad
│   ├── efraimRefivalRuntuwene
│   ├── eunikeYolandaSiahaan
│   ├── jesicaHartatiAgustinaPardede
│   ├── restuAdityaRachman
│   ├── rizqyEkaPutraRizaldy
│   ├── septoHadyTryana
│   └── tirzaYolandaHevin
├── data.csv
└── fetcher.py
```