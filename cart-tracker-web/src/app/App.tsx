import type { LatLngTuple } from 'leaflet'
import { CircleMarker, MapContainer, Tooltip } from 'react-leaflet'
import { SiteBasemap } from '../features/map/basemaps'

// ВРЕМЕННО: карта прямо в App, точка вписана в код.
// Цель шага — убедиться, что карта вообще работает.
// Дальше карта переедет в features/map/MapView.tsx,
// а координаты придут из public/data/demo-scenario.json.

// Точка (0, 0) площадки — origin из demo-scenario.json.
const SITE_ORIGIN: LatLngTuple = [55.9495, 37.182]

// cart-01 из demo-scenario.json: x = 20 м (восток), y = 30 м (север) от origin,
// переведено в широту/долготу вручную:
//   lat = 55.7 + 30 / 111 320                 ≈ 55.70027
//   lon = 37.6 + 20 / (111 320 · cos 55.7°)    ≈ 37.60032
const DEMO_CART: LatLngTuple = [55.9495, 37.182]

export default function App() {
	return (
		// Leaflet нужна явная высота контейнера, иначе карта будет высотой 0 px.
		// position: fixed + inset: 0 растягивает блок на всё окно браузера.
		<div style={{ position: 'fixed', inset: 0 }}>
			<MapContainer
				center={SITE_ORIGIN}
				zoom={18}
				maxZoom={20}
				// Без плашки «Leaflet» в правом нижнем углу.
				attributionControl={false}
				style={{ height: '100%', width: '100%' }}
			>
				<SiteBasemap />
				<CircleMarker
					center={DEMO_CART}
					radius={8}
					pathOptions={{
						color: '#1e3a8a',
						weight: 2,
						fillColor: '#3b82f6',
						fillOpacity: 0.9,
					}}
				>
					<Tooltip permanent direction='right' offset={[10, 0]}>
						cart-01
					</Tooltip>
				</CircleMarker>
			</MapContainer>
		</div>
	)
}
