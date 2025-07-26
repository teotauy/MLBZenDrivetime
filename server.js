import express from 'express';
import fetch from 'node-fetch';
import cors from 'cors';
import dotenv from 'dotenv';

dotenv.config();

const app = express();
app.use(express.json());
app.use(cors());

const GOOGLE_MAPS_API_KEY = process.env.GOOGLE_MAPS_API_KEY;

app.post('/api/calculate', async (req, res) => {
  const { startLocation, destinations } = req.body;
  if (!startLocation || !destinations || !destinations.length) {
    return res.status(400).json({ error: "Invalid input" });
  }
  // Build the API URL
  const origins = encodeURIComponent(startLocation);
  const dests = destinations.map(encodeURIComponent).join('|');
  const url = `https://maps.googleapis.com/maps/api/distancematrix/json?origins=${origins}&destinations=${dests}&units=imperial&key=${GOOGLE_MAPS_API_KEY}`;

  try {
    const response = await fetch(url);
    const data = await response.json();
    if (data.status !== "OK") throw new Error("API error");

    const results = data.rows[0].elements.map((e, i) => ({
      address: destinations[i],
      driveDurationMinutes: e.status === "OK" ? e.duration.value / 60 : null,
      driveDistanceMiles: e.status === "OK" ? e.distance.value / 1609.34 : null
    }));
    res.json(results);
  } catch (err) {
    res.status(500).json({ error: "Failed to get drive times" });
  }
});

const PORT = process.env.PORT || 8001;
app.listen(PORT, '0.0.0.0', () => console.log(`Backend running on :${PORT}`));