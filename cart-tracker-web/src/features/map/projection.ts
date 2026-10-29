import type { LatLngTuple } from 'leaflet'
import { localToGeo } from '../../domain/geo'
import { isGeoPoint, type Point, type SiteConfig } from '../../domain/types'

// Единственное место, где точка из данных превращается в координаты
// Leaflet [широта, долгота]. Остальной код хранит точки как в файле.
//
// Как пересчитывать, зависит от двух настроек площадки:
//   wgs84           -> точка уже в градусах, берём как есть;
//   local + карта   -> метры переводим в градусы вокруг origin;
//   local + план    -> на плане цеха (image/none) Leaflet работает
//                      в метрах напрямую: [y, x].

export function toLatLng(point: Point, site: SiteConfig): LatLngTuple {
	if (site.coordinateSystem === 'wgs84') {
		if (!isGeoPoint(point)) {
			throw new Error('Площадка в wgs84, а точка задана в метрах (x, y)')
		}
		return [point.lat, point.lon]
	}

	if (isGeoPoint(point)) {
		throw new Error('Площадка в local, а точка задана в градусах (lat, lon)')
	}

	const { type } = site.basemap
	if (type === 'image' || type === 'none') {
		return [point.y, point.x]
	}

	if (!site.origin) {
		throw new Error(
			'Для local-координат на карте нужен site.origin — где на Земле точка (0, 0)',
		)
	}
	const geo = localToGeo(point, site.origin, site.rotationDeg)
	return [geo.lat, geo.lon]
}
