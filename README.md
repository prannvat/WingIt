I would REALLY advise you to use the project in Linux. If you have a Windows computer, get either a Virtual Machine or set up dual booting.

When setting up the project:
1. Clone the file to your local git repositories using SSH mode, in the terminal
>>> git clone git@github.com:prannvat/WingIt.git

2. Open the project directory in the terminal
>>> cd WingIt

3. Attempt to activate venv using the command
>>> source venv/bin/activate

3.1. If the text (venv) does not appear before your username in the linux terminal, then use the additional document found at:
\WingIt\documentation\SetupVenv.odt
You can use LibreOffice Writer to open odt files

4. Once the text (venv) appears correctly before your username and you are in the project root directory, run the command:
>>> python app.py

5. Open a web browser, and go to the address shown in the linux terminal, as part of the Flask output. Use this to check that the project is opening correctly.

