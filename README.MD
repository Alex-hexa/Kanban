
# Kanban Local

This __Kanban board__ is running all in local (DB/APP). 

## Download and run

All you have to do is clone this repo :
```
git clone https://github.com/Alex-hexa/Kanban
```

Install Flask :
```
pip install flask
```

Run Python :
```
python app.py
```

And go to the URL :
```
http://127.0.0.1:5001
```

## Setting

### Change the column

To change the column, go to the __app.py__ file's and add, change or delete the elements inside the list name "__DEFAULT_COLUMNS__".
```
DEFAULT_COLUMNS = ["Pense bête", "À faire", "En cours", "Terminé"]
```

### Change the categories

To change the categories, go to the app and click to the button "__Gérer les catégories__". Then, you can __delete it on press the red trash button__.

If you want to add it, tap your title inside the input, choise your color on the grey square and __save it on the green plus button__.

### The ticket

For each column, you have a __green plus button to add a ticket__.

When you click on it, a pop up open's, you can now complete each input to create your ticket.