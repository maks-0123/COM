import { divIcon } from 'leaflet'
import { Marker, Tooltip } from 'react-leaflet'
import type { SiteConfig, Station } from '../../../domain/types'
import { toLatLng } from '../projection'

// Значок станции — тёмный треугольник (антенна), чтобы его нельзя было
// спутать с круглыми точками тележек. Свой divIcon вместо стандартного
// маркера: картинки стандартного маркера под Vite не находятся.
const STATION_ICON = divIcon({
	className: '', // убирает белый квадрат-фон, который Leaflet рисует по умолчанию
	html: `<svg width="18" height="16" viewBox="0 0 18 16">
		<path d="M9 1 L17 15 L1 15 Z" fill="#334155" stroke="#fff" stroke-width="1.5"/>
	</svg>`,
	iconSize: [18, 16],
	iconAnchor: [9, 10], // точка значка, которая совпадает с координатой станции
})

type Props = { stations: Station[]; site: SiteConfig }

export function StationLayer({ stations, site }: Props) {
	return stations.map((station) => (
		<Marker key={station.id} position={toLatLng(station.position, site)} icon={STATION_ICON}>
			<Tooltip direction='top' offset={[0, -8]}>
				{station.name}
			</Tooltip>
		</Marker>
	))
}
