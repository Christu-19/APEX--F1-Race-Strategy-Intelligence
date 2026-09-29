-- Number of races in each season
SELECT Year, COUNT(*) AS RaceCount
FROM race_summary
GROUP BY Year
ORDER BY Year;

-- Winners by season
SELECT Year,Race,Winner
FROM race_summary
ORDER BY Year,Race;

-- Driver performance
SELECT
    FullName,
    COUNT(*) AS RaceRecords,
    ROUND(AVG(Position), 2) AS AverageFinish,
    MIN(Position) AS BestFinish,
    MAX(Position) AS WorstFinish,
    SUM(Points) AS TotalPoints
FROM race_results
WHERE Position IS NOT NULL
GROUP BY FullName
ORDER BY AverageFinish ASC;

--  2025 podium finishes
SELECT
    FullName,
    Position,
    Race
FROM race_results
WHERE Year = 2025
  AND Position IN (1, 2, 3)
ORDER BY Race, Position;

-- Average finishing position by team in 2025
SELECT
    TeamName,
    COUNT(*) AS RaceRecords,
    ROUND(AVG(Position), 2) AS AverageFinish
FROM race_results
WHERE Year = 2025
  AND Position IS NOT NULL
GROUP BY TeamName
ORDER BY AverageFinish ASC;

-- Qualifying position vs race finishing position
SELECT
    r.Year,
    r.Race,
    r.FullName,
    q.Position AS QualifyingPosition,
    r.Position AS RacePosition
FROM race_results AS r
JOIN qualifying_results AS q
    ON r.Year = q.Year
    AND r.Race = q.Race
    AND r.DriverId = q.DriverId
WHERE r.Position IS NOT NULL
  AND q.Position IS NOT NULL
ORDER BY r.Year, r.Race, r.Position;

-- Position gained or lost relative to qualifying
SELECT
    r.Year,
    r.Race,
    r.FullName,
    q.Position AS QualifyingPosition,
    r.Position AS RacePosition,
    q.Position - r.Position AS PositionsGained
FROM race_results AS r
JOIN qualifying_results AS q
    ON r.Year = q.Year
    AND r.Race = q.Race
    AND r.DriverId = q.DriverId
WHERE r.Position IS NOT NULL
  AND q.Position IS NOT NULL
ORDER BY PositionsGained DESC;

-- Most frequently occurring race strategies

SELECT
    CompoundsUsed,
    COUNT(*) AS NumberOfDriverRaces,
    ROUND(AVG(Position), 2) AS AverageFinish
FROM strategy_profiles
WHERE Position IS NOT NULL
GROUP BY CompoundsUsed
ORDER BY NumberOfDriverRaces DESC;

-- Average observed lap pace by tyre compound

SELECT
    Compound,
    COUNT(*) AS NumberOfObservations,
    ROUND(AVG(AverageLapTime), 3) AS AverageLapTime
FROM tyre_age_pace
WHERE AverageLapTime IS NOT NULL
GROUP BY Compound
ORDER BY AverageLapTime ASC;

-- Race-phase pace by compound

SELECT
    RacePhase,
    Compound,
    COUNT(*) AS Observations,
    ROUND(AVG(AverageLapTime), 3) AS AverageLapTime
FROM phase_pace
WHERE AverageLapTime IS NOT NULL
GROUP BY RacePhase, Compound
ORDER BY RacePhase, AverageLapTime;

-- Driver strategy profile

SELECT
    Driver,
    TeamName,
    Year,
    Race,
    Position,
    NumberOfStints,
    PitStops,
    CompoundsUsed
FROM strategy_profiles
ORDER BY Year, Race, Position;

-- ML feature overview

SELECT
    Year,
    Race,
    FullName,
    GridPosition,
    QualifyingPosition,
    PreviousRaceFinish,
    DriverHistoricalAvgFinish,
    DriverRecentForm,
    TeamHistoricalAvgFinish,
    QualifyingTimeGap,
    Position
FROM driver_features
WHERE Position IS NOT NULL
ORDER BY Year, Race, Position;

-- Average predicted-feature context by season

SELECT
    Year,
    ROUND(AVG(QualifyingPosition), 2) AS AvgQualifyingPosition,
    ROUND(AVG(GridPosition), 2) AS AvgGridPosition,
    ROUND(AVG(PreviousRaceFinish), 2) AS AvgPreviousFinish,
    ROUND(AVG(DriverRecentForm), 2) AS AvgRecentForm,
    ROUND(AVG(TeamHistoricalAvgFinish), 2) AS AvgTeamHistoricalFinish
FROM driver_features
GROUP BY Year
ORDER BY Year;

-- 2025 drivers with the largest qualifying-to-race gains

SELECT
    r.FullName,
    r.Race,
    q.Position AS QualifyingPosition,
    r.Position AS RacePosition,
    q.Position - r.Position AS PositionsGained
FROM race_results AS r
JOIN qualifying_results AS q
    ON r.Year = q.Year
    AND r.Race = q.Race
    AND r.DriverId = q.DriverId
WHERE r.Year = 2025
  AND r.Position IS NOT NULL
  AND q.Position IS NOT NULL
ORDER BY PositionsGained DESC
LIMIT 10;

