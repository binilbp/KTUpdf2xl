# KTUpdf2xl
A Website to Convert the ktu marklist pdf to better Readable and Analysable form 

## Requirements

### venv (optional)
create a new python environment to avoid package conflicts
(for windows)
```sh
python -m venv venv
```

### Packages
The following packages are required:
- tabula-py[jpype]
- xlsxwriter
- pandas

The required packages can installed using requirements.txt file
```sh
pip install -r requirements.txt
```
### java 8+
java JRE required for the working of tabula-py
<details>
  <br>
  <summary>JRE Installation Guide (click to expand)</summary>

  1. Download JRE from https://adoptium.net/temurin/releases/?os=windows&arch=x64&package=jre
  (for windows)
  2. Install the msi file, and set the option as show in the image for setting up the path ![Step 3 image](https://github.com/13inilb/KTUpdf2xl/blob/tabula/Images/installation.png)
  3. Check if java is properly installed by the running the command in a new terminal
```sh
java -version
```
you should see an output which includes the version number  
</details>
