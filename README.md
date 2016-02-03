#Pytoube and Pymotion

Quick and dirty scripts to search and extract videos on:
- youtube:
with `pyoutube.py` file
by calling 
```python

    PyTubeSearch(
            query='Blockchain bitcoin', #for search and filter 
            user="admin@cortext.fr",  #declare user a new directory will be created
            project="BB", #declare project to store videos in it
            filter = True) #filter by query if title or description matches video will be stored
```
create a log file with article info in it
- dailymotion:
with `pymotion.py` file

```python

    PyMotionSearch(
            query='Blockchain bitcoin', #for search and filter 
            user="admin@cortext.fr",  #declare user a new directory will be created
            project="BB", #declare project to store videos in it
            filter = True) #filter by query if title matches video will be stored
```

## Install

How must have python2.7 installed
Dependencies are listed in requirements.pip
to install it run (in a virtualenv preferently)
```
pip install -r requirements.pip
```

### TO DO

This is a quick and dirty script so a lot of things can be improved
* Query: query accept only a simple expression
implement a more complexe version see Whoosh for example
* Logs:
detailled info are available in dailymotion too but not implements
such as 
    * authorname
    * author_url
    * date
    * Title
    * View

* Channel or User search option
are not implemented 

 





