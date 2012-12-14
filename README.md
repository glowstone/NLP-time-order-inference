
6863-final-project is a system to process texts, extract events from the texts, and extract timing and ordering information about events in the text. Sentences in the text are analyzed to build a queryable data structure which maintains the best available time information about each event and the relative orderings of events based on time and text context information. It can also determine whether a given text is temporally logical in its event relationships. Also includes a mini-query language for making time and ordering queries about extracted events.

Source and Setup
================

You will create everything inside of a Pyton virtual environment as this is best practice and will not influence any of your global settings.

It is assumed you are attempting this on Ubuntu. This should theoretically work on OS X if you’ve got gcc installed properly to be able to install numpy.

Getting the Source
------------------
Git Approach

    git clone https://github.com/dghubble/6863-final-project.git
    cd 6863-final-project

Alternately unzip the zip file and call the file 6863-final-project

    virtualenv 6863-env

(Not if the previous step fails, you need virtualenv. Try running “sudo easy_install virtualenv”)

    source 6863-env/bin/activate
    pip install nltk
    pip install -r pip-env-reqs.txt

(The above command will install numpy, and other needed modules)
Now its time to get the nltk corpora and modules we need. We’ll invoke a Python shell and use the GUI downloader. You must have Python IDLE installed from the PackageManager to find all the necessary corpora.

![Ubuntu Package Manager IDLE Install](https://raw.github.com/dghubble/6863-final-project/master/docs/img/idle_install.png "Package Manager Installation of IDLE")

Once you’re sure you have IDLE,

    python
    import nltk
    nltk.download()

This will open up GUI NLTK Package Downloader
Install the following Corpora: ptb, stopwords, treebank, words
Install the following Models: hmm_treebank_pos_tagger, maxent_ne_chunker, maxent_treebank_pos_tagger, punktk

![Corpora Installation GUI](https://raw.github.com/dghubble/6863-final-project/master/docs/img/corpora.png "Install Corpora")

![Model Installation GUI](https://raw.github.com/dghubble/6863-final-project/master/docs/img/models.png "Install Models")

    quit()   # This leaves the Python shell. 

You should be all set. Try running 

    python temporal_analyzer.py -f texts/time_example

or 

    python temporal_analyzer.py -f texts/ordering_example -q queries/ordering_example_query

![Running an Ordering Example](https://raw.github.com/dghubble/6863-final-project/master/docs/img/ordering_example_w_ref.png "Success")


If you have difficulties, glance over the docs/installation_log and see if you did anything wrong.

Feel free to use Github to communicate with us. Otherwise, you can directly contact [Dalton Hubble](mailto:dghubble@gmail.com) and [Thomas Garver](mailto:tgarvz@gmail.com)

