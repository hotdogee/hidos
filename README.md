# HiDOS
HiDOS bioinformatics platform
## CellQ
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
   * Install `virtualenv`
     * `pip install virtualenv`
       * Learn more: http://docs.python-guide.org/en/latest/dev/virtualenvs/
1. Install Erlang/OTP 64-bit
   * This is required for RabbitMQ server
   * Download: http://www.erlang.org/download.html
1. Install RabbitMQ server
   * Download: http://www.rabbitmq.com/download.html
   * Start the RabbitMQ service after installation
     * http://technet.microsoft.com/en-us/library/cc736564(v=ws.10).aspx
1. Clone the repo, initialize Python virtualenv(`init_venv.cmd`), and setup the database schema(`run_migrate.cmd`)
```
git clone https://github.com/hotdogee/hidos.git
cd hidos\hidos
init_venv.cmd
run_migrate.cmd
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
  * Check if the page `http://127.0.0.1:8000/` loads
