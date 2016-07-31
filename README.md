# HiDOS
HiDOS bioinformatics platform
## Cell Cloud
Setting up the development environment on Windows

1. Install Git
   * Download: http://git-scm.com/downloads
1. Install Python 2.7.x 64-bit (Does not work with Python 3.x)
   * Download: https://www.python.org/downloads/
   * The default installation location is `C:\Python27`, if you do not use the default, modify all following steps accordingly.
     * Choose to install "pip" and "Add python.exe to Path" during the Python Setup
   * Install pip if you didn't install it during Python Setup
     * Download get-pip.py: https://bootstrap.pypa.io/get-pip.py
     * Run `C:\Python27\python get-pip.py`
     * `pip.exe` should now be in `C:\Python27\Scripts`
   * Make sure `C:\Python27` and `C:\Python27\Scripts` are in your PATH. If you didn't choose "Add python.exe to Path" during Python Setup, you can run a script included with python that automatically does this: `C:\Python27\Tools\Scripts\win_add2path.py`
   * Update `pip`
     * `python -m pip install -U pip`
   * Update `setuptools`
     * `pip install -U setuptools`
   * Install `virtualenv`
     * `pip install virtualenv`
       * Learn more: http://docs.python-guide.org/en/latest/dev/virtualenvs/
   * Install `Microsoft Visual C++ Compiler for Python 2.7`
     * Download: https://www.microsoft.com/en-us/download/details.aspx?id=44266
1. Install PostgreSQL 9.5+
   * Download: http://bigsql.org/postgresql/installers.jsp
1. Install Erlang/OTP 64-bit
   * This is required for RabbitMQ server
   * Download: http://www.erlang.org/download.html
1. Install RabbitMQ server
   * Download: http://www.rabbitmq.com/download.html
   * Start the RabbitMQ service after installation
     * http://technet.microsoft.com/en-us/library/cc736564(v=ws.10).aspx
1. Install R
   * Download: https://cran.r-project.org/bin/windows/base/
   * Install EBImage package
     * http://bioconductor.org/packages/release/bioc/html/EBImage.html
     * Start R as Administrator and enter
       * `source("https://bioconductor.org/biocLite.R")`
       * `biocLite("EBImage")`
   * Install RJSONIO package
     * `install.packages('RJSONIO')`
   * Add RScript to PATH environment variable
     * C:\Program Files\R\R-3.x.x\bin\
1. Clone the repo, initialize Python virtualenv(`init_venv.cmd`), and initialize the database tables(`reset_datadb.cmd`)
   ```
git clone https://github.com/hotdogee/hidos.git
cd hidos\hidos
setup_postgres.cmd
init_venv.cmd
postgres_reset.cmd
```

1. Run development web server
  ```
run_server.cmd
```

1. Run job worker
  ```
run_celery.cmd
```

1. Test the app
  * Login to admin: `http://127.0.0.1:8000/admin/`
  * Explore the REST API: `http://127.0.0.1:8000/api/v1/`

1. Install VSCode (Optional)
   * Available on Windows, Mac, Linux
   * Supports Django debugging, linting, autopep8
   * hidos project includes vscode settings files
   * Download: https://code.visualstudio.com
   * Install Python extensions
     * https://marketplace.visualstudio.com/items?itemName=donjayamanne.python
