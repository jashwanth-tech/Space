name: Render Manim Video

on:
  push:
    branches: [ main ]
  workflow_dispatch:

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
    - name: Check out repository
      uses: actions/checkout@v4

    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.10'

    - name: Install System Dependencies (Fast)
      run: |
        sudo apt-get update
        sudo apt-get install -y libcairo2-dev libpango1.0-dev ffmpeg texlive texlive-latex-extra

    - name: Install Manim
      run: pip install manim numpy

    - name: Render Video
      run: manim -pqh scene.py OrbitalMechanics

    - name: Upload Video to Download
      uses: actions/upload-artifact@v4
      with:
        name: Physics-Animation
        path: media/
