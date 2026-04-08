"""Template for a small Artemis II mission-data analysis project."""

import csv

import matplotlib.pyplot as plt
import numpy as np


# -----------------------------
# Parameters
# -----------------------------
dataFile = "../data/artemisII.csv"


def parseOptionalFloat(value):
  """Convert a CSV entry to float, using NaN for missing values."""
  strippedValue = value.strip()
  if(strippedValue == ""):
    return np.nan
  return float(strippedValue)


def loadMissionData(fileName):
  """Read the Artemis II CSV file into a list of dictionaries."""
  rows = []

  with open(fileName, newline = "", encoding = "utf-8") as inputFile:
    reader = csv.DictReader(inputFile)
    for row in reader:
      rows.append(
        {
          "missionDay": parseOptionalFloat(row["missionDay"]),
          "date": row["date"].strip(),
          "event": row["event"].strip(),
          "distanceToEarthMiles": parseOptionalFloat(row["distanceToEarthMiles"]),
          "distanceToMoonMiles": parseOptionalFloat(row["distanceToMoonMiles"]),
          "eventType": row["eventType"].strip()
        }
      )

  return rows


def extractSeries(rows, key):
  """Return mission day values and one numerical series."""
  missionDays = []
  values = []

  for row in rows:
    if(np.isnan(row["missionDay"]) or np.isnan(row[key])):
      continue

    missionDays.append(row["missionDay"])
    values.append(row[key])

  return np.array(missionDays), np.array(values)


def plotDistances(rows):
  """Plot distance to Earth and distance to the Moon."""
  missionDayEarth, earthDistance = extractSeries(rows, "distanceToEarthMiles")
  missionDayMoon, moonDistance = extractSeries(rows, "distanceToMoonMiles")

  plt.figure(figsize = (8, 4.5))
  plt.plot(missionDayEarth, earthDistance, marker = "o", lw = 1.2, label = "Distance to Earth")
  plt.plot(missionDayMoon, moonDistance, marker = "s", lw = 1.2, label = "Distance to Moon")
  plt.xlabel("Mission day")
  plt.ylabel("Distance (miles)")
  plt.title("Artemis II mission distances")
  plt.grid(True, alpha = 0.3)
  plt.legend()
  plt.tight_layout()


def plotMissionTimeline(rows):
  """Plot a compact timeline of event labels."""
  missionDays = []
  eventIndex = []
  eventLabels = []

  for index, row in enumerate(rows):
    if(np.isnan(row["missionDay"])):
      continue

    missionDays.append(row["missionDay"])
    eventIndex.append(index)
    eventLabels.append(row["event"])

  plt.figure(figsize = (9, 4.5))
  plt.scatter(missionDays, eventIndex, color = "black", s = 18)

  for xValue, yValue, label in zip(missionDays, eventIndex, eventLabels):
    plt.text(xValue + 0.05, yValue, label, fontsize = 8, va = "center")

  plt.xlabel("Mission day")
  plt.ylabel("Event index")
  plt.title("Artemis II mission timeline")
  plt.grid(True, axis = "x", alpha = 0.3)
  plt.tight_layout()


def printSummary(rows):
  """Print a short numerical summary."""
  missionDayEarth, earthDistance = extractSeries(rows, "distanceToEarthMiles")
  farthestIndex = np.argmax(earthDistance)

  print(f"Number of events: {len(rows)}")
  print(
    "Farthest recorded distance to Earth: "
    f"{earthDistance[farthestIndex]:.0f} miles on mission day {missionDayEarth[farthestIndex]:.1f}"
  )


def main():
  """Run a simple Artemis II data analysis."""
  rows = loadMissionData(dataFile)
  printSummary(rows)
  plotDistances(rows)
  plotMissionTimeline(rows)
  plt.show()


if __name__ == "__main__":
  main()
