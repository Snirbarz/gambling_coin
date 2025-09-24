# gambling_coin

This repository contains the original PsychoPy implementation of the coin gambling task as well as a browser-based port built with [jsPsych](https://www.jspsych.org/).

## PsychoPy version

The original task logic is implemented in `gambling_interleaved_2_2.py` and related resource files. It was designed to run in the PsychoPy desktop environment.

## jsPsych version

A fully client-side jsPsych experiment is available in `jspsych_app/`.

### Running locally

1. Launch a local HTTP server from the repository root (e.g., `python -m http.server`).
2. Open `http://localhost:8000/jspsych_app/index.html` in a modern browser.
3. Provide the requested participant details and follow the on-screen instructions.
4. At the end of the experiment, use the provided button to download the CSV data file.

The jsPsych port reproduces the trial structure of the PsychoPy task, including the training phase, two experimental blocks, gamble decisions with imagery instructions, and the estimation sliders.

