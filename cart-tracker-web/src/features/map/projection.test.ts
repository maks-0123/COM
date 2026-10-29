import { describe, expect, it } from 'vitest'
import type { SiteConfig } from '../../domain/types'
import { toLatLng } from './projection'

const LOCAL_ON_MAP: SiteConfig = {
	id: 'demo',
	name: 'Demo',
	coordinateSystem: 'local',
	origin: { lat: 55.9495, lon: 37.182 },
	basemap: { type: 'pmtiles', url: '/basemap/site.pmtiles' },
}

describe('toLatLng', () => {
	it('wgs84: точка берётся как есть, в порядке [lat, lon]', () => {
		const site: SiteConfig = { ...LOCAL_ON_MAP, coordinateSystem: 'wgs84' }
		expect(toLatLng({ lat: 55.95, lon: 37.18 }, site)).toEqual([55.95, 37.18])
	})

	it('local на карте: (0, 0) — это origin', () => {
		expect(toLatLng({ x: 0, y: 0 }, LOCAL_ON_MAP)).toEqual([55.9495, 37.182])
	})

	it('local на плане цеха: [y, x] без пересчёта в градусы', () => {
		const site: SiteConfig = {
			...LOCAL_ON_MAP,
			basemap: { type: 'image', url: '/plan.png', widthM: 300, heightM: 200 },
		}
		expect(toLatLng({ x: 20, y: 30 }, site)).toEqual([30, 20])
	})

	it('ошибка, если система координат точки не совпадает с площадкой', () => {
		expect(() => toLatLng({ lat: 55.95, lon: 37.18 }, LOCAL_ON_MAP)).toThrow()
	})

	it('ошибка, если для local на карте не задан origin', () => {
		const site: SiteConfig = { ...LOCAL_ON_MAP, origin: undefined }
		expect(() => toLatLng({ x: 1, y: 1 }, site)).toThrow(/origin/)
	})
})
