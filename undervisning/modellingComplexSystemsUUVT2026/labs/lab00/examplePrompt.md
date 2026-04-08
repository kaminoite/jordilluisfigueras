# Task

Write a simple Python script to analyze the Artemis II mission timeline from a local CSV file.

# Data requirements

- Read the file `data/artemisII.csv`.
- Use the column names exactly as they appear in the CSV.
- Treat empty numerical entries as missing values.
- Keep the analysis local and reproducible. Do not scrape websites.

# Programming requirements

- Use Python with NumPy and Matplotlib.
- Use the standard `csv` module to read the file.
- Write a function that loads the dataset.
- Write a function that extracts numerical series for plotting.
- Write a function that plots distance versus mission day.
- Write a function that produces one additional summary plot or table.
- Keep the code short, readable, and well commented.
- Put the main execution in a `main()` function.

# Numerical and plotting task

Use the supplied dataset and produce:
- one plot of `distanceToEarthMiles` versus `missionDay`,
- one plot of `distanceToMoonMiles` versus `missionDay`, or a combined plot,
- labels or annotations for important events such as launch, lunar flyby, and return correction burn.

# Output

- Return only code.
- Add a short docstring at the top explaining what the script does.
- Do not use advanced libraries or interactive widgets.
