# Wheat eQTLs Atlas Website

------

This document describes how to build a website for searching and viewing the Wheat eQTL Atlas. For example, the site displays Manhattan plots for each dataset and a summary table of eQTLs for *Rht1-B* (*TraesCS4B03G0093100* in Chinese Spring V2.1). These instructions are adapted for an Ubuntu server; modifications may be required for other platforms. For **Windows**, Ubuntu could be installed from the microsoft store.

![](/images/web.rhtb1.png)

**Be extreme caution when hosting a website publicly**  If your site is accessible beyond your local network, ensure that file permissions, authentication settings, and access controls are properly configured.

- [Prerequisites](#prerequisites)
- [Web and Data](#web-and-data)
- [Database -- MySQL](#database----mysql)
- [Going Online](#going-online)
- [FAQ](#faq)   
- [Citation](#citation)
- [Acknowledgments](#acknowledgments)

## Prerequisites

-------

- **[NGINX](https://nginx.org/index.html)**
  
  - `sudo apt-get install nginx`

- **Python 3.10.12** 
  
  - Install "Flask" `pip install flask` and MySTL connector `pip install mysql-connector-python`: 

- **Data**
  
  - Website files, Manhattan plots in PNG format, and the eQTL summary table are available on [BaiduYun](https://pan.baidu.com/): [Wheat_eQTL_Atlas](https://pan.baidu.com/s/13JyHtHsUT5Ooo-VZka4YZA?pwd=zhrn) 

## Web and Data

-------

- **Data and Environment**
  All files listed below are available from [Wheat_eQTL_Atlas](https://pan.baidu.com/s/13JyHtHsUT5Ooo-VZka4YZA?pwd=zhrn). Place them into the following directory structure:
  
  ```
  mkdir -p /var/www/eqtl
  mkdir /var/www/eqtl/static
  mkdir /var/www/eqtl/templates
  
  mv web/eqtl.py /var/www/eqtl
  
  tar -zxvf ManhattanPlots.tar.gz
  mv image /var/www/eqtl/static/
  
  mv web/templates/index.html /var/www/eqtl/templates/
  
  # the eqtls table will be load to MySQL server 
  gunzip Wheat.FourPanels.eQTLs.formated.2025.csv.gz
  ```
  
  A Python 3 environment:   `python -m venv venv` and   `source venv/bin/activate`

- **NGINX Configuration**

Configure NGINX to host the website. Replace the IP address `192.168.1.233` with your own server IP. 

```
server {
    listen 80;
    server_name 192.168.1.233; # replace with your actual IP

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

}
```

## Database -- MySQL

-------

### Step 1: Install and Configure MySQL

**Install MySQL Server**:

```
sudo apt update
sudo apt install mysql-server
```

**Secure MySQL Installation**: Run the following command to improve MySQL security, and set username and password: `sudo mysql_secure_installation`.

### Step 2: load the eQTL table into MySQL

**2.1 Login and create the database and table for loading**:

```
# login

sudo mysql -u root -p

# Create the database eqtl:

CREATE DATABASE eqtl; 

USE eqtl;

#Create the table:
CREATE TABLE wheat ( 
   Project VARCHAR(50),
   Tissue VARCHAR(50),
   SamplesNo INT,
   Geneid VARCHAR(50) ,
   Chr VARCHAR(10),
   Start INT,
   End INT,
   Strand VARCHAR(4),
   Type VARCHAR(10),
   Chr_SNP VARCHAR(10),
   Position INT,
   maf FLOAT(2,2),
   Pvalue VARCHAR(40),
   Distance VARCHAR(20));
```

**2.2 Load the table from `ALL.merged.formated.2025.csv`**:

```
# enable local file loading

SET GLOBAL local_infile = 1;

# Log in with local file support (replace the file path as needed)

sudo mysql --local-infile=1 -u root -p

USE eqtl;

LOAD DATA LOCAL INFILE 'Wheat.FourPanels.eQTLs.formated.2025.csv' INTO TABLE wheat
FIELDS TERMINATED BY ',' 
LINES TERMINATED BY '\n' 
IGNORE 1 ROWS
(Project, Tissue, SamplesNo, Geneid, Chr, Start, End, Strand, Type, Chr_SNP, Position, maf, Pvalue, Distance);  
```

### Step 3: create a user for access of website

Create a MySQL user (e.g., flask_user) with a secure password (user and password will be need in `eqtl.py`) and grant the necessary privileges. This user will be used by the website to access the database locally.

```
sudo mysql -u root -p

# for example user "flask_user" with password "wheateQTLs@2025"

CREATE USER 'flask_user'@'localhost' IDENTIFIED BY 'wheateQTLs@2025';GRANT ALL PRIVILEGES ON eqtl.* TO 'flask_user'@'localhost';
FLUSH PRIVILEGES;
```

## Going Online

-------

To bring the Static Website online: `python eqtl.py`, then access it via `http://192.168.1.233/` (replace with your server IP)

## FAQ

-------

1. Why is there only a single SNP reported for most associated eQTLs? 
   Answer: This is a characteristic of the FarmCPU method used for mapping. Unlike standard mixed linear models that often report multiple correlated SNPs in a region, FarmCPU iteratively selects the single most associated SNP (called QTN) from a locus. It then uses this SNP as a cofactor in the model to statistically control for that locus's effect. This process efficiently eliminates signals from other SNPs in high linkage disequilibrium (LD) with the top hit, resulting in one representative SNP per locus. This SNP "tags" the associated genomic region; the true causal variant is likely in high LD with it.

## Citation

-------

1. If you use the data of this respository, please cite our **coming soon paper**:
   A Multi-Tissue eQTL Atlas Across Development and Genetic Backgrounds in Wheat Unveils Dynamic Regulation of the Transcriptome.

2. Ciation for the ground tissue of 2-week-old **Plant** RNA-Seq data (SRA Project: PRJNA670223):
   [He, F., Wang, W., Rutter, W. B., Jordan, K. W., Ren, J., Taagen, E., ... & Akhunov, E. (2022). Genomic variants affecting homoeologous gene expression dosage contribute to agronomic trait variation in allopolyploid wheat. Nature Communications, 13(1), 826.](https://doi.org/10.1038/s41467-022-28453-y)

3. Ciation for the **Seedling** Leaves at the three-leaf stage RNA-Seq data (SRA Project: PRJNA795836):
   [Mei, F., Chen, B., Du, L., Li, S., Zhu, D., Chen, N., ... & Mao, H. (2022). A gain-of-function allele of a DREB transcription factor gene ameliorates drought tolerance in wheat. The Plant Cell, 34(11), 4472-4494.](https://doi.org/10.1093/plcell/koac248)

4. Ciation for the second or third seedling **Leaf**  RNA-Seq data (SRA Project: PRJNA912645):
   [Barratt, L. J., He, Z., Fellgett, A., Wang, L., Mason, S. M., Bancroft, I., & Harper, A. L. (2023). Co‐expression network analysis of diverse wheat landraces reveals markers of early thermotolerance and a candidate master regulator of thermotolerance genes. The Plant Journal, 115(3), 614-626.](https://doi.org/10.1111/tpj.16248)

5. Ciation for the **Root** at 14 days after germination RNA-Seq data (SRA Project: PRJNA838764):
   [Zhao, P., Liu, Z., Shi, X., Hou, W., Cheng, M., Liu, Y., ... & Wang, X. (2024). Modern wheat breeding selection synergistically improves above-and belowground traits. Plant Physiology, 196(1), 47-50.](https://doi.org/10.1093/plphys/kiae270)

## Acknowledgments

-------
