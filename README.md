# gambling_coin

This repository contains the original PsychoPy implementation of the coin gambling task as well as a browser-based port built with [jsPsych](https://www.jspsych.org/).

## PsychoPy version

The original task logic is implemented in `gambling_interleaved_2_2.py` and related resource files. It was designed to run in the PsychoPy desktop environment.

## jsPsych version

A fully client-side jsPsych experiment is available in `jspsych_app/`.

### Running locally


1. Ensure the required JavaScript dependencies are available under `js/`:
   * `js/jspsych-7.3.3/` – copy the jsPsych distribution (core library, CSS, and the plugins used in the task).
   * `js/jatos.js` – include the JATOS helper script when packaging for a JATOS study.
   The experiment will fall back to the jsDelivr CDN for jsPsych assets if the local copies are missing, which is convenient for
   quick local testing but not recommended for production deployments.
2. Launch a local HTTP server from the repository root (e.g., `python -m http.server`).
3. Open `http://localhost:8000/jspsych_app/index.html` in a modern browser.
4. Provide the requested participant details and follow the on-screen instructions.
5. At the end of the experiment, download the CSV data file (or, in a JATOS deployment, the data will be submitted
   automatically to the server).

The jsPsych port reproduces the trial structure of the PsychoPy task, including the training phase, two experimental blocks, gamble decisions with imagery instructions, and the estimation sliders.

