import type { Layer } from 'leaflet'
import { leafletLayer } from 'protomaps-leaflet'
import { useEffect } from 'react'
import { useMap } from 'react-leaflet'

// Собственная подложка: карта рисуется прямо в браузере из файла
// public/basemap/site.pmtiles (его собирает scripts/build-basemap.sh).
// Никаких внешних сервисов и ключей — файл лежит рядом с сайтом.
const SITE_BASEMAP_URL = '/basemap/site.pmtiles'

export function SiteBasemap() {
	const map = useMap()

	useEffect(() => {
		// flavor 'light' — светлая серая схема в духе Positron:
		// дороги и здания не спорят по цвету с точками тележек.
		// lang 'ru' — подписи улиц на русском, где они есть в OSM.
		const layer = leafletLayer({
			url: SITE_BASEMAP_URL,
			flavor: 'light',
			lang: 'ru',
		}) as unknown as Layer

		layer.addTo(map)
		// Очистка: без неё StrictMode добавит слой дважды.
		return () => {
			layer.remove()
		}
	}, [map])

	return null
}
