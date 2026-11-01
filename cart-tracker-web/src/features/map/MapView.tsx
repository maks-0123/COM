import { MapContainer } from 'react-leaflet'
import type { Cart, PositionFix, SiteConfig, Station } from '../../domain/types'
import { SiteBasemap } from './basemaps'
import { AccuracyLayer } from './layers/AccuracyLayer'
import { CartLayer } from './layers/CartLayer'
import { StationLayer } from './layers/StationLayer'
import { toLatLng } from './projection'

// Карта целиком: подложка + станции + тележки.
// Компонент только рисует то, что ему передали. Откуда данные — из файла
// или от сервера — он не знает и знать не должен.

type Props = {
	site: SiteConfig
	stations: Station[]
	carts: Cart[]
	/** Текущая отметка каждой тележки: cartId -> отметка. */
	positions: Map<string, PositionFix>
	/** Текущее время источника: по нему тележка считается устаревшей. */
	nowMs: number
}

export function MapView({ site, stations, carts, positions, nowMs }: Props) {
	const stationPoints = stations.map((s) => toLatLng(s.position, site))

	return (
		<MapContainer
			// При открытии масштаб подбирается так, чтобы были видны все станции.
			// Это начальный вид: дальше масштабом управляет пользователь.
			{...(stationPoints.length > 0
				? { bounds: stationPoints, boundsOptions: { padding: [60, 60] } }
				: { center: [0, 0], zoom: 2 })}
			maxZoom={20}
			// Без плашки «Leaflet» в правом нижнем углу.
			attributionControl={false}
			style={{ height: '100%', width: '100%' }}
		>
			{site.basemap.type === 'pmtiles' && <SiteBasemap url={site.basemap.url} />}
			{/* Порядок важен: точность — под станциями и тележками. */}
			<AccuracyLayer positions={positions} site={site} nowMs={nowMs} />
			<StationLayer stations={stations} site={site} />
			<CartLayer carts={carts} positions={positions} site={site} nowMs={nowMs} />
		</MapContainer>
	)
}
