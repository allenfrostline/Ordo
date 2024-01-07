# Ordo

**Ordo** is a noun in Latin meaning *a methodical series, arrangement, or order*.
That is also what this simple web app is going to do: methodically identify your
preference over a bunch of items that you're having a decidophobia session upon.
Which ones should you buy? Are you paying too much for the coat? How come these
two skirts look exactly the same🤯?

If you're curious (or have been looking at your shopping cart for a few hours),
feel free to go to the next tab and give it a try. There's nothing to lose except
some ridiculously priced items from your fuss.

## Installing

```
pip install git+https://github.com/allenfrostline/ordo.git
```

## Running locally

You can run the server as a module:

```
python -m ordo
```

or the explicit file:

```
git clone https://github.com/allenfrostline/ordo.git
cd ordo/
streamlit run src/ordo/app.py --server.runOnSave true --theme.base light
```

## Running tests

```
pytest
```