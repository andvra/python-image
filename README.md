# Epicycles

Use Fourier transforms to generate epicycles to follow the edges of an image. Apply common CV techniques to extract edges from any given image.

<img src="./assets/game.png" width="500px">

## Getting started

Use Python >= 3.7 to run the code.

## Recommended: create and run virtual environment.

Create virtual environment

```
$ python -m venv venv
```

Run virtual environment

```
Windows:
  venv\script\activate.bat
Linux:
  . venv/bin/activate
```

## Install and run

Install packages:

```
$ pip install -r requirements.txt
```

Run:

```
$ python main.py
```

## References

Based on [this](https://www.youtube.com/watch?v=qS4H6PEcCCA) video by Mathologer.

## TODOs

Implement an SVG parser. Since SVGs are defined by equations, we could bypass the CV parts of the code. The results would be smoother but also more limited since most images you find will be a non-vectorized format such as PNG.
