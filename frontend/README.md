# Frontend

The web-based interactive map interface for the Mangaluru Bus Navigator.

## Overview

The frontend is a single-page application built with:

- **Leaflet.js** - Interactive maps
- **OpenStreetMap** - Map tiles
- **HTML5 & JavaScript** - UI and interactions
- **Fetch API** - Communication with backend

## Files

### `templates/index.html`

Main HTML file containing:

- Map container (Leaflet)
- Search and controls UI
- Route display interface
- JavaScript embedded or linked

## Quick Start

### Running the Frontend

The frontend is served by the Flask backend:

```bash
cd Neo4j/backend
python app.py
```

Then open browser to `http://localhost:5000`

### Features

- **Interactive Map** - Zoom, pan, click stops
- **Stop Search** - Type stop name to find it
- **Route Selection** - Click two stops to find routes
- **Path Display** - View routes on map with turn-by-turn
- **Zone Visualization** - Color-coded zones (if applicable)

## Development

### File Structure

```
frontend/
├── templates/
│   └── index.html          # Main page
└── static/                 # (Optional)
    ├── css/
    │   └── style.css       # Custom styles
    └── js/
        └── app.js          # Custom scripts
```

### Making Changes

If you modify `templates/index.html`:

1. Stop the Flask server (`Ctrl+C`)
2. Make changes to the file
3. Restart Flask (`python app.py`)
4. Refresh browser or clear cache

**Note:** Static assets (CSS, JS) may need cache clearing:

```bash
# Hard refresh in browser
Ctrl+Shift+R (Windows/Linux)
Cmd+Shift+R (macOS)
```

### Key Libraries

#### Leaflet.js

```html
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
```

**Common Usage:**

```javascript
// Initialize map
const map = L.map('map').setView([12.8698, 74.8426], 13);

// Add tile layer
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);

// Add marker
L.marker([12.8698, 74.8426]).addTo(map).bindPopup('Bus Stand');

// Draw polyline
L.polyline(
  [[12.8698, 74.8426], [12.8713, 74.8397]],
  {color: 'red'}
).addTo(map);
```

## API Integration

### Fetching Stops

```javascript
fetch('/api/stops?q=balmatta')
  .then(response => response.json())
  .then(stops => {
    // Process stops
    stops.forEach(stop => {
      console.log(stop.name, stop.lat, stop.lng);
    });
  });
```

### Finding Paths

```javascript
fetch('/api/paths?from_id=stop_123&to_id=stop_456&weight_field=weight_distance')
  .then(response => response.json())
  .then(paths => {
    // Display on map
    paths.forEach(path => {
      const coords = path.path.map(s => [s.lat, s.lng]);
      L.polyline(coords, {color: 'blue'}).addTo(map);
    });
  });
```

## Styling

### Custom CSS

Create `frontend/static/css/style.css`:

```css
#map {
  height: 100vh;
  width: 100%;
}

.info-box {
  background: white;
  padding: 10px;
  border-radius: 5px;
  box-shadow: 0 0 15px rgba(0, 0, 0, 0.2);
}

.bus-stop {
  color: #ff6b6b;
  font-weight: bold;
}
```

Link in HTML:

```html
<link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
```

## User Interactions

### Stop Selection

```javascript
// Handle stop click
map.on('click', function(e) {
  const lat = e.latlng.lat;
  const lng = e.latlng.lng;
  
  // Find nearest stop
  fetch(`/api/stops?lat=${lat}&lng=${lng}&closest=1`)
    .then(r => r.json())
    .then(stops => {
      if (stops.length > 0) {
        selectStop(stops[0]);
      }
    });
});
```

### Route Drawing

```javascript
function drawRoute(path) {
  // Clear previous
  map.eachLayer(layer => {
    if (layer instanceof L.Polyline) {
      map.removeLayer(layer);
    }
  });
  
  // Draw new route
  const coords = path.path.map(s => [s.lat, s.lng]);
  L.polyline(coords, {
    color: 'blue',
    weight: 3,
    opacity: 0.7
  }).addTo(map);
  
  // Add markers
  path.path.forEach((stop, idx) => {
    L.marker([stop.lat, stop.lng])
      .bindPopup(`${stop.name} (${idx + 1})`)
      .addTo(map);
  });
}
```

## Browser Compatibility

### Supported Browsers

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+
- Mobile browsers (iOS Safari, Chrome)

### Known Issues

- Older browsers may not support Fetch API (use polyfill)
- Mobile zoom may be limited on some devices

## Performance

### Optimization Tips

1. **Lazy Load** - Load stops only in viewport
2. **Cluster Markers** - Use Leaflet MarkerClusterGroup for many stops
3. **Cache Results** - Store API responses in browser storage
4. **Debounce Search** - Limit API calls while typing

Example - Debounce Search:

```javascript
let searchTimeout;
const searchInput = document.getElementById('search');

searchInput.addEventListener('input', (e) => {
  clearTimeout(searchTimeout);
  searchTimeout = setTimeout(() => {
    const query = e.target.value;
    fetchStops(query);
  }, 300);
});
```

### Bundle Size

Currently loads from CDN:

- Leaflet: ~142 KB
- No build process needed
- Keep JavaScript inline or minimal external files

## Accessibility

### Best Practices

```html
<!-- Use semantic HTML -->
<button aria-label="Find Route">Search</button>

<!-- Keyboard navigation -->
<input type="text" placeholder="Start typing..." autofocus>

<!-- ARIA live regions for updates -->
<div aria-live="polite" aria-atomic="true" id="status"></div>
```

## Testing

### Manual Testing

1. Open `http://localhost:5000`
2. Wait for map to load
3. Test stop search
4. Click two stops and find routes
5. Verify paths display correctly

### Automated Testing (Optional)

If you add Selenium or Cypress tests:

```bash
pytest frontend/tests/  # Python tests
npm test                 # Node.js tests
```

## Mobile Optimization

### Responsive Design

```css
@media (max-width: 768px) {
  #map {
    height: 60vh;
  }
  
  .controls {
    font-size: 16px;  /* Avoid auto-zoom on iOS */
  }
}
```

### Touch Interactions

```javascript
// Handle touch events
map.on('touch', function() {
  // Mobile-specific logic
});
```

## Deployment

### Build for Production

The frontend doesn't require compilation. Just ensure:

1. All URLs are relative or use correct domain
2. CSS and JS files are minified (optional)
3. CDN links are reliable or self-host

### Serving Static Assets

Flask automatically serves `templates/` and `static/`:

```python
app = Flask(
    __name__,
    template_folder="../../frontend/templates",
    static_folder="../../frontend/static"
)
```

To serve from a CDN:

```html
<!-- Instead of local: /static/css/style.css -->
<!-- Use CDN: https://cdn.example.com/style.css -->
<link rel="stylesheet" href="https://cdn.example.com/style.css">
```

## Troubleshooting

### Map Not Loading

- Check browser console for errors (`F12`)
- Verify Leaflet CDN is accessible
- Ensure map container has `id="map"`

### Stops Not Appearing

- Check `/api/stops` endpoint returns data
- Verify latitude/longitude are valid
- Check browser network tab for 404 errors

### Search Not Working

- Verify Flask backend is running
- Check CORS headers in Flask response
- Ensure stop names match database

### Performance Issues

- Reduce marker count
- Use clustering for large datasets
- Optimize API response size

## Related Files

- `Neo4j/backend/app.py` - Backend API
- `.env.local` - Configuration (not in frontend, used by backend)
