# Docker and Docker Compose

A ready-made presentation is included as `D510_Docker_and_Docker_Compose.slides.html`. Open it in a browser with internet access for Reveal.js.

Open `D510_Docker_and_Docker_Compose.ipynb` in Jupyter and read the rendered Markdown cells. Each cell is marked as a slide; commands are shown as text for use in a terminal.

The five SVG diagrams are embedded in the notebook and also saved in `assets/` for reuse. The ready-to-run example is in `compose-demo/compose.yaml`.

To export a presentation when nbconvert is installed:

```sh
jupyter nbconvert D510_Docker_and_Docker_Compose.ipynb --to slides
```

The exported presentation may need internet access to load Reveal.js. The notebook itself contains all diagram assets.

Installation and Docker commands target a remote Ubuntu VM only, not WSL or a corporate laptop. The notebook includes apt installation, group access, verification, and SSH port forwarding for the web examples.

## Spark image and cluster

Continue with `D511_Spark_Docker_Image_and_Compose.ipynb`. Its self-contained companion project is in `spark-docker/`; follow that folder's README to build and run the master and worker.
