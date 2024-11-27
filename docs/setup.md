### How to run this file locally, or globally:

## 1. Locally:
This website is fairly easy to run locally, in command prompt (on Windows), type in "python app.py" (or whatever the path of the main python file is), and hold shift (or alt) on "127.0.0.1".
Then, you will likely be redirected to your browser, with the website open, or you have to open the browser yourself. (Though, the browser will still be running)

## 2. Globally:
Running this globally is a little bit more tricky. (As you might expect)
But, it is still not too hard. Firstly: find a website hosting service (that supports Flask. Flask is the framework for this website.) Then, upload all the files (or connect to a GitHub or GitLab repository) to the hosting website.
Make sure that if you choose to upload the files via GitHub or GitLab, you need to include a requirements.txt file (all the requirements of this website, down below is an example.), if you use Heroku, you also need to include a ProcFile. Here is an example of a ProcFile: web: python app.py

Make sure that you have the .gitignore file included.

IMPORTANT: Make sure that you set debug mode to False in this line "app.run(debug=True)"

# Example of a requirements.txt file:
Flask==2.3.2
gunicorn==20.1.0